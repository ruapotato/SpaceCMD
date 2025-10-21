## Ship - Main spaceship class
## Manages hull, shields, power, rooms, crew, weapons
class_name Ship extends RefCounted

var ship_name: String = ""
var ship_class: String = ""

# Convenience alias for combat system
var name: String:
	get: return ship_name

# Resources
var hull: float = 30.0
var hull_max: float = 30.0
var shields: float = 0.0
var shields_max: int = 0
var dark_matter: int = 20  # FTL fuel
var missiles: int = 8
var scrap: int = 0

# Power
var reactor_power: int = 8
var power_available: int = 8

# Ship structure
var rooms: Dictionary = {}  # String -> Room
var systems: Dictionary = {}  # SystemType -> ShipSystem
var crew: Array[Crew] = []
var weapons: Array[Weapon] = []

# Galaxy position (1D for map navigation)
var galaxy_position: float = 800.0
var velocity: float = 0.0
var is_traveling: bool = false
var target_position: float = 0.0

# Combat position (3D for battle space)
var position: Vector3 = Vector3.ZERO
var velocity_3d: Vector3 = Vector3.ZERO
var heading: Vector3 = Vector3(1, 0, 0)  # Facing +X by default

# Movement parameters
var max_speed: float = 20.0  # Units per second
var acceleration: float = 10.0  # Units per second squared
var turn_rate: float = 90.0  # Degrees per second
var mass: float = 1.0  # Affects acceleration

# Movement inputs (set by AI or player)
var thrust_input: float = 0.0  # -1.0 (reverse) to 1.0 (forward)
var turn_input: float = 0.0  # -1.0 (left) to 1.0 (right)

# Ship OS (one per ship)
var os: ShipOS = null

func _init(p_name: String, p_class: String) -> void:
	ship_name = p_name
	ship_class = p_class

func update(delta: float) -> void:
	# Update ship state
	_update_position(delta)
	_update_systems(delta)
	_update_weapons(delta)
	_update_crew_ai(delta)
	_update_shields(delta)

func _update_position(delta: float) -> void:
	# 3D Combat Movement
	# Get engine power modifier
	var engines_room = _get_room_by_type(Room.SystemType.ENGINES)
	var engine_power = 1.0
	if engines_room and engines_room.is_functional():
		engine_power = (engines_room.power_allocated / float(engines_room.max_power)) if engines_room.max_power > 0 else 0.0
		engine_power *= _get_room_effectiveness(engines_room)
	else:
		engine_power = 0.0

	# Apply rotation (turn_input)
	if turn_input != 0.0 and engine_power > 0.0:
		var turn_degrees = turn_rate * turn_input * engine_power * delta
		var rotation = Quaternion(Vector3.UP, deg_to_rad(turn_degrees))
		heading = rotation * heading
		heading = heading.normalized()

	# Apply thrust (acceleration in heading direction)
	if thrust_input != 0.0 and engine_power > 0.0:
		var thrust_force = thrust_input * acceleration * engine_power
		var accel_vector = heading * thrust_force
		velocity_3d += accel_vector * delta

	# Apply drag (slow down over time when not thrusting)
	var drag = 0.5  # Drag coefficient
	velocity_3d *= (1.0 - drag * delta)

	# Clamp to max speed
	var current_speed = velocity_3d.length()
	if current_speed > max_speed:
		velocity_3d = velocity_3d.normalized() * max_speed

	# Update position
	position += velocity_3d * delta

	# TODO: Galaxy travel (separate from combat movement)

func _update_systems(delta: float) -> void:
	# Update power allocation
	_recalculate_power()

func _update_weapons(delta: float) -> void:
	var weapons_room = _get_room_by_type(Room.SystemType.WEAPONS)
	var weapons_powered = weapons_room != null and weapons_room.is_functional()
	var weapons_effectiveness = _get_room_effectiveness(weapons_room) if weapons_powered else 0.0
	var crew_bonus = _get_crew_bonus_for_room(weapons_room, "skill_weapons")

	for weapon in weapons:
		var effective_delta = delta * weapons_effectiveness * (1.0 + crew_bonus)
		weapon.update(effective_delta, weapons_powered)

func _update_crew_ai(delta: float) -> void:
	# Crew repair damaged rooms
	for crew_member in crew:
		if not crew_member.is_alive() or not crew_member.current_room:
			continue

		var room = crew_member.current_room
		if room.health < 1.0:
			var repair_amount = crew_member.skill_repair * 0.05 * delta
			room.repair(repair_amount)

func _update_shields(delta: float) -> void:
	if shields >= shields_max:
		return

	var shield_room = _get_room_by_type(Room.SystemType.SHIELDS)
	if not shield_room or not shield_room.is_functional():
		return

	# Base recharge rate: 0.5 shields/sec per power bar
	var base_rate = shield_room.power_allocated * 0.5
	var effectiveness = _get_room_effectiveness(shield_room)
	var crew_bonus = _get_crew_bonus_for_room(shield_room, "skill_shields")

	var recharge_rate = base_rate * effectiveness * (1.0 + crew_bonus)
	shields = min(float(shields_max), shields + recharge_rate * delta)

# Power management
func _recalculate_power() -> void:
	var total_allocated = 0
	for room in rooms.values():
		total_allocated += room.power_allocated

	power_available = reactor_power - total_allocated

func allocate_power(room_name: String, power: int) -> bool:
	if not rooms.has(room_name):
		return false

	var room: Room = rooms[room_name]
	var power_change = power - room.power_allocated

	# Check if we have enough power
	if power_change > power_available:
		return false

	# Check room max power
	if power > room.max_power:
		return false

	room.power_allocated = power
	_recalculate_power()
	return true

# Helper functions
func _get_room_by_type(type: Room.SystemType) -> Room:
	for room in rooms.values():
		if room.system_type == type:
			return room
	return null

func _get_room_effectiveness(room: Room) -> float:
	if not room or not room.is_functional():
		return 0.0

	var effectiveness = 1.0

	# Fire reduces effectiveness to 50%
	if room.on_fire:
		effectiveness *= 0.5

	# Low health reduces effectiveness
	if room.health < 0.5:
		effectiveness *= room.health * 2.0  # Scale from 0.0 to 1.0

	return effectiveness

func _get_crew_bonus_for_room(room: Room, skill_name: String) -> float:
	if not room:
		return 0.0

	var total_bonus = 0.0
	for crew_member in room.crew_in_room:
		if not crew_member.is_alive():
			continue

		var skill_level = 0
		match skill_name:
			"skill_shields":
				skill_level = crew_member.skill_shields
			"skill_weapons":
				skill_level = crew_member.skill_weapons
			"skill_engines":
				skill_level = crew_member.skill_engines
			"skill_repair":
				skill_level = crew_member.skill_repair
			"skill_helm":
				skill_level = crew_member.skill_helm

		# Each skill level adds 10% bonus
		total_bonus += skill_level * 0.1

	return total_bonus

# Get evasion chance based on engines
func get_evasion() -> float:
	var engines_room = _get_room_by_type(Room.SystemType.ENGINES)
	if not engines_room or not engines_room.is_functional():
		return 0.0

	var base_evasion = engines_room.power_allocated * 0.05
	var effectiveness = _get_room_effectiveness(engines_room)
	var crew_bonus = _get_crew_bonus_for_room(engines_room, "skill_engines")

	return base_evasion * effectiveness * (1.0 + crew_bonus)

# Check if weapons can fire
func can_fire_weapons() -> bool:
	var weapons_room = _get_room_by_type(Room.SystemType.WEAPONS)
	return weapons_room != null and weapons_room.is_functional()

# Movement controls
func set_thrust(thrust: float) -> void:
	thrust_input = clamp(thrust, -1.0, 1.0)

func set_turn(turn: float) -> void:
	turn_input = clamp(turn, -1.0, 1.0)

func stop_movement() -> void:
	thrust_input = 0.0
	turn_input = 0.0

# Calculate intercept point for lead targeting
# Returns the point in space where a projectile should be aimed to hit a moving target
# Returns Vector3.ZERO if no solution (target too fast, out of range, etc.)
static func calculate_lead_target(shooter_pos: Vector3, target_pos: Vector3, target_vel: Vector3, projectile_speed: float) -> Vector3:
	if projectile_speed <= 0:
		return target_pos  # Instant hit, just aim at current position

	# Vector from shooter to target
	var to_target = target_pos - shooter_pos
	var distance = to_target.length()

	# If target is stationary, just return current position
	if target_vel.length() < 0.01:
		return target_pos

	# Solve quadratic equation for intercept time
	# |target_pos + target_vel * t - shooter_pos| = projectile_speed * t
	# Rearranging: a*t^2 + b*t + c = 0
	var a = target_vel.dot(target_vel) - projectile_speed * projectile_speed
	var b = 2.0 * to_target.dot(target_vel)
	var c = to_target.dot(to_target)

	var discriminant = b * b - 4.0 * a * c

	# No solution (target too fast to hit)
	if discriminant < 0:
		return Vector3.ZERO

	# Solve for t (time to intercept)
	var t1 = (-b + sqrt(discriminant)) / (2.0 * a)
	var t2 = (-b - sqrt(discriminant)) / (2.0 * a)

	# Use the smallest positive time
	var t = 0.0
	if t1 > 0 and t2 > 0:
		t = min(t1, t2)
	elif t1 > 0:
		t = t1
	elif t2 > 0:
		t = t2
	else:
		return Vector3.ZERO  # No positive solution

	# Calculate intercept point
	var intercept = target_pos + target_vel * t
	return intercept

# Get the direction to fire to hit a moving target
func get_firing_direction_to(target: Ship, projectile_speed: float) -> Vector3:
	var intercept = calculate_lead_target(position, target.position, target.velocity_3d, projectile_speed)
	if intercept == Vector3.ZERO:
		# No valid intercept, just aim at current position
		intercept = target.position

	var direction = (intercept - position).normalized()
	return direction

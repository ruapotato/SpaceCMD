extends Node

## Combat Manager - Orchestrates multi-ship battles
## Singleton that manages all ships, projectiles, and combat state
##
## Responsibilities:
## - Track all active ships by faction
## - Update nearby_ships arrays for all ShipOS instances
## - Spawn and manage projectiles
## - Collision detection and damage application
## - Victory/defeat condition checking

# Signals for game integration
signal ship_destroyed(ship: Ship, faction: String)
signal ship_added(ship: Ship, faction: String)
signal battle_won(winning_faction: String)
signal battle_lost()
signal projectile_spawned(projectile)
signal projectile_hit(projectile, target: Ship)
signal all_enemies_destroyed()

# Ship tracking by faction
var ships: Dictionary = {
	"player": [],
	"enemy": [],
	"neutral": []
}

# All ships flattened for easy iteration
var all_ships: Array[Ship] = []

# Active projectiles (untyped to avoid parse-time dependency)
var projectiles: Array = []

# Combat state
var battle_active: bool = false
var player_ship: Ship = null

# Configuration
var hit_radius: float = 50.0  # Collision detection radius
var nearby_distance: float = 1000.0  # Distance for "nearby" ships

func _ready():
	print("[CombatManager] Initialized")

func _process(delta: float):
	if not battle_active:
		return

	# Update all projectiles
	process_projectiles(delta)

	# Update nearby ships for all ShipOS instances
	update_nearby_ships()

	# Check victory conditions
	check_victory_conditions()

## Ship Management

func add_ship(ship: Ship, faction: String = "enemy") -> void:
	"""Register a ship in combat."""
	if faction not in ships:
		push_error("Invalid faction: %s" % faction)
		return

	if ship in all_ships:
		push_warning("Ship %s already in combat" % ship.name)
		return

	ships[faction].append(ship)
	all_ships.append(ship)

	if faction == "player":
		player_ship = ship

	print("[CombatManager] Added %s ship: %s" % [faction, ship.name])
	ship_added.emit(ship, faction)

func remove_ship(ship: Ship) -> void:
	"""Remove a ship from combat (destroyed or escaped)."""
	var faction = get_ship_faction(ship)
	if faction:
		ships[faction].erase(ship)
		all_ships.erase(ship)
		print("[CombatManager] Removed ship: %s" % ship.name)

func get_ship_faction(ship: Ship) -> String:
	"""Get the faction of a ship."""
	for faction in ships:
		if ship in ships[faction]:
			return faction
	return ""

func start_battle() -> void:
	"""Begin combat processing."""
	battle_active = true
	print("[CombatManager] Battle started!")
	print("  Player ships: %d" % ships["player"].size())
	print("  Enemy ships: %d" % ships["enemy"].size())

func end_battle() -> void:
	"""Stop combat processing."""
	battle_active = false
	projectiles.clear()
	print("[CombatManager] Battle ended")

func reset() -> void:
	"""Clear all ships and projectiles."""
	ships["player"].clear()
	ships["enemy"].clear()
	ships["neutral"].clear()
	all_ships.clear()
	projectiles.clear()
	player_ship = null
	battle_active = false
	print("[CombatManager] Reset complete")

## Nearby Ships Management

func update_nearby_ships() -> void:
	"""Update nearby_ships array for all ShipOS instances."""
	for ship in all_ships:
		if not ship.os:
			continue

		# Find all ships within range
		var nearby: Array = []
		for other_ship in all_ships:
			var distance = ship.position.distance_to(other_ship.position)
			if distance <= nearby_distance:
				nearby.append(other_ship)

		# Update ShipOS
		ship.os.nearby_ships = nearby

func get_nearby_ships(ship: Ship, max_distance: float = 0.0) -> Array[Ship]:
	"""Get all ships within range of the given ship."""
	if max_distance == 0.0:
		max_distance = nearby_distance

	var nearby: Array[Ship] = []
	for other_ship in all_ships:
		if other_ship == ship:
			continue
		var distance = ship.position.distance_to(other_ship.position)
		if distance <= max_distance:
			nearby.append(other_ship)

	return nearby

## Projectile Management

func spawn_projectile(
	owner: Ship,
	target: Ship,
	weapon: Weapon,
	weapon_idx: int = 0
):
	"""Spawn a projectile from a weapon firing."""
	# Load Projectile class dynamically
	const ProjectileClass = preload("res://core/combat/projectile.gd")
	var projectile = ProjectileClass.new(
		owner.position,
		target.position,
		weapon.damage,
		owner,
		target,
		weapon.weapon_name,
		300.0  # Speed
	)

	projectiles.append(projectile)

	print("[CombatManager] Projectile spawned: %s fires %s at %s (%.1f damage)" % [
		owner.name,
		weapon.weapon_name,
		target.name,
		weapon.damage
	])

	projectile_spawned.emit(projectile)
	return projectile

func process_projectiles(delta: float) -> void:
	"""Update all projectiles and check for hits."""
	var i = 0
	while i < projectiles.size():
		var projectile = projectiles[i]

		# Update projectile position
		if not projectile.update(delta):
			# Projectile expired
			projectiles.remove_at(i)
			continue

		# Check collision with all ships
		var hit = false
		for ship in all_ships:
			if projectile.check_hit(ship, hit_radius):
				# Hit!
				apply_damage(ship, projectile.damage, projectile.owner_ship)
				projectile_hit.emit(projectile, ship)
				projectiles.remove_at(i)
				hit = true
				break

		if not hit:
			i += 1

## Damage System

func apply_damage(target: Ship, damage: float, source: Ship = null) -> void:
	"""Apply damage to a ship, handling shields and hull."""
	var source_name = source.name if source else "unknown"

	# Apply damage to shields first
	if target.shields > 0:
		var shield_damage = min(damage, target.shields)
		target.shields -= shield_damage
		damage -= shield_damage
		print("[CombatManager] %s shields: %.1f → %.1f" % [
			target.name,
			target.shields + shield_damage,
			target.shields
		])

	# Remaining damage goes to hull
	if damage > 0:
		target.hull -= damage
		print("[CombatManager] %s hull: %.1f → %.1f" % [
			target.name,
			target.hull + damage,
			target.hull
		])

	# Check if ship destroyed
	if target.hull <= 0:
		handle_ship_destroyed(target, source)

func handle_ship_destroyed(ship: Ship, source: Ship = null) -> void:
	"""Handle a ship being destroyed."""
	var faction = get_ship_faction(ship)
	print("[CombatManager] %s destroyed! (%s faction)" % [ship.name, faction])

	ship_destroyed.emit(ship, faction)
	remove_ship(ship)

	# Kill all processes on the ship's OS
	if ship.os:
		for pid in ship.os.kernel.process_manager.processes.keys():
			ship.os.kill_process(pid)

## Victory Conditions

func check_victory_conditions() -> void:
	"""Check if battle is won or lost."""
	if not battle_active:
		return

	# Check if all enemies destroyed
	if ships["enemy"].size() == 0:
		print("[CombatManager] Victory! All enemies destroyed")
		all_enemies_destroyed.emit()
		battle_won.emit("player")
		end_battle()
		return

	# Check if player destroyed
	if ships["player"].size() == 0:
		print("[CombatManager] Defeat! Player destroyed")
		battle_lost.emit()
		end_battle()
		return

## Debug and Utility

func get_battle_status() -> String:
	"""Get current battle status as string."""
	var status = "[Combat Status]\n"
	status += "  Active: %s\n" % battle_active
	status += "  Player ships: %d\n" % ships["player"].size()
	status += "  Enemy ships: %d\n" % ships["enemy"].size()
	status += "  Neutral ships: %d\n" % ships["neutral"].size()
	status += "  Projectiles: %d\n" % projectiles.size()
	return status

func print_status() -> void:
	"""Print battle status to console."""
	print(get_battle_status())

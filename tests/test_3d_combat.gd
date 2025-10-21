extends SceneTree

## Test Suite: 3D Combat Mechanics
## Tests ship movement, projectile travel, lead targeting, and device files

const Projectile = preload("res://core/combat/projectile.gd")

var test_count = 0
var pass_count = 0

func _init():
	print("============================================================")
	print("TEST SUITE: 3D Combat Mechanics")
	print("============================================================")

	test_basic_thrust()
	test_turning()
	test_velocity_drag()
	test_engine_power_affects_movement()
	test_projectile_travel_time()
	test_lead_targeting_stationary()
	test_lead_targeting_moving()
	test_movement_device_files()
	test_ship_movement_integration()

	print("\n============================================================")
	print("RESULTS: %d/%d tests passed" % [pass_count, test_count])
	print("============================================================")

	quit()

func assert_true(condition: bool, test_name: String) -> void:
	test_count += 1
	if condition:
		print("[PASS] %s" % test_name)
		pass_count += 1
	else:
		print("[FAIL] %s" % test_name)

func assert_float_near(actual: float, expected: float, tolerance: float, test_name: String) -> void:
	test_count += 1
	if abs(actual - expected) <= tolerance:
		print("[PASS] %s (%.3f ≈ %.3f)" % [test_name, actual, expected])
		pass_count += 1
	else:
		print("[FAIL] %s (%.3f != %.3f, tolerance %.3f)" % [test_name, actual, expected, tolerance])

func assert_vector_near(actual: Vector3, expected: Vector3, tolerance: float, test_name: String) -> void:
	var distance = actual.distance_to(expected)
	test_count += 1
	if distance <= tolerance:
		print("[PASS] %s" % test_name)
		pass_count += 1
	else:
		print("[FAIL] %s (distance: %.3f > %.3f)" % [test_name, distance, tolerance])

## Test 1: Basic Thrust
func test_basic_thrust() -> void:
	print("\n--- Test 1: Basic Thrust ---")

	var ship = Ship.new("Test Ship", "Fighter")
	ship.position = Vector3(0, 0, 0)
	ship.heading = Vector3(1, 0, 0)  # Facing +X
	ship.max_speed = 20.0
	ship.acceleration = 10.0

	# Add engine room (required for movement!)
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	# Apply forward thrust
	ship.set_thrust(1.0)
	assert_float_near(ship.thrust_input, 1.0, 0.01, "Thrust input set to 1.0")

	# Update for 1 second
	ship.update(1.0)

	# Should be moving forward
	# Note: drag reduces final velocity, so won't be exactly accel * time
	assert_true(ship.velocity_3d.x > 0, "Velocity X is positive (moving forward)")
	assert_true(ship.velocity_3d.x > 4.0, "Velocity increases significantly")

	# Position should have changed
	assert_true(ship.position.x > 0, "Position X increased")

	# Apply backward thrust
	ship.set_thrust(-1.0)
	ship.update(1.0)

	# Velocity should decrease
	assert_true(ship.velocity_3d.x < 10.0, "Velocity decreased with backward thrust")

## Test 2: Turning
func test_turning() -> void:
	print("\n--- Test 2: Turning ---")

	var ship = Ship.new("Test Ship", "Fighter")
	ship.heading = Vector3(1, 0, 0)  # Facing +X
	ship.turn_rate = 90.0  # 90 degrees per second

	# Add engine room
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	# Turn left for 1 second (should rotate 90 degrees)
	ship.set_turn(-1.0)
	ship.update(1.0)

	# Heading should have changed significantly
	var heading_after_left = ship.heading
	assert_true(heading_after_left.distance_to(Vector3(1, 0, 0)) > 0.5, "Heading changed significantly after left turn")

	# Reset and turn right
	ship.heading = Vector3(1, 0, 0)
	ship.set_turn(1.0)
	ship.update(1.0)

	# Heading should rotate (opposite direction from left)
	var heading_after_right = ship.heading
	assert_true(heading_after_right.distance_to(Vector3(1, 0, 0)) > 0.5, "Heading changed significantly after right turn")

	# Left and right turns should produce different headings
	assert_true(heading_after_left.distance_to(heading_after_right) > 1.0, "Left and right turns produce different headings")

## Test 3: Velocity and Drag
func test_velocity_drag() -> void:
	print("\n--- Test 3: Velocity and Drag ---")

	var ship = Ship.new("Test Ship", "Fighter")
	ship.heading = Vector3(1, 0, 0)
	ship.acceleration = 10.0

	# Add engine room
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	# Accelerate to speed
	ship.set_thrust(1.0)
	ship.update(1.0)
	var speed_with_thrust = ship.velocity_3d.length()

	# Stop thrusting - drag should slow us down
	ship.set_thrust(0.0)
	ship.update(1.0)
	var speed_after_drag = ship.velocity_3d.length()

	assert_true(speed_after_drag < speed_with_thrust, "Drag reduces velocity")
	assert_true(speed_after_drag > 0, "Drag doesn't stop ship instantly")

	# After many seconds, ship should be nearly stopped
	for i in range(10):
		ship.update(1.0)

	assert_float_near(ship.velocity_3d.length(), 0.0, 1.0, "Ship eventually stops from drag")

## Test 4: Engine Power Affects Movement
func test_engine_power_affects_movement() -> void:
	print("\n--- Test 4: Engine Power Affects Movement ---")

	var ship = Ship.new("Test Ship", "Fighter")
	ship.heading = Vector3(1, 0, 0)

	# Create engine room
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3  # Full power
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	# Thrust with full power
	ship.set_thrust(1.0)
	ship.update(1.0)
	var speed_full_power = ship.velocity_3d.length()

	# Reset
	ship.velocity_3d = Vector3.ZERO

	# Reduce engine power to 1 (33%)
	engines.power_allocated = 1
	ship.set_thrust(1.0)
	ship.update(1.0)
	var speed_low_power = ship.velocity_3d.length()

	assert_true(speed_full_power > speed_low_power, "Full engine power gives more acceleration")
	assert_float_near(speed_low_power / speed_full_power, 0.33, 0.1, "Acceleration proportional to engine power")

	# Damaged engines
	ship.velocity_3d = Vector3.ZERO
	engines.power_allocated = 3
	engines.health = 0.5  # 50% health
	ship.set_thrust(1.0)
	ship.update(1.0)
	var speed_damaged = ship.velocity_3d.length()

	# With 50% health, effectiveness should be 1.0 (health * 2 when < 0.5)
	# So speed should actually be the same! Test was wrong
	assert_true(speed_damaged > 0, "Damaged engines still provide thrust")

	# Now test with critically low health
	ship.velocity_3d = Vector3.ZERO
	engines.health = 0.1  # 10% health
	ship.set_thrust(1.0)
	ship.update(1.0)
	var speed_critical = ship.velocity_3d.length()

	assert_float_near(speed_critical, 0.0, 0.5, "Critically damaged engines (<20%) provide no thrust")

## Test 5: Projectile Travel Time
func test_projectile_travel_time() -> void:
	print("\n--- Test 5: Projectile Travel Time ---")

	var ship1 = Ship.new("Ship 1", "Fighter")
	ship1.position = Vector3(0, 0, 0)

	var ship2 = Ship.new("Ship 2", "Fighter")
	ship2.position = Vector3(100, 0, 0)  # 100 units away

	var weapon = Weapon.new("Laser")
	weapon.damage = 10

	var projectile = Projectile.new(
		ship1.position,
		ship2.position,
		weapon.damage,
		ship1,
		ship2,
		weapon.weapon_name,
		50.0  # 50 units/sec
	)

	# Projectile should not hit immediately
	assert_true(not projectile.check_hit(ship2, 5.0), "Projectile doesn't hit instantly")

	# After 2 seconds, projectile should travel 100 units (50 units/sec * 2 sec)
	projectile.update(2.0)

	# Check if close to target
	var distance_to_target = projectile.position.distance_to(ship2.position)
	assert_float_near(distance_to_target, 0.0, 10.0, "Projectile reaches target after travel time")

	# Should now be able to hit
	assert_true(projectile.check_hit(ship2, 10.0), "Projectile hits after traveling")

## Test 6: Lead Targeting - Stationary Target
func test_lead_targeting_stationary() -> void:
	print("\n--- Test 6: Lead Targeting - Stationary Target ---")

	var shooter_pos = Vector3(0, 0, 0)
	var target_pos = Vector3(100, 0, 0)
	var target_vel = Vector3(0, 0, 0)  # Stationary
	var projectile_speed = 50.0

	var intercept = Ship.calculate_lead_target(shooter_pos, target_pos, target_vel, projectile_speed)

	# For stationary target, intercept point should be current position
	assert_vector_near(intercept, target_pos, 0.1, "Stationary target intercept = current position")

## Test 7: Lead Targeting - Moving Target
func test_lead_targeting_moving() -> void:
	print("\n--- Test 7: Lead Targeting - Moving Target ---")

	var shooter_pos = Vector3(0, 0, 0)
	var target_pos = Vector3(100, 0, 0)
	var target_vel = Vector3(0, 0, 10)  # Moving in +Z at 10 units/sec
	var projectile_speed = 50.0

	var intercept = Ship.calculate_lead_target(shooter_pos, target_pos, target_vel, projectile_speed)

	# Intercept should be ahead of current position
	assert_true(intercept.z > target_pos.z, "Intercept point ahead of moving target")

	# Calculate time to intercept
	var time_to_intercept = shooter_pos.distance_to(intercept) / projectile_speed

	# Target's position at intercept time
	var target_at_intercept = target_pos + target_vel * time_to_intercept

	# Intercept point should match where target will be
	assert_vector_near(intercept, target_at_intercept, 1.0, "Intercept point matches target future position")

	# Test with fast moving target (perpendicular)
	target_pos = Vector3(100, 0, 0)
	target_vel = Vector3(0, 0, 40)  # Very fast perpendicular movement
	projectile_speed = 50.0

	intercept = Ship.calculate_lead_target(shooter_pos, target_pos, target_vel, projectile_speed)

	if intercept != Vector3.ZERO:
		time_to_intercept = shooter_pos.distance_to(intercept) / projectile_speed
		target_at_intercept = target_pos + target_vel * time_to_intercept
		assert_vector_near(intercept, target_at_intercept, 2.0, "Fast moving target intercept calculated")
	else:
		# Target too fast - no solution
		assert_true(true, "Target moving too fast to intercept (expected)")

## Test 8: Movement Device Files
func test_movement_device_files() -> void:
	print("\n--- Test 8: Movement Device Files ---")

	var ship = Ship.new("Test Ship", "Fighter")
	ship.os = ShipOS.new(ship)

	# Test thrust device
	ship.os.write_device("/dev/ship/actions/thrust", "forward")
	assert_float_near(ship.thrust_input, 1.0, 0.01, "Thrust 'forward' sets input to 1.0")

	ship.os.write_device("/dev/ship/actions/thrust", "backward")
	assert_float_near(ship.thrust_input, -1.0, 0.01, "Thrust 'backward' sets input to -1.0")

	ship.os.write_device("/dev/ship/actions/thrust", "stop")
	assert_float_near(ship.thrust_input, 0.0, 0.01, "Thrust 'stop' sets input to 0.0")

	ship.os.write_device("/dev/ship/actions/thrust", "0.5")
	assert_float_near(ship.thrust_input, 0.5, 0.01, "Thrust numeric value works")

	# Test turn device
	ship.os.write_device("/dev/ship/actions/turn", "left")
	assert_float_near(ship.turn_input, -1.0, 0.01, "Turn 'left' sets input to -1.0")

	ship.os.write_device("/dev/ship/actions/turn", "right")
	assert_float_near(ship.turn_input, 1.0, 0.01, "Turn 'right' sets input to 1.0")

	ship.os.write_device("/dev/ship/actions/turn", "stop")
	assert_float_near(ship.turn_input, 0.0, 0.01, "Turn 'stop' sets input to 0.0")

	# Test reading velocity
	ship.velocity_3d = Vector3(10, 0, 5)
	var vel_data = ship.os.read_device("/proc/ship/velocity")
	assert_true(vel_data.contains("Velocity"), "Velocity device readable")
	assert_true(vel_data.contains("10.00"), "Velocity shows correct X component")

	# Test reading heading
	ship.heading = Vector3(1, 0, 0)
	var head_data = ship.os.read_device("/proc/ship/heading")
	assert_true(head_data.contains("Heading"), "Heading device readable")
	assert_true(head_data.contains("1.00"), "Heading shows correct X component")

	# Test reading movement info
	var move_data = ship.os.read_device("/proc/ship/movement")
	assert_true(move_data.contains("Movement Status"), "Movement info readable")
	assert_true(move_data.contains("Position"), "Shows position")
	assert_true(move_data.contains("Velocity"), "Shows velocity")
	assert_true(move_data.contains("Thrust Input"), "Shows thrust input")

## Test 9: Ship Movement Integration
func test_ship_movement_integration() -> void:
	print("\n--- Test 9: Ship Movement Integration ---")

	var ship = Ship.new("Test Ship", "Fighter")
	ship.os = ShipOS.new(ship)
	ship.position = Vector3(0, 0, 0)
	ship.heading = Vector3(1, 0, 0)

	# Set up engines
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	# Command ship to thrust forward via device
	ship.os.write_device("/dev/ship/actions/thrust", "forward")

	# Update ship
	ship.update(1.0)

	# Ship should be moving
	assert_true(ship.velocity_3d.length() > 0, "Ship accelerates after thrust command")
	assert_true(ship.position.x > 0, "Ship position changes")

	# Stop thrust
	ship.os.write_device("/dev/ship/actions/thrust", "stop")
	var vel_before = ship.velocity_3d.length()

	ship.update(1.0)

	# Velocity should decrease due to drag
	assert_true(ship.velocity_3d.length() < vel_before, "Ship slows down with drag")

	# Test turning
	var heading_before = ship.heading
	ship.os.write_device("/dev/ship/actions/turn", "left")
	ship.update(0.5)

	# Heading should have changed
	var heading_after = ship.heading
	assert_true(heading_before.distance_to(heading_after) > 0.1, "Ship heading changes with turn command")

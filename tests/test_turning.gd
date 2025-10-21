extends SceneTree

## Test Suite: Ship Turning Mechanics
## Verifies that ships can rotate toward targets

var test_count = 0
var pass_count = 0

func _init():
	print("============================================================")
	print("TEST SUITE: Ship Turning Mechanics")
	print("============================================================")

	test_manual_turn()
	test_turn_device()
	test_turn_toward_target()
	test_turn_direction_device()

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

## Test 1: Manual Turn Input
func test_manual_turn() -> void:
	print("\n--- Test 1: Manual Turn Input ---")

	# Create ship
	var ship = Ship.new("Turner", "Fighter")
	ship.position = Vector3(0, 0, 0)
	ship.heading = Vector3(1, 0, 0)  # Facing +X

	# Add engine room for turn power
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	# Set turn input
	ship.set_turn(1.0)  # Turn right

	print("Initial heading: %s" % ship.heading)
	print("Turn input: %.2f" % ship.turn_input)

	# Update ship to apply rotation
	for i in range(10):
		ship.update(0.1)  # 1 second total

	print("Final heading: %s" % ship.heading)

	# Verify turn input was set
	assert_true(ship.turn_input == 1.0, "Turn input set correctly")

	# Verify heading changed (rotated)
	var initial_heading = Vector3(1, 0, 0)
	var heading_changed = not ship.heading.is_equal_approx(initial_heading)
	assert_true(heading_changed, "Ship heading rotated")

## Test 2: Turn Device Write
func test_turn_device() -> void:
	print("\n--- Test 2: Turn Device Write ---")

	# Create ship with OS
	var ship = Ship.new("DeviceTurner", "Cruiser")
	ship.position = Vector3(0, 0, 0)
	ship.heading = Vector3(1, 0, 0)
	ship.os = ShipOS.new(ship)

	# Add engines
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	ship.rooms["Engines"] = engines

	print("Writing 'right' to /dev/ship/actions/turn...")

	# Write to turn device via OS
	var turn_fd = ship.os.kernel.sys_open(0, '/dev/ship/actions/turn', ship.os.kernel.O_WRONLY)
	if turn_fd >= 0:
		ship.os.kernel.sys_write(0, turn_fd, "right".to_utf8_buffer())
		ship.os.kernel.sys_close(0, turn_fd)

	print("Turn input after device write: %.2f" % ship.turn_input)

	# Verify turn was set via device
	assert_true(ship.turn_input == 1.0, "Turn device sets turn input")

## Test 3: Calculate Turn Toward Target
func test_turn_toward_target() -> void:
	print("\n--- Test 3: Calculate Turn Toward Target ---")

	# Create ship facing +X
	var ship = Ship.new("Hunter", "Fighter")
	ship.position = Vector3(0, 0, 0)
	ship.heading = Vector3(1, 0, 0)  # Facing +X

	# Create target to the right (+Z)
	var target = Ship.new("Target", "Scout")
	target.position = Vector3(50, 0, 50)  # 45 degrees to the right

	# Calculate direction to target
	var to_target = (target.position - ship.position).normalized()
	print("Ship heading: %s" % ship.heading)
	print("Direction to target: %s" % to_target)

	# Calculate if target is to the left or right
	# Use cross product: heading × to_target
	# If Y component > 0, target is to the left (turn left)
	# If Y component < 0, target is to the right (turn right)
	var cross = ship.heading.cross(to_target)
	var turn_direction = sign(cross.y)

	print("Cross product Y: %.3f" % cross.y)
	print("Turn direction: %.0f (1=left, -1=right)" % turn_direction)

	# Target is at +Z relative to ship facing +X, so turn should be right (-1)
	assert_true(turn_direction < 0, "Correctly identifies target is to the right")

	# Calculate angle to target (dot product)
	var dot = ship.heading.dot(to_target)
	var angle_rad = acos(clamp(dot, -1.0, 1.0))
	var angle_deg = rad_to_deg(angle_rad)

	print("Angle to target: %.1f degrees" % angle_deg)

	# Should be approximately 45 degrees
	assert_true(abs(angle_deg - 45.0) < 1.0, "Angle to target is ~45 degrees")

## Test 4: Turn Direction Device
func test_turn_direction_device() -> void:
	print("\n--- Test 4: Turn Direction Device ---")

	# Create ship with OS facing +X
	var ship = Ship.new("Navigator", "Cruiser")
	ship.position = Vector3(0, 0, 0)
	ship.heading = Vector3(1, 0, 0)  # Facing +X
	ship.os = ShipOS.new(ship)

	# Create target to the right (+Z)
	var target = Ship.new("Target", "Scout")
	target.position = Vector3(50, 0, 50)  # 45 degrees to the right

	# Add target to nearby ships and set as current target
	ship.os.nearby_ships = [ship, target]
	ship.os.current_target = target

	# Read turn_direction device
	print("Reading /proc/ship/turn_direction...")
	var turn_fd = ship.os.kernel.sys_open(0, '/proc/ship/turn_direction', ship.os.kernel.O_RDONLY)
	if turn_fd >= 0:
		var turn_data = ship.os.kernel.sys_read(0, turn_fd, 1024)
		ship.os.kernel.sys_close(0, turn_fd)
		var turn_str = turn_data.get_string_from_utf8()

		print("Turn direction output:")
		print(turn_str)

		# Parse the output
		var lines = turn_str.split("\n")
		var turn_cmd = ""
		var angle = 0.0

		for line in lines:
			if "Turn:" in line:
				var parts = line.split(":")
				if parts.size() >= 2:
					turn_cmd = parts[1].strip_edges()
			elif "Angle:" in line:
				var parts = line.split(":")
				if parts.size() >= 2:
					var angle_str = parts[1].strip_edges().split(" ")[0]
					angle = angle_str.to_float()

		print("Parsed - Turn command: %s, Angle: %.1f degrees" % [turn_cmd, angle])

		# Target is to the left (toward +Z), so turn command should be "left"
		assert_true(turn_cmd == "left", "Turn direction device says 'left'")

		# Angle should be ~45 degrees
		assert_true(abs(angle - 45.0) < 1.0, "Turn direction device reports ~45 degree angle")

	# Test 4b: Target directly ahead (should be stop or very small angle)
	print("\n--- Test 4b: Target Directly Ahead ---")
	target.position = Vector3(100, 0, 0)  # Directly ahead

	turn_fd = ship.os.kernel.sys_open(0, '/proc/ship/turn_direction', ship.os.kernel.O_RDONLY)
	if turn_fd >= 0:
		var turn_data = ship.os.kernel.sys_read(0, turn_fd, 1024)
		ship.os.kernel.sys_close(0, turn_fd)
		var turn_str = turn_data.get_string_from_utf8()

		var lines = turn_str.split("\n")
		var turn_cmd = ""
		var angle = 0.0

		for line in lines:
			if "Turn:" in line:
				var parts = line.split(":")
				if parts.size() >= 2:
					turn_cmd = parts[1].strip_edges()
			elif "Angle:" in line:
				var parts = line.split(":")
				if parts.size() >= 2:
					var angle_str = parts[1].strip_edges().split(" ")[0]
					angle = angle_str.to_float()

		print("Target ahead - Turn command: %s, Angle: %.1f degrees" % [turn_cmd, angle])

		# Target is directly ahead, turn should be "stop" (within 2 degree threshold)
		assert_true(turn_cmd == "stop", "Turn direction device says 'stop' when aligned")

		# Angle should be ~0 degrees
		assert_true(abs(angle) < 1.0, "Turn direction device reports ~0 degree angle when aligned")

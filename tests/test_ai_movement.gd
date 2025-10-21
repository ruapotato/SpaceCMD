extends SceneTree

## Test Suite: AI Movement
## Verifies that AI scripts actually make ships move

var test_count = 0
var pass_count = 0

func _init():
	print("============================================================")
	print("TEST SUITE: AI Movement")
	print("============================================================")

	test_aggressive_charges()
	test_coward_flees()
	test_defensive_maintains_range()
	test_balanced_adapts()
	test_boss_phases()

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

## Test 1: Aggressive AI Charges Forward
func test_aggressive_charges() -> void:
	print("\n--- Test 1: Aggressive AI Charges Toward Enemy ---")

	# Create aggressive ship
	var aggro_ship = Ship.new("Aggressor", "Fighter")
	aggro_ship.position = Vector3(0, 0, 0)
	aggro_ship.heading = Vector3(1, 0, 0)
	aggro_ship.os = ShipOS.new(aggro_ship)

	# Add engine room
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	aggro_ship.rooms["Engines"] = engines

	# Add weapons for power allocation
	var weapons_room = Room.new("Weapons", Room.SystemType.WEAPONS, 1, 0)
	weapons_room.max_power = 4
	aggro_ship.rooms["Weapons"] = weapons_room

	# Add weapon
	var weapon = Weapon.new("Laser")
	weapon.charge = 1.0
	aggro_ship.weapons.append(weapon)

	# Create target ship
	var target = Ship.new("Target", "Cruiser")
	target.position = Vector3(100, 0, 0)  # 100 units away
	aggro_ship.os.nearby_ships = [aggro_ship, target]

	# Load aggressive AI
	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/aggressive.poo")
	aggro_ship.os.vfs.create_file("/bin/aggressive.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Aggressive AI...")
	var pid = aggro_ship.os.execute_command("/bin/aggressive.poo")

	# Record initial state
	var initial_pos = aggro_ship.position
	var initial_thrust = aggro_ship.thrust_input

	# Update ship for a few cycles to let AI run and physics update
	for i in range(10):
		aggro_ship.update(0.1)  # 0.1 sec per update = 1 second total

	print("Initial position: %s" % initial_pos)
	print("Final position: %s" % aggro_ship.position)
	print("Thrust input: %.2f" % aggro_ship.thrust_input)
	print("Velocity: %s" % aggro_ship.velocity_3d)

	# Verify AI set thrust forward
	assert_true(aggro_ship.thrust_input > 0, "Aggressive AI sets forward thrust")

	# Verify ship moved
	assert_true(aggro_ship.position.distance_to(initial_pos) > 0.1, "Ship position changed")

	# Verify ship is moving forward (velocity in +X direction)
	assert_true(aggro_ship.velocity_3d.length() > 0, "Ship has velocity")

## Test 2: Coward AI Flees
func test_coward_flees() -> void:
	print("\n--- Test 2: Coward AI Flees From Enemy ---")

	# Create coward ship
	var coward_ship = Ship.new("Coward", "Scout")
	coward_ship.position = Vector3(0, 0, 0)
	coward_ship.heading = Vector3(1, 0, 0)
	coward_ship.os = ShipOS.new(coward_ship)

	# Add engine room
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	coward_ship.rooms["Engines"] = engines

	# Add shields room for power allocation
	var shields_room = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields_room.max_power = 3
	coward_ship.rooms["Shields"] = shields_room

	# Add weapon
	var weapon = Weapon.new("Laser")
	weapon.charge = 1.0
	coward_ship.weapons.append(weapon)

	# Create enemy ship nearby (within SAFE_DISTANCE of 100)
	var enemy = Ship.new("Enemy", "Fighter")
	enemy.position = Vector3(50, 0, 0)  # 50 units away - too close!
	coward_ship.os.nearby_ships = [coward_ship, enemy]

	# Load coward AI
	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/coward.poo")
	coward_ship.os.vfs.create_file("/bin/coward.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Coward AI...")
	var pid = coward_ship.os.execute_command("/bin/coward.poo")

	# Record initial state
	var initial_pos = coward_ship.position
	var initial_thrust = coward_ship.thrust_input

	# Update ship for a few cycles
	for i in range(10):
		coward_ship.update(0.1)

	print("Initial position: %s" % initial_pos)
	print("Final position: %s" % coward_ship.position)
	print("Thrust input: %.2f" % coward_ship.thrust_input)
	print("Velocity: %s" % coward_ship.velocity_3d)

	# Verify AI set thrust backward (negative)
	assert_true(coward_ship.thrust_input < 0, "Coward AI sets backward thrust")

	# Verify ship moved
	assert_true(coward_ship.position.distance_to(initial_pos) > 0.1, "Ship position changed")

	# Verify ship has velocity (fleeing)
	assert_true(coward_ship.velocity_3d.length() > 0, "Ship has velocity")

## Test 3: Defensive AI Maintains Optimal Range
func test_defensive_maintains_range() -> void:
	print("\n--- Test 3: Defensive AI Maintains Optimal Range ---")

	# Create defensive ship
	var defensive_ship = Ship.new("Defender", "Cruiser")
	defensive_ship.position = Vector3(0, 0, 0)
	defensive_ship.heading = Vector3(1, 0, 0)
	defensive_ship.os = ShipOS.new(defensive_ship)

	# Add rooms
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	defensive_ship.rooms["Engines"] = engines

	var shields_room = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields_room.max_power = 3
	defensive_ship.rooms["Shields"] = shields_room

	var weapons_room = Room.new("Weapons", Room.SystemType.WEAPONS, 2, 0)
	weapons_room.max_power = 4
	defensive_ship.rooms["Weapons"] = weapons_room

	# Add weapon
	var weapon = Weapon.new("Laser")
	weapon.charge = 1.0
	defensive_ship.weapons.append(weapon)

	# Test scenario 1: Enemy too close (should back up)
	var enemy_close = Ship.new("Enemy", "Fighter")
	enemy_close.position = Vector3(40, 0, 0)  # 40 units - too close for optimal range (70)
	defensive_ship.os.nearby_ships = [defensive_ship, enemy_close]

	# Load defensive AI
	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/defensive.poo")
	defensive_ship.os.vfs.create_file("/bin/defensive.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Defensive AI (enemy too close)...")
	var pid = defensive_ship.os.execute_command("/bin/defensive.poo")

	# Update
	for i in range(5):
		defensive_ship.update(0.1)

	print("Enemy distance: 40 units (too close)")
	print("Thrust input: %.2f" % defensive_ship.thrust_input)

	# Should retreat when too close
	assert_true(defensive_ship.thrust_input <= 0, "Defensive AI backs up when enemy too close")

## Test 4: Balanced AI Adapts to Situation
func test_balanced_adapts() -> void:
	print("\n--- Test 4: Balanced AI Adapts Position ---")

	# Create balanced ship with advantage
	var balanced_ship = Ship.new("Balanced", "Cruiser")
	balanced_ship.position = Vector3(0, 0, 0)
	balanced_ship.heading = Vector3(1, 0, 0)
	balanced_ship.hull = 100.0
	balanced_ship.hull_max = 100.0
	balanced_ship.shields = 50.0
	balanced_ship.shields_max = 50
	balanced_ship.os = ShipOS.new(balanced_ship)

	# Add rooms
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	balanced_ship.rooms["Engines"] = engines

	var shields_room = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields_room.max_power = 3
	balanced_ship.rooms["Shields"] = shields_room

	var weapons_room = Room.new("Weapons", Room.SystemType.WEAPONS, 2, 0)
	weapons_room.max_power = 4
	balanced_ship.rooms["Weapons"] = weapons_room

	# Add weapon
	var weapon = Weapon.new("Laser")
	weapon.charge = 1.0
	balanced_ship.weapons.append(weapon)

	# Create damaged enemy (we have advantage)
	var enemy = Ship.new("Enemy", "Fighter")
	enemy.position = Vector3(80, 0, 0)  # 80 units away
	enemy.hull = 30.0
	enemy.hull_max = 100.0
	enemy.shields = 0.0
	enemy.shields_max = 20
	balanced_ship.os.nearby_ships = [balanced_ship, enemy]

	# Load balanced AI
	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/balanced.poo")
	balanced_ship.os.vfs.create_file("/bin/balanced.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Balanced AI (we have advantage)...")
	var pid = balanced_ship.os.execute_command("/bin/balanced.poo")

	# Update
	for i in range(5):
		balanced_ship.update(0.1)

	print("Our health: 150/150 (100%)")
	print("Enemy health: 30/120 (25%)")
	print("Thrust input: %.2f" % balanced_ship.thrust_input)

	# Should advance when we have advantage and enemy is far
	assert_true(balanced_ship.thrust_input > 0, "Balanced AI advances when it has advantage")

## Test 5: Boss AI Phase-Based Movement
func test_boss_phases() -> void:
	print("\n--- Test 5: Boss AI Phase-Based Movement ---")

	# Create boss ship in Phase 1 (high health)
	var boss_ship = Ship.new("Boss", "Battleship")
	boss_ship.position = Vector3(0, 0, 0)
	boss_ship.heading = Vector3(1, 0, 0)
	boss_ship.hull = 100.0
	boss_ship.hull_max = 100.0
	boss_ship.shields = 50.0
	boss_ship.shields_max = 50
	boss_ship.os = ShipOS.new(boss_ship)

	# Add rooms
	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 3
	engines.health = 1.0
	boss_ship.rooms["Engines"] = engines

	var shields_room = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields_room.max_power = 4
	boss_ship.rooms["Shields"] = shields_room

	var weapons_room = Room.new("Weapons", Room.SystemType.WEAPONS, 2, 0)
	weapons_room.max_power = 4
	boss_ship.rooms["Weapons"] = weapons_room

	# Add weapon
	var weapon = Weapon.new("Heavy Laser")
	weapon.charge = 1.0
	boss_ship.weapons.append(weapon)

	# Create player ship
	var player = Ship.new("Player", "Cruiser")
	player.position = Vector3(100, 0, 0)
	boss_ship.os.nearby_ships = [boss_ship, player]

	# Load boss AI
	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/boss.poo")
	boss_ship.os.vfs.create_file("/bin/boss.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Boss AI (Phase 1: 100% hull)...")
	var pid = boss_ship.os.execute_command("/bin/boss.poo")

	# Update
	for i in range(5):
		boss_ship.update(0.1)

	print("Boss hull: 100% (Phase 1 - Aggressive)")
	print("Thrust input: %.2f" % boss_ship.thrust_input)

	# Phase 1 should charge forward
	assert_true(boss_ship.thrust_input > 0, "Boss AI Phase 1 charges forward")

	# Test Phase 3 (damaged, should retreat)
	print("\n--- Test 5b: Boss AI Phase 3 (Damaged) ---")
	var boss_ship2 = Ship.new("Boss2", "Battleship")
	boss_ship2.position = Vector3(0, 0, 0)
	boss_ship2.heading = Vector3(1, 0, 0)
	boss_ship2.hull = 30.0  # 30% hull - Phase 3
	boss_ship2.hull_max = 100.0
	boss_ship2.shields = 10.0
	boss_ship2.shields_max = 50
	boss_ship2.os = ShipOS.new(boss_ship2)

	# Add rooms
	var engines2 = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines2.max_power = 3
	engines2.power_allocated = 3
	engines2.health = 1.0
	boss_ship2.rooms["Engines"] = engines2

	var shields_room2 = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields_room2.max_power = 4
	boss_ship2.rooms["Shields"] = shields_room2

	var weapons_room2 = Room.new("Weapons", Room.SystemType.WEAPONS, 2, 0)
	weapons_room2.max_power = 4
	boss_ship2.rooms["Weapons"] = weapons_room2

	var weapon2 = Weapon.new("Heavy Laser")
	weapon2.charge = 1.0
	boss_ship2.weapons.append(weapon2)

	var player2 = Ship.new("Player", "Cruiser")
	player2.position = Vector3(60, 0, 0)
	boss_ship2.os.nearby_ships = [boss_ship2, player2]

	boss_ship2.os.vfs.create_file("/bin/boss.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Boss AI (Phase 3: 30% hull)...")
	var pid2 = boss_ship2.os.execute_command("/bin/boss.poo")

	for i in range(5):
		boss_ship2.update(0.1)

	print("Boss hull: 30% (Phase 3 - Defensive)")
	print("Thrust input: %.2f" % boss_ship2.thrust_input)

	# Phase 3 should retreat
	assert_true(boss_ship2.thrust_input < 0, "Boss AI Phase 3 retreats to recharge")

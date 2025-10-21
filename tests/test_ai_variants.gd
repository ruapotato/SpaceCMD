extends SceneTree

## Test Suite: AI Variants
## Tests all 5 AI personalities: hostile, aggressive, defensive, balanced, coward, boss

var test_count = 0
var pass_count = 0

func _init():
	print("============================================================")
	print("TEST SUITE: AI Variants")
	print("============================================================")

	test_aggressive_ai()
	test_defensive_ai()
	test_balanced_ai()
	test_coward_ai()
	test_boss_ai_phases()

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

func assert_contains(text: String, substring: String, test_name: String) -> void:
	test_count += 1
	if substring in text:
		print("[PASS] %s" % test_name)
		pass_count += 1
	else:
		print("[FAIL] %s (expected '%s' in text)" % [test_name, substring])

## Helper: Create a test ship with rooms
func create_test_ship(ship_name: String, hull_percent: float = 1.0) -> Ship:
	var ship = Ship.new(ship_name, "Test")
	ship.hull = ship.hull_max * hull_percent
	ship.shields = 0.0
	ship.shields_max = 4
	ship.reactor_power = 8
	ship.galaxy_position = 800.0

	# Create rooms for power allocation
	var weapons_room = Room.new("Weapons", Room.SystemType.WEAPONS, 0, 0)
	weapons_room.max_power = 4
	var shields_room = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields_room.max_power = 3
	var engines_room = Room.new("Engines", Room.SystemType.ENGINES, 2, 0)
	engines_room.max_power = 3

	ship.rooms["Weapons"] = weapons_room
	ship.rooms["Shields"] = shields_room
	ship.rooms["Engines"] = engines_room

	# Add a weapon
	var weapon = Weapon.new("Test Laser")
	weapon.damage = 10
	weapon.charge = 1.0  # Ready
	weapon.cooldown_time = 3.0
	ship.weapons.append(weapon)

	return ship

## Helper: Create enemy ship
func create_enemy_ship() -> Ship:
	var enemy = Ship.new("Target Ship", "Enemy")
	enemy.hull = 20.0
	enemy.hull_max = 30.0
	enemy.shields = 2.0
	enemy.shields_max = 4
	enemy.galaxy_position = 805.0  # 5 units away
	return enemy

## Test 1: Aggressive AI
func test_aggressive_ai() -> void:
	print("\n--- Test 1: Aggressive AI ---")

	var ship = create_test_ship("Aggressive Ship")
	ship.os = ShipOS.new(ship)

	var enemy = create_enemy_ship()
	ship.os.nearby_ships = [ship, enemy]

	# Load and run aggressive AI
	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/aggressive.poo")
	ship.os.vfs.create_file("/bin/aggressive.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Aggressive AI...")
	var pid = ship.os.execute_command("/bin/aggressive.poo")

	# Check power allocation
	var weapons_room = ship.rooms["Weapons"]
	var shields_room = ship.rooms["Shields"]

	assert_true(weapons_room.power_allocated >= 3, "Aggressive: Allocates max power to weapons")
	assert_true(shields_room.power_allocated <= 1, "Aggressive: Minimal shields")

	# Check if target was acquired
	var target = ship.os.current_target
	assert_true(target != null, "Aggressive: Acquires target")

	# Check weapon state (should have fired)
	var weapon = ship.weapons[0]
	var fired = weapon.charge < 1.0
	assert_true(fired, "Aggressive: Fires weapons aggressively")

## Test 2: Defensive AI
func test_defensive_ai() -> void:
	print("\n--- Test 2: Defensive AI ---")

	# Test with low shields (should hold fire)
	var ship = create_test_ship("Defensive Ship")
	ship.shields = 1.0  # 25% shields
	ship.os = ShipOS.new(ship)

	var enemy = create_enemy_ship()
	ship.os.nearby_ships = [ship, enemy]

	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/defensive.poo")
	ship.os.vfs.create_file("/bin/defensive.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Defensive AI (low shields)...")
	var pid = ship.os.execute_command("/bin/defensive.poo")

	# Check power allocation - should prioritize shields
	var shields_room = ship.rooms["Shields"]
	assert_true(shields_room.power_allocated >= 2, "Defensive: Prioritizes shields when low")

	# Weapon should NOT have fired (shields too low)
	var weapon = ship.weapons[0]
	assert_true(weapon.charge >= 1.0, "Defensive: Holds fire when shields low")

	# Test with good shields (should fight)
	var ship2 = create_test_ship("Defensive Ship 2")
	ship2.shields = 3.5  # 87% shields
	ship2.os = ShipOS.new(ship2)
	ship2.os.nearby_ships = [ship2, enemy]
	ship2.os.vfs.create_file("/bin/defensive.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Defensive AI (good shields)...")
	pid = ship2.os.execute_command("/bin/defensive.poo")

	# Should fire now
	var weapon2 = ship2.weapons[0]
	var fired = weapon2.charge < 1.0
	assert_true(fired, "Defensive: Fires when shields adequate")

## Test 3: Balanced AI
func test_balanced_ai() -> void:
	print("\n--- Test 3: Balanced AI ---")

	# Test balanced situation
	var ship = create_test_ship("Balanced Ship", 0.8)  # 80% hull
	ship.shields = 2.0  # 50% shields
	ship.os = ShipOS.new(ship)

	var enemy = create_enemy_ship()
	enemy.shields = 2.0  # Even match
	ship.os.nearby_ships = [ship, enemy]

	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/balanced.poo")
	ship.os.vfs.create_file("/bin/balanced.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Balanced AI (even match)...")
	var pid = ship.os.execute_command("/bin/balanced.poo")

	# Should have balanced power
	var weapons_room = ship.rooms["Weapons"]
	var shields_room = ship.rooms["Shields"]
	assert_true(weapons_room.power_allocated >= 1, "Balanced: Allocates power to weapons")
	assert_true(shields_room.power_allocated >= 1, "Balanced: Allocates power to shields")

	# Test advantage situation (enemy weak)
	var ship2 = create_test_ship("Balanced Ship 2", 1.0)
	ship2.shields = 4.0  # Full shields
	ship2.os = ShipOS.new(ship2)

	var weak_enemy = create_enemy_ship()
	weak_enemy.hull = 5.0  # 16% hull - very weak
	weak_enemy.shields = 0.0  # No shields
	ship2.os.nearby_ships = [ship2, weak_enemy]

	ship2.os.vfs.create_file("/bin/balanced.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Balanced AI (we have advantage)...")
	pid = ship2.os.execute_command("/bin/balanced.poo")

	# Should be aggressive when we have advantage
	var weapons_room2 = ship2.rooms["Weapons"]
	assert_true(weapons_room2.power_allocated >= 2, "Balanced: Goes offensive when advantaged")

## Test 4: Coward AI
func test_coward_ai() -> void:
	print("\n--- Test 4: Coward AI ---")

	var ship = create_test_ship("Coward Ship")
	ship.os = ShipOS.new(ship)

	var enemy = create_enemy_ship()
	enemy.galaxy_position = 808.0  # 8 units away (close)
	ship.os.nearby_ships = [ship, enemy]

	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/coward.poo")
	ship.os.vfs.create_file("/bin/coward.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Coward AI...")
	var pid = ship.os.execute_command("/bin/coward.poo")

	# Should prioritize engines and shields, not weapons
	var engines_room = ship.rooms["Engines"]
	var weapons_room = ship.rooms["Weapons"]

	assert_true(engines_room.power_allocated >= 2, "Coward: Prioritizes engines for escape")
	assert_true(weapons_room.power_allocated <= 1, "Coward: Minimal weapons")

	# Should try to jump away (ship.is_traveling should be true)
	assert_true(ship.is_traveling, "Coward: Initiates jump to flee")

	# Test cornered situation (very close)
	var ship2 = create_test_ship("Cornered Coward")
	ship2.os = ShipOS.new(ship2)
	var close_enemy = create_enemy_ship()
	close_enemy.galaxy_position = 803.0  # 3 units - within weapon range
	ship2.os.nearby_ships = [ship2, close_enemy]

	ship2.os.vfs.create_file("/bin/coward.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Coward AI (cornered)...")
	pid = ship2.os.execute_command("/bin/coward.poo")

	# When cornered, should fight back
	var weapon2 = ship2.weapons[0]
	var fired = weapon2.charge < 1.0
	assert_true(fired, "Coward: Fights back when cornered")

## Test 5: Boss AI Multi-Phase
func test_boss_ai_phases() -> void:
	print("\n--- Test 5: Boss AI Multi-Phase ---")

	var ai_script = FileAccess.get_file_as_string("res://scripts/ai/boss.poo")

	# Phase 1: High hull (aggressive)
	var boss1 = create_test_ship("Boss Phase 1", 0.9)  # 90% hull
	boss1.os = ShipOS.new(boss1)
	var enemy = create_enemy_ship()
	boss1.os.nearby_ships = [boss1, enemy]
	boss1.os.vfs.create_file("/bin/boss.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Boss AI - Phase 1 (90% hull)...")
	var pid = boss1.os.execute_command("/bin/boss.poo")

	var weapons_room = boss1.rooms["Weapons"]
	assert_true(weapons_room.power_allocated >= 3, "Boss Phase 1: Aggressive (max weapons)")

	# Phase 2: Medium hull (balanced)
	var boss2 = create_test_ship("Boss Phase 2", 0.6)  # 60% hull
	boss2.os = ShipOS.new(boss2)
	boss2.os.nearby_ships = [boss2, enemy]
	boss2.os.vfs.create_file("/bin/boss.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Boss AI - Phase 2 (60% hull)...")
	pid = boss2.os.execute_command("/bin/boss.poo")

	var weapons_room2 = boss2.rooms["Weapons"]
	var shields_room2 = boss2.rooms["Shields"]
	assert_true(weapons_room2.power_allocated >= 2, "Boss Phase 2: Balanced weapons")
	assert_true(shields_room2.power_allocated >= 2, "Boss Phase 2: Balanced shields")

	# Phase 3: Low hull (defensive)
	var boss3 = create_test_ship("Boss Phase 3", 0.3)  # 30% hull
	boss3.os = ShipOS.new(boss3)
	boss3.os.nearby_ships = [boss3, enemy]
	boss3.os.vfs.create_file("/bin/boss.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Boss AI - Phase 3 (30% hull)...")
	pid = boss3.os.execute_command("/bin/boss.poo")

	var shields_room3 = boss3.rooms["Shields"]
	assert_true(shields_room3.power_allocated >= 3, "Boss Phase 3: Defensive (max shields)")

	# Phase 4: Critical hull (berserker)
	var boss4 = create_test_ship("Boss Phase 4", 0.15)  # 15% hull
	boss4.os = ShipOS.new(boss4)
	boss4.os.nearby_ships = [boss4, enemy]
	boss4.os.vfs.create_file("/bin/boss.poo", 0x1ED, 0, 0, ai_script.to_utf8_buffer())

	print("Running Boss AI - Phase 4 (15% hull - BERSERKER)...")
	pid = boss4.os.execute_command("/bin/boss.poo")

	var weapons_room4 = boss4.rooms["Weapons"]
	var shields_room4 = boss4.rooms["Shields"]
	assert_true(weapons_room4.power_allocated >= 4, "Boss Phase 4: Berserker (ALL weapons)")
	assert_true(shields_room4.power_allocated == 0, "Boss Phase 4: No shields (all-in)")

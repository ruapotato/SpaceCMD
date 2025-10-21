extends SceneTree

## Test Suite: Power Management & Ship Systems
## Tests power allocation, shield recharge, system damage, crew bonuses

var test_count = 0
var pass_count = 0

func _init():
	print("============================================================")
	print("TEST SUITE: Power Management & Ship Systems")
	print("============================================================")

	test_power_allocation()
	test_shield_recharge_basic()
	test_shield_recharge_with_power()
	test_shield_recharge_with_crew()
	test_system_damage_weapons()
	test_system_damage_shields()
	test_room_fire_penalty()
	test_crew_repair()
	test_weapon_charging_with_power()
	test_evasion_calculation()
	test_device_file_power_allocation()
	test_device_file_reads()

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
		print("[FAIL] %s (%.3f != %.3f)" % [test_name, actual, expected])

## Test 1: Power Allocation
func test_power_allocation() -> void:
	print("\n--- Test 1: Power Allocation ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.reactor_power = 10

	# Create rooms
	var weapons = Room.new("Weapons Bay", Room.SystemType.WEAPONS, 0, 0)
	weapons.max_power = 4
	var shields = Room.new("Shield Room", Room.SystemType.SHIELDS, 1, 0)
	shields.max_power = 2
	var engines = Room.new("Engine Room", Room.SystemType.ENGINES, 2, 0)
	engines.max_power = 3

	ship.rooms["Weapons Bay"] = weapons
	ship.rooms["Shield Room"] = shields
	ship.rooms["Engine Room"] = engines

	# Test basic allocation
	var success = ship.allocate_power("Weapons Bay", 3)
	assert_true(success, "Allocate 3 power to weapons")
	assert_true(weapons.power_allocated == 3, "Weapons has 3 power")
	assert_true(ship.power_available == 7, "7 power remaining")

	# Allocate to shields
	success = ship.allocate_power("Shield Room", 2)
	assert_true(success, "Allocate 2 power to shields")
	assert_true(ship.power_available == 5, "5 power remaining")

	# Try to allocate more than available
	success = ship.allocate_power("Engine Room", 6)
	assert_true(not success, "Cannot allocate more than available power")
	assert_true(engines.power_allocated == 0, "Engines still at 0 power")

	# Allocate within limits
	success = ship.allocate_power("Engine Room", 3)
	assert_true(success, "Allocate 3 power to engines")
	assert_true(ship.power_available == 2, "2 power remaining")

	# Try to exceed room max power
	success = ship.allocate_power("Shield Room", 3)
	assert_true(not success, "Cannot exceed room max power")
	assert_true(shields.power_allocated == 2, "Shields still at 2 power")

## Test 2: Basic Shield Recharge
func test_shield_recharge_basic() -> void:
	print("\n--- Test 2: Basic Shield Recharge ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.shields = 0.0
	ship.shields_max = 4

	var shield_room = Room.new("Shield Room", Room.SystemType.SHIELDS, 0, 0)
	shield_room.max_power = 2
	shield_room.power_allocated = 0
	shield_room.health = 1.0
	ship.rooms["Shield Room"] = shield_room

	# No power = no recharge
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 0.0, 0.01, "No recharge with 0 power")

	# With power
	shield_room.power_allocated = 2
	ship._update_shields(1.0)  # 2 power * 0.5 = 1.0 shield/sec
	assert_float_near(ship.shields, 1.0, 0.01, "Recharge 1.0 shield/sec with 2 power")

	# Continue recharging
	ship._update_shields(2.0)  # Another 2 seconds
	assert_float_near(ship.shields, 3.0, 0.01, "Shields at 3.0 after 3 seconds total")

	# Should cap at max
	ship._update_shields(5.0)
	assert_float_near(ship.shields, 4.0, 0.01, "Shields capped at max (4.0)")

## Test 3: Shield Recharge with Different Power Levels
func test_shield_recharge_with_power() -> void:
	print("\n--- Test 3: Shield Recharge Power Scaling ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.shields = 0.0
	ship.shields_max = 10

	var shield_room = Room.new("Shield Room", Room.SystemType.SHIELDS, 0, 0)
	shield_room.max_power = 3
	shield_room.health = 1.0
	ship.rooms["Shield Room"] = shield_room

	# 1 power bar
	shield_room.power_allocated = 1
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 0.5, 0.01, "0.5 shield/sec with 1 power")

	# Reset and test 3 power bars
	ship.shields = 0.0
	shield_room.power_allocated = 3
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 1.5, 0.01, "1.5 shields/sec with 3 power")

## Test 4: Shield Recharge with Crew Bonuses
func test_shield_recharge_with_crew() -> void:
	print("\n--- Test 4: Shield Recharge Crew Bonuses ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.shields = 0.0
	ship.shields_max = 10

	var shield_room = Room.new("Shield Room", Room.SystemType.SHIELDS, 0, 0)
	shield_room.max_power = 2
	shield_room.power_allocated = 2
	shield_room.health = 1.0
	ship.rooms["Shield Room"] = shield_room

	# Add crew with shield skill
	var crew = Crew.new("Engineer")
	crew.skill_shields = 2  # +20% bonus
	crew.assign_to_room(shield_room)
	ship.crew.append(crew)

	# Base rate: 2 * 0.5 = 1.0 shield/sec
	# With crew: 1.0 * (1.0 + 0.2) = 1.2 shields/sec
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 1.2, 0.01, "Crew bonus +20% (2 skill levels)")

	# Add another crew member with higher skill
	var crew2 = Crew.new("Expert")
	crew2.skill_shields = 5  # +50% bonus
	crew2.assign_to_room(shield_room)
	ship.crew.append(crew2)

	# Reset shields
	ship.shields = 0.0
	# Total bonus: 20% + 50% = 70%
	# Rate: 1.0 * 1.7 = 1.7 shields/sec
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 1.7, 0.01, "Two crew bonuses stack (+70% total)")

## Test 5: System Damage Affects Weapons
func test_system_damage_weapons() -> void:
	print("\n--- Test 5: Weapon System Damage ---")

	var ship = Ship.new("Test Ship", "Cruiser")

	var weapons_room = Room.new("Weapons Bay", Room.SystemType.WEAPONS, 0, 0)
	weapons_room.max_power = 2
	weapons_room.power_allocated = 2
	weapons_room.health = 1.0
	ship.rooms["Weapons Bay"] = weapons_room

	var weapon = Weapon.new("Laser")
	weapon.cooldown_time = 2.0
	weapon.charge = 0.0
	ship.weapons.append(weapon)

	# Normal charging: 1 second = 50% charge
	ship._update_weapons(1.0)
	assert_float_near(weapon.charge, 0.5, 0.01, "Weapon charges normally at 100% effectiveness")

	# Damage the weapons room (low health)
	weapon.charge = 0.0
	weapons_room.health = 0.5
	ship._update_weapons(1.0)
	# Effectiveness at 50% health = 1.0 (health * 2 when < 0.5)
	# Actually: 0.5 * 2.0 = 1.0, so full effectiveness
	assert_float_near(weapon.charge, 0.5, 0.01, "50% health = 100% effectiveness (0.5 * 2.0)")

	# Very low health
	weapon.charge = 0.0
	weapons_room.health = 0.25
	ship._update_weapons(1.0)
	# Effectiveness = 0.25 * 2.0 = 0.5 (50%)
	assert_float_near(weapon.charge, 0.25, 0.01, "25% health = 50% effectiveness")

	# Critical damage (below functional threshold)
	weapon.charge = 0.0
	weapons_room.health = 0.1
	ship._update_weapons(1.0)
	assert_float_near(weapon.charge, 0.0, 0.01, "Room below 20% health = offline")

	# Breached
	weapon.charge = 0.0
	weapons_room.health = 1.0
	weapons_room.breached = true
	ship._update_weapons(1.0)
	assert_float_near(weapon.charge, 0.0, 0.01, "Breached room = weapons offline")

## Test 6: System Damage Affects Shields
func test_system_damage_shields() -> void:
	print("\n--- Test 6: Shield System Damage ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.shields = 0.0
	ship.shields_max = 4

	var shield_room = Room.new("Shield Room", Room.SystemType.SHIELDS, 0, 0)
	shield_room.max_power = 2
	shield_room.power_allocated = 2
	shield_room.health = 1.0
	ship.rooms["Shield Room"] = shield_room

	# Normal recharge
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 1.0, 0.01, "Normal shield recharge")

	# Damaged shield room
	ship.shields = 0.0
	shield_room.health = 0.3
	ship._update_shields(1.0)
	# Effectiveness = 0.3 * 2.0 = 0.6
	# Recharge = 1.0 * 0.6 = 0.6
	assert_float_near(ship.shields, 0.6, 0.01, "30% health = 60% recharge rate")

	# Critical damage
	ship.shields = 0.0
	shield_room.health = 0.1
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 0.0, 0.01, "Shield room offline = no recharge")

## Test 7: Fire Penalty on Systems
func test_room_fire_penalty() -> void:
	print("\n--- Test 7: Fire Penalty ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.shields = 0.0
	ship.shields_max = 10

	var shield_room = Room.new("Shield Room", Room.SystemType.SHIELDS, 0, 0)
	shield_room.max_power = 2
	shield_room.power_allocated = 2
	shield_room.health = 1.0
	ship.rooms["Shield Room"] = shield_room

	# Set room on fire
	shield_room.on_fire = true

	# Fire reduces effectiveness to 50%
	# Base recharge: 1.0 shield/sec
	# With fire: 1.0 * 0.5 = 0.5 shields/sec
	ship._update_shields(1.0)
	assert_float_near(ship.shields, 0.5, 0.01, "Fire reduces effectiveness to 50%")

## Test 8: Crew Repair Mechanics
func test_crew_repair() -> void:
	print("\n--- Test 8: Crew Repair ---")

	var ship = Ship.new("Test Ship", "Cruiser")

	var damaged_room = Room.new("Engine Room", Room.SystemType.ENGINES, 0, 0)
	damaged_room.health = 0.5
	ship.rooms["Engine Room"] = damaged_room

	# Add crew with repair skill
	var repair_crew = Crew.new("Mechanic")
	repair_crew.skill_repair = 4  # 4 * 0.05 = 0.2 repair/sec
	repair_crew.assign_to_room(damaged_room)
	ship.crew.append(repair_crew)

	# Repair for 1 second
	ship._update_crew_ai(1.0)
	assert_float_near(damaged_room.health, 0.7, 0.01, "Repaired 0.2 in 1 second (skill 4)")

	# Repair to full
	ship._update_crew_ai(2.0)  # Another 2 seconds
	assert_float_near(damaged_room.health, 1.0, 0.01, "Fully repaired (capped at 1.0)")

	# Add second crew member
	var repair_crew2 = Crew.new("Engineer")
	repair_crew2.skill_repair = 2  # 2 * 0.05 = 0.1 repair/sec
	repair_crew2.assign_to_room(damaged_room)
	ship.crew.append(repair_crew2)

	# Damage again and test combined repair
	damaged_room.health = 0.4
	ship._update_crew_ai(1.0)
	# Combined: 0.2 + 0.1 = 0.3 repair/sec
	assert_float_near(damaged_room.health, 0.7, 0.01, "Two crew repair together (0.3/sec)")

## Test 9: Weapon Charging with Power and Crew
func test_weapon_charging_with_power() -> void:
	print("\n--- Test 9: Weapon Charging with Power/Crew ---")

	var ship = Ship.new("Test Ship", "Cruiser")

	var weapons_room = Room.new("Weapons Bay", Room.SystemType.WEAPONS, 0, 0)
	weapons_room.max_power = 2
	weapons_room.power_allocated = 2
	weapons_room.health = 1.0
	ship.rooms["Weapons Bay"] = weapons_room

	var weapon = Weapon.new("Laser")
	weapon.cooldown_time = 4.0
	weapon.charge = 0.0
	ship.weapons.append(weapon)

	# Add crew with weapon skill
	var gunner = Crew.new("Gunner")
	gunner.skill_weapons = 3  # +30% bonus
	gunner.assign_to_room(weapons_room)
	ship.crew.append(gunner)

	# Charge for 1 second
	# Base charge rate: 1 / 4.0 = 0.25 per second
	# With crew bonus: 0.25 * 1.3 = 0.325
	ship._update_weapons(1.0)
	assert_float_near(weapon.charge, 0.325, 0.01, "Weapon charges 30% faster with skilled crew")

	# No power = no charging
	weapon.charge = 0.0
	weapons_room.power_allocated = 0
	ship._update_weapons(1.0)
	assert_float_near(weapon.charge, 0.0, 0.01, "No power = no weapon charging")

## Test 10: Evasion Calculation
func test_evasion_calculation() -> void:
	print("\n--- Test 10: Evasion Calculation ---")

	var ship = Ship.new("Test Ship", "Cruiser")

	var engines = Room.new("Engine Room", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 0
	engines.health = 1.0
	ship.rooms["Engine Room"] = engines

	# No power = 0% evasion
	var evasion = ship.get_evasion()
	assert_float_near(evasion, 0.0, 0.01, "0% evasion with no power")

	# 2 power bars = 10% evasion (2 * 5%)
	engines.power_allocated = 2
	evasion = ship.get_evasion()
	assert_float_near(evasion, 0.10, 0.01, "10% evasion with 2 power")

	# Add skilled pilot
	var pilot = Crew.new("Ace Pilot")
	pilot.skill_engines = 4  # +40% bonus
	pilot.assign_to_room(engines)
	ship.crew.append(pilot)

	# 10% * 1.4 = 14%
	evasion = ship.get_evasion()
	assert_float_near(evasion, 0.14, 0.01, "14% evasion with crew bonus")

	# Damaged engines
	engines.health = 0.4
	# Effectiveness: 0.4 * 2.0 = 0.8 (80%)
	# Evasion: 0.10 * 0.8 * 1.4 = 0.112 (11.2%)
	evasion = ship.get_evasion()
	assert_float_near(evasion, 0.112, 0.01, "Evasion reduced by engine damage")

## Test 11: Device File Power Allocation
func test_device_file_power_allocation() -> void:
	print("\n--- Test 11: Device File Power Allocation ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.reactor_power = 10
	ship.os = ShipOS.new(ship)

	var weapons = Room.new("Weapons", Room.SystemType.WEAPONS, 0, 0)
	weapons.max_power = 3
	var shields = Room.new("Shields", Room.SystemType.SHIELDS, 1, 0)
	shields.max_power = 2

	ship.rooms["Weapons"] = weapons
	ship.rooms["Shields"] = shields

	# Allocate power via device file
	var result = ship.os.write_device("/dev/ship/actions/power", "Weapons:3")
	assert_true(result, "Power allocation via device file")
	assert_true(weapons.power_allocated == 3, "Weapons has 3 power after device write")

	# Multiple allocations
	result = ship.os.write_device("/dev/ship/actions/power", "Weapons:2,Shields:2")
	assert_true(result, "Multiple power allocations")
	assert_true(weapons.power_allocated == 2, "Weapons reduced to 2")
	assert_true(shields.power_allocated == 2, "Shields set to 2")
	assert_true(ship.power_available == 6, "6 power remaining")

## Test 12: Device File Reads
func test_device_file_reads() -> void:
	print("\n--- Test 12: Device File Reads ---")

	var ship = Ship.new("Test Ship", "Cruiser")
	ship.reactor_power = 8
	ship.shields = 2.5
	ship.shields_max = 4
	ship.os = ShipOS.new(ship)

	var engines = Room.new("Engines", Room.SystemType.ENGINES, 0, 0)
	engines.max_power = 3
	engines.power_allocated = 2
	engines.health = 0.8
	ship.rooms["Engines"] = engines

	# Read power status
	var power_data = ship.os.read_device("/dev/ship/power")
	assert_true(power_data.contains("8/8"), "Power device shows correct values")

	# Read evasion
	var evasion_data = ship.os.read_device("/proc/ship/evasion")
	assert_true(evasion_data.contains("Evasion:"), "Evasion proc file readable")
	assert_true(evasion_data.contains("Engine Power: 2/3"), "Shows engine power allocation")

	# Read power detail
	var power_detail = ship.os.read_device("/proc/ship/power_detail")
	assert_true(power_detail.contains("Reactor Output: 8"), "Shows reactor output")
	assert_true(power_detail.contains("Engines"), "Lists engine power allocation")

	# Read rooms with effectiveness
	var rooms_data = ship.os.read_device("/proc/ship/rooms")
	assert_true(rooms_data.contains("Engines"), "Shows engine room")
	assert_true(rooms_data.contains("Eff:"), "Shows effectiveness percentage")
	assert_true(rooms_data.contains("Crew:"), "Shows crew count")

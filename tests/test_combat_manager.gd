extends SceneTree

## Comprehensive Combat Manager Tests
## Tests multi-ship battles, projectiles, damage, and victory conditions

# Load CombatManager (autoloads may not work in headless mode)
const CombatManagerScript = preload("res://core/combat/combat_manager.gd")
var CombatManager = null

func _init():
	# Create CombatManager instance
	CombatManager = CombatManagerScript.new()
	root.add_child(CombatManager)

	print("\n" + "=".repeat(70))
	print("COMBAT MANAGER TEST SUITE")
	print("=".repeat(70) + "\n")

	var all_passed = true

	all_passed = test_ship_management() and all_passed
	all_passed = test_projectile_basics() and all_passed
	all_passed = test_damage_system() and all_passed
	all_passed = test_victory_conditions() and all_passed
	all_passed = test_full_combat_scenario() and all_passed
	all_passed = test_ai_combat_integration() and all_passed

	print("\n" + "=".repeat(70))
	if all_passed:
		print("✓ ALL TESTS PASSED")
	else:
		print("✗ SOME TESTS FAILED")
	print("=".repeat(70) + "\n")

	quit(0 if all_passed else 1)

## Test 1: Ship Management
func test_ship_management() -> bool:
	print("\n[TEST 1] Ship Management")
	print("-".repeat(50))

	CombatManager.reset()

	# Create test ships
	var player = Ship.new("USS Enterprise", "Federation Cruiser")
	player.position = Vector3(0, 0, 0)

	var enemy1 = Ship.new("Pirate Raider", "Rebel Scout")
	enemy1.position = Vector3(500, 0, 0)

	var enemy2 = Ship.new("Mantis Hunter", "Mantis Fighter")
	enemy2.position = Vector3(-500, 0, 0)

	# Add ships to combat
	CombatManager.add_ship(player, "player")
	CombatManager.add_ship(enemy1, "enemy")
	CombatManager.add_ship(enemy2, "enemy")

	# Verify ships added
	if CombatManager.ships["player"].size() != 1:
		print("✗ Player ship count incorrect")
		return false

	if CombatManager.ships["enemy"].size() != 2:
		print("✗ Enemy ship count incorrect")
		return false

	if CombatManager.all_ships.size() != 3:
		print("✗ Total ship count incorrect")
		return false

	# Test faction detection
	if CombatManager.get_ship_faction(player) != "player":
		print("✗ Player faction detection failed")
		return false

	if CombatManager.get_ship_faction(enemy1) != "enemy":
		print("✗ Enemy faction detection failed")
		return false

	# Remove a ship
	CombatManager.remove_ship(enemy2)
	if CombatManager.ships["enemy"].size() != 1:
		print("✗ Ship removal failed")
		return false

	print("✓ Ship management working correctly")
	return true

## Test 2: Projectile Basics
func test_projectile_basics() -> bool:
	print("\n[TEST 2] Projectile Basics")
	print("-".repeat(50))

	CombatManager.reset()

	# Create test ships
	var shooter = Ship.new("Shooter", "Test")
	shooter.position = Vector3(0, 0, 0)

	var target = Ship.new("Target", "Test")
	target.position = Vector3(1000, 0, 0)

	# Create weapon
	var laser = Weapon.new("Burst Laser")
	laser.damage = 10.0
	laser.charge = 1.0

	# Spawn projectile
	var projectile = CombatManager.spawn_projectile(shooter, target, laser, 0)

	if not projectile:
		print("✗ Projectile spawn failed")
		return false

	if CombatManager.projectiles.size() != 1:
		print("✗ Projectile not added to manager")
		return false

	# Test projectile update
	var initial_pos = projectile.position
	projectile.update(0.1)  # 0.1 second

	if projectile.position == initial_pos:
		print("✗ Projectile not moving")
		return false

	# Test projectile expiration
	projectile.lifetime = 11.0  # Over max_lifetime
	if projectile.update(0.1):
		print("✗ Projectile should have expired")
		return false

	print("✓ Projectile basics working correctly")
	return true

## Test 3: Damage System
func test_damage_system() -> bool:
	print("\n[TEST 3] Damage System")
	print("-".repeat(50))

	CombatManager.reset()

	# Create target ship
	var target = Ship.new("Target", "Test")
	target.hull = 30.0
	target.shields = 10.0
	target.position = Vector3(0, 0, 0)

	CombatManager.add_ship(target, "enemy")

	# Test shield absorption
	var initial_hull = target.hull
	var initial_shields = target.shields

	CombatManager.apply_damage(target, 5.0)

	if target.shields != 5.0:
		print("✗ Shield damage incorrect (expected 5.0, got %.1f)" % target.shields)
		return false

	if target.hull != initial_hull:
		print("✗ Hull should not be damaged when shields are up")
		return false

	# Test shield penetration
	CombatManager.apply_damage(target, 7.0)  # 5 shields + 2 hull

	if target.shields != 0.0:
		print("✗ Shields should be depleted")
		return false

	if target.hull != 28.0:
		print("✗ Hull damage incorrect (expected 28.0, got %.1f)" % target.hull)
		return false

	# Test ship destruction
	var destroyed = false
	CombatManager.ship_destroyed.connect(func(_ship, _faction): destroyed = true)

	CombatManager.apply_damage(target, 100.0)

	if target.hull > 0:
		print("✗ Ship should be destroyed")
		return false

	if not destroyed:
		print("✗ ship_destroyed signal not emitted")
		return false

	if CombatManager.ships["enemy"].size() != 0:
		print("✗ Destroyed ship not removed from manager")
		return false

	print("✓ Damage system working correctly")
	return true

## Test 4: Victory Conditions
func test_victory_conditions() -> bool:
	print("\n[TEST 4] Victory Conditions")
	print("-".repeat(50))

	# Test victory (all enemies destroyed)
	CombatManager.reset()

	var player = Ship.new("Player", "Test")
	player.position = Vector3.ZERO
	CombatManager.add_ship(player, "player")

	var enemy = Ship.new("Enemy", "Test")
	enemy.position = Vector3(100, 0, 0)
	enemy.hull = 10.0
	CombatManager.add_ship(enemy, "enemy")

	CombatManager.start_battle()

	var victory_detected = false
	CombatManager.battle_won.connect(func(_faction): victory_detected = true)

	# Destroy enemy
	CombatManager.apply_damage(enemy, 100.0)
	CombatManager.check_victory_conditions()

	if not victory_detected:
		print("✗ Victory not detected")
		return false

	if CombatManager.battle_active:
		print("✗ Battle should have ended")
		return false

	# Test defeat (player destroyed)
	CombatManager.reset()

	player = Ship.new("Player", "Test")
	player.position = Vector3.ZERO
	player.hull = 10.0
	CombatManager.add_ship(player, "player")

	enemy = Ship.new("Enemy", "Test")
	enemy.position = Vector3(100, 0, 0)
	CombatManager.add_ship(enemy, "enemy")

	CombatManager.start_battle()

	var defeat_detected = false
	CombatManager.battle_lost.connect(func(): defeat_detected = true)

	# Destroy player
	CombatManager.apply_damage(player, 100.0)
	CombatManager.check_victory_conditions()

	if not defeat_detected:
		print("✗ Defeat not detected")
		return false

	print("✓ Victory conditions working correctly")
	return true

## Test 5: Full Combat Scenario
func test_full_combat_scenario() -> bool:
	print("\n[TEST 5] Full Combat Scenario")
	print("-".repeat(50))

	CombatManager.reset()

	# Create player ship
	var player = Ship.new("USS Enterprise", "Federation Cruiser")
	player.hull = 30.0
	player.shields = 10.0
	player.position = Vector3(0, 0, 0)

	var player_laser = Weapon.new("Burst Laser")
	player_laser.damage = 5.0
	player_laser.charge = 1.0
	player.weapons.append(player_laser)

	# Create enemy ship
	var enemy = Ship.new("Pirate Raider", "Rebel Scout")
	enemy.hull = 20.0
	enemy.shields = 5.0
	enemy.position = Vector3(300, 0, 0)  # Close range

	var enemy_laser = Weapon.new("Light Laser")
	enemy_laser.damage = 3.0
	enemy_laser.charge = 1.0
	enemy.weapons.append(enemy_laser)

	# Add to combat
	CombatManager.add_ship(player, "player")
	CombatManager.add_ship(enemy, "enemy")
	CombatManager.start_battle()

	# Fire player weapon at enemy
	var projectile = CombatManager.spawn_projectile(player, enemy, player_laser, 0)

	if not projectile:
		print("✗ Failed to spawn projectile")
		return false

	# Simulate projectile travel and hit
	var hit_detected = false
	CombatManager.projectile_hit.connect(func(_proj, _target): hit_detected = true)

	# Move projectile toward target until hit
	var max_iterations = 100
	var iterations = 0
	while iterations < max_iterations:
		projectile.update(0.016)  # 16ms frame
		if projectile.check_hit(enemy, 50.0):
			CombatManager.apply_damage(enemy, projectile.damage, player)
			CombatManager.projectiles.clear()
			hit_detected = true
			break
		iterations += 1

	if not hit_detected:
		print("✗ Projectile never hit target")
		return false

	# Verify damage applied
	if enemy.shields != 0.0 or enemy.hull != 20.0:
		print("✗ Damage not applied correctly (shields: %.1f, hull: %.1f)" % [enemy.shields, enemy.hull])
		return false

	print("✓ Full combat scenario working correctly")
	return true

## Test 6: AI Combat Integration
func test_ai_combat_integration() -> bool:
	print("\n[TEST 6] AI Combat Integration")
	print("-".repeat(50))

	CombatManager.reset()

	# Create player ship
	var player = Ship.new("USS Enterprise", "Federation Cruiser")
	player.hull = 30.0
	player.shields = 10.0
	player.position = Vector3(0, 0, 0)
	player.galaxy_position = 800.0

	# Create player OS
	var player_os = ShipOS.new(player)
	player.os = player_os

	# Create enemy ship with AI
	var enemy = Ship.new("Pirate Raider", "Rebel Scout")
	enemy.hull = 20.0
	enemy.shields = 5.0
	enemy.position = Vector3(300, 0, 0)
	enemy.galaxy_position = 850.0

	var laser = Weapon.new("Burst Laser")
	laser.damage = 5.0
	laser.charge = 1.0
	enemy.weapons.append(laser)

	# Create enemy OS and load AI
	var enemy_os = ShipOS.new(enemy)
	enemy.os = enemy_os
	enemy_os.nearby_ships = [player, enemy]

	# Load hostile AI
	var ai_code = FileAccess.get_file_as_string("res://scripts/ai/hostile.poo")
	if not ai_code:
		print("✗ Failed to load hostile AI script")
		return false

	enemy_os.vfs.create_file("/bin/hostile.poo", 0x1ED, 0, 0, ai_code.to_utf8_buffer())
	var ai_pid = enemy_os.execute_command("/bin/hostile.poo")

	if ai_pid <= 0:
		print("✗ Failed to spawn AI process")
		return false

	# Add ships to combat
	CombatManager.add_ship(player, "player")
	CombatManager.add_ship(enemy, "enemy")
	CombatManager.start_battle()

	# Update enemy OS to let AI run
	var ai_fired = false
	var max_updates = 10
	for i in range(max_updates):
		enemy_os.update(0.1)
		if CombatManager.projectiles.size() > 0:
			ai_fired = true
			break

	if not ai_fired:
		print("✗ AI did not fire weapon")
		print("  AI PID: %d" % ai_pid)
		print("  AI status: %s" % enemy_os.kernel.process_manager.get_process_info(ai_pid))
		return false

	print("✓ AI combat integration working correctly")
	return true

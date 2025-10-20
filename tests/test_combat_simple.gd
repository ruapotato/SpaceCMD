extends SceneTree

## Simple Combat Manager Test - Minimal test to verify basic functionality

func _init():
	print("\n=== SIMPLE COMBAT MANAGER TEST ===\n")

	# Load CombatManager class
	var CombatManagerClass = load("res://core/combat/combat_manager.gd")
	var combat_mgr = CombatManagerClass.new()

	print("✓ CombatManager loaded")

	# Create a simple ship
	var ship = Ship.new("Test Ship", "Test Class")
	ship.position = Vector3(0, 0, 0)
	print("✓ Ship created: %s" % ship.ship_name)

	# Add ship to combat
	combat_mgr.add_ship(ship, "player")
	print("✓ Ship added to combat")

	# Check ship was added
	if combat_mgr.ships["player"].size() == 1:
		print("✓ Ship registered correctly")
	else:
		print("✗ Ship not registered")
		quit(1)
		return

	# Create a weapon
	var weapon = Weapon.new("Test Laser")
	weapon.damage = 10.0
	weapon.charge = 1.0
	print("✓ Weapon created: %s" % weapon.weapon_name)

	# Create target
	var target = Ship.new("Target", "Enemy")
	target.position = Vector3(100, 0, 0)
	combat_mgr.add_ship(target, "enemy")
	print("✓ Target added")

	# Test projectile spawn
	var projectile = combat_mgr.spawn_projectile(ship, target, weapon, 0)
	if projectile:
		print("✓ Projectile spawned")
		print("  From: %s" % projectile.owner_ship.ship_name)
		print("  To: %s" % projectile.target_ship.ship_name)
		print("  Damage: %.1f" % projectile.damage)
	else:
		print("✗ Projectile spawn failed")
		quit(1)
		return

	# Test damage
	var initial_hull = target.hull
	combat_mgr.apply_damage(target, 5.0)
	if target.hull < initial_hull:
		print("✓ Damage applied (%.1f → %.1f)" % [initial_hull, target.hull])
	else:
		print("✗ Damage not applied")
		quit(1)
		return

	print("\n=== ALL BASIC TESTS PASSED ===\n")
	quit(0)

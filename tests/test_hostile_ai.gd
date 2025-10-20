extends SceneTree

## Test Hostile AI with Sensors and Targeting

func _initialize():
	print("============================================================")
	print("HOSTILE AI TEST")
	print("============================================================\n")

	test_hostile_ai_complete_scenario()

	quit()

func test_hostile_ai_complete_scenario():
	print("[TEST: Hostile AI Complete Scenario]")

	# Create player ship
	var player_ship = Ship.new("USS Enterprise", "Kestrel")
	player_ship.hull = 30.0
	player_ship.galaxy_position = 800.0
	var player_os = ShipOS.new(player_ship)

	# Create enemy ship with weapons
	var enemy_ship = Ship.new("Pirate Cruiser", "Rebel Fighter")
	enemy_ship.hull = 25.0
	enemy_ship.galaxy_position = 805.0  # 5 units away

	var laser = Weapon.new("Burst Laser")
	laser.charge = 1.0  # Ready to fire
	enemy_ship.weapons.append(laser)

	var enemy_os = ShipOS.new(enemy_ship)

	# Set up sensor context - each ship can see the other
	player_os.nearby_ships = [player_ship, enemy_ship]
	enemy_os.nearby_ships = [player_ship, enemy_ship]

	print("\n--- INITIAL STATE ---")
	print("Player: %s at position %.1f" % [player_ship.ship_name, player_ship.galaxy_position])
	print("Enemy: %s at position %.1f (%.1f units away)" % [
		enemy_ship.ship_name,
		enemy_ship.galaxy_position,
		abs(enemy_ship.galaxy_position - player_ship.galaxy_position)
	])

	# Test sensor reading
	print("\n--- ENEMY SENSORS ---")
	var sensors_data = enemy_os.read_device("/proc/ship/sensors")
	print(sensors_data)

	# Test target (should be empty)
	print("--- ENEMY TARGET (before) ---")
	var target_before = enemy_os.read_device("/dev/ship/target")
	print(target_before)

	# Load and spawn hostile AI
	print("\n--- SPAWNING HOSTILE AI ---")
	var hostile_script = FileAccess.get_file_as_string("res://scripts/ai/hostile.poo")
	enemy_os.vfs.create_file("/bin/hostile.poo", 0x1ED, 0, 0, hostile_script.to_utf8_buffer())

	var ai_pid = enemy_os.execute_command("/bin/hostile.poo")
	print("  ✓ Hostile AI spawned with PID: %d" % ai_pid)

	# Run one AI update cycle
	print("\n--- RUNNING AI CYCLE ---")
	enemy_os.update(0.1)

	# Check results
	print("\n--- RESULTS ---")

	# Check if target was acquired
	var target_after = enemy_os.read_device("/dev/ship/target")
	print("Enemy target (after):")
	print(target_after)

	if "USS Enterprise" in target_after:
		print("  ✓ AI successfully acquired player as target")
	else:
		print("  ✗ AI failed to acquire target")

	# Check if weapon was fired
	if laser.charge < 1.0:
		print("  ✓ AI successfully fired weapon (charge: %.1f%%)" % (laser.charge * 100))
	else:
		print("  ✗ AI did not fire weapon (charge still: %.1f%%)" % (laser.charge * 100))

	# Check weapon status
	print("\n--- WEAPON STATUS ---")
	var weapons_status = enemy_os.read_device("/proc/ship/weapons")
	print(weapons_status)

	# Test player killing the AI
	print("\n--- PLAYER HACKS ENEMY SHIP ---")
	print("Player executes: kill %d" % ai_pid)
	var killed = enemy_os.kill_process(ai_pid)

	if killed:
		print("  ✓ Enemy AI terminated successfully")

		var processes = enemy_os.get_processes()
		for proc in processes:
			if proc["pid"] == ai_pid:
				print("  ✓ AI process state: %s" % proc["state"])
				break
	else:
		print("  ✗ Failed to kill AI process")

	print("\n============================================================")
	print("✅ HOSTILE AI TEST COMPLETE")
	print("============================================================")

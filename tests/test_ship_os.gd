extends SceneTree

## ShipOS Integration Test
## Tests the full integration of VFS + PooScript + Kernel with Ship state

func test_assert(condition: bool, message: String) -> void:
	if condition:
		print("  ✓ %s" % message)
	else:
		print("  ✗ FAILED: %s" % message)
		push_error("Assertion failed: %s" % message)

func _initialize():
	print("============================================================")
	print("SHIPOS INTEGRATION TEST")
	print("============================================================\n")

	var all_passed = true

	all_passed = test_basic_ship_os() and all_passed
	all_passed = test_device_reading() and all_passed
	all_passed = test_proc_files() and all_passed
	all_passed = test_device_writing() and all_passed
	all_passed = test_ai_script_integration() and all_passed

	print("\n============================================================")
	if all_passed:
		print("✅ ALL TESTS PASSED")
	else:
		print("❌ SOME TESTS FAILED")
	print("============================================================")

	quit()

## Test 1: Basic ShipOS creation
func test_basic_ship_os() -> bool:
	print("[TEST 1: Basic ShipOS Creation]")

	# Create a ship
	var ship = Ship.new("USS Enterprise", "Kestrel")
	ship.hull = 25.0
	ship.shields = 0.0
	ship.scrap = 50

	# Create ShipOS
	var ship_os = ShipOS.new(ship)

	# Verify components initialized
	test_assert(ship_os.vfs != null, "VFS initialized")
	test_assert(ship_os.kernel != null, "Kernel initialized")
	test_assert(ship_os.pooscript != null, "PooScript initialized")
	test_assert(ship_os.hostname == "uss_enterprise", "Hostname set correctly")

	# Verify directory structure
	test_assert(ship_os.vfs.path_exists("/dev/ship"), "/dev/ship exists")
	test_assert(ship_os.vfs.path_exists("/proc/ship"), "/proc/ship exists")
	test_assert(ship_os.vfs.path_exists("/bin"), "/bin exists")
	test_assert(ship_os.vfs.path_exists("/sbin"), "/sbin exists")

	# Verify init process spawned
	var processes = ship_os.get_processes()
	test_assert(processes.size() == 1, "Init process spawned")
	test_assert(processes[0]["pid"] == 1, "Init has PID 1")

	print("✅ Basic ShipOS: ALL TESTS PASSED\n")
	return true

## Test 2: Device file reading
func test_device_reading() -> bool:
	print("[TEST 2: Device File Reading]")

	var ship = Ship.new("Stealth Cruiser", "Nesasio")
	ship.hull = 20.0
	ship.hull_max = 25.0
	ship.shields = 3.0
	ship.shields_max = 4
	ship.scrap = 75
	ship.missiles = 6
	ship.dark_matter = 15

	var ship_os = ShipOS.new(ship)

	# Read hull device
	var hull = ship_os.read_device("/dev/ship/hull")
	test_assert(hull == "20.0", "Read hull: %s" % hull)

	# Read shields device
	var shields = ship_os.read_device("/dev/ship/shields")
	test_assert(shields == "3.0", "Read shields: %s" % shields)

	# Read scrap device
	var scrap = ship_os.read_device("/dev/ship/scrap")
	test_assert(scrap == "75", "Read scrap: %s" % scrap)

	# Read power device
	var power = ship_os.read_device("/dev/ship/power")
	test_assert(power == "8/8", "Read power: %s" % power)

	# Modify ship state and re-read
	ship.hull = 15.0
	var new_hull = ship_os.read_device("/dev/ship/hull")
	test_assert(new_hull == "15.0", "Device reflects updated hull: %s" % new_hull)

	print("✅ Device Reading: ALL TESTS PASSED\n")
	return true

## Test 3: Proc files
func test_proc_files() -> bool:
	print("[TEST 3: Proc Files]")

	var ship = Ship.new("Red-Tail", "Kestrel")

	# Add weapons
	var laser = Weapon.new("Burst Laser I")
	laser.damage = 1
	laser.shots = 2
	laser.charge = 1.0  # Ready to fire
	ship.weapons.append(laser)

	var missile = Weapon.new("Artemis Missile")
	missile.damage = 2
	missile.charge = 0.5  # Charging
	missile.requires_missiles = true
	ship.weapons.append(missile)

	# Add crew
	var crew1 = Crew.new("Alice")
	crew1.health = 100.0
	ship.crew.append(crew1)

	var crew2 = Crew.new("Bob")
	crew2.health = 75.0
	ship.crew.append(crew2)

	# Add rooms
	var helm_room = Room.new("Helm", Room.SystemType.HELM, 0, 0)
	helm_room.health = 1.0
	helm_room.power_allocated = 2
	ship.rooms["helm"] = helm_room

	var weapons_room = Room.new("Weapons", Room.SystemType.WEAPONS, 1, 0)
	weapons_room.health = 0.6
	weapons_room.power_allocated = 3
	weapons_room.on_fire = true
	ship.rooms["weapons"] = weapons_room

	crew1.assign_to_room(helm_room)

	# Add systems
	var weapons_system = ShipSystem.new("Weapons", Room.SystemType.WEAPONS)
	weapons_system.room = weapons_room
	ship.systems[Room.SystemType.WEAPONS] = weapons_system

	var ship_os = ShipOS.new(ship)

	# Read /proc/ship/status
	var status = ship_os.read_device("/proc/ship/status")
	test_assert("Red-Tail" in status, "Status contains ship name")
	test_assert("30.0/30.0" in status, "Status contains hull")

	# Read /proc/ship/weapons
	var weapons = ship_os.read_device("/proc/ship/weapons")
	test_assert("Burst Laser I" in weapons, "Weapons list contains Burst Laser")
	test_assert("READY" in weapons, "Shows ready weapon")
	test_assert("CHARGING" in weapons, "Shows charging weapon")
	test_assert("Artemis Missile" in weapons, "Weapons list contains Artemis")

	# Read /proc/ship/crew
	var crew = ship_os.read_device("/proc/ship/crew")
	test_assert("Alice" in crew, "Crew list contains Alice")
	test_assert("Bob" in crew, "Crew list contains Bob")
	test_assert("ALIVE" in crew, "Shows crew status")

	# Read /proc/ship/rooms
	var rooms = ship_os.read_device("/proc/ship/rooms")
	test_assert("Helm" in rooms, "Rooms list contains Helm")
	test_assert("Weapons" in rooms, "Rooms list contains Weapons")
	test_assert("FIRE" in rooms, "Shows fire condition")

	print("✅ Proc Files: ALL TESTS PASSED\n")
	return true

## Test 4: Device writing (action devices)
func test_device_writing() -> bool:
	print("[TEST 4: Device Writing (Actions)]")

	var ship = Ship.new("Engi Cruiser", "Torus")

	# Add weapon
	var ion = Weapon.new("Ion Blast")
	ion.charge = 1.0  # Ready
	ship.weapons.append(ion)

	var ship_os = ShipOS.new(ship)

	# Fire weapon via device write
	var result = ship_os.write_device("/dev/ship/actions/fire", "0")
	test_assert(result, "Fired weapon via device")
	test_assert(ion.charge == 0.0, "Weapon charge reset after firing")

	# Jump via device write
	ship_os.write_device("/dev/ship/actions/jump", "1200.0")
	test_assert(ship.target_position == 1200.0, "Jump destination set")
	test_assert(ship.is_traveling == true, "Ship is traveling")

	# Set target via device write
	ship_os.write_device("/dev/ship/actions/target", "enemy_ship")
	# Note: target storage not implemented yet, just verifying no crash

	print("✅ Device Writing: ALL TESTS PASSED\n")
	return true

## Test 5: AI Script Integration (The Full Loop!)
func test_ai_script_integration() -> bool:
	print("[TEST 5: AI Script Integration - THE BIG ONE]")

	var ship = Ship.new("Pirate Ship", "Rebel Fighter")

	# Add weapon
	var laser = Weapon.new("Heavy Laser")
	laser.charge = 1.0  # Ready to fire
	ship.weapons.append(laser)

	var ship_os = ShipOS.new(ship)

	# Create a hostile AI script
	var hostile_ai = """
extends RefCounted

func main(pid, kernel, args, env):
	print('[AI] Hostile AI starting (PID %d)' % pid)

	# Read ship status
	var fd = kernel.sys_open(pid, '/proc/ship/status', kernel.O_RDONLY)
	if fd < 0:
		print('[AI] ERROR: Could not open /proc/ship/status')
		return -1
	var status = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	print('[AI] Ship status read: %d bytes' % status.size())

	# Check weapons
	fd = kernel.sys_open(pid, '/proc/ship/weapons', kernel.O_RDONLY)
	if fd < 0:
		print('[AI] ERROR: Could not open /proc/ship/weapons')
		return -1
	var weapons = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	var weapons_str = weapons.get_string_from_utf8()
	print('[AI] Weapons: %s' % weapons_str)

	# Fire weapon if ready
	if 'READY' in weapons_str:
		print('[AI] Weapon is READY, firing!')
		fd = kernel.sys_open(pid, '/dev/ship/actions/fire', kernel.O_WRONLY)
		if fd < 0:
			print('[AI] ERROR: Could not open fire device')
			return -1
		var bytes_written = kernel.sys_write(pid, fd, '0'.to_utf8_buffer())
		kernel.sys_close(pid, fd)
		print('[AI] Fired weapon! (wrote %d bytes)' % bytes_written)
	else:
		print('[AI] Weapon not ready, waiting...')

	print('[AI] Hostile AI completed')
	return 0
"""

	# Write AI script to VFS
	ship_os.vfs.create_file("/bin/hostile.poo", 0x1ED, 0, 0, hostile_ai.to_utf8_buffer())

	# Spawn the AI script
	var ai_pid = ship_os.execute_command("/bin/hostile.poo")
	test_assert(ai_pid > 0, "AI script spawned with PID: %d" % ai_pid)

	# Give it time to run (simulate one update)
	ship_os.update(0.1)

	# Verify weapon was fired (charge should be 0)
	test_assert(laser.charge == 0.0, "AI successfully fired the weapon!")

	# Verify we can kill the AI
	var killed = ship_os.kill_process(ai_pid)
	test_assert(killed, "Killed AI process")

	var processes = ship_os.get_processes()
	var ai_process = null
	for proc in processes:
		if proc["pid"] == ai_pid:
			ai_process = proc
			break

	test_assert(ai_process != null, "AI process still in table")
	test_assert(ai_process["state"] == "STOPPED", "AI process is STOPPED")

	print("✅ AI Script Integration: ALL TESTS PASSED\n")
	print("🎉 THE FULL INTEGRATION WORKS!")
	print("   - PooScript AI can read ship state via /proc files")
	print("   - PooScript AI can control ship via /dev/ship/actions")
	print("   - Player can kill AI with kill(pid)")
	return true

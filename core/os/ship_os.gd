## ShipOS - Integrated OS for each ship
## Combines VFS + PooScript + Kernel with device bridge to ship state
class_name ShipOS extends RefCounted

var ship: Ship
var vfs: VFS
var kernel: KernelInterface
var pooscript: PooScript
var hostname: String = ""

# Combat/Galaxy context (set externally by combat manager)
var nearby_ships: Array = []  # Array of Ship objects in sensor range
var current_target: Ship = null
var combat_manager = null  # Reference to CombatManager (set externally)

# Bot management (set externally by ship scene)
var bots: Array = []  # Array of Bot objects
var ship_rooms: Array = []  # Array of RoomInstance objects

# Device callbacks - these are triggered when PooScript writes to devices
var device_write_callbacks: Dictionary = {}  # device_path -> Callable

func _init(p_ship: Ship, p_hostname: String = "") -> void:
	ship = p_ship
	hostname = p_hostname if p_hostname else p_ship.ship_name.to_lower().replace(" ", "_")

	vfs = VFS.new()
	kernel = KernelInterface.new(vfs)
	pooscript = PooScript.new(vfs)
	pooscript.set_kernel(kernel)  # Allow scripts to access kernel syscalls

	_create_directory_structure()
	_populate_bin_commands()
	_mount_ship_devices()
	_spawn_init_process()

## Create standard Unix directory structure
func _create_directory_structure() -> void:
	# VFS already creates base directories, just add /sbin
	if not vfs.stat("/sbin"):
		vfs.mkdir("/sbin", 0x1ED, 0, 0)  # 755

## Populate /bin with PooScript commands
func _populate_bin_commands() -> void:
	# Basic Unix commands
	_create_command("ls", """# List directory contents
var path = args[0] if args.size() > 0 else '/'
var entries = vfs.list_dir(path)
if entries.is_empty():
	pprint('ls: cannot access \\'%s\\': No such directory' % path)
	return 1
for entry in entries:
	var name = entry[0] if entry is Array and entry.size() > 0 else str(entry)
	pprint(name)
return 0
""")

	_create_command("cat", """# Read file contents
if args.size() == 0:
	pprint('Usage: cat <filename>')
	return 1
var path = args[0]
var fd = kernel.sys_open(pid, path, kernel.O_RDONLY)
if fd < 0:
	pprint('cat: %s: No such file or directory' % path)
	return 1
var data = kernel.sys_read(pid, fd, 4096)
kernel.sys_close(pid, fd)
pprint(data.get_string_from_utf8())
return 0
""")

	_create_command("pwd", """# Print working directory
pprint(env.get('PWD', '/'))
return 0
""")

	_create_command("cd", """# Change directory
if args.size() == 0:
	pprint('Usage: cd <directory>')
	return 1
var target_dir = args[0]
pprint('cd: Target %s' % target_dir)
return 0
""")

	_create_command("echo", """# Echo arguments
pprint(' '.join(args))
return 0
""")

	_create_command("help", """# Show available commands
pprint('Available commands: ls, cat, cd, pwd, echo, help, status, weapons, systems, crew, rooms, sensors, position, bots, target, fire, power, thrust, turn, jump, send')
return 0
""")

	# Ship status commands
	_create_command("status", """# Show ship status
var fd = kernel.sys_open(pid, '/proc/ship/status', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("weapons", """# Show weapons status
var fd = kernel.sys_open(pid, '/proc/ship/weapons', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("systems", """# Show systems status
var fd = kernel.sys_open(pid, '/proc/ship/systems', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("crew", """# Show crew status
var fd = kernel.sys_open(pid, '/proc/ship/crew', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("rooms", """# Show rooms status
var fd = kernel.sys_open(pid, '/proc/ship/rooms', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("sensors", """# Show sensor contacts
var fd = kernel.sys_open(pid, '/proc/ship/sensors', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("position", """# Show ship position
var fd = kernel.sys_open(pid, '/proc/ship/position', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	_create_command("bots", """# Show bot status
var fd = kernel.sys_open(pid, '/proc/ship/bots', kernel.O_RDONLY)
if fd >= 0:
	var data = kernel.sys_read(pid, fd, 4096)
	kernel.sys_close(pid, fd)
	pprint(data.get_string_from_utf8())
	return 0
return 1
""")

	# Ship action commands
	_create_command("target", """# Set combat target
if args.size() == 0:
	var fd = kernel.sys_open(pid, '/dev/ship/target', kernel.O_RDONLY)
	if fd >= 0:
		var data = kernel.sys_read(pid, fd, 1024)
		kernel.sys_close(pid, fd)
		pprint(data.get_string_from_utf8())
		return 0
	return 1
else:
	var target_name = args[0]
	var fd = kernel.sys_open(pid, '/dev/ship/target', kernel.O_WRONLY)
	if fd >= 0:
		kernel.sys_write(pid, fd, target_name.to_utf8_buffer())
		kernel.sys_close(pid, fd)
		pprint('Target set to: %s' % target_name)
		return 0
	pprint('Failed to set target')
	return 1
""")

	_create_command("fire", """# Fire weapon at target
if args.size() == 0:
	pprint('Usage: fire <weapon_index>')
	return 1
var weapon_idx = args[0]
var fd = kernel.sys_open(pid, '/dev/ship/actions/fire', kernel.O_WRONLY)
if fd >= 0:
	kernel.sys_write(pid, fd, weapon_idx.to_utf8_buffer())
	kernel.sys_close(pid, fd)
	pprint('Firing weapon %s' % weapon_idx)
	return 0
pprint('Failed to fire weapon')
return 1
""")

	_create_command("power", """# Allocate power to systems
if args.size() == 0:
	var fd = kernel.sys_open(pid, '/proc/ship/power_detail', kernel.O_RDONLY)
	if fd >= 0:
		var data = kernel.sys_read(pid, fd, 4096)
		kernel.sys_close(pid, fd)
		pprint(data.get_string_from_utf8())
		return 0
	return 1
else:
	var allocation = ' '.join(args)
	var fd = kernel.sys_open(pid, '/dev/ship/actions/power', kernel.O_WRONLY)
	if fd >= 0:
		kernel.sys_write(pid, fd, allocation.to_utf8_buffer())
		kernel.sys_close(pid, fd)
		pprint('Power allocated: %s' % allocation)
		return 0
	pprint('Failed to allocate power')
	return 1
""")

	_create_command("thrust", """# Control ship thrust
if args.size() == 0:
	pprint('Usage: thrust <forward|backward|stop|value>')
	return 1
var thrust_cmd = args[0]
var fd = kernel.sys_open(pid, '/dev/ship/actions/thrust', kernel.O_WRONLY)
if fd >= 0:
	kernel.sys_write(pid, fd, thrust_cmd.to_utf8_buffer())
	kernel.sys_close(pid, fd)
	pprint('Thrust: %s' % thrust_cmd)
	return 0
pprint('Failed to set thrust')
return 1
""")

	_create_command("turn", """# Control ship turning
if args.size() == 0:
	pprint('Usage: turn <left|right|stop|value>')
	return 1
var turn_cmd = args[0]
var fd = kernel.sys_open(pid, '/dev/ship/actions/turn', kernel.O_WRONLY)
if fd >= 0:
	kernel.sys_write(pid, fd, turn_cmd.to_utf8_buffer())
	kernel.sys_close(pid, fd)
	pprint('Turn: %s' % turn_cmd)
	return 0
pprint('Failed to turn')
return 1
""")

	_create_command("jump", """# Jump to galaxy position
if args.size() == 0:
	pprint('Usage: jump <position>')
	return 1
var destination = args[0]
var fd = kernel.sys_open(pid, '/dev/ship/actions/jump', kernel.O_WRONLY)
if fd >= 0:
	kernel.sys_write(pid, fd, destination.to_utf8_buffer())
	kernel.sys_close(pid, fd)
	pprint('Jumping to: %s' % destination)
	return 0
pprint('Failed to jump')
return 1
""")

	_create_command("send", """# Send bot to room
if args.size() < 2:
	pprint('Usage: send <bot_id> <room_name>')
	pprint('Example: send 1 Engine Room')
	pprint('Use \\'bots\\' to list available bots and their locations')
	return 1
var bot_id = args[0]
var room_name = ' '.join(args.slice(1))
var cmd = '%s %s' % [bot_id, room_name]
var fd = kernel.sys_open(pid, '/dev/ship/actions/bot', kernel.O_WRONLY)
if fd >= 0:
	kernel.sys_write(pid, fd, cmd.to_utf8_buffer())
	kernel.sys_close(pid, fd)
	pprint('Bot %s ordered to move to %s' % [bot_id, room_name])
	return 0
pprint('Failed to send bot')
return 1
""")

	print("[ShipOS] Populated /bin with commands")

## Helper to create a command file in /bin
func _create_command(name: String, script: String) -> void:
	var path = "/bin/" + name
	vfs.create_file(path, 0x1ED, 0, 0, script.to_utf8_buffer())  # 755 permissions

## Mount all ship device files
func _mount_ship_devices() -> void:
	# Read-only ship status devices (/dev/ship/*)
	_mount_device("/dev/ship/hull", _read_hull, null)
	_mount_device("/dev/ship/hull_max", _read_hull_max, null)
	_mount_device("/dev/ship/shields", _read_shields, null)
	_mount_device("/dev/ship/shields_max", _read_shields_max, null)
	_mount_device("/dev/ship/power", _read_power, null)
	_mount_device("/dev/ship/scrap", _read_scrap, null)
	_mount_device("/dev/ship/missiles", _read_missiles, null)
	_mount_device("/dev/ship/dark_matter", _read_dark_matter, null)

	# Read-only proc files (/proc/ship/*)
	_mount_device("/proc/ship/status", _read_ship_status, null)
	_mount_device("/proc/ship/weapons", _read_weapons_status, null)
	_mount_device("/proc/ship/systems", _read_systems_status, null)
	_mount_device("/proc/ship/crew", _read_crew_status, null)
	_mount_device("/proc/ship/rooms", _read_rooms_status, null)
	_mount_device("/proc/ship/sensors", _read_sensors, null)
	_mount_device("/proc/ship/position", _read_position, null)
	_mount_device("/proc/ship/bots", _read_bots_status, null)

	# Read-write target device
	_mount_device("/dev/ship/target", _read_target, _write_target)

	# Write-only action devices (/dev/ship/actions/*)
	vfs.mkdir("/dev/ship/actions", 0x1ED, 0, 0)  # 755
	_mount_device("/dev/ship/actions/fire", null, _write_fire_weapon)
	_mount_device("/dev/ship/actions/target", null, _write_set_target)
	_mount_device("/dev/ship/actions/jump", null, _write_jump)
	_mount_device("/dev/ship/actions/power", null, _write_allocate_power)
	_mount_device("/dev/ship/actions/bot", null, _write_bot_command)

## Helper to mount a device file
func _mount_device(path: String, read_handler: Variant, write_handler: Variant) -> void:
	var device_name = path.replace("/", "_")
	vfs.create_device(path, true, 0, 0, device_name)

	var read_cb = read_handler if read_handler is Callable else func(_size): return PackedByteArray()
	var write_cb = write_handler if write_handler is Callable else func(_data): return -1

	vfs.register_device(device_name, read_cb, write_cb)

	if write_handler is Callable:
		device_write_callbacks[path] = write_handler

## Update loop - sync ship state to OS
func update(delta: float) -> void:
	# Update PooScript processes (they run in background)
	pooscript.update(delta)

	# Device files automatically read current ship state when accessed
	# No need to manually update them - handlers read ship.* directly

## Spawn init process (runs on ship startup)
func _spawn_init_process() -> void:
	# Create a simple init script
	var ship_name_escaped = ship.ship_name
	var hull_val = ship.hull
	var hull_max_val = ship.hull_max

	var init_script = """pprint('[INIT] ShipOS booting for %s')
pprint('[INIT] Hull: %.1f/%.1f')
pprint('[INIT] Systems online')
return 0
""" % [ship_name_escaped, hull_val, hull_max_val]

	vfs.create_file("/sbin/init", 0x1ED, 0, 0, init_script.to_utf8_buffer())

	# Spawn init process (PID 1)
	pooscript.spawn("/sbin/init", [], {}, 0, 1)

#region Device Read Handlers (Ship state → Device data)

func _read_hull(_size: int) -> PackedByteArray:
	return ("%.1f" % ship.hull).to_utf8_buffer()

func _read_hull_max(_size: int) -> PackedByteArray:
	return ("%.1f" % ship.hull_max).to_utf8_buffer()

func _read_shields(_size: int) -> PackedByteArray:
	return ("%.1f" % ship.shields).to_utf8_buffer()

func _read_shields_max(_size: int) -> PackedByteArray:
	return ("%d" % ship.shields_max).to_utf8_buffer()

func _read_power(_size: int) -> PackedByteArray:
	return ("%d/%d" % [ship.power_available, ship.reactor_power]).to_utf8_buffer()

func _read_scrap(_size: int) -> PackedByteArray:
	return ("%d" % ship.scrap).to_utf8_buffer()

func _read_missiles(_size: int) -> PackedByteArray:
	return ("%d" % ship.missiles).to_utf8_buffer()

func _read_dark_matter(_size: int) -> PackedByteArray:
	return ("%d" % ship.dark_matter).to_utf8_buffer()

func _read_ship_status(_size: int) -> PackedByteArray:
	var status = """Ship: %s (%s)
Hull: %.1f/%.1f
Shields: %.1f/%d
Power: %d/%d
Scrap: %d
Missiles: %d
Dark Matter: %d
Position: %.1f
""" % [
		ship.ship_name, ship.ship_class,
		ship.hull, ship.hull_max,
		ship.shields, ship.shields_max,
		ship.power_available, ship.reactor_power,
		ship.scrap, ship.missiles, ship.dark_matter,
		ship.galaxy_position
	]
	return status.to_utf8_buffer()

func _read_weapons_status(_size: int) -> PackedByteArray:
	var status = "Weapons (%d):\n" % ship.weapons.size()
	for i in range(ship.weapons.size()):
		var w = ship.weapons[i]
		var ready = "READY" if w.is_ready() else "CHARGING"
		status += "  [%d] %s: %s (charge: %.0f%%)\n" % [i, w.weapon_name, ready, w.charge * 100]
	return status.to_utf8_buffer()

func _read_systems_status(_size: int) -> PackedByteArray:
	var status = "Systems:\n"
	for system_type in ship.systems:
		var sys: ShipSystem = ship.systems[system_type]
		var online = "ONLINE" if sys.is_online() else "OFFLINE"
		var effectiveness = sys.get_effectiveness() * 100
		status += "  %s: %s (%.0f%% effective)\n" % [sys.system_name, online, effectiveness]
	return status.to_utf8_buffer()

func _read_crew_status(_size: int) -> PackedByteArray:
	var status = "Crew (%d):\n" % ship.crew.size()
	for crew_member in ship.crew:
		var room_name = crew_member.current_room.room_name if crew_member.current_room else "None"
		var alive = "ALIVE" if crew_member.is_alive() else "DEAD"
		status += "  %s: %s (HP: %.0f/%.0f) [%s]\n" % [
			crew_member.crew_name, alive,
			crew_member.health, crew_member.health_max,
			room_name
		]
	return status.to_utf8_buffer()

func _read_rooms_status(_size: int) -> PackedByteArray:
	var status = "Rooms (%d):\n" % ship.rooms.size()
	for room_name in ship.rooms:
		var room: Room = ship.rooms[room_name]
		var functional = "OK" if room.is_functional() else "DAMAGED"
		var conditions = []
		if room.on_fire:
			conditions.append("FIRE")
		if room.breached:
			conditions.append("BREACH")
		if room.venting:
			conditions.append("VENTING")
		var cond_str = ", ".join(conditions) if conditions.size() > 0 else "Normal"
		status += "  %s: %s (HP: %.0f%%, Power: %d/%d) [%s]\n" % [
			room_name, functional,
			room.health * 100, room.power_allocated, room.max_power,
			cond_str
		]
	return status.to_utf8_buffer()

func _read_sensors(_size: int) -> PackedByteArray:
	var status = "Sensors - Contacts (%d):\n" % nearby_ships.size()
	if nearby_ships.is_empty():
		status += "  No contacts detected\n"
	else:
		for other_ship in nearby_ships:
			if other_ship == ship:
				continue  # Don't list ourselves
			var distance = abs(other_ship.galaxy_position - ship.galaxy_position)
			var bearing = "+" if other_ship.galaxy_position > ship.galaxy_position else "-"
			var is_target = " [TARGET]" if other_ship == current_target else ""
			status += "  %s: %.1f units %s (Hull: %.0f/%.0f)%s\n" % [
				other_ship.ship_name,
				distance,
				bearing,
				other_ship.hull,
				other_ship.hull_max,
				is_target
			]
	return status.to_utf8_buffer()

func _read_position(_size: int) -> PackedByteArray:
	var status = "Position: %.2f\nVelocity: %.2f\nTraveling: %s\n" % [
		ship.galaxy_position,
		ship.velocity,
		"Yes" if ship.is_traveling else "No"
	]
	return status.to_utf8_buffer()

func _read_target(_size: int) -> PackedByteArray:
	if current_target:
		var distance = abs(current_target.galaxy_position - ship.galaxy_position)
		var status = "Target: %s\nDistance: %.1f units\nHull: %.0f/%.0f\nShields: %.0f/%d\n" % [
			current_target.ship_name,
			distance,
			current_target.hull,
			current_target.hull_max,
			current_target.shields,
			current_target.shields_max
		]
		return status.to_utf8_buffer()
	else:
		return "No target selected\n".to_utf8_buffer()

func _read_bots_status(_size: int) -> PackedByteArray:
	var status = "Bots (%d):\n" % bots.size()
	if bots.is_empty():
		status += "  No bots available\n"
	else:
		for bot in bots:
			status += "  [%d] %s\n" % [bot.bot_id, bot.get_status()]
	return status.to_utf8_buffer()

#endregion

#region Device Write Handlers (Device writes → Ship actions)

func _write_fire_weapon(data: PackedByteArray) -> int:
	var weapon_idx = data.get_string_from_utf8().to_int()
	if weapon_idx >= 0 and weapon_idx < ship.weapons.size():
		var weapon = ship.weapons[weapon_idx]

		# Check if weapon is ready
		if not weapon.is_ready():
			print("[ShipOS] Weapon %d not ready" % weapon_idx)
			return -1

		# Check if we have a target
		if not current_target:
			print("[ShipOS] No target selected")
			return -1

		# Fire the weapon (consumes charge)
		if weapon.fire():
			print("[ShipOS] Fired weapon %d: %s at %s" % [weapon_idx, weapon.weapon_name, current_target.ship_name])

			# Notify CombatManager to spawn projectile (if available)
			if combat_manager:
				combat_manager.spawn_projectile(ship, current_target, weapon, weapon_idx)

			return data.size()
		else:
			print("[ShipOS] Weapon %d fire failed" % weapon_idx)
			return -1
	return -1

func _write_target(data: PackedByteArray) -> int:
	var target_name = data.get_string_from_utf8().strip_edges()

	# Find ship by name in nearby_ships
	for other_ship in nearby_ships:
		if other_ship.ship_name.to_lower() == target_name.to_lower():
			current_target = other_ship
			print("[ShipOS] Target acquired: %s" % other_ship.ship_name)
			return data.size()

	# Clear target if empty or not found
	if target_name.is_empty() or target_name.to_lower() == "none":
		current_target = null
		print("[ShipOS] Target cleared")
		return data.size()

	print("[ShipOS] Target not found: %s" % target_name)
	return -1

func _write_set_target(data: PackedByteArray) -> int:
	# Legacy action device - redirects to _write_target
	return _write_target(data)

func _write_jump(data: PackedByteArray) -> int:
	var destination = data.get_string_from_utf8().to_float()
	print("[ShipOS] Initiating jump to: %.1f" % destination)
	ship.target_position = destination
	ship.is_traveling = true
	return data.size()

func _write_allocate_power(data: PackedByteArray) -> int:
	var power_cmd = data.get_string_from_utf8()
	print("[ShipOS] Power allocation: %s" % power_cmd)
	# TODO: Parse power allocation command
	# Format: "weapons:3,shields:2,engines:3"
	return data.size()

func _write_bot_command(data: PackedByteArray) -> int:
	var cmd = data.get_string_from_utf8().strip_edges()
	var parts = cmd.split(" ", false)

	if parts.size() < 2:
		print("[ShipOS] Invalid bot command format. Use: <bot_id> <room_name>")
		return -1

	var bot_id = parts[0].to_int()
	var room_name = " ".join(parts.slice(1))  # Room name may have spaces

	# Find bot
	var target_bot = null
	for bot in bots:
		if bot.bot_id == bot_id:
			target_bot = bot
			break

	if not target_bot:
		print("[ShipOS] Bot %d not found" % bot_id)
		return -1

	# Find room
	var target_room = null
	for room in ship_rooms:
		if room.get_name().to_lower() == room_name.to_lower():
			target_room = room
			break

	if not target_room:
		print("[ShipOS] Room '%s' not found" % room_name)
		return -1

	# Send bot to room
	target_bot.move_to_room(target_room)
	print("[ShipOS] Bot %d ordered to move to %s" % [bot_id, target_room.get_name()])
	return data.size()

#endregion

## Helper: Execute a command in the OS
func execute_command(command: String, args: Array = [], env: Dictionary = {}) -> int:
	# Check if command file exists
	var cmd_path = command if command.begins_with("/") else "/bin/" + command
	if not vfs.path_exists(cmd_path):
		print("[ShipOS] Command not found: %s" % command)
		return -1

	# Spawn as process
	var pid = pooscript.spawn(cmd_path, args, env, 0, 1)
	return pid

## Helper: Get process list
func get_processes() -> Array:
	return pooscript.ps()

## Helper: Kill a process
func kill_process(pid: int) -> bool:
	return pooscript.kill_process(pid)

## Helper: Read a device file (for external access)
func read_device(path: String) -> String:
	var data = vfs.read_file(path)
	if data:
		return data.get_string_from_utf8()
	return ""

## Helper: Write to a device file (for external access)
func write_device(path: String, data: String) -> bool:
	return vfs.write_file(path, data.to_utf8_buffer())

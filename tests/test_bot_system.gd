extends SceneTree

## Test bot spawning and control system

func _init():
	print("\n=== Testing Bot System ===\n")

	# Create ship layout
	var layout = ShipGenerator.generate_basic_ship()
	print("✓ Ship layout created with %d rooms" % layout.rooms.size())

	# Create ShipOS
	var ship = Ship.new("Test Ship", "Cruiser")
	var ship_os = ShipOS.new(ship)
	print("✓ ShipOS created")

	# Create bots
	var bots: Array[Bot] = []

	# Bot 1 - Engineer
	var bot1 = Bot.new()
	bot1.bot_id = 1
	bot1.bot_name = "Engineer"
	bot1.bot_color = Color(0.8, 0.4, 0.2)
	var engine_room = _find_room_by_type(layout, RoomSystem.RoomType.ENGINE)
	if engine_room:
		bot1.position = engine_room.world_position + Vector3(1.5, 0, 1.5)
		bot1.set_current_room(engine_room)
		bots.append(bot1)
		print("✓ Created Engineer bot in %s" % engine_room.get_name())

	# Bot 2 - Gunner
	var bot2 = Bot.new()
	bot2.bot_id = 2
	bot2.bot_name = "Gunner"
	bot2.bot_color = Color(0.8, 0.2, 0.2)
	var weapons_room = _find_room_by_type(layout, RoomSystem.RoomType.WEAPONS)
	if weapons_room:
		bot2.position = weapons_room.world_position + Vector3(2.0, 0, 1.5)
		bot2.set_current_room(weapons_room)
		bots.append(bot2)
		print("✓ Created Gunner bot in %s" % weapons_room.get_name())

	# Register bots with ShipOS
	ship_os.bots = bots
	ship_os.ship_rooms = layout.rooms
	print("✓ Registered %d bots with ShipOS" % bots.size())

	# Test 'bots' command
	print("\n--- Testing 'bots' command ---")
	var bots_output = ship_os.read_device("/proc/ship/bots")
	print(bots_output)

	# Test bot status
	print("\n--- Testing bot status ---")
	for bot in bots:
		print(bot.get_status())

	# Test 'send' command
	print("\n--- Testing bot movement command ---")
	var helm_room = _find_room_by_type(layout, RoomSystem.RoomType.HELM)
	if helm_room:
		print("Sending Bot 1 to %s" % helm_room.get_name())
		var success = ship_os.write_device("/dev/ship/actions/bot", "1 %s" % helm_room.get_name())
		if success:
			print("✓ Bot 1 movement command accepted")
			print("  Target room: %s" % helm_room.get_name())
			if bot1.target_room:
				print("  Bot 1 is now moving: %s" % bot1.is_moving)
		else:
			print("✗ Bot 1 movement command failed")

	# Test command execution
	print("\n--- Testing command execution ---")
	var pid = ship_os.execute_command("bots", [])
	if pid > 0:
		var process = ship_os.pooscript.get_process(pid)
		if process and process.script_obj:
			var output = process.script_obj.call("get_output")
			print("Command output:")
			print(output)
			ship_os.pooscript.reap(pid)
		print("✓ 'bots' command executed (PID: %d)" % pid)
	else:
		print("✗ 'bots' command failed")

	# Test send command
	print("\n--- Testing 'send' command execution ---")
	var send_pid = ship_os.execute_command("send", ["2", "Helm"])
	if send_pid > 0:
		var send_process = ship_os.pooscript.get_process(send_pid)
		if send_process and send_process.script_obj:
			var send_output = send_process.script_obj.call("get_output")
			print("Command output:")
			print(send_output)
			ship_os.pooscript.reap(send_pid)
		print("✓ 'send' command executed (PID: %d)" % send_pid)
		if bot2.is_moving:
			print("✓ Bot 2 is moving to target room")
	else:
		print("✗ 'send' command failed")

	print("\n=== All Bot System Tests Complete ===\n")
	quit()

func _find_room_by_type(layout: RoomSystem.ShipLayout, type: RoomSystem.RoomType) -> RoomSystem.RoomInstance:
	for room in layout.rooms:
		if room.type == type:
			return room
	return null

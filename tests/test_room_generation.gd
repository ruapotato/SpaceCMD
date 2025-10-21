extends Node

## Test procedural room generation

func _ready():
	print("\n============================================================")
	print("TEST: Room Generation System")
	print("============================================================\n")

	test_basic_ship()
	test_random_ship()
	test_room_connections()

	print("\n============================================================")
	print("All room generation tests complete!")
	print("============================================================\n")

	get_tree().quit()

func test_basic_ship():
	print("--- Test 1: Generate Basic Ship ---")

	var layout = ShipGenerator.generate_basic_ship()

	check(layout != null, "Layout should be created")
	check(layout.rooms.size() >= 3, "Should have at least 3 required rooms")

	# Check for required rooms
	var has_helm = false
	var has_reactor = false
	var has_engine = false

	for room in layout.rooms:
		if room.type == RoomSystem.RoomType.HELM:
			has_helm = true
		elif room.type == RoomSystem.RoomType.REACTOR:
			has_reactor = true
		elif room.type == RoomSystem.RoomType.ENGINE:
			has_engine = true

	check(has_helm, "Should have helm")
	check(has_reactor, "Should have reactor")
	check(has_engine, "Should have engine")

	print("[PASS] Basic ship generated with %d rooms" % layout.rooms.size())

func test_random_ship():
	print("\n--- Test 2: Generate Random Ship ---")

	var layout = ShipGenerator.generate_random_ship(Vector2i(10, 5), 6)

	check(layout != null, "Layout should be created")
	check(layout.rooms.size() > 0, "Should have rooms")

	print("[PASS] Random ship generated with %d rooms" % layout.rooms.size())

func test_room_connections():
	print("\n--- Test 3: Room Connections ---")

	var layout = ShipGenerator.generate_basic_ship()

	var total_connections = 0
	for room in layout.rooms:
		total_connections += room.connections.size()
		print("  %s has %d connections" % [room.get_name(), room.connections.size()])

	check(total_connections > 0, "Rooms should have connections")

	print("[PASS] Rooms are connected")

func check(condition: bool, message: String):
	if not condition:
		push_error("ASSERTION FAILED: " + message)
		get_tree().quit(1)

extends Node
class_name ShipGenerator

## Procedurally generates ship layouts with interconnected rooms

static func generate_basic_ship() -> RoomSystem.ShipLayout:
	"""Generate a plus-shaped ship with uniform 2x2 rooms and 2x2 corridors"""
	var layout = RoomSystem.ShipLayout.new(Vector2i(16, 16))

	# Helm in center (7, 7) - 2x2
	var helm = RoomSystem.RoomInstance.new(RoomSystem.RoomType.HELM, Vector2i(7, 7))
	layout.place_room(helm)

	# North corridor and Weapons
	var north_corridor = RoomSystem.RoomInstance.new(RoomSystem.RoomType.CORRIDOR, Vector2i(7, 5))
	var weapons = RoomSystem.RoomInstance.new(RoomSystem.RoomType.WEAPONS, Vector2i(7, 3))
	layout.place_room(north_corridor)
	layout.place_room(weapons)

	# South corridor and Engine
	var south_corridor = RoomSystem.RoomInstance.new(RoomSystem.RoomType.CORRIDOR, Vector2i(7, 9))
	var engine = RoomSystem.RoomInstance.new(RoomSystem.RoomType.ENGINE, Vector2i(7, 11))
	layout.place_room(south_corridor)
	layout.place_room(engine)

	# East corridor and Reactor
	var east_corridor = RoomSystem.RoomInstance.new(RoomSystem.RoomType.CORRIDOR, Vector2i(9, 7))
	var reactor = RoomSystem.RoomInstance.new(RoomSystem.RoomType.REACTOR, Vector2i(11, 7))
	layout.place_room(east_corridor)
	layout.place_room(reactor)

	# West corridor and Shields
	var west_corridor = RoomSystem.RoomInstance.new(RoomSystem.RoomType.CORRIDOR, Vector2i(5, 7))
	var shields = RoomSystem.RoomInstance.new(RoomSystem.RoomType.SHIELDS, Vector2i(3, 7))
	layout.place_room(west_corridor)
	layout.place_room(shields)

	# Connect adjacent rooms with doorways
	layout.connect_adjacent_rooms()

	print("[ShipGenerator] Generated plus-shaped ship (all rooms and corridors 2x2):")
	print("  - Rooms: %d" % layout.rooms.size())
	for room in layout.rooms:
		print("    - %s at %v size %v (connections: %d)" % [room.get_name(), room.grid_position, room.size, room.connections.size()])

	return layout

static func generate_random_ship(grid_size: Vector2i = Vector2i(10, 5), room_count: int = 6) -> RoomSystem.ShipLayout:
	"""Generate a random ship layout"""
	var layout = RoomSystem.ShipLayout.new(grid_size)

	# Always include required rooms
	var required_types = [
		RoomSystem.RoomType.HELM,
		RoomSystem.RoomType.REACTOR,
		RoomSystem.RoomType.ENGINE
	]

	# Optional room pool
	var optional_types = [
		RoomSystem.RoomType.WEAPONS,
		RoomSystem.RoomType.REPAIR_BAY,
		RoomSystem.RoomType.SHIELDS,
		RoomSystem.RoomType.CREW_QUARTERS,
		RoomSystem.RoomType.CARGO
	]

	# Place required rooms first
	for room_type in required_types:
		var placed = false
		var attempts = 0
		while not placed and attempts < 20:
			var pos = Vector2i(randi() % (grid_size.x - 2), randi() % (grid_size.y - 2))
			var room = RoomSystem.RoomInstance.new(room_type, pos)
			placed = layout.place_room(room)
			attempts += 1

		if not placed:
			push_error("[ShipGenerator] Failed to place required room: %d" % room_type)

	# Place optional rooms
	var rooms_placed = layout.rooms.size()
	while rooms_placed < room_count:
		var room_type = optional_types[randi() % optional_types.size()]
		var pos = Vector2i(randi() % (grid_size.x - 2), randi() % (grid_size.y - 2))
		var room = RoomSystem.RoomInstance.new(room_type, pos)

		if layout.place_room(room):
			rooms_placed += 1

	# Connect adjacent rooms
	layout.connect_adjacent_rooms()

	print("[ShipGenerator] Generated random ship:")
	print("  - Rooms: %d" % layout.rooms.size())

	return layout

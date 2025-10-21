extends Node
class_name RoomSystem

## Room types available in ships
enum RoomType {
	HELM,         # Bridge - navigation, sensors, targeting
	ENGINE,       # Engines - propulsion, FTL
	WEAPONS,      # Weapons control - firing, targeting
	REACTOR,      # Power core - power allocation
	REPAIR_BAY,   # Bot repair station
	SHIELDS,      # Shield control
	CREW_QUARTERS, # Bot storage/charging
	CARGO,        # Storage
	CORRIDOR      # Connecting hallway
}

## Room metadata - defines what each room type does
const ROOM_DATA = {
	RoomType.HELM: {
		"name": "Helm",
		"description": "Ship control and navigation",
		"console_type": "helm",
		"required": true,  # Must exist on every ship
		"size": Vector2i(2, 2),  # Grid size
		"color": Color(0.2, 0.4, 0.8)
	},
	RoomType.ENGINE: {
		"name": "Engine Room",
		"description": "Propulsion systems",
		"console_type": "engine",
		"required": true,
		"size": Vector2i(2, 2),
		"color": Color(0.8, 0.4, 0.2)
	},
	RoomType.WEAPONS: {
		"name": "Weapons Bay",
		"description": "Weapon control systems",
		"console_type": "weapons",
		"required": false,
		"size": Vector2i(2, 2),  # Standardized to 2x2
		"color": Color(0.8, 0.2, 0.2)
	},
	RoomType.REACTOR: {
		"name": "Reactor Core",
		"description": "Power generation and distribution",
		"console_type": "reactor",
		"required": true,
		"size": Vector2i(2, 2),
		"color": Color(0.2, 0.8, 0.2)
	},
	RoomType.REPAIR_BAY: {
		"name": "Repair Bay",
		"description": "Bot maintenance and repair",
		"console_type": "repair",
		"required": false,
		"size": Vector2i(2, 2),  # Standardized to 2x2
		"color": Color(0.6, 0.6, 0.2)
	},
	RoomType.SHIELDS: {
		"name": "Shield Generator",
		"description": "Defensive systems",
		"console_type": "shields",
		"required": false,
		"size": Vector2i(2, 2),  # Standardized to 2x2
		"color": Color(0.2, 0.6, 0.8)
	},
	RoomType.CREW_QUARTERS: {
		"name": "Crew Quarters",
		"description": "Bot charging stations",
		"console_type": null,
		"required": false,
		"size": Vector2i(2, 2),  # Standardized to 2x2
		"color": Color(0.4, 0.4, 0.4)
	},
	RoomType.CARGO: {
		"name": "Cargo Bay",
		"description": "Storage",
		"console_type": null,
		"required": false,
		"size": Vector2i(2, 2),
		"color": Color(0.3, 0.3, 0.3)
	},
	RoomType.CORRIDOR: {
		"name": "Corridor",
		"description": "Connecting passage",
		"console_type": null,
		"required": false,
		"size": Vector2i(2, 2),  # Standardized to 2x2
		"color": Color(0.25, 0.25, 0.25)
	}
}

## Individual room instance
class RoomInstance:
	var type: RoomType
	var grid_position: Vector2i  # Position in ship grid
	var size: Vector2i           # Size in grid units
	var connections: Array[RoomInstance] = []  # Connected rooms
	var doorways: Array[Dictionary] = []  # {direction: Vector3, to_room: RoomInstance}
	var consoles: Array[Node3D] = []  # Console objects in this room
	var world_position: Vector3 = Vector3.ZERO  # 3D world position

	func _init(room_type: RoomType, grid_pos: Vector2i):
		type = room_type
		grid_position = grid_pos
		size = RoomSystem.ROOM_DATA[type]["size"]

	func get_name() -> String:
		return RoomSystem.ROOM_DATA[type]["name"]

	func get_color() -> Color:
		return RoomSystem.ROOM_DATA[type]["color"]

	func get_console_type() -> String:
		var console = RoomSystem.ROOM_DATA[type].get("console_type")
		return console if console != null else ""

	func has_console() -> bool:
		return get_console_type() != ""

	func add_connection(room: RoomInstance, direction: Vector2i):
		if room not in connections:
			connections.append(room)
			doorways.append({
				"to_room": room,
				"direction": direction
			})

## Ship layout - collection of rooms
class ShipLayout:
	var rooms: Array[RoomInstance] = []
	var grid_size: Vector2i = Vector2i(8, 4)  # Default ship grid
	var grid: Array = []  # 2D array of room assignments

	func _init(size: Vector2i = Vector2i(8, 4)):
		grid_size = size
		_initialize_grid()

	func _initialize_grid():
		grid.clear()
		for y in range(grid_size.y):
			var row = []
			for x in range(grid_size.x):
				row.append(null)
			grid.append(row)

	func can_place_room(pos: Vector2i, size: Vector2i) -> bool:
		"""Check if a room can be placed at position"""
		if pos.x < 0 or pos.y < 0:
			return false
		if pos.x + size.x > grid_size.x or pos.y + size.y > grid_size.y:
			return false

		# Check if all cells are empty
		for y in range(size.y):
			for x in range(size.x):
				if grid[pos.y + y][pos.x + x] != null:
					return false
		return true

	func place_room(room: RoomInstance) -> bool:
		"""Place a room on the grid"""
		if not can_place_room(room.grid_position, room.size):
			return false

		# Mark grid cells as occupied
		for y in range(room.size.y):
			for x in range(room.size.x):
				grid[room.grid_position.y + y][room.grid_position.x + x] = room

		rooms.append(room)
		return true

	func get_room_at(pos: Vector2i) -> RoomInstance:
		"""Get room at grid position"""
		if pos.x < 0 or pos.y < 0 or pos.x >= grid_size.x or pos.y >= grid_size.y:
			return null
		return grid[pos.y][pos.x]

	func find_adjacent_rooms(room: RoomInstance) -> Array[Dictionary]:
		"""Find rooms adjacent to this room"""
		var adjacent: Array[Dictionary] = []
		var directions = [
			Vector2i(1, 0),   # Right
			Vector2i(-1, 0),  # Left
			Vector2i(0, 1),   # Down
			Vector2i(0, -1)   # Up
		]

		for dir in directions:
			# Check all edges of the room
			for y in range(room.size.y):
				for x in range(room.size.x):
					var check_pos = room.grid_position + Vector2i(x, y) + dir
					var other_room = get_room_at(check_pos)

					if other_room and other_room != room:
						# Found adjacent room
						var already_added = false
						for adj in adjacent:
							if adj["room"] == other_room:
								already_added = true
								break

						if not already_added:
							adjacent.append({
								"room": other_room,
								"direction": dir
							})

		return adjacent

	func connect_adjacent_rooms():
		"""Automatically create doorways between adjacent rooms"""
		for room in rooms:
			var adjacent = find_adjacent_rooms(room)
			for adj in adjacent:
				room.add_connection(adj["room"], adj["direction"])

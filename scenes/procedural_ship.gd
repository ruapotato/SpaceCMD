extends Node3D

## Procedurally generated ship interior
## Creates rooms, places consoles, spawns player

@export var use_random_layout: bool = false
@export var grid_size: Vector2i = Vector2i(10, 5)
@export var room_count: int = 6

@onready var terminal_ui: TerminalUI = $TerminalUI

var ship_layout: RoomSystem.ShipLayout
var generated_ship: Node3D
var player: PlayerBot
var ship_os: ShipOS
var consoles: Array[HelmConsole] = []
var bots: Array[Bot] = []  # Additional crew bots

func _ready() -> void:
	# Generate ship layout
	if use_random_layout:
		ship_layout = ShipGenerator.generate_random_ship(grid_size, room_count)
	else:
		ship_layout = ShipGenerator.generate_basic_ship()

	# Generate 3D mesh
	var mesh_generator = RoomMeshGenerator.new()
	generated_ship = mesh_generator.generate_ship_mesh(ship_layout)
	add_child(generated_ship)

	# Create ShipOS
	create_ship_os()

	# Place consoles in rooms
	place_consoles(mesh_generator)

	# Spawn player in first room
	spawn_player()

	# Spawn additional crew bots
	spawn_crew_bots()

	# Connect terminal UI
	setup_terminal()

	print("[ProceduralShip] Ship generation complete!")
	print("  - Rooms: %d" % ship_layout.rooms.size())
	print("  - Consoles: %d" % consoles.size())
	print("  - Crew bots: %d" % bots.size())

func create_ship_os() -> void:
	"""Create ShipOS for this ship"""
	var ship = Ship.new("Procedural Ship", "Cruiser")
	ship.position = Vector3(0, 0, 0)
	ship_os = ShipOS.new(ship)
	print("[ProceduralShip] ShipOS created")

func place_consoles(mesh_generator: RoomMeshGenerator) -> void:
	"""Place consoles in rooms that need them"""
	for room in ship_layout.rooms:
		if room.has_console():
			var console = create_console_for_room(room, mesh_generator)
			if console:
				consoles.append(console)
				room.consoles.append(console)

				# Add to generated ship
				generated_ship.add_child(console)

func create_console_for_room(room: RoomSystem.RoomInstance, mesh_generator: RoomMeshGenerator) -> HelmConsole:
	"""Create a console appropriate for the room type"""
	# Load console scene
	var console_scene = load("res://player/helm_console.tscn")
	var console: HelmConsole = console_scene.instantiate()

	# Position console in center of room
	var room_width = room.size.x * mesh_generator.ROOM_CELL_SIZE
	var room_depth = room.size.y * mesh_generator.ROOM_CELL_SIZE

	console.position = room.world_position + Vector3(
		room_width / 2,
		0,
		room_depth / 2 - 1.0  # Slightly offset toward front
	)

	# Set console properties
	console.console_name = room.get_name()
	console.set("ship_os", ship_os)  # Set dynamically to avoid type checking

	print("[ProceduralShip] Placed %s console in %s at %v" % [room.get_console_type(), room.get_name(), console.position])

	return console

func spawn_player() -> void:
	"""Spawn player bot in first room"""
	if ship_layout.rooms.is_empty():
		push_error("[ProceduralShip] No rooms to spawn player in!")
		return

	# Spawn in helm if available, otherwise first room
	var spawn_room = ship_layout.rooms[0]
	for room in ship_layout.rooms:
		if room.type == RoomSystem.RoomType.HELM:
			spawn_room = room
			break

	# Load player scene
	var player_scene = load("res://player/player_bot.tscn")
	player = player_scene.instantiate()

	# Position player in room
	var spawn_pos = spawn_room.world_position + Vector3(2.0, 0, 2.0)
	player.position = spawn_pos

	add_child(player)

	print("[ProceduralShip] Player spawned in %s at %v" % [spawn_room.get_name(), spawn_pos])

func spawn_crew_bots() -> void:
	"""Spawn 2 additional crew bots in different rooms"""
	if ship_layout.rooms.size() < 3:
		push_error("[ProceduralShip] Not enough rooms for crew bots!")
		return

	# Bot 1: Spawn in Engine room (or second room)
	var bot1_room = _find_room_by_type(RoomSystem.RoomType.ENGINE)
	if not bot1_room and ship_layout.rooms.size() > 1:
		bot1_room = ship_layout.rooms[1]

	if bot1_room:
		var bot1 = _create_bot(1, "Engineer", Color(0.8, 0.4, 0.2), bot1_room)
		bots.append(bot1)
		add_child(bot1)

	# Bot 2: Spawn in Weapons room (or third room)
	var bot2_room = _find_room_by_type(RoomSystem.RoomType.WEAPONS)
	if not bot2_room and ship_layout.rooms.size() > 2:
		bot2_room = ship_layout.rooms[2]

	if bot2_room:
		var bot2 = _create_bot(2, "Gunner", Color(0.8, 0.2, 0.2), bot2_room)
		bots.append(bot2)
		add_child(bot2)

	# Register bots and rooms with ShipOS
	if ship_os:
		ship_os.set("bots", bots)
		ship_os.set("ship_rooms", ship_layout.rooms)

	print("[ProceduralShip] Spawned %d crew bots" % bots.size())

func _create_bot(id: int, bot_name: String, color: Color, room: RoomSystem.RoomInstance) -> Bot:
	"""Create and configure a bot"""
	var bot_scene = load("res://player/bot.tscn")
	var bot: Bot = bot_scene.instantiate()

	bot.bot_id = id
	bot.bot_name = bot_name
	bot.bot_color = color

	# Position bot in room
	var spawn_pos = room.world_position + Vector3(1.5 + (id * 0.5), 0, 1.5)
	bot.position = spawn_pos
	bot.set_current_room(room)

	# Connect signals
	bot.arrived_at_room.connect(_on_bot_arrived)
	bot.movement_started.connect(_on_bot_movement_started)

	print("[ProceduralShip] Spawned %s (ID:%d) in %s at %v" % [bot_name, id, room.get_name(), spawn_pos])

	return bot

func _find_room_by_type(type: RoomSystem.RoomType) -> RoomSystem.RoomInstance:
	"""Find a room by its type"""
	for room in ship_layout.rooms:
		if room.type == type:
			return room
	return null

func _on_bot_arrived(room: RoomSystem.RoomInstance) -> void:
	"""Handle bot arrival at room"""
	print("[ProceduralShip] Bot arrived at %s" % room.get_name())

func _on_bot_movement_started(room: RoomSystem.RoomInstance) -> void:
	"""Handle bot starting movement"""
	print("[ProceduralShip] Bot moving to %s" % room.get_name())

func setup_terminal() -> void:
	"""Setup terminal UI connections"""
	if not player or not terminal_ui:
		return

	# Connect player signals
	player.terminal_mode_changed.connect(_on_terminal_mode_changed)
	player.interacted_with.connect(_on_player_interacted)

	# Connect console signals
	for console in consoles:
		console.console_activated.connect(_on_console_activated)
		console.console_deactivated.connect(_on_console_deactivated)

	terminal_ui.hide()

func _on_terminal_mode_changed(enabled: bool) -> void:
	"""Handle terminal mode changes"""
	if not enabled and terminal_ui and terminal_ui.visible:
		terminal_ui.close_console()

func _on_player_interacted(object: Node) -> void:
	"""Handle player interaction"""
	print("[ProceduralShip] Player interacted with: %s" % object.name)

func _on_console_activated(console: HelmConsole) -> void:
	"""Handle console activation"""
	if terminal_ui:
		terminal_ui.open_console(console)

func _on_console_deactivated(console: HelmConsole) -> void:
	"""Handle console deactivation"""
	if terminal_ui:
		terminal_ui.close_console()

func _input(event: InputEvent) -> void:
	"""Handle global input"""
	if event.is_action_pressed("ui_cancel"):
		if terminal_ui and terminal_ui.visible:
			# Find active console
			for console in consoles:
				if console.is_active:
					console.deactivate(player)
					break
			get_viewport().set_input_as_handled()

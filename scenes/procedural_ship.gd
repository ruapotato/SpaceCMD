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

	# Connect terminal UI
	setup_terminal()

	print("[ProceduralShip] Ship generation complete!")
	print("  - Rooms: %d" % ship_layout.rooms.size())
	print("  - Consoles: %d" % consoles.size())

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

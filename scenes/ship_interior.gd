extends Node3D

## Ship Interior Scene Controller
## Manages player, terminals, and mode switching

@onready var player: PlayerBot = $PlayerBot
@onready var terminal_ui: TerminalUI = $TerminalUI
@onready var helm_console: HelmConsole = $HelmConsole

# Ship OS - will be connected to this ship's OS
var ship_os: ShipOS = null

func _ready() -> void:
	# Connect signals
	if player:
		player.terminal_mode_changed.connect(_on_terminal_mode_changed)
		player.interacted_with.connect(_on_player_interacted)

	if helm_console:
		helm_console.console_activated.connect(_on_console_activated)
		helm_console.console_deactivated.connect(_on_console_deactivated)

	# Hide terminal UI initially
	if terminal_ui:
		terminal_ui.hide()

	# Create a test ShipOS for the helm
	create_test_ship_os()

func create_test_ship_os() -> void:
	"""Create a test ShipOS instance for testing terminal"""
	# Create a dummy ship
	var ship = Ship.new("Test Ship", "Cruiser")
	ship.position = Vector3(0, 0, 0)

	# Create ShipOS for this ship
	ship_os = ShipOS.new(ship)

	# Connect to helm console
	if helm_console:
		helm_console.set("ship_os", ship_os)  # Set dynamically to avoid type checking

	print("[ShipInterior] Test ShipOS created and connected to helm")

func _on_terminal_mode_changed(enabled: bool) -> void:
	"""Handle terminal mode changes"""
	if enabled:
		print("[ShipInterior] Entering terminal mode")
	else:
		print("[ShipInterior] Exiting terminal mode")
		if terminal_ui and terminal_ui.visible:
			terminal_ui.close_console()

func _on_player_interacted(object: Node) -> void:
	"""Handle player interaction with objects"""
	print("[ShipInterior] Player interacted with: %s" % object.name)

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
	# ESC to exit terminal mode
	if event.is_action_pressed("ui_cancel"):
		if terminal_ui and terminal_ui.visible:
			if helm_console and helm_console.is_active:
				helm_console.deactivate(player)
			get_viewport().set_input_as_handled()

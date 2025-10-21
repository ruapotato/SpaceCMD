extends StaticBody3D
class_name HelmConsole

## Helm console - interactable terminal for ship control
## When player presses E, opens fullscreen terminal UI

@export var console_name: String = "Helm"

var ship_os = null  # ShipOS instance - set at runtime

signal console_activated(console: HelmConsole)
signal console_deactivated(console: HelmConsole)

var is_active: bool = false

func _ready() -> void:
	# Add to "interactable" group for easier identification
	add_to_group("interactable")

func can_interact() -> bool:
	"""Returns true if this console can be interacted with"""
	return not is_active

func interact(player: PlayerBot) -> void:
	"""Called when player presses E while looking at this console"""
	if can_interact():
		activate(player)

func activate(player: PlayerBot) -> void:
	"""Activate the console (enter terminal mode)"""
	is_active = true
	player.enter_terminal_mode()
	console_activated.emit(self)
	print("[HelmConsole] %s console activated" % console_name)

func deactivate(player: PlayerBot) -> void:
	"""Deactivate the console (exit terminal mode)"""
	is_active = false
	if player:
		player.exit_terminal_mode()
	console_deactivated.emit(self)
	print("[HelmConsole] %s console deactivated" % console_name)

func execute_command(command: String) -> String:
	"""Execute a command on the ship's OS"""
	if not ship_os:
		return "ERROR: No ShipOS connected to this console"

	# TODO: Parse and execute command through ShipOS
	# For now, just echo
	return "> %s\nCommand executed (not yet implemented)" % command

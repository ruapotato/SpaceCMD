extends Control
class_name TerminalUI

## Fullscreen terminal interface
## Shows when player interacts with helm console
## Hides when player presses Escape

@onready var output_text: TextEdit = $Panel/VBoxContainer/OutputText
@onready var input_line: LineEdit = $Panel/VBoxContainer/InputLine
@onready var console_label: Label = $Panel/VBoxContainer/ConsoleLabel

var current_console: HelmConsole = null
var command_history: Array[String] = []
var history_index: int = -1

signal command_executed(command: String, result: String)

func _ready() -> void:
	hide()
	input_line.text_submitted.connect(_on_command_submitted)
	clear_output()

func _input(event: InputEvent) -> void:
	if not visible:
		return

	# Command history navigation
	if event.is_action_pressed("ui_up"):
		navigate_history(-1)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("ui_down"):
		navigate_history(1)
		get_viewport().set_input_as_handled()

func open_console(console: HelmConsole) -> void:
	"""Open terminal UI for a specific console"""
	current_console = console
	console_label.text = "=== %s Console ===" % console.console_name
	show()
	input_line.grab_focus()

	# Welcome message
	append_output("SpaceOS v1.0 - Ship Operating System")
	append_output("Type 'help' for available commands")
	append_output("")

func close_console() -> void:
	"""Close terminal UI"""
	hide()
	if current_console:
		current_console.is_active = false
		current_console = null

func _on_command_submitted(command: String) -> void:
	"""Handle command submission"""
	if command.strip_edges().is_empty():
		return

	# Add to history
	command_history.append(command)
	history_index = command_history.size()

	# Echo command
	append_output("> %s" % command)

	# Execute command
	var result: String = ""
	if current_console and current_console.get("ship_os"):
		result = execute_ship_command(command)
		print("[TerminalUI] Received result from execute_ship_command: '", result, "'")
	else:
		# No ShipOS connected - show error
		var parts = command.split(" ", false)
		if not parts.is_empty() and parts[0] == "clear":
			clear_output()
		else:
			result = "ERROR: No ShipOS connected. Cannot execute commands."

	# Show result - always show something even if empty (for debugging)
	if not result.is_empty():
		append_output(result)
	else:
		append_output("[No output from command]")

	append_output("")  # Blank line

	# Clear input
	input_line.clear()

	# Emit signal
	command_executed.emit(command, result)

func execute_ship_command(command: String) -> String:
	"""Execute command on ship OS"""
	# Parse command (basic shell-like parsing)
	var parts = command.split(" ", false)
	if parts.is_empty():
		return ""

	var cmd = parts[0]
	var args = parts.slice(1) if parts.size() > 1 else []

	# Handle special commands that don't need ShipOS
	if cmd == "clear":
		clear_output()
		return ""

	# Execute command through ShipOS
	var ship_os_ref = current_console.get("ship_os") if current_console else null
	if not ship_os_ref:
		return "ERROR: No ShipOS connected"

	# Check if command exists in /bin
	var cmd_path = "/bin/" + cmd
	var os = ship_os_ref
	var vfs = os.get("vfs")
	if not vfs:
		return "ERROR: No VFS available"

	if not vfs.path_exists(cmd_path):
		return "Command not found: %s (type 'help' for available commands)" % cmd

	# Spawn command as process and capture output
	var pooscript = os.get("pooscript")
	if not pooscript:
		return "ERROR: No PooScript engine available"

	# Execute command (spawns and runs to completion immediately)
	var pid = pooscript.spawn(cmd_path, args, {"PWD": "/"}, 0, 1)

	if pid <= 0:
		return "ERROR: Failed to spawn command"

	# Get process and retrieve output
	var process = pooscript.get_process(pid)
	if not process:
		return "ERROR: Process not found"

	# Get script object and retrieve captured output
	var script_obj = process.script_obj

	if not script_obj:
		print("[TerminalUI] ERROR: No script_obj!")
		pooscript.reap(pid)
		return "ERROR: No script object"

	if not script_obj.has_method("get_output"):
		print("[TerminalUI] ERROR: No get_output method!")
		pooscript.reap(pid)
		return "ERROR: No get_output method"

	var output = script_obj.call("get_output")
	print("[TerminalUI] Command output: '", output, "' (length: ", output.length() if output is String else "N/A", ")")

	# Clean up zombie process
	pooscript.reap(pid)

	# Return the output - even if empty, let the caller decide what to do
	if output is String:
		return output
	else:
		return "ERROR: Output is not a string: " + str(typeof(output))

func append_output(text: String) -> void:
	"""Append text to output"""
	output_text.text += text + "\n"

	# Auto-scroll to bottom
	await get_tree().process_frame
	output_text.scroll_vertical = int(output_text.get_line_count())

func clear_output() -> void:
	"""Clear terminal output"""
	output_text.text = ""

func navigate_history(direction: int) -> void:
	"""Navigate command history"""
	if command_history.is_empty():
		return

	history_index += direction
	history_index = clampi(history_index, 0, command_history.size())

	if history_index < command_history.size():
		input_line.text = command_history[history_index]
		input_line.caret_column = input_line.text.length()
	else:
		input_line.clear()

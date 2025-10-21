extends CharacterBody3D
class_name PlayerBot

## Player-controlled robot that can walk around the ship
## Can interact with consoles, terminals, and other ship systems

@export var move_speed: float = 5.0
@export var mouse_sensitivity: float = 0.002
@export var interact_range: float = 3.0

@onready var camera: Camera3D = $Camera3D
@onready var interaction_raycast: RayCast3D = $Camera3D/InteractionRay

var is_in_terminal_mode: bool = false
var current_interactable: Node = null

signal terminal_mode_changed(enabled: bool)
signal interacted_with(object: Node)

func _ready() -> void:
	# Capture mouse for FPS controls
	if not is_in_terminal_mode:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _physics_process(delta: float) -> void:
	# Don't process movement if in terminal mode
	if is_in_terminal_mode:
		return

	# Handle movement
	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	if direction:
		velocity.x = direction.x * move_speed
		velocity.z = direction.z * move_speed
	else:
		velocity.x = move_toward(velocity.x, 0, move_speed)
		velocity.z = move_toward(velocity.z, 0, move_speed)

	# Apply gravity
	if not is_on_floor():
		velocity.y -= 9.8 * delta

	move_and_slide()

	# Check for interactable objects
	check_interaction()

func _unhandled_input(event: InputEvent) -> void:
	# Mouse look (only when not in terminal mode)
	if event is InputEventMouseMotion and not is_in_terminal_mode:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotate_x(-event.relative.y * mouse_sensitivity)
		camera.rotation.x = clamp(camera.rotation.x, -PI/2, PI/2)

	# Interaction key
	if event.is_action_pressed("interact") and not is_in_terminal_mode:
		try_interact()

	# Exit terminal mode
	if event.is_action_pressed("ui_cancel") and is_in_terminal_mode:
		exit_terminal_mode()

func check_interaction() -> void:
	"""Check if player is looking at an interactable object"""
	if interaction_raycast.is_colliding():
		var collider = interaction_raycast.get_collider()
		if collider and collider.has_method("can_interact"):
			current_interactable = collider
		else:
			current_interactable = null
	else:
		current_interactable = null

func try_interact() -> void:
	"""Try to interact with the current interactable object"""
	if current_interactable and current_interactable.has_method("interact"):
		current_interactable.interact(self)
		interacted_with.emit(current_interactable)

func enter_terminal_mode() -> void:
	"""Enter terminal mode (fullscreen UI)"""
	is_in_terminal_mode = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	terminal_mode_changed.emit(true)

func exit_terminal_mode() -> void:
	"""Exit terminal mode (back to 3D view)"""
	is_in_terminal_mode = false
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	terminal_mode_changed.emit(false)

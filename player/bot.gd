extends CharacterBody3D
class_name Bot

## Generic bot that can navigate to rooms and perform tasks
## Can be controlled via ShipOS commands

@export var bot_id: int = 0
@export var bot_name: String = "Bot"
@export var move_speed: float = 3.0
@export var arrival_threshold: float = 0.5

var target_room: RoomSystem.RoomInstance = null
var current_room: RoomSystem.RoomInstance = null
var is_moving: bool = false
var bot_color: Color = Color.WHITE

signal arrived_at_room(room: RoomSystem.RoomInstance)
signal movement_started(room: RoomSystem.RoomInstance)

# Simple 3D representation
var mesh_instance: MeshInstance3D
var collision_shape: CollisionShape3D

func _ready() -> void:
	# Create visual representation
	_create_bot_mesh()

func _create_bot_mesh() -> void:
	"""Create a simple capsule mesh for the bot"""
	# Mesh
	mesh_instance = MeshInstance3D.new()
	var capsule = CapsuleMesh.new()
	capsule.radius = 0.3
	capsule.height = 1.6
	mesh_instance.mesh = capsule

	# Material
	var material = StandardMaterial3D.new()
	material.albedo_color = bot_color
	material.emission_enabled = true
	material.emission = bot_color * 0.3
	mesh_instance.material_override = material

	add_child(mesh_instance)
	mesh_instance.position = Vector3(0, 0.8, 0)

	# Collision
	collision_shape = CollisionShape3D.new()
	var shape = CapsuleShape3D.new()
	shape.radius = 0.3
	shape.height = 1.6
	collision_shape.shape = shape
	collision_shape.position = Vector3(0, 0.8, 0)
	add_child(collision_shape)

func _physics_process(delta: float) -> void:
	"""Handle bot movement"""
	if not is_moving or not target_room:
		return

	# Move toward target room center
	var target_pos = target_room.world_position + Vector3(2.0, 0, 2.0)
	var direction = (target_pos - global_position).normalized()

	# Check if arrived
	if global_position.distance_to(target_pos) < arrival_threshold:
		_arrive_at_room()
		return

	# Move toward target
	velocity.x = direction.x * move_speed
	velocity.z = direction.z * move_speed

	# Apply gravity
	if not is_on_floor():
		velocity.y -= 9.8 * delta

	move_and_slide()

func move_to_room(room: RoomSystem.RoomInstance) -> void:
	"""Command bot to move to a specific room"""
	if not room:
		return

	target_room = room
	is_moving = true
	movement_started.emit(room)

func stop_moving() -> void:
	"""Stop bot movement"""
	is_moving = false
	velocity = Vector3.ZERO

func _arrive_at_room() -> void:
	"""Bot has arrived at target room"""
	is_moving = false
	velocity = Vector3.ZERO
	current_room = target_room
	target_room = null
	arrived_at_room.emit(current_room)

func get_status() -> String:
	"""Get bot status string"""
	var status = "%s (ID: %d)" % [bot_name, bot_id]
	if is_moving and target_room:
		status += " - Moving to %s" % target_room.get_name()
	elif current_room:
		status += " - In %s" % current_room.get_name()
	else:
		status += " - Location unknown"
	return status

func set_current_room(room: RoomSystem.RoomInstance) -> void:
	"""Manually set the bot's current room (for initialization)"""
	current_room = room

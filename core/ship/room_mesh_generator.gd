extends Node3D
class_name RoomMeshGenerator

## Generates 3D meshes for ship rooms and corridors

const ROOM_CELL_SIZE: float = 4.0  # Size of one grid cell in meters
const ROOM_HEIGHT: float = 3.0     # Height of rooms
const WALL_THICKNESS: float = 0.2
const DOOR_WIDTH: float = 1.5
const DOOR_HEIGHT: float = 2.5

var ship_layout: RoomSystem.ShipLayout
var room_meshes: Dictionary = {}  # room -> Node3D

func generate_ship_mesh(layout: RoomSystem.ShipLayout) -> Node3D:
	"""Generate 3D mesh for entire ship"""
	ship_layout = layout

	var ship_root = Node3D.new()
	ship_root.name = "GeneratedShip"

	# Generate each room WITH doorway holes
	for room in layout.rooms:
		var room_node = generate_room_mesh(room)
		ship_root.add_child(room_node)
		room_meshes[room] = room_node

	# Add doorway frames (visual markers)
	for room in layout.rooms:
		add_doorway_frames(room, ship_root)

	print("[RoomMeshGenerator] Generated ship mesh with %d rooms" % layout.rooms.size())
	return ship_root

func generate_room_mesh(room: RoomSystem.RoomInstance) -> Node3D:
	"""Generate 3D mesh for a single room"""
	var room_node = Node3D.new()
	room_node.name = room.get_name().replace(" ", "_")

	# Calculate world position
	room.world_position = Vector3(
		room.grid_position.x * ROOM_CELL_SIZE,
		0,
		room.grid_position.y * ROOM_CELL_SIZE
	)
	room_node.position = room.world_position

	# Room dimensions
	var room_width = room.size.x * ROOM_CELL_SIZE
	var room_depth = room.size.y * ROOM_CELL_SIZE

	# Floor
	var floor = create_floor(room_width, room_depth)
	room_node.add_child(floor)

	# Ceiling
	var ceiling = create_ceiling(room_width, room_depth)
	room_node.add_child(ceiling)

	# Walls (with doorway holes cut out)
	var walls = create_walls_with_doorways(room, room_width, room_depth, room.get_color())
	room_node.add_child(walls)

	# Lighting
	var light = OmniLight3D.new()
	light.position = Vector3(room_width / 2, ROOM_HEIGHT - 0.5, room_depth / 2)
	light.light_energy = 0.8
	light.light_color = room.get_color().lightened(0.5)
	light.omni_range = max(room_width, room_depth)
	room_node.add_child(light)

	# Add collision for floor
	var static_body = StaticBody3D.new()
	static_body.collision_layer = 1
	static_body.collision_mask = 0

	var floor_collision = CollisionShape3D.new()
	var floor_shape = BoxShape3D.new()
	floor_shape.size = Vector3(room_width, 0.2, room_depth)
	floor_collision.shape = floor_shape
	floor_collision.position = Vector3(room_width / 2, -0.1, room_depth / 2)

	static_body.add_child(floor_collision)
	room_node.add_child(static_body)

	return room_node

func create_floor(width: float, depth: float) -> CSGBox3D:
	"""Create floor mesh"""
	var floor = CSGBox3D.new()
	floor.size = Vector3(width, 0.2, depth)
	floor.position = Vector3(width / 2, -0.1, depth / 2)

	var material = StandardMaterial3D.new()
	material.albedo_color = Color(0.3, 0.3, 0.35)
	material.metallic = 0.2
	material.roughness = 0.8
	floor.material = material

	return floor

func create_ceiling(width: float, depth: float) -> CSGBox3D:
	"""Create ceiling mesh"""
	var ceiling = CSGBox3D.new()
	ceiling.size = Vector3(width, 0.2, depth)
	ceiling.position = Vector3(width / 2, ROOM_HEIGHT + 0.1, depth / 2)

	var material = StandardMaterial3D.new()
	material.albedo_color = Color(0.25, 0.25, 0.3)
	ceiling.material = material

	return ceiling

func create_walls_with_doorways(room: RoomSystem.RoomInstance, width: float, depth: float, color: Color) -> Node3D:
	"""Create walls for room with doorway holes cut out"""
	var walls_node = Node3D.new()
	walls_node.name = "Walls"

	var material = StandardMaterial3D.new()
	material.albedo_color = color.darkened(0.3)
	material.metallic = 0.3
	material.roughness = 0.7

	# Check which walls need doorways
	var has_door_north = false
	var has_door_south = false
	var has_door_west = false
	var has_door_east = false

	for doorway in room.doorways:
		var dir: Vector2i = doorway["direction"]
		if dir.y < 0:  # North
			has_door_north = true
		elif dir.y > 0:  # South
			has_door_south = true
		elif dir.x < 0:  # West
			has_door_west = true
		elif dir.x > 0:  # East
			has_door_east = true

	# North wall (Z-)
	if has_door_north:
		var north_wall = create_wall_with_door(width, WALL_THICKNESS, true, material)
		north_wall.position = Vector3(width / 2, ROOM_HEIGHT / 2, -WALL_THICKNESS / 2)
		walls_node.add_child(north_wall)
	else:
		var north = CSGBox3D.new()
		north.size = Vector3(width, ROOM_HEIGHT, WALL_THICKNESS)
		north.position = Vector3(width / 2, ROOM_HEIGHT / 2, -WALL_THICKNESS / 2)
		north.material = material
		walls_node.add_child(north)

	# South wall (Z+)
	if has_door_south:
		var south_wall = create_wall_with_door(width, WALL_THICKNESS, true, material)
		south_wall.position = Vector3(width / 2, ROOM_HEIGHT / 2, depth + WALL_THICKNESS / 2)
		walls_node.add_child(south_wall)
	else:
		var south = CSGBox3D.new()
		south.size = Vector3(width, ROOM_HEIGHT, WALL_THICKNESS)
		south.position = Vector3(width / 2, ROOM_HEIGHT / 2, depth + WALL_THICKNESS / 2)
		south.material = material
		walls_node.add_child(south)

	# West wall (X-)
	if has_door_west:
		var west_wall = create_wall_with_door(depth, WALL_THICKNESS, false, material)
		west_wall.position = Vector3(-WALL_THICKNESS / 2, ROOM_HEIGHT / 2, depth / 2)
		walls_node.add_child(west_wall)
	else:
		var west = CSGBox3D.new()
		west.size = Vector3(WALL_THICKNESS, ROOM_HEIGHT, depth)
		west.position = Vector3(-WALL_THICKNESS / 2, ROOM_HEIGHT / 2, depth / 2)
		west.material = material
		walls_node.add_child(west)

	# East wall (X+)
	if has_door_east:
		var east_wall = create_wall_with_door(depth, WALL_THICKNESS, false, material)
		east_wall.position = Vector3(width + WALL_THICKNESS / 2, ROOM_HEIGHT / 2, depth / 2)
		walls_node.add_child(east_wall)
	else:
		var east = CSGBox3D.new()
		east.size = Vector3(WALL_THICKNESS, ROOM_HEIGHT, depth)
		east.position = Vector3(width + WALL_THICKNESS / 2, ROOM_HEIGHT / 2, depth / 2)
		east.material = material
		walls_node.add_child(east)

	return walls_node

func create_wall_with_door(length: float, thickness: float, horizontal: bool, wall_material: Material) -> CSGCombiner3D:
	"""Create a wall with a doorway hole cut in the center"""
	var combiner = CSGCombiner3D.new()

	# Main wall
	var wall = CSGBox3D.new()
	if horizontal:
		wall.size = Vector3(length, ROOM_HEIGHT, thickness)
	else:
		wall.size = Vector3(thickness, ROOM_HEIGHT, length)

	# Apply material to the wall
	wall.material = wall_material

	# Door hole (subtract from wall)
	var door_hole = CSGBox3D.new()
	door_hole.operation = CSGShape3D.OPERATION_SUBTRACTION
	door_hole.size = Vector3(DOOR_WIDTH, DOOR_HEIGHT, thickness * 2)
	door_hole.position = Vector3(0, -((ROOM_HEIGHT - DOOR_HEIGHT) / 2), 0)

	combiner.add_child(wall)
	combiner.add_child(door_hole)

	return combiner

func add_doorway_frames(room: RoomSystem.RoomInstance, ship_root: Node3D):
	"""Add decorative frames around doorways"""
	for doorway_data in room.doorways:
		var direction: Vector2i = doorway_data["direction"]
		var frame = create_doorway_frame(room, direction)
		if frame:
			ship_root.add_child(frame)

func create_doorway_frame(room: RoomSystem.RoomInstance, direction: Vector2i) -> Node3D:
	"""Create a simple doorway frame for visual reference"""
	var frame_node = Node3D.new()
	frame_node.name = "DoorFrame_%s" % room.get_name()

	# Calculate doorway position
	var room_width = room.size.x * ROOM_CELL_SIZE
	var room_depth = room.size.y * ROOM_CELL_SIZE

	var door_pos = room.world_position + Vector3(room_width / 2, DOOR_HEIGHT / 2, room_depth / 2)

	if direction.x > 0:  # East
		door_pos.x += room_width / 2
	elif direction.x < 0:  # West
		door_pos.x -= room_width / 2
	elif direction.y > 0:  # South
		door_pos.z += room_depth / 2
	elif direction.y < 0:  # North
		door_pos.z -= room_depth / 2

	frame_node.position = door_pos

	# Simple visual indicator (small light)
	var light = OmniLight3D.new()
	light.light_energy = 0.5
	light.light_color = Color(0.8, 1.0, 0.8)
	light.omni_range = 2.0
	frame_node.add_child(light)

	return frame_node

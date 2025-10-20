## ShipSystem - Base class for ship systems
class_name ShipSystem extends RefCounted

var system_name: String = ""
var system_type: Room.SystemType = Room.SystemType.NONE
var level: int = 1
var room: Room = null

func _init(p_name: String, p_type: Room.SystemType) -> void:
	system_name = p_name
	system_type = p_type

func update(delta: float) -> void:
	pass

func is_online() -> bool:
	if not room:
		return false
	return room.is_functional()

func get_effectiveness() -> float:
	if not is_online():
		return 0.0

	var health_factor: float = room.health
	var power_ratio: float = float(room.power_allocated) / float(room.max_power)

	# Base effectiveness without crew: 25%
	if room.crew_in_room.is_empty():
		return health_factor * power_ratio * 0.25

	# With crew: 100% + skill bonuses
	return health_factor * power_ratio * 1.0

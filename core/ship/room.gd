## Room - A room in the ship with a system
class_name Room extends RefCounted

enum SystemType {
	NONE,
	HELM,
	SHIELDS,
	WEAPONS,
	ENGINES,
	REACTOR,
	REPAIR_BAY,
	SENSORS,
	DOORS,
	TELEPORTER,
	CLOAKING
}

var room_name: String = ""
var system_type: SystemType = SystemType.NONE

# Position in ship grid
var x: int = 0
var y: int = 0
var width: int = 1
var height: int = 1

# System state
var power_allocated: int = 0
var max_power: int = 3
var health: float = 1.0  # 0.0 to 1.0

# Room conditions
var on_fire: bool = false
var breached: bool = false
var venting: bool = false

# Crew in room
var crew_in_room: Array[Crew] = []

# Connected rooms
var connections: Array[Room] = []

func _init(p_name: String, p_type: SystemType, p_x: int, p_y: int) -> void:
	room_name = p_name
	system_type = p_type
	x = p_x
	y = p_y

func is_functional() -> bool:
	if health <= 0.2:
		return false
	if breached:
		return false
	if power_allocated <= 0:
		return false
	return true

func take_damage(amount: float) -> void:
	health = max(0.0, health - amount)

func repair(amount: float) -> void:
	health = min(1.0, health + amount)

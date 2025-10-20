## Crew - Crew member with skills and AI
class_name Crew extends RefCounted

var crew_name: String = ""
var race: String = "human"

var health: float = 100.0
var health_max: float = 100.0

var current_room: Room = null

# Skills (0-5 levels)
var skill_helm: int = 0
var skill_weapons: int = 0
var skill_shields: int = 0
var skill_engines: int = 0
var skill_repair: int = 0

func _init(p_name: String) -> void:
	crew_name = p_name

func is_alive() -> bool:
	return health > 0

func take_damage(amount: float) -> void:
	health = max(0, health - amount)

func assign_to_room(room: Room) -> void:
	if current_room and current_room.crew_in_room.has(self):
		current_room.crew_in_room.erase(self)
	current_room = room
	if room:
		room.crew_in_room.append(self)

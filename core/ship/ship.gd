## Ship - Main spaceship class
## Manages hull, shields, power, rooms, crew, weapons
class_name Ship extends RefCounted

var ship_name: String = ""
var ship_class: String = ""

# Resources
var hull: float = 30.0
var hull_max: float = 30.0
var shields: float = 0.0
var shields_max: int = 0
var dark_matter: int = 20  # FTL fuel
var missiles: int = 8
var scrap: int = 0

# Power
var reactor_power: int = 8
var power_available: int = 8

# Ship structure
var rooms: Dictionary = {}  # String -> Room
var systems: Dictionary = {}  # SystemType -> ShipSystem
var crew: Array[Crew] = []
var weapons: Array[Weapon] = []

# Galaxy position
var galaxy_position: float = 800.0
var velocity: float = 0.0
var is_traveling: bool = false
var target_position: float = 0.0

func _init(p_name: String, p_class: String) -> void:
	ship_name = p_name
	ship_class = p_class

func update(delta: float) -> void:
	# Update ship state
	_update_position(delta)
	_update_systems(delta)
	_update_weapons(delta)
	_update_crew_ai(delta)
	_update_shields(delta)

func _update_position(delta: float) -> void:
	pass  # TODO

func _update_systems(delta: float) -> void:
	pass  # TODO

func _update_weapons(delta: float) -> void:
	pass  # TODO

func _update_crew_ai(delta: float) -> void:
	pass  # TODO

func _update_shields(delta: float) -> void:
	pass  # TODO

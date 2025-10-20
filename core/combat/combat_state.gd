## CombatState - Manages combat between two ships
class_name CombatState extends RefCounted

var player_ship: Ship
var enemy_ship: Ship
var active: bool = true
var turn: int = 0

var player_target: String = ""  # Room name
var combat_distance: float = 5.0

var combat_log: Array[String] = []

func _init(p_player: Ship, p_enemy: Ship) -> void:
	player_ship = p_player
	enemy_ship = p_enemy

func update(delta: float) -> void:
	player_ship.update(delta)
	enemy_ship.update(delta)
	_enemy_ai(delta)

func _enemy_ai(delta: float) -> void:
	# TODO: Enemy AI
	pass

func fire_player_weapon(weapon_index: int) -> bool:
	# TODO
	return false

## Weapon - Ship weapon system
class_name Weapon extends RefCounted

var weapon_name: String = ""
var damage: int = 1
var shots: int = 1
var cooldown_time: float = 3.0
var charge: float = 1.0  # 0.0 to 1.0
var pierce: int = 0  # Shield pierce
var weapon_range: float = 5.0

var requires_missiles: bool = false

func _init(p_name: String) -> void:
	weapon_name = p_name

func update(delta: float, powered: bool) -> void:
	if not is_ready() and powered:
		charge += delta / cooldown_time
		charge = min(1.0, charge)

func is_ready() -> bool:
	return charge >= 1.0

func fire() -> bool:
	if not is_ready():
		return false
	charge = 0.0
	return true

extends RefCounted
class_name Projectile

## Represents a fired weapon projectile traveling through space
## Tracks position, velocity, damage, and handles collision detection

var position: Vector3
var velocity: Vector3
var damage: float
var owner_ship: Ship  # Ship that fired this projectile
var target_ship: Ship  # Intended target (may miss)
var weapon_name: String
var lifetime: float = 0.0
var max_lifetime: float = 10.0  # Despawn after 10 seconds

func _init(
	start_pos: Vector3,
	target_pos: Vector3,
	projectile_damage: float,
	owner: Ship,
	target: Ship,
	weapon: String,
	speed: float = 300.0
):
	position = start_pos
	damage = projectile_damage
	owner_ship = owner
	target_ship = target
	weapon_name = weapon

	# Calculate velocity toward target
	var direction = (target_pos - start_pos).normalized()
	velocity = direction * speed

func update(delta: float) -> bool:
	"""Update projectile position. Returns false if projectile should be removed."""
	lifetime += delta

	# Remove if too old
	if lifetime > max_lifetime:
		return false

	# Move projectile
	position += velocity * delta

	return true

func check_hit(ship: Ship, hit_radius: float = 50.0) -> bool:
	"""Check if projectile hit the given ship."""
	if ship == owner_ship:
		return false  # Can't hit yourself

	var distance = position.distance_to(ship.position)
	return distance < hit_radius

func get_info() -> String:
	"""Debug info about this projectile."""
	return "%s projectile from %s → %s (%.1f damage, pos: %s)" % [
		weapon_name,
		owner_ship.name if owner_ship else "unknown",
		target_ship.name if target_ship else "unknown",
		damage,
		position
	]

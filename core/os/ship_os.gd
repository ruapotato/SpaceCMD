## ShipOS - Ship Operating System
## Integrates Ship with Unix-like OS and VFS
class_name ShipOS extends RefCounted

var ship: Ship
var vfs: VFS
var hostname: String = ""

func _init(p_ship: Ship, p_hostname: String = "") -> void:
	ship = p_ship
	hostname = p_hostname if p_hostname else p_ship.ship_name.to_lower()
	vfs = VFS.new()
	_mount_ship_systems()

func _mount_ship_systems() -> void:
	# Create /dev/ship, /proc/ship, /sys/ship
	print("ShipOS: Mounting ship systems...")
	# TODO

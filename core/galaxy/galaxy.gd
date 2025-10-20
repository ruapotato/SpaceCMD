## Galaxy - Manages the 1D galaxy map with POIs and encounters
## 1D linear galaxy (distance from origin)
class_name Galaxy extends RefCounted

## Point of Interest types
enum POIType {
	EMPTY,          # Empty space
	STORE,          # Shop to buy upgrades
	ENCOUNTER,      # Enemy ship
	NEBULA,         # Hazard zone
	ASTEROID,       # Mining opportunity
	DISTRESS,       # Rescue mission
	BOSS            # Boss fight
}

## Point of Interest data
class POI extends RefCounted:
	var position: float = 0.0
	var type: POIType = POIType.EMPTY
	var data: Dictionary = {}
	var visited: bool = false
	var difficulty: int = 1

	func _init(p_position: float, p_type: POIType, p_difficulty: int = 1) -> void:
		position = p_position
		type = p_type
		difficulty = p_difficulty

## Galaxy configuration
var galaxy_size: float = 10000.0  # Total distance to traverse
var current_sector: int = 1
var max_sectors: int = 8

## All points of interest
var pois: Array[POI] = []

## Player's current position
var player_position: float = 0.0

func _init() -> void:
	_generate_galaxy()

## Generate the galaxy with POIs
func _generate_galaxy() -> void:
	# TODO: Implement galaxy generation
	# Will create POIs at various positions
	# Difficulty scales with distance from origin
	pass

## Get POIs near a position
func get_nearby_pois(position: float, radius: float) -> Array[POI]:
	var nearby: Array[POI] = []
	for poi in pois:
		if abs(poi.position - position) <= radius:
			nearby.append(poi)
	return nearby

## Get next POI in travel direction
func get_next_poi(from_position: float) -> POI:
	var closest_poi: POI = null
	var closest_distance: float = INF

	for poi in pois:
		if poi.position > from_position:
			var distance = poi.position - from_position
			if distance < closest_distance:
				closest_distance = distance
				closest_poi = poi

	return closest_poi

## Calculate difficulty at position
func get_difficulty_at_position(position: float) -> int:
	var progress = position / galaxy_size
	return int(1 + progress * 7)  # Scales 1-8

## Update galaxy state
func update(delta: float) -> void:
	# TODO: Update any dynamic POIs
	pass

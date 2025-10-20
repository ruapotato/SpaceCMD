## GameManager - Global game state singleton
## Autoloaded at startup, accessible everywhere as GameManager
extends Node

## Current player ship
var player_ship: Ship = null

## Current combat state
var combat_state: CombatState = null

## Galaxy manager
var galaxy: Galaxy = null

## Global game state
enum GameState {
	MAIN_MENU,
	IN_FLIGHT,      # Flying through space
	IN_COMBAT,      # Active combat
	DOCKED,         # At station
	PAUSED
}

var current_state: GameState = GameState.MAIN_MENU

## Signals
signal combat_started(enemy_ship: Ship)
signal combat_ended(victory: bool)
signal ship_destroyed(ship: Ship)
signal game_over()

func _ready() -> void:
	print("GameManager initialized")

## Start new game
func new_game() -> void:
	print("Starting new game...")
	# Will create player ship, galaxy, etc.
	current_state = GameState.IN_FLIGHT

## Enter combat
func start_combat(enemy: Ship) -> void:
	if not player_ship:
		push_error("Cannot start combat: no player ship")
		return

	print("Combat started with ", enemy.name)
	current_state = GameState.IN_COMBAT
	combat_started.emit(enemy)

## End combat
func end_combat(victory: bool) -> void:
	print("Combat ended. Victory: ", victory)
	current_state = GameState.IN_FLIGHT
	combat_ended.emit(victory)

## Game loop update
func _process(delta: float) -> void:
	match current_state:
		GameState.IN_FLIGHT:
			_update_flight(delta)
		GameState.IN_COMBAT:
			_update_combat(delta)

func _update_flight(delta: float) -> void:
	if player_ship:
		player_ship.update(delta)

func _update_combat(delta: float) -> void:
	if combat_state:
		combat_state.update(delta)

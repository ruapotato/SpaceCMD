#!/usr/bin/env python3
"""
Test console mode with combat
"""

import time
from core.ships import create_ship
from core.game import Game

def test_console_mode():
    """Test console mode with simulated combat"""
    print("Testing Console Mode with Combat\n")

    # Create ship
    ship = create_ship("kestrel")

    # Create game in console mode with WorldManager
    game = Game(ship, use_terminal_ui=False, enable_world=True)

    # Give it a moment to start
    time.sleep(0.5)

    # Trigger an encounter manually
    if game.world_manager:
        print("Triggering test encounter...\n")
        game.world_manager.trigger_encounter("gnat", forced=True)

        # Wait for combat to start (background thread needs to process)
        time.sleep(1.0)

        # Move player closer to engage combat
        if game.world_manager.combat_state and game.world_manager.enemy_ship:
            # Force combat to be active by setting player position close to enemy
            enemy_pos = game.world_manager.enemy_ship.ship.galaxy_position
            game.ship.galaxy_position = enemy_pos - 3.0  # Move within engagement range
            game.world_manager.combat_state.player_galaxy_position = game.ship.galaxy_position
            print(f"Moving player to engage (enemy at {enemy_pos:.1f}, player at {game.ship.galaxy_position:.1f})\n")
            time.sleep(0.5)

    # Render a few times to show combat
    for i in range(5):
        game.render()
        print(f"\n[Frame {i+1}] - In combat: {game.in_combat}")
        if game.enemy_ship:
            print(f"  Enemy: {game.enemy_ship.name} - {game.enemy_ship.hull}/{game.enemy_ship.hull_max} hull")
            if game.world_manager.combat_state:
                print(f"  Combat active: {game.world_manager.combat_state.active}")
                print(f"  Galaxy distance: {abs(game.ship.galaxy_position - game.enemy_ship.galaxy_position):.1f}")
        print()
        time.sleep(0.8)

    # Show status
    game.log("=== STATUS TEST ===")
    exit_code, stdout, stderr = game.ship_os.execute_command("status")
    for line in stdout.split('\n'):
        game.log(line)

    # One more render to show the log
    game.render()

    print("\n✓ Console mode test complete!\n")
    game.running = False

if __name__ == '__main__':
    test_console_mode()

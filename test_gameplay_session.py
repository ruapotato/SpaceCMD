#!/usr/bin/env python3
"""
Test a full gameplay session in console mode
Simulates player actions to test the game loop
"""

import time
from core.ships import create_ship
from core.game import Game

def simulate_gameplay():
    """Simulate a full gameplay session"""
    print("=" * 80)
    print("SPACECMD - HACKERS MEET FTL GAMEPLAY TEST")
    print("=" * 80)
    print()

    # Create ship
    ship = create_ship("kestrel")

    # Create game in console mode with WorldManager
    game = Game(ship, use_terminal_ui=False, enable_world=True)
    time.sleep(0.5)

    # Initial status
    print("\n🚀 MISSION START")
    game.render()
    time.sleep(1)

    # Check systems
    print("\n📊 Checking ship systems...")
    exit_code, stdout, stderr = game.ship_os.execute_command("systems")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(1)

    # Check crew
    print("\n👥 Checking crew roster...")
    exit_code, stdout, stderr = game.ship_os.execute_command("crew")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(1)

    # Trigger combat encounter
    print("\n⚠️  TRIGGERING COMBAT ENCOUNTER...")
    if game.world_manager:
        game.world_manager.trigger_encounter("gnat", forced=True)
        time.sleep(1.5)

        # Move into engagement range
        if game.world_manager.combat_state and game.world_manager.enemy_ship:
            enemy_pos = game.world_manager.enemy_ship.ship.galaxy_position
            game.ship.galaxy_position = enemy_pos - 3.0
            game.world_manager.combat_state.player_galaxy_position = game.ship.galaxy_position
            print(f"   Engaging enemy at {enemy_pos:.1f}u (player at {game.ship.galaxy_position:.1f}u)")
            time.sleep(0.5)

    # Combat loop
    print("\n⚔️  ENTERING COMBAT...")
    for turn in range(5):
        game.render()
        print(f"\n--- Combat Turn {turn + 1} ---")

        if not game.in_combat:
            print("Combat ended!")
            break

        if game.enemy_ship and game.enemy_ship.hull <= 0:
            print("✓ Enemy destroyed!")
            break

        # Check enemy
        if turn == 0:
            exit_code, stdout, stderr = game.ship_os.execute_command("enemy")
            for line in stdout.split('\n')[:10]:  # First 10 lines
                game.log(line)

        # Target shields on first turn
        if turn == 0:
            exit_code, stdout, stderr = game.ship_os.execute_command("target shields")
            for line in stdout.split('\n'):
                game.log(line)

        # Fire weapon
        if turn % 2 == 0:  # Fire every other turn
            exit_code, stdout, stderr = game.ship_os.execute_command("fire 1")
            for line in stdout.split('\n'):
                game.log(line)

        time.sleep(1.5)

    # Final status
    print("\n📊 POST-COMBAT STATUS")
    game.render()
    time.sleep(1)

    # Show combat results
    exit_code, stdout, stderr = game.ship_os.execute_command("status")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()

    print("\n" + "=" * 80)
    print("GAMEPLAY TEST COMPLETE")
    print("=" * 80)
    print(f"\nFinal Hull: {ship.hull}/{ship.hull_max}")
    print(f"Final Shields: {int(ship.shields)}/{ship.shields_max}")
    if game.enemy_ship:
        print(f"Enemy Hull: {game.enemy_ship.hull}/{game.enemy_ship.hull_max}")
    print()

    game.running = False

if __name__ == '__main__':
    simulate_gameplay()

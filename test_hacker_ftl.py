#!/usr/bin/env python3
"""
Test HACKERS + FTL Gameplay
Demonstrates the full network combat experience
"""

import time
from core.ships import create_ship
from core.game import Game

def test_hacker_gameplay():
    """Test the full hackers meets FTL experience"""
    print("╔" + "═" * 78 + "╗")
    print("║" + " SPACECMD - HACKERS MEET FTL ".center(78) + "║")
    print("║" + " Network Combat Demonstration ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Create ship
    ship = create_ship("kestrel")
    game = Game(ship, use_terminal_ui=False, enable_world=True)
    time.sleep(0.5)

    # Show intro
    print("\n🚀 MISSION BRIEFING")
    print("=" * 78)
    print("You are a hacker-captain commanding the Nautilus.")
    print("Your ship is equipped with:")
    print("  • Advanced weapons systems")
    print("  • Network intrusion tools")
    print("  • Malware deployment suite")
    print("  • Exploit framework")
    print()
    print("In combat, you can:")
    print("  1. Fire weapons (traditional FTL combat)")
    print("  2. Scan enemy networks for vulnerabilities")
    print("  3. Hack enemy systems to disable them")
    print("  4. Deploy malware for persistent damage")
    print("  5. Combine both for maximum effectiveness!")
    print("=" * 78)
    time.sleep(2)

    # Trigger encounter
    print("\n⚠️  ENCOUNTER: HOSTILE SHIP DETECTED")
    if game.world_manager:
        game.world_manager.trigger_encounter("gnat", forced=True)
        time.sleep(1.5)

        # Engage
        if game.world_manager.combat_state and game.world_manager.enemy_ship:
            enemy_pos = game.world_manager.enemy_ship.ship.galaxy_position
            game.ship.galaxy_position = enemy_pos - 3.0
            game.world_manager.combat_state.player_galaxy_position = game.ship.galaxy_position
            print(f"   Enemy at {enemy_pos:.1f}u - Moving to engage...")
            time.sleep(0.5)

    game.render()
    time.sleep(1)

    # TURN 1: Network Scan
    print("\n" + "=" * 78)
    print("TURN 1: NETWORK RECONNAISSANCE")
    print("=" * 78)
    print("\n> scan")
    exit_code, stdout, stderr = game.ship_os.execute_command("scan")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # TURN 2: Deploy hack
    print("\n" + "=" * 78)
    print("TURN 2: EXPLOIT DEPLOYMENT")
    print("=" * 78)
    print("\n> hack buffer_overflow weapons")
    exit_code, stdout, stderr = game.ship_os.execute_command("hack buffer_overflow weapons")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # TURN 3: Deploy malware
    print("\n" + "=" * 78)
    print("TURN 3: MALWARE DEPLOYMENT")
    print("=" * 78)
    print("\n> malware worm shields")
    exit_code, stdout, stderr = game.ship_os.execute_command("malware worm shields")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # TURN 4: Check hack status
    print("\n" + "=" * 78)
    print("TURN 4: NETWORK STATUS CHECK")
    print("=" * 78)
    print("\n> hacks")
    exit_code, stdout, stderr = game.ship_os.execute_command("hacks")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # TURN 5: Fire weapons
    print("\n" + "=" * 78)
    print("TURN 5: KINETIC STRIKE (Traditional FTL Combat)")
    print("=" * 78)
    print("\n> fire 1")
    exit_code, stdout, stderr = game.ship_os.execute_command("fire 1")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # Final status
    print("\n" + "=" * 78)
    print("COMBAT DEMONSTRATION COMPLETE")
    print("=" * 78)
    print()
    print("💻 HACKERS + FTL GAMEPLAY SUMMARY:")
    print()
    print("✓ Network Scanning    - Discover enemy vulnerabilities")
    print("✓ Exploit Deployment  - Disable enemy systems remotely")
    print("✓ Malware Attacks     - Persistent damage over time")
    print("✓ Status Monitoring   - Track all network operations")
    print("✓ Kinetic Weapons     - Traditional FTL combat")
    print()
    print("RECOMMENDED TACTICS:")
    print("1. scan → Find vulnerabilities")
    print("2. hack → Disable key systems (shields/weapons)")
    print("3. malware → Deploy persistent threats")
    print("4. fire → Finish with weapons while enemy is weakened")
    print()
    print("ADVANCED TACTICS:")
    print("• Hack enemy weapons before they fire")
    print("• Deploy logic bombs for delayed damage")
    print("• Plant backdoors for permanent access")
    print("• Combine DOS attacks with weapon fire")
    print()
    print("=" * 78)

    game.running = False

if __name__ == '__main__':
    test_hacker_gameplay()

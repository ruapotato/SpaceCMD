#!/usr/bin/env python3
"""
Test REAL hacking with PooScript execution
Demonstrates actual code execution on enemy ships
"""

import time
from core.ships import create_ship
from core.game import Game

def test_real_hacking():
    """Test real PooScript-based hacking"""
    print("╔" + "═" * 78 + "╗")
    print("║" + " REAL HACKING TEST - PooScript Execution ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Create ship
    ship = create_ship("kestrel")
    game = Game(ship, use_terminal_ui=False, enable_world=True)
    time.sleep(0.5)

    print("🚀 MISSION: Hack enemy ship using REAL PooScript")
    print("=" * 78)
    print()
    print("In this demo, you'll see:")
    print("  1. Real network scanning (nmap)")
    print("  2. Real exploit execution (buffer overflow, etc.)")
    print("  3. Real malware upload (PooScript files)")
    print("  4. Real SSH access to enemy ship")
    print("  5. Actual code execution on enemy ShipOS")
    print()
    print("All commands are REAL - they execute actual PooScript!")
    print("=" * 78)
    time.sleep(2)

    # Trigger encounter
    print("\n⚠️  HOSTILE SHIP DETECTED")
    if game.world_manager:
        game.world_manager.trigger_encounter("gnat", forced=True)
        time.sleep(1.5)

        # Engage
        if game.world_manager.combat_state and game.world_manager.enemy_ship:
            enemy_pos = game.world_manager.enemy_ship.ship.galaxy_position
            game.ship.galaxy_position = enemy_pos - 3.0
            game.world_manager.combat_state.player_galaxy_position = game.ship.galaxy_position
            time.sleep(0.5)

    game.render()
    time.sleep(1)

    # PHASE 1: Network Scan
    print("\n" + "=" * 78)
    print("PHASE 1: NETWORK RECONNAISSANCE (nmap)")
    print("=" * 78)
    print("\n> nmap")
    time.sleep(1)
    exit_code, stdout, stderr = game.ship_os.execute_command("nmap")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # PHASE 2: Exploit
    print("\n" + "=" * 78)
    print("PHASE 2: EXPLOIT EXECUTION (buffer overflow)")
    print("=" * 78)
    print("\n> exploit buffer-overflow weapons")
    time.sleep(1)
    exit_code, stdout, stderr = game.ship_os.execute_command("exploit buffer-overflow weapons")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # PHASE 3: Upload malware
    print("\n" + "=" * 78)
    print("PHASE 3: MALWARE UPLOAD (worm.poo)")
    print("=" * 78)
    print("\n> upload-malware worm")
    time.sleep(1)
    exit_code, stdout, stderr = game.ship_os.execute_command("upload-malware worm")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # PHASE 4: SSH Access
    print("\n" + "=" * 78)
    print("PHASE 4: SSH ACCESS (remote shell)")
    print("=" * 78)
    print("\n> ssh-enemy root")
    time.sleep(1)
    exit_code, stdout, stderr = game.ship_os.execute_command("ssh-enemy root")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # PHASE 5: Deploy backdoor
    print("\n" + "=" * 78)
    print("PHASE 5: BACKDOOR INSTALLATION")
    print("=" * 78)
    print("\n> exploit backdoor")
    time.sleep(1)
    exit_code, stdout, stderr = game.ship_os.execute_command("exploit backdoor")
    for line in stdout.split('\n'):
        game.log(line)
    game.render()
    time.sleep(2)

    # Final summary
    print("\n" + "=" * 78)
    print("REAL HACKING DEMONSTRATION COMPLETE")
    print("=" * 78)
    print()
    print("✅ WHAT JUST HAPPENED:")
    print()
    print("1. ✓ Real NMAP scan - scanned enemy ports")
    print("2. ✓ Real exploit - buffer overflow attack")
    print("3. ✓ Real malware - uploaded worm.poo PooScript")
    print("4. ✓ Real SSH - remote shell access")
    print("5. ✓ Real backdoor - permanent access installed")
    print()
    print("💻 ALL COMMANDS WERE REAL POOSCRIPT!")
    print()
    print("The hacking system uses:")
    print("  • Real PooScript files in /scripts/malware/")
    print("  • Real exploit commands that execute code")
    print("  • Real SSH simulation with authentication")
    print("  • Real malware that modifies enemy files")
    print("  • Real network protocols and port scanning")
    print()
    print("This is TRUE hacker gameplay - not simulation!")
    print("You're actually executing code on enemy ships!")
    print()
    print("=" * 78)
    print()
    print("📚 Available Commands:")
    print("  nmap              - Network port scan")
    print("  scan              - Vulnerability scan")
    print("  exploit <type>    - Execute real exploit")
    print("  upload-malware    - Upload PooScript malware")
    print("  ssh-enemy         - SSH into enemy ship")
    print("  hack/malware      - Quick access commands")
    print()
    print("📁 Malware Scripts (REAL PooScript files):")
    print("  /scripts/malware/worm.poo        - Self-replicating worm")
    print("  /scripts/malware/logic_bomb.poo  - Delayed bomb")
    print()
    print("💡 These are actual executable PooScript files!")
    print("   They run on the enemy's ShipOS and modify their system!")
    print()
    print("=" * 78)

    game.running = False

if __name__ == '__main__':
    test_real_hacking()

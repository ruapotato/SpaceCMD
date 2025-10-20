#!/usr/bin/env python3
"""
spacecmd - Roguelike Game Mode

Complete roguelike spaceship game with tutorial, combat, and ASCII visuals.
Navigate through hostile sectors, fight enemies, and reach your destination!
"""

import sys
import time
import random
from core.ships import create_ship, SHIP_TEMPLATES
from core.enemy_ships import create_random_enemy
from core.combat import CombatState
from core.render import Icons, Color


def safe_input(prompt: str = "") -> str:
    """Input with EOFError handling"""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return ""


def print_slow(text: str, delay: float = 0.001):
    """Print text with typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def clear_screen():
    """Clear terminal"""
    import os
    os.system('clear' if os.name != 'nt' else 'cls')


def print_combat_display(combat: CombatState):
    """
    Display visual combat scene with ASCII art.
    """
    player = combat.player_ship
    enemy = combat.enemy_ship

    print("\n" + "=" * 80)
    print(f"  COMBAT - Turn {combat.turn}".center(80))
    print("=" * 80)
    print()

    # Side-by-side ship display
    print(f"  YOUR SHIP: {player.name:20}        ENEMY: {enemy.name}")
    print()

    # Simple ship representations
    player_ship_art = [
        "    ┏━━━┓    ",
        "    ┃ 🎯┃    ",
        "═══ ┃🔴🔴┃ ══ ",
        "    ┃ ⚙️ ┃    ",
        "    ┗━━━┛    "
    ]

    enemy_ship_art = [
        "    ┏━━━┓    ",
        "    ┃ 💀┃    ",
        " ══ ┃⚡⚡┃ ═══",
        "    ┃ ⚙️ ┃    ",
        "    ┗━━━┛    "
    ]

    # Print ships side by side
    for p_line, e_line in zip(player_ship_art, enemy_ship_art):
        print(f"  {p_line}                    {e_line}")

    print()

    # Status bars
    p_hull_pct = player.hull / player.hull_max
    p_hull_bar = Icons.FULL_BLOCK * int(p_hull_pct * 12) + Icons.LIGHT_SHADE * (12 - int(p_hull_pct * 12))

    e_hull_pct = enemy.hull / enemy.hull_max if enemy.hull_max > 0 else 0
    e_hull_bar = Icons.FULL_BLOCK * int(e_hull_pct * 12) + Icons.LIGHT_SHADE * (12 - int(e_hull_pct * 12))

    p_shield_icons = Icons.SHIELDS * int(player.shields) + Icons.LIGHT_SHADE * (player.shields_max - int(player.shields))
    e_shield_icons = Icons.SHIELDS * int(enemy.shields) + Icons.LIGHT_SHADE * (enemy.shields_max - int(enemy.shields))

    print(f"  HULL:    [{p_hull_bar}] {player.hull:>2}/{player.hull_max:<2}      HULL:    [{e_hull_bar}] {enemy.hull:>2}/{enemy.hull_max:<2}")
    print(f"  SHIELDS: {p_shield_icons} {int(player.shields)}/{player.shields_max}                  SHIELDS: {e_shield_icons} {int(enemy.shields)}/{enemy.shields_max}")
    print()

    # Weapons
    print("  YOUR WEAPONS:")
    for i, weapon in enumerate(player.weapons):
        charge_bar = Icons.FULL_BLOCK * int(weapon.charge * 10) + Icons.LIGHT_SHADE * (10 - int(weapon.charge * 10))
        ready = "READY" if weapon.is_ready() else f"{int(weapon.charge * 100)}%"
        print(f"    {i+1}. {weapon.name:20} [{charge_bar}] {ready:>6}")

    print()
    print("─" * 80)

    # Combat log (last 5 messages)
    if combat.log:
        print("  COMBAT LOG:")
        for msg in combat.log[-5:]:
            print(f"    {msg}")
        print("─" * 80)


def tutorial_sequence():
    """
    Interactive tutorial that teaches the player.
    """
    clear_screen()

    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                          WELCOME TO SPACECMD                              ║
║                                                                           ║
║                    A Roguelike Spaceship Command Sim                      ║
║                          Inspired by FTL                                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    safe_input("Press Enter to begin tutorial...")
    clear_screen()

    print_slow("╔═══════════════════════════════════════════════════════════════════════════╗")
    print_slow("║                             MISSION BRIEFING                              ║")
    print_slow("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print_slow("Captain, the galaxy is in turmoil.", 0.02)
    print()
    print_slow("Your mission: Navigate through 8 hostile sectors and reach Federation HQ", 0.02)
    print_slow("with vital intelligence about the Rebel fleet.", 0.02)
    print()
    print_slow("Along the way, you'll encounter:", 0.02)
    print_slow("  • Pirates and hostile ships", 0.02)
    print_slow("  • Merchants selling upgrades", 0.02)
    print_slow("  • Distress signals and anomalies", 0.02)
    print_slow("  • The Rebel fleet (always pursuing!)", 0.02)
    print()
    print_slow("Your ship systems are managed through the COMMAND LINE.", 0.02)
    print_slow("Every system, every crew member - all accessible as files!", 0.02)
    print()

    safe_input("Press Enter to learn ship systems...")
    clear_screen()

    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                           SHIP SYSTEMS 101                                ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("Your ship has several critical systems:")
    print()
    print("  " + Icons.SHIELDS + " SHIELDS   - Absorb incoming damage")
    print("  " + Icons.WEAPONS_LASER + " WEAPONS   - Fire lasers, missiles, and more")
    print("  " + Icons.ENGINES + " ENGINES   - Dodge attacks and jump to FTL")
    print("  " + Icons.OXYGEN + " OXYGEN    - Keep your crew breathing")
    print("  " + Icons.REACTOR + " REACTOR   - Generate power for all systems")
    print("  " + Icons.MEDBAY + " MEDBAY    - Heal injured crew")
    print()
    print("Each system requires POWER from your reactor.")
    print("You must balance power between systems tactically!")
    print()

    safe_input("Press Enter to learn combat...")
    clear_screen()

    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                          COMBAT BASICS                                    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("When you encounter an enemy ship:")
    print()
    print("  1. Your WEAPONS charge up over time")
    print("  2. When charged, you can FIRE at the enemy")
    print("  3. Enemy SHIELDS absorb damage first")
    print("  4. After shields, damage hits their HULL")
    print("  5. Destroy their hull to WIN!")
    print()
    print("TARGETING: You can target specific enemy systems:")
    print("  • Target WEAPONS to stop their attacks")
    print("  • Target SHIELDS to break through defenses")
    print("  • Target ENGINES to prevent escape")
    print()
    print("Remember: The enemy shoots back! Manage your shields!")
    print()

    safe_input("Press Enter for your first mission...")


def run_combat(player_ship, difficulty=1):
    """
    Run a combat encounter.
    Returns True if player wins, False if player loses.
    """
    clear_screen()

    # Create enemy
    enemy = create_random_enemy(difficulty)

    print(f"\n⚠️  HOSTILE SHIP DETECTED: {enemy.name}!\n")
    time.sleep(1)
    print("Engaging in combat...")
    time.sleep(1)

    # Initialize combat
    combat = CombatState(player_ship, enemy)
    combat.set_target("Weapons")  # Default target

    last_update = time.time()

    while combat.active:
        # Update combat (0.5 second ticks)
        current_time = time.time()
        dt = current_time - last_update
        if dt >= 0.5:
            combat.update(0.5)
            last_update = current_time

        # Display
        clear_screen()
        print_combat_display(combat)

        # Get player input
        print("\nACTIONS:")
        print("  [1-9] Fire weapon    [t] Target system    [w] Wait")
        print("  [s] Ship status      [q] Retreat (lose)")
        print()

        try:
            import select
            if select.select([sys.stdin], [], [], 0.1)[0]:
                action = safe_input("Command> ").strip().lower()

                if action == 'q':
                    print("\nRetreating from combat...")
                    return False

                elif action == 's':
                    print(f"\nYour ship: {player_ship.hull}/{player_ship.hull_max} hull")
                    print(f"Enemy: {enemy.hull}/{enemy.hull_max} hull")
                    safe_input("\nPress Enter to continue...")

                elif action == 't':
                    print("\nTarget enemy system:")
                    print("  [w] Weapons  [s] Shields  [e] Engines")
                    target = safe_input("Target> ").strip().lower()
                    if target == 'w':
                        combat.set_target("Weapons")
                        print("Targeting enemy weapons!")
                    elif target == 's':
                        combat.set_target("Shields")
                        print("Targeting enemy shields!")
                    elif target == 'e':
                        combat.set_target("Engines")
                        print("Targeting enemy engines!")
                    time.sleep(0.5)

                elif action.isdigit():
                    weapon_idx = int(action) - 1
                    if 0 <= weapon_idx < len(player_ship.weapons):
                        if combat.fire_player_weapon(weapon_idx):
                            print(f"\nFired {player_ship.weapons[weapon_idx].name}!")
                            time.sleep(0.5)
                        else:
                            print("\nWeapon not ready!")
                            time.sleep(0.5)

        except:
            # No input available, continue
            pass

        # Check for end
        if not combat.active:
            break

    # Combat ended
    clear_screen()
    print_combat_display(combat)
    print()

    if enemy.hull <= 0:
        print("\n✓ VICTORY! Enemy ship destroyed!")
        print(f"\n  Reward: +{enemy.scrap} scrap")
        player_ship.scrap += enemy.scrap
        safe_input("\nPress Enter to continue...")
        return True
    else:
        print("\n💀 DEFEAT! Your ship has been destroyed!")
        safe_input("\nPress Enter to continue...")
        return False


def main():
    """Main game loop"""
    # Show tutorial
    tutorial_sequence()

    # Choose ship
    clear_screen()
    print("Select your ship:")
    print()
    print("  1. Kestrel (Balanced, recommended for first time)")
    print("  2. Stealth Ship (Hard mode - no shields!)")
    print("  3. Mantis Cruiser (Boarding focused)")
    print()

    choice = safe_input("Choice (1-3)> ").strip()

    ship_types = {
        '1': 'kestrel',
        '2': 'stealth',
        '3': 'mantis'
    }

    ship_type = ship_types.get(choice, 'kestrel')
    player_ship = create_ship(ship_type)

    clear_screen()
    print(f"\n✓ {player_ship.name} ready for departure!")
    print(f"  Hull: {player_ship.hull}")
    print(f"  Shields: {player_ship.shields_max} layers")
    print(f"  Crew: {len(player_ship.crew)}")
    print(f"  Weapons: {len(player_ship.weapons)}")
    print()
    safe_input("Press Enter to begin your journey...")

    # Game loop - simplified version
    sector = 1
    encounters = 0

    while sector <= 3 and player_ship.hull > 0:  # Shortened to 3 sectors for demo
        clear_screen()
        print(f"\n╔═══════════════════════════════════════════════════════════════╗")
        print(f"║  SECTOR {sector}/3                                              ║")
        print(f"║  Hull: {player_ship.hull}/{player_ship.hull_max}  Scrap: {player_ship.scrap}                                ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝")
        print()
        print("Jump to next beacon?")
        print()
        print("  [j] Jump    [r] Repair (costs scrap)    [q] Quit")
        print()

        action = safe_input("Command> ").strip().lower()

        if action == 'q':
            print("\nMission aborted.")
            break

        elif action == 'r':
            repair_cost = 10
            if player_ship.scrap >= repair_cost and player_ship.hull < player_ship.hull_max:
                player_ship.scrap -= repair_cost
                player_ship.hull = min(player_ship.hull_max, player_ship.hull + 5)
                print(f"\nRepaired 5 hull for {repair_cost} scrap")
                time.sleep(1)
            else:
                print("\nCannot repair (need 10 scrap or hull full)")
                time.sleep(1)

        elif action == 'j':
            encounters += 1

            # Random encounter
            encounter_type = random.choice(['combat', 'combat', 'nothing', 'scrap'])

            if encounter_type == 'combat':
                difficulty = 1 if sector == 1 else 2
                victory = run_combat(player_ship, difficulty)

                if not victory:
                    break  # Game over

            elif encounter_type == 'scrap':
                clear_screen()
                found = random.randint(10, 30)
                print(f"\n✓ Found debris field!")
                print(f"  +{found} scrap")
                player_ship.scrap += found
                safe_input("\nPress Enter to continue...")

            else:
                clear_screen()
                print("\n• Empty space. Nothing here.")
                safe_input("\nPress Enter to continue...")

            # Every 3 jumps, advance sector
            if encounters % 3 == 0:
                sector += 1
                if sector <= 3:
                    print(f"\n✓ Jumped to Sector {sector}!")
                    time.sleep(1)

    # Game end
    clear_screen()
    if player_ship.hull > 0 and sector > 3:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                         VICTORY!                              ║
║                                                               ║
║              You've reached Federation HQ!                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
        print(f"\nFinal Score: {player_ship.scrap} scrap")
    else:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                         GAME OVER                             ║
║                                                               ║
║                   Your ship was destroyed.                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

    print("\nThanks for playing spacecmd!")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

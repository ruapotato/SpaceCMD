#!/usr/bin/env python3
"""
spacecmd - Command-Line Spaceship Simulator

A roguelike spaceship command simulator inspired by FTL,
played entirely in the terminal with beautiful ASCII/Unicode graphics.
"""

import sys
import argparse
from core.ships import create_ship, SHIP_TEMPLATES
from core.game import Game


def print_intro():
    """Print game introduction"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                        SPACECMD v0.1                          ║
║                                                               ║
║              Command-Line Spaceship Simulator                 ║
║                   Inspired by FTL                             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

You are the captain of a spacecraft on a dangerous journey
through hostile space. Manage your ship's systems, command your
crew, and survive encounters with pirates, rebels, and the
unknown.

Every command matters. Every decision counts.

Type 'help' for available commands.
Type 'exit' to quit.

═══════════════════════════════════════════════════════════════

""")


def choose_ship():
    """Let player choose their ship"""
    print("Choose your ship:")
    print()

    ship_info = {
        "kestrel": "Balanced cruiser with shields and good crew (RECOMMENDED)",
        "stealth": "Stealth ship with cloaking, no shields (HARD MODE)",
        "mantis": "Boarding ship with teleporter, strong crew combat (AGGRESSIVE)"
    }

    for i, (ship_type, description) in enumerate(ship_info.items(), 1):
        print(f"  {i}. {ship_type.upper():10} - {description}")

    print()

    while True:
        try:
            choice = input("Select ship (1-3) or name: ").strip().lower()

            # Try by number
            if choice in ['1', '2', '3']:
                ship_type = list(ship_info.keys())[int(choice) - 1]
                return ship_type

            # Try by name
            if choice in SHIP_TEMPLATES:
                return choice

            print(f"Invalid choice: {choice}")

        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting...")
            sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='spacecmd - Command-Line Spaceship Simulator')
    parser.add_argument('--ship', choices=list(SHIP_TEMPLATES.keys()),
                        help='Choose ship type')
    parser.add_argument('--no-intro', action='store_true',
                        help='Skip intro text')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable color output')

    args = parser.parse_args()

    # Print intro
    if not args.no_intro:
        print_intro()

    # Choose ship
    if args.ship:
        ship_type = args.ship
        print(f"Launching {ship_type.upper()}...\n")
    else:
        ship_type = choose_ship()
        print()

    # Create ship
    try:
        ship = create_ship(ship_type)
        print(f"✓ {ship.name} is ready for departure!")
        print(f"  Class: {ship.ship_class}")
        print(f"  Hull: {ship.hull}")
        print(f"  Crew: {len(ship.crew)}")
        print()
        print("Initializing ship systems...")
        print()
        try:
            input("Press Enter to begin...")
        except (EOFError, KeyboardInterrupt):
            pass
        print()
    except Exception as e:
        print(f"ERROR: Failed to initialize ship: {e}")
        sys.exit(1)

    # Create game
    game = Game(ship)

    # Run game loop
    try:
        game.run()
    except Exception as e:
        print(f"\n\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║                   Mission Terminated                          ║")
    print("║                                                               ║")
    print("║              Thank you for playing spacecmd!                  ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()


if __name__ == '__main__':
    main()

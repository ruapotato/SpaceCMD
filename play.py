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


def run_gui_mode(ship_type=None):
    """
    Run the game in GUI desktop mode.

    Args:
        ship_type: Optional ship type to start with
    """
    from core.gui import Desktop
    from core.ship_os import ShipOS
    from core.ships import create_ship

    print("Starting SpaceCMD Desktop Environment...")
    print("Booting ShipOS...")
    print("")

    # Create ship first
    ship = create_ship(ship_type or "kestrel")

    # Create ShipOS instance with ship
    ship_os = ShipOS(ship=ship)

    # Boot the system
    ship_os.boot(verbose=False)

    # Login as root
    if not ship_os.login('root', 'root'):
        print("ERROR: Failed to login to ShipOS")
        return

    print("ShipOS booted successfully!")
    print("Controls:")
    print("  Ctrl+T - New terminal")
    print("  Ctrl+D - Tactical display")
    print("  ESC    - Exit")
    print("")

    # Create desktop environment
    desktop = Desktop(width=1280, height=800, fullscreen=False)

    # Set ship_os in desktop (creates top bar with system monitor)
    desktop.set_ship_os(ship_os)

    # Create world manager (Python layer controls world, not ShipOS)
    from core.world_manager import WorldManager
    world_manager = WorldManager(ship_os)
    ship_os.world_manager = world_manager  # Give ShipOS reference to world

    # Wire up attack callback to desktop flash effect
    world_manager.on_attack_callback = desktop.trigger_attack_flash

    # For tutorial: spawn a gnat immediately after 5 seconds
    def tutorial_encounter():
        """Spawn tutorial enemy after delay"""
        import time
        time.sleep(5.0)
        if desktop.running:
            print("\n📡 Incoming transmission detected...")
            time.sleep(1.0)
            print("⚠️  Unidentified craft approaching!")
            time.sleep(0.5)
            world_manager.trigger_encounter("gnat", forced=True)

    import threading
    tutorial_thread = threading.Thread(target=tutorial_encounter, daemon=True)
    tutorial_thread.start()

    # Start update loops in background
    def update_world_and_ship():
        """Update world and ship state continuously"""
        import time
        while desktop.running:
            # Update world (spawns enemies, manages combat)
            world_manager.update(0.1)
            # Update ship (physics, crew, oxygen)
            ship_os.update_ship_state(0.1)
            time.sleep(0.1)

    world_thread = threading.Thread(target=update_world_and_ship, daemon=True)
    world_thread.start()

    # Override desktop's create_terminal_window to integrate with ShipOS
    original_create_terminal = desktop.create_terminal_window

    def create_shipos_terminal(title="Terminal", x=100, y=100):
        """Create a terminal connected to ShipOS"""
        window = original_create_terminal(title, x, y)
        terminal = window.content_widget

        # Set prompt from ShipOS
        terminal.set_prompt(ship_os.get_prompt())

        # Connect to ShipOS
        def command_handler(cmd):
            """Execute command through ShipOS"""
            exit_code, stdout, stderr = ship_os.execute_command(cmd)

            # Write output
            if stdout:
                terminal.write(stdout)
            if stderr:
                terminal.write(stderr)

            # Update prompt
            terminal.set_prompt(ship_os.get_prompt())

        terminal.set_command_callback(command_handler)

        # Welcome message for first terminal
        if len(desktop.windows) == 1:
            terminal.write("╔═══════════════════════════════════════════════════╗")
            terminal.write("║         SPACECMD DESKTOP ENVIRONMENT              ║")
            terminal.write("║              Ship OS v1.0                         ║")
            terminal.write("╚═══════════════════════════════════════════════════╝")
            terminal.write("")
            terminal.write(f"Welcome aboard the {ship_type or 'kestrel'}!")
            terminal.write("")
            terminal.write("All commands are executed through ShipOS.")
            terminal.write("Try: ls, pwd, cat /etc/hostname, status")
            terminal.write("")

        return window

    # Replace the method
    desktop.create_terminal_window = create_shipos_terminal

    # Create initial terminal (offset from top bar)
    topbar_height = desktop.topbar.height if desktop.topbar else 32
    desktop.create_terminal_window("Ship Terminal", 50, topbar_height + 20)

    # Create tactical display and wire to world manager
    tactical_window = desktop.create_tactical_window("Tactical Display", 600, topbar_height + 20)
    if tactical_window:
        tactical_widget = tactical_window.content_widget
        tactical_widget.world_manager = world_manager
        tactical_widget.ship_os = ship_os  # Wire up ship_os for command execution

        # Update tactical from combat every frame
        desktop._tactical_widget = tactical_widget

    # Create galaxy map window and wire to world manager
    map_window = desktop.create_map_window("Galaxy Map", 50, topbar_height + 50)
    if map_window:
        map_widget = map_window.content_widget
        map_widget.set_world_manager(world_manager)
        map_widget.ship_os = ship_os  # Wire up ship_os for command execution

    # Make stars static (they'll move when ship moves)
    desktop.warp_speed = 0

    # Run the desktop
    desktop.run()

    print("Desktop environment closed.")


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
        "kestrel": ("NAUTILUS", "Balanced cruiser with shields and good crew (RECOMMENDED)"),
        "stealth": ("CUCUMBER", "Stealth ship with cloaking, no shields (HARD MODE)"),
        "mantis": ("HAIRPIN", "Boarding ship with teleporter, strong crew combat (AGGRESSIVE)")
    }

    for i, (ship_type, (name, description)) in enumerate(ship_info.items(), 1):
        print(f"  {i}. {name:10} - {description}")

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
    parser.add_argument('--no-gui', action='store_true',
                        help='Use pure CLI mode (for debugging)')
    parser.add_argument('--gui', action='store_true',
                        help='Use GUI desktop environment (default)')

    args = parser.parse_args()

    # Determine mode (default to GUI unless --no-gui specified)
    use_gui = not args.no_gui

    # Choose ship
    if args.ship:
        ship_type = args.ship
    else:
        # Only interactive ship selection in CLI mode
        if not use_gui:
            if not args.no_intro:
                print_intro()
            ship_type = choose_ship()
            print()
        else:
            # Default ship for GUI mode (can add GUI ship selector later)
            ship_type = "kestrel"

    # Route to appropriate mode
    if use_gui:
        # GUI MODE
        try:
            run_gui_mode(ship_type)
        except Exception as e:
            print(f"\n\nGUI ERROR: {e}")
            import traceback
            traceback.print_exc()
            print("\nTry running with --no-gui for CLI mode")
            sys.exit(1)
    else:
        # CLI MODE (original terminal-based game)
        if not args.no_intro:
            print_intro()

        print(f"Launching {ship_type.upper()}...\n")

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

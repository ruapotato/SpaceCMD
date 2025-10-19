#!/usr/bin/env python3
"""
Test/Demo script for SpaceCMD Pygame Desktop Environment

Demonstrates:
- Window management
- Terminal emulator
- Tactical display
- Starfield background
- LCARS + GNOME 2 theming
"""

import sys
import os

# Add core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.gui import Desktop


def terminal_command_handler(terminal, command):
    """Handle commands from terminal"""
    command = command.strip().lower()

    if command == "help":
        terminal.write("Available commands:")
        terminal.write("  help     - Show this help")
        terminal.write("  status   - Show ship status")
        terminal.write("  fire     - Fire weapons")
        terminal.write("  warp     - Enable warp drive")
        terminal.write("  clear    - Clear terminal")
        terminal.write("  systems  - List ship systems")
        terminal.write("")

    elif command == "status":
        terminal.write("=== SHIP STATUS ===")
        terminal.write("Hull: 28/30")
        terminal.write("Shields: 3/4")
        terminal.write("Power: 7/8")
        terminal.write("Crew: 3/3")
        terminal.write("")

    elif command == "fire":
        terminal.write(">>> WEAPONS FIRING!")
        terminal.write("Laser charged... FIRE!")
        terminal.write("")

    elif command == "warp":
        terminal.write(">>> ENGAGING WARP DRIVE")
        terminal.write("Warp speed: 5")
        terminal.write("")

    elif command == "systems":
        terminal.write("=== SHIP SYSTEMS ===")
        terminal.write("  [OK] Shields    - 100% - Power: 2")
        terminal.write("  [OK] Weapons    - 100% - Power: 2")
        terminal.write("  [OK] Engines    - 100% - Power: 2")
        terminal.write("  [OK] Oxygen     - 100% - Power: 1")
        terminal.write("  [OK] Medbay     -  80% - Power: 1")
        terminal.write("")

    elif command == "clear":
        terminal.clear()

    elif command:
        terminal.write(f"Unknown command: {command}")
        terminal.write("Type 'help' for available commands.")
        terminal.write("")


def main():
    """Main demo function"""
    print("Starting SpaceCMD Desktop Environment...")
    print("Controls:")
    print("  Ctrl+T - New terminal")
    print("  Ctrl+D - Tactical display")
    print("  ESC    - Exit")
    print("")

    # Create desktop
    desktop = Desktop(width=1024, height=768, fullscreen=False)

    # Create initial terminal window
    terminal_window = desktop.create_terminal_window("Main Terminal", 100, 100)

    # Set up terminal
    terminal = terminal_window.content_widget
    terminal.set_prompt("ship:/ $ ")

    # Set command handler
    def cmd_handler(command):
        terminal_command_handler(terminal, command)

    terminal.set_command_callback(cmd_handler)

    # Welcome message
    terminal.write("╔═══════════════════════════════════════════════════╗")
    terminal.write("║         SPACECMD DESKTOP ENVIRONMENT              ║")
    terminal.write("║              Kestrel Ship OS v1.0                 ║")
    terminal.write("╚═══════════════════════════════════════════════════╝")
    terminal.write("")
    terminal.write("Welcome aboard the Kestrel!")
    terminal.write("")
    terminal.write("Type 'help' for available commands.")
    terminal.write("Use Ctrl+T to open new terminals.")
    terminal.write("Use Ctrl+D to open tactical display.")
    terminal.write("")

    # Create tactical display
    tactical_window = desktop.create_tactical_window("Tactical Display", 200, 50)

    # Run desktop
    desktop.run()

    print("Desktop environment closed.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

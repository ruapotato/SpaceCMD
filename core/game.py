"""
spacecmd - Main Game Loop

Integrates ship display with interactive command shell.
Now powered by ShipOS - a full Unix-like operating system!
"""

import os
import sys
from typing import Optional, List
from .ship import Ship, SystemType
from .render import ShipRenderer
from .ships import create_ship
from .terminal_ui import TerminalUI, Color
from .ship_os import ShipOS


class Game:
    """
    Main game state and loop.
    Combines visual display with PooScript shell.
    """

    def __init__(self, ship: Ship, use_terminal_ui: bool = True):
        self.ship = ship
        self.renderer = ShipRenderer(use_color=True)
        self.running = True
        self.use_terminal_ui = use_terminal_ui

        # Initialize ShipOS - full Unix-like OS for the ship!
        self.ship_os = ShipOS(ship)
        self.ship_os.login('root', 'root')  # Auto-login as captain

        # Always init message log for compatibility
        self.message_log: List[str] = []
        self.max_log_lines = 5

        # Initialize UI
        if use_terminal_ui:
            self.ui = TerminalUI()
            # Set player ship name in tactical display
            self.ui.set_player_ship_name(ship.name.upper())
        else:
            self.ui = None

        # Combat state
        self.in_combat = False
        self.enemy_ship: Optional[Ship] = None

    def log(self, message: str, color: str = ""):
        """Add a message to the message log"""
        if self.ui:
            self.ui.add_output(message)
        else:
            self.message_log.append(message)
            if len(self.message_log) > self.max_log_lines:
                self.message_log.pop(0)

    def clear_screen(self):
        """Clear the terminal"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def render(self):
        """Render the complete game display"""
        if self.ui:
            # Update viewport with combat info
            if self.in_combat and self.enemy_ship:
                # Create enemy ship layout from enemy ship data
                from .terminal_ui import ShipLayout
                enemy_layout = ShipLayout(self.enemy_ship.name.upper())
                self.ui.set_enemy_ship(enemy_layout)
            else:
                self.ui.clear_enemy()

            # Render terminal UI
            self.ui.render_frame(
                ship_name=self.ship.name.upper(),
                hull=self.ship.hull,
                shields=int(self.ship.shields)
            )
        else:
            # Old rendering
            self.clear_screen()

            # Render ship
            ship_lines = self.renderer.render_ship(self.ship)
            for line in ship_lines:
                print(line)

            # Render message log
            print()
            print("─" * 60)
            print("MESSAGE LOG:")
            for msg in self.message_log:
                print(f"  {msg}")

            # Render command prompt
            print("─" * 60)
            print()

    def handle_command(self, command: str) -> bool:
        """
        Handle a gameplay command through ShipOS.
        All commands now go through the PooScript shell!
        Returns False if should exit game.
        """
        if not command.strip():
            return True

        # Check for exit/quit commands (handled specially)
        cmd_lower = command.strip().lower()
        if cmd_lower in ['exit', 'quit', 'q']:
            self.log("Exiting spacecmd. Safe travels!")
            self.running = False
            return False

        # Check for warp/jump for visual effect
        if cmd_lower in ['warp', 'jump']:
            if self.ui:
                self.ui.set_warp(True)
                self.log(f"{Color.CYAN}⚡ WARP DRIVE ENGAGED!{Color.RESET}")
                self.log(f"{Color.CYAN}═══ Streaking through space ═══{Color.RESET}")
            else:
                self.log("⚡ Warp drive engaged!")
            return True

        # Execute command through ShipOS
        try:
            exit_code, stdout, stderr = self.ship_os.execute_command(command)

            # Display output
            if stdout:
                for line in stdout.rstrip('\n').split('\n'):
                    self.log(line)

            if stderr:
                for line in stderr.rstrip('\n').split('\n'):
                    self.log(f"{Color.RED}{line}{Color.RESET}")

        except Exception as e:
            self.log(f"{Color.RED}Error executing command: {e}{Color.RESET}")

        return True

    # ==================== GAME LOOP HELPERS ====================
    # Note: Most commands are now handled by ShipOS PooScript binaries
    # Only game loop specific functionality remains here

    # ==================== GAME LOOP ====================

    def run(self):
        """Main game loop"""
        # Show welcome message
        self.log(f"{Color.GREEN}✓{Color.RESET} Welcome aboard the {self.ship.name}!")
        self.log("Type 'help' for commands, 'exit' to quit")
        self.log("")
        self.log("ShipOS initialized - all systems now scriptable with PooScript!")
        self.log("Try: ls /systems, cat /ship/hull, or just type 'status'")

        while self.running:
            # Update viewport animation
            if self.ui:
                self.ui.update_viewport(0.5)

            # Render game state
            self.render()

            # Get command
            if self.ui:
                command = self.ui.get_command()
            else:
                try:
                    command = input(f"{self.ship.name}> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    self.log("Exiting...")
                    break

            # Handle command
            if command:
                self.running = self.handle_command(command)

        # Final message
        if not self.ui:
            self.render()
            print("\nFarewell, Captain!")
        else:
            self.log(f"{Color.YELLOW}Farewell, Captain!{Color.RESET}")

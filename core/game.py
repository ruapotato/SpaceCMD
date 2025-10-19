"""
spacecmd - Main Game Loop

Integrates ship display with interactive command shell.
Now powered by ShipOS - a full Unix-like operating system!
Includes WorldManager for full gameplay with combat and galaxy navigation.
"""

import os
import sys
import threading
import time
from typing import Optional, List
from .ship import Ship, SystemType
from .render import ShipRenderer
from .ships import create_ship
from .terminal_ui import TerminalUI, Color
from .ship_os import ShipOS
from .world_manager import WorldManager


class Game:
    """
    Main game state and loop.
    Combines visual display with PooScript shell.
    Now includes WorldManager for full gameplay!
    """

    def __init__(self, ship: Ship, use_terminal_ui: bool = True, enable_world: bool = True):
        self.ship = ship
        self.renderer = ShipRenderer(use_color=True)
        self.running = True
        self.use_terminal_ui = use_terminal_ui

        # Initialize ShipOS - full Unix-like OS for the ship!
        self.ship_os = ShipOS(ship)
        self.ship_os.login('root', 'root')  # Auto-login as captain

        # Always init message log for compatibility
        self.message_log: List[str] = []
        self.max_log_lines = 20  # Increased for combat messages

        # Initialize UI
        if use_terminal_ui:
            self.ui = TerminalUI()
            # Set player ship name in tactical display
            self.ui.set_player_ship_name(ship.name.upper())
        else:
            self.ui = None

        # World Manager - controls combat, encounters, galaxy
        self.world_manager = None
        self.world_thread = None
        if enable_world:
            self.world_manager = WorldManager(self.ship_os)
            self.ship_os.world_manager = self.world_manager

            # Start world update thread
            self.world_thread = threading.Thread(target=self._update_world_loop, daemon=True)
            self.world_thread.start()

        # Combat state (shortcut to world_manager.combat_state)
        self.in_combat = False
        self.enemy_ship: Optional[Ship] = None

    def _update_world_loop(self):
        """Background thread to update world and ship state"""
        while self.running:
            if self.world_manager:
                self.world_manager.update(0.1)
                self.ship_os.update_ship_state(0.1)

                # Update combat state shortcuts
                if self.world_manager.combat_state and self.world_manager.combat_state.active:
                    self.in_combat = True
                    self.enemy_ship = self.world_manager.enemy_ship.ship if self.world_manager.enemy_ship else None
                else:
                    self.in_combat = False
                    self.enemy_ship = None

            time.sleep(0.1)

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
            # Console mode rendering
            self.clear_screen()

            # Header
            print("╔" + "═" * 78 + "╗")
            print(f"║  SPACECMD - {self.ship.name.upper():^66} ║")
            print("╚" + "═" * 78 + "╝")
            print()

            # Ship status bar
            hull_pct = self.ship.hull / self.ship.hull_max if self.ship.hull_max > 0 else 0
            hull_bar = "█" * int(hull_pct * 20) + "░" * (20 - int(hull_pct * 20))
            shields_display = "🛡️" * int(self.ship.shields)

            print(f"  HULL: [{hull_bar}] {self.ship.hull}/{self.ship.hull_max}")
            print(f"  SHIELDS: {shields_display} {int(self.ship.shields)}/{self.ship.shields_max}")

            # Galaxy position
            if self.world_manager:
                galaxy_pos = self.ship.galaxy_distance_from_center
                max_dist = self.world_manager.galaxy.max_distance
                progress_pct = (max_dist - galaxy_pos) / max_dist * 100
                print(f"  POSITION: {galaxy_pos:.0f}u from center ({progress_pct:.1f}% to core)")

            print()

            # Combat display
            if self.in_combat and self.enemy_ship:
                print("┌─ COMBAT ─────────────────────────────────────────────────────────┐")
                print(f"│  ENEMY: {self.enemy_ship.name:30}                        │")
                e_hull_pct = self.enemy_ship.hull / self.enemy_ship.hull_max if self.enemy_ship.hull_max > 0 else 0
                e_hull_bar = "█" * int(e_hull_pct * 15) + "░" * (15 - int(e_hull_pct * 15))
                e_shields = "🛡️" * int(self.enemy_ship.shields)
                print(f"│  Hull: [{e_hull_bar}] {self.enemy_ship.hull}/{self.enemy_ship.hull_max:>3}                       │")
                print(f"│  Shields: {e_shields} {int(self.enemy_ship.shields)}/{self.enemy_ship.shields_max}                                         │")

                # Show weapons status
                print(f"│                                                                  │")
                print(f"│  YOUR WEAPONS:                                                   │")
                for i, weapon in enumerate(self.ship.weapons[:3]):  # Show first 3
                    charge_pct = int(weapon.charge * 100)
                    ready = "READY" if weapon.is_ready() else f"{charge_pct}%"
                    print(f"│    {i+1}. {weapon.name:20} {ready:>6}                          │")
                print("└──────────────────────────────────────────────────────────────────┘")
                print()

            # Message log
            print("─ LOG " + "─" * 73)
            for msg in self.message_log[-15:]:  # Show last 15 messages
                # Truncate long messages
                if len(msg) > 78:
                    msg = msg[:75] + "..."
                print(f"  {msg}")

            # Command prompt
            print("─" * 79)
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
        if self.world_manager:
            self.log("Navigate the galaxy, fight enemies, and reach the core!")
            self.log(f"Current position: {self.ship.galaxy_distance_from_center:.0f}u from center")
            self.log("")
            self.log("Commands: 'status', 'systems', 'jump', 'fire 1', 'target shields'")
            self.log("ShipOS: 'ls /systems', 'cat /ship/hull', 'help'")
            self.log("Type 'exit' to quit")
        else:
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
                    prompt = f"{self.ship.name}"
                    if self.in_combat:
                        prompt += " [COMBAT]"
                    prompt += "> "
                    command = input(prompt).strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    self.log("Exiting...")
                    break

            # Handle command
            if command:
                self.running = self.handle_command(command)

        # Final message
        if not self.ui:
            self.clear_screen()
            print("\n╔" + "═" * 60 + "╗")
            print("║" + " " * 60 + "║")
            print("║" + "Mission Complete".center(60) + "║")
            print("║" + " " * 60 + "║")
            if self.ship.hull > 0:
                print("║" + f"Final Status: {self.ship.hull}/{self.ship.hull_max} hull".center(60) + "║")
                print("║" + "Thank you for playing SpaceCMD!".center(60) + "║")
            else:
                print("║" + "Ship Destroyed".center(60) + "║")
            print("║" + " " * 60 + "║")
            print("╚" + "═" * 60 + "╝")
            print("\nFarewell, Captain!\n")
        else:
            self.log(f"{Color.YELLOW}Farewell, Captain!{Color.RESET}")

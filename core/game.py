"""
spacecmd - Main Game Loop

Integrates ship display with interactive command shell.
"""

import os
import sys
from typing import Optional, List
from .ship import Ship, SystemType
from .render import ShipRenderer
from .ships import create_ship
from .terminal_ui import TerminalUI, Color


class Game:
    """
    Main game state and loop.
    Combines visual display with command input.
    """

    def __init__(self, ship: Ship, use_terminal_ui: bool = True):
        self.ship = ship
        self.renderer = ShipRenderer(use_color=True)
        self.running = True
        self.use_terminal_ui = use_terminal_ui

        # Always init message log for compatibility
        self.message_log: List[str] = []
        self.max_log_lines = 5

        # Initialize UI
        if use_terminal_ui:
            self.ui = TerminalUI()
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
                self.ui.add_enemy(self.ui.width - 20, self.ui.viewport_height // 2)
            else:
                self.ui.clear_enemies()

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
        Handle a gameplay command.
        Returns False if should exit game.
        """
        if not command.strip():
            return True

        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:]

        # Route to command handlers
        if cmd in ['exit', 'quit', 'q']:
            return self.cmd_exit(args)
        elif cmd in ['help', 'h', '?']:
            return self.cmd_help(args)
        elif cmd in ['status', 'stat', 's']:
            return self.cmd_status(args)
        elif cmd in ['power', 'pwr', 'p']:
            return self.cmd_power(args)
        elif cmd in ['crew', 'c']:
            return self.cmd_crew(args)
        elif cmd in ['assign', 'move']:
            return self.cmd_assign(args)
        elif cmd in ['systems', 'sys']:
            return self.cmd_systems(args)
        elif cmd in ['repair', 'fix']:
            return self.cmd_repair(args)
        elif cmd in ['vent', 'v']:
            return self.cmd_vent(args)
        elif cmd in ['damage', 'dmg']:  # Debug command
            return self.cmd_damage(args)
        elif cmd in ['wait', 'w']:
            return self.cmd_wait(args)
        elif cmd in ['warp', 'jump']:
            return self.cmd_warp(args)
        else:
            self.log(f"Unknown command: {cmd}. Type 'help' for commands.")

        return True

    # ==================== COMMANDS ====================

    def cmd_exit(self, args):
        """Exit the game"""
        self.log("Exiting spacecmd. Safe travels!")
        self.running = False
        return False

    def cmd_help(self, args):
        """Show help"""
        self.log("=== SPACECMD COMMANDS ===")
        self.log("status/s        - Show detailed ship status")
        self.log("systems/sys     - List all systems")
        self.log("power <sys> <n> - Allocate N power to system")
        self.log("crew/c          - Show crew roster")
        self.log("assign <crew> <room> - Move crew to room")
        self.log("repair <room>   - Order crew to repair room")
        self.log("vent <room>     - Open airlocks to vent room")
        self.log("warp/jump       - Engage warp drive")
        self.log("wait/w [n]      - Wait N seconds (default 1)")
        self.log("help/h/?        - Show this help")
        self.log("exit/quit/q     - Exit game")
        return True

    def cmd_status(self, args):
        """Show detailed status"""
        self.log(f"=== {self.ship.name.upper()} ({self.ship.ship_class}) ===")
        self.log(f"Hull: {self.ship.hull}/{self.ship.hull_max} | Shields: {int(self.ship.shields)}/{self.ship.shields_max}")
        self.log(f"Power: {self.ship.reactor_power - self.ship.power_available}/{self.ship.reactor_power} | Fuel: {self.ship.fuel}")
        self.log(f"Crew: {len(self.ship.crew)} | Scrap: {self.ship.scrap}")
        return True

    def cmd_systems(self, args):
        """List all systems"""
        self.log("=== SHIP SYSTEMS ===")
        for room_name, room in self.ship.rooms.items():
            if room.system_type != SystemType.NONE:
                status = "ONLINE" if room.is_functional else "OFFLINE"
                health = f"{room.health:.0%}"
                power = f"{room.power_allocated}/{room.max_power}"
                self.log(f"{room_name:12} [{status:7}] HP:{health:4} PWR:{power}")
        return True

    def cmd_power(self, args):
        """Allocate power to a system"""
        if len(args) < 2:
            self.log("Usage: power <system> <amount>")
            self.log("Example: power shields 3")
            return True

        system_name = args[0].lower()
        try:
            amount = int(args[1])
        except ValueError:
            self.log(f"Invalid power amount: {args[1]}")
            return True

        # Find system by name
        system_type = None
        target_room = None

        for room in self.ship.rooms.values():
            if room.system_type.value == system_name or room.name.lower() == system_name.lower():
                system_type = room.system_type
                target_room = room
                break

        if not system_type or system_type == SystemType.NONE:
            self.log(f"System not found: {system_name}")
            return True

        # Check current power
        current = target_room.power_allocated
        delta = amount - current

        if delta > 0:
            # Allocating more power
            if delta > self.ship.power_available:
                self.log(f"Not enough power! Need {delta}, have {self.ship.power_available}")
                return True
            if amount > target_room.max_power:
                self.log(f"{target_room.name} max power is {target_room.max_power}")
                amount = target_room.max_power
                delta = amount - current

            target_room.power_allocated = amount
            self.ship.power_available -= delta
            self.log(f"Allocated {amount} power to {target_room.name} (+{delta})")

        elif delta < 0:
            # Removing power
            target_room.power_allocated = amount
            self.ship.power_available -= delta  # delta is negative, so this adds
            self.log(f"Allocated {amount} power to {target_room.name} ({delta})")

        else:
            self.log(f"{target_room.name} already has {amount} power")

        return True

    def cmd_crew(self, args):
        """Show crew roster"""
        self.log("=== CREW ROSTER ===")
        for crew in self.ship.crew:
            location = crew.room.name if crew.room else "Unknown"
            hp = f"{crew.health:.0f}/{crew.health_max}"
            status = "HEALTHY" if crew.health > 70 else "INJURED" if crew.health > 30 else "CRITICAL"
            self.log(f"{crew.name:20} ({crew.race:8}) HP:{hp:7} [{status:8}] @ {location}")
        return True

    def cmd_assign(self, args):
        """Assign crew to a room"""
        if len(args) < 2:
            self.log("Usage: assign <crew_name> <room_name>")
            self.log("Example: assign hayes helm")
            return True

        crew_name = args[0].lower()
        room_name = " ".join(args[1:]).lower()

        # Find crew
        crew = None
        for c in self.ship.crew:
            if crew_name in c.name.lower():
                crew = c
                break

        if not crew:
            self.log(f"Crew member not found: {crew_name}")
            return True

        # Find room
        room = None
        for r in self.ship.rooms.values():
            if room_name in r.name.lower():
                room = r
                break

        if not room:
            self.log(f"Room not found: {room_name}")
            return True

        # Assign
        old_room = crew.room.name if crew.room else "nowhere"
        crew.assign_to_room(room)
        self.log(f"{crew.name} moved from {old_room} to {room.name}")

        return True

    def cmd_repair(self, args):
        """Order crew to repair a room"""
        if len(args) < 1:
            self.log("Usage: repair <room_name>")
            return True

        room_name = " ".join(args).lower()

        # Find room
        room = None
        for r in self.ship.rooms.values():
            if room_name in r.name.lower():
                room = r
                break

        if not room:
            self.log(f"Room not found: {room_name}")
            return True

        if room.health >= 1.0:
            self.log(f"{room.name} is already fully repaired")
            return True

        if not room.crew:
            self.log(f"No crew in {room.name} to perform repairs")
            return True

        # Repair happens over time in update loop
        self.log(f"Crew in {room.name} will repair the system")
        return True

    def cmd_vent(self, args):
        """Vent a room (open airlocks)"""
        if len(args) < 1:
            self.log("Usage: vent <room_name>")
            return True

        room_name = " ".join(args).lower()

        # Find room
        room = None
        for r in self.ship.rooms.values():
            if room_name in r.name.lower():
                room = r
                break

        if not room:
            self.log(f"Room not found: {room_name}")
            return True

        room.venting = not room.venting

        if room.venting:
            self.log(f"Venting {room.name} - airlocks OPEN")
            if room.crew:
                self.log(f"WARNING: {len(room.crew)} crew member(s) in venting room!")
        else:
            self.log(f"Closed airlocks in {room.name}")

        return True

    def cmd_damage(self, args):
        """Debug: Damage a room"""
        if len(args) < 1:
            self.log("Usage: damage <room_name> [amount]")
            return True

        room_name = args[0].lower()
        amount = float(args[1]) if len(args) > 1 else 0.3

        # Find room
        room = None
        for r in self.ship.rooms.values():
            if room_name in r.name.lower():
                room = r
                break

        if not room:
            self.log(f"Room not found: {room_name}")
            return True

        room.take_damage(amount)
        self.log(f"{room.name} took {amount:.0%} damage (now at {room.health:.0%})")

        # Random chance to start fire
        import random
        if random.random() < 0.3:
            room.on_fire = True
            self.log(f"FIRE in {room.name}!")

        return True

    def cmd_wait(self, args):
        """Wait for time to pass"""
        duration = float(args[0]) if args else 1.0

        self.log(f"Waiting {duration:.1f} seconds...")

        # Update ship state
        self.ship.update(duration)

        # Check for events
        for room in self.ship.rooms.values():
            if room.health < 0.5 and room.health > 0:
                self.log(f"⚠️  {room.name} is badly damaged!")
            if room.on_fire:
                self.log(f"🔥 {room.name} is on fire!")
            if room.oxygen_level < 0.3:
                self.log(f"💨 Low oxygen in {room.name}!")

        for crew in self.ship.crew:
            if crew.health < 50 and crew.health > 0:
                self.log(f"⚠️  {crew.name} is injured!")
            if crew.health <= 0:
                self.log(f"💀 {crew.name} has died!")

        return True

    def cmd_warp(self, args):
        """Engage warp drive for visual effect"""
        if self.ui:
            self.ui.set_warp(True)
            self.log(f"{Color.CYAN}⚡ WARP DRIVE ENGAGED!{Color.RESET}")
            self.log(f"{Color.CYAN}═══ Streaking through space ═══{Color.RESET}")
        else:
            self.log("⚡ Warp drive engaged!")
        return True

    # ==================== GAME LOOP ====================

    def run(self):
        """Main game loop"""
        self.log(f"{Color.GREEN}✓{Color.RESET} Welcome aboard the {self.ship.name}!")
        self.log("Type 'help' for commands, 'exit' to quit")

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

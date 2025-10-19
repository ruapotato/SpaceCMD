#!/usr/bin/env python3
"""
LCARS-style Terminal UI System
Three-panel interface: Viewport (top), Tactical Map (middle), Command Line (bottom)
"""

import sys
import os
import random
import shutil
import tempfile
from typing import List, Tuple, Optional


class Color:
    """ANSI color codes for LCARS theme"""
    # LCARS colors
    ORANGE = '\033[38;5;208m'  # LCARS orange
    PINK = '\033[38;5;13m'      # LCARS pink/magenta
    BLUE = '\033[38;5;39m'      # LCARS blue
    PURPLE = '\033[38;5;99m'    # LCARS purple
    YELLOW = '\033[38;5;220m'   # LCARS yellow

    # Ship/space colors
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    DARK_GRAY = '\033[38;5;236m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'

    # Text formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    CLEAR = '\033[2J'
    HOME = '\033[H'


class ShipSystem:
    """Represents a ship system (engines, shields, etc.)"""
    def __init__(self, name: str, health: int = 100, power: int = 0):
        self.name = name
        self.health = health
        self.power = power
        self.online = True
        self.icon = self._get_icon()

    def _get_icon(self) -> str:
        icons = {
            "engines": "E",
            "shields": "S",
            "weapons": "W",
            "oxygen": "O",
            "medbay": "M",
            "reactor": "R",
            "helm": "H",
            "sensors": "N"
        }
        return icons.get(self.name.lower(), "?")


class ShipLayout:
    """Represents a ship's interior layout"""
    def __init__(self, name: str = "Player"):
        self.name = name
        self.rooms = {}  # {(x, y): {"name": str, "system": ShipSystem, "crew": []}}
        self.crew_positions = []  # [(x, y, name)]
        self.hull_breach = []  # [(x, y)] - breached rooms
        self._create_default_layout()

    def _create_default_layout(self):
        """Create default ship layout"""
        # Simple 3x2 room layout
        self.rooms = {
            (0, 0): {"name": "Helm", "system": ShipSystem("helm"), "crew": []},
            (1, 0): {"name": "Shields", "system": ShipSystem("shields"), "crew": []},
            (2, 0): {"name": "Weapons", "system": ShipSystem("weapons"), "crew": []},
            (0, 1): {"name": "Engines", "system": ShipSystem("engines"), "crew": []},
            (1, 1): {"name": "Oxygen", "system": ShipSystem("oxygen"), "crew": []},
            (2, 1): {"name": "Medbay", "system": ShipSystem("medbay"), "crew": []},
        }
        # Add some crew
        self.crew_positions = [(0, 0, "AI-1"), (1, 0, "AI-2"), (2, 1, "AI-3")]


class TacticalMap:
    """Renders tactical map showing detailed ship interiors"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.player_ship = ShipLayout("KESTREL")
        self.enemy_ship = None
        self.projectiles = []  # (x, y, type, direction)
        self.show_enemy = False

    def set_enemy_ship(self, enemy_layout: ShipLayout):
        """Set the current enemy ship to display"""
        self.enemy_ship = enemy_layout
        self.show_enemy = True

    def clear_enemy(self):
        """Clear enemy ship"""
        self.enemy_ship = None
        self.show_enemy = False

    def update(self, dt: float = 0.1):
        """Update projectiles and animations"""
        new_projectiles = []
        for x, y, ptype, dx, dy in self.projectiles:
            # Move projectile
            x += dx * 3
            y += dy
            # Keep if still on screen
            if 0 <= x < self.width and 0 <= y < self.height:
                new_projectiles.append((x, y, ptype, dx, dy))
        self.projectiles = new_projectiles

    def add_projectile(self, x: int, y: int, ptype: str = "laser", direction: Tuple[int, int] = (1, 0)):
        """Add weapon fire to map"""
        self.projectiles.append((x, y, ptype, direction[0], direction[1]))

    def _render_ship(self, ship: ShipLayout, start_x: int, start_y: int, enemy: bool = False) -> List[str]:
        """Render a single ship's interior"""
        ship_lines = []
        color = Color.RED if enemy else Color.GREEN

        # Ship header
        ship_lines.append(f"{color}╔═══════════════════════════╗{Color.RESET}")
        ship_lines.append(f"{color}║{Color.RESET} {ship.name:^25} {color}║{Color.RESET}")
        ship_lines.append(f"{color}╠═══════════════════════════╣{Color.RESET}")

        # Render rooms in a grid
        for row in range(2):  # 2 rows of rooms
            # Room top border
            line = f"{color}║{Color.RESET}"
            for col in range(3):  # 3 columns
                if (col, row) in ship.rooms:
                    line += f"{color}┌───────┐{Color.RESET}"
                else:
                    line += "         "
            line += f"{color}║{Color.RESET}"
            ship_lines.append(line)

            # Room name and system
            line = f"{color}║{Color.RESET}"
            for col in range(3):
                if (col, row) in ship.rooms:
                    room = ship.rooms[(col, row)]
                    system = room["system"]
                    sys_color = Color.GREEN if system.online else Color.DARK_GRAY
                    line += f"{color}│{Color.RESET}{sys_color}{system.icon:^7}{Color.RESET}{color}│{Color.RESET}"
                else:
                    line += "         "
            line += f"{color}║{Color.RESET}"
            ship_lines.append(line)

            # Crew positions
            line = f"{color}║{Color.RESET}"
            for col in range(3):
                if (col, row) in ship.rooms:
                    # Count crew in this room
                    crew_here = sum(1 for x, y, _ in ship.crew_positions if (x, y) == (col, row))
                    crew_str = f"🤖{crew_here}" if crew_here > 0 else "   "
                    line += f"{color}│{Color.RESET}{crew_str:^7}{color}│{Color.RESET}"
                else:
                    line += "         "
            line += f"{color}║{Color.RESET}"
            ship_lines.append(line)

            # Room bottom border
            line = f"{color}║{Color.RESET}"
            for col in range(3):
                if (col, row) in ship.rooms:
                    line += f"{color}└───────┘{Color.RESET}"
                else:
                    line += "         "
            line += f"{color}║{Color.RESET}"
            ship_lines.append(line)

        ship_lines.append(f"{color}╚═══════════════════════════╝{Color.RESET}")

        return ship_lines

    def render(self) -> List[str]:
        """Render tactical map with ship interiors"""
        lines = []

        # Side by side view
        if self.enemy_ship and self.show_enemy:
            # Both ships
            player_lines = self._render_ship(self.player_ship, 0, 0, False)
            enemy_lines = self._render_ship(self.enemy_ship, 35, 0, True)

            # Combine side by side
            for p_line, e_line in zip(player_lines, enemy_lines):
                combined = p_line + "  " + e_line
                lines.append(combined)

            # Add projectiles between ships
            if self.projectiles:
                proj_line = " " * 30
                for px, py, ptype, _, _ in self.projectiles:
                    if ptype == "laser":
                        proj_line = " " * 30 + f"{Color.CYAN}═══►{Color.RESET}"
                    elif ptype == "missile":
                        proj_line = " " * 30 + f"{Color.YELLOW}◆◆◆►{Color.RESET}"
                lines.append(proj_line)
        else:
            # Just player ship
            lines = self._render_ship(self.player_ship, 0, 0, False)

        # Pad to fill height
        while len(lines) < self.height - 2:
            lines.append("")

        return lines


class ViewportRenderer:
    """Renders the space viewport - stars, ships, warp effects"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.stars = self._generate_stars()
        self.warp_active = False
        self.enemy_ships = []
        self.player_speed = 0

    def _generate_stars(self) -> List[Tuple[int, int, str]]:
        """Generate random star field"""
        stars = []
        for _ in range(self.width * self.height // 20):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            char = random.choice(['.', '·', '∗', '✦', '★'])
            stars.append((x, y, char))
        return stars

    def update_stars(self, warp_speed: float = 0):
        """Update star positions for movement effect"""
        new_stars = []
        for x, y, char in self.stars:
            if warp_speed > 0:
                # Warp effect - stars streak
                x -= int(warp_speed * 2)
                if x < 0:
                    x = self.width - 1
                    y = random.randint(0, self.height - 1)
            new_stars.append((x, y, char))
        self.stars = new_stars

    def add_enemy_ship(self, x: int, y: int):
        """Add enemy ship to viewport"""
        self.enemy_ships.append((x, y))

    def clear_enemies(self):
        """Remove all enemy ships"""
        self.enemy_ships = []

    def render(self) -> List[str]:
        """Render the viewport as list of lines"""
        # Create empty grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw stars
        for x, y, char in self.stars:
            if 0 <= y < self.height and 0 <= x < self.width:
                grid[y][x] = f"{Color.GRAY}{char}{Color.RESET}"

        # Draw warp streaks if active
        if self.warp_active:
            for i in range(self.height):
                for j in range(0, self.width, 8):
                    if random.random() < 0.3:
                        streak_len = random.randint(3, 8)
                        for k in range(streak_len):
                            if j + k < self.width:
                                grid[i][j + k] = f"{Color.CYAN}═{Color.RESET}"

        # Draw enemy ships
        for ex, ey in self.enemy_ships:
            if 0 <= ey < self.height and 0 <= ex < self.width - 5:
                # Simple enemy ship
                enemy_art = [
                    f"{Color.RED}◄═╬═►{Color.RESET}",
                ]
                if ey < self.height:
                    for i, char in enumerate(enemy_art[0]):
                        if ex + i < self.width:
                            grid[ey][ex + i] = char

        # Convert grid to strings
        lines = [''.join(row) for row in grid]
        return lines


class TerminalUI:
    """Main terminal UI controller"""

    def __init__(self):
        self.width, self.height = self._get_terminal_size()

        # Calculate panel sizes (roughly equal thirds)
        self.viewport_height = max(8, self.height // 3)
        self.tactical_height = max(8, self.height // 3)
        self.terminal_height = self.height - self.viewport_height - self.tactical_height - 6

        self.viewport = ViewportRenderer(self.width - 4, self.viewport_height - 2)
        self.tactical_map = TacticalMap(self.width - 4, self.tactical_height - 2)

        # Command-line style output (integrated prompt and history)
        self.command_history = []
        self.max_history_lines = self.terminal_height - 1

    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal dimensions"""
        size = shutil.get_terminal_size((80, 24))
        return size.columns, size.lines

    def clear(self):
        """Clear screen"""
        print(Color.CLEAR + Color.HOME, end='')
        sys.stdout.flush()

    def add_output(self, text: str):
        """Add text to command history"""
        lines = text.split('\n')
        for line in lines:
            self.command_history.append(line)

        # Keep only recent lines
        if len(self.command_history) > self.max_history_lines:
            self.command_history = self.command_history[-self.max_history_lines:]

    def render_frame(self, ship_name: str = "KESTREL", hull: int = 30, shields: int = 4):
        """Render complete UI frame"""
        self.clear()

        # Top LCARS bar
        self._render_lcars_header(ship_name, hull, shields)

        # Viewport section (top third)
        self._render_viewport()

        # Tactical map section (middle third)
        self._render_tactical_map()

        # Terminal section (bottom third)
        self._render_terminal()

        sys.stdout.flush()

    def _render_lcars_header(self, ship_name: str, hull: int, shields: int):
        """Render LCARS-style header bar"""
        bar = f"{Color.ORANGE}{'═' * self.width}{Color.RESET}"
        print(bar)

        # Ship info
        hull_bar = f"{Color.GREEN}{'█' * (hull // 3)}{Color.DARK_GRAY}{'░' * (10 - hull // 3)}{Color.RESET}"
        shield_bar = f"{Color.BLUE}{'█' * shields}{Color.DARK_GRAY}{'░' * (4 - shields)}{Color.RESET}"

        status = f"{Color.ORANGE}╡{Color.RESET} {Color.YELLOW}{ship_name}{Color.RESET} {Color.ORANGE}╞═{Color.RESET} HULL:[{hull_bar}] SHIELD:[{shield_bar}] {Color.ORANGE}{'═' * (self.width - 50)}{Color.RESET}"
        print(status)
        print(bar)

    def _render_viewport(self):
        """Render space viewport"""
        # Viewport border
        print(f"{Color.PURPLE}╔{'═' * (self.width - 2)}╗{Color.RESET}")

        viewport_lines = self.viewport.render()
        for line in viewport_lines:
            print(f"{Color.PURPLE}║{Color.RESET} {line:<{self.width - 4}} {Color.PURPLE}║{Color.RESET}")

        print(f"{Color.PURPLE}╚{'═' * (self.width - 2)}╝{Color.RESET}")

    def _render_tactical_map(self):
        """Render tactical map section"""
        # Tactical border
        print(f"{Color.PINK}╔{'═' * (self.width - 2)}╗{Color.RESET}")
        print(f"{Color.PINK}║{Color.RESET} {Color.YELLOW}TACTICAL DISPLAY{Color.RESET}{' ' * (self.width - 20)} {Color.PINK}║{Color.RESET}")
        print(f"{Color.PINK}╠{'═' * (self.width - 2)}╣{Color.RESET}")

        # Render tactical map
        tactical_lines = self.tactical_map.render()
        for line in tactical_lines:
            print(f"{Color.PINK}║{Color.RESET} {line:<{self.width - 4}} {Color.PINK}║{Color.RESET}")

        print(f"{Color.PINK}╚{'═' * (self.width - 2)}╝{Color.RESET}")

    def _render_terminal(self):
        """Render classic command-line terminal section"""
        # Terminal border
        print(f"{Color.BLUE}╔{'═' * (self.width - 2)}╗{Color.RESET}")
        print(f"{Color.BLUE}║{Color.RESET} {Color.CYAN}COMMAND TERMINAL{Color.RESET}{' ' * (self.width - 20)} {Color.BLUE}║{Color.RESET}")
        print(f"{Color.BLUE}╠{'═' * (self.width - 2)}╣{Color.RESET}")

        # Show command history (scrolling output)
        display_lines = self.command_history[-self.max_history_lines:]
        for line in display_lines:
            # Truncate if too long
            if len(line) > self.width - 4:
                line = line[:self.width - 7] + "..."
            print(f"{Color.BLUE}║{Color.RESET} {line:<{self.width - 4}} {Color.BLUE}║{Color.RESET}")

        # Fill empty lines
        for _ in range(self.max_history_lines - len(display_lines)):
            print(f"{Color.BLUE}║{Color.RESET} {' ' * (self.width - 4)} {Color.BLUE}║{Color.RESET}")

        # Integrated prompt at bottom
        print(f"{Color.BLUE}║{Color.RESET} {Color.YELLOW}${Color.RESET} ", end='')
        sys.stdout.flush()

    def get_command(self) -> str:
        """Get command input from user (classic terminal style)"""
        try:
            cmd = input()
            # Close terminal box
            print(f"{Color.BLUE}╚{'═' * (self.width - 2)}╝{Color.RESET}")
            # Add command to history
            if cmd.strip():
                self.add_output(f"{Color.YELLOW}$ {cmd}{Color.RESET}")
            return cmd.strip()
        except (EOFError, KeyboardInterrupt):
            print(f"{Color.BLUE}╚{'═' * (self.width - 2)}╝{Color.RESET}")
            return "exit"

    def set_warp(self, active: bool):
        """Toggle warp effect in viewport"""
        self.viewport.warp_active = active

    def update_viewport(self, warp_speed: float = 0):
        """Update viewport animation"""
        self.viewport.update_stars(warp_speed)

    def set_enemy_ship(self, enemy_layout: ShipLayout):
        """Set enemy ship on tactical map"""
        self.tactical_map.set_enemy_ship(enemy_layout)

    def clear_enemy(self):
        """Clear enemy from tactical map"""
        self.tactical_map.clear_enemy()

    def fire_weapon(self, weapon_type: str = "laser"):
        """Fire weapon from player ship"""
        self.tactical_map.add_projectile(0, 0, weapon_type, (1, 0))

    def update_tactical(self, dt: float = 0.1):
        """Update tactical map animations"""
        self.tactical_map.update(dt)

    def set_player_ship_name(self, name: str):
        """Update player ship name in tactical display"""
        self.tactical_map.player_ship.name = name


class SimpleTextEditor:
    """Simple in-game text editor for editing files"""

    def __init__(self):
        self.width, self.height = shutil.get_terminal_size((80, 24))
        self.lines = []
        self.cursor_line = 0
        self.scroll_offset = 0
        self.modified = False
        self.filename = ""

    def load_file(self, filename: str):
        """Load file into editor"""
        self.filename = filename
        try:
            with open(filename, 'r') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
        except FileNotFoundError:
            self.lines = [""]
        except Exception as e:
            self.lines = [f"Error loading file: {e}"]

    def save_file(self):
        """Save current buffer to file"""
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))
            self.modified = False
            return True
        except Exception as e:
            return False

    def render(self):
        """Render editor screen"""
        print(Color.CLEAR + Color.HOME, end='')

        # Header
        modified_indicator = "*" if self.modified else " "
        header = f" EDITOR: {self.filename}{modified_indicator} "
        print(f"{Color.ORANGE}{'═' * self.width}{Color.RESET}")
        print(f"{Color.ORANGE}║{Color.RESET}{header:^{self.width - 2}}{Color.ORANGE}║{Color.RESET}")
        print(f"{Color.ORANGE}{'═' * self.width}{Color.RESET}")

        # Text area
        visible_height = self.height - 6
        for i in range(visible_height):
            line_num = self.scroll_offset + i
            if line_num < len(self.lines):
                line = self.lines[line_num]
                # Highlight current line
                if line_num == self.cursor_line:
                    print(f"{Color.CYAN}>{Color.RESET} {line_num + 1:3} {Color.BOLD}{line}{Color.RESET}")
                else:
                    print(f"  {line_num + 1:3} {line}")
            else:
                print(f"{Color.DARK_GRAY}  ~{Color.RESET}")

        # Footer with commands
        print(f"{Color.ORANGE}{'═' * self.width}{Color.RESET}")
        footer = "Ctrl+S: Save | Ctrl+Q: Quit | Ctrl+N: New line | Ctrl+D: Delete line"
        print(f"{Color.YELLOW}{footer}{Color.RESET}")

        sys.stdout.flush()

    def edit_line(self):
        """Edit the current line"""
        current_text = self.lines[self.cursor_line] if self.cursor_line < len(self.lines) else ""
        print(f"\n{Color.GREEN}Edit line {self.cursor_line + 1}:{Color.RESET} ", end='')
        try:
            new_text = input()
            if self.cursor_line < len(self.lines):
                self.lines[self.cursor_line] = new_text
            self.modified = True
        except (EOFError, KeyboardInterrupt):
            pass

    def run(self):
        """Run editor main loop"""
        while True:
            self.render()

            print(f"\n{Color.CYAN}Command (e=edit, j=down, k=up, n=new, d=delete, s=save, q=quit):{Color.RESET} ", end='')

            try:
                cmd = input().strip().lower()

                if cmd == 'q':
                    if self.modified:
                        print(f"{Color.YELLOW}Save changes? (y/n):{Color.RESET} ", end='')
                        save = input().strip().lower()
                        if save == 'y':
                            self.save_file()
                    break
                elif cmd == 's':
                    if self.save_file():
                        print(f"{Color.GREEN}File saved!{Color.RESET}")
                    else:
                        print(f"{Color.RED}Error saving file!{Color.RESET}")
                    import time
                    time.sleep(1)
                elif cmd == 'e':
                    self.edit_line()
                elif cmd == 'j':
                    if self.cursor_line < len(self.lines) - 1:
                        self.cursor_line += 1
                        # Scroll if needed
                        if self.cursor_line >= self.scroll_offset + (self.height - 6):
                            self.scroll_offset += 1
                elif cmd == 'k':
                    if self.cursor_line > 0:
                        self.cursor_line -= 1
                        # Scroll if needed
                        if self.cursor_line < self.scroll_offset:
                            self.scroll_offset -= 1
                elif cmd == 'n':
                    self.lines.insert(self.cursor_line + 1, "")
                    self.cursor_line += 1
                    self.modified = True
                elif cmd == 'd':
                    if len(self.lines) > 1:
                        del self.lines[self.cursor_line]
                        if self.cursor_line >= len(self.lines):
                            self.cursor_line = len(self.lines) - 1
                        self.modified = True

            except (EOFError, KeyboardInterrupt):
                break


def edit_file(filename: str):
    """Edit a file using the simple text editor"""
    editor = SimpleTextEditor()
    editor.load_file(filename)
    editor.run()


# Convenience function for quick testing
def demo():
    """Demo the UI system"""
    ui = TerminalUI()

    ui.add_output("System online. Welcome aboard the Kestrel.")
    ui.add_output("All systems nominal.")
    ui.add_output(f"{Color.GREEN}✓{Color.RESET} Shields: ONLINE")
    ui.add_output(f"{Color.GREEN}✓{Color.RESET} Weapons: ONLINE")
    ui.add_output(f"{Color.YELLOW}⚠{Color.RESET} Reactor at 70% capacity")
    ui.add_output("")
    ui.add_output("Commands: fire, warp, status, edit, scan, quit")

    # Add enemy ship to tactical map
    enemy = ShipLayout("PIRATE CRUISER")
    ui.set_enemy_ship(enemy)

    ui.render_frame("KESTREL", 28, 3)

    while True:
        cmd = ui.get_command()

        if cmd.lower() in ['exit', 'quit', 'q']:
            break

        if 'warp' in cmd.lower():
            ui.set_warp(True)
            ui.add_output(f"{Color.CYAN}⚡ Engaging warp drive!{Color.RESET}")
        elif 'status' in cmd.lower():
            ui.add_output("=== SHIP STATUS ===")
            ui.add_output("Hull: 28/30")
            ui.add_output("Shields: 3/4")
            ui.add_output("Power: 7/8")
        elif 'fire' in cmd.lower():
            ui.fire_weapon("laser")
            ui.add_output(f"{Color.RED}⚡ Weapons firing!{Color.RESET}")
        elif 'edit' in cmd.lower():
            parts = cmd.split()
            filename = parts[1] if len(parts) > 1 else "test.txt"
            ui.add_output(f"Opening editor for {filename}...")
            edit_file(filename)
            ui.add_output(f"Editor closed. File saved: {filename}")
        else:
            ui.add_output(f"Unknown command: {cmd}")

        ui.update_viewport(2.0 if ui.viewport.warp_active else 0)
        ui.update_tactical()
        ui.render_frame("KESTREL", 28, 3)


if __name__ == '__main__':
    demo()

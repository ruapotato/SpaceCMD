#!/usr/bin/env python3
"""
LCARS-style Terminal UI System
Three-panel interface: Viewport (top), Output (middle), Command (bottom)
"""

import sys
import os
import random
import shutil
from typing import List, Tuple


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

        # Calculate panel sizes
        self.viewport_height = max(8, self.height // 3)
        self.output_height = max(10, self.height - self.viewport_height - 8)
        self.command_height = 4

        self.viewport = ViewportRenderer(self.width - 4, self.viewport_height - 2)
        self.output_buffer = []
        self.max_output_lines = self.output_height - 2

    def _get_terminal_size(self) -> Tuple[int, int]:
        """Get terminal dimensions"""
        size = shutil.get_terminal_size((80, 24))
        return size.columns, size.lines

    def clear(self):
        """Clear screen"""
        print(Color.CLEAR + Color.HOME, end='')
        sys.stdout.flush()

    def add_output(self, text: str):
        """Add text to output buffer"""
        lines = text.split('\n')
        for line in lines:
            self.output_buffer.append(line)

        # Keep only recent lines
        if len(self.output_buffer) > self.max_output_lines:
            self.output_buffer = self.output_buffer[-self.max_output_lines:]

    def render_frame(self, ship_name: str = "KESTREL", hull: int = 30, shields: int = 4):
        """Render complete UI frame"""
        self.clear()

        # Top LCARS bar
        self._render_lcars_header(ship_name, hull, shields)

        # Viewport section
        self._render_viewport()

        # Output section
        self._render_output()

        # Command section
        self._render_command()

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

    def _render_output(self):
        """Render command output section"""
        # Output border
        print(f"{Color.BLUE}╔{'═' * (self.width - 2)}╗{Color.RESET}")
        print(f"{Color.BLUE}║{Color.RESET} {Color.CYAN}COMMAND OUTPUT{Color.RESET}{' ' * (self.width - 18)} {Color.BLUE}║{Color.RESET}")
        print(f"{Color.BLUE}╠{'═' * (self.width - 2)}╣{Color.RESET}")

        # Show recent output
        display_lines = self.output_buffer[-self.max_output_lines:]
        for line in display_lines:
            # Truncate if too long
            if len(line) > self.width - 4:
                line = line[:self.width - 7] + "..."
            print(f"{Color.BLUE}║{Color.RESET} {line:<{self.width - 4}} {Color.BLUE}║{Color.RESET}")

        # Fill empty lines
        for _ in range(self.max_output_lines - len(display_lines)):
            print(f"{Color.BLUE}║{Color.RESET} {' ' * (self.width - 4)} {Color.BLUE}║{Color.RESET}")

        print(f"{Color.BLUE}╚{'═' * (self.width - 2)}╝{Color.RESET}")

    def _render_command(self):
        """Render command input section"""
        print(f"{Color.ORANGE}╔{'═' * (self.width - 2)}╗{Color.RESET}")
        print(f"{Color.ORANGE}║{Color.RESET} {Color.YELLOW}>{Color.RESET} ", end='')
        sys.stdout.flush()

    def get_command(self) -> str:
        """Get command input from user"""
        try:
            cmd = input()
            # Close command box
            print(f"\r{' ' * self.width}\r{Color.ORANGE}╚{'═' * (self.width - 2)}╝{Color.RESET}")
            return cmd.strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"

    def set_warp(self, active: bool):
        """Toggle warp effect in viewport"""
        self.viewport.warp_active = active

    def update_viewport(self, warp_speed: float = 0):
        """Update viewport animation"""
        self.viewport.update_stars(warp_speed)

    def add_enemy(self, x: int, y: int):
        """Add enemy to viewport"""
        self.viewport.add_enemy_ship(x, y)

    def clear_enemies(self):
        """Clear enemies from viewport"""
        self.viewport.clear_enemies()


# Convenience function for quick testing
def demo():
    """Demo the UI system"""
    ui = TerminalUI()

    ui.add_output("System online. Welcome aboard the Kestrel.")
    ui.add_output("All systems nominal.")
    ui.add_output(f"{Color.GREEN}✓{Color.RESET} Shields: ONLINE")
    ui.add_output(f"{Color.GREEN}✓{Color.RESET} Weapons: ONLINE")
    ui.add_output(f"{Color.YELLOW}⚠{Color.RESET} Reactor at 70% capacity")

    # Add enemy ship
    ui.add_enemy(ui.width - 20, ui.viewport_height // 2)

    ui.render_frame("KESTREL", 28, 3)

    while True:
        cmd = ui.get_command()

        if cmd.lower() in ['exit', 'quit', 'q']:
            break

        ui.add_output(f"{Color.YELLOW}> {cmd}{Color.RESET}")

        if 'warp' in cmd.lower():
            ui.set_warp(True)
            ui.add_output(f"{Color.CYAN}⚡ Engaging warp drive!{Color.RESET}")
        elif 'status' in cmd.lower():
            ui.add_output("=== SHIP STATUS ===")
            ui.add_output("Hull: 28/30")
            ui.add_output("Shields: 3/4")
            ui.add_output("Power: 7/8")
        elif 'fire' in cmd.lower():
            ui.add_output(f"{Color.RED}🔴 Weapons firing!{Color.RESET}")
        else:
            ui.add_output(f"Unknown command: {cmd}")

        ui.update_viewport(2.0 if ui.viewport.warp_active else 0)
        ui.render_frame("KESTREL", 28, 3)


if __name__ == '__main__':
    demo()

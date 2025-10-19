"""
spacecmd - ASCII/Unicode Rendering System

Beautiful terminal graphics for ship visualization.
"""

from typing import List, Dict, Tuple, Optional
from .ship import Ship, Room, Crew, SystemType, RoomState


class Color:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """True color (24-bit)"""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """True color background"""
        return f"\033[48;2;{r};{g};{b}m"


class Icons:
    """Unicode icons for ship systems and states"""
    # Crew
    CREW = "👤"
    CREW_DEAD = "💀"

    # Systems
    HELM = "🎯"
    SHIELDS = "🛡️"
    WEAPONS_LASER = "🔴"
    WEAPONS_MISSILE = "🚀"
    ENGINES = "⚙️"
    OXYGEN = "💨"
    REACTOR = "⚡"
    MEDBAY = "💉"
    SENSORS = "📡"
    TELEPORTER = "🌀"
    CLOAKING = "▓"
    DRONE = "🤖"
    FIRE = "🔥"
    WARNING = "⚠️"
    EXPLOSION = "💥"

    # Progress/bars
    FULL_BLOCK = "█"
    LIGHT_SHADE = "░"
    MEDIUM_SHADE = "▒"
    DARK_SHADE = "▓"

    # Box drawing
    H_LINE = "─"
    V_LINE = "│"
    TL_CORNER = "┌"
    TR_CORNER = "┐"
    BL_CORNER = "└"
    BR_CORNER = "┘"
    T_DOWN = "┬"
    T_UP = "┴"
    T_RIGHT = "├"
    T_LEFT = "┤"
    CROSS = "┼"

    # Heavy box drawing
    H_HEAVY = "━"
    V_HEAVY = "┃"
    TL_HEAVY = "┏"
    TR_HEAVY = "┓"
    BL_HEAVY = "┗"
    BR_HEAVY = "┛"

    # Double box drawing
    H_DOUBLE = "═"
    V_DOUBLE = "║"
    TL_DOUBLE = "╔"
    TR_DOUBLE = "╗"
    BL_DOUBLE = "╚"
    BR_DOUBLE = "╝"
    T_DOWN_DOUBLE = "╦"
    T_UP_DOUBLE = "╩"
    T_RIGHT_DOUBLE = "╠"
    T_LEFT_DOUBLE = "╣"


class ShipRenderer:
    """
    Renders ships as ASCII/Unicode art.
    """

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def render_ship(self, ship: Ship, width: int = 60) -> List[str]:
        """
        Render a ship as ASCII art.
        Returns a list of strings (lines).
        """
        lines = []

        # Header
        lines.extend(self._render_header(ship, width))

        # Status bars
        lines.extend(self._render_status_bars(ship, width))

        # Ship layout
        lines.extend(self._render_ship_layout(ship))

        # Weapons status
        lines.extend(self._render_weapons_status(ship, width))

        return lines

    def _render_header(self, ship: Ship, width: int) -> List[str]:
        """Render ship name header"""
        title = f"  {ship.name.upper()} - {ship.ship_class.upper()}  "
        padding = (width - len(title)) // 2

        lines = []
        lines.append(Icons.TL_DOUBLE + Icons.H_DOUBLE * (width - 2) + Icons.TR_DOUBLE)
        lines.append(Icons.V_DOUBLE + " " * padding + title + " " * (width - len(title) - padding - 2) + Icons.V_DOUBLE)
        lines.append(Icons.BL_DOUBLE + Icons.H_DOUBLE * (width - 2) + Icons.BR_DOUBLE)

        return lines

    def _render_status_bars(self, ship: Ship, width: int) -> List[str]:
        """Render status bars (hull, shields, oxygen, power)"""
        lines = []

        # Calculate bar width
        bar_width = 12

        # Hull
        hull_pct = ship.hull / ship.hull_max
        hull_bar = self._render_progress_bar(hull_pct, bar_width)
        hull_color = self._get_health_color(hull_pct)
        hull_text = f"HULL:    {hull_bar} {ship.hull}/{ship.hull_max}"

        # Shields
        if ship.shields_max > 0:
            shield_pct = ship.shields / ship.shields_max
            shield_bar = self._render_progress_bar(shield_pct, bar_width)
            shield_text = f"SHIELDS: {shield_bar} {int(ship.shields)}/{ship.shields_max}"
        else:
            shield_text = f"SHIELDS: [NO SHIELDS]"

        # Power
        power_used = ship.reactor_power - ship.power_available
        power_icons = Icons.REACTOR * power_used + Icons.LIGHT_SHADE * ship.power_available
        power_text = f"POWER:   {power_icons} {power_used}/{ship.reactor_power}"

        # Fuel
        fuel_text = f"FUEL:    {ship.fuel}"

        lines.append("")
        lines.append(f"  {hull_text}")
        lines.append(f"  {shield_text}")
        lines.append(f"  {power_text}")
        lines.append(f"  {fuel_text}")
        lines.append("")

        return lines

    def _render_progress_bar(self, percent: float, width: int = 12) -> str:
        """Render a progress bar"""
        filled = int(percent * width)
        empty = width - filled
        return f"[{Icons.FULL_BLOCK * filled}{Icons.LIGHT_SHADE * empty}]"

    def _get_health_color(self, percent: float) -> str:
        """Get color based on health percentage"""
        if not self.use_color:
            return ""

        if percent > 0.7:
            return Color.GREEN
        elif percent > 0.3:
            return Color.YELLOW
        else:
            return Color.RED

    def _render_ship_layout(self, ship: Ship) -> List[str]:
        """
        Render the ship's room layout.
        This is a simple grid-based rendering.
        """
        lines = []

        # For now, render a simple list of rooms
        # Later we'll do proper 2D grid rendering
        lines.append("  SHIP LAYOUT:")
        lines.append("")

        for room_name, room in ship.rooms.items():
            lines.append(self._render_room_line(room))

        return lines

    def _render_room_line(self, room: Room) -> str:
        """Render a single room as a line"""
        # Room name
        name_str = f"  {room.name:12}"

        # System icon
        icon = self._get_system_icon(room.system_type)

        # Health bar
        health_bar = self._render_progress_bar(room.health, 8)

        # Power
        power_str = Icons.REACTOR * room.power_allocated + Icons.LIGHT_SHADE * (room.max_power - room.power_allocated)

        # Crew
        crew_str = Icons.CREW * len(room.crew) if room.crew else "   "

        # Status
        status = ""
        if room.on_fire:
            status = Icons.FIRE
        elif room.breached:
            status = Icons.WARNING
        elif room.oxygen_level < 0.3:
            status = Icons.WARNING

        return f"{name_str} {icon} {health_bar} {power_str} {crew_str} {status}"

    def _get_system_icon(self, system_type: SystemType) -> str:
        """Get icon for system type"""
        icons = {
            SystemType.HELM: Icons.HELM,
            SystemType.SHIELDS: Icons.SHIELDS,
            SystemType.WEAPONS: Icons.WEAPONS_LASER,
            SystemType.ENGINES: Icons.ENGINES,
            SystemType.OXYGEN: Icons.OXYGEN,
            SystemType.REACTOR: Icons.REACTOR,
            SystemType.MEDBAY: Icons.MEDBAY,
            SystemType.SENSORS: Icons.SENSORS,
            SystemType.TELEPORTER: Icons.TELEPORTER,
            SystemType.CLOAKING: Icons.CLOAKING,
            SystemType.DRONE_BAY: Icons.DRONE,
            SystemType.NONE: " ",
        }
        return icons.get(system_type, "?")

    def _render_weapons_status(self, ship: Ship, width: int) -> List[str]:
        """Render weapons charging status"""
        lines = []
        lines.append("")
        lines.append("  WEAPONS:")

        # TODO: Implement when we have weapon system
        lines.append("    No weapons installed")

        return lines

    def render_to_terminal(self, ship: Ship):
        """Render ship directly to terminal"""
        lines = self.render_ship(ship)
        print("\n".join(lines))

    def clear_screen(self):
        """Clear terminal screen"""
        import os
        os.system('clear' if os.name != 'nt' else 'cls')


def render_box(lines: List[str], title: str = "") -> List[str]:
    """
    Wrap lines in a box with optional title.
    """
    if not lines:
        return []

    width = max(len(line) for line in lines) + 2

    result = []

    # Top
    if title:
        title_str = f" {title} "
        padding = (width - len(title_str)) // 2
        top = Icons.TL_DOUBLE + Icons.H_DOUBLE * padding + title_str + Icons.H_DOUBLE * (width - padding - len(title_str)) + Icons.TR_DOUBLE
    else:
        top = Icons.TL_DOUBLE + Icons.H_DOUBLE * width + Icons.TR_DOUBLE

    result.append(top)

    # Content
    for line in lines:
        padded = line + " " * (width - len(line))
        result.append(Icons.V_DOUBLE + padded + Icons.V_DOUBLE)

    # Bottom
    result.append(Icons.BL_DOUBLE + Icons.H_DOUBLE * width + Icons.BR_DOUBLE)

    return result

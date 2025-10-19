"""
Pygame-based Desktop Environment for SpaceCMD

A virtual desktop with window management, terminals, and tactical displays.
LCARS + GNOME 2 aesthetic.
"""

from .desktop import Desktop
from .window import Window
from .terminal_widget import TerminalWidget
from .tactical_widget import TacticalWidget
from .topbar import TopBar

__all__ = ['Desktop', 'Window', 'TerminalWidget', 'TacticalWidget', 'TopBar']

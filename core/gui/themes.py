"""
Theme definitions for SpaceCMD Desktop Environment

Combines LCARS (Star Trek) aesthetic with GNOME 2 window manager style.
"""

import pygame

# LCARS Color Palette
LCARS_ORANGE = (255, 153, 0)      # Primary accent
LCARS_PINK = (204, 153, 255)      # Secondary accent
LCARS_BLUE = (153, 204, 255)      # Tertiary accent
LCARS_PURPLE = (153, 102, 204)    # Window borders
LCARS_YELLOW = (255, 204, 0)      # Highlights
LCARS_RED = (255, 68, 68)         # Alerts/Close button
LCARS_PEACH = (255, 136, 119)     # Warm accent

# GNOME 2 inspired grays
GNOME_DARK_GRAY = (60, 60, 60)    # Titlebar background
GNOME_MID_GRAY = (90, 90, 90)     # Inactive windows
GNOME_LIGHT_GRAY = (180, 180, 180)# Text
GNOME_BORDER = (40, 40, 40)       # Window borders

# Space/Terminal colors
SPACE_BLACK = (0, 0, 0)           # Deep space
TERMINAL_BG = (10, 10, 30)        # Terminal background (dark blue-black)
TERMINAL_FG = (200, 255, 200)     # Terminal text (green tint)
TERMINAL_CURSOR = (0, 255, 100)   # Cursor color

# Starfield
STAR_WHITE = (255, 255, 255)
STAR_BLUE = (180, 200, 255)
STAR_YELLOW = (255, 255, 200)

# System status colors
STATUS_ONLINE = (0, 255, 0)       # Green
STATUS_DAMAGED = (255, 165, 0)    # Orange
STATUS_OFFLINE = (128, 128, 128)  # Gray
STATUS_CRITICAL = (255, 0, 0)     # Red

# Transparency
ALPHA_FULL = 255
ALPHA_WINDOW = 240
ALPHA_OVERLAY = 180


class Theme:
    """Theme configuration"""

    # Window styling
    WINDOW_TITLEBAR_HEIGHT = 28
    WINDOW_BORDER_WIDTH = 2
    WINDOW_BUTTON_SIZE = 20
    WINDOW_PADDING = 4

    # Taskbar
    TASKBAR_HEIGHT = 32
    TASKBAR_BUTTON_WIDTH = 150

    # Fonts (will be initialized at runtime)
    FONT_TITLE = None       # Window titles
    FONT_TERMINAL = None    # Terminal text (monospace)
    FONT_UI = None          # UI elements
    FONT_SMALL = None       # Small text

    # Window colors
    TITLEBAR_ACTIVE = GNOME_DARK_GRAY
    TITLEBAR_INACTIVE = GNOME_MID_GRAY
    WINDOW_BG = TERMINAL_BG
    WINDOW_BORDER = LCARS_PURPLE

    # Button colors
    BUTTON_CLOSE = LCARS_RED
    BUTTON_MINIMIZE = LCARS_YELLOW
    BUTTON_MAXIMIZE = LCARS_BLUE

    # Desktop
    DESKTOP_BG = SPACE_BLACK

    @staticmethod
    def init_fonts():
        """Initialize fonts (call after pygame.init())"""
        pygame.font.init()

        # Try to find a good monospace font
        monospace_fonts = [
            'DejaVuSansMono',
            'LiberationMono',
            'UbuntuMono',
            'Courier New',
            'Courier',
            'monospace'
        ]

        mono_font = None
        for font_name in monospace_fonts:
            if pygame.font.match_font(font_name):
                mono_font = font_name
                break

        # Fallback to pygame default monospace
        if not mono_font:
            mono_font = pygame.font.get_default_font()

        Theme.FONT_TERMINAL = pygame.font.SysFont(mono_font, 14)
        Theme.FONT_TITLE = pygame.font.SysFont('sans-serif', 12, bold=True)
        Theme.FONT_UI = pygame.font.SysFont('sans-serif', 11)
        Theme.FONT_SMALL = pygame.font.SysFont('sans-serif', 10)


def draw_rounded_rect(surface, color, rect, radius=5):
    """Draw a rounded rectangle"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_lcars_button(surface, rect, color, text="", font=None):
    """Draw an LCARS-style rounded button"""
    # LCARS buttons are rounded rectangles
    draw_rounded_rect(surface, color, rect, radius=rect.height // 2)

    # Add text if provided
    if text and font:
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

"""
Desktop Environment and Window Manager for SpaceCMD

Manages multiple windows, taskbar, and desktop background.
LCARS + GNOME 2 aesthetic with animated starfield background.
"""

import pygame
import random
from typing import List, Optional
from .window import Window, WindowState
from .themes import Theme, draw_rounded_rect
from .topbar import TopBar


class Star:
    """A single star in the background"""
    def __init__(self, x, y, z, screen_width, screen_height):
        self.x = x
        self.y = y
        self.z = z  # Depth (1.0 = far, 0.1 = close)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.brightness = random.randint(100, 255)
        self.color_tint = random.choice(['white', 'blue', 'yellow'])

    def update(self, speed=0.5):
        """Move star toward viewer"""
        self.z -= speed * 0.01
        if self.z <= 0:
            # Reset to far away
            self.z = 1.0
            self.x = random.uniform(-1, 1)
            self.y = random.uniform(-1, 1)

    def get_screen_pos(self):
        """Get screen position based on perspective"""
        # Simple perspective projection
        scale = (1.0 - self.z) * 0.5
        screen_x = int((self.x / self.z) * self.screen_width / 2 + self.screen_width / 2)
        screen_y = int((self.y / self.z) * self.screen_height / 2 + self.screen_height / 2)
        size = max(1, int(3 * (1.0 - self.z)))
        return screen_x, screen_y, size

    def get_color(self):
        """Get star color based on brightness and tint"""
        b = self.brightness
        if self.color_tint == 'blue':
            return (int(b * 0.7), int(b * 0.8), b)
        elif self.color_tint == 'yellow':
            return (b, b, int(b * 0.8))
        else:  # white
            return (b, b, b)


class Taskbar:
    """GNOME 2 style taskbar"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rect = pygame.Rect(
            0,
            screen_height - Theme.TASKBAR_HEIGHT,
            screen_width,
            Theme.TASKBAR_HEIGHT
        )
        self.buttons = []  # List of (window, rect) tuples
        self.menu_button = pygame.Rect(4, self.rect.y + 4, 100, Theme.TASKBAR_HEIGHT - 8)

    def update_buttons(self, windows):
        """Update taskbar buttons based on open windows"""
        self.buttons = []
        x = self.menu_button.right + 8

        for window in windows:
            if window.visible or window.state == WindowState.MINIMIZED:
                button_rect = pygame.Rect(
                    x,
                    self.rect.y + 4,
                    Theme.TASKBAR_BUTTON_WIDTH,
                    Theme.TASKBAR_HEIGHT - 8
                )
                self.buttons.append((window, button_rect))
                x += Theme.TASKBAR_BUTTON_WIDTH + 4

    def handle_event(self, event, mouse_pos):
        """Handle taskbar events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check menu button
            if self.menu_button.collidepoint(mouse_pos):
                return ('menu', None)

            # Check window buttons
            for window, button_rect in self.buttons:
                if button_rect.collidepoint(mouse_pos):
                    if window.state == WindowState.MINIMIZED:
                        window.restore()
                    return ('focus_window', window)

        return (None, None)

    def render(self, surface):
        """Render taskbar"""
        # Draw taskbar background
        pygame.draw.rect(surface, Theme.TITLEBAR_ACTIVE, self.rect)

        # Draw top border (LCARS accent)
        pygame.draw.line(
            surface,
            Theme.WINDOW_BORDER,
            (0, self.rect.y),
            (self.screen_width, self.rect.y),
            2
        )

        # Draw menu button (LCARS style)
        draw_rounded_rect(surface, (255, 153, 0), self.menu_button, radius=4)
        if Theme.FONT_UI:
            menu_text = Theme.FONT_UI.render("APPS", True, (0, 0, 0))
            text_rect = menu_text.get_rect(center=self.menu_button.center)
            surface.blit(menu_text, text_rect)

        # Draw window buttons
        for window, button_rect in self.buttons:
            # Button color based on state
            if window.focused and window.state != WindowState.MINIMIZED:
                color = (120, 120, 120)
            elif window.state == WindowState.MINIMIZED:
                color = (70, 70, 70)
            else:
                color = (90, 90, 90)

            pygame.draw.rect(surface, color, button_rect, border_radius=3)

            # Window title
            if Theme.FONT_UI:
                # Truncate title if needed
                title = window.title
                if len(title) > 20:
                    title = title[:17] + "..."

                title_surface = Theme.FONT_UI.render(title, True, (255, 255, 255))
                title_rect = title_surface.get_rect(center=button_rect.center)
                surface.blit(title_surface, title_rect)


class Desktop:
    """
    Main desktop environment with window management.

    Features:
    - Multiple window management with z-order
    - Animated starfield background
    - Taskbar with window buttons
    - Focus management
    - LCARS + GNOME 2 styling
    """

    def __init__(self, width=1024, height=768, fullscreen=False):
        pygame.init()
        Theme.init_fonts()

        self.width = width
        self.height = height

        # Create display
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("SpaceCMD Desktop")

        # Window management
        self.windows: List[Window] = []
        self.focused_window: Optional[Window] = None

        # Desktop elements
        self.topbar = None  # Will be set when ship_os is available
        self.taskbar = Taskbar(width, height)

        # Starfield background
        self.stars = self._create_starfield(200)
        self.warp_speed = 0.5  # Default speed

        # FPS and timing
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60

        # Menu state
        self.menu_open = False
        self.menu_rect = pygame.Rect(4, height - Theme.TASKBAR_HEIGHT - 280, 180, 280)

        # ShipOS reference (will be set by play.py)
        self.ship_os = None

    def _create_starfield(self, count):
        """Create starfield with random stars"""
        stars = []
        for _ in range(count):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            z = random.uniform(0.1, 1.0)
            stars.append(Star(x, y, z, self.width, self.height))
        return stars

    def set_ship_os(self, ship_os):
        """
        Set the ShipOS instance and create top bar.

        Args:
            ship_os: ShipOS instance
        """
        self.ship_os = ship_os
        self.topbar = TopBar(self.width, self.height, ship_os)

    def add_window(self, window: Window):
        """Add a window to the desktop"""
        self.windows.append(window)
        self.focus_window(window)

    def remove_window(self, window: Window):
        """Remove a window from the desktop"""
        if window in self.windows:
            self.windows.remove(window)
            if self.focused_window == window:
                self.focused_window = None
                if self.windows:
                    self.focus_window(self.windows[-1])

    def focus_window(self, window: Window):
        """Bring window to front and focus it"""
        if window in self.windows:
            # Unfocus all windows
            for w in self.windows:
                w.focused = False

            # Move to top of z-order
            self.windows.remove(window)
            self.windows.append(window)

            # Focus the window
            window.focused = True
            self.focused_window = window

    def create_terminal_window(self, title="Terminal", x=100, y=100):
        """
        Create a new terminal window.

        Returns:
            Window: The created window
        """
        from .terminal_widget import TerminalWidget

        terminal = TerminalWidget(600, 400)
        window = Window(title, x, y, 600, 400, terminal)
        self.add_window(window)
        return window

    def create_tactical_window(self, title="Tactical Display", x=200, y=50):
        """
        Create a tactical display window.

        Returns:
            Window: The created window
        """
        from .tactical_widget import TacticalWidget

        # Make tactical display much larger and more impressive!
        tactical = TacticalWidget(900, 650)
        window = Window(title, x, y, 900, 650, tactical)
        self.add_window(window)
        return window

    def create_file_browser_window(self, title="Files", x=150, y=100):
        """
        Create a file browser window.

        Returns:
            Window: The created window
        """
        from .file_browser import FileBrowserWidget
        from .text_editor import TextEditorWidget

        if not self.ship_os:
            return None

        browser = FileBrowserWidget(500, 400, self.ship_os)
        window = Window(title, x, y, 500, 400, browser)

        # Set callback to open files in text editor
        def open_file(file_path):
            self.create_text_editor_window(file_path)

        browser.set_file_open_callback(open_file)

        self.add_window(window)
        return window

    def create_text_editor_window(self, file_path=None, title=None, x=200, y=150):
        """
        Create a text editor window.

        Args:
            file_path: Optional file path to open
            title: Optional window title (defaults to filename)
            x: X position
            y: Y position

        Returns:
            Window: The created window
        """
        from .text_editor import TextEditorWidget

        if not self.ship_os:
            return None

        # Determine title
        if title is None:
            if file_path:
                title = f"Edit: {file_path}"
            else:
                title = "Text Editor"

        editor = TextEditorWidget(700, 500, self.ship_os, file_path)
        window = Window(title, x, y, 700, 500, editor)
        self.add_window(window)
        return window

    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                # Global shortcuts
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_t:
                        # Ctrl+T: New terminal
                        offset = len([w for w in self.windows if "Terminal" in w.title]) * 30
                        self.create_terminal_window(
                            f"Terminal {len(self.windows) + 1}",
                            100 + offset,
                            100 + offset
                        )
                        continue
                    elif event.key == pygame.K_d:
                        # Ctrl+D: Tactical display
                        self.create_tactical_window()
                        continue

            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()

            # Check taskbar first
            action, data = self.taskbar.handle_event(event, mouse_pos)
            if action == 'menu':
                self.menu_open = not self.menu_open
                continue
            elif action == 'focus_window':
                self.focus_window(data)
                continue

            # Handle menu clicks
            if self.menu_open and event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_rect.collidepoint(mouse_pos):
                    # Calculate which menu item
                    relative_y = mouse_pos[1] - self.menu_rect.y
                    item_index = relative_y // 40

                    if item_index == 0:  # New Terminal
                        self.create_terminal_window()
                    elif item_index == 1:  # File Browser
                        self.create_file_browser_window()
                    elif item_index == 2:  # Text Editor
                        self.create_text_editor_window()
                    elif item_index == 3:  # Tactical Display
                        self.create_tactical_window()
                    elif item_index == 5:  # Quit (after separator)
                        self.running = False

                    self.menu_open = False
                    continue
                else:
                    self.menu_open = False

            # Pass events to windows (in reverse z-order, so top window gets first)
            for window in reversed(self.windows):
                if window.handle_event(event, mouse_pos):
                    # Event consumed
                    # If clicking on window, focus it
                    if event.type == pygame.MOUSEBUTTONDOWN and window.contains_point(*mouse_pos):
                        self.focus_window(window)
                    break

    def update(self, dt):
        """
        Update desktop state.

        Args:
            dt: Delta time in seconds
        """
        # Update starfield
        for star in self.stars:
            star.update(self.warp_speed)

        # Update top bar
        if self.topbar:
            self.topbar.update(dt)

        # Update windows
        for window in self.windows:
            window.update(dt)

        # Update taskbar
        self.taskbar.update_buttons(self.windows)

        # Handle maximize state
        for window in self.windows:
            if window.state == WindowState.MAXIMIZED and window.saved_rect:
                # Account for both top bar and taskbar
                available_height = self.height - Theme.TASKBAR_HEIGHT
                if self.topbar:
                    available_height -= self.topbar.height
                window.maximize(self.width, available_height, Theme.TASKBAR_HEIGHT)

    def render(self):
        """Render the desktop"""
        # Clear screen with black
        self.screen.fill((0, 0, 0))

        # Render starfield
        for star in self.stars:
            x, y, size = star.get_screen_pos()
            if 0 <= x < self.width and 0 <= y < self.height:
                color = star.get_color()
                if size == 1:
                    self.screen.set_at((x, y), color)
                else:
                    pygame.draw.circle(self.screen, color, (x, y), size)

        # Render top bar
        if self.topbar:
            self.topbar.render(self.screen)

        # Render windows (in z-order)
        for window in self.windows:
            if window.visible and window.state != WindowState.MINIMIZED:
                window_surface = window.render()
                self.screen.blit(window_surface, window.rect.topleft)

        # Render taskbar
        self.taskbar.render(self.screen)

        # Render menu if open
        if self.menu_open:
            self._render_menu()

        # Update display
        pygame.display.flip()

    def _render_menu(self):
        """Render application menu"""
        # Menu background
        pygame.draw.rect(self.screen, (60, 60, 60), self.menu_rect, border_radius=4)
        pygame.draw.rect(self.screen, (255, 153, 0), self.menu_rect, 2, border_radius=4)

        # Menu items
        menu_items = [
            "New Terminal",
            "File Browser",
            "Text Editor",
            "Tactical Display",
            "---",
            "Quit"
        ]

        y = self.menu_rect.y + 8
        for i, item in enumerate(menu_items):
            if item == "---":
                # Separator
                pygame.draw.line(
                    self.screen,
                    (100, 100, 100),
                    (self.menu_rect.x + 8, y + 8),
                    (self.menu_rect.right - 8, y + 8)
                )
            else:
                if Theme.FONT_UI:
                    text = Theme.FONT_UI.render(item, True, (255, 255, 255))
                    self.screen.blit(text, (self.menu_rect.x + 12, y))

            y += 40

    def run(self):
        """Main event loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()

    def set_warp_speed(self, speed):
        """Set starfield warp speed"""
        self.warp_speed = speed

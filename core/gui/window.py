"""
Window class for SpaceCMD Desktop Environment

Provides draggable, resizable windows with LCARS+GNOME2 styling.
"""

import pygame
from .themes import Theme, draw_rounded_rect, draw_lcars_button


class WindowState:
    """Window state enumeration"""
    NORMAL = 0
    MAXIMIZED = 1
    MINIMIZED = 2


class Window:
    """
    A desktop window with title bar, borders, and controls.

    Features:
    - Draggable via title bar
    - Minimize/Maximize/Close buttons
    - Resizable (future enhancement)
    - Focus management
    - LCARS + GNOME 2 styling
    """

    def __init__(self, title, x, y, width, height, content_widget=None):
        self.title = title
        self.rect = pygame.Rect(x, y, width, height)
        self.state = WindowState.NORMAL
        self.focused = False
        self.dragging = False
        self.drag_offset = (0, 0)
        self.content_widget = content_widget
        self.visible = True

        # Store original position/size for maximize/restore
        self.saved_rect = None

        # Create surface for window
        self.surface = None
        self._create_surface()

        # Content area (excludes titlebar)
        self.content_rect = pygame.Rect(
            self.rect.x + Theme.WINDOW_BORDER_WIDTH,
            self.rect.y + Theme.WINDOW_TITLEBAR_HEIGHT,
            self.rect.width - Theme.WINDOW_BORDER_WIDTH * 2,
            self.rect.height - Theme.WINDOW_TITLEBAR_HEIGHT - Theme.WINDOW_BORDER_WIDTH
        )

        # Resize content widget to match content area
        if self.content_widget and hasattr(self.content_widget, 'set_size'):
            self.content_widget.set_size(
                self.rect.width - Theme.WINDOW_BORDER_WIDTH * 2,
                self.rect.height - Theme.WINDOW_TITLEBAR_HEIGHT - Theme.WINDOW_BORDER_WIDTH
            )

        # Button rectangles (relative to window)
        button_y = Theme.WINDOW_PADDING
        button_size = Theme.WINDOW_BUTTON_SIZE
        button_spacing = 4

        # Close button (left side, GNOME 2 style)
        self.close_button = pygame.Rect(
            Theme.WINDOW_PADDING,
            button_y,
            button_size,
            button_size
        )

        # Minimize button
        self.minimize_button = pygame.Rect(
            self.rect.width - Theme.WINDOW_PADDING - button_size * 2 - button_spacing,
            button_y,
            button_size,
            button_size
        )

        # Maximize button
        self.maximize_button = pygame.Rect(
            self.rect.width - Theme.WINDOW_PADDING - button_size,
            button_y,
            button_size,
            button_size
        )

    def _create_surface(self):
        """Create the window surface"""
        self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

    def set_content_widget(self, widget):
        """Set the content widget for this window"""
        self.content_widget = widget
        if hasattr(widget, 'set_size'):
            widget.set_size(self.content_rect.width, self.content_rect.height)

    def handle_event(self, event, mouse_pos):
        """
        Handle input events.

        Args:
            event: pygame event
            mouse_pos: (x, y) mouse position in screen coordinates

        Returns:
            bool: True if event was consumed
        """
        if not self.visible or self.state == WindowState.MINIMIZED:
            return False

        # Keyboard events go directly to content widget if focused
        if event.type == pygame.KEYDOWN and self.focused:
            if self.content_widget and hasattr(self.content_widget, 'handle_event'):
                return self.content_widget.handle_event(event, (0, 0))

        # Convert mouse pos to window-relative coordinates
        rel_x = mouse_pos[0] - self.rect.x
        rel_y = mouse_pos[1] - self.rect.y

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicking titlebar
            titlebar_rect = pygame.Rect(0, 0, self.rect.width, Theme.WINDOW_TITLEBAR_HEIGHT)

            if titlebar_rect.collidepoint(rel_x, rel_y):
                # Check buttons first
                if self.close_button.collidepoint(rel_x, rel_y):
                    self.visible = False
                    return True

                if self.minimize_button.collidepoint(rel_x, rel_y):
                    self.minimize()
                    return True

                if self.maximize_button.collidepoint(rel_x, rel_y):
                    self.toggle_maximize()
                    return True

                # Start dragging
                self.dragging = True
                self.drag_offset = (rel_x, rel_y)
                return True

            # Pass event to content widget
            if self.content_widget and hasattr(self.content_widget, 'handle_event'):
                content_x = rel_x - Theme.WINDOW_BORDER_WIDTH
                content_y = rel_y - Theme.WINDOW_TITLEBAR_HEIGHT
                return self.content_widget.handle_event(event, (content_x, content_y))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.state != WindowState.MAXIMIZED:
                # Update window position
                self.rect.x = mouse_pos[0] - self.drag_offset[0]
                self.rect.y = mouse_pos[1] - self.drag_offset[1]
                self._update_content_rect()
                return True

        # Pass other events to content widget
        if self.content_widget and hasattr(self.content_widget, 'handle_event'):
            content_x = rel_x - Theme.WINDOW_BORDER_WIDTH
            content_y = rel_y - Theme.WINDOW_TITLEBAR_HEIGHT
            return self.content_widget.handle_event(event, (content_x, content_y))

        return False

    def _update_content_rect(self):
        """Update content rect based on window position"""
        self.content_rect = pygame.Rect(
            self.rect.x + Theme.WINDOW_BORDER_WIDTH,
            self.rect.y + Theme.WINDOW_TITLEBAR_HEIGHT,
            self.rect.width - Theme.WINDOW_BORDER_WIDTH * 2,
            self.rect.height - Theme.WINDOW_TITLEBAR_HEIGHT - Theme.WINDOW_BORDER_WIDTH
        )

    def minimize(self):
        """Minimize the window"""
        self.state = WindowState.MINIMIZED

    def restore(self):
        """Restore minimized window"""
        self.state = WindowState.NORMAL

    def toggle_maximize(self):
        """Toggle between maximized and normal state"""
        if self.state == WindowState.MAXIMIZED:
            # Restore
            if self.saved_rect:
                self.rect = self.saved_rect.copy()
                self.saved_rect = None
                self.state = WindowState.NORMAL
                self._create_surface()
                self._update_content_rect()
                self._update_button_positions()
        else:
            # Maximize (will be handled by Desktop to get screen size)
            self.state = WindowState.MAXIMIZED

    def maximize(self, screen_width, screen_height, taskbar_height):
        """Maximize window to fill screen (minus taskbar)"""
        self.saved_rect = self.rect.copy()
        self.rect = pygame.Rect(0, 0, screen_width, screen_height - taskbar_height)
        self.state = WindowState.MAXIMIZED
        self._create_surface()
        self._update_content_rect()
        self._update_button_positions()

    def _update_button_positions(self):
        """Update button positions after resize"""
        button_y = Theme.WINDOW_PADDING
        button_size = Theme.WINDOW_BUTTON_SIZE
        button_spacing = 4

        self.minimize_button.x = self.rect.width - Theme.WINDOW_PADDING - button_size * 2 - button_spacing
        self.maximize_button.x = self.rect.width - Theme.WINDOW_PADDING - button_size

    def update(self, dt):
        """
        Update window state.

        Args:
            dt: Delta time in seconds
        """
        if self.content_widget and hasattr(self.content_widget, 'update'):
            self.content_widget.update(dt)

    def render(self):
        """
        Render the window to its surface.

        Returns:
            pygame.Surface: The rendered window surface
        """
        # Clear surface
        self.surface.fill((0, 0, 0, 0))

        # Draw border
        border_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        pygame.draw.rect(self.surface, Theme.WINDOW_BORDER, border_rect, Theme.WINDOW_BORDER_WIDTH)

        # Draw titlebar
        titlebar_color = Theme.TITLEBAR_ACTIVE if self.focused else Theme.TITLEBAR_INACTIVE
        titlebar_rect = pygame.Rect(
            Theme.WINDOW_BORDER_WIDTH,
            Theme.WINDOW_BORDER_WIDTH,
            self.rect.width - Theme.WINDOW_BORDER_WIDTH * 2,
            Theme.WINDOW_TITLEBAR_HEIGHT - Theme.WINDOW_BORDER_WIDTH
        )
        pygame.draw.rect(self.surface, titlebar_color, titlebar_rect)

        # Draw title text
        if Theme.FONT_TITLE:
            title_surface = Theme.FONT_TITLE.render(self.title, True, (255, 255, 255))
            title_x = (self.rect.width - title_surface.get_width()) // 2
            title_y = Theme.WINDOW_PADDING + 2
            self.surface.blit(title_surface, (title_x, title_y))

        # Draw buttons
        # Close button (red, left side)
        pygame.draw.circle(
            self.surface,
            Theme.BUTTON_CLOSE,
            (self.close_button.centerx, self.close_button.centery),
            self.close_button.width // 2
        )

        # Minimize button (yellow)
        pygame.draw.circle(
            self.surface,
            Theme.BUTTON_MINIMIZE,
            (self.minimize_button.centerx, self.minimize_button.centery),
            self.minimize_button.width // 2
        )

        # Maximize button (blue)
        pygame.draw.circle(
            self.surface,
            Theme.BUTTON_MAXIMIZE,
            (self.maximize_button.centerx, self.maximize_button.centery),
            self.maximize_button.width // 2
        )

        # Draw content background
        content_bg_rect = pygame.Rect(
            Theme.WINDOW_BORDER_WIDTH,
            Theme.WINDOW_TITLEBAR_HEIGHT,
            self.rect.width - Theme.WINDOW_BORDER_WIDTH * 2,
            self.rect.height - Theme.WINDOW_TITLEBAR_HEIGHT - Theme.WINDOW_BORDER_WIDTH
        )
        pygame.draw.rect(self.surface, Theme.WINDOW_BG, content_bg_rect)

        # Render content widget
        if self.content_widget and hasattr(self.content_widget, 'render'):
            content_surface = self.content_widget.render()
            if content_surface:
                self.surface.blit(
                    content_surface,
                    (Theme.WINDOW_BORDER_WIDTH, Theme.WINDOW_TITLEBAR_HEIGHT)
                )

        return self.surface

    def contains_point(self, x, y):
        """Check if a point is inside the window"""
        return self.rect.collidepoint(x, y)

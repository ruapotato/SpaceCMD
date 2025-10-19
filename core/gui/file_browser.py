"""
File Browser Widget for SpaceCMD Desktop

GNOME 2-style file manager that browses the ShipOS filesystem.
"""

import pygame
from .themes import Theme, TERMINAL_BG, TERMINAL_FG


class FileBrowserWidget:
    """
    File browser widget for navigating ShipOS filesystem.

    Features:
    - Directory navigation
    - File/directory listing
    - Double-click to open files or navigate directories
    - Scrollable file list
    - Path display
    """

    def __init__(self, width, height, ship_os):
        """
        Initialize file browser.

        Args:
            width: Widget width
            height: Widget height
            ship_os: ShipOS instance for filesystem access
        """
        self.width = width
        self.height = height
        self.ship_os = ship_os
        self.surface = None

        # Current directory
        self.current_path = "/root"

        # File list
        self.files = []
        self.selected_index = -1
        self.scroll_offset = 0

        # Click tracking for double-click
        self.last_click_time = 0
        self.last_click_index = -1
        self.double_click_threshold = 0.3  # seconds

        # Callbacks
        self.on_file_open = None  # Called when file is double-clicked

        # Calculate dimensions
        self._calculate_dimensions()

        # Initial directory load
        self._load_directory()

    def _calculate_dimensions(self):
        """Calculate character grid dimensions"""
        if Theme.FONT_TERMINAL:
            char_surface = Theme.FONT_TERMINAL.render("W", False, (255, 255, 255))
            self.char_width = char_surface.get_width()
            self.char_height = char_surface.get_height()
            self.rows = (self.height - 40) // self.char_height  # Reserve space for path bar
        else:
            self.char_width = 8
            self.char_height = 14
            self.rows = 20

    def set_size(self, width, height):
        """Update widget size"""
        self.width = width
        self.height = height
        self._calculate_dimensions()

    def _load_directory(self):
        """Load current directory contents"""
        self.files = []

        # Execute ls command
        exit_code, stdout, stderr = self.ship_os.execute_command(f"ls -la {self.current_path}")

        if exit_code == 0 and stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue

                # Parse ls -la output (simplified)
                parts = line.split(None, 8)  # Split on whitespace, max 9 parts
                if len(parts) < 9:
                    continue

                permissions = parts[0]
                filename = parts[8]

                # Determine type
                if permissions.startswith('d'):
                    file_type = 'dir'
                elif permissions.startswith('l'):
                    file_type = 'link'
                else:
                    file_type = 'file'

                self.files.append({
                    'name': filename,
                    'type': file_type,
                    'permissions': permissions
                })

        # Reset selection and scroll
        self.selected_index = -1
        self.scroll_offset = 0

    def navigate_to(self, path):
        """Navigate to a specific path"""
        # Normalize path
        if not path.startswith('/'):
            # Relative path
            if path == '..':
                # Go up one directory
                parts = self.current_path.rstrip('/').split('/')
                if len(parts) > 1:
                    self.current_path = '/'.join(parts[:-1]) or '/'
                else:
                    self.current_path = '/'
            else:
                # Navigate into subdirectory
                if self.current_path.endswith('/'):
                    self.current_path = self.current_path + path
                else:
                    self.current_path = self.current_path + '/' + path
        else:
            # Absolute path
            self.current_path = path

        # Reload directory
        self._load_directory()

    def handle_event(self, event, mouse_pos):
        """
        Handle input events.

        Args:
            event: pygame event
            mouse_pos: (x, y) mouse position relative to widget

        Returns:
            bool: True if event was consumed
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicking in file list area
            list_start_y = 30
            if mouse_pos[1] >= list_start_y:
                # Calculate which file was clicked
                relative_y = mouse_pos[1] - list_start_y
                file_index = (relative_y // self.char_height) + self.scroll_offset

                if 0 <= file_index < len(self.files):
                    current_time = pygame.time.get_ticks() / 1000.0

                    # Check for double-click
                    if (file_index == self.last_click_index and
                        current_time - self.last_click_time < self.double_click_threshold):
                        # Double-click!
                        self._handle_double_click(file_index)
                    else:
                        # Single click - just select
                        self.selected_index = file_index

                    self.last_click_time = current_time
                    self.last_click_index = file_index
                    return True

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll file list
            if event.y > 0:
                # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            else:
                # Scroll down
                max_scroll = max(0, len(self.files) - self.rows)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            return True

        elif event.type == pygame.KEYDOWN:
            # Keyboard navigation
            if event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    # Auto-scroll if needed
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                return True
            elif event.key == pygame.K_DOWN:
                if self.selected_index < len(self.files) - 1:
                    self.selected_index += 1
                    # Auto-scroll if needed
                    if self.selected_index >= self.scroll_offset + self.rows:
                        self.scroll_offset = self.selected_index - self.rows + 1
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Enter key - navigate/open
                if 0 <= self.selected_index < len(self.files):
                    self._handle_double_click(self.selected_index)
                return True
            elif event.key == pygame.K_BACKSPACE:
                # Go up one directory
                self.navigate_to('..')
                return True

        return False

    def _handle_double_click(self, file_index):
        """Handle double-click or Enter key on a file"""
        if 0 <= file_index < len(self.files):
            file_info = self.files[file_index]

            if file_info['type'] == 'dir':
                # Navigate into directory
                self.navigate_to(file_info['name'])
            else:
                # Open file
                file_path = self.current_path.rstrip('/') + '/' + file_info['name']
                if self.on_file_open:
                    self.on_file_open(file_path)

    def update(self, dt):
        """Update widget state"""
        pass

    def render(self):
        """Render the file browser"""
        # Create fresh surface
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(TERMINAL_BG)

        if not Theme.FONT_TERMINAL:
            return self.surface

        # Render path bar at top
        path_surface = Theme.FONT_UI.render(f"Location: {self.current_path}", True, (100, 255, 150))
        self.surface.blit(path_surface, (8, 8))

        # Draw separator
        pygame.draw.line(self.surface, (80, 80, 80), (0, 28), (self.width, 28), 1)

        # Render file list
        y = 30
        visible_end = min(self.scroll_offset + self.rows, len(self.files))

        for i in range(self.scroll_offset, visible_end):
            file_info = self.files[i]

            # Background for selected item
            if i == self.selected_index:
                sel_rect = pygame.Rect(0, y, self.width, self.char_height)
                pygame.draw.rect(self.surface, (40, 40, 80), sel_rect)

            # Icon/indicator
            if file_info['type'] == 'dir':
                icon = "📁"
                color = (100, 200, 255)  # Blue for directories
            elif file_info['type'] == 'link':
                icon = "🔗"
                color = (200, 100, 255)  # Purple for links
            else:
                icon = "📄"
                color = (200, 200, 200)  # Gray for files

            # Render file name
            text = f"{icon} {file_info['name']}"
            text_surface = Theme.FONT_TERMINAL.render(text, True, color)
            self.surface.blit(text_surface, (8, y))

            y += self.char_height

        # Scrollbar indicator if needed
        if len(self.files) > self.rows:
            scrollbar_height = self.height - 30
            scrollbar_x = self.width - 8
            scrollbar_y = 30

            # Draw scrollbar track
            pygame.draw.rect(self.surface, (40, 40, 40),
                           (scrollbar_x, scrollbar_y, 6, scrollbar_height))

            # Draw scrollbar thumb
            thumb_height = max(20, int(scrollbar_height * (self.rows / len(self.files))))
            thumb_y = scrollbar_y + int((self.scroll_offset / len(self.files)) * scrollbar_height)
            pygame.draw.rect(self.surface, (100, 100, 100),
                           (scrollbar_x, thumb_y, 6, thumb_height))

        return self.surface

    def set_file_open_callback(self, callback):
        """
        Set callback for when a file is opened.

        Args:
            callback: Function that takes file_path as argument
        """
        self.on_file_open = callback

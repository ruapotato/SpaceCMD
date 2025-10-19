"""
File Browser Widget for SpaceCMD Desktop

GNOME 2-style file manager that browses the ShipOS filesystem.
ENHANCED: Gamified navigation with visual effects and breadcrumbs!
"""

import pygame
from .themes import Theme, TERMINAL_BG, TERMINAL_FG


class FileBrowserWidget:
    """
    File browser widget for navigating ShipOS filesystem.

    Features:
    - Directory navigation with breadcrumb trail
    - File/directory listing with icons and colors
    - Double-click to open files or navigate directories
    - Scrollable file list with smooth scrolling
    - Path display with visual effects
    - File preview pane
    - Gamified navigation feedback
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
        self.path_history = ["/root"]  # Navigation history
        self.history_index = 0

        # File list
        self.files = []
        self.selected_index = -1
        self.scroll_offset = 0
        self.target_scroll = 0  # For smooth scrolling

        # Click tracking for double-click
        self.last_click_time = 0
        self.last_click_index = -1
        self.double_click_threshold = 0.3  # seconds

        # Visual effects
        self.navigation_flash = 0.0  # Flash effect when navigating
        self.hover_index = -1

        # File preview
        self.preview_content = None
        self.show_preview = False

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
        """Navigate to a specific path with visual feedback"""
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

        # Add to history (unless we're navigating via back/forward)
        if self.history_index < len(self.path_history) - 1:
            # We're in the middle of history, truncate forward history
            self.path_history = self.path_history[:self.history_index + 1]

        if not self.path_history or self.path_history[-1] != self.current_path:
            self.path_history.append(self.current_path)
            self.history_index = len(self.path_history) - 1

        # Trigger navigation flash effect
        self.navigation_flash = 1.0

        # Reload directory
        self._load_directory()

    def navigate_back(self):
        """Navigate to previous directory in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.path_history[self.history_index]
            self.navigation_flash = 0.8
            self._load_directory()
            return True
        return False

    def navigate_forward(self):
        """Navigate to next directory in history"""
        if self.history_index < len(self.path_history) - 1:
            self.history_index += 1
            self.current_path = self.path_history[self.history_index]
            self.navigation_flash = 0.8
            self._load_directory()
            return True
        return False

    def navigate_up(self):
        """Navigate to parent directory"""
        self.navigate_to('..')

    def get_breadcrumbs(self):
        """Get breadcrumb trail for current path"""
        parts = self.current_path.strip('/').split('/')
        breadcrumbs = [('/', 'root')]

        current = ''
        for part in parts:
            if part:
                current += '/' + part
                breadcrumbs.append((current, part))

        return breadcrumbs

    def handle_event(self, event, mouse_pos):
        """
        Handle input events.

        Args:
            event: pygame event
            mouse_pos: (x, y) mouse position relative to widget

        Returns:
            bool: True if event was consumed
        """
        if event.type == pygame.MOUSEMOTION:
            # Track hover for highlighting
            list_start_y = 60
            if mouse_pos[1] >= list_start_y:
                relative_y = mouse_pos[1] - list_start_y
                self.hover_index = (relative_y // self.char_height) + self.scroll_offset
            else:
                self.hover_index = -1

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for back/forward buttons (left side of path bar)
            if event.button == 1 and mouse_pos[1] < 30:
                # Back button (first 40 pixels)
                if 8 <= mouse_pos[0] < 48:
                    self.navigate_back()
                    return True
                # Forward button (next 40 pixels)
                elif 52 <= mouse_pos[0] < 92:
                    self.navigate_forward()
                    return True
                # Up button (next 40 pixels)
                elif 96 <= mouse_pos[0] < 136:
                    self.navigate_up()
                    return True

            # Check if clicking in file list area
            list_start_y = 60
            if event.button == 1 and mouse_pos[1] >= list_start_y:
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
                        self._load_preview(file_index)

                    self.last_click_time = current_time
                    self.last_click_index = file_index
                    return True

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll file list with smooth scrolling
            if event.y > 0:
                # Scroll up
                self.target_scroll = max(0, self.target_scroll - 3)
            else:
                # Scroll down
                max_scroll = max(0, len(self.files) - self.rows)
                self.target_scroll = min(max_scroll, self.target_scroll + 3)
            return True

        elif event.type == pygame.KEYDOWN:
            # Keyboard navigation
            if event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self._load_preview(self.selected_index)
                    # Auto-scroll if needed
                    if self.selected_index < self.scroll_offset:
                        self.target_scroll = self.selected_index
                return True
            elif event.key == pygame.K_DOWN:
                if self.selected_index < len(self.files) - 1:
                    self.selected_index += 1
                    self._load_preview(self.selected_index)
                    # Auto-scroll if needed
                    if self.selected_index >= self.scroll_offset + self.rows:
                        self.target_scroll = self.selected_index - self.rows + 1
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Enter key - navigate/open
                if 0 <= self.selected_index < len(self.files):
                    self._handle_double_click(self.selected_index)
                return True
            elif event.key == pygame.K_BACKSPACE:
                # Go up one directory
                self.navigate_up()
                return True
            # Browser-style navigation
            elif event.mod & pygame.KMOD_ALT:
                if event.key == pygame.K_LEFT:
                    self.navigate_back()
                    return True
                elif event.key == pygame.K_RIGHT:
                    self.navigate_forward()
                    return True

        return False

    def _load_preview(self, file_index):
        """Load preview for selected file"""
        if 0 <= file_index < len(self.files):
            file_info = self.files[file_index]
            if file_info['type'] == 'file':
                file_path = self.current_path.rstrip('/') + '/' + file_info['name']
                # Try to read first few lines
                exit_code, stdout, stderr = self.ship_os.execute_command(f"head -n 5 {file_path}")
                if exit_code == 0 and stdout:
                    self.preview_content = stdout.strip()
                    self.show_preview = True
                else:
                    self.preview_content = "[Binary file or no preview available]"
                    self.show_preview = True
            else:
                self.show_preview = False
                self.preview_content = None

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
        # Smooth scrolling
        if self.scroll_offset != self.target_scroll:
            diff = self.target_scroll - self.scroll_offset
            self.scroll_offset += diff * min(10 * dt, 1.0)
            # Snap to target if close enough
            if abs(diff) < 0.1:
                self.scroll_offset = self.target_scroll

        # Decay navigation flash
        if self.navigation_flash > 0:
            self.navigation_flash = max(0, self.navigation_flash - dt * 2.0)

    def render(self):
        """Render the file browser"""
        # Create fresh surface
        self.surface = pygame.Surface((self.width, self.height))

        # Background with navigation flash effect
        bg_color = TERMINAL_BG
        if self.navigation_flash > 0:
            flash_amount = int(self.navigation_flash * 30)
            bg_color = (
                min(255, TERMINAL_BG[0] + flash_amount),
                min(255, TERMINAL_BG[1] + flash_amount),
                min(255, TERMINAL_BG[2] + flash_amount)
            )
        self.surface.fill(bg_color)

        if not Theme.FONT_TERMINAL:
            return self.surface

        # Navigation bar with back/forward/up buttons
        nav_y = 4
        button_x = 8

        # Back button
        back_enabled = self.history_index > 0
        back_color = (100, 200, 100) if back_enabled else (60, 60, 60)
        back_rect = pygame.Rect(button_x, nav_y, 36, 20)
        pygame.draw.rect(self.surface, back_color, back_rect, border_radius=3)
        if Theme.FONT_UI:
            back_text = Theme.FONT_UI.render("<", True, (255, 255, 255))
            self.surface.blit(back_text, (back_rect.centerx - back_text.get_width()//2, nav_y + 3))
        button_x += 44

        # Forward button
        forward_enabled = self.history_index < len(self.path_history) - 1
        forward_color = (100, 200, 100) if forward_enabled else (60, 60, 60)
        forward_rect = pygame.Rect(button_x, nav_y, 36, 20)
        pygame.draw.rect(self.surface, forward_color, forward_rect, border_radius=3)
        if Theme.FONT_UI:
            forward_text = Theme.FONT_UI.render(">", True, (255, 255, 255))
            self.surface.blit(forward_text, (forward_rect.centerx - forward_text.get_width()//2, nav_y + 3))
        button_x += 44

        # Up button
        up_rect = pygame.Rect(button_x, nav_y, 36, 20)
        pygame.draw.rect(self.surface, (100, 150, 200), up_rect, border_radius=3)
        if Theme.FONT_UI:
            up_text = Theme.FONT_UI.render("^", True, (255, 255, 255))
            self.surface.blit(up_text, (up_rect.centerx - up_text.get_width()//2, nav_y + 3))
        button_x += 44

        # Breadcrumb trail
        breadcrumbs = self.get_breadcrumbs()
        crumb_x = button_x + 8
        for i, (path, label) in enumerate(breadcrumbs):
            if i > 0:
                # Separator
                sep_surface = Theme.FONT_UI.render(">", True, (100, 100, 100))
                self.surface.blit(sep_surface, (crumb_x, nav_y + 3))
                crumb_x += sep_surface.get_width() + 4

            # Breadcrumb
            crumb_color = (100, 255, 150) if i == len(breadcrumbs) - 1 else (150, 150, 150)
            crumb_surface = Theme.FONT_UI.render(label, True, crumb_color)
            self.surface.blit(crumb_surface, (crumb_x, nav_y + 3))
            crumb_x += crumb_surface.get_width() + 4

        # Draw separator after nav bar
        pygame.draw.line(self.surface, (80, 80, 80), (0, 28), (self.width, 28), 1)

        # File count and info
        info_text = f"{len(self.files)} items"
        if self.selected_index >= 0 and self.selected_index < len(self.files):
            info_text += f" | Selected: {self.files[self.selected_index]['name']}"
        info_surface = Theme.FONT_UI.render(info_text, True, (120, 120, 120))
        self.surface.blit(info_surface, (8, 32))

        # Draw separator after info
        pygame.draw.line(self.surface, (80, 80, 80), (0, 56), (self.width, 56), 1)

        # Render file list
        y = 60
        visible_start = int(self.scroll_offset)
        visible_end = min(visible_start + self.rows + 1, len(self.files))

        for i in range(visible_start, visible_end):
            file_info = self.files[i]

            # Background for hover
            if i == self.hover_index and i != self.selected_index:
                hover_rect = pygame.Rect(0, y, self.width, self.char_height)
                pygame.draw.rect(self.surface, (30, 30, 50), hover_rect)

            # Background for selected item
            if i == self.selected_index:
                sel_rect = pygame.Rect(0, y, self.width, self.char_height)
                pygame.draw.rect(self.surface, (40, 60, 100), sel_rect)

            # Icon/indicator with better colors
            if file_info['type'] == 'dir':
                if file_info['name'] == '..':
                    icon = "⬆️"
                else:
                    icon = "📁"
                color = (100, 200, 255)  # Blue for directories
            elif file_info['type'] == 'link':
                icon = "🔗"
                color = (200, 100, 255)  # Purple for links
            else:
                # Different icons based on file extension
                name = file_info['name']
                if name.endswith('.txt') or name.endswith('.md'):
                    icon = "📝"
                    color = (200, 200, 150)
                elif name.endswith('.py'):
                    icon = "🐍"
                    color = (100, 200, 100)
                elif name.endswith('.sh'):
                    icon = "⚙️"
                    color = (150, 150, 200)
                elif name.endswith('.exe') or name.endswith('.bin'):
                    icon = "⚡"
                    color = (255, 100, 100)
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
            scrollbar_height = self.height - 60
            scrollbar_x = self.width - 8
            scrollbar_y = 60

            # Draw scrollbar track
            pygame.draw.rect(self.surface, (40, 40, 40),
                           (scrollbar_x, scrollbar_y, 6, scrollbar_height))

            # Draw scrollbar thumb
            thumb_height = max(20, int(scrollbar_height * (self.rows / len(self.files))))
            thumb_y = scrollbar_y + int((self.scroll_offset / len(self.files)) * scrollbar_height)
            pygame.draw.rect(self.surface, (100, 150, 100),
                           (scrollbar_x, thumb_y, 6, thumb_height))

        return self.surface

    def set_file_open_callback(self, callback):
        """
        Set callback for when a file is opened.

        Args:
            callback: Function that takes file_path as argument
        """
        self.on_file_open = callback

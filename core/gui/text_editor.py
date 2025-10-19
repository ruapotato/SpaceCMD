"""
Text Editor Widget for SpaceCMD Desktop

Simple text editor for viewing and editing files in ShipOS.
"""

import pygame
from .themes import Theme, TERMINAL_BG, TERMINAL_FG


class TextEditorWidget:
    """
    Text editor widget for editing files in ShipOS.

    Features:
    - View and edit text files
    - Cursor movement
    - Line numbers
    - Save functionality (Ctrl+S)
    - Scrolling
    - Read-only mode
    """

    def __init__(self, width, height, ship_os, file_path=None, read_only=False):
        """
        Initialize text editor.

        Args:
            width: Widget width
            height: Widget height
            ship_os: ShipOS instance for file operations
            file_path: Optional file path to load
            read_only: If True, editing is disabled
        """
        self.width = width
        self.height = height
        self.ship_os = ship_os
        self.file_path = file_path
        self.read_only = read_only
        self.surface = None

        # Text content (list of lines)
        self.lines = [""]
        self.modified = False

        # Cursor position
        self.cursor_line = 0
        self.cursor_col = 0

        # Scroll offset
        self.scroll_offset = 0

        # Cursor blink
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.cursor_blink_interval = 0.5

        # Calculate dimensions
        self._calculate_dimensions()

        # Load file if provided
        if file_path:
            self._load_file(file_path)

    def _calculate_dimensions(self):
        """Calculate character grid dimensions"""
        if Theme.FONT_TERMINAL:
            char_surface = Theme.FONT_TERMINAL.render("W", False, (255, 255, 255))
            self.char_width = char_surface.get_width()
            self.char_height = char_surface.get_height()

            # Line number width (5 digits + space)
            self.line_num_width = self.char_width * 6

            # Calculate visible area
            self.rows = (self.height - 20) // self.char_height  # Reserve for status bar
            self.cols = (self.width - self.line_num_width - 8) // self.char_width
        else:
            self.char_width = 8
            self.char_height = 14
            self.line_num_width = 48
            self.rows = 20
            self.cols = 80

    def set_size(self, width, height):
        """Update widget size"""
        self.width = width
        self.height = height
        self._calculate_dimensions()

    def _load_file(self, file_path):
        """Load file contents"""
        exit_code, stdout, stderr = self.ship_os.execute_command(f"cat {file_path}")

        if exit_code == 0:
            self.lines = stdout.split('\n')
            if len(self.lines) == 0:
                self.lines = [""]
            self.modified = False
            self.file_path = file_path
            return True
        else:
            # File doesn't exist or error - start with empty
            self.lines = [""]
            self.modified = False
            return False

    def save_file(self):
        """Save current content to file"""
        if self.read_only or not self.file_path:
            return False

        # Write content using ShipOS
        content = '\n'.join(self.lines)

        # Create temp file with content
        temp_path = "/tmp/editor_temp"
        exit_code, stdout, stderr = self.ship_os.execute_command(
            f"cat > {temp_path} <<'EDITOR_EOF'\n{content}\nEDITOR_EOF"
        )

        if exit_code == 0:
            # Move to destination
            exit_code, stdout, stderr = self.ship_os.execute_command(
                f"mv {temp_path} {self.file_path}"
            )
            if exit_code == 0:
                self.modified = False
                return True

        return False

    def handle_event(self, event, mouse_pos):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if self.read_only:
                # In read-only mode, only allow navigation
                if event.key == pygame.K_UP:
                    self._move_cursor_up()
                    return True
                elif event.key == pygame.K_DOWN:
                    self._move_cursor_down()
                    return True
                elif event.key == pygame.K_LEFT:
                    self._move_cursor_left()
                    return True
                elif event.key == pygame.K_RIGHT:
                    self._move_cursor_right()
                    return True
                elif event.key == pygame.K_HOME:
                    self.cursor_col = 0
                    return True
                elif event.key == pygame.K_END:
                    self.cursor_col = len(self.lines[self.cursor_line])
                    return True
                elif event.key == pygame.K_PAGEUP:
                    self.scroll_offset = max(0, self.scroll_offset - self.rows)
                    return True
                elif event.key == pygame.K_PAGEDOWN:
                    max_scroll = max(0, len(self.lines) - self.rows)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + self.rows)
                    return True
                return False

            # Editable mode
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_s:
                    # Save file
                    self.save_file()
                    return True
                elif event.key == pygame.K_a:
                    # Select all (not implemented, move to start for now)
                    self.cursor_col = 0
                    return True
                elif event.key == pygame.K_e:
                    # Move to end
                    self.cursor_col = len(self.lines[self.cursor_line])
                    return True

            # Navigation
            if event.key == pygame.K_UP:
                self._move_cursor_up()
                return True
            elif event.key == pygame.K_DOWN:
                self._move_cursor_down()
                return True
            elif event.key == pygame.K_LEFT:
                self._move_cursor_left()
                return True
            elif event.key == pygame.K_RIGHT:
                self._move_cursor_right()
                return True
            elif event.key == pygame.K_HOME:
                self.cursor_col = 0
                return True
            elif event.key == pygame.K_END:
                self.cursor_col = len(self.lines[self.cursor_line])
                return True

            # Editing
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self._insert_newline()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self._backspace()
                return True
            elif event.key == pygame.K_DELETE:
                self._delete()
                return True
            elif event.key == pygame.K_TAB:
                self._insert_char('    ')  # 4 spaces
                return True
            elif event.unicode and event.unicode.isprintable():
                self._insert_char(event.unicode)
                return True

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            else:
                max_scroll = max(0, len(self.lines) - self.rows)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            return True

        return False

    def _move_cursor_up(self):
        """Move cursor up one line"""
        if self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            # Auto-scroll
            if self.cursor_line < self.scroll_offset:
                self.scroll_offset = self.cursor_line

    def _move_cursor_down(self):
        """Move cursor down one line"""
        if self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            # Auto-scroll
            if self.cursor_line >= self.scroll_offset + self.rows:
                self.scroll_offset = self.cursor_line - self.rows + 1

    def _move_cursor_left(self):
        """Move cursor left"""
        if self.cursor_col > 0:
            self.cursor_col -= 1
        elif self.cursor_line > 0:
            # Move to end of previous line
            self.cursor_line -= 1
            self.cursor_col = len(self.lines[self.cursor_line])

    def _move_cursor_right(self):
        """Move cursor right"""
        if self.cursor_col < len(self.lines[self.cursor_line]):
            self.cursor_col += 1
        elif self.cursor_line < len(self.lines) - 1:
            # Move to start of next line
            self.cursor_line += 1
            self.cursor_col = 0

    def _insert_char(self, char):
        """Insert character at cursor"""
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_col] + char + line[self.cursor_col:]
        self.cursor_col += len(char)
        self.modified = True

    def _insert_newline(self):
        """Insert newline at cursor"""
        line = self.lines[self.cursor_line]
        # Split line at cursor
        before = line[:self.cursor_col]
        after = line[self.cursor_col:]
        self.lines[self.cursor_line] = before
        self.lines.insert(self.cursor_line + 1, after)
        self.cursor_line += 1
        self.cursor_col = 0
        self.modified = True

    def _backspace(self):
        """Delete character before cursor"""
        if self.cursor_col > 0:
            line = self.lines[self.cursor_line]
            self.lines[self.cursor_line] = line[:self.cursor_col - 1] + line[self.cursor_col:]
            self.cursor_col -= 1
            self.modified = True
        elif self.cursor_line > 0:
            # Merge with previous line
            prev_line = self.lines[self.cursor_line - 1]
            curr_line = self.lines[self.cursor_line]
            self.cursor_col = len(prev_line)
            self.lines[self.cursor_line - 1] = prev_line + curr_line
            self.lines.pop(self.cursor_line)
            self.cursor_line -= 1
            self.modified = True

    def _delete(self):
        """Delete character at cursor"""
        line = self.lines[self.cursor_line]
        if self.cursor_col < len(line):
            self.lines[self.cursor_line] = line[:self.cursor_col] + line[self.cursor_col + 1:]
            self.modified = True
        elif self.cursor_line < len(self.lines) - 1:
            # Merge with next line
            next_line = self.lines[self.cursor_line + 1]
            self.lines[self.cursor_line] = line + next_line
            self.lines.pop(self.cursor_line + 1)
            self.modified = True

    def update(self, dt):
        """Update editor state"""
        # Cursor blink
        self.cursor_blink_time += dt
        if self.cursor_blink_time >= self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = 0

    def render(self):
        """Render the editor"""
        # Create fresh surface
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(TERMINAL_BG)

        if not Theme.FONT_TERMINAL:
            return self.surface

        # Render visible lines
        y = 4
        visible_end = min(self.scroll_offset + self.rows, len(self.lines))

        for i in range(self.scroll_offset, visible_end):
            # Line number
            line_num = str(i + 1).rjust(5)
            line_num_surface = Theme.FONT_TERMINAL.render(line_num, True, (100, 100, 100))
            self.surface.blit(line_num_surface, (4, y))

            # Line number separator
            pygame.draw.line(self.surface, (60, 60, 60),
                           (self.line_num_width - 4, y),
                           (self.line_num_width - 4, y + self.char_height))

            # Line content
            line = self.lines[i]
            if line:
                # Truncate if too long
                visible_chars = min(len(line), self.cols)
                visible_line = line[:visible_chars]
                text_surface = Theme.FONT_TERMINAL.render(visible_line, True, TERMINAL_FG)
                self.surface.blit(text_surface, (self.line_num_width + 4, y))

            # Cursor on this line
            if i == self.cursor_line and self.cursor_visible:
                cursor_x = self.line_num_width + 4 + self.cursor_col * self.char_width
                cursor_rect = pygame.Rect(cursor_x, y, 2, self.char_height)
                pygame.draw.rect(self.surface, (0, 255, 100), cursor_rect)

            y += self.char_height

        # Status bar at bottom
        status_y = self.height - self.char_height - 4
        pygame.draw.rect(self.surface, (20, 20, 40),
                        (0, status_y - 2, self.width, self.char_height + 4))

        status_parts = []
        if self.file_path:
            status_parts.append(self.file_path)
        else:
            status_parts.append("[New File]")

        if self.modified:
            status_parts.append("[Modified]")
        if self.read_only:
            status_parts.append("[Read-Only]")

        status_parts.append(f"Line {self.cursor_line + 1}/{len(self.lines)}")
        status_parts.append(f"Col {self.cursor_col + 1}")

        if not self.read_only:
            status_parts.append("Ctrl+S:Save")

        status_text = " | ".join(status_parts)
        status_surface = Theme.FONT_TERMINAL.render(status_text, True, (200, 200, 200))
        self.surface.blit(status_surface, (8, status_y))

        return self.surface

"""
Terminal Emulator Widget

A fully-featured terminal emulator with:
- Command history (up/down arrows)
- Readline-like editing (Ctrl+A, Ctrl+E, Ctrl+U, etc.)
- Scrollback buffer
- ANSI color support (basic)
- Cursor with blink animation
"""

import pygame
import time
from collections import deque
from .themes import Theme, TERMINAL_BG, TERMINAL_FG, TERMINAL_CURSOR


class TerminalWidget:
    """
    Terminal emulator widget for displaying text and accepting commands.

    Features:
    - Scrollback buffer
    - Command history with up/down arrows
    - Readline-style editing
    - Blinking cursor
    - ANSI color support
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = None

        # Text buffer (scrollback)
        self.buffer = deque(maxlen=1000)  # Keep last 1000 lines
        self.scroll_offset = 0  # How many lines scrolled back

        # Current input line
        self.input_line = ""
        self.cursor_pos = 0  # Position in input_line
        self.prompt = "$ "

        # Command history
        self.history = deque(maxlen=100)
        self.history_index = -1  # -1 means current input, 0+ means history
        self.history_temp = ""  # Temporary storage for current input when browsing history

        # Cursor blink
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.cursor_blink_interval = 0.5  # Seconds

        # Colors (basic ANSI support)
        self.current_fg = TERMINAL_FG
        self.current_bg = TERMINAL_BG

        # Calculate dimensions
        self._calculate_dimensions()

        # Callback for when user submits a command
        self.on_command = None  # Function to call with command string

    def _calculate_dimensions(self):
        """Calculate character grid dimensions"""
        if Theme.FONT_TERMINAL:
            # Get font metrics
            char_surface = Theme.FONT_TERMINAL.render("W", False, (255, 255, 255))
            self.char_width = char_surface.get_width()
            self.char_height = char_surface.get_height()

            # Calculate how many characters fit
            self.cols = self.width // self.char_width
            self.rows = self.height // self.char_height
        else:
            self.cols = 80
            self.rows = 24
            self.char_width = 8
            self.char_height = 14

    def set_size(self, width, height):
        """Update widget size"""
        self.width = width
        self.height = height
        self._calculate_dimensions()

    def write(self, text):
        """Write text to terminal (like print())"""
        # Handle empty text
        if not text:
            return

        lines = text.split('\n')
        for line in lines:
            # Only add non-empty lines or keep empty lines that are intentional
            self.buffer.append(line)

        # Auto-scroll to bottom when new text arrives
        self.scroll_offset = 0

    def write_line(self, text):
        """Write a line of text (adds newline)"""
        self.write(text + '\n')

    def clear(self):
        """Clear the terminal"""
        self.buffer.clear()

    def _move_cursor_left(self):
        """Move cursor left"""
        if self.cursor_pos > 0:
            self.cursor_pos -= 1

    def _move_cursor_right(self):
        """Move cursor right"""
        if self.cursor_pos < len(self.input_line):
            self.cursor_pos += 1

    def _move_cursor_home(self):
        """Move cursor to start of line"""
        self.cursor_pos = 0

    def _move_cursor_end(self):
        """Move cursor to end of line"""
        self.cursor_pos = len(self.input_line)

    def _delete_char(self):
        """Delete character under cursor (Delete key)"""
        if self.cursor_pos < len(self.input_line):
            self.input_line = self.input_line[:self.cursor_pos] + self.input_line[self.cursor_pos + 1:]

    def _backspace(self):
        """Delete character before cursor"""
        if self.cursor_pos > 0:
            self.input_line = self.input_line[:self.cursor_pos - 1] + self.input_line[self.cursor_pos:]
            self.cursor_pos -= 1

    def _delete_to_end(self):
        """Delete from cursor to end of line (Ctrl+K)"""
        self.input_line = self.input_line[:self.cursor_pos]

    def _delete_to_start(self):
        """Delete from start to cursor (Ctrl+U)"""
        self.input_line = self.input_line[self.cursor_pos:]
        self.cursor_pos = 0

    def _history_prev(self):
        """Navigate to previous command in history (up arrow)"""
        if not self.history:
            return

        if self.history_index == -1:
            # Save current input
            self.history_temp = self.input_line
            self.history_index = len(self.history) - 1
        elif self.history_index > 0:
            self.history_index -= 1

        if 0 <= self.history_index < len(self.history):
            self.input_line = self.history[self.history_index]
            self.cursor_pos = len(self.input_line)

    def _history_next(self):
        """Navigate to next command in history (down arrow)"""
        if self.history_index == -1:
            return

        self.history_index += 1

        if self.history_index >= len(self.history):
            # Back to current input
            self.input_line = self.history_temp
            self.history_index = -1
        else:
            self.input_line = self.history[self.history_index]

        self.cursor_pos = len(self.input_line)

    def _submit_command(self):
        """Submit the current command"""
        command = self.input_line.strip()

        # Add to buffer
        self.buffer.append(self.prompt + self.input_line)

        # Add to history if not empty
        if command:
            self.history.append(command)

        # Reset input
        self.input_line = ""
        self.cursor_pos = 0
        self.history_index = -1
        self.history_temp = ""

        # Call callback if set
        if self.on_command and command:
            self.on_command(command)

    def handle_event(self, event, mouse_pos):
        """
        Handle input events.

        Args:
            event: pygame event
            mouse_pos: (x, y) mouse position relative to widget

        Returns:
            bool: True if event was consumed
        """
        if event.type == pygame.KEYDOWN:
            # Readline-style shortcuts
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_a:
                    self._move_cursor_home()
                    return True
                elif event.key == pygame.K_e:
                    self._move_cursor_end()
                    return True
                elif event.key == pygame.K_u:
                    self._delete_to_start()
                    return True
                elif event.key == pygame.K_k:
                    self._delete_to_end()
                    return True
                elif event.key == pygame.K_l:
                    self.clear()
                    return True
                # Ctrl+C could be handled here for interrupt

            # Navigation keys
            if event.key == pygame.K_LEFT:
                self._move_cursor_left()
                return True
            elif event.key == pygame.K_RIGHT:
                self._move_cursor_right()
                return True
            elif event.key == pygame.K_HOME:
                self._move_cursor_home()
                return True
            elif event.key == pygame.K_END:
                self._move_cursor_end()
                return True
            elif event.key == pygame.K_UP:
                self._history_prev()
                return True
            elif event.key == pygame.K_DOWN:
                self._history_next()
                return True

            # Editing keys
            elif event.key == pygame.K_BACKSPACE:
                self._backspace()
                return True
            elif event.key == pygame.K_DELETE:
                self._delete_char()
                return True

            # Submit command
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self._submit_command()
                return True

            # Character input
            elif event.unicode and event.unicode.isprintable():
                # Insert character at cursor
                self.input_line = (
                    self.input_line[:self.cursor_pos] +
                    event.unicode +
                    self.input_line[self.cursor_pos:]
                )
                self.cursor_pos += 1
                # Force cursor to be visible when typing
                self.cursor_visible = True
                self.cursor_blink_time = 0
                # Debug output
                print(f"DEBUG: Typed '{event.unicode}' - input_line: '{self.input_line}' - cursor_pos: {self.cursor_pos}")
                return True

        # Scroll wheel
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll up (event.y > 0) means go back in history
            # Scroll down (event.y < 0) means go forward to recent
            if event.y > 0:
                # Scroll up (back in history)
                max_scroll = len(self.buffer) - (self.rows - 1)
                self.scroll_offset = min(max_scroll, self.scroll_offset + abs(event.y))
            else:
                # Scroll down (toward recent)
                self.scroll_offset = max(0, self.scroll_offset - abs(event.y))
            return True

        return False

    def update(self, dt):
        """
        Update widget state.

        Args:
            dt: Delta time in seconds
        """
        # Update cursor blink
        self.cursor_blink_time += dt
        if self.cursor_blink_time >= self.cursor_blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = 0

    def render(self):
        """
        Render the terminal.

        Returns:
            pygame.Surface: Rendered terminal surface
        """
        # Create surface if needed
        if self.surface is None or self.surface.get_size() != (self.width, self.height):
            self.surface = pygame.Surface((self.width, self.height))

        # ALWAYS clear and redraw the entire surface
        self.surface.fill(TERMINAL_BG)

        if not Theme.FONT_TERMINAL:
            return self.surface

        # Calculate visible lines
        visible_lines = self.rows - 1  # Reserve one line for input

        # Get buffer content
        total_lines = len(self.buffer)

        # When scroll_offset is 0, show the most recent lines
        # When scroll_offset > 0, we're scrolled back in history
        if self.scroll_offset == 0:
            # Show most recent lines
            start_line = max(0, total_lines - visible_lines)
            end_line = total_lines
        else:
            # Scrolled back
            start_line = max(0, total_lines - visible_lines - self.scroll_offset)
            end_line = max(0, total_lines - self.scroll_offset)

        # Render buffer lines
        y = 0
        for i in range(start_line, end_line):
            if i < len(self.buffer):
                line = self.buffer[i]
                # Truncate long lines
                if len(line) * self.char_width > self.width - 8:
                    visible_chars = (self.width - 8) // self.char_width
                    line = line[:visible_chars]
                # TODO: Parse basic ANSI codes
                text_surface = Theme.FONT_TERMINAL.render(line, True, TERMINAL_FG)
                self.surface.blit(text_surface, (4, y))
                y += self.char_height

        # Fill remaining space to ensure input is always at bottom
        while y < self.height - self.char_height - 8:
            y += self.char_height

        # Render input line at bottom (always visible, always at same position)
        input_y = self.height - self.char_height - 4

        # Draw a subtle background for the input line to make it stand out
        input_bg_rect = pygame.Rect(0, input_y - 2, self.width, self.char_height + 6)
        pygame.draw.rect(self.surface, (15, 15, 40), input_bg_rect)

        # Prompt
        prompt_surface = Theme.FONT_TERMINAL.render(self.prompt, True, (100, 255, 150))
        self.surface.blit(prompt_surface, (4, input_y))

        # Input text - ALWAYS render
        prompt_width = prompt_surface.get_width()

        # Calculate how much space we have for input
        max_input_width = self.width - prompt_width - 20
        visible_chars = max(1, max_input_width // self.char_width) if self.char_width > 0 else 40

        # Determine what portion of input to show
        cursor_offset = self.cursor_pos
        visible_input = self.input_line

        if len(self.input_line) > visible_chars:
            # Input is too long, need to scroll
            if self.cursor_pos >= visible_chars:
                # Show the portion around the cursor
                start_pos = max(0, self.cursor_pos - visible_chars + 1)
                visible_input = self.input_line[start_pos:start_pos + visible_chars]
                cursor_offset = self.cursor_pos - start_pos
            else:
                # Show from beginning
                visible_input = self.input_line[:visible_chars]
                cursor_offset = self.cursor_pos

        # ALWAYS render the input text (even if empty string)
        input_surface = Theme.FONT_TERMINAL.render(visible_input, True, TERMINAL_FG)
        self.surface.blit(input_surface, (4 + prompt_width, input_y))

        # Cursor - ALWAYS draw it (make it block style for better visibility)
        cursor_x = 4 + prompt_width + cursor_offset * self.char_width
        if self.cursor_visible:
            # Block cursor
            cursor_rect = pygame.Rect(cursor_x, input_y, max(self.char_width, 8), self.char_height)
            pygame.draw.rect(self.surface, TERMINAL_CURSOR, cursor_rect)
        else:
            # Draw a thin line even when "blinking off" so you know where you are
            cursor_rect = pygame.Rect(cursor_x, input_y, 2, self.char_height)
            pygame.draw.rect(self.surface, (0, 150, 50), cursor_rect)

        return self.surface

    def set_prompt(self, prompt):
        """Set the command prompt"""
        self.prompt = prompt

    def set_command_callback(self, callback):
        """
        Set callback for command submission.

        Args:
            callback: Function that takes command string as argument
        """
        self.on_command = callback

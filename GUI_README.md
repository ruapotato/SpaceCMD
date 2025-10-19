# SpaceCMD Pygame Desktop Environment

## Overview

SpaceCMD now features a full Pygame-based desktop environment that combines LCARS (Star Trek) aesthetics with GNOME 2 window manager functionality. This provides a rich graphical interface while maintaining the command-line Unix experience.

## Features

### Desktop Environment
- **Window Manager**: Full window management with dragging, minimize, maximize, and close
- **Taskbar**: GNOME 2-style taskbar showing open windows
- **Application Menu**: Click the APPS button to launch terminals and tactical displays
- **Animated Starfield**: Dynamic star background (speed tied to ship velocity)
- **LCARS Theming**: Orange/pink/blue color scheme inspired by Star Trek interfaces

### Terminal Emulator
- **Full ShipOS Integration**: All terminals connect to the same ShipOS instance
- **Readline Features**:
  - `Ctrl+A` - Move to start of line
  - `Ctrl+E` - Move to end of line
  - `Ctrl+U` - Delete to start of line
  - `Ctrl+K` - Delete to end of line
  - `Ctrl+L` - Clear screen
  - `Up/Down` - Navigate command history
- **Scrollback Buffer**: 1000 lines of history
- **Multi-Terminal**: Open multiple terminal windows that share the same filesystem
- **Live Input**: See characters as you type them

### Tactical Display
- **FTL-Style Ship Interiors**: Visual representation of ship rooms and systems
- **System Status**: Color-coded health indicators for each system
- **Crew Positions**: Shows crew member locations
- **Damage Visualization**: Fire, breaches, and system failures
- **Weapon Animations**: Projectile effects for combat

## Running the GUI

### GUI Mode (Default)
```bash
python3 play.py
```

### CLI Mode (for debugging)
```bash
python3 play.py --no-gui
```

### Choose Specific Ship
```bash
python3 play.py --ship kestrel
```

## Keyboard Shortcuts

### Global Desktop
- `Ctrl+T` - Open new terminal window
- `Ctrl+D` - Open tactical display window
- `ESC` - Exit the application

### Terminal
- `Ctrl+A` - Beginning of line
- `Ctrl+E` - End of line
- `Ctrl+U` - Delete to beginning
- `Ctrl+K` - Delete to end
- `Ctrl+L` - Clear terminal
- `Up/Down` - Command history
- `Left/Right` - Move cursor
- `Home/End` - Jump to start/end

### Window Management
- **Drag titlebar** - Move window
- **Red button** - Close window
- **Yellow button** - Minimize window
- **Blue button** - Maximize/restore window

## Architecture

```
core/gui/
├── __init__.py          - Package exports
├── desktop.py           - Desktop environment & window manager
├── window.py            - Window class (dragging, buttons, focus)
├── terminal_widget.py   - Terminal emulator with readline support
├── tactical_widget.py   - FTL-style tactical display
├── themes.py            - LCARS + GNOME 2 color schemes
```

### Key Components

**Desktop Class** (`desktop.py`)
- Manages all windows (z-order, focus)
- Renders animated starfield background
- Handles global keyboard shortcuts
- Runs main event loop at 60 FPS

**Window Class** (`window.py`)
- Draggable via titlebar
- Minimize/maximize/close buttons
- Focus management (click to focus)
- Contains content widgets (terminal, tactical, etc.)

**TerminalWidget** (`terminal_widget.py`)
- Connected to ShipOS via `system.execute_command()`
- Full readline editing support
- Scrollback buffer with mouse wheel scrolling
- Command history
- Blinking cursor

**TacticalWidget** (`tactical_widget.py`)
- Ship layout visualization
- Room-based display (like FTL)
- System health monitoring
- Crew tracking
- Weapon fire animations

## Integration with ShipOS

All terminals in the GUI connect to a shared `UnixSystem` instance:

```python
# Create ShipOS
ship_os = UnixSystem(hostname="kestrel", ip_or_interfaces={'eth0': '192.168.1.10'})
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

# Terminals execute commands through ShipOS
exit_code, stdout, stderr = ship_os.execute_command(command)
```

This means:
- **Shared Filesystem**: Files created in one terminal appear in all others
- **Shared Processes**: Background jobs visible across terminals
- **Unix Realism**: Full `/dev`, `/proc`, `/sys` filesystem access
- **PoohScript Execution**: All commands run through PoohScript interpreter

## Testing

### Quick GUI Test
```bash
python3 test_gui.py
```

This launches a demo desktop with:
- Two terminal windows
- One tactical display
- Pre-populated welcome message
- Sample commands (help, status, ls, clear)

## Customization

### Adding New Widget Types

1. Create widget class in `core/gui/`:
```python
class MyWidget:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = None

    def update(self, dt):
        """Update state (called every frame)"""
        pass

    def render(self):
        """Return pygame.Surface to display"""
        return self.surface

    def handle_event(self, event, mouse_pos):
        """Handle input events, return True if consumed"""
        return False
```

2. Add creation method to Desktop:
```python
def create_my_window(self, title="My Window", x=100, y=100):
    widget = MyWidget(600, 400)
    window = Window(title, x, y, 600, 400, widget)
    self.add_window(window)
    return window
```

### Customizing Colors

Edit `core/gui/themes.py`:

```python
# LCARS colors
LCARS_ORANGE = (255, 153, 0)
LCARS_PINK = (204, 153, 255)
LCARS_BLUE = (153, 204, 255)
# ... etc
```

## Future Enhancements

### Planned Features
- [ ] Resizable windows (drag corners/edges)
- [ ] Window snapping (drag to edge to snap half-screen)
- [ ] Tab support in terminals
- [ ] File browser widget
- [ ] Ship status widget showing hull/shields/power
- [ ] Mini-map showing sector navigation
- [ ] Damage effects impacting shell commands
- [ ] Varied ship shapes in tactical display
- [ ] Sound effects for UI interactions
- [ ] Custom mouse cursor

### Tactical Display Improvements
- [ ] Different ship layouts (Kestrel, Stealth, Mantis)
- [ ] Room-specific icons
- [ ] Animated fires and breaches
- [ ] Door controls
- [ ] Teleporter beam animations
- [ ] Shield layer visualization

### Terminal Enhancements
- [ ] Tab completion
- [ ] Syntax highlighting for PoohScript
- [ ] ANSI color code support
- [ ] Split panes (tmux-style)
- [ ] Copy/paste support
- [ ] Mouse selection

## Troubleshooting

### GUI won't start
```bash
# Make sure pygame is installed
pip install pygame

# Try CLI mode to test ShipOS
python3 play.py --no-gui
```

### Terminals are blank
- Check that ShipOS booted successfully
- Look for errors in console output
- Verify that commands work in CLI mode first

### Input not showing
- Make sure window is focused (click on it)
- Check that Theme.FONT_TERMINAL is initialized
- Verify pygame fonts are available

### Performance issues
- Reduce number of stars in starfield
- Lower FPS in desktop.py (default is 60)
- Close unused windows

## Contributing

The GUI system is designed to be modular and extensible. To add new features:

1. Create widgets in `core/gui/`
2. Add keyboard shortcuts in `Desktop.handle_events()`
3. Update themes in `themes.py`
4. Test with both `test_gui.py` and `play.py`

## License

GPL-3.0 (same as SpaceCMD)

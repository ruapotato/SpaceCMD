"""
Top Bar with System Monitor for SpaceCMD Desktop

GNOME 2-style panel at the top showing ship stats from virtual devices.
"""

import pygame
from .themes import Theme


class SystemMonitor:
    """
    System monitor widget that reads ship stats from virtual devices.

    Displays:
    - Hull integrity from /dev/ship/hull
    - Shield levels from /dev/ship/shields
    - Power allocation from /proc/ship/power
    - Reactor status from /dev/ship/reactor
    """

    def __init__(self, ship_os):
        """
        Initialize system monitor.

        Args:
            ship_os: ShipOS instance to read device files from
        """
        self.ship_os = ship_os
        self.hull = 0
        self.hull_max = 30  # Default, will update
        self.shields = 0
        self.shields_max = 4
        self.power_used = 0
        self.power_total = 0
        self.location = "Unknown"
        self.location_available = False
        self.update_interval = 0.5  # Update every 0.5 seconds
        self.time_since_update = 0

    def update(self, dt):
        """
        Update stats by reading from virtual devices.

        Args:
            dt: Delta time in seconds
        """
        self.time_since_update += dt

        if self.time_since_update >= self.update_interval:
            self.time_since_update = 0
            self._read_devices()

    def _read_devices(self):
        """Read ship stats from virtual device files"""
        try:
            # Read hull from /dev/ship/hull
            exit_code, stdout, stderr = self.ship_os.execute_command("cat /dev/ship/hull")
            if exit_code == 0 and stdout.strip():
                self.hull = int(float(stdout.strip()))

            # Read shields from /dev/ship/shields
            exit_code, stdout, stderr = self.ship_os.execute_command("cat /dev/ship/shields")
            if exit_code == 0 and stdout.strip():
                self.shields = int(float(stdout.strip()))

            # Read power info from /proc/ship/power
            exit_code, stdout, stderr = self.ship_os.execute_command("cat /proc/ship/power")
            if exit_code == 0 and stdout:
                for line in stdout.split('\n'):
                    if 'Total:' in line:
                        self.power_total = int(line.split(':')[1].strip())
                    elif 'Allocated:' in line:
                        self.power_used = int(line.split(':')[1].strip())

            # Read location from /proc/ship/sensors (requires sensors to be functional)
            exit_code, stdout, stderr = self.ship_os.execute_command("cat /proc/ship/sensors")
            if exit_code == 0 and stdout:
                if "SENSORS OFFLINE" not in stdout:
                    # Sensors are online, extract location
                    self.location_available = True
                    for line in stdout.split('\n'):
                        if 'Galaxy Position:' in line:
                            # Extract distance value
                            parts = line.split(':')
                            if len(parts) > 1:
                                distance_str = parts[1].strip().split()[0]
                                self.location = f"{float(distance_str):.0f}u"
                            break
                else:
                    # Sensors offline
                    self.location_available = False
                    self.location = "OFFLINE"

            # Get max values from ship object if available
            if hasattr(self.ship_os, 'ship'):
                self.hull_max = self.ship_os.ship.hull_max
                self.shields_max = self.ship_os.ship.shields_max

        except Exception as e:
            # Fail silently - keep showing last known values
            pass

    def render(self, surface, x, y, width):
        """
        Render system monitor widgets.

        Args:
            surface: Surface to render to
            x: X position
            y: Y position
            width: Available width
        """
        if not Theme.FONT_UI:
            return

        # Starting position
        current_x = x + 8

        # Hull monitor
        hull_text = f"HULL: {self.hull}/{self.hull_max}"
        hull_color = self._get_health_color(self.hull, self.hull_max)
        hull_surface = Theme.FONT_UI.render(hull_text, True, hull_color)
        surface.blit(hull_surface, (current_x, y + 8))
        current_x += hull_surface.get_width() + 4

        # Hull bar
        bar_width = 80
        bar_height = 12
        hull_pct = self.hull / self.hull_max if self.hull_max > 0 else 0
        self._draw_bar(surface, current_x, y + 10, bar_width, bar_height, hull_pct, hull_color)
        current_x += bar_width + 16

        # Shields monitor
        shield_text = f"SHIELDS: {self.shields}/{self.shields_max}"
        shield_color = (153, 204, 255)  # LCARS blue
        shield_surface = Theme.FONT_UI.render(shield_text, True, shield_color)
        surface.blit(shield_surface, (current_x, y + 8))
        current_x += shield_surface.get_width() + 4

        # Shield bar
        shield_pct = self.shields / self.shields_max if self.shields_max > 0 else 0
        self._draw_bar(surface, current_x, y + 10, bar_width, bar_height, shield_pct, shield_color)
        current_x += bar_width + 16

        # Power monitor
        power_text = f"POWER: {self.power_used}/{self.power_total}"
        power_color = (255, 204, 0)  # LCARS yellow
        power_surface = Theme.FONT_UI.render(power_text, True, power_color)
        surface.blit(power_surface, (current_x, y + 8))
        current_x += power_surface.get_width() + 4

        # Power bar
        power_pct = self.power_used / self.power_total if self.power_total > 0 else 0
        self._draw_bar(surface, current_x, y + 10, bar_width, bar_height, power_pct, power_color)
        current_x += bar_width + 16

        # Location monitor (requires sensors)
        if self.location_available:
            location_text = f"LOCATION: {self.location}"
            location_color = (153, 255, 153)  # Green
        else:
            location_text = f"SENSORS: {self.location}"
            location_color = (128, 128, 128)  # Gray

        location_surface = Theme.FONT_UI.render(location_text, True, location_color)
        surface.blit(location_surface, (current_x, y + 8))

    def _get_health_color(self, current, maximum):
        """Get color based on health percentage"""
        if maximum == 0:
            return (128, 128, 128)

        pct = current / maximum
        if pct > 0.6:
            return (0, 255, 0)  # Green
        elif pct > 0.3:
            return (255, 165, 0)  # Orange
        else:
            return (255, 0, 0)  # Red

    def _draw_bar(self, surface, x, y, width, height, percentage, color):
        """Draw a progress bar"""
        # Background (dark)
        pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))

        # Foreground (filled portion)
        filled_width = int(width * percentage)
        if filled_width > 0:
            pygame.draw.rect(surface, color, (x, y, filled_width, height))

        # Border
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)


class TopBar:
    """
    GNOME 2-style top panel with system monitor and application menu.
    """

    def __init__(self, screen_width, screen_height, ship_os=None):
        """
        Initialize top bar.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            ship_os: ShipOS instance for system monitor
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.height = Theme.TASKBAR_HEIGHT  # Same height as taskbar
        self.rect = pygame.Rect(0, 0, screen_width, self.height)

        # System monitor (right side)
        self.system_monitor = SystemMonitor(ship_os) if ship_os else None

        # Ship name (left side)
        self.ship_name = ship_os.ship.name if (ship_os and hasattr(ship_os, 'ship')) else "SpaceCMD"

    def update(self, dt):
        """
        Update top bar.

        Args:
            dt: Delta time in seconds
        """
        if self.system_monitor:
            self.system_monitor.update(dt)

    def render(self, surface):
        """Render top bar"""
        # Draw background
        pygame.draw.rect(surface, Theme.TITLEBAR_ACTIVE, self.rect)

        # Draw bottom border (LCARS accent)
        pygame.draw.line(
            surface,
            Theme.WINDOW_BORDER,
            (0, self.height - 1),
            (self.screen_width, self.height - 1),
            2
        )

        # Ship name on left
        if Theme.FONT_TITLE:
            name_surface = Theme.FONT_TITLE.render(self.ship_name.upper(), True, (255, 153, 0))
            surface.blit(name_surface, (12, 8))

        # System monitor on right
        if self.system_monitor:
            monitor_x = self.screen_width - 700  # Give it 700px on the right
            self.system_monitor.render(surface, monitor_x, 0, 700)

    def handle_event(self, event, mouse_pos):
        """
        Handle top bar events.

        Args:
            event: pygame event
            mouse_pos: (x, y) mouse position

        Returns:
            Tuple of (action, data) or (None, None)
        """
        # Future: Add clickable menu items, etc.
        return (None, None)

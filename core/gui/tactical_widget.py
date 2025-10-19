"""
Tactical Display Widget

FTL-style ship interior visualization showing:
- Room layout
- System status
- Crew positions
- Damage indicators
- Weapon fire
"""

import pygame
import random
from .themes import Theme, STATUS_ONLINE, STATUS_DAMAGED, STATUS_OFFLINE, STATUS_CRITICAL


class ShipRoom:
    """Represents a single room on the ship"""
    def __init__(self, name, system_type=None, x=0, y=0, width=1, height=1):
        self.name = name
        self.system_type = system_type  # "weapons", "shields", "engines", etc.
        self.x = x
        self.y = y
        self.width = width  # In grid units
        self.height = height
        self.health = 100
        self.oxygen = 100
        self.on_fire = False
        self.breached = False
        self.crew = []  # List of crew member names in this room

    def get_status_color(self):
        """Get color based on room/system health"""
        if self.breached or self.on_fire:
            return STATUS_CRITICAL
        elif self.health < 30:
            return STATUS_CRITICAL
        elif self.health < 70:
            return STATUS_DAMAGED
        else:
            return STATUS_ONLINE


class ShipLayout:
    """Ship layout definition"""
    def __init__(self, ship_name="KESTREL"):
        self.ship_name = ship_name
        self.rooms = []
        self.crew = []  # List of crew members
        self.hull = 30
        self.max_hull = 30
        self.shields = 2
        self.max_shields = 4

        # Create default layout
        self._create_default_layout()

    def _create_default_layout(self):
        """Create default ship layout (like Kestrel from FTL)"""
        # Row 0
        self.rooms.append(ShipRoom("Shields", "shields", 0, 0, 1, 1))
        self.rooms.append(ShipRoom("Helm", "helm", 1, 0, 1, 1))
        self.rooms.append(ShipRoom("Weapons", "weapons", 2, 0, 2, 1))

        # Row 1
        self.rooms.append(ShipRoom("Engines", "engines", 0, 1, 1, 1))
        self.rooms.append(ShipRoom("Medbay", "medbay", 1, 1, 1, 1))
        self.rooms.append(ShipRoom("Oxygen", "oxygen", 2, 1, 1, 1))
        self.rooms.append(ShipRoom("Reactor", "reactor", 3, 1, 1, 1))

        # Add some crew
        self.crew = [
            {"name": "Bot-1", "room": 1, "health": 100},
            {"name": "Bot-2", "room": 3, "health": 100},
            {"name": "Bot-3", "room": 5, "health": 100},
        ]

        # Assign crew to rooms
        for crew_member in self.crew:
            room_idx = crew_member["room"]
            if room_idx < len(self.rooms):
                self.rooms[room_idx].crew.append(crew_member["name"])

    def get_room_at(self, grid_x, grid_y):
        """Get room at grid position"""
        for room in self.rooms:
            if (room.x <= grid_x < room.x + room.width and
                room.y <= grid_y < room.y + room.height):
                return room
        return None

    def update_from_ship_data(self, ship_data):
        """Update layout from ship state data (from ShipOS)"""
        # This would be called with real ship data
        # For now, it's a placeholder
        pass


class Projectile:
    """Weapon projectile animation"""
    def __init__(self, x, y, target_x, target_y, ptype="laser"):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.type = ptype
        self.speed = 300  # pixels per second
        self.alive = True

    def update(self, dt):
        """Update projectile position"""
        # Move toward target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2) ** 0.5

        if dist < 5:
            self.alive = False
            return

        # Normalize and move
        if dist > 0:
            dx /= dist
            dy /= dist
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt


class TacticalWidget:
    """
    Tactical display showing ship interior.

    Features:
    - FTL-style room layout
    - System status visualization
    - Crew positions (interactive - click to move)
    - Damage indicators
    - Weapon fire animations
    - Command log showing executed commands
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = None

        # Ship layout
        self.player_ship = ShipLayout("KESTREL")
        self.enemy_ship = None  # Optional enemy ship

        # Display settings
        self.show_enemy = False
        self.room_size = 80  # Pixels per room grid unit (larger!)

        # Animations
        self.projectiles = []

        # Layout positioning - center the ship
        self.player_x = 50
        self.player_y = 80
        self.enemy_x = width - 350
        self.enemy_y = 80

        # Command log for mini-terminal
        self.command_log = []
        self.max_log_lines = 5
        self.command_log_height = 120  # Height of command log section

        # Interactive crew selection
        self.selected_crew = None
        self.crew_rects = {}  # Maps crew name to clickable rect

    def set_size(self, width, height):
        """Update widget size"""
        self.width = width
        self.height = height
        self.enemy_x = width - 350

    def log_command(self, command):
        """Add a command to the log"""
        self.command_log.append(f"> {command}")
        # Keep only recent commands
        if len(self.command_log) > self.max_log_lines:
            self.command_log = self.command_log[-self.max_log_lines:]

    def move_crew(self, crew_name, target_room):
        """Move a crew member to a target room"""
        # Log the action
        self.log_command(f"crew move {crew_name} {target_room}")
        # TODO: Actually move the crew in the ship layout
        # For now, just log it

    def set_enemy_ship(self, enemy_layout):
        """Set enemy ship to display"""
        self.enemy_ship = enemy_layout
        self.show_enemy = True

    def clear_enemy(self):
        """Remove enemy ship"""
        self.enemy_ship = None
        self.show_enemy = False

    def fire_weapon(self, weapon_type="laser"):
        """Animate weapon fire from player to enemy"""
        if self.enemy_ship:
            # Fire from player weapon room to enemy
            proj = Projectile(
                self.player_x + 200,
                self.player_y + 60,
                self.enemy_x + 50,
                self.enemy_y + 60,
                weapon_type
            )
            self.projectiles.append(proj)

    def update(self, dt):
        """
        Update widget state.

        Args:
            dt: Delta time in seconds
        """
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.alive]
        for proj in self.projectiles:
            proj.update(dt)

    def _render_ship(self, surface, ship, offset_x, offset_y, is_enemy=False):
        """Render a single ship's interior with improved visuals"""
        # Ship outline color
        ship_color = (220, 60, 60) if is_enemy else (60, 220, 120)
        accent_color = (255, 100, 100) if is_enemy else (100, 255, 150)

        # Title with glow effect
        if Theme.FONT_TITLE:
            title_font = pygame.font.SysFont('sans-serif', 16, bold=True)
            title = title_font.render(ship.ship_name, True, accent_color)
            surface.blit(title, (offset_x, offset_y - 35))

        # Hull/Shields bars
        if Theme.FONT_SMALL:
            bar_y = offset_y - 18
            bar_width = 200
            bar_height = 12

            # Hull bar
            hull_label = Theme.FONT_SMALL.render("HULL", True, (200, 200, 200))
            surface.blit(hull_label, (offset_x, bar_y))

            hull_bar_x = offset_x + 45
            # Background
            pygame.draw.rect(surface, (40, 40, 40), (hull_bar_x, bar_y, bar_width, bar_height))
            # Fill
            hull_fill = int((ship.hull / ship.max_hull) * bar_width)
            hull_color = STATUS_ONLINE if ship.hull > ship.max_hull * 0.7 else STATUS_DAMAGED if ship.hull > ship.max_hull * 0.3 else STATUS_CRITICAL
            pygame.draw.rect(surface, hull_color, (hull_bar_x, bar_y, hull_fill, bar_height))
            # Border
            pygame.draw.rect(surface, ship_color, (hull_bar_x, bar_y, bar_width, bar_height), 2)
            # Text
            hull_text = Theme.FONT_SMALL.render(f"{ship.hull}/{ship.max_hull}", True, (255, 255, 255))
            surface.blit(hull_text, (hull_bar_x + bar_width + 5, bar_y))

            # Shield bar
            bar_y += 15
            shield_label = Theme.FONT_SMALL.render("SHLD", True, (200, 200, 200))
            surface.blit(shield_label, (offset_x, bar_y))

            shield_bar_x = offset_x + 45
            # Background
            pygame.draw.rect(surface, (40, 40, 40), (shield_bar_x, bar_y, bar_width, bar_height))
            # Fill (shields in segments)
            segment_width = bar_width // ship.max_shields
            for i in range(ship.shields):
                seg_x = shield_bar_x + i * segment_width + 2
                pygame.draw.rect(surface, (100, 150, 255), (seg_x, bar_y + 2, segment_width - 4, bar_height - 4))
            # Border
            pygame.draw.rect(surface, ship_color, (shield_bar_x, bar_y, bar_width, bar_height), 2)
            # Text
            shield_text = Theme.FONT_SMALL.render(f"{ship.shields}/{ship.max_shields}", True, (255, 255, 255))
            surface.blit(shield_text, (shield_bar_x + bar_width + 5, bar_y))

        # Render rooms
        for room in ship.rooms:
            room_x = offset_x + room.x * self.room_size
            room_y = offset_y + room.y * self.room_size
            room_w = room.width * self.room_size
            room_h = room.height * self.room_size

            # Room background
            room_rect = pygame.Rect(room_x, room_y, room_w, room_h)

            # Fill color based on status
            bg_color = (20, 20, 40)
            pygame.draw.rect(surface, bg_color, room_rect)

            # Border color based on health
            border_color = room.get_status_color()
            pygame.draw.rect(surface, border_color, room_rect, 2)

            # System icon/name
            if room.system_type and Theme.FONT_SMALL:
                # System name
                sys_text = Theme.FONT_SMALL.render(room.system_type.upper(), True, border_color)
                text_x = room_x + (room_w - sys_text.get_width()) // 2
                text_y = room_y + 5
                surface.blit(sys_text, (text_x, text_y))

                # Health bar
                health_bar_width = room_w - 10
                health_bar_height = 4
                health_bar_x = room_x + 5
                health_bar_y = room_y + room_h - 10

                # Background
                pygame.draw.rect(
                    surface,
                    (60, 60, 60),
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height)
                )

                # Health fill
                health_fill = int((room.health / 100) * health_bar_width)
                pygame.draw.rect(
                    surface,
                    border_color,
                    (health_bar_x, health_bar_y, health_fill, health_bar_height)
                )

            # Crew indicators (interactive!)
            if room.crew and Theme.FONT_SMALL:
                crew_y = room_y + room_h - 20
                for i, crew_name in enumerate(room.crew):
                    # Crew icon position
                    crew_x = room_x + 10 + (i * 20)

                    # Determine if this crew is selected
                    is_selected = (self.selected_crew == crew_name)

                    # Draw crew indicator (larger and more visible)
                    crew_size = 8
                    crew_color = (255, 255, 100) if is_selected else (100, 200, 255)

                    # Clickable rect for crew
                    crew_rect = pygame.Rect(crew_x - crew_size, crew_y - crew_size, crew_size * 2, crew_size * 2)
                    self.crew_rects[crew_name] = crew_rect

                    # Draw crew icon
                    pygame.draw.circle(surface, crew_color, (crew_x, crew_y), crew_size)

                    # Selection indicator
                    if is_selected:
                        pygame.draw.circle(surface, (255, 255, 0), (crew_x, crew_y), crew_size + 2, 2)

            # Fire/breach indicators
            if room.on_fire:
                if Theme.FONT_UI:
                    fire_text = Theme.FONT_UI.render("FIRE", True, (255, 100, 0))
                    surface.blit(fire_text, (room_x + 5, room_y + room_h // 2))

            if room.breached:
                if Theme.FONT_UI:
                    breach_text = Theme.FONT_UI.render("BREACH", True, (255, 0, 0))
                    surface.blit(breach_text, (room_x + 5, room_y + room_h // 2 + 15))

    def _render_projectiles(self, surface):
        """Render weapon projectiles"""
        for proj in self.projectiles:
            if proj.type == "laser":
                # Red laser beam
                pygame.draw.circle(surface, (255, 50, 50), (int(proj.x), int(proj.y)), 3)
                # Trail
                trail_x = proj.x - 10
                pygame.draw.line(
                    surface,
                    (255, 100, 100),
                    (trail_x, proj.y),
                    (proj.x, proj.y),
                    2
                )
            elif proj.type == "missile":
                # Yellow missile
                pygame.draw.circle(surface, (255, 200, 0), (int(proj.x), int(proj.y)), 4)

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
            # Check if clicking on crew
            for crew_name, rect in self.crew_rects.items():
                if rect.collidepoint(mouse_pos):
                    if self.selected_crew == crew_name:
                        # Deselect
                        self.selected_crew = None
                        self.log_command(f"deselect {crew_name}")
                    else:
                        # Select
                        self.selected_crew = crew_name
                        self.log_command(f"select {crew_name}")
                    return True

            # Check if clicking on a room (to move selected crew)
            if self.selected_crew:
                # Check if mouse is over a room
                for room in self.player_ship.rooms:
                    room_x = self.player_x + room.x * self.room_size
                    room_y = self.player_y + 40 + room.y * self.room_size
                    room_w = room.width * self.room_size
                    room_h = room.height * self.room_size
                    room_rect = pygame.Rect(room_x, room_y, room_w, room_h)

                    if room_rect.collidepoint(mouse_pos):
                        # Move crew to this room
                        self.move_crew(self.selected_crew, room.name)
                        self.selected_crew = None
                        return True

        return False

    def render(self):
        """
        Render the tactical display.

        Returns:
            pygame.Surface: Rendered tactical surface
        """
        # Create surface if needed
        if not self.surface or self.surface.get_size() != (self.width, self.height):
            self.surface = pygame.Surface((self.width, self.height))

        # Clear crew rects for fresh tracking
        self.crew_rects = {}

        # Clear surface with gradient background
        self.surface.fill((5, 5, 20))

        # Calculate main display area (leaving room for command log)
        main_height = self.height - self.command_log_height

        # Title bar with LCARS styling
        title_bar_height = 30
        pygame.draw.rect(self.surface, (255, 153, 0), (0, 0, self.width, title_bar_height))
        if Theme.FONT_TITLE:
            title_font = pygame.font.SysFont('sans-serif', 14, bold=True)
            title = title_font.render("◄◄ TACTICAL DISPLAY ►►", True, (0, 0, 0))
            title_rect = title.get_rect(center=(self.width // 2, title_bar_height // 2))
            self.surface.blit(title, title_rect)

        # Render player ship
        self._render_ship(self.surface, self.player_ship, self.player_x, self.player_y + 40, False)

        # Render enemy ship if present
        if self.show_enemy and self.enemy_ship:
            self._render_ship(self.surface, self.enemy_ship, self.enemy_x, self.enemy_y + 40, True)

        # Render projectiles
        self._render_projectiles(self.surface)

        # Render command log section at bottom
        self._render_command_log(self.surface, main_height)

        return self.surface

    def _render_command_log(self, surface, y_start):
        """Render the command log mini-terminal at the bottom"""
        # Background for command log
        log_rect = pygame.Rect(0, y_start, self.width, self.command_log_height)
        pygame.draw.rect(surface, (10, 10, 30), log_rect)

        # Border
        pygame.draw.rect(surface, (255, 153, 0), log_rect, 2)

        # Title
        if Theme.FONT_SMALL:
            title = Theme.FONT_SMALL.render("COMMAND LOG", True, (255, 153, 0))
            surface.blit(title, (8, y_start + 4))

        # Render command lines
        if Theme.FONT_TERMINAL:
            line_y = y_start + 22
            for cmd in self.command_log:
                cmd_surface = Theme.FONT_TERMINAL.render(cmd, True, (100, 255, 150))
                surface.blit(cmd_surface, (8, line_y))
                line_y += 16

        # Hint text if no commands
        if not self.command_log and Theme.FONT_SMALL:
            hint = Theme.FONT_SMALL.render("Click crew members to select them, click rooms to move them", True, (100, 100, 100))
            surface.blit(hint, (8, y_start + 50))

    def update_player_ship(self, ship_data):
        """Update player ship from game data"""
        self.player_ship.update_from_ship_data(ship_data)

    def update_enemy_ship(self, ship_data):
        """Update enemy ship from game data"""
        if self.enemy_ship:
            self.enemy_ship.update_from_ship_data(ship_data)

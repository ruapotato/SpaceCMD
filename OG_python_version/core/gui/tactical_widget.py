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

# Import sound effects
try:
    from core.audio.sound_fx import play_sound
except:
    def play_sound(name, volume=1.0):
        pass


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
        self.rooms.append(ShipRoom("Repair Bay", "repair_bay", 1, 1, 1, 1))
        self.rooms.append(ShipRoom("Sensors", "sensors", 2, 1, 1, 1))
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
    """Weapon projectile animation with source/target tracking"""
    def __init__(self, x, y, target_x, target_y, ptype="laser", is_enemy=False, source_room=None, target_room=None):
        self.start_x = x  # Store origin for visual effects
        self.start_y = y
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.type = ptype
        self.speed = 300  # pixels per second
        self.alive = True
        self.is_enemy = is_enemy  # True if fired by enemy, False if fired by player
        self.source_room = source_room  # Room name where shot originated
        self.target_room = target_room  # Room name being targeted
        self.impact_effect_time = 0.3  # Show impact effect for 0.3 seconds after hit
        self.has_hit = False

    def update(self, dt):
        """Update projectile position"""
        # Move toward target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2) ** 0.5

        if dist < 5:
            self.has_hit = True
            self.impact_effect_time -= dt
            if self.impact_effect_time <= 0:
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
        self.room_size = 60  # Smaller rooms to fit both ships!

        # Animations
        self.projectiles = []

        # Layout positioning - side by side like FTL!
        # Move ships down to make room for status bars
        self.player_x = 20
        self.player_y = 180  # Moved down from 120
        self.enemy_x = width - 300
        self.enemy_y = 180  # Moved down from 120

        # Command log for mini-terminal
        self.command_log = []
        self.max_log_lines = 5
        self.command_log_height = 150  # More space for controls

        # Interactive controls
        self.selected_crew = None
        self.crew_rects = {}  # Maps crew name to clickable rect
        self.selected_target_room = None  # Enemy room to target
        self.enemy_room_rects = {}  # Clickable enemy rooms
        self.weapon_buttons = []  # Weapon fire buttons
        self.beacon_button = None  # Beacon control button
        self.beacon_active = False  # Beacon state

        # Navigation buttons (galaxy map controls)
        self.nav_btn_warp_toward = None
        self.nav_btn_warp_away = None
        self.nav_btn_stop = None

        # Reference to world manager (set externally)
        self.world_manager = None

        # Reference to ship_os for executing commands (set externally)
        self.ship_os = None

        # Background stars for atmosphere
        self.bg_stars = [(random.randint(0, width), random.randint(0, height - self.command_log_height),
                         random.randint(1, 3)) for _ in range(100)]

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

    def move_crew(self, crew_name, target_room_name):
        """Move a crew member to a target room (executes real command)"""
        # Execute actual crew movement through ship_os
        if self.ship_os:
            # Map display room name to actual ship system
            # (Display uses "Weapons", "Shields", etc. - actual ship uses same)
            command = f"crew assign {crew_name} {target_room_name}"
            self.log_command(f"$ {command}")

            exit_code, stdout, stderr = self.ship_os.execute_command(command)

            if stdout:
                for line in stdout.strip().split('\n'):
                    self.log_command(line)
            if stderr:
                for line in stderr.strip().split('\n'):
                    self.log_command(f"✗ {line}")

            # The display will be updated by _sync_player_ship_from_real() on next update
        else:
            # Fallback: just update display if no ship_os
            self.log_command(f"Moving {crew_name} to {target_room_name}...")

            # Find which room the crew is currently in
            current_room = None
            for room in self.player_ship.rooms:
                if crew_name in room.crew:
                    current_room = room
                    break

            # Find the target room
            target_room = None
            for room in self.player_ship.rooms:
                if room.name == target_room_name:
                    target_room = room
                    break

            # Move the crew in display only
            if current_room and target_room and current_room != target_room:
                current_room.crew.remove(crew_name)
                target_room.crew.append(crew_name)
                self.log_command(f"✓ {crew_name} moved to {target_room_name}")
            elif not current_room:
                self.log_command(f"✗ Error: {crew_name} not found")
            elif not target_room:
                self.log_command(f"✗ Error: {target_room_name} not found")
            else:
                self.log_command(f"✗ {crew_name} already in {target_room_name}")

    def set_enemy_ship(self, enemy_layout):
        """Set enemy ship to display"""
        self.enemy_ship = enemy_layout
        self.show_enemy = True

    def clear_enemy(self):
        """Remove enemy ship"""
        self.enemy_ship = None
        self.show_enemy = False

    def fire_weapon(self, weapon_type="laser", target_room_name=None):
        """Animate weapon fire from player to enemy"""
        if self.enemy_ship:
            # Find player weapon room position
            weapon_room_x = self.player_x + 200  # Approximate weapons room
            weapon_room_y = self.player_y + 60

            # Find target room position if specified
            target_x = self.enemy_x + 50
            target_y = self.enemy_y + 60
            if target_room_name:
                for room in self.enemy_ship.rooms:
                    if room.name == target_room_name:
                        target_x = self.enemy_x + (room.x + room.width / 2) * self.room_size
                        target_y = self.enemy_y + 40 + (room.y + room.height / 2) * self.room_size
                        break

            # Create projectile with source and target info
            proj = Projectile(
                weapon_room_x,
                weapon_room_y,
                target_x,
                target_y,
                weapon_type,
                is_enemy=False,
                source_room="Weapons",
                target_room=target_room_name
            )
            self.projectiles.append(proj)

    def fire_enemy_weapon(self, weapon_type="laser", target_room_name=None):
        """Animate weapon fire from enemy to player"""
        if self.enemy_ship and self.player_ship:
            # Find enemy weapon room position
            enemy_weapon_room_x = self.enemy_x + 50
            enemy_weapon_room_y = self.enemy_y + 60

            # Find target room position if specified
            target_x = self.player_x + 120
            target_y = self.player_y + 60
            if target_room_name:
                for room in self.player_ship.rooms:
                    if room.name == target_room_name:
                        target_x = self.player_x + (room.x + room.width / 2) * self.room_size
                        target_y = self.player_y + 40 + (room.y + room.height / 2) * self.room_size
                        break

            # Create enemy projectile
            proj = Projectile(
                enemy_weapon_room_x,
                enemy_weapon_room_y,
                target_x,
                target_y,
                weapon_type,
                is_enemy=True,
                source_room="Enemy Weapons",
                target_room=target_room_name
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

        # Update star positions based on ship velocity (warp effect!)
        # Stars move whenever ship has velocity, not just during warp travel
        if self.world_manager and hasattr(self.world_manager, 'ship_os'):
            ship = self.world_manager.ship_os.ship
            # Check velocity instead of is_traveling - stars move during chase too!
            if abs(ship.velocity) > 0.1:
                # Move stars to create motion effect
                # Velocity is in galaxy units/sec, scale it for visual effect
                star_speed = ship.velocity * 20  # Scale for visual effect

                # Move each star
                new_stars = []
                for star_x, star_y, star_size in self.bg_stars:
                    # Move star based on velocity (stars move opposite to ship direction)
                    new_x = star_x + star_speed * dt

                    # Wrap stars around screen edges
                    if new_x < 0:
                        new_x += self.width
                    elif new_x > self.width:
                        new_x -= self.width

                    new_stars.append((new_x, star_y, star_size))

                self.bg_stars = new_stars

    def _render_ship(self, surface, ship, offset_x, offset_y, is_enemy=False, alpha=1.0):
        """Render a single ship's interior with improved visuals

        Args:
            surface: Surface to render on
            ship: Ship to render
            offset_x: X offset for rendering
            offset_y: Y offset for rendering
            is_enemy: Whether this is an enemy ship
            alpha: Opacity (0.0 = invisible, 1.0 = fully visible) for fading
        """
        # Ship color theme
        ship_color = (220, 60, 60) if is_enemy else (60, 220, 120)
        accent_color = (255, 100, 100) if is_enemy else (100, 255, 150)
        glow_color = (255, 150, 150) if is_enemy else (150, 255, 200)

        # If alpha < 1.0, we need to render to a temporary surface first
        if alpha < 1.0:
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))  # Transparent background
            render_target = temp_surface
        else:
            render_target = surface

        # Clear enemy room rects if rendering enemy
        if is_enemy:
            self.enemy_room_rects = {}

        # Calculate ship bounds for hull outline
        min_x = min(room.x for room in ship.rooms) * self.room_size
        max_x = max(room.x + room.width for room in ship.rooms) * self.room_size
        min_y = min(room.y for room in ship.rooms) * self.room_size
        max_y = max(room.y + room.height for room in ship.rooms) * self.room_size

        # Draw ship hull outline with glow effect
        hull_rect = pygame.Rect(
            offset_x + min_x - 8,
            offset_y + min_y - 8,
            max_x - min_x + 16,
            max_y - min_y + 16
        )

        # Glow layers (multiple for effect)
        for i in range(3, 0, -1):
            glow_alpha = 40 * (4 - i)
            glow_surf = pygame.Surface((hull_rect.width + i*4, hull_rect.height + i*4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*glow_color, glow_alpha), glow_surf.get_rect(), border_radius=12)
            surface.blit(glow_surf, (hull_rect.x - i*2, hull_rect.y - i*2))

        # Main hull outline
        pygame.draw.rect(surface, ship_color, hull_rect, 3, border_radius=8)

        # Title with glow effect
        if Theme.FONT_TITLE:
            title_font = pygame.font.SysFont('sans-serif', 20, bold=True)
            title = title_font.render(ship.ship_name, True, accent_color)
            surface.blit(title, (offset_x, offset_y - 35))

            # Show galaxy position if available
            if hasattr(ship, 'galaxy_position'):
                pos_font = pygame.font.SysFont('sans-serif', 14, bold=True)
                pos_text = f"Position: {ship.galaxy_position:.1f} from center"
                pos_color = (150, 200, 255) if not is_enemy else (255, 150, 150)
                pos_surface = pos_font.render(pos_text, True, pos_color)
                surface.blit(pos_surface, (offset_x, offset_y - 15))

        # Hull/Shields bars - moved higher and made bigger
        if Theme.FONT_SMALL:
            bar_y = offset_y - 80  # Moved up from -18
            bar_width = 220  # Wider
            bar_height = 16  # Taller

            # Hull bar with bigger font
            hull_font = pygame.font.SysFont('sans-serif', 18, bold=True)
            hull_label = hull_font.render("HULL", True, (200, 200, 200))
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
            # Text with bigger font
            stats_font = pygame.font.SysFont('sans-serif', 18, bold=True)
            hull_text = stats_font.render(f"{ship.hull}/{ship.max_hull}", True, (255, 255, 255))
            surface.blit(hull_text, (hull_bar_x + bar_width + 5, bar_y))

            # Shield bar
            bar_y += 20  # More spacing
            shield_label = hull_font.render("SHLD", True, (200, 200, 200))
            surface.blit(shield_label, (offset_x, bar_y))

            shield_bar_x = offset_x + 45
            # Background
            pygame.draw.rect(surface, (40, 40, 40), (shield_bar_x, bar_y, bar_width, bar_height))
            # Fill (shields in segments)
            if ship.max_shields > 0:
                segment_width = bar_width // ship.max_shields
                for i in range(ship.shields):
                    seg_x = shield_bar_x + i * segment_width + 2
                    pygame.draw.rect(surface, (100, 150, 255), (seg_x, bar_y + 2, segment_width - 4, bar_height - 4))
            # Border
            pygame.draw.rect(surface, ship_color, (shield_bar_x, bar_y, bar_width, bar_height), 2)
            # Text with bigger font
            shield_text = stats_font.render(f"{ship.shields}/{ship.max_shields}", True, (255, 255, 255))
            surface.blit(shield_text, (shield_bar_x + bar_width + 5, bar_y))

            # Galaxy position info
            bar_y += 22  # More spacing
            pos_font = pygame.font.SysFont('sans-serif', 14, bold=True)

            # Get galaxy position
            if hasattr(ship, 'galaxy_position'):
                galaxy_pos = ship.galaxy_position
                pos_label = pos_font.render(f"POS: {galaxy_pos:.1f} from center", True, (150, 200, 255))
                surface.blit(pos_label, (offset_x, bar_y))

                # If in combat, show enemy range
                if not is_enemy and self.world_manager and self.world_manager.combat_state:
                    combat_state = self.world_manager.combat_state
                    enemy_pos = combat_state.enemy_galaxy_position
                    range_distance = abs(galaxy_pos - enemy_pos)

                    bar_y += 16
                    range_label = pos_font.render(f"ENEMY RANGE: {range_distance:.1f} units", True, (255, 200, 100))
                    surface.blit(range_label, (offset_x, bar_y))

        # Render rooms
        for room in ship.rooms:
            room_x = offset_x + room.x * self.room_size
            room_y = offset_y + room.y * self.room_size
            room_w = room.width * self.room_size
            room_h = room.height * self.room_size

            # Room background with gradient
            room_rect = pygame.Rect(room_x, room_y, room_w, room_h)

            # Base colors
            bg_top = (25, 25, 55)
            bg_bottom = (15, 15, 35)

            # Highlight room if crew is selected (to show it's clickable)
            if self.selected_crew and not is_enemy:
                bg_top = (40, 40, 70)
                bg_bottom = (25, 25, 50)

            # Draw gradient background
            for i in range(room_h):
                blend = i / room_h
                r = int(bg_top[0] * (1 - blend) + bg_bottom[0] * blend)
                g = int(bg_top[1] * (1 - blend) + bg_bottom[1] * blend)
                b = int(bg_top[2] * (1 - blend) + bg_bottom[2] * blend)
                pygame.draw.line(surface, (r, g, b), (room_x, room_y + i), (room_x + room_w, room_y + i))

            # Border color based on health
            border_color = room.get_status_color()

            # Extra bright border if this is a target room (when crew is selected)
            border_width = 3

            # Highlight for targeting (enemy rooms)
            if is_enemy and self.selected_target_room == room.name:
                border_color = (255, 255, 0)  # Yellow for selected target
                border_width = 5

                # Add pulsing glow effect for targeted room
                import time
                pulse = abs((time.time() * 2) % 2 - 1)  # 0 to 1 to 0
                glow_alpha = int(100 + 100 * pulse)
                glow_surf = pygame.Surface((room_w + 12, room_h + 12), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*border_color, glow_alpha), glow_surf.get_rect(), border_radius=4)
                surface.blit(glow_surf, (room_x - 6, room_y - 6))

            # Clickable highlight for enemy rooms (in combat)
            elif is_enemy and self.show_enemy:
                # Store clickable rect for enemy rooms
                self.enemy_room_rects[room.name] = room_rect.copy()

            # Green highlight for friendly targetable rooms (crew movement)
            elif self.selected_crew and not is_enemy:
                border_color = (100, 255, 150)  # Green highlight for targetable rooms
                border_width = 4

                # Add pulsing glow effect for targetable rooms
                import time
                pulse = abs((time.time() * 2) % 2 - 1)  # 0 to 1 to 0
                glow_alpha = int(50 + 50 * pulse)
                glow_surf = pygame.Surface((room_w + 8, room_h + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*border_color, glow_alpha), glow_surf.get_rect(), border_radius=4)
                surface.blit(glow_surf, (room_x - 4, room_y - 4))

            # Main border with rounded corners
            pygame.draw.rect(surface, border_color, room_rect, border_width, border_radius=4)

            # System icon/name
            if room.system_type and Theme.FONT_SMALL:
                # System name
                sys_text = Theme.FONT_SMALL.render(room.system_type.upper(), True, border_color)
                text_x = room_x + (room_w - sys_text.get_width()) // 2
                text_y = room_y + 5
                surface.blit(sys_text, (text_x, text_y))

                # Health bar (bigger and more prominent!)
                health_bar_width = room_w - 10
                health_bar_height = 8  # Doubled from 4px to 8px
                health_bar_x = room_x + 5
                health_bar_y = room_y + room_h - 15

                # Background
                pygame.draw.rect(
                    surface,
                    (40, 40, 40),
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height),
                    border_radius=2
                )

                # Health fill
                health_fill = int((room.health / 100) * health_bar_width)
                pygame.draw.rect(
                    surface,
                    border_color,
                    (health_bar_x, health_bar_y, health_fill, health_bar_height),
                    border_radius=2
                )

                # Border around health bar
                pygame.draw.rect(
                    surface,
                    (100, 100, 100),
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height),
                    1,
                    border_radius=2
                )

                # Show health percentage text if damaged
                if room.health < 100 and Theme.FONT_SMALL:
                    health_font = pygame.font.SysFont('sans-serif', 10, bold=True)
                    health_text = health_font.render(f"{int(room.health)}%", True, (255, 255, 255))
                    text_x = health_bar_x + health_bar_width + 3
                    surface.blit(health_text, (text_x, health_bar_y - 1))

            # Repair progress indicator
            if room.crew and room.health < 100 and not is_enemy and Theme.FONT_SMALL:
                # Show wrench icon when crew is repairing
                repair_font = pygame.font.SysFont('sans-serif', 20, bold=True)
                wrench_text = repair_font.render("🔧", True, (255, 200, 100))

                # Pulsing effect for active repair
                import time
                pulse = abs((time.time() * 3) % 2 - 1)  # 0 to 1 to 0, faster
                alpha = int(150 + 105 * pulse)  # 150 to 255

                # Create wrench with transparency
                wrench_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
                wrench_render = repair_font.render("🔧", True, (*((255, 200, 100)), alpha))

                wrench_x = room_x + room_w - 30
                wrench_y = room_y + 25
                surface.blit(wrench_text, (wrench_x, wrench_y))

                # Repair progress text
                progress_font = pygame.font.SysFont('sans-serif', 9, bold=True)
                repair_text = progress_font.render("REPAIRING", True, (255, 200, 100))
                surface.blit(repair_text, (room_x + 5, room_y + 18))

            # Crew indicators (interactive!)
            if room.crew and Theme.FONT_SMALL:
                crew_y = room_y + room_h - 25
                for i, crew_name in enumerate(room.crew):
                    # Crew icon position
                    crew_x = room_x + 15 + (i * 28)

                    # Determine if this crew is selected
                    is_selected = (self.selected_crew == crew_name)

                    # Draw crew indicator (larger and more visible)
                    crew_size = 10
                    crew_color = (255, 255, 100) if is_selected else (100, 200, 255)

                    # Clickable rect for crew (larger hit area)
                    crew_rect = pygame.Rect(crew_x - crew_size - 2, crew_y - crew_size - 2,
                                          (crew_size + 2) * 2, (crew_size + 2) * 2)
                    self.crew_rects[crew_name] = crew_rect

                    # Draw crew icon with glow
                    if is_selected:
                        # Glowing selection halo
                        for r in range(crew_size + 6, crew_size, -1):
                            alpha = int(100 * ((r - crew_size) / 6))
                            glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                            pygame.draw.circle(glow_surf, (*crew_color, alpha), (r, r), r)
                            surface.blit(glow_surf, (crew_x - r, crew_y - r))

                    # Outer rim (dark)
                    pygame.draw.circle(surface, (20, 20, 20), (crew_x, crew_y), crew_size + 2)

                    # Main crew icon
                    pygame.draw.circle(surface, crew_color, (crew_x, crew_y), crew_size)

                    # Inner highlight
                    pygame.draw.circle(surface, (255, 255, 255), (crew_x - 2, crew_y - 2), 3)

                    # Selection ring
                    if is_selected:
                        pygame.draw.circle(surface, (255, 255, 0), (crew_x, crew_y), crew_size + 4, 2)

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
        """Render weapon projectiles with source and impact indicators"""
        for proj in self.projectiles:
            # Determine projectile color based on who fired it
            if proj.is_enemy:
                # Enemy shots are orange/red
                proj_color = (255, 100, 50)
                trail_color = (255, 150, 100)
            else:
                # Player shots are blue/cyan
                proj_color = (50, 150, 255)
                trail_color = (100, 200, 255)

            if proj.has_hit:
                # Show impact effect
                import time
                pulse = abs((time.time() * 10) % 2 - 1)  # Fast pulse
                impact_radius = int(8 + pulse * 8)  # 8-16 pixels
                impact_alpha = int((1.0 - pulse) * 200)  # Fade out

                # Draw expanding impact circle
                impact_surf = pygame.Surface((impact_radius*2, impact_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(impact_surf, (*proj_color, impact_alpha),
                                 (impact_radius, impact_radius), impact_radius)
                surface.blit(impact_surf, (int(proj.target_x - impact_radius),
                                          int(proj.target_y - impact_radius)))

                # Draw flash at impact point
                flash_color = (255, 255, 255)
                pygame.draw.circle(surface, flash_color, (int(proj.target_x), int(proj.target_y)),
                                 int(4 * (1.0 - pulse)))
            else:
                # Draw source indicator (small glow at origin)
                source_glow_radius = 6
                source_surf = pygame.Surface((source_glow_radius*2, source_glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(source_surf, (*proj_color, 100),
                                 (source_glow_radius, source_glow_radius), source_glow_radius)
                surface.blit(source_surf, (int(proj.start_x - source_glow_radius),
                                          int(proj.start_y - source_glow_radius)))

                # Draw target indicator (pulsing reticle at target)
                import time
                pulse = abs((time.time() * 3) % 2 - 1)  # Pulse effect
                reticle_size = int(8 + pulse * 4)
                reticle_alpha = int(100 + pulse * 100)

                # Draw crosshair at target
                reticle_surf = pygame.Surface((reticle_size*2, reticle_size*2), pygame.SRCALPHA)
                # Vertical line
                pygame.draw.line(reticle_surf, (*proj_color, reticle_alpha),
                               (reticle_size, reticle_size - reticle_size//2),
                               (reticle_size, reticle_size + reticle_size//2), 2)
                # Horizontal line
                pygame.draw.line(reticle_surf, (*proj_color, reticle_alpha),
                               (reticle_size - reticle_size//2, reticle_size),
                               (reticle_size + reticle_size//2, reticle_size), 2)
                # Circle
                pygame.draw.circle(reticle_surf, (*proj_color, reticle_alpha),
                                 (reticle_size, reticle_size), reticle_size//2, 2)
                surface.blit(reticle_surf, (int(proj.target_x - reticle_size),
                                           int(proj.target_y - reticle_size)))

                # Draw projectile
                if proj.type == "laser":
                    # Laser beam
                    pygame.draw.circle(surface, proj_color, (int(proj.x), int(proj.y)), 4)
                    # Trail
                    trail_length = 20
                    dx = proj.target_x - proj.start_x
                    dy = proj.target_y - proj.start_y
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        trail_start_x = proj.x - dx * trail_length
                        trail_start_y = proj.y - dy * trail_length
                        pygame.draw.line(
                            surface,
                            trail_color,
                            (trail_start_x, trail_start_y),
                            (proj.x, proj.y),
                            3
                        )
                    # Core glow
                    glow_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*proj_color, 150), (6, 6), 6)
                    surface.blit(glow_surf, (int(proj.x - 6), int(proj.y - 6)))

                elif proj.type == "missile":
                    # Missile with exhaust trail
                    pygame.draw.circle(surface, (255, 200, 0), (int(proj.x), int(proj.y)), 5)
                    # Exhaust
                    dx = proj.target_x - proj.start_x
                    dy = proj.target_y - proj.start_y
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        for i in range(3):
                            trail_x = proj.x - dx * (i * 8)
                            trail_y = proj.y - dy * (i * 8)
                            alpha = 200 - i * 60
                            exhaust_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                            pygame.draw.circle(exhaust_surf, (255, 150, 50, alpha), (4, 4), 4 - i)
                            surface.blit(exhaust_surf, (int(trail_x - 4), int(trail_y - 4)))

    def _render_distance_indicator(self, surface, combat_state):
        """Render distance indicator - shows galaxy distance or weapon range"""
        center_x = (self.player_x + 200 + self.enemy_x) // 2
        center_y = 80

        # Calculate galaxy distance
        galaxy_distance = abs(combat_state.player_galaxy_position - combat_state.enemy_galaxy_position)

        if not combat_state.active:
            # Not engaged - show galaxy distance to enemy
            panel_width = 280
            panel_height = 70
            panel_x = center_x - panel_width // 2
            panel_y = center_y - panel_height // 2

            pygame.draw.rect(surface, (20, 20, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=8)
            pygame.draw.rect(surface, (255, 153, 0), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=8)

            if Theme.FONT_SMALL:
                title_font = pygame.font.SysFont('sans-serif', 16, bold=True)
                title = title_font.render("ENEMY DISTANCE", True, (255, 153, 0))
                title_rect = title.get_rect(center=(center_x, panel_y + 15))
                surface.blit(title, title_rect)

                dist_font = pygame.font.SysFont('sans-serif', 20, bold=True)
                if galaxy_distance >= combat_state.sensor_range:
                    dist_color = (100, 255, 100)  # Green - escaped!
                    dist_text = f"{galaxy_distance:.1f}u - ESCAPED!"
                elif galaxy_distance > combat_state.engagement_range:
                    dist_color = (255, 200, 100)  # Orange - can warp away
                    dist_text = f"{galaxy_distance:.1f}u - Use warp to escape"
                else:
                    dist_color = (255, 100, 100)  # Red - will engage
                    dist_text = f"{galaxy_distance:.1f}u - ENGAGING!"

                dist_surface = dist_font.render(dist_text, True, dist_color)
                dist_rect = dist_surface.get_rect(center=(center_x, panel_y + 45))
                surface.blit(dist_surface, dist_rect)
        else:
            # Active combat - show weapon range
            combat_distance = combat_state.combat_distance

            panel_width = 220
            panel_height = 60
            panel_x = center_x - panel_width // 2
            panel_y = center_y - panel_height // 2

            pygame.draw.rect(surface, (20, 20, 40), (panel_x, panel_y, panel_width, panel_height), border_radius=8)
            pygame.draw.rect(surface, (255, 153, 0), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=8)

            if Theme.FONT_SMALL:
                title_font = pygame.font.SysFont('sans-serif', 14, bold=True)
                title = title_font.render("WEAPON RANGE", True, (255, 153, 0))
                title_rect = title.get_rect(center=(center_x, panel_y + 12))
                surface.blit(title, title_rect)

                dist_font = pygame.font.SysFont('sans-serif', 22, bold=True)
                dist_text = f"{combat_distance:.1f} units"
                dist_color = (100, 255, 150)

                dist_surface = dist_font.render(dist_text, True, dist_color)
                dist_rect = dist_surface.get_rect(center=(center_x, panel_y + 38))
                surface.blit(dist_surface, dist_rect)

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
            # Check if clicking beacon button
            if self.beacon_button and self.beacon_button.collidepoint(mouse_pos):
                play_sound("click", 0.3)
                # Toggle beacon
                new_state = 0 if self.beacon_active else 1
                command = f"echo {new_state} > /dev/ship/beacon"
                self.log_command(f"$ {command}")

                if self.ship_os:
                    exit_code, stdout, stderr = self.ship_os.execute_command(command)
                    self.beacon_active = not self.beacon_active
                    status = "ACTIVE" if self.beacon_active else "INACTIVE"
                    self.log_command(f"Distress Beacon: {status}")
                    if self.beacon_active:
                        self.log_command("⚠️  WARNING: Will attract enemies!")

                return True

            # Check navigation buttons
            if self.nav_btn_warp_toward and self.nav_btn_warp_toward.collidepoint(mouse_pos):
                play_sound("click", 0.3)
                self._execute_nav_command("warp_to_center", "Warping toward center...")
                return True

            if self.nav_btn_warp_away and self.nav_btn_warp_away.collidepoint(mouse_pos):
                play_sound("click", 0.3)
                self._execute_nav_command("warp_from_center", "Warping away from center...")
                return True

            if self.nav_btn_stop and self.nav_btn_stop.collidepoint(mouse_pos):
                play_sound("click", 0.3)
                self._execute_nav_command("stop", "Emergency stop...")
                return True

            # Check if clicking weapon buttons (combat controls)
            for weapon_idx, button_rect in self.weapon_buttons:
                if button_rect.collidepoint(mouse_pos):
                    play_sound("click", 0.4)
                    self._fire_weapon(weapon_idx)
                    return True

            # Check if clicking on enemy rooms (targeting)
            if self.show_enemy:
                for room_name, rect in self.enemy_room_rects.items():
                    if rect.collidepoint(mouse_pos):
                        play_sound("select", 0.3)
                        self.selected_target_room = room_name

                        # Execute actual command and show it
                        command = f"target {room_name}"
                        self.log_command(f"$ {command}")

                        if self.ship_os:
                            exit_code, stdout, stderr = self.ship_os.execute_command(command)
                            if stdout:
                                for line in stdout.strip().split('\n'):
                                    self.log_command(line)

                        return True

            # Check if clicking on crew
            for crew_name, rect in self.crew_rects.items():
                if rect.collidepoint(mouse_pos):
                    play_sound("select", 0.3)
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

    def _fire_weapon(self, weapon_index):
        """Fire a weapon at the selected target"""
        if not self.world_manager or not self.world_manager.combat_state:
            self.log_command("No combat active!")
            return

        # Execute actual command and show it
        weapon_num = weapon_index + 1  # Convert to 1-based for user
        command = f"fire {weapon_num}"
        self.log_command(f"$ {command}")

        if self.ship_os:
            exit_code, stdout, stderr = self.ship_os.execute_command(command)
            if stdout:
                for line in stdout.strip().split('\n'):
                    self.log_command(line)
            if stderr:
                for line in stderr.strip().split('\n'):
                    self.log_command(f"ERROR: {line}")

        # Animate projectile
        combat_state = self.world_manager.combat_state
        if weapon_index < len(combat_state.player_ship.weapons):
            weapon = combat_state.player_ship.weapons[weapon_index]
            if weapon.is_ready():
                # Fire weapon with target room info for animation
                self.fire_weapon(
                    weapon.weapon_type if hasattr(weapon, 'weapon_type') else "laser",
                    self.selected_target_room
                )

    def _execute_nav_command(self, command, message):
        """Execute a navigation command"""
        self.log_command(message)
        if self.ship_os:
            exit_code, stdout, stderr = self.ship_os.execute_command(command)
            if stdout:
                for line in stdout.strip().split('\n'):
                    self.log_command(line)
            if stderr:
                for line in stderr.strip().split('\n'):
                    self.log_command(f"ERROR: {line}")

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

        # Clear surface with space background
        self.surface.fill((5, 5, 20))

        # Draw background stars
        for star_x, star_y, star_size in self.bg_stars:
            brightness = random.randint(150, 255)
            star_color = (brightness, brightness, brightness)
            # Convert to integers for pygame
            star_x_int = int(star_x)
            star_y_int = int(star_y)
            if star_size == 1:
                self.surface.set_at((star_x_int, star_y_int), star_color)
            else:
                pygame.draw.circle(self.surface, star_color, (star_x_int, star_y_int), star_size // 2)

        # Calculate main display area (leaving room for command log)
        main_height = self.height - self.command_log_height

        # Title bar with LCARS styling
        title_bar_height = 30
        pygame.draw.rect(self.surface, (255, 153, 0), (0, 0, self.width, title_bar_height))
        if Theme.FONT_TITLE:
            title_font = pygame.font.SysFont('sans-serif', 18, bold=True)
            title = title_font.render("◄◄ TACTICAL DISPLAY ►►", True, (0, 0, 0))
            title_rect = title.get_rect(center=(self.width // 2, title_bar_height // 2))
            self.surface.blit(title, title_rect)

        # Render player ship
        self._render_ship(self.surface, self.player_ship, self.player_x, self.player_y + 40, False)

        # Render enemy ship if present
        if self.show_enemy and self.enemy_ship:
            # Calculate enemy fade based on distance
            enemy_alpha = 1.0
            if self.world_manager and self.world_manager.combat_state:
                combat_state = self.world_manager.combat_state
                # Calculate galaxy distance
                distance = abs(combat_state.player_galaxy_position - combat_state.enemy_galaxy_position)
                sensor_range = combat_state.sensor_range

                # Fade enemy as they approach sensor range
                # Start fading at 70% of sensor range (21 units for 30 unit range)
                fade_start = sensor_range * 0.7
                if distance > fade_start:
                    # Linear fade from 1.0 to 0.0 as distance goes from fade_start to sensor_range
                    fade_amount = (distance - fade_start) / (sensor_range - fade_start)
                    enemy_alpha = max(0.0, 1.0 - fade_amount)

            self._render_ship(self.surface, self.enemy_ship, self.enemy_x, self.enemy_y + 40, True, alpha=enemy_alpha)

            # Render distance indicator (between ships)
            if self.world_manager and self.world_manager.combat_state:
                self._render_distance_indicator(self.surface, self.world_manager.combat_state)

        # Render projectiles
        self._render_projectiles(self.surface)

        # Render command log section at bottom
        self._render_command_log(self.surface, main_height)

        return self.surface

    def _render_command_log(self, surface, y_start):
        """Render the command log and weapon controls at the bottom"""
        # Background for command log
        log_rect = pygame.Rect(0, y_start, self.width, self.command_log_height)
        pygame.draw.rect(surface, (10, 10, 30), log_rect)

        # Border
        pygame.draw.rect(surface, (255, 153, 0), log_rect, 2)

        # Navigation buttons (galaxy map controls) - top right area
        nav_button_width = 140
        nav_button_height = 28
        nav_button_spacing = 5
        nav_start_x = self.width - nav_button_width - 10

        # Beacon button (always visible) - above nav buttons
        beacon_button_width = 140
        beacon_button_height = 28
        self.beacon_button = pygame.Rect(
            nav_start_x,
            y_start + 5,
            beacon_button_width,
            beacon_button_height
        )

        # Draw beacon button
        beacon_color = (255, 50, 50) if self.beacon_active else (100, 100, 100)
        pygame.draw.rect(surface, beacon_color, self.beacon_button, border_radius=4)
        pygame.draw.rect(surface, (255, 153, 0), self.beacon_button, 2, border_radius=4)

        if Theme.FONT_SMALL:
            beacon_font = pygame.font.SysFont('sans-serif', 14, bold=True)
            beacon_text = "📡 BEACON: ON" if self.beacon_active else "📡 BEACON: OFF"
            beacon_surface = beacon_font.render(beacon_text, True, (255, 255, 255))
            text_rect = beacon_surface.get_rect(center=self.beacon_button.center)
            surface.blit(beacon_surface, text_rect)

        # Navigation buttons
        nav_y = y_start + 5 + beacon_button_height + nav_button_spacing

        # Warp toward center button
        self.nav_btn_warp_toward = pygame.Rect(
            nav_start_x,
            nav_y,
            nav_button_width,
            nav_button_height
        )
        pygame.draw.rect(surface, (50, 100, 200), self.nav_btn_warp_toward, border_radius=4)
        pygame.draw.rect(surface, (100, 150, 255), self.nav_btn_warp_toward, 2, border_radius=4)
        if Theme.FONT_SMALL:
            nav_font = pygame.font.SysFont('sans-serif', 12, bold=True)
            nav_text = nav_font.render("→ TOWARD CENTER", True, (255, 255, 255))
            text_rect = nav_text.get_rect(center=self.nav_btn_warp_toward.center)
            surface.blit(nav_text, text_rect)

        # Warp away from center button
        nav_y += nav_button_height + nav_button_spacing
        self.nav_btn_warp_away = pygame.Rect(
            nav_start_x,
            nav_y,
            nav_button_width,
            nav_button_height
        )
        pygame.draw.rect(surface, (50, 100, 200), self.nav_btn_warp_away, border_radius=4)
        pygame.draw.rect(surface, (100, 150, 255), self.nav_btn_warp_away, 2, border_radius=4)
        if Theme.FONT_SMALL:
            nav_text = nav_font.render("← AWAY FROM CENTER", True, (255, 255, 255))
            text_rect = nav_text.get_rect(center=self.nav_btn_warp_away.center)
            surface.blit(nav_text, text_rect)

        # Stop button
        nav_y += nav_button_height + nav_button_spacing
        self.nav_btn_stop = pygame.Rect(
            nav_start_x,
            nav_y,
            nav_button_width,
            nav_button_height
        )
        pygame.draw.rect(surface, (150, 50, 50), self.nav_btn_stop, border_radius=4)
        pygame.draw.rect(surface, (255, 100, 100), self.nav_btn_stop, 2, border_radius=4)
        if Theme.FONT_SMALL:
            nav_text = nav_font.render("■ STOP", True, (255, 255, 255))
            text_rect = nav_text.get_rect(center=self.nav_btn_stop.center)
            surface.blit(nav_text, text_rect)

        # Left side: Weapon controls (if in combat)
        weapons_width = self.width // 2
        if self.world_manager and self.world_manager.is_in_combat():
            # Weapons section
            weapons_rect = pygame.Rect(8, y_start + 4, weapons_width - 16, self.command_log_height - 8)
            pygame.draw.rect(surface, (20, 20, 50), weapons_rect, border_radius=4)

            if Theme.FONT_SMALL:
                title = Theme.FONT_SMALL.render("WEAPONS", True, (255, 153, 0))
                surface.blit(title, (weapons_rect.x + 4, weapons_rect.y + 2))

                # Target info
                target_y = weapons_rect.y + 20
                if self.selected_target_room:
                    target_text = Theme.FONT_SMALL.render(f"Target: {self.selected_target_room}", True, (255, 255, 100))
                else:
                    target_text = Theme.FONT_SMALL.render("Target: None (click enemy room)", True, (150, 150, 150))
                surface.blit(target_text, (weapons_rect.x + 4, target_y))

            # Weapon buttons
            self.weapon_buttons = []
            combat_state = self.world_manager.combat_state
            if combat_state:
                button_y = weapons_rect.y + 45
                for i, weapon in enumerate(combat_state.player_ship.weapons):
                    # Weapon button
                    button_rect = pygame.Rect(weapons_rect.x + 4, button_y, weapons_width - 24, 28)
                    self.weapon_buttons.append((i, button_rect))

                    # Button color based on ready state
                    if weapon.is_ready():
                        btn_color = (60, 160, 60)  # Green - ready
                        text_color = (255, 255, 255)
                    else:
                        btn_color = (80, 80, 80)  # Gray - charging
                        text_color = (150, 150, 150)

                    pygame.draw.rect(surface, btn_color, button_rect, border_radius=4)
                    pygame.draw.rect(surface, (100, 255, 100) if weapon.is_ready() else (100, 100, 100),
                                   button_rect, 2, border_radius=4)

                    # Weapon info
                    if Theme.FONT_SMALL:
                        if weapon.is_ready():
                            status = "READY"
                        else:
                            time_remaining = (1.0 - weapon.charge) * weapon.cooldown_time
                            status = f"{time_remaining:.1f}s"
                        weapon_text = Theme.FONT_SMALL.render(
                            f"{i+1}. {weapon.name} - {status}",
                            True, text_color
                        )
                        surface.blit(weapon_text, (button_rect.x + 4, button_rect.y + 8))

                    button_y += 32

        # Right side: Command log (ensure it doesn't overlap navigation buttons)
        log_x = weapons_width + 8
        # Calculate max width for log text to avoid nav buttons
        nav_button_start = self.width - 150  # Nav buttons start at width - 140 - 10
        max_log_width = nav_button_start - log_x - 10  # Leave 10px gap

        if Theme.FONT_SMALL:
            title = Theme.FONT_SMALL.render("COMBAT LOG", True, (255, 153, 0))
            surface.blit(title, (log_x, y_start + 4))

        # Render command lines (truncate if too long to avoid overlap)
        if Theme.FONT_TERMINAL:
            line_y = y_start + 22
            for cmd in self.command_log[-5:]:  # Only last 5 lines
                # Truncate command if it would overlap with nav buttons
                truncated_cmd = cmd
                cmd_surface = Theme.FONT_TERMINAL.render(truncated_cmd, True, (100, 255, 150))

                # If text is too wide, truncate it
                while cmd_surface.get_width() > max_log_width and len(truncated_cmd) > 0:
                    truncated_cmd = truncated_cmd[:-4] + "..."
                    cmd_surface = Theme.FONT_TERMINAL.render(truncated_cmd, True, (100, 255, 150))

                surface.blit(cmd_surface, (log_x, line_y))
                line_y += 18

        # Hint text if no commands
        if not self.command_log and Theme.FONT_SMALL:
            if self.world_manager and self.world_manager.is_in_combat():
                hint_text = "Click enemy rooms to target, click weapons to fire"
            else:
                hint_text = "Click crew to select, click rooms to move crew"

            # Truncate hint if needed
            hint = Theme.FONT_SMALL.render(hint_text, True, (100, 100, 100))
            while hint.get_width() > max_log_width and len(hint_text) > 0:
                hint_text = hint_text[:-4] + "..."
                hint = Theme.FONT_SMALL.render(hint_text, True, (100, 100, 100))

            surface.blit(hint, (log_x, y_start + 50))

    def update_player_ship(self, ship_data):
        """Update player ship from game data"""
        self.player_ship.update_from_ship_data(ship_data)

    def update_enemy_ship(self, ship_data):
        """Update enemy ship from game data"""
        if self.enemy_ship:
            self.enemy_ship.update_from_ship_data(ship_data)

    def _sync_player_ship_from_real(self, real_ship):
        """Sync player ship display with actual ship state (room health, crew positions)"""
        # Create mapping of system type to display room
        system_to_display_room = {}
        for room in self.player_ship.rooms:
            if room.system_type:
                system_to_display_room[room.system_type] = room

        # Update room health and conditions from real ship
        for room_name, real_room in real_ship.rooms.items():
            system_type = real_room.system_type.value if real_room.system_type else None
            if system_type in system_to_display_room:
                display_room = system_to_display_room[system_type]
                # Update health (convert 0.0-1.0 to 0-100)
                display_room.health = int(real_room.health * 100)
                # Update conditions
                display_room.on_fire = real_room.on_fire
                display_room.breached = real_room.breached

        # Update crew positions from real ship
        # First clear all crew from rooms
        for room in self.player_ship.rooms:
            room.crew = []

        # Then reassign crew to their actual rooms
        for crew_member in real_ship.crew:
            if crew_member.room and crew_member.is_alive:
                # Find display room by system type
                system_type = crew_member.room.system_type.value if crew_member.room.system_type else None
                if system_type in system_to_display_room:
                    display_room = system_to_display_room[system_type]
                    if crew_member.name not in display_room.crew:
                        display_room.crew.append(crew_member.name)

    def update_from_combat(self, combat_state):
        """Update tactical display from combat state"""
        if combat_state and combat_state.active:
            # Check if enemy is destroyed - hide immediately even if combat is still "active"
            if combat_state.enemy_ship.hull <= 0:
                self.enemy_ship = None
                self.show_enemy = False
                self.selected_target_room = None
                return

            # Show enemy
            if not self.enemy_ship:
                self.enemy_ship = ShipLayout(combat_state.enemy_ship.name)

            # Update enemy ship stats
            self.enemy_ship.hull = int(combat_state.enemy_ship.hull)
            self.enemy_ship.max_hull = combat_state.enemy_ship.hull_max
            self.enemy_ship.shields = int(combat_state.enemy_ship.shields)
            self.enemy_ship.max_shields = combat_state.enemy_ship.shields_max
            self.enemy_ship.ship_name = combat_state.enemy_ship.name

            # Update enemy rooms from actual ship
            self.enemy_ship.rooms = []
            for i, (room_name, room) in enumerate(combat_state.enemy_ship.rooms.items()):
                # Create simple grid layout for enemy
                grid_x = i % 2
                grid_y = i // 2
                ship_room = ShipRoom(room_name, room.system_type.value if room.system_type else None,
                                    grid_x, grid_y, 1, 1)
                ship_room.health = int(room.health * 100)
                ship_room.on_fire = room.on_fire
                ship_room.breached = room.breached
                self.enemy_ship.rooms.append(ship_room)

            self.show_enemy = True

            # Update player ship stats
            self.player_ship.hull = int(combat_state.player_ship.hull)
            self.player_ship.max_hull = combat_state.player_ship.hull_max
            self.player_ship.shields = int(combat_state.player_ship.shields)
            self.player_ship.max_shields = combat_state.player_ship.shields_max

            # Sync player ship room health and crew from actual ship state
            self._sync_player_ship_from_real(combat_state.player_ship)
        else:
            # No combat - hide enemy
            self.enemy_ship = None
            self.show_enemy = False
            self.selected_target_room = None

            # Still sync player ship state when not in combat
            if self.world_manager and hasattr(self.world_manager, 'ship_os'):
                player_ship = self.world_manager.ship_os.ship
                self._sync_player_ship_from_real(player_ship)

                # Update player stats
                self.player_ship.hull = int(player_ship.hull)
                self.player_ship.max_hull = player_ship.hull_max
                self.player_ship.shields = int(player_ship.shields)
                self.player_ship.max_shields = player_ship.shields_max

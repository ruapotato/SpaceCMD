"""
Ship Info Widget - Displays detailed ship statistics

Shows:
- Hull and shields
- Shield recharge rate
- Power allocation
- Resources (dark matter, missiles, scrap)
- System effectiveness
- Crew status
- Weapon status
"""

import pygame
from .themes import Theme


class ShipInfoWidget:
    """
    Widget that displays comprehensive ship information.

    Similar to FTL's ship info screen, shows all stats and rates.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = None

        # References (set externally)
        self.ship_os = None

        # Scroll state
        self.scroll_y = 0
        self.max_scroll = 0

        # Fonts
        self.font_title = pygame.font.SysFont('monospace', 18, bold=True)
        self.font_normal = pygame.font.SysFont('monospace', 12)
        self.font_small = pygame.font.SysFont('monospace', 10)

    def set_ship_os(self, ship_os):
        """Set ShipOS reference"""
        self.ship_os = ship_os

    def handle_event(self, event, mouse_pos):
        """Handle input events"""
        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 20
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
            return True

        return False

    def update(self, dt):
        """Update widget state"""
        pass

    def render(self):
        """Render the ship info display"""
        if not self.surface or self.surface.get_size() != (self.width, self.height):
            self.surface = pygame.Surface((self.width, self.height))

        # Clear with dark background
        self.surface.fill((10, 10, 20))

        if not self.ship_os:
            # No ship OS - show error
            text = self.font_title.render("NO SHIP DATA", True, (200, 50, 50))
            rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.surface.blit(text, rect)
            return self.surface

        ship = self.ship_os.ship
        y = 10 - self.scroll_y

        # Title
        title = self.font_title.render(f"◄◄ {ship.name.upper()} ►►", True, (255, 153, 0))
        title_rect = title.get_rect(centerx=self.width // 2, y=y)
        self.surface.blit(title, title_rect)
        y += 30

        # Ship class
        class_text = self.font_normal.render(ship.ship_class, True, (150, 150, 150))
        class_rect = class_text.get_rect(centerx=self.width // 2, y=y)
        self.surface.blit(class_text, class_rect)
        y += 25

        # === HULL & SHIELDS ===
        y = self._render_section_header(y, "HULL & SHIELDS")

        # Hull bar
        hull_pct = ship.hull / ship.hull_max
        y = self._render_bar(y, "Hull", ship.hull, ship.hull_max, hull_pct,
                            (50, 200, 50) if hull_pct > 0.5 else (200, 200, 50) if hull_pct > 0.25 else (200, 50, 50))

        # Shields bar
        shield_pct = ship.shields / ship.shields_max if ship.shields_max > 0 else 0
        y = self._render_bar(y, "Shields", int(ship.shields), ship.shields_max, shield_pct, (100, 150, 255))

        # Shield recharge rate
        from core.ship import SystemType
        if SystemType.SHIELDS in ship.systems:
            shields_system = ship.systems[SystemType.SHIELDS]
            if shields_system.room:
                shield_recharge = shields_system.get_effectiveness()
                recharge_text = f"Recharge: {shield_recharge:.2f} /sec"

                if shields_system.is_online():
                    health = shields_system.room.health * 100
                    power = shields_system.room.power_allocated / shields_system.room.max_power * 100
                    crew = shields_system.room.crew_bonus * 100
                    recharge_text += f" (HP:{health:.0f}% × PWR:{power:.0f}% × Crew:+{crew:.0f}%)"
                    color = (100, 255, 100)
                else:
                    recharge_text += " [OFFLINE]"
                    color = (150, 50, 50)

                text_surf = self.font_small.render(recharge_text, True, color)
                self.surface.blit(text_surf, (20, y))
                y += 15

        y += 10

        # === POWER ===
        y = self._render_section_header(y, "POWER")

        power_used = ship.reactor_power - ship.power_available
        power_pct = power_used / ship.reactor_power if ship.reactor_power > 0 else 0
        y = self._render_bar(y, "Reactor", power_used, ship.reactor_power, power_pct, (255, 200, 100))

        avail_text = f"Available: {ship.power_available}"
        text_surf = self.font_small.render(avail_text, True, (150, 150, 150))
        self.surface.blit(text_surf, (20, y))
        y += 20

        # === RESOURCES ===
        y = self._render_section_header(y, "RESOURCES")

        resources = [
            ("Dark Matter:", ship.dark_matter, (150, 100, 255)),
            ("Missiles:", ship.missiles, (255, 150, 100)),
            ("Scrap:", ship.scrap, (255, 200, 100)),
        ]

        for label, value, color in resources:
            text = self.font_normal.render(f"{label:15} {value}", True, color)
            self.surface.blit(text, (20, y))
            y += 18

        y += 10

        # === SYSTEMS ===
        y = self._render_section_header(y, "SYSTEMS")

        for system_type, system in ship.systems.items():
            if system_type == SystemType.NONE or not system.room:
                continue

            room = system.room
            effectiveness = system.get_effectiveness()
            status_color = (100, 255, 100) if system.is_online() else (150, 50, 50)

            # System name and status
            name = system_type.value.capitalize()
            status = "ONLINE" if system.is_online() else "OFFLINE"

            name_text = self.font_normal.render(f"{name:12} [{status}]", True, status_color)
            self.surface.blit(name_text, (20, y))

            # Stats
            stats = f"PWR:{room.power_allocated}/{room.max_power} HP:{room.health:.0%} EFF:{effectiveness:.0%}"
            stats_text = self.font_small.render(stats, True, (150, 150, 150))
            self.surface.blit(stats_text, (220, y + 2))

            y += 18

        y += 10

        # === CREW ===
        y = self._render_section_header(y, f"CREW ({len(ship.crew)})")

        for crew in ship.crew:
            location = crew.room.name if crew.room else "Unassigned"
            hp_pct = crew.health / crew.health_max
            hp_color = (100, 255, 100) if hp_pct > 0.7 else (255, 200, 100) if hp_pct > 0.3 else (255, 50, 50)

            crew_text = f"{crew.name:20} @ {location:12}"
            text_surf = self.font_small.render(crew_text, True, (200, 200, 200))
            self.surface.blit(text_surf, (20, y))

            hp_text = f"HP:{crew.health:.0f}"
            hp_surf = self.font_small.render(hp_text, True, hp_color)
            self.surface.blit(hp_surf, (350, y))

            y += 15

        y += 10

        # === WEAPONS ===
        y = self._render_section_header(y, f"WEAPONS ({len(ship.weapons)})")

        if ship.weapons:
            for i, weapon in enumerate(ship.weapons):
                charge_pct = weapon.charge
                status_color = (100, 255, 100) if weapon.is_ready() else (200, 200, 50)

                weapon_text = f"{i+1}. {weapon.name:18}"
                text_surf = self.font_normal.render(weapon_text, True, (200, 200, 200))
                self.surface.blit(text_surf, (20, y))

                stats = f"DMG:{weapon.damage} CD:{weapon.cooldown_time:.1f}s"
                stats_surf = self.font_small.render(stats, True, (150, 150, 150))
                self.surface.blit(stats_surf, (250, y + 2))

                # Charge bar
                bar_x = 370
                bar_y = y + 3
                bar_width = 80
                bar_height = 12

                pygame.draw.rect(self.surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                if charge_pct > 0:
                    fill_width = int(bar_width * charge_pct)
                    pygame.draw.rect(self.surface, status_color, (bar_x, bar_y, fill_width, bar_height))
                pygame.draw.rect(self.surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

                # Status text
                status = "READY" if weapon.is_ready() else f"{charge_pct*100:.0f}%"
                status_surf = self.font_small.render(status, True, status_color)
                status_rect = status_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
                self.surface.blit(status_surf, status_rect)

                y += 22
        else:
            text_surf = self.font_small.render("No weapons installed", True, (150, 50, 50))
            self.surface.blit(text_surf, (20, y))
            y += 20

        # Update max scroll
        self.max_scroll = max(0, y - self.height + 20)

        # Scroll indicator
        if self.max_scroll > 0:
            scroll_pct = self.scroll_y / self.max_scroll
            indicator_height = max(20, int(self.height * (self.height / (y + 20))))
            indicator_y = int((self.height - indicator_height) * scroll_pct)

            pygame.draw.rect(self.surface, (100, 100, 100),
                           (self.width - 10, indicator_y, 8, indicator_height), border_radius=4)

        return self.surface

    def _render_section_header(self, y, text):
        """Render a section header"""
        header = self.font_normal.render(f"=== {text} ===", True, (255, 153, 0))
        self.surface.blit(header, (10, y))
        return y + 22

    def _render_bar(self, y, label, current, maximum, percent, color):
        """Render a labeled progress bar"""
        # Label
        label_text = f"{label}:"
        text_surf = self.font_normal.render(label_text, True, (200, 200, 200))
        self.surface.blit(text_surf, (20, y))

        # Value
        value_text = f"{current:.0f}/{maximum}"
        value_surf = self.font_normal.render(value_text, True, (150, 150, 150))
        self.surface.blit(value_surf, (150, y))

        # Bar
        bar_x = 250
        bar_width = self.width - bar_x - 30
        bar_height = 16

        # Background
        pygame.draw.rect(self.surface, (30, 30, 30), (bar_x, y, bar_width, bar_height))

        # Fill
        if percent > 0:
            fill_width = int(bar_width * percent)
            pygame.draw.rect(self.surface, color, (bar_x, y, fill_width, bar_height))

        # Border
        pygame.draw.rect(self.surface, (100, 100, 100), (bar_x, y, bar_width, bar_height), 1)

        # Percentage
        pct_text = f"{percent*100:.0f}%"
        pct_surf = self.font_small.render(pct_text, True, (255, 255, 255))
        pct_rect = pct_surf.get_rect(center=(bar_x + bar_width // 2, y + bar_height // 2))
        self.surface.blit(pct_surf, pct_rect)

        return y + 20

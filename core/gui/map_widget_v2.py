"""
Galaxy Map Widget V2 - Complete Redesign

FTL-style vertical progression map with clear purpose:
- Shows current sector and path forward
- Visual node types with icons
- Reward previews
- Clear linear progression through sectors
"""

import pygame
import random
from .themes import Theme

# Node type colors and icons
NODE_STYLES = {
    "combat": {"color": (200, 50, 50), "icon": "⚔️", "name": "HOSTILE"},
    "elite": {"color": (150, 30, 30), "icon": "💀", "name": "ELITE ENEMY"},
    "store": {"color": (50, 150, 200), "icon": "🛒", "name": "STORE"},
    "event": {"color": (200, 150, 50), "icon": "❓", "name": "UNKNOWN"},
    "distress": {"color": (255, 200, 100), "icon": "📡", "name": "DISTRESS"},
    "repair": {"color": (50, 200, 100), "icon": "🔧", "name": "REPAIR"},
    "nebula": {"color": (150, 50, 200), "icon": "🌫️", "name": "NEBULA"},
    "asteroid": {"color": (120, 120, 120), "icon": "☄️", "name": "ASTEROID"},
    "boss": {"color": (255, 50, 255), "icon": "👑", "name": "BOSS"},
    "empty": {"color": (80, 80, 80), "icon": "·", "name": "EMPTY"},
}


class MapWidgetV2:
    """
    FTL-style galaxy map showing vertical progression through sectors.

    Features:
    - Vertical columns for sectors
    - Clear visual path forward
    - Node type indicators
    - Reward previews
    - Click to jump
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = None

        # References (set externally)
        self.world_manager = None
        self.ship_os = None

        # Visual settings (base values)
        self.base_node_radius = 25
        self.base_sector_width = 180
        self.base_node_spacing_y = 80
        self.padding = 40

        # Zoom control
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0

        # Camera/scroll
        self.scroll_x = 0
        self.scroll_y = 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.last_mouse_pos = (0, 0)

        # Command log
        self.command_log = []
        self.max_log_lines = 3

        # Background stars
        self.bg_stars = [(random.randint(0, width), random.randint(0, height),
                         random.randint(1, 2)) for _ in range(50)]

    @property
    def node_radius(self):
        """Get scaled node radius based on zoom"""
        return int(self.base_node_radius * self.zoom)

    @property
    def sector_width(self):
        """Get scaled sector width based on zoom"""
        return int(self.base_sector_width * self.zoom)

    @property
    def node_spacing_y(self):
        """Get scaled node spacing based on zoom"""
        return int(self.base_node_spacing_y * self.zoom)

    def set_world_manager(self, world_manager):
        """Set world manager reference"""
        self.world_manager = world_manager

    def log_command(self, message):
        """Add message to command log"""
        self.command_log.append(message)
        if len(self.command_log) > self.max_log_lines:
            self.command_log.pop(0)

    def handle_event(self, event, mouse_pos):
        """Handle input events"""
        # Mouse wheel zoom
        if event.type == pygame.MOUSEWHEEL:
            old_zoom = self.zoom
            # Zoom in/out
            self.zoom += event.y * 0.1
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

            # Zoom toward mouse cursor
            if self.zoom != old_zoom:
                zoom_factor = self.zoom / old_zoom
                # Adjust scroll to zoom toward mouse
                self.scroll_x = (self.scroll_x - mouse_pos[0]) * zoom_factor + mouse_pos[0]
                self.scroll_y = (self.scroll_y - mouse_pos[1]) * zoom_factor + mouse_pos[1]

            return True

        # Middle mouse button drag for panning
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Middle mouse
            self.dragging = True
            self.drag_start = mouse_pos
            self.last_mouse_pos = mouse_pos
            return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.dragging = False
            return True

        if event.type == pygame.MOUSEMOTION and self.dragging:
            dx = mouse_pos[0] - self.last_mouse_pos[0]
            dy = mouse_pos[1] - self.last_mouse_pos[1]
            self.scroll_x -= dx
            self.scroll_y -= dy
            self.last_mouse_pos = mouse_pos
            return True

        if not self.world_manager:
            return False

        # Left click on nodes
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicking on a node
            current_node = self.world_manager.world_map.get_current_node()
            available = self.world_manager.get_available_jumps()

            # Check each available node
            for node in available:
                node_screen_pos = self._get_node_screen_pos(node)
                if node_screen_pos:
                    nx, ny = node_screen_pos
                    dist = ((mouse_pos[0] - nx)**2 + (mouse_pos[1] - ny)**2)**0.5

                    if dist < self.node_radius:
                        # Jump to this node!
                        command = f"jump {node.id}"
                        self.log_command(f"Jumping to {node.type.value}...")

                        if self.ship_os:
                            exit_code, stdout, stderr = self.ship_os.execute_command(command)
                            if exit_code == 0:
                                self.log_command(f"✓ Arrived at {node.type.value}")
                            else:
                                self.log_command(f"✗ Jump failed!")

                        return True

        return False

    def _get_node_screen_pos(self, node):
        """Get screen position for a node"""
        # Vertical layout: sectors are columns, nodes are rows
        sector_x = self.padding + node.sector * self.sector_width - self.scroll_x

        # Get all nodes in this sector
        sector_nodes = [n for n in self.world_manager.world_map.nodes.values()
                       if n.sector == node.sector]

        # Find index of this node in sector
        try:
            node_idx = sector_nodes.index(node)
        except ValueError:
            return None

        node_y = self.padding + 60 + node_idx * self.node_spacing_y - self.scroll_y

        return (sector_x, node_y)

    def update(self, dt):
        """Update widget state"""
        # Auto-scroll to keep current sector visible
        if self.world_manager:
            current = self.world_manager.world_map.get_current_node()
            if current:
                target_x = current.sector * self.sector_width
                # Smooth scroll
                diff = target_x - self.scroll_x
                self.scroll_x += diff * 0.1

    def render(self):
        """Render the map"""
        if not self.surface or self.surface.get_size() != (self.width, self.height):
            self.surface = pygame.Surface((self.width, self.height))

        # Clear with space background
        self.surface.fill((5, 5, 15))

        # Draw background stars
        for star_x, star_y, star_size in self.bg_stars:
            pygame.draw.circle(self.surface, (100, 100, 120), (star_x, star_y), star_size // 2)

        if not self.world_manager:
            # No world manager - show placeholder
            if Theme.FONT_TITLE:
                text = Theme.FONT_TITLE.render("NO MAP DATA", True, (100, 100, 100))
                rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self.surface.blit(text, rect)
            return self.surface

        # Get current node and available jumps
        current_node = self.world_manager.world_map.get_current_node()
        available_jumps = set(n.id for n in self.world_manager.get_available_jumps())

        # Draw title
        title_font = pygame.font.SysFont('sans-serif', 24, bold=True)
        title = title_font.render("◄◄ GALAXY MAP ►►", True, (255, 153, 0))
        title_rect = title.get_rect(center=(self.width // 2, 20))
        self.surface.blit(title, title_rect)

        # Draw sector headers and progress
        num_sectors = self.world_manager.world_map.num_sectors
        for sector in range(num_sectors):
            sector_x = self.padding + sector * self.sector_width - int(self.scroll_x)

            # Skip if off-screen
            if sector_x < -100 or sector_x > self.width + 100:
                continue

            # Sector header
            sector_label = f"SECTOR {sector + 1}"
            sector_font = pygame.font.SysFont('sans-serif', 16, bold=True)

            # Highlight current sector
            if current_node and current_node.sector == sector:
                color = (255, 200, 100)
                # Draw highlight box
                pygame.draw.rect(self.surface, (60, 40, 0),
                               (sector_x - 20, 45, 160, 25), border_radius=4)
            else:
                color = (150, 150, 150)

            sector_text = sector_font.render(sector_label, True, color)
            text_rect = sector_text.get_rect(center=(sector_x + 60, 57))
            self.surface.blit(sector_text, text_rect)

        # Draw connections between nodes
        for node in self.world_manager.world_map.nodes.values():
            node_pos = self._get_node_screen_pos(node)
            if not node_pos:
                continue

            nx, ny = node_pos

            # Skip if off-screen
            if nx < -50 or nx > self.width + 50 or ny < -50 or ny > self.height + 50:
                continue

            # Draw connections to next sector
            for connected_id in node.connections:
                # Look up the connected node object
                if connected_id not in self.world_manager.world_map.nodes:
                    continue
                connected = self.world_manager.world_map.nodes[connected_id]
                conn_pos = self._get_node_screen_pos(connected)
                if conn_pos:
                    cx, cy = conn_pos

                    # Connection line
                    if node.visited:
                        line_color = (80, 80, 100)  # Dim for visited
                    else:
                        line_color = (120, 120, 140)  # Brighter for unvisited

                    pygame.draw.line(self.surface, line_color, (nx, ny), (cx, cy), 2)

        # Draw nodes
        for node in self.world_manager.world_map.nodes.values():
            node_pos = self._get_node_screen_pos(node)
            if not node_pos:
                continue

            nx, ny = node_pos

            # Skip if off-screen
            if nx < -50 or nx > self.width + 50 or ny < -50 or ny > self.height + 50:
                continue

            # Determine node appearance
            is_current = (current_node and node.id == current_node.id)
            is_available = node.id in available_jumps
            is_visited = node.visited

            # Get node style
            style = NODE_STYLES.get(node.type.value, NODE_STYLES["empty"])
            base_color = style["color"]

            # Modify color based on state
            if is_visited:
                # Dim visited nodes
                node_color = tuple(c // 2 for c in base_color)
            else:
                node_color = base_color

            # Draw node
            if is_current:
                # Current node - pulsing glow
                import time
                pulse = abs((time.time() * 2) % 2 - 1)
                glow_radius = int(self.node_radius + 10 + pulse * 5)
                glow_color = (255, 200, 100)

                # Glow layers
                for r in range(glow_radius, self.node_radius, -2):
                    alpha_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    alpha = int(80 * (glow_radius - r) / (glow_radius - self.node_radius))
                    pygame.draw.circle(alpha_surf, (*glow_color, alpha), (r, r), r)
                    self.surface.blit(alpha_surf, (nx - r, ny - r))

                # Main circle
                pygame.draw.circle(self.surface, (255, 255, 255), (nx, ny), self.node_radius + 3)
                pygame.draw.circle(self.surface, node_color, (nx, ny), self.node_radius)

            elif is_available:
                # Available jump - yellow highlight
                pygame.draw.circle(self.surface, (255, 255, 0), (nx, ny), self.node_radius + 4, 3)
                pygame.draw.circle(self.surface, node_color, (nx, ny), self.node_radius)
                pygame.draw.circle(self.surface, (200, 200, 200), (nx, ny), self.node_radius, 2)

            else:
                # Normal node
                pygame.draw.circle(self.surface, node_color, (nx, ny), self.node_radius)
                if not is_visited:
                    pygame.draw.circle(self.surface, (100, 100, 100), (nx, ny), self.node_radius, 2)

            # Draw icon
            icon_font = pygame.font.SysFont('sans-serif', 24)
            icon = icon_font.render(style["icon"], True, (255, 255, 255))
            icon_rect = icon.get_rect(center=(nx, ny))
            self.surface.blit(icon, icon_rect)

            # Draw node label for available/current nodes
            if is_current or is_available:
                label_font = pygame.font.SysFont('sans-serif', 10, bold=True)
                label = label_font.render(style["name"], True, (255, 255, 255))
                label_rect = label.get_rect(center=(nx, ny + self.node_radius + 10))
                self.surface.blit(label, label_rect)

        # Draw info panel at bottom
        self._render_info_panel()

        return self.surface

    def _render_info_panel(self):
        """Render info panel showing current status and controls"""
        panel_height = 100
        panel_y = self.height - panel_height

        # Background
        pygame.draw.rect(self.surface, (20, 20, 40), (0, panel_y, self.width, panel_height))
        pygame.draw.rect(self.surface, (255, 153, 0), (0, panel_y, self.width, panel_height), 2)

        if not self.world_manager:
            return

        # Current location info
        current = self.world_manager.world_map.get_current_node()
        if current:
            info_font = pygame.font.SysFont('sans-serif', 14, bold=True)
            style = NODE_STYLES.get(current.type.value, NODE_STYLES["empty"])

            location_text = f"CURRENT: {style['icon']} {style['name']} (Sector {current.sector + 1})"
            location_surf = info_font.render(location_text, True, (100, 255, 150))
            self.surface.blit(location_surf, (10, panel_y + 10))

        # Available jumps count
        available = self.world_manager.get_available_jumps()
        if available:
            jumps_text = f"Available jumps: {len(available)}"
            jumps_font = pygame.font.SysFont('sans-serif', 12)
            jumps_surf = jumps_font.render(jumps_text, True, (200, 200, 200))
            self.surface.blit(jumps_surf, (10, panel_y + 35))

        # Command log
        log_font = pygame.font.SysFont('sans-serif', 12)
        log_y = panel_y + 55
        for msg in self.command_log[-3:]:
            log_surf = log_font.render(msg, True, (150, 200, 255))
            self.surface.blit(log_surf, (10, log_y))
            log_y += 15

        # Instructions and zoom info
        hint_font = pygame.font.SysFont('sans-serif', 11)
        hint = hint_font.render("Click yellow nodes to jump • Mouse wheel zoom • Middle-drag pan", True, (120, 120, 120))
        self.surface.blit(hint, (self.width - 450, panel_y + 10))

        # Zoom level
        zoom_text = f"Zoom: {self.zoom:.1f}x"
        zoom_surf = hint_font.render(zoom_text, True, (150, 150, 150))
        self.surface.blit(zoom_surf, (self.width - 100, panel_y + 30))

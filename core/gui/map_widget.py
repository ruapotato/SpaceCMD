"""
Map Widget

Visual display of the world map with sectors, nodes, and navigation.
FTL-style map visualization.
"""

import pygame
import random
from typing import Optional, Dict, Tuple
from .themes import Theme
from ..world_map import NodeType


# Node type colors (FTL-inspired)
NODE_COLORS = {
    NodeType.EMPTY: (100, 100, 100),        # Gray
    NodeType.COMBAT: (200, 50, 50),         # Red
    NodeType.ELITE_COMBAT: (255, 100, 0),   # Orange-red
    NodeType.STORE: (50, 150, 255),         # Blue
    NodeType.EVENT: (150, 255, 150),        # Green
    NodeType.DISTRESS: (255, 200, 0),       # Yellow
    NodeType.NEBULA: (150, 100, 200),       # Purple
    NodeType.ASTEROID: (150, 100, 50),      # Brown
    NodeType.REPAIR: (0, 200, 0),           # Bright green
    NodeType.BOSS: (255, 0, 255),           # Magenta
}


class MapWidget:
    """
    Map visualization widget.

    Shows the galaxy map with nodes, connections, and allows navigation.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = None

        # World manager reference (set externally)
        self.world_manager = None
        self.ship_os = None

        # Map display settings
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.node_size = 20  # Base radius of node circles

        # Node positions cache (screen coordinates)
        self.node_positions: Dict[str, Tuple[int, int]] = {}

        # Interaction
        self.hovered_node_id = None
        self.selected_node_id = None

        # Background stars
        self.bg_stars = [(random.randint(0, width), random.randint(0, height),
                         random.randint(1, 3)) for _ in range(200)]

        # Command log
        self.command_log = []
        self.max_log_lines = 3

    def set_world_manager(self, world_manager):
        """Set the world manager to display"""
        self.world_manager = world_manager
        self._calculate_camera_position()

    def _calculate_camera_position(self):
        """Center camera on current node"""
        if not self.world_manager:
            return

        current = self.world_manager.world_map.get_current_node()
        if not current:
            return

        # Center on current node
        self.camera_x = current.position[0] - self.width // 2
        self.camera_y = current.position[1] - self.height // 2

    def _world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int((world_x - self.camera_x) * self.zoom) + self.width // 2
        screen_y = int((world_y - self.camera_y) * self.zoom) + self.height // 2
        return (screen_x, screen_y)

    def _screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.width // 2) / self.zoom + self.camera_x
        world_y = (screen_y - self.height // 2) / self.zoom + self.camera_y
        return (world_x, world_y)

    def log_command(self, message: str):
        """Add message to command log"""
        self.command_log.append(message)
        if len(self.command_log) > self.max_log_lines:
            self.command_log = self.command_log[-self.max_log_lines:]

    def handle_event(self, event, mouse_pos):
        """Handle input events"""
        if event.type == pygame.MOUSEMOTION:
            # Check if hovering over a node
            self.hovered_node_id = None
            for node_id, screen_pos in self.node_positions.items():
                dx = mouse_pos[0] - screen_pos[0]
                dy = mouse_pos[1] - screen_pos[1]
                dist = (dx*dx + dy*dy) ** 0.5
                if dist < self.node_size:
                    self.hovered_node_id = node_id
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicking on a node
            for node_id, screen_pos in self.node_positions.items():
                dx = mouse_pos[0] - screen_pos[0]
                dy = mouse_pos[1] - screen_pos[1]
                dist = (dx*dx + dy*dy) ** 0.5
                if dist < self.node_size:
                    # Clicked on a node!
                    self._handle_node_click(node_id)
                    return True

        return False

    def _handle_node_click(self, node_id: str):
        """Handle clicking on a node"""
        if not self.world_manager:
            return

        # Check if this is an available jump destination
        current = self.world_manager.world_map.get_current_node()
        if not current:
            return

        # Can we jump there?
        if node_id in current.connections:
            # Execute jump command
            command = f"jump {node_id}"
            self.log_command(f"$ {command}")

            if self.ship_os:
                exit_code, stdout, stderr = self.ship_os.execute_command(command)
                if stdout:
                    for line in stdout.strip().split('\n'):
                        self.log_command(line)
                if stderr:
                    self.log_command(f"ERROR: {stderr.strip()}")

            # Recenter camera on new position
            self._calculate_camera_position()
        else:
            # Can't jump there
            node = self.world_manager.world_map.nodes.get(node_id)
            if node:
                if node.id == current.id:
                    self.log_command("Already at this location")
                else:
                    self.log_command(f"Cannot jump to {node_id} - not reachable")

    def render(self):
        """Render the map"""
        if not self.surface or self.surface.get_size() != (self.width, self.height):
            self.surface = pygame.Surface((self.width, self.height))

        if not self.world_manager:
            # No map to display
            self.surface.fill((10, 10, 30))
            if Theme.FONT_TITLE:
                text = Theme.FONT_TITLE.render("No map data", True, (100, 100, 100))
                self.surface.blit(text, (self.width // 2 - 50, self.height // 2))
            return self.surface

        # Clear surface
        self.surface.fill((5, 5, 20))

        # Draw background stars
        for star_x, star_y, star_size in self.bg_stars:
            brightness = random.randint(100, 200)
            star_color = (brightness, brightness, brightness)
            if star_size == 1:
                self.surface.set_at((star_x, star_y), star_color)
            else:
                pygame.draw.circle(self.surface, star_color, (star_x, star_y), star_size // 2)

        world_map = self.world_manager.world_map
        current_node = world_map.get_current_node()

        # Clear node positions cache
        self.node_positions = {}

        # First pass: Draw connections
        for node in world_map.nodes.values():
            start_pos = self._world_to_screen(node.position[0], node.position[1])

            # Draw connections to next nodes
            for conn_id in node.connections:
                if conn_id in world_map.nodes:
                    conn_node = world_map.nodes[conn_id]
                    end_pos = self._world_to_screen(conn_node.position[0], conn_node.position[1])

                    # Connection color
                    if node.visited:
                        color = (80, 80, 80)  # Gray for explored paths
                    else:
                        color = (40, 40, 40)  # Darker for unexplored

                    pygame.draw.line(self.surface, color, start_pos, end_pos, 2)

        # Second pass: Draw nodes
        for node in world_map.nodes.values():
            screen_pos = self._world_to_screen(node.position[0], node.position[1])
            self.node_positions[node.id] = screen_pos

            # Skip if off screen
            if (screen_pos[0] < -50 or screen_pos[0] > self.width + 50 or
                screen_pos[1] < -50 or screen_pos[1] > self.height + 50):
                continue

            # Node color based on type
            base_color = NODE_COLORS.get(node.type, (100, 100, 100))

            # Modify color based on state
            if not node.visited:
                # Darken unvisited nodes
                base_color = tuple(int(c * 0.5) for c in base_color)

            # Determine node appearance
            is_current = (current_node and node.id == current_node.id)
            is_available = (current_node and node.id in current_node.connections)
            is_hovered = (node.id == self.hovered_node_id)

            # Draw node
            node_radius = self.node_size

            # Pulsing effect for current node
            if is_current:
                import time
                pulse = abs((time.time() * 3) % 2 - 1)
                glow_radius = int(node_radius + 8 + pulse * 6)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*base_color, 100), (glow_radius, glow_radius), glow_radius)
                self.surface.blit(glow_surf, (screen_pos[0] - glow_radius, screen_pos[1] - glow_radius))

            # Highlight available jumps
            if is_available:
                highlight_color = (255, 255, 100)
                pygame.draw.circle(self.surface, highlight_color, screen_pos, node_radius + 4, 3)

            # Main node circle
            pygame.draw.circle(self.surface, base_color, screen_pos, node_radius)

            # Border
            border_color = (255, 255, 255) if is_current else (200, 200, 200) if is_available else (100, 100, 100)
            border_width = 3 if is_current else 2
            pygame.draw.circle(self.surface, border_color, screen_pos, node_radius, border_width)

            # Icon or marker in center
            if is_current:
                # Draw ship icon
                pygame.draw.circle(self.surface, (255, 255, 255), screen_pos, 6)
                pygame.draw.circle(self.surface, (0, 0, 0), screen_pos, 6, 2)

            # Hover effect
            if is_hovered:
                pygame.draw.circle(self.surface, (255, 255, 255), screen_pos, node_radius + 2, 1)

        # Draw sector labels
        self._draw_sector_labels(world_map)

        # Draw info panel
        self._draw_info_panel(current_node)

        return self.surface

    def _draw_sector_labels(self, world_map):
        """Draw sector number labels"""
        if not Theme.FONT_TITLE:
            return

        # Draw sector dividers and labels
        for sector in range(world_map.num_sectors):
            # Get first node in sector to determine x position
            sector_nodes = world_map.get_sector_nodes(sector)
            if not sector_nodes:
                continue

            # Use first node's x position
            sector_x = sector_nodes[0].position[0]
            screen_pos = self._world_to_screen(sector_x, -50)

            # Draw sector label
            label_font = pygame.font.SysFont('sans-serif', 18, bold=True)
            label = label_font.render(f"SECTOR {sector + 1}", True, (255, 153, 0))
            self.surface.blit(label, (screen_pos[0] - 40, 10))

    def _draw_info_panel(self, current_node):
        """Draw info panel at bottom"""
        panel_height = 100
        panel_y = self.height - panel_height

        # Background
        panel_rect = pygame.Rect(0, panel_y, self.width, panel_height)
        pygame.draw.rect(self.surface, (10, 10, 30), panel_rect)
        pygame.draw.rect(self.surface, (255, 153, 0), panel_rect, 2)

        if not Theme.FONT_SMALL:
            return

        y_offset = panel_y + 8

        # Current location
        if current_node:
            info_font = pygame.font.SysFont('sans-serif', 16, bold=True)
            location_text = info_font.render(f"Location: {current_node.id}", True, (255, 255, 255))
            self.surface.blit(location_text, (10, y_offset))

            type_text = info_font.render(f"Type: {current_node.type.value.upper()}", True, NODE_COLORS.get(current_node.type, (255, 255, 255)))
            self.surface.blit(type_text, (200, y_offset))

            sector_text = info_font.render(f"Sector: {current_node.sector + 1}/{self.world_manager.world_map.num_sectors}", True, (255, 255, 255))
            self.surface.blit(sector_text, (450, y_offset))

        # Hovered node info
        if self.hovered_node_id and self.hovered_node_id in self.world_manager.world_map.nodes:
            hovered = self.world_manager.world_map.nodes[self.hovered_node_id]
            y_offset += 25
            hover_font = pygame.font.SysFont('sans-serif', 14)
            hover_text = hover_font.render(f"Hover: {hovered.id} - {hovered.type.value}", True, (200, 200, 200))
            self.surface.blit(hover_text, (10, y_offset))

        # Command log
        if self.command_log:
            y_offset += 25
            log_font = pygame.font.SysFont('sans-serif', 13)
            for i, cmd in enumerate(self.command_log[-2:]):  # Last 2 lines
                log_text = log_font.render(cmd, True, (100, 255, 150))
                self.surface.blit(log_text, (10, y_offset + i * 16))

    def update(self, dt: float):
        """Update widget state"""
        pass

    def set_size(self, width: int, height: int):
        """Update widget size"""
        self.width = width
        self.height = height

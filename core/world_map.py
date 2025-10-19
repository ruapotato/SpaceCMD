"""
World Map System

Spiral galaxy navigation with:
- 2D spiral pattern from outer edge to center
- Difficulty increases toward the center
- Different node types (combat, store, event, nebula)
- Path choices and strategic navigation
- Scaling rewards and enemies
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
import random
import math


class NodeType(Enum):
    """Types of map nodes"""
    EMPTY = "empty"              # Safe, nothing happens
    COMBAT = "combat"            # Enemy encounter
    ELITE_COMBAT = "elite"       # Harder enemy, better rewards
    STORE = "store"              # Merchant/shop
    EVENT = "event"              # Random event with choices
    DISTRESS = "distress"        # Distress beacon (risky)
    NEBULA = "nebula"            # Nebula (shields disabled)
    ASTEROID = "asteroid"        # Asteroid field (evasion down)
    REPAIR = "repair"            # Repair station (free repairs)
    BOSS = "boss"                # Sector boss


class MapNode:
    """A single location on the map"""

    def __init__(self, node_id: str, node_type: NodeType, sector: int, position: Tuple[int, int],
                 distance_from_center: float = 0.0):
        self.id = node_id
        self.type = node_type
        self.sector = sector  # Which sector/ring (0-based, 0=outer, higher=inner)
        self.position = position  # (x, y) for visualization
        self.visited = False
        self.connections: List[str] = []  # IDs of connected nodes
        self.distance_from_center = distance_from_center  # For difficulty calculation

        # Node-specific data (difficulty based on distance to center)
        # Closer to center = harder (inverse of distance)
        self.difficulty = sector  # Sector also tracks progression
        self.reward_scrap = 0
        self.enemy_type = None
        self.event_id = None

    def __repr__(self):
        return f"<Node {self.id} [{self.type.value}] S{self.sector} {'VISITED' if self.visited else 'UNVISITED'}>"


class WorldMap:
    """
    The complete world map with sectors and nodes.

    Like FTL, player navigates through sectors, choosing paths
    and encountering various events and enemies.
    """

    def __init__(self, num_sectors: int = 8, nodes_per_sector: int = 8):
        self.num_sectors = num_sectors
        self.nodes_per_sector = nodes_per_sector
        self.nodes: Dict[str, MapNode] = {}
        self.current_node_id: Optional[str] = None
        self.current_sector = 0

        # Spiral parameters
        self.spiral_center_x = 0  # Will be set during generation
        self.spiral_center_y = 0
        self.total_nodes = num_sectors * nodes_per_sector

        # Generate the map
        self._generate_spiral_map()

    def _generate_spiral_map(self):
        """
        Generate a spiral galaxy map.

        - Nodes arranged in a spiral from outer edge (easy) to center (hard)
        - Difficulty increases as you approach the center
        - Boss at the center
        """
        # Spiral parameters
        max_radius = 400  # Starting radius (outer edge)
        min_radius = 50   # Ending radius (center)
        total_angle = math.pi * 6  # 3 full rotations

        # Calculate center position for visualization
        self.spiral_center_x = 0
        self.spiral_center_y = 0

        all_nodes_ordered = []  # Keep track of node order for connections

        # Create nodes along spiral
        for i in range(self.total_nodes):
            # Progress from 0.0 (outer) to 1.0 (center)
            progress = i / max(1, self.total_nodes - 1)

            # Spiral parameters
            theta = progress * total_angle  # Angle increases as we spiral in
            radius = max_radius - (max_radius - min_radius) * progress  # Radius decreases

            # Add some randomness to avoid perfect spiral
            theta += random.uniform(-0.1, 0.1)
            radius += random.uniform(-20, 20)

            # Calculate position
            x = self.spiral_center_x + radius * math.cos(theta)
            y = self.spiral_center_y + radius * math.sin(theta)
            position = (int(x), int(y))

            # Determine sector (divide into rings/sectors)
            sector = int(progress * self.num_sectors)
            sector = min(sector, self.num_sectors - 1)

            # Node ID
            node_id = f"N{i:03d}"

            # Distance from center (for difficulty)
            distance_from_center = radius

            # Determine node type
            node_type = self._determine_node_type(sector, i)

            # Boss at the end (center)
            if i == self.total_nodes - 1:
                node_type = NodeType.BOSS

            # Create node
            node = MapNode(node_id, node_type, sector, position, distance_from_center)

            # Set difficulty (inverse of distance - closer to center = harder)
            # Normalize to 0-7 range
            node.difficulty = int((1.0 - progress) * 0.5 + progress * 7.5)

            # Set rewards based on difficulty
            if node_type == NodeType.COMBAT:
                node.reward_scrap = 10 + node.difficulty * 5 + random.randint(0, 5)
                node.enemy_type = self._get_enemy_for_difficulty(node.difficulty)
            elif node_type == NodeType.ELITE_COMBAT:
                node.reward_scrap = 20 + node.difficulty * 10 + random.randint(5, 15)
                node.enemy_type = self._get_elite_enemy_for_difficulty(node.difficulty)
            elif node_type == NodeType.STORE:
                node.reward_scrap = 0  # Stores cost money
            elif node_type == NodeType.BOSS:
                node.reward_scrap = 100
                node.enemy_type = "rebel_flagship"

            self.nodes[node_id] = node
            all_nodes_ordered.append(node)

        # Connect nodes
        # Each node connects to 2-3 nearby nodes further along the spiral
        for i, node in enumerate(all_nodes_ordered[:-1]):  # Skip last node (boss)
            # Connect to next 1-3 nodes along spiral
            num_connections = random.randint(2, 3)

            for j in range(1, num_connections + 1):
                next_idx = min(i + j, len(all_nodes_ordered) - 1)
                if next_idx > i and next_idx < len(all_nodes_ordered):
                    next_node = all_nodes_ordered[next_idx]
                    # Add bidirectional connection (can backtrack if needed)
                    if next_node.id not in node.connections:
                        node.connections.append(next_node.id)

            # Also add some cross-connections to nearby nodes in space
            for other in all_nodes_ordered[max(0, i-3):i+5]:
                if other.id == node.id:
                    continue

                # Check distance
                dx = node.position[0] - other.position[0]
                dy = node.position[1] - other.position[1]
                dist = math.sqrt(dx*dx + dy*dy)

                # Connect if very close
                if dist < 80 and random.random() < 0.3:
                    if other.id not in node.connections and len(node.connections) < 4:
                        node.connections.append(other.id)

        # Set starting node (first node - outer edge)
        self.current_node_id = "N000"
        if self.current_node_id in self.nodes:
            self.nodes[self.current_node_id].visited = True

    def _determine_node_type(self, sector: int, position: int) -> NodeType:
        """Determine what type of node this should be"""
        # First node of each sector is always safe
        if position == 0 and sector > 0:
            return NodeType.EMPTY

        # Last sector should have boss
        if sector == self.num_sectors - 1 and position == self.nodes_per_sector - 1:
            return NodeType.BOSS

        # Random distribution of node types
        roll = random.random()

        # More combat in later sectors
        combat_chance = 0.4 + (sector * 0.05)

        if roll < combat_chance:
            # 10% of combat encounters are elite
            if random.random() < 0.1 + (sector * 0.02):
                return NodeType.ELITE_COMBAT
            return NodeType.COMBAT
        elif roll < combat_chance + 0.15:
            return NodeType.EVENT
        elif roll < combat_chance + 0.25:
            return NodeType.STORE
        elif roll < combat_chance + 0.30:
            return NodeType.DISTRESS
        elif roll < combat_chance + 0.35:
            return NodeType.REPAIR
        elif roll < combat_chance + 0.40:
            return NodeType.NEBULA
        elif roll < combat_chance + 0.45:
            return NodeType.ASTEROID
        else:
            return NodeType.EMPTY

    def _get_enemy_for_difficulty(self, difficulty: int) -> str:
        """Get enemy type appropriate for difficulty level (0-7)"""
        if difficulty <= 1:
            return "gnat"
        elif difficulty <= 3:
            return random.choice(["pirate_scout", "gnat"])
        elif difficulty <= 5:
            return random.choice(["pirate_scout", "mantis_fighter"])
        else:
            return random.choice(["mantis_fighter", "rebel_fighter"])

    def _get_elite_enemy_for_difficulty(self, difficulty: int) -> str:
        """Get elite enemy type for difficulty level"""
        if difficulty <= 2:
            return "mantis_fighter"
        elif difficulty <= 5:
            return "rebel_fighter"
        else:
            return "rebel_fighter"  # TODO: Add more enemy types

    def _get_enemy_for_sector(self, sector: int) -> str:
        """Get enemy type appropriate for sector difficulty (legacy compatibility)"""
        return self._get_enemy_for_difficulty(sector)

    def _get_elite_enemy_for_sector(self, sector: int) -> str:
        """Get elite enemy type for sector (legacy compatibility)"""
        return self._get_elite_enemy_for_difficulty(sector)

    def _connect_sector_nodes(self, sector_nodes: List[str], next_sector: int):
        """Connect nodes in current sector to nodes in next sector"""
        next_sector_nodes = [nid for nid in self.nodes.keys()
                            if self.nodes[nid].sector == next_sector]

        if not next_sector_nodes:
            return

        # Each node connects to 2-3 nodes in next sector
        for node_id in sector_nodes:
            node = self.nodes[node_id]

            # Pick 2-3 random nodes from next sector
            num_connections = random.randint(2, min(3, len(next_sector_nodes)))
            connections = random.sample(next_sector_nodes,
                                       min(num_connections, len(next_sector_nodes)))

            node.connections.extend(connections)

    def get_current_node(self) -> Optional[MapNode]:
        """Get the current node player is at"""
        if self.current_node_id:
            return self.nodes[self.current_node_id]
        return None

    def get_available_jumps(self) -> List[MapNode]:
        """Get list of nodes player can jump to from current position"""
        current = self.get_current_node()
        if not current:
            return []

        available = []
        for node_id in current.connections:
            if node_id in self.nodes:
                available.append(self.nodes[node_id])

        return available

    def jump_to_node(self, node_id: str) -> bool:
        """
        Jump to a new node.
        Returns True if successful, False if not accessible.
        """
        current = self.get_current_node()
        if not current:
            return False

        # Check if node is accessible from current position
        if node_id not in current.connections:
            return False

        # Make the jump
        self.current_node_id = node_id
        target_node = self.nodes[node_id]
        target_node.visited = True
        self.current_sector = target_node.sector

        return True

    def get_sector_nodes(self, sector: int) -> List[MapNode]:
        """Get all nodes in a specific sector"""
        return [node for node in self.nodes.values() if node.sector == sector]

    def get_map_bounds(self) -> Tuple[int, int, int, int]:
        """Get bounding box of map (min_x, min_y, max_x, max_y)"""
        if not self.nodes:
            return (0, 0, 0, 0)

        positions = [node.position for node in self.nodes.values()]
        min_x = min(p[0] for p in positions)
        max_x = max(p[0] for p in positions)
        min_y = min(p[1] for p in positions)
        max_y = max(p[1] for p in positions)

        return (min_x, min_y, max_x, max_y)

    def get_progress(self) -> float:
        """Get player progress through the map (0.0 to 1.0)"""
        if self.num_sectors == 0:
            return 0.0
        return self.current_sector / self.num_sectors

    def __repr__(self):
        current = self.get_current_node()
        return f"<WorldMap sectors={self.num_sectors} current={current.id if current else 'None'}>"

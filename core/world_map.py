"""
World Map System

FTL-style sector-based navigation with:
- Multiple sectors with increasing difficulty
- Different node types (combat, store, event, nebula)
- Path choices and strategic navigation
- Scaling rewards and enemies
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
import random


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

    def __init__(self, node_id: str, node_type: NodeType, sector: int, position: Tuple[int, int]):
        self.id = node_id
        self.type = node_type
        self.sector = sector  # Which sector (0-based)
        self.position = position  # (x, y) for visualization
        self.visited = False
        self.connections: List[str] = []  # IDs of connected nodes

        # Node-specific data
        self.difficulty = sector  # Base difficulty = sector number
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

        # Generate the map
        self._generate_map()

    def _generate_map(self):
        """Generate a random map with sectors and nodes"""
        node_counter = 0
        all_sector_nodes = {}  # sector -> [node_ids]

        # First pass: Create all nodes
        for sector in range(self.num_sectors):
            # Each sector has multiple nodes arranged vertically
            sector_nodes = []

            for i in range(self.nodes_per_sector):
                node_id = f"S{sector}N{i}"

                # Determine node type based on sector and position
                node_type = self._determine_node_type(sector, i)

                # Position for visualization
                x = sector * 120 + random.randint(-10, 10)
                y = i * 80 + random.randint(-10, 10)
                position = (x, y)

                node = MapNode(node_id, node_type, sector, position)

                # Set difficulty and rewards
                node.difficulty = sector
                if node_type == NodeType.COMBAT:
                    node.reward_scrap = 10 + sector * 5 + random.randint(0, 5)
                    node.enemy_type = self._get_enemy_for_sector(sector)
                elif node_type == NodeType.ELITE_COMBAT:
                    node.reward_scrap = 20 + sector * 10 + random.randint(5, 15)
                    node.enemy_type = self._get_elite_enemy_for_sector(sector)
                elif node_type == NodeType.STORE:
                    node.reward_scrap = 0  # Stores cost money

                self.nodes[node_id] = node
                sector_nodes.append(node_id)
                node_counter += 1

            all_sector_nodes[sector] = sector_nodes

        # Second pass: Connect nodes between sectors
        for sector in range(self.num_sectors - 1):
            self._connect_sector_nodes(all_sector_nodes[sector], sector + 1)

        # Set starting node
        self.current_node_id = "S0N0"
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

    def _get_enemy_for_sector(self, sector: int) -> str:
        """Get enemy type appropriate for sector difficulty"""
        if sector == 0:
            return "gnat"
        elif sector <= 2:
            return random.choice(["pirate_scout", "gnat"])
        elif sector <= 5:
            return random.choice(["pirate_scout", "mantis_fighter"])
        else:
            return random.choice(["mantis_fighter", "rebel_fighter"])

    def _get_elite_enemy_for_sector(self, sector: int) -> str:
        """Get elite enemy type for sector"""
        if sector <= 2:
            return "mantis_fighter"
        elif sector <= 5:
            return "rebel_fighter"
        else:
            return "rebel_fighter"  # TODO: Add more enemy types

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

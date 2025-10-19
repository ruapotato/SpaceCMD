#!/usr/bin/env python3
"""Debug map connections"""

from core.world_map import WorldMap

# Create a small map
map = WorldMap(num_sectors=2, nodes_per_sector=3)

print(f"Total nodes: {len(map.nodes)}")
print(f"Current node: {map.current_node_id}")

# Check first node
first_node = map.nodes[map.current_node_id]
print(f"\nFirst node: {first_node.id}")
print(f"Sector: {first_node.sector}")
print(f"Connections: {first_node.connections}")

# Check all sector 0 nodes
print(f"\nAll Sector 0 nodes:")
for node_id, node in sorted(map.nodes.items()):
    if node.sector == 0:
        print(f"  {node_id}: {len(node.connections)} connections -> {node.connections}")

print(f"\nAll Sector 1 nodes:")
for node_id, node in sorted(map.nodes.items()):
    if node.sector == 1:
        print(f"  {node_id}: exists")

# Try to manually get available jumps
available = map.get_available_jumps()
print(f"\nAvailable jumps from {map.current_node_id}: {len(available)}")
for node in available:
    print(f"  - {node.id}")

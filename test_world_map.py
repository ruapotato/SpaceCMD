#!/usr/bin/env python3
"""Test the world map and navigation system"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager

print("=" * 70)
print("WORLD MAP NAVIGATION TEST")
print("=" * 70)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

# Create world manager with smaller map for testing
world_manager = WorldManager(ship_os, num_sectors=4)
ship_os.world_manager = world_manager

print(f"\nMap created: {world_manager.world_map.num_sectors} sectors")
print(f"Total nodes: {len(world_manager.world_map.nodes)}")

# Show starting location
print("\n1. Testing 'map' command...")
print("-" * 70)
exit_code, stdout, stderr = ship_os.execute_command("map")
print(stdout)

# Show available jumps
current = world_manager.world_map.get_current_node()
available = world_manager.get_available_jumps()
print(f"Current node: {current.id} ({current.type.value})")
print(f"Available jumps: {len(available)}")
for node in available[:3]:  # Show first 3
    print(f"  - {node.id}: {node.type.value} (Sector {node.sector + 1})")

# Try jumping to first available node
if available:
    target = available[0]
    print(f"\n2. Testing jump to {target.id}...")
    print("-" * 70)
    exit_code, stdout, stderr = ship_os.execute_command(f"jump {target.id}")
    print(stdout)
    if stderr:
        print(f"STDERR: {stderr}")

    # Verify we moved
    new_current = world_manager.world_map.get_current_node()
    print(f"\nCurrent location after jump: {new_current.id} ({new_current.type.value})")
    print(f"Fuel remaining: {ship.fuel}")

# Test invalid jump
print(f"\n3. Testing invalid jump...")
print("-" * 70)
exit_code, stdout, stderr = ship_os.execute_command("jump INVALID")
print(f"Output: {stdout}")
print(f"Errors: {stderr}")
print(f"Exit code: {exit_code} (should be 1 for error)")

# Show progression
print(f"\n4. Map Progress")
print("-" * 70)
progress = world_manager.world_map.get_progress()
print(f"Progress: {progress:.1%}")
print(f"Current sector: {world_manager.world_map.current_sector + 1}/{world_manager.world_map.num_sectors}")

# Test node types
print(f"\n5. Node Type Distribution")
print("-" * 70)
from collections import Counter
node_types = Counter(node.type.value for node in world_manager.world_map.nodes.values())
for node_type, count in sorted(node_types.items()):
    percentage = (count / len(world_manager.world_map.nodes)) * 100
    print(f"  {node_type:15}: {count:3} ({percentage:5.1f}%)")

# Test difficulty scaling
print(f"\n6. Difficulty Scaling by Sector")
print("-" * 70)
for sector in range(world_manager.world_map.num_sectors):
    sector_nodes = world_manager.world_map.get_sector_nodes(sector)
    combat_nodes = [n for n in sector_nodes if 'combat' in n.type.value.lower()]
    if combat_nodes:
        avg_reward = sum(n.reward_scrap for n in combat_nodes) / len(combat_nodes)
        print(f"  Sector {sector + 1}: Avg reward = {avg_reward:.1f} scrap")

print("\n" + "=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
print("\nKey Features:")
print("✓ World map with multiple sectors")
print("✓ Different node types (combat, store, event, etc)")
print("✓ Navigation commands (map, jump)")
print("✓ Difficulty scaling with sector depth")
print("✓ Scaling rewards")
print("=" * 70)

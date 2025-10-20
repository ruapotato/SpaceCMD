#!/usr/bin/env python3
"""
Test the new spiral galaxy map
"""

import sys
from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
import math

def test_spiral_map():
    """Test spiral galaxy map generation"""
    print("="*60)
    print("TEST: Spiral Galaxy Map")
    print("="*60)

    # Create ship
    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    # Create world manager with spiral map
    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    world_map = world_manager.world_map

    print(f"\n✓ Created spiral galaxy map")
    print(f"  Total nodes: {len(world_map.nodes)}")
    print(f"  Sectors: {world_map.num_sectors}")

    # Check spiral properties
    print("\n  Checking spiral structure...")

    # Get all nodes sorted by index
    nodes_sorted = sorted(world_map.nodes.values(), key=lambda n: n.id)

    # Check first few nodes (should be outer edge, easier)
    print("\n  Outer edge nodes (first 5):")
    for node in nodes_sorted[:5]:
        dist = node.distance_from_center
        print(f"    {node.id}: dist={dist:.1f}, difficulty={node.difficulty}, type={node.type.value}")

    # Check last few nodes (should be center, harder)
    print("\n  Center nodes (last 5):")
    for node in nodes_sorted[-5:]:
        dist = node.distance_from_center
        print(f"    {node.id}: dist={dist:.1f}, difficulty={node.difficulty}, type={node.type.value}")

    # Check if difficulty increases toward center
    outer_avg_difficulty = sum(n.difficulty for n in nodes_sorted[:10]) / 10
    center_avg_difficulty = sum(n.difficulty for n in nodes_sorted[-10:]) / 10

    print(f"\n  Average difficulty:")
    print(f"    Outer 10 nodes: {outer_avg_difficulty:.1f}")
    print(f"    Center 10 nodes: {center_avg_difficulty:.1f}")

    if center_avg_difficulty > outer_avg_difficulty:
        print("  ✓ Difficulty increases toward center!")
    else:
        print("  ✗ WARNING: Difficulty not properly scaled")

    # Check boss at center
    last_node = nodes_sorted[-1]
    print(f"\n  Final node (should be boss):")
    print(f"    {last_node.id}: {last_node.type.value}, difficulty={last_node.difficulty}")

    if last_node.type.value == "boss":
        print("  ✓ Boss at center!")
    else:
        print("  ✗ WARNING: No boss at center")

    # Check connections
    total_connections = sum(len(n.connections) for n in world_map.nodes.values())
    avg_connections = total_connections / len(world_map.nodes)
    print(f"\n  Connectivity:")
    print(f"    Total connections: {total_connections}")
    print(f"    Average per node: {avg_connections:.1f}")

    # Check starting node
    current = world_map.get_current_node()
    print(f"\n  Starting node:")
    print(f"    {current.id}: {current.type.value}")
    print(f"    Distance from center: {current.distance_from_center:.1f}")
    print(f"    Difficulty: {current.difficulty}")

    if current.distance_from_center > 300:  # Should be near outer edge
        print("  ✓ Starting at outer edge!")
    else:
        print("  ✗ WARNING: Not starting at outer edge")

    # Test jumping
    print("\n  Testing jump system...")
    available = world_manager.get_available_jumps()
    print(f"    Available jumps: {len(available)}")

    if available:
        first_jump = available[0]
        print(f"    Jumping to: {first_jump.id} ({first_jump.type.value})")
        success = world_manager.jump_to_node(first_jump.id)

        if success:
            print("  ✓ Jump successful!")
            new_current = world_map.get_current_node()
            print(f"    Now at: {new_current.id}")
            print(f"    Distance from center: {new_current.distance_from_center:.1f}")
        else:
            print("  ✗ Jump failed")
            return False
    else:
        print("  ✗ No available jumps")
        return False

    print("\n✓ Spiral galaxy map test PASSED!")
    return True

def visualize_map_ascii():
    """Create simple ASCII visualization of spiral"""
    print("\n" + "="*60)
    print("ASCII Visualization of Spiral")
    print("="*60)

    # Create ship
    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    # Create world manager
    world_manager = WorldManager(ship_os, num_sectors=8)
    world_map = world_manager.world_map

    # Create 60x30 grid
    grid_width = 80
    grid_height = 40
    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

    # Find min/max positions
    all_x = [n.position[0] for n in world_map.nodes.values()]
    all_y = [n.position[1] for n in world_map.nodes.values()]

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    # Map nodes to grid
    for node in world_map.nodes.values():
        # Scale to grid
        x_norm = (node.position[0] - min_x) / (max_x - min_x)
        y_norm = (node.position[1] - min_y) / (max_y - min_y)

        grid_x = int(x_norm * (grid_width - 1))
        grid_y = int(y_norm * (grid_height - 1))

        # Mark node
        if node.type.value == "boss":
            grid[grid_y][grid_x] = 'B'  # Boss
        elif node.type.value == "combat":
            grid[grid_y][grid_x] = 'X'  # Combat
        elif node.type.value == "store":
            grid[grid_y][grid_x] = '$'  # Store
        elif node.id == world_map.current_node_id:
            grid[grid_y][grid_x] = '@'  # Current
        else:
            grid[grid_y][grid_x] = '.'  # Other

    # Print grid
    print("\nLegend: @ = Start, X = Combat, $ = Store, B = Boss, . = Other\n")
    for row in grid:
        print(''.join(row))

def main():
    """Run all tests"""
    print("\n🌌 Spiral Galaxy Map Test Suite")
    print()

    results = []

    # Test map generation
    try:
        results.append(("Spiral Map Generation", test_spiral_map()))
    except Exception as e:
        print(f"\n✗ Spiral map test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Spiral Map Generation", False))

    # Visualize
    try:
        visualize_map_ascii()
    except Exception as e:
        print(f"\n✗ Visualization failed: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

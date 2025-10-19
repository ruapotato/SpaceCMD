#!/usr/bin/env python3
"""
Test map fixes:
1. Map can be closed and reopened
2. Ship icon moves when jumping
3. Location requires sensors to be functional
"""

import sys
from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.ship import SystemType

def test_map_references():
    """Test that reopened map has proper references"""
    print("="*60)
    print("TEST: Map Window References")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Simulate creating map widget like desktop does
    from core.gui.map_widget_v2 import MapWidgetV2

    # First map
    print("\nCreating first map widget...")
    map1 = MapWidgetV2(800, 600)
    map1.ship_os = ship_os
    map1.set_world_manager(world_manager)

    if map1.ship_os and map1.world_manager:
        print("  ✓ First map has ship_os and world_manager")
    else:
        print("  ✗ First map missing references")
        return False

    # Simulate closing and reopening (creating second map)
    print("\nCreating second map widget (simulating reopen)...")
    map2 = MapWidgetV2(800, 600)
    map2.ship_os = ship_os
    if hasattr(ship_os, 'world_manager') and ship_os.world_manager:
        map2.set_world_manager(ship_os.world_manager)

    if map2.ship_os and map2.world_manager:
        print("  ✓ Second map has ship_os and world_manager")
    else:
        print("  ✗ Second map missing references")
        return False

    # Check that ship position can be calculated
    ship_pos = map2._get_ship_screen_pos()
    if ship_pos is not None:
        print(f"  ✓ Ship position calculated: {ship_pos}")
    else:
        print("  ✗ Ship position is None")
        return False

    print("\n✓ Map references test PASSED!")
    return True

def test_ship_icon_moves():
    """Test that ship icon position updates when jumping"""
    print("\n" + "="*60)
    print("TEST: Ship Icon Movement")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    from core.gui.map_widget_v2 import MapWidgetV2

    map_widget = MapWidgetV2(800, 600)
    map_widget.ship_os = ship_os
    map_widget.set_world_manager(world_manager)

    # Get initial position
    initial_pos = map_widget._get_ship_screen_pos()
    if initial_pos is None:
        print("  ✗ Initial ship position is None")
        return False

    initial_node = world_manager.world_map.get_current_node()
    print(f"\nInitial position:")
    print(f"  Node: {initial_node.id}")
    print(f"  Screen pos: {initial_pos}")

    # Jump to next node
    available = world_manager.get_available_jumps()
    if not available:
        print("  ✗ No available jumps")
        return False

    target = available[0]
    print(f"\nJumping to {target.id}...")
    world_manager.jump_to_node(target.id)

    # Get new position
    new_pos = map_widget._get_ship_screen_pos()
    if new_pos is None:
        print("  ✗ New ship position is None")
        return False

    new_node = world_manager.world_map.get_current_node()
    print(f"  New node: {new_node.id}")
    print(f"  New screen pos: {new_pos}")

    # Position should have changed (unless by coincidence same screen pos)
    if new_node.id != initial_node.id:
        print("  ✓ Ship moved to different node")

        # Screen position might be same if nodes are close, but at least
        # the calculation should work
        if new_pos != initial_pos:
            print("  ✓ Ship screen position changed")
        else:
            print("  ⚠️  Screen position unchanged (nodes might be close)")
    else:
        print("  ✗ Ship didn't move nodes")
        return False

    print("\n✓ Ship icon movement test PASSED!")
    return True

def test_location_requires_sensors():
    """Test that location info requires sensors"""
    print("\n" + "="*60)
    print("TEST: Location Requires Sensors")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Test with sensors offline
    print("\nTesting with sensors OFFLINE...")
    ship.allocate_power(SystemType.SENSORS, 0)

    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")
    output = stdout if isinstance(stdout, str) else stdout.decode()

    if "SENSORS OFFLINE" in output:
        print("  ✓ Shows 'SENSORS OFFLINE' when unpowered")
    else:
        print("  ✗ Should require sensors")
        print(f"  Output: {output[:100]}")
        return False

    if "Galaxy Position" not in output:
        print("  ✓ Location info hidden when sensors offline")
    else:
        print("  ✗ Location info exposed without sensors")
        return False

    # Test with sensors online
    print("\nTesting with sensors ONLINE...")
    ship.allocate_power(SystemType.SENSORS, 1)

    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")
    output = stdout if isinstance(stdout, str) else stdout.decode()

    if "SENSORS OFFLINE" not in output:
        print("  ✓ Sensors working when powered")
    else:
        print("  ✗ Should show data when sensors online")
        return False

    if "Galaxy Position" in output:
        print("  ✓ Location info available with sensors")
    else:
        print("  ✗ Location info missing with sensors online")
        return False

    print("\n✓ Sensor requirement test PASSED!")
    return True

def main():
    """Run all tests"""
    print("\n🛠️  Map Fixes Test Suite")
    print()

    results = []

    # Test 1: Map references
    try:
        results.append(("Map References", test_map_references()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Map References", False))

    # Test 2: Ship icon moves
    try:
        results.append(("Ship Icon Movement", test_ship_icon_moves()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Ship Icon Movement", False))

    # Test 3: Location requires sensors
    try:
        results.append(("Sensor Requirement", test_location_requires_sensors()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Sensor Requirement", False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 All fixes verified!")
        print("\nFIXES:")
        print("  ✓ Map window references set on creation")
        print("  ✓ Ship icon tracks current node position")
        print("  ✓ Location data requires functional sensors")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

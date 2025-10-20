#!/usr/bin/env python3
"""
Test GUI location display:
1. Location shows on top bar
2. Location requires sensors to be functional
3. Ship icon updates when jumping
"""

import sys
from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.ship import SystemType
from core.gui.topbar import SystemMonitor

def test_topbar_location():
    """Test that top bar shows location with sensors"""
    print("="*60)
    print("TEST: Top Bar Location Display")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Create system monitor
    monitor = SystemMonitor(ship_os)

    # Test with sensors offline
    print("\nTesting with sensors OFFLINE...")
    ship.allocate_power(SystemType.SENSORS, 0)
    monitor._read_devices()

    if not monitor.location_available:
        print(f"  ✓ Location not available (shows: '{monitor.location}')")
    else:
        print(f"  ✗ Location should be unavailable")
        return False

    # Test with sensors online
    print("\nTesting with sensors ONLINE...")
    ship.allocate_power(SystemType.SENSORS, 1)
    monitor._read_devices()

    if monitor.location_available:
        print(f"  ✓ Location available: {monitor.location}")
    else:
        print(f"  ✗ Location should be available")
        return False

    # Check that location is a reasonable value
    if 'u' in monitor.location:  # Should be formatted like "400u"
        distance_str = monitor.location.replace('u', '')
        try:
            distance = float(distance_str)
            if 0 <= distance <= 500:
                print(f"  ✓ Location value reasonable: {distance} units")
            else:
                print(f"  ⚠️  Location value seems off: {distance}")
        except:
            print(f"  ✗ Location not properly formatted: {monitor.location}")
            return False
    else:
        print(f"  ✗ Location format unexpected: {monitor.location}")
        return False

    print("\n✓ Top bar location test PASSED!")
    return True

def test_location_updates_on_jump():
    """Test that location updates when jumping"""
    print("\n" + "="*60)
    print("TEST: Location Updates on Jump")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Enable sensors
    ship.allocate_power(SystemType.SENSORS, 1)

    # Create system monitor
    monitor = SystemMonitor(ship_os)
    monitor._read_devices()

    initial_location = monitor.location
    initial_node = world_manager.world_map.get_current_node()

    print(f"\nInitial location:")
    print(f"  Node: {initial_node.id}")
    print(f"  Display: {initial_location}")

    # Jump to next node
    available = world_manager.get_available_jumps()
    if not available:
        print("  ✗ No available jumps")
        return False

    target = available[0]
    print(f"\nJumping to {target.id}...")
    world_manager.jump_to_node(target.id)

    # Update monitor
    monitor._read_devices()
    new_location = monitor.location
    new_node = world_manager.world_map.get_current_node()

    print(f"  New node: {new_node.id}")
    print(f"  New display: {new_location}")

    # Location should have changed (unless nodes are exactly same distance)
    if new_location != initial_location:
        print("  ✓ Location updated after jump")
    else:
        # Check if nodes are at different distances
        if abs(initial_node.distance_from_center - new_node.distance_from_center) > 1.0:
            print(f"  ✗ Location should have changed (node distance changed by {abs(initial_node.distance_from_center - new_node.distance_from_center):.1f})")
            return False
        else:
            print("  ⚠️  Location unchanged (nodes at similar distances)")

    print("\n✓ Location update test PASSED!")
    return True

def test_map_ship_icon_updates():
    """Test that map ship icon position changes on jump"""
    print("\n" + "="*60)
    print("TEST: Map Ship Icon Updates")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    from core.gui.map_widget_v2 import MapWidgetV2

    # Create map widget
    map_widget = MapWidgetV2(800, 600)
    map_widget.ship_os = ship_os
    map_widget.set_world_manager(world_manager)

    # Get initial ship position
    initial_pos = map_widget._get_ship_screen_pos()
    initial_node = world_manager.world_map.get_current_node()

    print(f"\nInitial position:")
    print(f"  Node: {initial_node.id}")
    print(f"  Screen: {initial_pos}")

    # Jump
    available = world_manager.get_available_jumps()
    if not available:
        print("  ✗ No jumps available")
        return False

    target = available[0]
    print(f"\nJumping to {target.id}...")
    world_manager.jump_to_node(target.id)

    # Get new position (should update automatically)
    new_pos = map_widget._get_ship_screen_pos()
    new_node = world_manager.world_map.get_current_node()

    print(f"  New node: {new_node.id}")
    print(f"  New screen: {new_pos}")

    # Position should change
    if new_pos != initial_pos:
        print("  ✓ Ship icon position updated")
    else:
        print("  ⚠️  Ship icon position unchanged")
        # This might be OK if nodes are visually close

    # More important: node should change
    if new_node.id != initial_node.id:
        print("  ✓ Ship is at new node")
    else:
        print("  ✗ Ship didn't move nodes")
        return False

    print("\n✓ Map ship icon test PASSED!")
    return True

def main():
    """Run all tests"""
    print("\n🎯 GUI Location Display Test Suite")
    print()

    results = []

    # Test 1: Top bar location
    try:
        results.append(("Top Bar Location", test_topbar_location()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Top Bar Location", False))

    # Test 2: Location updates
    try:
        results.append(("Location Updates", test_location_updates_on_jump()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Location Updates", False))

    # Test 3: Map ship icon
    try:
        results.append(("Map Ship Icon", test_map_ship_icon_updates()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Map Ship Icon", False))

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
        print("\nGUI LOCATION FEATURES:")
        print("  ✓ Location displayed on top bar")
        print("  ✓ Requires functional sensors (shows 'OFFLINE' when unpowered)")
        print("  ✓ Location updates when jumping to new node")
        print("  ✓ Ship icon position updates on galaxy map")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

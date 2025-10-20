#!/usr/bin/env python3
"""
Test ship position indicator on galaxy map
"""

import sys
from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager

def test_ship_position_tracking():
    """Test that ship position is tracked correctly"""
    print("="*60)
    print("TEST: Ship Position Tracking")
    print("="*60)

    # Create ship and OS
    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    # Create world manager
    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Check initial position
    print(f"\nInitial ship position:")
    print(f"  Distance from center: {ship.galaxy_distance_from_center:.1f}")

    current_node = world_manager.world_map.get_current_node()
    print(f"  Current node: {current_node.id}")
    print(f"  Node distance from center: {current_node.distance_from_center:.1f}")

    # These should match since we just spawned
    if abs(ship.galaxy_distance_from_center - current_node.distance_from_center) < 1.0:
        print("  ✓ Ship position matches current node!")
    else:
        print("  ✗ WARNING: Ship position doesn't match node")
        return False

    # Test jump updates position
    print("\n  Testing jump updates ship position...")
    available = world_manager.get_available_jumps()

    if not available:
        print("  ✗ No available jumps")
        return False

    target = available[0]
    print(f"  Jumping to: {target.id} (distance {target.distance_from_center:.1f})")

    old_distance = ship.galaxy_distance_from_center
    success = world_manager.jump_to_node(target.id)

    if not success:
        print("  ✗ Jump failed")
        return False

    new_distance = ship.galaxy_distance_from_center
    print(f"  Ship distance updated: {old_distance:.1f} → {new_distance:.1f}")

    if abs(new_distance - target.distance_from_center) < 1.0:
        print("  ✓ Ship position updated correctly!")
    else:
        print(f"  ✗ Ship position ({new_distance:.1f}) doesn't match target ({target.distance_from_center:.1f})")
        return False

    print("\n✓ Ship position tracking test PASSED!")
    return True

def test_sensor_device():
    """Test /proc/ship/sensors device"""
    print("\n" + "="*60)
    print("TEST: /proc/ship/sensors Device")
    print("="*60)

    # Create ship and OS
    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    # Create world manager
    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Allocate power to sensors so they're online
    from core.ship import SystemType
    ship.allocate_power(SystemType.SENSORS, 1)

    # Test reading sensors with sensors online
    print("\n  Testing with sensors ONLINE...")
    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")

    if exit_code != 0:
        print(f"  ✗ Command failed: {stderr}")
        return False

    # stdout is already a string
    output = stdout if isinstance(stdout, str) else stdout.decode()

    print("\n  Output:")
    for line in output.split('\n')[:5]:
        print(f"    {line}")

    if "SENSORS OFFLINE" in output:
        print("  ✗ Sensors should be online!")
        return False

    if "Galaxy Position" not in output:
        print("  ✗ Missing galaxy position info")
        return False

    print("\n  ✓ Sensor data available!")

    # Test with sensors offline (remove power)
    from core.ship import SystemType
    print("\n  Testing with sensors OFFLINE...")
    ship.allocate_power(SystemType.SENSORS, 0)

    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")

    output = stdout if isinstance(stdout, str) else stdout.decode()
    if "SENSORS OFFLINE" not in output:
        print("  ✗ Should show 'SENSORS OFFLINE'")
        return False

    print("  ✓ Shows 'SENSORS OFFLINE' when unpowered!")

    print("\n✓ Sensor device test PASSED!")
    return True

def main():
    """Run all tests"""
    print("\n🚀 Ship Position Indicator Test Suite")
    print()

    results = []

    # Test 1: Position tracking
    try:
        results.append(("Ship Position Tracking", test_ship_position_tracking()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Ship Position Tracking", False))

    # Test 2: Sensor device
    try:
        results.append(("Sensor Device", test_sensor_device()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Sensor Device", False))

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
        print("\nNEW FEATURES:")
        print("  • Ship position tracked by distance from galactic center")
        print("  • Position updates automatically on jump")
        print("  • /proc/ship/sensors shows location (requires sensors)")
        print("  • Visual ship indicator on galaxy map (YOUR SHIP)")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

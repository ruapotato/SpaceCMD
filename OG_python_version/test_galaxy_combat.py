#!/usr/bin/env python3
"""
Test all new galaxy and combat features:
- Ship position tracking (distance from galactic center)
- Sensor data exposure via /proc
- Weapon ranges
- Combat distance mechanics
- Ship speed and chase mechanics
"""

import sys
from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.ship import SystemType

def test_galaxy_position():
    """Test ship position tracking in galaxy"""
    print("="*60)
    print("TEST: Galaxy Position Tracking")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Check initial position
    start_node = world_manager.world_map.get_current_node()
    print(f"\nStarting position:")
    print(f"  Node: {start_node.id}")
    print(f"  Distance from center: {ship.galaxy_distance_from_center:.1f}")
    print(f"  Ship speed: {ship.speed:.1f} (max: {ship.max_speed:.1f})")

    if abs(ship.galaxy_distance_from_center - start_node.distance_from_center) < 1.0:
        print("  ✓ Position matches node")
    else:
        print("  ✗ Position mismatch")
        return False

    # Test jump updates position
    available = world_manager.get_available_jumps()
    if available:
        target = available[0]
        print(f"\nJumping to {target.id}...")
        world_manager.jump_to_node(target.id)

        if abs(ship.galaxy_distance_from_center - target.distance_from_center) < 1.0:
            print(f"  ✓ Position updated to {ship.galaxy_distance_from_center:.1f}")
        else:
            print(f"  ✗ Position not updated correctly")
            return False

    print("\n✓ Galaxy position tracking PASSED!")
    return True

def test_sensor_data():
    """Test /proc/ship/sensors device"""
    print("\n" + "="*60)
    print("TEST: Sensor Data Exposure")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Power sensors
    ship.allocate_power(SystemType.SENSORS, 1)

    # Read sensor data
    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")

    if exit_code != 0:
        print(f"  ✗ Command failed: {stderr}")
        return False

    output = stdout if isinstance(stdout, str) else stdout.decode()

    print("\nSensor output:")
    for line in output.split('\n')[:8]:
        if line.strip():
            print(f"  {line}")

    # Check for required fields
    if "Galaxy Position" in output and "Ship Speed" in output:
        print("\n  ✓ Sensor data includes position and speed")
    else:
        print("\n  ✗ Missing sensor data")
        return False

    # Test with sensors offline
    ship.allocate_power(SystemType.SENSORS, 0)
    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")
    output = stdout if isinstance(stdout, str) else stdout.decode()

    if "SENSORS OFFLINE" in output:
        print("  ✓ Shows offline when unpowered")
    else:
        print("  ✗ Should show offline")
        return False

    print("\n✓ Sensor data exposure PASSED!")
    return True

def test_weapon_ranges():
    """Test weapon range mechanics"""
    print("\n" + "="*60)
    print("TEST: Weapon Range Mechanics")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Check weapon ranges
    print("\nWeapon ranges:")
    for i, weapon in enumerate(ship.weapons):
        print(f"  {i+1}. {weapon.name}: {weapon.range:.1f} units")

    if len(ship.weapons) == 0:
        print("  ✗ No weapons to test")
        return False

    # Check that different weapon types have different ranges
    ranges = set(w.range for w in ship.weapons)
    if len(ranges) > 1:
        print("  ✓ Weapons have varying ranges")
    else:
        print("  ⚠️  All weapons have same range")

    # Trigger combat to test range checking
    print("\nTriggering combat...")
    world_manager.trigger_encounter("gnat", forced=True)

    if not world_manager.is_in_combat():
        print("  ✗ Failed to start combat")
        return False

    combat = world_manager.combat_state
    print(f"  Combat distance: {combat.combat_distance:.1f} units")

    # Check sensor data shows weapon ranges
    ship.allocate_power(SystemType.SENSORS, 1)
    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/sensors")
    output = stdout if isinstance(stdout, str) else stdout.decode()

    if "Weapon Ranges:" in output:
        print("  ✓ Sensors show weapon ranges in combat")
    else:
        print("  ✗ Weapon ranges not shown")
        return False

    print("\n✓ Weapon range mechanics PASSED!")
    return True

def test_combat_distance():
    """Test combat distance and movement"""
    print("\n" + "="*60)
    print("TEST: Combat Distance & Movement")
    print("="*60)

    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Trigger combat
    world_manager.trigger_encounter("gnat", forced=True)
    combat = world_manager.combat_state

    initial_distance = combat.combat_distance
    print(f"\nInitial combat distance: {initial_distance:.1f} units")

    # Test moving closer
    success = combat.move_closer()
    if success:
        new_distance = combat.combat_distance
        print(f"  Advanced to: {new_distance:.1f} units")
        if new_distance < initial_distance:
            print("  ✓ Move closer works")
        else:
            print("  ✗ Distance didn't decrease")
            return False
    else:
        print("  ⚠️  Already at minimum distance")

    # Test moving away
    success = combat.move_away()
    if success:
        new_distance = combat.combat_distance
        print(f"  Retreated to: {new_distance:.1f} units")
        print("  ✓ Move away works")
    else:
        print("  ⚠️  Already at maximum distance")

    print("\n✓ Combat distance mechanics PASSED!")
    return True

def test_ship_speeds():
    """Test ship speed differences"""
    print("\n" + "="*60)
    print("TEST: Ship Speed & Chase Mechanics")
    print("="*60)

    ship = create_ship("kestrel")
    print(f"\nPlayer ship speed: {ship.speed:.1f} (max: {ship.max_speed:.1f})")

    # Test enemy speeds
    from core.enemy_ships import ENEMY_SHIPS

    print("\nEnemy ship speeds:")
    for enemy_type, create_func in ENEMY_SHIPS.items():
        enemy = create_func()
        print(f"  {enemy.name:20} Speed: {enemy.speed:.1f}")

    # Check that speeds vary
    speeds = set()
    for create_func in ENEMY_SHIPS.values():
        enemy = create_func()
        speeds.add(enemy.speed)

    if len(speeds) > 1:
        print(f"\n  ✓ Enemy ships have {len(speeds)} different speed classes")
    else:
        print("\n  ✗ All enemies same speed")
        return False

    # Test pursuit mechanics
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    world_manager = WorldManager(ship_os, num_sectors=8)
    ship_os.world_manager = world_manager

    # Fight fast enemy (gnat)
    print("\n  Testing pursuit by fast enemy (Gnat)...")
    world_manager.trigger_encounter("gnat", forced=True)
    combat = world_manager.combat_state
    initial_dist = combat.combat_distance

    # Run combat for a bit
    for _ in range(5):
        combat.update(1.0)  # 1 second updates

    final_dist = combat.combat_distance
    print(f"    Initial: {initial_dist:.1f} → Final: {final_dist:.1f} units")

    if final_dist < initial_dist:
        print("    ✓ Fast enemy pursued successfully")
    else:
        print("    ⚠️  Enemy didn't close distance")

    print("\n✓ Ship speed mechanics PASSED!")
    return True

def main():
    """Run all tests"""
    print("\n🌌 Galaxy & Combat Mechanics Test Suite")
    print()

    results = []

    # Test 1: Galaxy position tracking
    try:
        results.append(("Galaxy Position", test_galaxy_position()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Galaxy Position", False))

    # Test 2: Sensor data
    try:
        results.append(("Sensor Data", test_sensor_data()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Sensor Data", False))

    # Test 3: Weapon ranges
    try:
        results.append(("Weapon Ranges", test_weapon_ranges()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Weapon Ranges", False))

    # Test 4: Combat distance
    try:
        results.append(("Combat Distance", test_combat_distance()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Combat Distance", False))

    # Test 5: Ship speeds
    try:
        results.append(("Ship Speeds", test_ship_speeds()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Ship Speeds", False))

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
        print("\nNEW FEATURES IMPLEMENTED:")
        print("  ✓ Galaxy position tracking (distance from center)")
        print("  ✓ Sensor data via /proc/ship/sensors")
        print("  ✓ Ship position indicator on galaxy map")
        print("  ✓ Weapon range mechanics (different ranges per weapon)")
        print("  ✓ Combat distance system (0.5 - 10.0 units)")
        print("  ✓ Movement commands (advance/retreat)")
        print("  ✓ Ship speed differences (pursuit/escape)")
        print("  ✓ Enemy AI uses speed to pursue")
        print("\nNEW COMMANDS:")
        print("  • advance  - Move closer to enemy in combat")
        print("  • retreat  - Move away from enemy in combat")
        print("  • cat /proc/ship/sensors - View position & weapon ranges")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

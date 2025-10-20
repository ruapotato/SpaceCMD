#!/usr/bin/env python3
"""
Test bot mechanics:
- Systems work without crew (but at 25% effectiveness)
- Systems work better with crew (100%+ effectiveness)
"""

import sys
from core.ships import create_ship
from core.ship import Room, ShipSystem, SystemType

def test_system_without_crew():
    """Test that systems work without crew"""
    print("="*60)
    print("TEST: Systems Work Without Crew (Automated)")
    print("="*60)

    # Create a ship
    ship = create_ship("kestrel")

    # Get engines system (has crew assigned)
    if SystemType.ENGINES not in ship.systems:
        print("✗ No engines system found")
        return False

    engines_system = ship.systems[SystemType.ENGINES]
    engines_room = engines_system.room

    print(f"\nEngines room initial state:")
    print(f"  Health: {engines_room.health:.1%}")
    print(f"  Power: {engines_room.power_allocated}/{engines_room.max_power}")
    print(f"  Crew: {len(engines_room.crew)}")

    # Allocate power to engines
    ship.allocate_power(SystemType.ENGINES, 2)

    print(f"\nAfter allocating power:")
    print(f"  Power: {engines_room.power_allocated}/{engines_room.max_power}")

    # Check if functional
    print(f"\n  Is functional: {engines_system.is_online()}")

    if not engines_system.is_online():
        print("✗ Engine system should be functional with power")
        return False

    # Check effectiveness WITH crew (first, to establish baseline)
    print("\n--- WITH CREW (baseline) ---")
    original_crew = engines_room.crew.copy()

    print(f"  Crew count: {len(engines_room.crew)}")
    print(f"  Is functional: {engines_system.is_online()}")

    effectiveness_with_crew = engines_system.get_effectiveness()
    print(f"  Effectiveness: {effectiveness_with_crew:.1%}")

    expected_with_crew = engines_room.health * (engines_room.power_allocated / engines_room.max_power)
    print(f"  Expected: ~{expected_with_crew:.1%} (base 100%)")

    # Check effectiveness WITHOUT crew
    print("\n--- WITHOUT CREW (automated) ---")
    # Remove all crew from engines room
    engines_room.crew = []

    print(f"  Crew count: {len(engines_room.crew)}")
    print(f"  Is functional: {engines_system.is_online()}")

    effectiveness_no_crew = engines_system.get_effectiveness()
    print(f"  Effectiveness: {effectiveness_no_crew:.1%}")

    # Should be around 25% (0.25 base * health * power ratio)
    expected_no_crew = 0.25 * engines_room.health * (engines_room.power_allocated / engines_room.max_power)
    print(f"  Expected: ~{expected_no_crew:.1%}")

    if not engines_system.is_online():
        print("✗ System should work without crew!")
        return False

    if effectiveness_no_crew < 0.1:
        print("✗ Effectiveness too low without crew")
        return False

    print("✓ System works without crew (automated mode)")

    # Verify crew improves effectiveness
    if effectiveness_with_crew <= effectiveness_no_crew:
        print("✗ Crew should improve effectiveness!")
        return False

    print("✓ Crew improves effectiveness")

    # Calculate improvement
    improvement = (effectiveness_with_crew / effectiveness_no_crew - 1) * 100
    print(f"\n  Improvement with crew: {improvement:.0f}%")

    if improvement < 200:  # Should be ~300% improvement (from 25% to 100%)
        print(f"⚠️  Warning: Improvement seems low ({improvement:.0f}%)")

    print("\n✓ Bot mechanics test PASSED!")
    return True

def test_shield_recharge_rates():
    """Test shield recharge with and without crew"""
    print("\n" + "="*60)
    print("TEST: Shield Recharge Rates")
    print("="*60)

    # Create ship
    ship = create_ship("kestrel")

    # Set max shields
    ship.shields_max = 4
    ship.shields = 0

    # Get shields system
    shields_system = ship.systems[SystemType.SHIELDS]
    shields_room = shields_system.room

    # Allocate power
    ship.allocate_power(SystemType.SHIELDS, 3)

    print(f"\nShields configuration:")
    print(f"  Max shields: {ship.shields_max}")
    print(f"  Current shields: {ship.shields}")
    print(f"  Power allocated: {shields_room.power_allocated}/{shields_room.max_power}")

    # Find a crew member and assign to shields
    print(f"\nInitial shields crew: {len(shields_room.crew)}")
    if len(ship.crew) > 0:
        # Assign one crew to shields
        ship.crew[0].assign_to_room(shields_room)
        print(f"Assigned {ship.crew[0].name} to shields")

    # Test WITH crew (first)
    print("\n--- Recharge WITH CREW ---")

    effectiveness_with_crew = shields_system.get_effectiveness()
    recharge_rate_with_crew = effectiveness_with_crew

    print(f"  Crew: {len(shields_room.crew)}")
    print(f"  Effectiveness: {effectiveness_with_crew:.2f}")
    print(f"  Recharge rate: {recharge_rate_with_crew:.2f} shields/sec")

    # Simulate 1 second of recharge
    ship.shields = 0
    ship.update(1.0)

    shields_recharged_with_crew = ship.shields
    print(f"  Shields after 1 sec: {shields_recharged_with_crew:.2f}")

    # Test WITHOUT crew
    print("\n--- Recharge WITHOUT CREW ---")
    shields_room.crew = []

    effectiveness_no_crew = shields_system.get_effectiveness()
    recharge_rate_no_crew = effectiveness_no_crew

    print(f"  Crew: {len(shields_room.crew)}")
    print(f"  Effectiveness: {effectiveness_no_crew:.2f}")
    print(f"  Recharge rate: {recharge_rate_no_crew:.2f} shields/sec")

    # Simulate 1 second of recharge
    ship.shields = 0
    ship.update(1.0)

    shields_recharged_no_crew = ship.shields
    print(f"  Shields after 1 sec: {shields_recharged_no_crew:.2f}")

    # Compare
    print(f"\n  Improvement with crew: {(shields_recharged_with_crew / shields_recharged_no_crew):.1f}x faster")

    if shields_recharged_with_crew > shields_recharged_no_crew:
        print("✓ Crew improves recharge rate")
        return True
    else:
        print("✗ Crew should improve recharge rate")
        return False

def main():
    """Run all tests"""
    print("\n🤖 Bot Mechanics Test Suite")
    print("Testing: Systems work without crew, but better with crew")
    print()

    results = []

    # Test 1: System functionality without crew
    try:
        results.append(("System Without Crew", test_system_without_crew()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("System Without Crew", False))

    # Test 2: Shield recharge rates
    try:
        results.append(("Shield Recharge Rates", test_shield_recharge_rates()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Shield Recharge Rates", False))

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
        print("\nNEW MECHANICS:")
        print("  • Systems work without crew at 25% effectiveness")
        print("  • Crew increases effectiveness to 100% + bonuses")
        print("  • More crew = better performance")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

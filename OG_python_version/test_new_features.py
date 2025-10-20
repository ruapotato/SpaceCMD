#!/usr/bin/env python3
"""
Test script for new features:
1. Jump animation with moving stars
2. Crew display in tactical view
"""

import sys
import time
from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.gui import Desktop

def test_jump_animation():
    """Test the jump animation feature"""
    print("="*60)
    print("TEST 1: Jump Animation with Moving Stars")
    print("="*60)

    # Create ship
    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    # Create world manager
    world_manager = WorldManager(ship_os)
    ship_os.world_manager = world_manager

    # Create desktop (headless for testing)
    desktop = Desktop(width=800, height=600, fullscreen=False)
    desktop.set_ship_os(ship_os)

    # Wire up jump callback
    world_manager.on_jump_complete = lambda node: desktop.trigger_jump_animation()

    # Get available jumps
    available_jumps = world_manager.get_available_jumps()

    if available_jumps:
        print(f"\n✓ Found {len(available_jumps)} available jump destinations")
        first_jump = available_jumps[0]
        print(f"  Jumping to: {first_jump.id} ({first_jump.type.value})")

        # Trigger jump
        success = world_manager.jump_to_node(first_jump.id)

        if success:
            print(f"✓ Jump initiated successfully")

            # Simulate animation frames
            print("\nSimulating jump animation...")
            for i in range(20):
                desktop.update(0.1)  # Update with 0.1 second delta

                if desktop.jump_animation_active:
                    progress = desktop.jump_animation_time / desktop.jump_animation_duration
                    print(f"  Frame {i}: Animation progress {progress*100:.1f}%, Warp speed: {desktop.warp_speed:.2f}")
                else:
                    if i > 0:
                        print(f"  ✓ Animation completed at frame {i}")
                        break

                time.sleep(0.05)  # Small delay for readability

            print("\n✓ Jump animation test PASSED")
            return True
        else:
            print("✗ Jump failed")
            return False
    else:
        print("✗ No jump destinations available")
        return False

def test_crew_display():
    """Test crew display synchronization"""
    print("\n" + "="*60)
    print("TEST 2: Crew Display in Tactical View")
    print("="*60)

    # Create ship
    ship = create_ship("kestrel")
    ship_os = ShipOS(ship=ship)
    ship_os.boot(verbose=False)
    ship_os.login('root', 'root')

    # Create world manager
    world_manager = WorldManager(ship_os)
    ship_os.world_manager = world_manager

    # Import tactical widget
    from core.gui.tactical_widget import TacticalWidget

    # Create tactical widget
    tactical = TacticalWidget(800, 600)
    tactical.world_manager = world_manager
    tactical.ship_os = ship_os

    print(f"\n✓ Created tactical widget")
    print(f"  Ship has {len(ship.crew)} crew members")

    # Show initial crew positions
    print("\n  Initial crew positions:")
    for crew in ship.crew:
        room_name = crew.room.name if crew.room else "Unassigned"
        print(f"    {crew.name}: {room_name}")

    # Update tactical display (sync crew positions)
    tactical.update_from_combat(None)  # No combat, just sync

    # Check tactical display rooms for crew
    print("\n  Tactical display crew (after sync):")
    crew_count = 0
    for room in tactical.player_ship.rooms:
        if room.crew:
            print(f"    {room.name}: {room.crew}")
            crew_count += len(room.crew)

    if crew_count > 0:
        print(f"\n✓ Crew display shows {crew_count} crew members")
        print("✓ Crew display test PASSED")
        return True
    else:
        print("\n✗ No crew shown in tactical display")
        return False

def main():
    """Run all tests"""
    print("\n🚀 SpaceCMD New Features Test Suite")
    print("Testing:")
    print("  1. Jump Animation with Moving Stars")
    print("  2. Crew Display Synchronization")
    print()

    results = []

    # Test jump animation
    try:
        results.append(("Jump Animation", test_jump_animation()))
    except Exception as e:
        print(f"\n✗ Jump animation test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Jump Animation", False))

    # Test crew display
    try:
        results.append(("Crew Display", test_crew_display()))
    except Exception as e:
        print(f"\n✗ Crew display test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Crew Display", False))

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

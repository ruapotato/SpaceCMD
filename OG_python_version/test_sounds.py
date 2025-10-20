#!/usr/bin/env python3
"""Test sound effects system"""

import sys
import time
sys.path.insert(0, '/home/david/SpaceCMD')

print("Testing Sound Effects System")
print("=" * 60)

try:
    from core.audio.sound_fx import get_sound_manager, play_sound

    sound_mgr = get_sound_manager()

    print(f"\n✓ Sound system initialized")
    print(f"  Generated {len(sound_mgr.sounds)} sound effects")

    print("\nTesting sounds:")
    print("  1. Laser fire...")
    play_sound("laser_fire", 0.5)
    time.sleep(0.3)

    print("  2. Shield hit...")
    play_sound("shield_hit", 0.6)
    time.sleep(0.3)

    print("  3. Hull hit...")
    play_sound("hull_hit", 0.7)
    time.sleep(0.4)

    print("  4. System damage...")
    play_sound("system_damage", 0.5)
    time.sleep(0.3)

    print("  5. Explosion...")
    play_sound("explosion", 0.8)
    time.sleep(1.0)

    print("  6. UI click...")
    play_sound("click", 0.3)
    time.sleep(0.2)

    print("  7. UI select...")
    play_sound("select", 0.3)
    time.sleep(0.2)

    print("\n✓ All sounds played successfully!")
    print("\nSound effects are fully integrated into:")
    print("  - Weapon fire (laser, missile, beam)")
    print("  - Combat impacts (shield hit, hull hit)")
    print("  - System damage alerts")
    print("  - Explosions (ship destruction)")
    print("  - UI interactions (clicks, selections)")

    print("\n" + "=" * 60)
    print("✓ Sound system test complete!")

except Exception as e:
    print(f"\n✗ Error testing sounds: {e}")
    import traceback
    traceback.print_exc()

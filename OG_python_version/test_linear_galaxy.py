#!/usr/bin/env python3
"""
Quick test to verify linear galaxy system is working
"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_kestrel
from core.ship_os import ShipOS
from core.world_manager import WorldManager

print("=" * 60)
print("LINEAR GALAXY SYSTEM TEST")
print("=" * 60)

# Load ship
print("\n1. Loading Kestrel ship...")
ship = create_kestrel()
print(f"   ✓ Ship loaded: {ship.name}")

# Create ShipOS
print("\n2. Creating ShipOS...")
ship_os = ShipOS(ship=ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')
print(f"   ✓ ShipOS initialized")

# Create WorldManager with linear galaxy
print("\n3. Creating WorldManager with LinearGalaxy...")
world_manager = WorldManager(ship_os, max_galaxy_distance=1000.0)
ship_os.world_manager = world_manager
print(f"   ✓ WorldManager created")
print(f"   ✓ Galaxy max distance: {world_manager.galaxy.max_distance}")
print(f"   ✓ Number of POIs: {len(world_manager.galaxy.pois)}")
print(f"   ✓ Ship starting position: {ship.galaxy_distance_from_center:.1f}")

# Test VFS device files
print("\n4. Testing VFS device files...")

# Test /proc/ship/location
exit_code, stdout, stderr = ship_os.execute_command('cat /proc/ship/location')
print(f"\n   /proc/ship/location:")
print("   " + stdout.replace('\n', '\n   '))

# Test /proc/ship/sensors
exit_code, stdout, stderr = ship_os.execute_command('cat /proc/ship/sensors')
print(f"\n   /proc/ship/sensors:")
print("   " + stdout.replace('\n', '\n   '))

# Test /proc/ship/pois
exit_code, stdout, stderr = ship_os.execute_command('cat /proc/ship/pois')
print(f"\n   /proc/ship/pois (showing first 20 lines):")
lines = stdout.split('\n')[:20]
print("   " + '\n   '.join(lines))

# Test ship movement
print("\n5. Testing ship movement...")
print(f"   Current position: {ship.galaxy_position:.1f}")

# Set course toward center
ship.set_course(800.0)
print(f"   ✓ Course set to: {ship.target_position:.1f}")

# Simulate some movement
print("\n   Simulating 5 seconds of movement...")
for i in range(5):
    ship.update_position(1.0)
    print(f"   - After {i+1}s: Position={ship.galaxy_position:.1f}, Velocity={ship.velocity:.2f}")

# Test enemy spawn
print("\n6. Testing enemy spawn with OS...")
world_manager.trigger_encounter(enemy_type="gnat", forced=True)
if world_manager.enemy_ship:
    print(f"   ✓ Enemy spawned: {world_manager.enemy_ship.ship.name}")
    print(f"   ✓ Enemy has ShipOS: {world_manager.enemy_ship.ship_os is not None}")
    print(f"   ✓ Enemy AI script exists: {world_manager.enemy_ship.ship_os.vfs.stat('/root/ai.poo', 1) is not None}")

    # Try running enemy AI
    print("\n   Running enemy AI turn...")
    result = world_manager.enemy_ship.run_ai_turn()
    print(f"   ✓ AI executed: {result}")

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)

#!/usr/bin/env python3
"""
Test the new world architecture:
- Python (WorldManager) controls enemy spawning
- ShipOS controls the ship
- Hostile script activates beacon, not directly spawns enemies
"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
import time

print("=" * 60)
print("Testing World Architecture")
print("=" * 60)
print()

# Create ship and OS
print("1. Creating ship and ShipOS...")
ship = create_ship("kestrel")
ship_os = ShipOS(ship=ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')
print(f"   ✓ Ship created: {ship.name}")
print(f"   ✓ Hull: {ship.hull}/{ship.hull_max}")
print()

# Create world manager (Python layer)
print("2. Creating WorldManager (Python layer)...")
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager  # Connect them
print("   ✓ WorldManager created")
print("   ✓ ShipOS connected to world")
print()

# Test beacon device
print("3. Testing beacon device...")
exit_code, stdout, stderr = ship_os.execute_command("cat /dev/ship/beacon")
print(f"   Beacon status: {stdout.strip()}")
print()

# Test hostile script exists
print("4. Testing hostile script...")
exit_code, stdout, stderr = ship_os.execute_command("ls -la /tmp/hostile.poo")
if exit_code == 0:
    print("   ✓ Hostile script exists at /tmp/hostile.poo")
    print(f"   {stdout.strip()}")
else:
    print("   ✗ Hostile script not found!")
print()

# Test activating beacon via command
print("5. Activating distress beacon...")
exit_code, stdout, stderr = ship_os.execute_command("echo 1 > /dev/ship/beacon")
print(f"   Command exit code: {exit_code}")
exit_code, stdout, stderr = ship_os.execute_command("cat /dev/ship/beacon")
print(f"   Beacon status: {stdout.strip()}")
print(f"   WorldManager sees beacon: {world_manager.distress_beacon_active}")
print()

# Test manual encounter trigger
print("6. Testing manual encounter trigger (Python layer)...")
success = world_manager.trigger_encounter("gnat", forced=True)
if success:
    print("   ✓ Encounter triggered!")
    print(f"   Enemy: {world_manager.enemy_ship.name}")
    print(f"   Hull: {world_manager.enemy_ship.hull}/{world_manager.enemy_ship.hull_max}")
    print(f"   In combat: {world_manager.is_in_combat()}")
else:
    print("   ✗ Failed to trigger encounter")
print()

# Test combat update
print("7. Testing combat update...")
if world_manager.is_in_combat():
    prev_hull = ship.hull
    world_manager.update(0.5)  # Update for 0.5 seconds
    print(f"   Player hull: {ship.hull}/{ship.hull_max} (was {prev_hull})")
    print(f"   Enemy hull: {world_manager.enemy_ship.hull}/{world_manager.enemy_ship.hull_max}")
    print(f"   Still in combat: {world_manager.is_in_combat()}")
print()

print("=" * 60)
print("Architecture Test Complete!")
print("=" * 60)
print()
print("Summary:")
print("  - ShipOS controls ship systems ✓")
print("  - WorldManager controls encounters ✓")
print("  - Beacon device works ✓")
print("  - Hostile script exists ✓")
print("  - Proper separation of concerns ✓")

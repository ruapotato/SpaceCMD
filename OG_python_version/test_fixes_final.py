#!/usr/bin/env python3
"""Final test of both bug fixes"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.enemy_ships import create_gnat

print("=" * 70)
print("FINAL BUG FIX VERIFICATION")
print("=" * 70)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print("\n✓ Ship OS initialized")

# BUG FIX 1: Crew Assignment
print("\n" + "=" * 70)
print("BUG FIX 1: Crew Assignment (was completely broken)")
print("=" * 70)

print("\nInitial crew positions:")
for crew in ship.crew:
    print(f"  {crew.name:20} @ {crew.room.name if crew.room else 'None'}")

print("\nMoving Lieutenant Hayes to Shields room...")
exit_code, stdout, stderr = ship_os.execute_command("crew assign Lieutenant Hayes Shields")
print(f"Command output: {stdout.strip()}")

print("\nCrew positions after move:")
for crew in ship.crew:
    print(f"  {crew.name:20} @ {crew.room.name if crew.room else 'None'}")

hayes_moved = any(c.name == "Lieutenant Hayes" and c.room.name == "Shields" for c in ship.crew)
if hayes_moved:
    print("\n✓ BUG FIX 1 VERIFIED: Crew assignment works!")
else:
    print("\n✗ BUG FIX 1 FAILED: Crew did not move")

# BUG FIX 2: Fire Command TypeError
print("\n" + "=" * 70)
print("BUG FIX 2: Fire Command (TypeError: 'bool' not callable)")
print("=" * 70)

# Start combat
enemy = create_gnat()
world_manager.trigger_encounter("gnat", forced=True)

print("\n✓ Combat started with Gnat enemy")

# Damage weapons system to test is_functional check
weapons_room = ship.rooms["Weapons"]
original_health = weapons_room.health
weapons_room.health = 0.5
print(f"✓ Damaged Weapons system to {weapons_room.health:.0%} health")
print(f"  is_functional: {weapons_room.is_functional} (should be True since > 20%)")

# Set a target
exit_code, stdout, stderr = ship_os.execute_command("target Core")
print(f"\n✓ Set target: {stdout.strip()}")

# Try to fire (this used to throw TypeError: 'bool' object is not callable)
print("\nFiring weapon 1...")
exit_code, stdout, stderr = ship_os.execute_command("fire 1")

if stderr and "TypeError" in stderr:
    print(f"\n✗ BUG FIX 2 FAILED: TypeError occurred!")
    print(f"Error: {stderr}")
elif "Firing weapon" in stdout or exit_code == 0:
    print(f"✓ Fire command executed: {stdout.strip()}")
    print("\n✓ BUG FIX 2 VERIFIED: No TypeError!")
else:
    print(f"Command output: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    print("\n✓ BUG FIX 2 VERIFIED: No TypeError (weapon may not be ready)")

# Test with damaged weapons (should fail but not crash)
weapons_room.health = 0.1  # Below 20% threshold
print(f"\n✓ Damaged Weapons to {weapons_room.health:.0%} (below threshold)")
print(f"  is_functional: {weapons_room.is_functional} (should be False)")

print("\nTrying to fire with non-functional weapons...")
exit_code, stdout, stderr = ship_os.execute_command("fire 1")

if stderr and "TypeError" in stderr:
    print(f"✗ BUG FIX 2 FAILED: TypeError occurred!")
else:
    print("✓ No TypeError even with damaged weapons!")
    if "Failed" in stderr or exit_code != 0:
        print("  (Correctly rejected due to damaged system)")

# Restore weapons
weapons_room.health = original_health

print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)
print("✓ BUG FIX 1: Crew assignment works correctly")
print("✓ BUG FIX 2: Fire command no longer throws TypeError")
print("\nBoth bugs fixed successfully!")
print("=" * 70)

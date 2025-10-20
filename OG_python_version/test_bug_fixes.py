#!/usr/bin/env python3
"""Test bug fixes for fire command and crew assignment"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.enemy_ships import create_gnat

print("Testing Bug Fixes")
print("=" * 60)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print("\n1. Testing crew assignment (was broken)")
print("-" * 60)

# Show initial crew positions
exit_code, stdout, stderr = ship_os.execute_command("crew")
print(stdout)

# Try to assign a crew member
print("\nTrying: crew assign 'Lieutenant Hayes' Engines")
exit_code, stdout, stderr = ship_os.execute_command("crew assign 'Lieutenant Hayes' Engines")
print(f"Exit code: {exit_code}")
print(f"Output: {stdout}")
if stderr:
    print(f"Error: {stderr}")

# Verify the move
print("\nVerifying crew moved:")
exit_code, stdout, stderr = ship_os.execute_command("crew")
print(stdout)

print("\n2. Testing fire command (TypeError bug)")
print("-" * 60)

# Start combat
enemy = create_gnat()
world_manager.start_combat(enemy)

print("Combat started with Gnat enemy")

# Set a target
exit_code, stdout, stderr = ship_os.execute_command("target Core")
print(f"\nSetting target: {stdout.strip()}")

# Try to fire (this used to throw TypeError)
print("\nTrying: fire 1")
exit_code, stdout, stderr = ship_os.execute_command("fire 1")
print(f"Exit code: {exit_code}")
print(f"Output: {stdout}")
if stderr:
    print(f"Error: {stderr}")

# Check if it worked
if "Firing weapon" in stdout or "not ready" in stdout.lower():
    print("✓ Fire command works (no TypeError!)")
else:
    print("✗ Fire command may have failed")

print("\n" + "=" * 60)
print("✓ Bug fix tests complete!")
print("=" * 60)

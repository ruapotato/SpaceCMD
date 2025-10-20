#!/usr/bin/env python3
"""Debug the shell fire command"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print("Starting combat...")
world_manager.trigger_encounter("gnat", forced=True)

print("\nTargeting...")
ship_os.execute_command("target Core")

# Charge weapon
ship.weapons[0].charge = 1.0

# Check if fire script exists
print("\nChecking fire script...")
exit_code, stdout, stderr = ship_os.execute_command("which fire")
print(f"which fire: {stdout.strip()}")

# Try reading the fire script
print("\nReading fire script...")
exit_code, stdout, stderr = ship_os.execute_command("cat /bin/fire | head -20")
print(f"First 20 lines of /bin/fire:")
print(stdout)

# Now try firing
print("\n" + "="*60)
print("Attempting to execute: fire 1")
print("="*60)
exit_code, stdout, stderr = ship_os.execute_command("fire 1")
print(f"Exit code: {exit_code}")
print(f"STDOUT:\n{stdout}")
print(f"STDERR:\n{stderr}")

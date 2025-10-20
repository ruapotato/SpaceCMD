#!/usr/bin/env python3
"""Test firing weapon when it's actually ready"""

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

print("\nTargeting enemy Core...")
ship_os.execute_command("target Core")

# Charge the weapon manually for testing
print("\nCharging player weapon to 100%...")
ship.weapons[0].charge = 1.0
print(f"Weapon charge: {ship.weapons[0].charge}")
print(f"Weapon is_ready(): {ship.weapons[0].is_ready()}")

print("\nAttempting to fire weapon...")
exit_code, stdout, stderr = ship_os.execute_command("fire 1")
print(f"Exit code: {exit_code}")
print(f"Output: {stdout}")
print(f"Errors: {stderr}")

# Check enemy ship health
combat = world_manager.combat_state
print(f"\nEnemy hull after firing: {combat.enemy_ship.hull}/{combat.enemy_ship.hull_max}")

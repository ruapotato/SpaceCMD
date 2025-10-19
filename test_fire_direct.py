#!/usr/bin/env python3
"""Test firing weapon directly via combat_state"""

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
combat = world_manager.combat_state

print("\nTargeting enemy Core...")
combat.set_target("Core")

# Charge the weapon manually for testing
print("\nCharging player weapon to 100%...")
ship.weapons[0].charge = 1.0
print(f"Weapon charge: {ship.weapons[0].charge}")
print(f"Weapon is_ready(): {ship.weapons[0].is_ready()}")

print("\nAttempting to fire weapon via combat_state...")
try:
    result = combat.fire_player_weapon(0)
    print(f"fire_player_weapon returned: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Check enemy ship health
print(f"\nEnemy hull after firing: {combat.enemy_ship.hull}/{combat.enemy_ship.hull_max}")
print(f"Enemy 'Core' room health: {combat.enemy_ship.rooms['Core'].health:.0%}")

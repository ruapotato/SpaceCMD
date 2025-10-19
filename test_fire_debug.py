#!/usr/bin/env python3
"""Debug the fire command issue"""

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

print("\nChecking weapon...")
weapon = ship.weapons[0]
print(f"Weapon: {weapon.name}")
print(f"Charge: {weapon.charge}")
print(f"is_ready type: {type(weapon.is_ready)}")
print(f"is_ready value: {weapon.is_ready}")

# Try calling is_ready()
try:
    result = weapon.is_ready()
    print(f"is_ready() result: {result}")
except Exception as e:
    print(f"ERROR calling is_ready(): {e}")
    import traceback
    traceback.print_exc()

print("\nAttempting to fire via combat_state...")
try:
    result = world_manager.combat_state.fire_player_weapon(0)
    print(f"fire_player_weapon result: {result}")
except Exception as e:
    print(f"ERROR in fire_player_weapon: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""Test the fire command in actual combat"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_kestrel
from core.enemy_ships import create_gnat
from core.combat import CombatState
from core.ship_os import ShipOS
from core.world_manager import WorldManager

print("Testing fire command in combat scenario...")
print("=" * 60)

# Create player ship
player_ship = create_kestrel()
print(f"Player ship: {player_ship.name}")
print(f"  Weapons: {len(player_ship.weapons)}")
print(f"  Weapon 1: {player_ship.weapons[0].name}")
print(f"  Charge: {player_ship.weapons[0].charge:.1f}")
print(f"  Ready: {player_ship.weapons[0].is_ready()}")
print(f"  Power allocated to weapons: {[r.power_allocated for r in player_ship.rooms.values() if r.name == 'Weapons'][0]}")

# Create ShipOS
ship_os = ShipOS(player_ship)

# Create world manager and link it
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

# Trigger combat
world_manager.trigger_encounter("gnat", forced=True)
enemy = world_manager.enemy_ship
print(f"\nEnemy ship: {enemy.name}")

print(f"World manager in combat: {world_manager.is_in_combat()}")

# Set target
enemy_rooms = list(enemy.rooms.keys())
target_room = enemy_rooms[0] if enemy_rooms else None
print(f"\nSetting target to: {target_room}")

if target_room:
    exit_code, stdout, stderr = ship_os.execute_command(f"target {target_room}")
    print(f"  Target command: exit={exit_code}")
    print(f"  Output: {stdout.strip()}")
    if stderr:
        print(f"  Error: {stderr.strip()}")

# Check weapon status
print(f"\nWeapon status before fire:")
print(f"  Charge: {player_ship.weapons[0].charge:.1f}")
print(f"  Ready: {player_ship.weapons[0].is_ready()}")

# Try to fire
print(f"\nExecuting 'fire 1' command...")
exit_code, stdout, stderr = ship_os.execute_command("fire 1")

print(f"\nFire command result:")
print(f"  Exit code: {exit_code}")
print(f"  Stdout: {stdout.strip()}")
print(f"  Stderr: {stderr.strip()}")

# Check weapon status after
print(f"\nWeapon status after fire:")
print(f"  Charge: {player_ship.weapons[0].charge:.1f}")
print(f"  Ready: {player_ship.weapons[0].is_ready()}")

print("\n" + "=" * 60)
if exit_code == 0:
    print("✓ SUCCESS: Fire command worked!")
else:
    print(f"✗ FAIL: Fire command failed with exit code {exit_code}")
    print(f"   This means: bytes_written was {'' if exit_code != 0 else 'positive'}")

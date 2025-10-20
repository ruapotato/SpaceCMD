#!/usr/bin/env python3
"""Test combat balance improvements"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.enemy_ships import create_gnat
from core.combat import CombatState

print("Testing Combat Balance Improvements")
print("=" * 50)

# Create player ship
player = create_ship("kestrel")
print(f"\nPlayer Ship: {player.name}")
print(f"  Hull: {player.hull}/{player.hull_max}")
print(f"  Shields: {player.shields}/{player.shields_max}")
print(f"  Crew: {len(player.crew)}")

# Create enemy (tutorial gnat)
enemy = create_gnat()
print(f"\nEnemy Ship: {enemy.name}")
print(f"  Hull: {enemy.hull}/{enemy.hull_max}")
print(f"  Damage: {enemy.weapons[0].damage}")
print(f"  Cooldown: {enemy.weapons[0].cooldown}s")

# Create combat
combat = CombatState(player, enemy)

print("\n" + "=" * 50)
print("COMBAT TEST")
print("=" * 50)

# Simulate enemy firing once
print("\nEnemy fires laser...")
weapon = enemy.weapons[0]
weapon.charge = 1.0  # Fully charged

# Target player shields room
combat.enemy_target = "Shields"
success = combat._fire_weapon(enemy, player, weapon, "Shields")

if success:
    print(f"✓ Hit successful")
    print(f"  Player hull: {player.hull}/{player.hull_max}")
    print(f"  Player shields: {player.shields}/{player.shields_max}")

    # Check shields room health
    shields_room = player.rooms["Shields"]
    print(f"  Shields room health: {shields_room.health:.1%}")
    print(f"  Shields room functional: {shields_room.is_functional}")
    print(f"  Fire: {shields_room.on_fire}")
    print(f"  Breach: {shields_room.breached}")

print("\n" + "=" * 50)
print("CREW AUTO-REPAIR TEST")
print("=" * 50)

# Damage the weapons room significantly
weapons_room = player.rooms["Weapons"]
weapons_room.health = 0.5
print(f"\nDamaged Weapons room to {weapons_room.health:.1%}")
print(f"  Crew in room: {len(weapons_room.crew)}")
print(f"  Is functional: {weapons_room.is_functional}")

# Assign a crew member to weapons room
if player.crew:
    crew = player.crew[0]
    crew.assign_to_room(weapons_room)
    print(f"  Assigned {crew.name} to Weapons room")

    # Simulate repair for 5 seconds
    print(f"\nSimulating 5 seconds of repair...")
    for i in range(5):
        player.update(1.0)
        print(f"  After {i+1}s: {weapons_room.health:.1%} ({weapons_room.is_functional})")
        if weapons_room.health >= 1.0:
            print(f"  ✓ Fully repaired!")
            break

print("\n" + "=" * 50)
print("SYSTEM DURABILITY TEST")
print("=" * 50)

# Test that systems work at low health
test_room = player.rooms["Engines"]
test_room.power_allocated = 2
test_room.health = 0.3  # 30% health

print(f"\nEngines room at {test_room.health:.1%} health")
print(f"  Power: {test_room.power_allocated}")
print(f"  Crew: {len(test_room.crew)}")
print(f"  Is functional: {test_room.is_functional} (should be True if health > 20%)")

test_room.health = 0.15  # 15% health
print(f"\nEngines room at {test_room.health:.1%} health")
print(f"  Is functional: {test_room.is_functional} (should be False if health < 20%)")

print("\n" + "=" * 50)
print("✓ Balance tests complete!")
print("=" * 50)

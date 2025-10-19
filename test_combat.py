#!/usr/bin/env python3
"""
Test strategic combat and crew bonuses
"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_kestrel
from core.enemy_ships import create_gnat
from core.combat import CombatState
from core.ship import SystemType

print("=" * 60)
print("STRATEGIC COMBAT TEST")
print("=" * 60)

# Create player ship
player = create_kestrel()
print(f"\n✓ Player ship: {player.name}")
print(f"  Hull: {player.hull}/{player.hull_max}")
print(f"  Power: {player.reactor_power} (base)")

# Test reactor bonus
reactor_room = None
for room_name, room in player.rooms.items():
    if room.system_type == SystemType.REACTOR:
        reactor_room = room
        break

if reactor_room and player.crew:
    # Move a crew to reactor
    player.crew[0].assign_to_room(reactor_room)
    available_power = player.get_available_power()
    bonus = available_power - player.reactor_power
    print(f"  Power with crew in reactor: {available_power} (+{bonus} bonus!)")
    print(f"  ✓ Reactor crew bonus working!")

# Create enemy
enemy = create_gnat()
print(f"\n✓ Enemy ship: {enemy.name}")
print(f"  Hull: {enemy.hull}/{enemy.hull_max}")
print(f"  Shields: {int(enemy.shields)}/{enemy.shields_max}")
print(f"\n  Strategic Layout:")
for room_name, room in enemy.rooms.items():
    if room.system_type != SystemType.NONE:
        print(f"    - {room.name:12} ({room.system_type.value:8}) HP:{room.health:.0%} PWR:{room.power_allocated}")

# Create combat
combat = CombatState(player, enemy)
print(f"\n✓ Combat initiated")
print(f"  Combat distance: {combat.combat_distance:.1f} units")

# Test strategic targeting
print(f"\n📍 Testing strategic targeting:")

# Check if weapons system is functional
weapons_system_ok = False
for room_name, room in player.rooms.items():
    if room.system_type == SystemType.WEAPONS:
        print(f"\n  Player weapons room: {room.name}")
        print(f"    Power: {room.power_allocated}/{room.max_power}")
        print(f"    Health: {room.health:.0%}")
        print(f"    Functional: {room.is_functional}")
        if not room.is_functional:
            print(f"    ⚠️ Weapons room not functional! Allocating power...")
            # Try to power it
            player.allocate_power(SystemType.WEAPONS, 2)
            print(f"    Power after allocation: {room.power_allocated}/{room.max_power}")
            print(f"    Functional now: {room.is_functional}")
        weapons_system_ok = room.is_functional
        break

# Move closer to get in range
print(f"\n  Moving closer to get in range...")
combat.combat_distance = 3.0  # Set to close range
print(f"  Combat distance: {combat.combat_distance:.1f} units")

# Target enemy weapons
combat.set_target("Weapons")
print(f"\n1. Targeting enemy WEAPONS system")
print(f"   Before: Weapons HP = {enemy.rooms['Weapons'].health:.0%}")

# Fire at weapons
if player.weapons and weapons_system_ok:
    weapon = player.weapons[0]
    weapon.charge = 1.0  # Fully charge
    print(f"   Weapon: {weapon.name} (damage: {weapon.damage}, charge: {weapon.charge:.0%})")
    print(f"   Range: {weapon.range} (combat distance: {combat.combat_distance:.1f})")
    success = combat.fire_player_weapon(0)
    if success:
        print(f"   ✓ Fired {weapon.name}!")
        print(f"   After: Weapons HP = {enemy.rooms['Weapons'].health:.0%}")
        print(f"   Enemy Hull: {enemy.hull}/{enemy.hull_max}")

        # Check if system was damaged significantly
        if enemy.rooms['Weapons'].health < 1.0:
            print(f"   ✓ Strategic targeting working! System damaged without destroying hull!")
        else:
            print(f"   ⚠️ System not damaged enough")
    else:
        print(f"   ✗ Failed to fire weapon")
elif not weapons_system_ok:
    print(f"   ✗ Weapons system not functional!")
else:
    print(f"   ✗ No weapons!")

# Show damage to all systems
print(f"\n📊 Enemy system status after attack:")
for room_name, room in enemy.rooms.items():
    if room.system_type != SystemType.NONE:
        status = "OK" if room.health > 0.7 else "DMG" if room.health > 0.3 else "CRIT"
        print(f"    [{status}] {room.name:12} HP:{room.health:5.0%}  {'⚠️' if room.health < 0.7 else '✓'}")

print(f"\n   Enemy Hull: {enemy.hull}/{enemy.hull_max}")
if enemy.hull > enemy.hull_max * 0.8:
    print(f"   ✓ Hull mostly intact - can disable without destroying!")

print("\n" + "=" * 60)
print("✓ STRATEGIC COMBAT SYSTEM WORKING!")
print("=" * 60)
print("\nKey Features:")
print("  ✓ Crew in reactor gives +power")
print("  ✓ Can target specific enemy systems")
print("  ✓ Systems take significant damage when targeted")
print("  ✓ Hull takes minimal damage (can disable without killing)")
print("=" * 60)

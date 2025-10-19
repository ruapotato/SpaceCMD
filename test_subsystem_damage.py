#!/usr/bin/env python3
"""Test FTL-style subsystem damage mechanics"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.ship import SystemType

print("=" * 70)
print("FTL-STYLE SUBSYSTEM DAMAGE TEST")
print("=" * 70)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)  # Boot to install scripts
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print("\n1. Starting combat with Gnat...")
success = world_manager.trigger_encounter("gnat", forced=True)

if not success:
    print("✗ Failed to start combat")
    exit(1)

combat = world_manager.combat_state
print(f"✓ Combat started with {combat.enemy_ship.name}")

# Find enemy's weapon pod room
enemy_weapon_room = None
for room_name, room in combat.enemy_ship.rooms.items():
    if room.system_type == SystemType.WEAPONS:
        enemy_weapon_room = room
        break

if not enemy_weapon_room:
    print("✗ Enemy has no weapons system!")
    exit(1)

print(f"\n2. Enemy weapons system: {enemy_weapon_room.name}")
print(f"   Initial health: {enemy_weapon_room.health:.0%}")
print(f"   Is functional: {enemy_weapon_room.is_functional}")

# Target the enemy weapons system
print(f"\n3. Targeting enemy {enemy_weapon_room.name}...")
exit_code, stdout, stderr = ship_os.execute_command(f"target {enemy_weapon_room.name}")
print(f"   {stdout.strip()}")

# Try to fire our weapon
print(f"\n4. Firing our weapon at enemy weapons system...")
exit_code, stdout, stderr = ship_os.execute_command("fire 1")
print(f"   Exit code: {exit_code}")
print(f"   Output: {stdout.strip()}")
if stderr:
    print(f"   Errors: {stderr.strip()}")

# Check enemy system health after hit
print(f"\n5. Enemy weapons system after hit:")
print(f"   Health: {enemy_weapon_room.health:.0%}")
print(f"   Is functional: {enemy_weapon_room.is_functional}")

# Now damage OUR weapons system to test error handling
print(f"\n6. Damaging OUR weapons system to test error handling...")
player_weapon_room = None
for room_name, room in ship.rooms.items():
    if room.system_type == SystemType.WEAPONS:
        player_weapon_room = room
        break

if player_weapon_room:
    print(f"   Our weapons system: {player_weapon_room.name}")
    print(f"   Initial health: {player_weapon_room.health:.0%}")

    # Damage it heavily
    player_weapon_room.take_damage(0.8)  # Reduce to 20% health
    print(f"   After damage: {player_weapon_room.health:.0%}")
    print(f"   Is functional: {player_weapon_room.is_functional}")

    # Try to fire with damaged system
    print(f"\n7. Attempting to fire with damaged weapons system...")
    exit_code, stdout, stderr = ship_os.execute_command("fire 1")
    print(f"   Exit code: {exit_code}")
    print(f"   Output: {stdout.strip()}")
    if stderr:
        print(f"   Errors: {stderr.strip()}")

    # Destroy the system completely
    player_weapon_room.take_damage(0.3)  # Reduce to 0% health
    print(f"\n8. Destroying weapons system completely...")
    print(f"   Health: {player_weapon_room.health:.0%}")
    print(f"   Is functional: {player_weapon_room.is_functional}")

    # Try to fire with destroyed system
    print(f"\n9. Attempting to fire with destroyed weapons system...")
    exit_code, stdout, stderr = ship_os.execute_command("fire 1")
    print(f"   Exit code: {exit_code}")
    print(f"   Output: {stdout.strip()}")
    if stderr:
        print(f"   Errors: {stderr.strip()}")

    # Check system status via sysfs
    print(f"\n10. Checking system status via /sys/ship/systems/weapons/status...")
    exit_code, stdout, stderr = ship_os.execute_command("cat /sys/ship/systems/weapons/status")
    print(f"    {stdout.strip()}")

print("\n" + "=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
print("\nExpected behaviors:")
print("✓ Targeting enemy systems works")
print("✓ Damage is applied to targeted subsystems")
print("✓ Damaged systems show reduced health")
print("✓ Destroyed systems cannot be used (fire command fails)")
print("✓ Clear error messages when trying to use broken systems")
print("=" * 70)

#!/usr/bin/env python3
"""Test that enemy can damage player hull"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager

print("=" * 60)
print("DAMAGE TEST")
print("=" * 60)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print(f"\nPlayer ship starting hull: {ship.hull}/{ship.hull_max}")
print(f"Player ship starting shields: {ship.shields}/{ship.shields_max}")

# Start combat
print("\nStarting combat with Gnat...")
success = world_manager.trigger_encounter("gnat", forced=True)

if success:
    combat = world_manager.combat_state
    print(f"✓ Combat started")
    print(f"  Enemy: {combat.enemy_ship.name}")
    print(f"  Enemy hull: {combat.enemy_ship.hull}/{combat.enemy_ship.hull_max}")
    print(f"  Enemy shields: {combat.enemy_ship.shields}/{combat.enemy_ship.shields_max}")
    print(f"  Enemy weapon damage: {combat.enemy_ship.weapons[0].damage}")

    # Simulate several combat turns
    print("\nSimulating combat updates...")
    for i in range(5):
        print(f"\n--- Turn {i+1} ---")
        world_manager.update(0.5)  # Half second update

        print(f"Player hull: {ship.hull}/{ship.hull_max}")
        print(f"Player shields: {ship.shields}/{ship.shields_max}")
        print(f"Enemy hull: {combat.enemy_ship.hull}/{combat.enemy_ship.hull_max}")

        # Show last 3 log entries (if available)
        if hasattr(combat, 'combat_log') and combat.combat_log:
            print("Recent combat log:")
            for entry in combat.combat_log[-3:]:
                print(f"  {entry}")

        if ship.hull < ship.hull_max:
            print("\n🎯 SUCCESS! Enemy is dealing hull damage!")
            break
    else:
        print("\n⚠️  No hull damage detected after 5 turns")
else:
    print("✗ Failed to start combat")

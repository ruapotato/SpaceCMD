#!/usr/bin/env python3
"""Test that starting weapon is fully charged"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_kestrel

print("Testing weapon charge fix...")
print("=" * 60)

ship = create_kestrel()

print(f"\nShip: {ship.name}")
print(f"Weapons: {len(ship.weapons)}")

for i, weapon in enumerate(ship.weapons):
    print(f"\nWeapon {i+1}: {weapon.name}")
    print(f"  Type: {weapon.weapon_type}")
    print(f"  Charge: {weapon.charge:.1f} / 1.0")
    print(f"  Cooldown: {weapon.cooldown_time}s")
    print(f"  Ready to fire: {'YES ✓' if weapon.charge >= 1.0 else 'NO (charging...)'}")

print("\n" + "=" * 60)
if ship.weapons[0].charge >= 1.0:
    print("✓ SUCCESS: Starting weapon is fully charged and ready!")
else:
    print(f"✗ FAIL: Weapon charge is {ship.weapons[0].charge}, expected 1.0")

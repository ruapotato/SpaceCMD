#!/usr/bin/env python3
"""Quick test to check if hostile script is created"""

from core.ships import create_ship
from core.ship_os import ShipOS

ship = create_ship("kestrel")
ship_os = ShipOS(ship=ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

print("Checking /tmp directory...")
code, out, err = ship_os.execute_command("ls -la /tmp/")
print(out)
print()

print("Checking for hostile.poo...")
code, out, err = ship_os.execute_command("ls -la /tmp/hostile.poo")
print(f"Exit code: {code}")
if code == 0:
    print(out)
else:
    print("File not found!")
    print(err)
print()

print("Trying to read the file...")
code, out, err = ship_os.execute_command("cat /tmp/hostile.poo")
if code == 0:
    print("SUCCESS! File contents:")
    print(out)
else:
    print(f"FAILED with code {code}")
    print(err)

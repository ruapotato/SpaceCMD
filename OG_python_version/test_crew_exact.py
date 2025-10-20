#!/usr/bin/env python3
"""Test direct device write for crew assignment"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.ship_os import ShipOS

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

print("Crew before:")
for crew in ship.crew:
    print(f"  {crew.name} @ {crew.room.name if crew.room else 'None'}")

# Direct device write test
print("\nDirect test: echo 'Lieutenant Hayes Shields' > /dev/ship/crew_assign")
exit_code, stdout, stderr = ship_os.execute_command("echo 'Lieutenant Hayes Shields' > /dev/ship/crew_assign")
print(f"Exit: {exit_code}")

print("\nCrew after:")
for crew in ship.crew:
    print(f"  {crew.name} @ {crew.room.name if crew.room else 'None'}")

# Try via command
print("\n" + "=" * 60)
print("Via command: crew assign Lieutenant Hayes Shields")
exit_code, stdout, stderr = ship_os.execute_command("crew assign Lieutenant Hayes Shields")
print(f"Exit: {exit_code}")
print(f"Out: {stdout}")

print("\nCrew final:")
for crew in ship.crew:
    print(f"  {crew.name} @ {crew.room.name if crew.room else 'None'}")

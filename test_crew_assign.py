#!/usr/bin/env python3
"""Simple test of crew assignment"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.ship_os import ShipOS

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

print("Ship rooms:")
for name, room in ship.rooms.items():
    print(f"  {name}: system_type={room.system_type.value if room.system_type else 'None'}")

print("\nCrew members:")
for crew in ship.crew:
    room_name = crew.room.name if crew.room else "None"
    print(f"  {crew.name} @ {room_name}")

# Test without quotes
print("\n" + "=" * 60)
print("Test 1: crew assign Lieutenant_Hayes Shields")
exit_code, stdout, stderr = ship_os.execute_command("crew assign Lieutenant_Hayes Shields")
print(f"Exit: {exit_code}")
print(f"Out: {stdout}")
print(f"Err: {stderr}")

# Check the crew position
print("\nCrew after assignment:")
for crew in ship.crew:
    room_name = crew.room.name if crew.room else "None"
    print(f"  {crew.name} @ {room_name}")

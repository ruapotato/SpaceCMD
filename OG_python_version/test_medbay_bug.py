#!/usr/bin/env python3
"""Test Medbay crew assignment bug"""

import sys
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.ship_os import ShipOS

# Create ship
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

print("Actual ship rooms:")
for name, room in ship.rooms.items():
    system = room.system_type.value if room.system_type else "none"
    print(f"  '{name}': system_type={system}")

print("\nTactical display room names (from ShipLayout):")
from core.gui.tactical_widget import ShipLayout
layout = ShipLayout("KESTREL")
for room in layout.rooms:
    print(f"  '{room.name}': system_type={room.system_type}")

print("\n" + "=" * 60)
print("Testing crew assignment to Medbay:")
print("=" * 60)

# Try the exact command that tactical widget would send
print("\nCommand: crew assign Lieutenant Hayes Medbay")
exit_code, stdout, stderr = ship_os.execute_command("crew assign Lieutenant Hayes Medbay")
print(f"Exit: {exit_code}")
print(f"Out: {stdout}")
print(f"Err: {stderr}")

# Check what happened
for crew in ship.crew:
    if crew.name == "Lieutenant Hayes":
        room_name = crew.room.name if crew.room else "None"
        print(f"\nLieutenant Hayes location: {room_name}")

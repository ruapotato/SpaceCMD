#!/usr/bin/env python3
"""
spacecmd - Ship Demo

Test the new ship system and renderer.
"""

import sys
import time
from core.ships import create_ship
from core.render import ShipRenderer


def main():
    """Demo the ship system"""
    print("=" * 60)
    print("SPACECMD - Ship System Demo")
    print("=" * 60)
    print()

    # Create ships
    ship_types = ["kestrel", "stealth", "mantis"]

    if len(sys.argv) > 1:
        ship_type = sys.argv[1]
        if ship_type not in ship_types:
            print(f"Unknown ship type: {ship_type}")
            print(f"Available: {', '.join(ship_types)}")
            sys.exit(1)
    else:
        ship_type = "kestrel"

    print(f"Creating {ship_type}...\n")
    ship = create_ship(ship_type)

    # Create renderer
    renderer = ShipRenderer(use_color=True)

    # Render ship
    renderer.render_to_terminal(ship)

    print("\n" + "=" * 60)
    print("SHIP DETAILS")
    print("=" * 60)
    print()
    print(f"Name: {ship.name}")
    print(f"Class: {ship.ship_class}")
    print(f"Hull: {ship.hull}/{ship.hull_max}")
    print(f"Shields: {int(ship.shields)}/{ship.shields_max}")
    print(f"Power: {ship.reactor_power - ship.power_available}/{ship.reactor_power}")
    print(f"Fuel: {ship.fuel}")
    print()

    print("CREW:")
    for crew in ship.crew:
        print(f"  - {crew.name} ({crew.race})")
        print(f"    HP: {crew.health}/{crew.health_max}")
        print(f"    Location: {crew.room.name if crew.room else 'None'}")
        print(f"    Skills: {crew.skills}")
        print()

    print("ROOMS:")
    for room_name, room in ship.rooms.items():
        print(f"  - {room_name}:")
        print(f"    System: {room.system_type.value}")
        print(f"    Health: {room.health:.1%}")
        print(f"    Power: {room.power_allocated}/{room.max_power}")
        print(f"    Oxygen: {room.oxygen_level:.1%}")
        print(f"    Crew: {len(room.crew)}")
        print()

    print("=" * 60)
    print("SIMULATION TEST")
    print("=" * 60)
    print("\nSimulating 5 seconds of ship operation...\n")

    # Simulate some time passing
    for i in range(5):
        print(f"Tick {i + 1}/5...")
        ship.update(1.0)
        time.sleep(0.5)

    print("\nSimulation complete!")
    print("\nRendering ship after simulation:\n")

    renderer.render_to_terminal(ship)

    print("\n" + "=" * 60)
    print("TEST DAMAGE")
    print("=" * 60)
    print("\nSimulating damage to weapons system...\n")

    # Damage weapons room
    weapons_room = ship.rooms.get("Weapons")
    if weapons_room:
        weapons_room.take_damage(0.5)
        weapons_room.on_fire = True

    renderer.render_to_terminal(ship)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

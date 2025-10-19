"""
spacecmd - Ship Templates

Factory functions to create different ship types.
"""

from .ship import Ship, Room, Crew, SystemType, ShipSystem
from .weapons import create_weapon


def create_kestrel() -> Ship:
    """
    Create the Nautilus - a balanced human cruiser.
    Good starting ship with all basic systems.
    """
    ship = Ship("Nautilus", "Human Cruiser")

    # Resources
    ship.hull_max = 30
    ship.hull = 30
    ship.reactor_power = 8
    ship.power_available = 8
    ship.dark_matter = 20
    ship.missiles = 8
    ship.scrap = 0

    # Create rooms (3x3 grid layout)
    # Top row
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    helm.max_power = 2
    ship.add_room(helm)

    shields = Room("Shields", SystemType.SHIELDS, x=1, y=0)
    shields.max_power = 3
    ship.add_room(shields)

    oxygen = Room("Oxygen", SystemType.OXYGEN, x=2, y=0)
    oxygen.max_power = 1
    ship.add_room(oxygen)

    # Middle row
    weapons = Room("Weapons", SystemType.WEAPONS, x=0, y=1)
    weapons.max_power = 4
    ship.add_room(weapons)

    corridor = Room("Corridor", SystemType.NONE, x=1, y=1)
    corridor.max_power = 0
    ship.add_room(corridor)

    medbay = Room("Medbay", SystemType.MEDBAY, x=2, y=1)
    medbay.max_power = 2
    ship.add_room(medbay)

    # Bottom row
    reactor = Room("Reactor", SystemType.REACTOR, x=0, y=2)
    reactor.max_power = 0  # Reactor doesn't consume power
    ship.add_room(reactor)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=2)
    engines.max_power = 3
    ship.add_room(engines)

    sensors = Room("Sensors", SystemType.SENSORS, x=2, y=2)
    sensors.max_power = 2
    ship.add_room(sensors)

    # Connect rooms (for crew pathfinding and oxygen flow)
    helm.connect_to(shields)
    shields.connect_to(oxygen)
    helm.connect_to(weapons)
    shields.connect_to(corridor)
    oxygen.connect_to(medbay)
    weapons.connect_to(corridor)
    corridor.connect_to(medbay)
    weapons.connect_to(reactor)
    corridor.connect_to(engines)
    medbay.connect_to(sensors)
    reactor.connect_to(engines)
    engines.connect_to(sensors)

    # Add systems
    ship.add_system(ShipSystem("Helm Control", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Shield Generator", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Oxygen System", SystemType.OXYGEN), "Oxygen")
    ship.add_system(ShipSystem("Weapon Control", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Medbay", SystemType.MEDBAY), "Medbay")
    ship.add_system(ShipSystem("Reactor Core", SystemType.REACTOR), "Reactor")
    ship.add_system(ShipSystem("Engine Room", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Sensor Array", SystemType.SENSORS), "Sensors")

    # Initial power allocation
    ship.allocate_power(SystemType.SHIELDS, 2)
    ship.allocate_power(SystemType.OXYGEN, 1)
    ship.allocate_power(SystemType.ENGINES, 2)
    ship.allocate_power(SystemType.WEAPONS, 2)

    # Set shields
    ship.shields_max = 4
    ship.shields = 4

    # Create starting crew
    pilot = Crew("Lieutenant Hayes", "human")
    pilot.skills.helm = 1
    pilot.skills.weapons = 1
    ship.add_crew_member(pilot)
    pilot.assign_to_room(helm)

    engineer = Crew("Chief O'Brien", "human")
    engineer.skills.engines = 2
    engineer.skills.repair = 2
    ship.add_crew_member(engineer)
    engineer.assign_to_room(engines)

    gunner = Crew("Sergeant Vega", "human")
    gunner.skills.weapons = 2
    gunner.skills.shields = 1
    ship.add_crew_member(gunner)
    gunner.assign_to_room(weapons)

    # Add starting weapons
    burst_laser = create_weapon("burst_laser_ii")
    burst_laser.charge = 1.0  # Start fully charged and ready to fire!
    ship.add_weapon(burst_laser)

    return ship


def create_stealth_cruiser() -> Ship:
    """
    Create the Cucumber - weak hull, no shields, but has cloaking.
    """
    ship = Ship("Cucumber", "Stealth Cruiser")

    ship.hull_max = 20
    ship.hull = 20
    ship.reactor_power = 6
    ship.power_available = 6
    ship.dark_matter = 16
    ship.missiles = 4
    ship.scrap = 0

    # Stealth ships have no shields
    ship.shields_max = 0
    ship.shields = 0

    # Rooms
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    cloaking = Room("Cloaking", SystemType.CLOAKING, x=1, y=0)
    cloaking.max_power = 3
    ship.add_room(cloaking)

    weapons = Room("Weapons", SystemType.WEAPONS, x=0, y=1)
    weapons.max_power = 4
    ship.add_room(weapons)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=1)
    engines.max_power = 3
    ship.add_room(engines)

    reactor = Room("Reactor", SystemType.REACTOR, x=0, y=2)
    ship.add_room(reactor)

    oxygen = Room("Oxygen", SystemType.OXYGEN, x=1, y=2)
    ship.add_room(oxygen)

    # Connections
    helm.connect_to(cloaking)
    helm.connect_to(weapons)
    cloaking.connect_to(engines)
    weapons.connect_to(engines)
    weapons.connect_to(reactor)
    engines.connect_to(oxygen)
    reactor.connect_to(oxygen)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Cloaking Device", SystemType.CLOAKING), "Cloaking")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Reactor", SystemType.REACTOR), "Reactor")
    ship.add_system(ShipSystem("Oxygen", SystemType.OXYGEN), "Oxygen")

    # Initial power
    ship.allocate_power(SystemType.OXYGEN, 1)
    ship.allocate_power(SystemType.ENGINES, 3)
    ship.allocate_power(SystemType.WEAPONS, 2)

    # Crew
    pilot = Crew("Ghost", "human")
    pilot.skills.helm = 2
    pilot.skills.engines = 2
    ship.add_crew_member(pilot)
    pilot.assign_to_room(helm)

    gunner = Crew("Shadow", "human")
    gunner.skills.weapons = 3
    ship.add_crew_member(gunner)
    gunner.assign_to_room(weapons)

    return ship


def create_mantis_cruiser() -> Ship:
    """
    Create the Hairpin - teleporter, strong crew combat.
    """
    ship = Ship("Hairpin", "Mantis Cruiser")

    ship.hull_max = 25
    ship.hull = 25
    ship.reactor_power = 7
    ship.power_available = 7
    ship.dark_matter = 18
    ship.missiles = 6
    ship.scrap = 0

    # Rooms
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    shields = Room("Shields", SystemType.SHIELDS, x=1, y=0)
    shields.max_power = 2
    ship.add_room(shields)

    weapons = Room("Weapons", SystemType.WEAPONS, x=0, y=1)
    weapons.max_power = 3
    ship.add_room(weapons)

    teleporter = Room("Teleporter", SystemType.TELEPORTER, x=1, y=1)
    teleporter.max_power = 3
    ship.add_room(teleporter)

    oxygen = Room("Oxygen", SystemType.OXYGEN, x=2, y=1)
    ship.add_room(oxygen)

    reactor = Room("Reactor", SystemType.REACTOR, x=0, y=2)
    ship.add_room(reactor)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=2)
    engines.max_power = 2
    ship.add_room(engines)

    medbay = Room("Medbay", SystemType.MEDBAY, x=2, y=2)
    medbay.max_power = 2
    ship.add_room(medbay)

    # Connections
    helm.connect_to(shields)
    helm.connect_to(weapons)
    shields.connect_to(teleporter)
    weapons.connect_to(teleporter)
    teleporter.connect_to(oxygen)
    weapons.connect_to(reactor)
    teleporter.connect_to(engines)
    oxygen.connect_to(medbay)
    reactor.connect_to(engines)
    engines.connect_to(medbay)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Shields", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Teleporter", SystemType.TELEPORTER), "Teleporter")
    ship.add_system(ShipSystem("Oxygen", SystemType.OXYGEN), "Oxygen")
    ship.add_system(ShipSystem("Reactor", SystemType.REACTOR), "Reactor")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Medbay", SystemType.MEDBAY), "Medbay")

    # Initial power
    ship.allocate_power(SystemType.SHIELDS, 2)
    ship.allocate_power(SystemType.OXYGEN, 1)
    ship.allocate_power(SystemType.ENGINES, 1)
    ship.allocate_power(SystemType.WEAPONS, 2)
    ship.allocate_power(SystemType.TELEPORTER, 1)

    ship.shields_max = 2
    ship.shields = 2

    # Mantis crew - excellent fighters!
    warrior1 = Crew("Kazaaak", "mantis")
    warrior1.skills.combat = 4
    warrior1.skills.weapons = 1
    warrior1.combat_damage = 20  # Mantis hit harder
    ship.add_crew_member(warrior1)
    warrior1.assign_to_room(teleporter)

    warrior2 = Crew("Thraxxx", "mantis")
    warrior2.skills.combat = 4
    warrior2.skills.repair = 1
    warrior2.combat_damage = 20
    ship.add_crew_member(warrior2)
    warrior2.assign_to_room(teleporter)

    pilot = Crew("Skzzzt", "mantis")
    pilot.skills.helm = 2
    pilot.skills.combat = 2
    ship.add_crew_member(pilot)
    pilot.assign_to_room(helm)

    engineer = Crew("Vrzzak", "mantis")
    engineer.skills.engines = 2
    engineer.skills.combat = 2
    ship.add_crew_member(engineer)
    engineer.assign_to_room(engines)

    return ship


# Ship registry
SHIP_TEMPLATES = {
    "kestrel": create_kestrel,
    "stealth": create_stealth_cruiser,
    "mantis": create_mantis_cruiser,
}


def create_ship(ship_type: str) -> Ship:
    """Create a ship by type name"""
    if ship_type not in SHIP_TEMPLATES:
        raise ValueError(f"Unknown ship type: {ship_type}. Available: {list(SHIP_TEMPLATES.keys())}")

    return SHIP_TEMPLATES[ship_type]()

"""
spacecmd - Enemy Ship Templates

Factory functions for enemy ships.
"""

from .ship import Ship, Room, Crew, SystemType, ShipSystem
from .weapons import create_weapon
import random


def create_gnat() -> Ship:
    """
    Create a tiny, weak gnat-class ship.
    Perfect for tutorial - barely any threat!
    """
    ship = Ship("Hostile Gnat", "Gnat-class Drone")

    # Very weak stats - tutorial enemy
    ship.hull_max = 5
    ship.hull = 5
    ship.reactor_power = 2
    ship.power_available = 2
    ship.dark_matter = 0
    ship.scrap = 5  # Small reward

    # Minimal layout - just one tiny room
    helm = Room("Core", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    weapons = Room("Weapon Pod", SystemType.WEAPONS, x=1, y=0)
    weapons.max_power = 1
    ship.add_room(weapons)

    helm.connect_to(weapons)

    # Minimal systems
    ship.add_system(ShipSystem("Core", SystemType.HELM), "Core")
    ship.add_system(ShipSystem("Weapon Pod", SystemType.WEAPONS), "Weapon Pod")

    # Minimal power
    ship.allocate_power(SystemType.WEAPONS, 1)

    # NO shields - super vulnerable
    ship.shields_max = 0
    ship.shields = 0

    # Weak AI crew - need crew in weapons room for it to function!
    pilot = Crew("Rogue AI", "robot")
    pilot.skills.weapons = 1  # Give some skill so it can fire
    pilot.health = 20
    ship.add_crew_member(pilot)
    pilot.assign_to_room(weapons)  # Put in weapons room so it can fire!

    # Very weak weapon - START CHARGED so it fires immediately!
    laser = create_weapon("basic_laser")
    laser.damage = 2  # Weak damage for tutorial enemy
    laser.cooldown = 15.0  # Slow firing
    laser.charge = 1.0  # START FULLY CHARGED!
    ship.add_weapon(laser)

    # Very fast - hard to hit, tries to get close
    ship.max_speed = 3.0
    ship.speed = 3.0

    return ship


def create_pirate_scout() -> Ship:
    """
    Create a weak pirate scout ship.
    """
    ship = Ship("Pirate Scout", "Pirate Scout")

    # Weaker stats
    ship.hull_max = 15
    ship.hull = 15
    ship.reactor_power = 4
    ship.power_available = 4
    ship.dark_matter = 0
    ship.scrap = 15  # Reward for defeating

    # Simple layout
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    weapons = Room("Weapons", SystemType.WEAPONS, x=1, y=0)
    weapons.max_power = 2
    ship.add_room(weapons)

    shields = Room("Shields", SystemType.SHIELDS, x=0, y=1)
    shields.max_power = 2
    ship.add_room(shields)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=1)
    engines.max_power = 2
    ship.add_room(engines)

    # Connections
    helm.connect_to(weapons)
    helm.connect_to(shields)
    weapons.connect_to(engines)
    shields.connect_to(engines)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Shields", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")

    # Power
    ship.allocate_power(SystemType.SHIELDS, 1)
    ship.allocate_power(SystemType.WEAPONS, 2)
    ship.allocate_power(SystemType.ENGINES, 1)

    # Shields
    ship.shields_max = 2
    ship.shields = 2

    # Crew
    pirate1 = Crew("Pirate Captain", "human")
    pirate1.skills.weapons = 1
    ship.add_crew_member(pirate1)
    pirate1.assign_to_room(helm)

    pirate2 = Crew("Pirate Gunner", "human")
    pirate2.skills.weapons = 1
    ship.add_crew_member(pirate2)
    pirate2.assign_to_room(weapons)

    # Weapons - start charged!
    laser = create_weapon("basic_laser")
    laser.charge = 1.0  # Ready to fire immediately
    ship.add_weapon(laser)

    # Medium speed
    ship.max_speed = 2.0
    ship.speed = 2.0

    return ship


def create_mantis_fighter() -> Ship:
    """
    Create a Mantis boarding ship (dangerous!).
    """
    ship = Ship("Mantis Fighter", "Mantis Ship")

    ship.hull_max = 20
    ship.hull = 20
    ship.reactor_power = 5
    ship.power_available = 5
    ship.scrap = 25

    # Simple layout
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    weapons = Room("Weapons", SystemType.WEAPONS, x=1, y=0)
    ship.add_room(weapons)

    teleporter = Room("Teleporter", SystemType.TELEPORTER, x=0, y=1)
    ship.add_room(teleporter)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=1)
    ship.add_room(engines)

    helm.connect_to(weapons)
    helm.connect_to(teleporter)
    weapons.connect_to(engines)
    teleporter.connect_to(engines)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Teleporter", SystemType.TELEPORTER), "Teleporter")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")

    ship.allocate_power(SystemType.WEAPONS, 2)
    ship.allocate_power(SystemType.ENGINES, 2)
    ship.allocate_power(SystemType.TELEPORTER, 1)

    ship.shields_max = 1
    ship.shields = 1

    # Strong boarding crew
    mantis1 = Crew("Mantis Warrior", "mantis")
    mantis1.skills.combat = 3
    mantis1.combat_damage = 20
    ship.add_crew_member(mantis1)
    mantis1.assign_to_room(teleporter)

    mantis2 = Crew("Mantis Fighter", "mantis")
    mantis2.skills.combat = 3
    mantis2.combat_damage = 20
    ship.add_crew_member(mantis2)
    mantis2.assign_to_room(weapons)

    # Weapons - start charged!
    laser = create_weapon("basic_laser")
    laser.charge = 1.0  # Ready to fire immediately
    ship.add_weapon(laser)

    # Very fast - aggressive pursuit
    ship.max_speed = 3.5
    ship.speed = 3.5

    return ship


def create_rebel_fighter() -> Ship:
    """
    Create a Rebel fighter (mid-game enemy).
    """
    ship = Ship("Rebel Fighter", "Rebel Ship")

    ship.hull_max = 25
    ship.hull = 25
    ship.reactor_power = 6
    ship.power_available = 6
    ship.scrap = 35

    # Rooms
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    shields = Room("Shields", SystemType.SHIELDS, x=1, y=0)
    shields.max_power = 3
    ship.add_room(shields)

    weapons = Room("Weapons", SystemType.WEAPONS, x=0, y=1)
    weapons.max_power = 3
    ship.add_room(weapons)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=1)
    engines.max_power = 3
    ship.add_room(engines)

    helm.connect_to(shields)
    helm.connect_to(weapons)
    shields.connect_to(engines)
    weapons.connect_to(engines)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Shields", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")

    ship.allocate_power(SystemType.SHIELDS, 2)
    ship.allocate_power(SystemType.WEAPONS, 2)
    ship.allocate_power(SystemType.ENGINES, 2)

    ship.shields_max = 3
    ship.shields = 3

    # Crew
    rebel1 = Crew("Rebel Officer", "human")
    rebel1.skills.weapons = 2
    ship.add_crew_member(rebel1)
    rebel1.assign_to_room(helm)

    rebel2 = Crew("Rebel Gunner", "human")
    rebel2.skills.weapons = 2
    ship.add_crew_member(rebel2)
    rebel2.assign_to_room(weapons)

    # Better weapons - start charged!
    burst = create_weapon("burst_laser_ii")
    burst.charge = 1.0  # Ready to fire immediately
    ship.add_weapon(burst)

    # Slower but powerful
    ship.max_speed = 1.5
    ship.speed = 1.5

    return ship


# Enemy ship catalog
ENEMY_SHIPS = {
    "gnat": create_gnat,
    "pirate_scout": create_pirate_scout,
    "mantis_fighter": create_mantis_fighter,
    "rebel_fighter": create_rebel_fighter,
}


def create_random_enemy(difficulty: int = 1) -> Ship:
    """
    Create a random enemy ship based on difficulty.
    difficulty: 0-3 (tutorial to hard)
    """
    if difficulty == 0:
        # Tutorial mode - always gnat
        return create_gnat()
    elif difficulty == 1:
        choices = ["pirate_scout"]
    elif difficulty == 2:
        choices = ["pirate_scout", "mantis_fighter"]
    else:
        choices = list(ENEMY_SHIPS.keys())

    enemy_type = random.choice(choices)
    return ENEMY_SHIPS[enemy_type]()

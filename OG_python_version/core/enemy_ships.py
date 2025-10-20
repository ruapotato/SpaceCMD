"""
spacecmd - Enemy Ship Templates

Factory functions for enemy ships.
Each enemy ship gets its own ShipOS instance running hostile AI scripts!
"""

from .ship import Ship, Room, Crew, SystemType, ShipSystem
from .weapons import create_weapon
from .ship_os import ShipOS
import random
import os
from typing import Optional


class EnemyShipWithOS:
    """
    Enemy ship with its own ShipOS instance running hostile AI.

    This represents an enemy computer - it has its own OS, filesystem,
    and runs hostile PooScript to control the ship.
    """

    def __init__(self, ship: Ship, ai_script_path: str = None):
        """
        Create enemy ship with OS.

        Args:
            ship: The ship hardware
            ai_script_path: Path to hostile AI script (default: enemy_ai.poo)
        """
        self.ship = ship

        # Create ShipOS for enemy (enemies are computers too!)
        self.ship_os = ShipOS(ship=ship, hostname=f"enemy-{ship.name.lower().replace(' ', '-')}")

        # Boot the OS (silently - enemies don't print boot messages)
        self.ship_os.boot(verbose=False)

        # Auto-login as root (enemies have root access to their own systems)
        self.ship_os.login('root', 'root')

        # Install hostile AI script
        if ai_script_path is None:
            # Use default enemy AI
            ai_script_path = os.path.join(os.path.dirname(__file__), 'resources', 'enemy_ai.poo')

        try:
            with open(ai_script_path, 'r') as f:
                ai_script = f.read()

            # Install AI script to /root/ai.poo
            self.ship_os.vfs.create_file('/root/ai.poo', 0o755, 1, 1, ai_script.encode('utf-8'), 1)  # Create as executable
        except FileNotFoundError:
            # Fallback: simple hardcoded AI
            pass

    def run_ai_turn(self):
        """
        Execute one turn of the enemy AI.
        Runs the /root/ai.poo script through PooScript interpreter.
        """
        # Execute the AI script
        exit_code, stdout, stderr = self.ship_os.execute_command('/root/ai.poo')

        # AI script sets pursuit decision in /tmp/ai_pursue
        # (Combat system will read this)
        return exit_code == 0

    def should_pursue(self) -> bool:
        """
        Check if enemy will pursue player if they flee.
        Reads decision from AI script output.
        """
        try:
            # AI writes '1' to pursue, '0' to let escape
            result = self.ship_os.vfs.read_file('/tmp/ai_pursue', 1)
            if result:
                return result.decode('utf-8').strip() == '1'
        except:
            pass

        # Default: pursue if in good shape
        return self.ship.hull > self.ship.hull_max * 0.5


def create_gnat() -> Ship:
    """
    Create a simple, strategic enemy ship.
    Clear subsystems for targeting practice!

    STRATEGIC TARGETS:
    - Weapons: Disable their offense
    - Engines: Prevent escape
    - Power Core: Reduce power availability
    - Shields: Break defenses (weak)
    """
    ship = Ship("Hostile Gnat", "Gnat-class Scout")

    # Balanced stats for strategic combat
    ship.hull_max = 20  # Increased hull so systems are the targets
    ship.hull = 20
    ship.reactor_power = 4
    ship.power_available = 4
    ship.dark_matter = 0
    ship.scrap = 10  # Reward

    # STRATEGIC LAYOUT: 4 clear targets
    # Row 1: Weapons and Shields
    weapons = Room("Weapons", SystemType.WEAPONS, x=0, y=0)
    weapons.max_power = 2
    ship.add_room(weapons)

    shields = Room("Shields", SystemType.SHIELDS, x=1, y=0)
    shields.max_power = 1  # Weak shields
    ship.add_room(shields)

    # Row 2: Engines and Power Core
    engines = Room("Engines", SystemType.ENGINES, x=0, y=1)
    engines.max_power = 2
    ship.add_room(engines)

    reactor = Room("Power Core", SystemType.REACTOR, x=1, y=1)
    reactor.max_power = 1
    ship.add_room(reactor)

    # Connect rooms
    weapons.connect_to(shields)
    weapons.connect_to(engines)
    shields.connect_to(reactor)
    engines.connect_to(reactor)

    # Add systems
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Shields", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Power Core", SystemType.REACTOR), "Power Core")

    # Power allocation
    ship.allocate_power(SystemType.WEAPONS, 2)
    ship.allocate_power(SystemType.SHIELDS, 1)
    ship.allocate_power(SystemType.ENGINES, 1)

    # Weak shields (1 layer)
    ship.shields_max = 1
    ship.shields = 1

    # ONE robot managing all systems (runs PooScript AI!)
    robot = Crew("Scout AI", "robot")
    robot.skills.weapons = 1
    robot.skills.engines = 1
    robot.health = 100
    ship.add_crew_member(robot)
    robot.assign_to_room(weapons)  # Start in weapons room

    # Basic weapon - START CHARGED
    laser = create_weapon("basic_laser")
    laser.damage = 3  # Moderate damage
    laser.cooldown = 8.0  # Decent firing rate
    laser.charge = 1.0  # START FULLY CHARGED!
    ship.add_weapon(laser)

    # Moderate speed
    ship.max_speed = 100.0
    ship.speed = 100.0

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

    # Simple layout - added reactor for proper ship function
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

    reactor = Room("Reactor", SystemType.REACTOR, x=2, y=0)
    reactor.max_power = 1
    ship.add_room(reactor)

    # Connections
    helm.connect_to(weapons)
    helm.connect_to(shields)
    weapons.connect_to(engines)
    weapons.connect_to(reactor)
    shields.connect_to(engines)
    engines.connect_to(reactor)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Shields", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Reactor", SystemType.REACTOR), "Reactor")

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

    # Simple layout - added reactor for proper ship function
    helm = Room("Helm", SystemType.HELM, x=0, y=0)
    ship.add_room(helm)

    weapons = Room("Weapons", SystemType.WEAPONS, x=1, y=0)
    ship.add_room(weapons)

    teleporter = Room("Teleporter", SystemType.TELEPORTER, x=0, y=1)
    ship.add_room(teleporter)

    engines = Room("Engines", SystemType.ENGINES, x=1, y=1)
    ship.add_room(engines)

    reactor = Room("Reactor", SystemType.REACTOR, x=2, y=0)
    reactor.max_power = 1
    ship.add_room(reactor)

    helm.connect_to(weapons)
    helm.connect_to(teleporter)
    weapons.connect_to(engines)
    weapons.connect_to(reactor)
    teleporter.connect_to(engines)
    engines.connect_to(reactor)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Teleporter", SystemType.TELEPORTER), "Teleporter")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Reactor", SystemType.REACTOR), "Reactor")

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

    # Rooms - added reactor for proper ship function
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

    reactor = Room("Reactor", SystemType.REACTOR, x=2, y=0)
    reactor.max_power = 1
    ship.add_room(reactor)

    helm.connect_to(shields)
    helm.connect_to(weapons)
    shields.connect_to(engines)
    shields.connect_to(reactor)
    weapons.connect_to(engines)
    engines.connect_to(reactor)

    # Systems
    ship.add_system(ShipSystem("Helm", SystemType.HELM), "Helm")
    ship.add_system(ShipSystem("Shields", SystemType.SHIELDS), "Shields")
    ship.add_system(ShipSystem("Weapons", SystemType.WEAPONS), "Weapons")
    ship.add_system(ShipSystem("Engines", SystemType.ENGINES), "Engines")
    ship.add_system(ShipSystem("Reactor", SystemType.REACTOR), "Reactor")

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


# Enemy ship catalog (returns raw Ship objects)
ENEMY_SHIPS = {
    "gnat": create_gnat,
    "pirate_scout": create_pirate_scout,
    "mantis_fighter": create_mantis_fighter,
    "rebel_fighter": create_rebel_fighter,
}


def create_enemy_with_os(enemy_type: str) -> EnemyShipWithOS:
    """
    Create an enemy ship with its own ShipOS running hostile AI.

    Args:
        enemy_type: Type of enemy ("gnat", "pirate_scout", etc.)

    Returns:
        EnemyShipWithOS instance (enemy computer running hostile script)
    """
    if enemy_type not in ENEMY_SHIPS:
        enemy_type = "gnat"  # Fallback

    # Create the ship hardware
    ship = ENEMY_SHIPS[enemy_type]()

    # Wrap it with OS and AI
    return EnemyShipWithOS(ship)


def create_random_enemy(difficulty: int = 1) -> Ship:
    """
    Create a random enemy ship based on difficulty (LEGACY - returns raw Ship).
    Use create_enemy_with_os() for new code!

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


def create_random_enemy_with_os(difficulty: int = 1) -> EnemyShipWithOS:
    """
    Create a random enemy with OS based on difficulty.

    Args:
        difficulty: 0-3 (tutorial to hard)

    Returns:
        EnemyShipWithOS instance (complete enemy computer)
    """
    if difficulty == 0:
        enemy_type = "gnat"
    elif difficulty == 1:
        choices = ["pirate_scout"]
        enemy_type = random.choice(choices)
    elif difficulty == 2:
        choices = ["pirate_scout", "mantis_fighter"]
        enemy_type = random.choice(choices)
    else:
        enemy_type = random.choice(list(ENEMY_SHIPS.keys()))

    return create_enemy_with_os(enemy_type)

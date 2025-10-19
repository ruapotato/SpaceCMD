"""
spacecmd - Ship and Room System

Core classes for ship structure, rooms, and systems.
Replaces the old VFS with a ship-based architecture.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
import json


class SystemType(Enum):
    """Types of ship systems"""
    HELM = "helm"
    SHIELDS = "shields"
    WEAPONS = "weapons"
    ENGINES = "engines"
    OXYGEN = "oxygen"
    REACTOR = "reactor"
    MEDBAY = "medbay"
    SENSORS = "sensors"
    DOORS = "doors"
    TELEPORTER = "teleporter"
    CLOAKING = "cloaking"
    DRONE_BAY = "drones"
    NONE = "none"  # Empty rooms or corridors


class RoomState(Enum):
    """State of a room"""
    NORMAL = "normal"
    DAMAGED = "damaged"
    CRITICAL = "critical"
    ON_FIRE = "on_fire"
    BREACHED = "breached"
    NO_OXYGEN = "no_oxygen"


class Room:
    """
    A room in the ship containing a system.
    Rooms can be connected, damaged, on fire, breached, etc.
    """

    def __init__(self, name: str, system_type: SystemType,
                 x: int, y: int, width: int = 1, height: int = 1):
        self.name = name
        self.system_type = system_type

        # Position and size in ship grid
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # System power and health
        self.power_allocated = 0
        self.max_power = 3  # Most systems can take up to 3 power
        self.health = 1.0  # 0.0 to 1.0

        # Room conditions
        self.oxygen_level = 1.0  # 0.0 to 1.0
        self.on_fire = False
        self.breached = False
        self.venting = False  # Doors open to space

        # Crew in this room
        self.crew: List['Crew'] = []

        # Connected rooms (for pathfinding and oxygen flow)
        self.connections: List['Room'] = []

        # System-specific data
        self.system_data = {}

    @property
    def state(self) -> RoomState:
        """Determine room state based on conditions"""
        if self.breached:
            return RoomState.BREACHED
        if self.on_fire:
            return RoomState.ON_FIRE
        if self.oxygen_level < 0.2:
            return RoomState.NO_OXYGEN
        if self.health < 0.3:
            return RoomState.CRITICAL
        if self.health < 0.7:
            return RoomState.DAMAGED
        return RoomState.NORMAL

    @property
    def is_functional(self) -> bool:
        """Can this room's system operate?"""
        return (self.health > 0.2 and  # Systems work until they're severely damaged (< 20%)
                self.power_allocated > 0 and
                not self.breached and
                len(self.crew) > 0)  # Need crew to operate most systems

    @property
    def crew_bonus(self) -> float:
        """
        Bonus from crew stationed in room.
        More skilled crew = better system performance
        """
        if not self.crew:
            return 0.0

        # Get highest skill for this system type
        skill_name = self.system_type.value
        max_skill = max([getattr(c.skills, skill_name, 0) for c in self.crew])

        # Each skill level gives 10% bonus
        return max_skill * 0.1

    def connect_to(self, room: 'Room'):
        """Connect this room to another (bidirectional)"""
        if room not in self.connections:
            self.connections.append(room)
        if self not in room.connections:
            room.connections.append(self)

    def take_damage(self, amount: float):
        """Deal damage to this room's system"""
        self.health = max(0.0, self.health - amount)

    def repair(self, amount: float):
        """Repair this room's system"""
        self.health = min(1.0, self.health + amount)

    def __repr__(self):
        return f"<Room {self.name} ({self.system_type.value}) HP:{self.health:.1%} PWR:{self.power_allocated}/{self.max_power}>"


class ShipSystem:
    """
    Base class for ship systems (weapons, shields, etc.)
    Systems are installed in rooms and provide functionality.
    """

    def __init__(self, name: str, system_type: SystemType):
        self.name = name
        self.system_type = system_type
        self.level = 1  # Upgrade level (1-3)
        self.room: Optional[Room] = None

    def update(self, dt: float):
        """Update system state each tick"""
        pass

    def is_online(self) -> bool:
        """Is this system functional?"""
        if not self.room:
            return False
        return self.room.is_functional

    def get_effectiveness(self) -> float:
        """
        How effective is this system? (0.0 to 1.0+)
        Affected by power, health, crew skill
        """
        if not self.is_online():
            return 0.0

        base = self.room.health
        crew_bonus = self.room.crew_bonus
        power_ratio = self.room.power_allocated / self.room.max_power

        return base * power_ratio * (1.0 + crew_bonus)


class Ship:
    """
    Main ship class containing rooms, systems, crew, and resources.
    This replaces the old VFS system.
    """

    def __init__(self, name: str, ship_class: str):
        self.name = name
        self.ship_class = ship_class

        # Ship resources
        self.hull_max = 30
        self.hull = 30
        self.fuel = 20
        self.missiles = 8
        self.drone_parts = 4
        self.scrap = 0

        # Power system
        self.reactor_power = 8
        self.power_available = 8

        # Ship layout
        self.rooms: Dict[str, Room] = {}
        self.systems: Dict[SystemType, ShipSystem] = {}
        self.crew: List['Crew'] = []
        self.weapons: List['Weapon'] = []  # Installed weapons

        # Combat state
        self.shields = 0
        self.shields_max = 0
        self.evasion = 0

        # Ship template (ASCII art)
        self.template = None

    def add_room(self, room: Room):
        """Add a room to the ship"""
        self.rooms[room.name] = room

        # Register system
        if room.system_type != SystemType.NONE:
            # System will be added separately
            pass

    def add_system(self, system: ShipSystem, room_name: str):
        """Install a system in a room"""
        if room_name not in self.rooms:
            raise ValueError(f"Room {room_name} not found")

        room = self.rooms[room_name]
        system.room = room
        self.systems[system.system_type] = system

    def add_crew_member(self, crew: 'Crew'):
        """Add a crew member to the ship"""
        self.crew.append(crew)
        crew.ship = self

    def add_weapon(self, weapon: 'Weapon'):
        """Add a weapon to the ship"""
        self.weapons.append(weapon)

    def allocate_power(self, system_type: SystemType, power: int):
        """Allocate power to a system"""
        if system_type not in self.systems:
            return False

        system = self.systems[system_type]
        room = system.room

        # Check if we have enough power
        current_power = room.power_allocated
        power_needed = power - current_power

        if power_needed > self.power_available:
            return False

        # Allocate
        room.power_allocated = min(power, room.max_power)
        self.power_available -= power_needed

        return True

    def deallocate_power(self, system_type: SystemType):
        """Remove power from a system"""
        if system_type not in self.systems:
            return False

        system = self.systems[system_type]
        room = system.room

        self.power_available += room.power_allocated
        room.power_allocated = 0

        return True

    def take_damage(self, damage: int, target_room: Optional[str] = None):
        """
        Take hull damage. Optionally target a specific room.
        """
        if self.shields > 0:
            # Shields absorb damage
            absorbed = min(damage, self.shields)
            self.shields -= absorbed
            damage -= absorbed

        if damage > 0:
            self.hull -= damage

            # Apply damage to targeted room
            if target_room and target_room in self.rooms:
                room = self.rooms[target_room]
                room.take_damage(0.2 * damage)  # System damage

    def update(self, dt: float):
        """
        Update ship state each game tick.
        - Update all systems
        - Update weapons
        - Update oxygen levels
        - Handle fires
        - Check crew status
        - Autonomous crew actions (repair, fight fires, etc.)
        """
        # Update all systems
        for system in self.systems.values():
            system.update(dt)

        # Update weapons
        weapons_powered = SystemType.WEAPONS in self.systems and self.systems[SystemType.WEAPONS].is_online()
        for weapon in self.weapons:
            weapon.update(dt, weapons_powered)

        # Autonomous crew actions (AI bots manage themselves!)
        self._update_crew_ai(dt)

        # Update oxygen (spreads between connected rooms)
        self._update_oxygen(dt)

        # Update fires
        self._update_fires(dt)

        # Update shields (regenerate)
        if SystemType.SHIELDS in self.systems:
            shields_system = self.systems[SystemType.SHIELDS]
            if shields_system.is_online():
                # Shields recharge when not taking damage
                self.shields = min(self.shields_max,
                                   self.shields + dt * shields_system.get_effectiveness())

    def _update_crew_ai(self, dt: float):
        """
        Autonomous crew AI - bots manage ship automatically!
        Priority:
        1. Fight fires (critical)
        2. Repair damaged systems
        3. Heal in medbay if injured
        4. Operate their assigned system
        """
        for crew in self.crew:
            if not crew.is_alive or not crew.room:
                continue

            # Priority 1: Fight fires
            if crew.room.on_fire:
                # Fighting fire (put it out over time)
                import random
                if random.random() < dt * 0.3:  # 30% chance per second to extinguish
                    crew.room.on_fire = False
                continue

            # Priority 2: Repair damaged systems
            if crew.room.health < 1.0:
                crew.repair_system(dt * 3.0)  # 3x faster repair for bots!
                continue

            # Priority 3: Heal in medbay if injured
            if crew.health < crew.health_max * 0.8:  # Below 80% health
                # Try to go to medbay
                medbay_room = None
                for room in self.rooms.values():
                    if room.system_type == SystemType.MEDBAY and room.is_functional:
                        medbay_room = room
                        break

                if medbay_room and crew.room == medbay_room:
                    # Heal in medbay (it repairs bots!)
                    heal_rate = 10.0  # 10 HP per second
                    crew.heal(dt * heal_rate)

            # Priority 4: Just operate their system (already in room)
            # Crew just being present in room provides bonuses

    def _update_oxygen(self, dt: float):
        """Update oxygen levels in all rooms"""
        if SystemType.OXYGEN not in self.systems:
            return

        o2_system = self.systems[SystemType.OXYGEN]

        for room in self.rooms.values():
            # Breached rooms lose oxygen
            if room.breached or room.venting:
                room.oxygen_level = max(0.0, room.oxygen_level - dt * 0.5)

            # O2 system replenishes oxygen
            elif o2_system.is_online():
                room.oxygen_level = min(1.0, room.oxygen_level + dt * 0.2 * o2_system.get_effectiveness())

            # Crew consume oxygen
            if room.crew:
                consumption = len(room.crew) * dt * 0.05
                room.oxygen_level = max(0.0, room.oxygen_level - consumption)

            # Damage crew in low oxygen
            if room.oxygen_level < 0.3:
                for crew in room.crew:
                    crew.take_damage(dt * 0.1)

    def _update_fires(self, dt: float):
        """Update fire spread and damage"""
        for room in self.rooms.values():
            if room.on_fire:
                # Fire damages room and crew
                room.take_damage(dt * 0.05)

                for crew in room.crew:
                    crew.take_damage(dt * 0.2)

                # Fire consumes oxygen
                room.oxygen_level = max(0.0, room.oxygen_level - dt * 0.3)

                # Fire spreads to connected rooms (small chance)
                if room.oxygen_level > 0.2:  # Needs oxygen to spread
                    for connected in room.connections:
                        if not connected.on_fire and connected.oxygen_level > 0.5:
                            # 1% chance per second to spread
                            import random
                            if random.random() < dt * 0.01:
                                connected.on_fire = True

                # Fire dies in vacuum
                if room.oxygen_level < 0.1:
                    room.on_fire = False

    def get_power_usage(self) -> Dict[str, int]:
        """Get current power allocation by system"""
        usage = {}
        for name, room in self.rooms.items():
            if room.power_allocated > 0:
                usage[name] = room.power_allocated
        return usage

    def to_dict(self) -> dict:
        """Serialize ship to dict for saving"""
        return {
            'name': self.name,
            'ship_class': self.ship_class,
            'hull': self.hull,
            'hull_max': self.hull_max,
            'fuel': self.fuel,
            'missiles': self.missiles,
            'scrap': self.scrap,
            'reactor_power': self.reactor_power,
            'rooms': {name: {
                'health': room.health,
                'power': room.power_allocated,
                'oxygen': room.oxygen_level,
                'on_fire': room.on_fire,
                'breached': room.breached,
            } for name, room in self.rooms.items()},
        }

    @classmethod
    def from_template(cls, template_name: str) -> 'Ship':
        """Create a ship from a template file"""
        # This will load from data/ships/{template_name}.json
        # For now, we'll create ships programmatically
        raise NotImplementedError("Ship templates not yet implemented")

    def __repr__(self):
        return f"<Ship '{self.name}' ({self.ship_class}) Hull:{self.hull}/{self.hull_max}>"


class Crew:
    """
    Crew member with skills, health, and position.
    Replaces the old process system.
    """

    def __init__(self, name: str, race: str = "human"):
        self.name = name
        self.race = race

        # Position
        self.ship: Optional[Ship] = None
        self.room: Optional[Room] = None

        # Stats
        self.health_max = 100
        self.health = 100

        # Skills (0-5 levels, each level gives bonus)
        self.skills = CrewSkills()

        # Experience
        self.experience = 0

        # Combat
        self.combat_damage = 10
        self.is_fighting = False

    def assign_to_room(self, room: Room):
        """Move crew member to a room"""
        if self.room:
            self.room.crew.remove(self)

        self.room = room
        room.crew.append(self)

    def take_damage(self, amount: float):
        """Take damage"""
        self.health = max(0, self.health - amount)

    def heal(self, amount: float):
        """Heal crew member"""
        self.health = min(self.health_max, self.health + amount)

    def repair_system(self, dt: float):
        """Repair the system in current room"""
        if not self.room or self.room.health >= 1.0:
            return

        # Repair speed based on skill (bots repair fast!)
        repair_skill = self.skills.repair
        repair_rate = 0.2 * (1 + repair_skill * 0.5)  # Base 20% per second (2x faster than before)

        self.room.repair(dt * repair_rate)

        # Gain experience
        self.gain_experience(dt * 0.5)

    def gain_experience(self, amount: float):
        """Gain experience and potentially level up"""
        self.experience += amount
        # TODO: Implement skill leveling

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def __repr__(self):
        return f"<Crew {self.name} ({self.race}) HP:{self.health}/{self.health_max}>"


class CrewSkills:
    """Crew member skills"""

    def __init__(self):
        self.helm = 0      # Piloting skill (improves evasion)
        self.weapons = 0   # Weapon skill (faster charge, better aim)
        self.shields = 0   # Shield skill (better shield strength)
        self.engines = 0   # Engine skill (better evasion, faster FTL)
        self.repair = 0    # Repair skill (faster repairs)
        self.combat = 0    # Combat skill (better at fighting boarders)

    def __repr__(self):
        return f"<Skills pilot:{self.helm} wpn:{self.weapons} shd:{self.shields} eng:{self.engines} rep:{self.repair} cbt:{self.combat}>"

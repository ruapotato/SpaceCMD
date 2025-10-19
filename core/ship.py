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
    REACTOR = "reactor"
    REPAIR_BAY = "repair_bay"
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
        self.on_fire = False
        self.breached = False
        self.venting = False  # Doors open to space

        # Crew in this room
        self.crew: List['Crew'] = []

        # Connected rooms (for pathfinding)
        self.connections: List['Room'] = []

        # System-specific data
        self.system_data = {}

        # Reference to parent ship (set when added to ship)
        self.ship: Optional['Ship'] = None

    @property
    def state(self) -> RoomState:
        """Determine room state based on conditions"""
        if self.breached:
            return RoomState.BREACHED
        if self.on_fire:
            return RoomState.ON_FIRE
        if self.health < 0.3:
            return RoomState.CRITICAL
        if self.health < 0.7:
            return RoomState.DAMAGED
        return RoomState.NORMAL

    @property
    def is_functional(self) -> bool:
        """
        Can this room's system operate?

        CRITICAL OS-LEVEL CHECK:
        - Systems need power allocated
        - Ship must have enough TOTAL power from reactor
        - If reactor damaged: available power drops, systems fail!
        """
        if self.health <= 0.2:  # Systems work until severely damaged (< 20%)
            return False
        if self.breached:  # Breached systems don't work
            return False
        if self.power_allocated <= 0:  # Need power
            return False

        # CRITICAL: Check if ship has enough power from reactor!
        # If reactor is damaged, total power drops, systems start failing
        if self.ship:
            total_power_needed = sum(r.power_allocated for r in self.ship.rooms.values())
            available_power = self.ship.get_available_power()

            # If ship is over-budget on power, systems fail!
            # Higher priority systems (lower in list) fail first
            if total_power_needed > available_power:
                # Calculate power deficit
                power_deficit = total_power_needed - available_power

                # This system only works if we haven't exceeded budget
                # Systems fail in priority order (weapons/engines fail first when reactor damaged)
                accumulated_power = 0
                for room_name, room in self.ship.rooms.items():
                    accumulated_power += room.power_allocated
                    if room == self:
                        # This is our room - check if we're within budget
                        return accumulated_power <= available_power

        return True

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
        """
        Deal damage to this room's system.
        Crew/robots in the room also take damage!
        """
        self.health = max(0.0, self.health - amount)

        # CREW/ROBOTS TAKE DAMAGE when room is damaged!
        # Each point of system damage = 5 HP damage to crew
        crew_damage = amount * 5.0
        for crew in self.crew:
            crew.take_damage(crew_damage)

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
        Affected by power, health, and crew.

        CREW BONUSES (what each system does with crew):
        - SHIELDS: Crew → Faster shield recharge (10% per skill level)
        - WEAPONS: Crew → Faster weapon charge (10% per skill level)
        - ENGINES: Crew → Faster ship speed (10% per skill level)
        - REACTOR: Crew → +1 power per crew member (see get_available_power())
        - REPAIR_BAY: Crew → Faster repair/healing (effectiveness affects repair rate)
        - HELM: Crew → Better evasion (effectiveness affects dodge chance)

        Base formula:
        - Without crew: 25% base effectiveness (automated systems)
        - With 1+ crew: 100% effectiveness + crew bonuses
        - Crew skills provide additional bonuses (10% per skill level)
        """
        if not self.is_online():
            return 0.0

        health_factor = self.room.health
        power_ratio = self.room.power_allocated / self.room.max_power

        # Base effectiveness without crew (automated systems at 25%)
        if not self.room.crew:
            # Low base rate: 25% effectiveness without crew
            return health_factor * power_ratio * 0.25

        # With crew: full effectiveness + bonuses
        crew_bonus = self.room.crew_bonus
        return health_factor * power_ratio * (1.0 + crew_bonus)


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
        self.dark_matter = 20  # Fuel for FTL jumps
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

        # Galaxy position and movement (1D linear galaxy)
        self.galaxy_position = 800.0  # Current position (distance from center, 0 = center)
        self.velocity = 0.0  # Current velocity (positive = away from center, negative = toward center)
        self.target_position = None  # Target position to travel to (None = not traveling)
        self.is_traveling = False  # Whether actively traveling
        self.base_speed = 0.8  # Base travel speed without engines (units per second) - 20 min to cross galaxy
        self.max_speed = 1.5  # Maximum travel speed with engines+crew (units per second) - 11 min to cross galaxy
        # With engines but NO crew (25% effectiveness): 0.975 u/s - 17 min to cross galaxy
        # CREW IN ENGINES IS CRITICAL for fast travel!

        # Legacy compatibility (remove eventually)
        self.galaxy_distance_from_center = self.galaxy_position  # Deprecated
        self.speed = 1.0  # Deprecated

        # Ship template (ASCII art)
        self.template = None

    def add_room(self, room: Room):
        """Add a room to the ship"""
        self.rooms[room.name] = room
        room.ship = self  # Give room reference to ship

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

    def get_available_power(self) -> int:
        """
        Get available power considering reactor health and crew bonus.

        CRITICAL MECHANIC: Reactor damage reduces power output!
        - 100% health = 100% power
        - 50% health = 50% power
        - Damaged reactor disables weapons and engines!

        Returns:
            Total available power (base * reactor_health + crew bonus)
        """
        base_power = self.reactor_power

        # REACTOR DAMAGE REDUCES POWER OUTPUT (OS-level mechanic!)
        if SystemType.REACTOR in self.systems:
            reactor_system = self.systems[SystemType.REACTOR]
            if reactor_system.room:
                # Reactor health directly affects power output
                reactor_health = reactor_system.room.health
                base_power = int(base_power * reactor_health)

                # Reactor crew bonus: +1 power per crew member in reactor room
                if reactor_system.room.crew:
                    crew_count = len(reactor_system.room.crew)
                    base_power += crew_count  # Each crew adds 1 power!

        return base_power

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

    def get_current_speed(self) -> float:
        """
        Calculate current ship speed based on engine effectiveness.
        More power + more crew in engines = faster!

        Returns:
            Current speed in units per second
        """
        # Base speed without engines
        speed = self.base_speed

        # Engines boost speed significantly
        if SystemType.ENGINES in self.systems:
            engine_system = self.systems[SystemType.ENGINES]
            engine_effectiveness = engine_system.get_effectiveness()

            # Engines can double speed when fully powered and crewed
            # 0% effectiveness = base_speed (50)
            # 100% effectiveness = max_speed (200)
            speed_boost = engine_effectiveness * (self.max_speed - self.base_speed)
            speed += speed_boost

        return speed

    def set_course(self, target_position: float):
        """
        Set course to a target position.
        Ship will travel toward this position until it arrives.

        Args:
            target_position: Target position in galaxy
        """
        self.target_position = target_position
        self.is_traveling = True

        # Calculate current speed (depends on engines!)
        current_speed = self.get_current_speed()

        # Set velocity based on direction
        if target_position < self.galaxy_position:
            # Traveling toward center (negative velocity)
            self.velocity = -current_speed
        else:
            # Traveling away from center (positive velocity)
            self.velocity = current_speed

    def stop_traveling(self):
        """Stop traveling (emergency stop or arrival)"""
        self.is_traveling = False
        self.velocity = 0.0
        self.target_position = None

    def update_position(self, dt: float):
        """
        Update ship's position based on velocity.
        Called every frame to handle continuous movement.

        Args:
            dt: Delta time in seconds
        """
        if not self.is_traveling or self.target_position is None:
            return

        # Move ship
        distance_to_move = self.velocity * dt
        new_position = self.galaxy_position + distance_to_move

        # Check if we've arrived at target
        if self.velocity > 0:  # Moving away from center
            if new_position >= self.target_position:
                # Arrived!
                self.galaxy_position = self.target_position
                self.stop_traveling()
                return
        else:  # Moving toward center
            if new_position <= self.target_position:
                # Arrived!
                self.galaxy_position = self.target_position
                self.stop_traveling()
                return

        # Continue moving
        self.galaxy_position = new_position

        # Update legacy field
        self.galaxy_distance_from_center = self.galaxy_position

    def update(self, dt: float):
        """
        Update ship state each game tick.
        - Update position (continuous movement)
        - Update all systems
        - Update weapons
        - Update oxygen levels
        - Handle fires
        - Check crew status
        - Autonomous crew actions (repair, fight fires, etc.)
        """
        # Update position (continuous galaxy travel)
        self.update_position(dt)

        # Update all systems
        for system in self.systems.values():
            system.update(dt)

        # Update weapons
        weapons_powered = SystemType.WEAPONS in self.systems and self.systems[SystemType.WEAPONS].is_online()
        for weapon in self.weapons:
            weapon.update(dt, weapons_powered)

        # Autonomous crew actions (AI bots manage themselves!)
        self._update_crew_ai(dt)

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
                # Very slow repairs - 1/100th of base rate (much more realistic)
                crew.repair_system(dt * 0.01)
                continue

            # Priority 3: Heal in repair bay if injured
            if crew.health < crew.health_max * 0.8:  # Below 80% health
                # Try to go to repair bay
                repair_bay_room = None
                for room in self.rooms.values():
                    if room.system_type == SystemType.REPAIR_BAY and room.is_functional:
                        repair_bay_room = room
                        break

                if repair_bay_room and crew.room == repair_bay_room:
                    # Heal in repair bay (it repairs bots!)
                    heal_rate = 10.0  # 10 HP per second
                    crew.heal(dt * heal_rate)

            # Priority 4: Just operate their system (already in room)
            # Crew just being present in room provides bonuses


    def _update_fires(self, dt: float):
        """Update fire spread and damage"""
        for room in self.rooms.values():
            if room.on_fire:
                # Fire damages room and crew
                room.take_damage(dt * 0.05)

                for crew in room.crew:
                    crew.take_damage(dt * 0.2)

                # Fire spreads to connected rooms (small chance)
                for connected in room.connections:
                    if not connected.on_fire:
                        # 1% chance per second to spread
                        import random
                        if random.random() < dt * 0.01:
                            connected.on_fire = True

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
            'dark_matter': self.dark_matter,
            'missiles': self.missiles,
            'scrap': self.scrap,
            'reactor_power': self.reactor_power,
            'rooms': {name: {
                'health': room.health,
                'power': room.power_allocated,
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
        """
        Repair the system in current room.

        IMPORTANT: Robots repair SLOWER than humans!
        - Humans: Fast repairs (100% rate)
        - Robots: Slow repairs (50% rate)
        """
        if not self.room or self.room.health >= 1.0:
            return

        # Base repair rate
        repair_skill = self.skills.repair
        repair_rate = 0.2 * (1 + repair_skill * 0.5)  # Base 20% per second

        # ROBOTS REPAIR SLOWER (50% rate)
        if self.race == "robot":
            repair_rate *= 0.5

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

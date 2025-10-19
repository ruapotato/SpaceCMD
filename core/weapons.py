"""
spacecmd - Weapons System

Weapon types, firing mechanics, and damage calculation.
"""

from typing import Optional, List
from enum import Enum
import random


class WeaponType(Enum):
    """Types of weapons"""
    LASER = "laser"
    BURST_LASER = "burst_laser"
    HEAVY_LASER = "heavy_laser"
    MISSILE = "missile"
    ION = "ion"
    BEAM = "beam"
    BOMB = "bomb"


class Weapon:
    """
    A weapon installed on a ship.
    """

    def __init__(self, name: str, weapon_type: WeaponType):
        self.name = name
        self.weapon_type = weapon_type

        # Weapon stats (set based on type)
        self.power_required = 1
        self.cooldown_time = 10.0  # seconds
        self.charge = 0.0  # 0.0 to 1.0
        self.damage = 1
        self.shots = 1  # Burst lasers fire multiple shots
        self.pierce = 0  # Shields pierced
        self.requires_missiles = False

        self._setup_weapon_stats()

    def _setup_weapon_stats(self):
        """Configure stats based on weapon type"""
        if self.weapon_type == WeaponType.LASER:
            self.power_required = 1
            self.cooldown_time = 10.0
            self.damage = 1
            self.shots = 1

        elif self.weapon_type == WeaponType.BURST_LASER:
            self.power_required = 2
            self.cooldown_time = 12.0
            self.damage = 1
            self.shots = 3  # Fires 3 shots!

        elif self.weapon_type == WeaponType.HEAVY_LASER:
            self.power_required = 1
            self.cooldown_time = 9.0
            self.damage = 2
            self.shots = 1

        elif self.weapon_type == WeaponType.MISSILE:
            self.power_required = 1
            self.cooldown_time = 11.0
            self.damage = 3
            self.shots = 1
            self.pierce = 999  # Missiles bypass shields
            self.requires_missiles = True

        elif self.weapon_type == WeaponType.ION:
            self.power_required = 1
            self.cooldown_time = 8.0
            self.damage = 0
            self.shots = 1
            self.ion_damage = 1  # Removes 1 shield layer

        elif self.weapon_type == WeaponType.BEAM:
            self.power_required = 2
            self.cooldown_time = 20.0
            self.damage = 2
            self.shots = 1
            self.beam_length = 3  # Hits multiple rooms

        elif self.weapon_type == WeaponType.BOMB:
            self.power_required = 1
            self.cooldown_time = 15.0
            self.damage = 3
            self.shots = 1
            self.pierce = 999  # Bombs teleport through shields
            self.requires_missiles = True

    def update(self, dt: float, powered: bool):
        """Update weapon charging"""
        if powered and self.charge < 1.0:
            # Charge faster with more weapon skill (handled externally)
            self.charge = min(1.0, self.charge + dt / self.cooldown_time)

    def is_ready(self) -> bool:
        """Can this weapon fire?"""
        return self.charge >= 1.0

    def fire(self) -> bool:
        """
        Fire the weapon.
        Returns True if successful.
        """
        if not self.is_ready():
            return False

        self.charge = 0.0
        return True

    def __repr__(self):
        return f"<Weapon {self.name} ({self.weapon_type.value}) Charge:{self.charge:.0%}>"


# Weapon catalog
WEAPON_CATALOG = {
    "basic_laser": {
        "name": "Basic Laser",
        "type": WeaponType.LASER,
        "cost": 20,
    },
    "burst_laser_ii": {
        "name": "Burst Laser II",
        "type": WeaponType.BURST_LASER,
        "cost": 50,
    },
    "heavy_laser_i": {
        "name": "Heavy Laser I",
        "type": WeaponType.HEAVY_LASER,
        "cost": 40,
    },
    "artemis_missile": {
        "name": "Artemis Missile",
        "type": WeaponType.MISSILE,
        "cost": 30,
    },
    "ion_blast": {
        "name": "Ion Blast",
        "type": WeaponType.ION,
        "cost": 25,
    },
    "pike_beam": {
        "name": "Pike Beam",
        "type": WeaponType.BEAM,
        "cost": 55,
    },
}


def create_weapon(weapon_id: str) -> Optional[Weapon]:
    """Create a weapon from catalog"""
    if weapon_id not in WEAPON_CATALOG:
        return None

    data = WEAPON_CATALOG[weapon_id]
    weapon = Weapon(data["name"], data["type"])
    return weapon

"""
spacecmd - Combat Engine

Turn-based combat system for ship-to-ship battles.
"""

from typing import Optional, List
from .ship import Ship, Room, SystemType
from .weapons import Weapon
import random

# Import sound effects (optional - will work without sounds)
try:
    from core.audio.sound_fx import play_sound
    SOUNDS_ENABLED = True
except:
    SOUNDS_ENABLED = False
    def play_sound(name, volume=1.0):
        pass


class CombatState:
    """
    Manages combat between two ships.
    """

    def __init__(self, player_ship: Ship, enemy_ship: Ship):
        self.player_ship = player_ship
        self.enemy_ship = enemy_ship

        self.active = True
        self.turn = 0
        self.player_target = None  # Which enemy system to target
        self.enemy_target = None  # Which player system enemy targets

        # Combat distance (units between ships)
        self.combat_distance = 5.0  # Start at medium range
        self.min_distance = 0.5
        self.max_distance = 10.0

        # Combat log
        self.log: List[str] = []

    def log_event(self, message: str):
        """Add message to combat log"""
        self.log.append(f"[T{self.turn}] {message}")
        if len(self.log) > 20:
            self.log.pop(0)

    def update(self, dt: float):
        """
        Update combat state.
        - Update weapon charging
        - Auto-fire enemy weapons
        - Check victory/defeat conditions
        """
        if not self.active:
            return

        # Update both ships
        self.player_ship.update(dt)
        self.enemy_ship.update(dt)

        # Enemy AI
        self._enemy_ai(dt)

        # Check end conditions
        if self.player_ship.hull <= 0:
            self.active = False
            self.log_event("💀 YOUR SHIP HAS BEEN DESTROYED!")
            play_sound("explosion", 1.0)

        if self.enemy_ship.hull <= 0:
            self.active = False
            self.log_event("✓ Enemy ship destroyed!")
            play_sound("explosion", 0.8)

    def _enemy_ai(self, dt: float):
        """Simple enemy AI"""
        # Pick a random target if we don't have one
        if not self.enemy_target and self.player_ship.rooms:
            targets = [r for r in self.player_ship.rooms.values()
                      if r.system_type != SystemType.NONE]
            if targets:
                self.enemy_target = random.choice(targets).name

        # Enemy movement AI: Use speed to pursue or maintain range
        if self.enemy_ship.weapons:
            # Find weapon with shortest range
            min_weapon_range = min(w.range for w in self.enemy_ship.weapons)

            # Calculate speed differential (negative = enemy is faster)
            speed_diff = self.player_ship.speed - self.enemy_ship.speed

            # If we're too far, move closer
            if self.combat_distance > min_weapon_range * 0.9:
                # Enemy tries to close distance using speed advantage
                # Faster ships close distance automatically
                enemy_advance_rate = self.enemy_ship.speed * dt
                player_retreat_rate = self.player_ship.speed * dt * 0.3  # Player can partially counter

                net_closing = enemy_advance_rate - player_retreat_rate

                if net_closing > 0:
                    old_dist = self.combat_distance
                    self.combat_distance = max(self.min_distance, self.combat_distance - net_closing)
                    if old_dist != self.combat_distance and abs(old_dist - self.combat_distance) > 0.1:
                        self.log_event(f"Enemy pursuing: {old_dist:.1f} → {self.combat_distance:.1f} units")

            # If player is trying to escape and is faster, they can pull away
            elif speed_diff > 0.5:
                # Player is significantly faster - can create distance
                escape_rate = speed_diff * dt * 0.5
                if random.random() < 0.3:  # 30% chance per update to escape slightly
                    old_dist = self.combat_distance
                    self.combat_distance = min(self.max_distance, self.combat_distance + escape_rate)
                    if old_dist != self.combat_distance and abs(old_dist - self.combat_distance) > 0.1:
                        self.log_event(f"Outmaneuvering enemy: {old_dist:.1f} → {self.combat_distance:.1f} units")

        # Fire enemy weapons when ready
        for weapon in self.enemy_ship.weapons:
            if weapon.is_ready():
                # Only try to fire if in range
                if self.combat_distance <= weapon.range:
                    self._fire_weapon(self.enemy_ship, self.player_ship, weapon, self.enemy_target)

    def fire_player_weapon(self, weapon_index: int) -> bool:
        """
        Player fires a weapon at the targeted enemy system.
        Returns True if successful.
        """
        if weapon_index >= len(self.player_ship.weapons):
            return False

        weapon = self.player_ship.weapons[weapon_index]
        return self._fire_weapon(self.player_ship, self.enemy_ship, weapon, self.player_target)

    def move_closer(self) -> bool:
        """
        Player ship attempts to move closer to enemy.
        Returns True if successful.
        """
        if self.combat_distance <= self.min_distance:
            return False

        # Move 1 unit closer
        old_distance = self.combat_distance
        self.combat_distance = max(self.min_distance, self.combat_distance - 1.0)
        self.log_event(f"Moving closer: {old_distance:.1f} → {self.combat_distance:.1f} units")
        return True

    def move_away(self) -> bool:
        """
        Player ship attempts to move away from enemy.
        Returns True if successful.
        """
        if self.combat_distance >= self.max_distance:
            return False

        # Move 1 unit away
        old_distance = self.combat_distance
        self.combat_distance = min(self.max_distance, self.combat_distance + 1.0)
        self.log_event(f"Moving away: {old_distance:.1f} → {self.combat_distance:.1f} units")
        return True

    def _fire_weapon(self, attacker: Ship, defender: Ship, weapon: Weapon, target_room_name: Optional[str]) -> bool:
        """
        Fire a weapon from attacker at defender.
        """
        if not weapon.fire():
            return False

        # Check range
        if self.combat_distance > weapon.range:
            attacker_name = "You" if attacker == self.player_ship else attacker.name
            self.log_event(f"{attacker_name}: {weapon.name} out of range! ({self.combat_distance:.1f}/{weapon.range:.1f})")
            # Still consume the charge
            return False

        # Check missiles
        if weapon.requires_missiles:
            if attacker.missiles <= 0:
                self.log_event(f"{attacker.name}: No missiles!")
                return False
            attacker.missiles -= 1

        attacker_name = "You" if attacker == self.player_ship else attacker.name

        # Play weapon fire sound
        weapon_sound = "laser_fire"  # Default
        if hasattr(weapon, 'weapon_type'):
            weapon_type_str = weapon.weapon_type.value  # Get enum value as string
            if "missile" in weapon_type_str:
                weapon_sound = "missile_fire"
            elif "beam" in weapon_type_str:
                weapon_sound = "beam_fire"
        play_sound(weapon_sound, 0.5)

        # Calculate damage
        total_damage = weapon.damage * weapon.shots

        # Apply to shields first (unless weapon pierces)
        if weapon.pierce < defender.shields:
            shield_damage = min(total_damage, defender.shields)
            defender.shields -= shield_damage
            total_damage -= shield_damage

            self.log_event(f"{attacker_name} fired {weapon.name}!")
            if shield_damage > 0:
                self.log_event(f"  🛡️  Enemy shields absorbed {int(shield_damage)} damage")
                # Shield hit sound
                play_sound("shield_hit", 0.6)

        # Remaining damage hits hull and systems
        if total_damage > 0:
            defender.hull -= total_damage
            self.log_event(f"  💥 {int(total_damage)} hull damage!")
            # Hull hit sound
            play_sound("hull_hit", 0.7)

            # Damage specific system if targeted
            if target_room_name and target_room_name in defender.rooms:
                room = defender.rooms[target_room_name]
                system_damage = total_damage * 0.03  # Only 3% of hull damage goes to system (much less fragile)
                room.take_damage(system_damage)

                # Only log if significant damage
                if room.health < 0.7:
                    self.log_event(f"  ⚠️  {room.name} damaged! ({room.health:.0%})")
                    play_sound("system_damage", 0.5)

                # Much lower chance of fire (only 5%)
                if random.random() < 0.05:
                    room.on_fire = True
                    self.log_event(f"  🔥 Fire in {room.name}!")
                    play_sound("alarm", 0.4)

                # Very low chance of breach (only 2% and needs big damage)
                if random.random() < 0.02 and total_damage >= 5:
                    room.breached = True
                    self.log_event(f"  💨 {room.name} breached!")
                    play_sound("alarm", 0.5)

        return True

    def set_target(self, room_name: str) -> bool:
        """Set player weapon target"""
        if room_name in self.enemy_ship.rooms:
            self.player_target = room_name
            return True
        return False

    def get_player_weapons(self) -> List[Weapon]:
        """Get player's weapons"""
        return self.player_ship.weapons

    def get_enemy_info(self) -> dict:
        """Get visible enemy ship info"""
        return {
            'name': self.enemy_ship.name,
            'hull': self.enemy_ship.hull,
            'hull_max': self.enemy_ship.hull_max,
            'shields': int(self.enemy_ship.shields),
            'shields_max': self.enemy_ship.shields_max,
        }

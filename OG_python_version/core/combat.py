"""
spacecmd - Combat Engine

Turn-based combat system for ship-to-ship battles.
Now with HACKING - network-based combat!
"""

from typing import Optional, List
from .ship import Ship, Room, SystemType
from .weapons import Weapon
from .hacking import HackingSystem, ExploitType, MalwareType
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
    Now includes actual galaxy positions and fleet mechanics.
    """

    def __init__(self, player_ship: Ship, enemy_ship: Ship):
        self.player_ship = player_ship
        self.enemy_ship = enemy_ship

        self.active = True
        self.turn = 0
        self.player_target = None  # Which enemy system to target
        self.enemy_target = None  # Which player system enemy targets

        # Combat distance (relative distance between ships during engagement)
        self.combat_distance = 5.0  # Start at medium range
        self.min_distance = 0.5
        self.max_distance = 10.0

        # Combat log - MUST INITIALIZE FIRST!
        self.log: List[str] = []

        # HACKING SYSTEM - Network-based combat!
        self.hacking = HackingSystem()
        self.player_has_root_access = False  # Did player hack into enemy?
        self.enemy_has_root_access = False   # Did enemy hack into player?

        # Galaxy positions (actual positions in galaxy)
        # Enemy spawns at a distance, player can warp away to escape
        self.player_galaxy_position = player_ship.galaxy_position
        self.enemy_galaxy_position = enemy_ship.galaxy_position if hasattr(enemy_ship, 'galaxy_position') else player_ship.galaxy_position

        # Distance-based engagement
        initial_distance = abs(self.player_galaxy_position - self.enemy_galaxy_position)
        self.sensor_range = 30.0  # Enemy fades beyond this distance
        self.engagement_range = 10.0  # Combat starts when within this distance

        # Combat state based on distance
        if initial_distance > self.engagement_range:
            # Enemy detected but not engaged - player can warp away!
            self.log_event(f"Enemy detected {initial_distance:.1f} units away!")
            self.log_event(f"Use warp commands to escape or advance to engage")
            # Start inactive until player gets close or enemy catches up
            self.active = False
        else:
            # Close range - immediate engagement
            self.log_event(f"Enemy engagement at {initial_distance:.1f} units!")

    def log_event(self, message: str):
        """Add message to combat log"""
        self.log.append(f"[T{self.turn}] {message}")
        if len(self.log) > 20:
            self.log.pop(0)

    def update(self, dt: float):
        """
        Update combat state.
        - Check distance for engagement/disengagement
        - Update weapon charging
        - Auto-fire enemy weapons
        - Check victory/defeat conditions
        """
        # Update ship positions (from normal warp commands)
        self.player_galaxy_position = self.player_ship.galaxy_position
        self.enemy_galaxy_position = self.enemy_ship.galaxy_position

        # Calculate current distance
        current_distance = abs(self.player_galaxy_position - self.enemy_galaxy_position)

        # Check for engagement/disengagement based on distance
        if not self.active and current_distance <= self.engagement_range:
            # Enemy got close - engage combat!
            self.active = True
            self.log_event(f"Enemy closing in! Combat engaged at {current_distance:.1f} units")
            play_sound("alarm", 0.5)
        elif self.active and current_distance > self.sensor_range:
            # Escaped beyond sensor range!
            self.active = False
            self.log_event(f"✓ Escaped beyond sensor range ({current_distance:.1f} units)")
            play_sound("success", 0.5)
            return

        # Only continue if combat is active
        if not self.active:
            # Update ships but no combat
            self.player_ship.update(dt)
            self.enemy_ship.update(dt)
            return

        # Active combat - update both ships
        self.player_ship.update(dt)
        self.enemy_ship.update(dt)

        # Update hacking system (network combat!)
        hack_messages = self.hacking.update(dt)
        for msg in hack_messages:
            self.log_event(msg)

        # Enemy AI
        self._enemy_ai(dt)

        # Check end conditions
        # Ship destroyed if hull <= 0 OR 75%+ systems destroyed
        player_destroyed = self._check_ship_destroyed(self.player_ship)
        enemy_destroyed = self._check_ship_destroyed(self.enemy_ship)

        if player_destroyed:
            self.active = False
            self.log_event("💀 YOUR SHIP HAS BEEN DESTROYED!")
            play_sound("explosion", 1.0)

        if enemy_destroyed:
            self.active = False
            self.log_event("✓ Enemy ship destroyed!")
            play_sound("explosion", 0.8)

    def _check_ship_destroyed(self, ship: Ship) -> bool:
        """
        Check if ship is destroyed.
        Ship is destroyed if:
        1. Hull <= 0, OR
        2. 75% or more of systems are destroyed
        """
        # Check hull
        if ship.hull <= 0:
            return True

        # Check system destruction percentage
        total_systems = len([r for r in ship.rooms.values() if r.system_type != SystemType.NONE])
        if total_systems == 0:
            return ship.hull <= 0  # Fallback to hull only

        destroyed_systems = len([r for r in ship.rooms.values()
                                if r.system_type != SystemType.NONE and r.health <= 0])

        destruction_percentage = destroyed_systems / total_systems

        # Ship explodes if 75% or more systems destroyed
        if destruction_percentage >= 0.75:
            # Set hull to 0 to mark as destroyed
            ship.hull = 0
            return True

        return False

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
        Player ship attempts to move closer to enemy during active combat.
        Returns True if successful.
        """
        if not self.active:
            return False  # Can't maneuver if not in active combat

        if self.combat_distance <= self.min_distance:
            return False

        # Move 1 unit closer
        old_distance = self.combat_distance
        self.combat_distance = max(self.min_distance, self.combat_distance - 1.0)
        self.log_event(f"Moving closer: {old_distance:.1f} → {self.combat_distance:.1f} units")
        return True

    def move_away(self) -> bool:
        """
        Player ship attempts to move away from enemy during active combat.
        Returns True if successful.
        """
        if not self.active:
            return False  # Can't maneuver if not in active combat

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

        KERNEL ENFORCEMENT: Checks all requirements (power, charge, etc.)
        Returns False with error message if requirements not met.
        PooScripts cannot bypass these checks!
        """
        attacker_name = "You" if attacker == self.player_ship else attacker.name

        # KERNEL CHECK 1: Weapons system must be functional (has power, not damaged, etc.)
        if SystemType.WEAPONS in attacker.systems:
            weapons_system = attacker.systems[SystemType.WEAPONS]
            if not weapons_system.is_online():
                # Determine why weapons are offline
                if not weapons_system.room:
                    self.log_event(f"{attacker_name}: ERROR - No weapons system!")
                elif weapons_system.room.health <= 0.2:
                    self.log_event(f"{attacker_name}: ERROR - Weapons system destroyed!")
                elif weapons_system.room.breached:
                    self.log_event(f"{attacker_name}: ERROR - Weapons system breached!")
                elif weapons_system.room.power_allocated <= 0:
                    self.log_event(f"{attacker_name}: ERROR - Weapons have no power!")
                elif not weapons_system.room.is_functional:
                    # Check if it's a reactor power issue
                    total_power = sum(r.power_allocated for r in attacker.rooms.values())
                    available = attacker.get_available_power()
                    if total_power > available:
                        self.log_event(f"{attacker_name}: ERROR - Insufficient power! ({available}/{total_power} available)")
                        self.log_event(f"  Reactor damaged - not enough power for all systems!")
                    else:
                        self.log_event(f"{attacker_name}: ERROR - Weapons system offline!")
                return False
        else:
            self.log_event(f"{attacker_name}: ERROR - No weapons system!")
            return False

        # KERNEL CHECK 2: Weapon must be charged
        if not weapon.is_ready():
            self.log_event(f"{attacker_name}: {weapon.name} not ready (charging...)")
            return False

        # Consume the charge (weapon fires)
        if not weapon.fire():
            return False

        # KERNEL CHECK 3: Range
        if self.combat_distance > weapon.range:
            self.log_event(f"{attacker_name}: {weapon.name} out of range! ({self.combat_distance:.1f}/{weapon.range:.1f})")
            # Charge already consumed
            return False

        # KERNEL CHECK 4: Missiles
        if weapon.requires_missiles:
            if attacker.missiles <= 0:
                self.log_event(f"{attacker.name}: No missiles!")
                # Charge already consumed
                return False
            attacker.missiles -= 1

        # Play weapon fire sound
        weapon_sound = "laser_fire"  # Default
        if hasattr(weapon, 'weapon_type'):
            weapon_type_str = weapon.weapon_type.value  # Get enum value as string
            if "missile" in weapon_type_str:
                weapon_sound = "missile_fire"
            elif "beam" in weapon_type_str:
                weapon_sound = "beam_fire"
        play_sound(weapon_sound, 0.5)

        # Calculate damage with crew bonus
        # Base damage from weapon
        base_damage = weapon.damage * weapon.shots

        # Crew in weapons room provide damage bonus
        # Each skill level = +10% damage, crew effectiveness already included in system
        crew_bonus = 0.0
        if SystemType.WEAPONS in attacker.systems:
            weapons_system = attacker.systems[SystemType.WEAPONS]
            if weapons_system.room and weapons_system.room.crew:
                # Get crew bonus from room (10% per skill level)
                crew_bonus = weapons_system.room.crew_bonus

        # Apply crew bonus to damage (100% base + bonus)
        total_damage = base_damage * (1.0 + crew_bonus)

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

        # Remaining damage hits systems or hull based on targeting
        if total_damage > 0:
            # STRATEGIC TARGETING: If targeting a system, damage goes there FIRST
            if target_room_name and target_room_name in defender.rooms:
                room = defender.rooms[target_room_name]

                # System takes FULL damage (converted to health %)
                # Each point of damage = 5% system health lost (20 damage destroys a system)
                system_damage = total_damage * 0.05
                old_health = room.health
                room.take_damage(system_damage)

                self.log_event(f"{attacker_name} fired {weapon.name} at {room.name}!")
                self.log_event(f"  ⚡ {room.name}: {old_health:.0%} → {room.health:.0%}")

                # System damage sound
                if room.health < 0.5:
                    play_sound("system_damage", 0.7)
                else:
                    play_sound("hull_hit", 0.5)

                # If system is destroyed, SPILLOVER to hull (only 20%)
                if room.health <= 0:
                    spillover = total_damage * 0.2
                    defender.hull -= spillover
                    self.log_event(f"  💥 {room.name} destroyed! {int(spillover)} spillover to hull")
                    play_sound("explosion", 0.6)
                else:
                    # Minor hull damage when hitting subsystem (10%)
                    defender.hull -= total_damage * 0.1
                    if total_damage * 0.1 > 1:
                        self.log_event(f"  💥 {int(total_damage * 0.1)} hull damage")

                # Higher chance of fire when targeting systems (15%)
                if random.random() < 0.15 and room.health > 0:
                    room.on_fire = True
                    self.log_event(f"  🔥 Fire in {room.name}!")
                    play_sound("alarm", 0.4)

                # Chance of breach on very damaged systems (10%)
                if random.random() < 0.10 and room.health < 0.3:
                    room.breached = True
                    self.log_event(f"  💨 {room.name} breached!")
                    play_sound("alarm", 0.5)

            else:
                # No targeting = hull damage
                defender.hull -= total_damage
                self.log_event(f"{attacker_name} fired {weapon.name}!")
                self.log_event(f"  💥 {int(total_damage)} hull damage!")
                play_sound("hull_hit", 0.7)

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

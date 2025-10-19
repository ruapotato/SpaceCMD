"""
World Manager - Controls the game world outside the ship

This is the Python layer that controls:
- Linear galaxy simulation
- Enemy spawning (with ShipOS instances!)
- Random encounters
- World events
- Environmental hazards
- Loot and rewards

The ship's OS (ShipOS) only controls the ship itself.
The world manager controls everything external to the ship.
"""

import random
import time
from typing import Optional, Callable
from .linear_galaxy import LinearGalaxy, POIType
from .enemy_ships import create_enemy_with_os


class WorldManager:
    """
    Manages the game world and enemy encounters.

    This is separate from ShipOS - ShipOS controls the ship,
    WorldManager controls the world around the ship.
    """

    def __init__(self, ship_os, max_galaxy_distance: float = 1000.0):
        """
        Initialize world manager.

        Args:
            ship_os: The ShipOS instance (for monitoring ship state)
            max_galaxy_distance: Size of the galaxy (distance from center to outer rim)
        """
        self.ship_os = ship_os
        self.ship = ship_os.ship

        # Linear Galaxy (1D galaxy from center to outer rim)
        self.galaxy = LinearGalaxy(max_distance=max_galaxy_distance)

        # Initialize ship position to outer rim (start position)
        self.ship.galaxy_distance_from_center = max_galaxy_distance

        # Combat state
        self.combat_state = None
        self.enemy_ship = None  # EnemyShipWithOS instance (enemy computer!)

        # World state
        self.distress_beacon_active = False  # Ship broadcasting distress
        self.scan_signature_high = False     # Ship has high scan signature
        self.last_encounter_time = 0
        self.encounter_cooldown = 10.0  # Seconds between encounters (was 30.0)

        # Callbacks
        self.on_attack_callback = None  # Called when ship takes damage
        self.on_encounter_start = None  # Called when encounter begins
        self.on_encounter_end = None    # Called when encounter ends
        self.on_poi_arrival = None      # Called when arriving at POI

        # Encounter probability (chance per second of enemy encounter while traveling)
        self.base_encounter_chance = 0.05  # 5% per second while moving (was 1%)
        self.encounter_multiplier = 1.0

    def set_distress_beacon(self, active: bool):
        """
        Ship emits distress beacon (attracts enemies!).
        Called when ship's systems broadcast signals.
        """
        self.distress_beacon_active = active
        if active:
            print("\n📡 DISTRESS BEACON ACTIVATED - Enemies will detect us!\n")
            # Immediate high chance of encounter
            self.encounter_multiplier = 10.0
        else:
            self.encounter_multiplier = 1.0

    def set_scan_signature(self, high: bool):
        """
        Ship has high scan signature (more visible to enemies).
        Called when ship runs active scans or uses high-power systems.
        """
        self.scan_signature_high = high
        if high:
            self.encounter_multiplier = 3.0
        else:
            self.encounter_multiplier = 1.0

    def trigger_encounter(self, enemy_type: str = None, forced: bool = False):
        """
        Spawn an enemy encounter.

        Args:
            enemy_type: Type of enemy to spawn (None = auto-select based on difficulty)
            forced: If True, bypass cooldown and probability checks
        """
        # Check cooldown
        if not forced:
            time_since_last = time.time() - self.last_encounter_time
            if time_since_last < self.encounter_cooldown:
                return False

        # Already in combat?
        if self.combat_state and self.combat_state.active:
            return False

        # Auto-select enemy type based on position if not specified
        if enemy_type is None:
            enemy_type = self.galaxy.get_enemy_type_for_position(self.ship.galaxy_distance_from_center)

        # Create enemy WITH OS (enemies are computers running hostile AI!)
        self.enemy_ship = create_enemy_with_os(enemy_type)

        # Spawn enemy at sensor range distance (15-25 units away)
        # This gives player a chance to react and potentially outrun them!
        spawn_distance = random.uniform(15, 25)
        # Spawn ahead or behind player randomly
        direction = random.choice([-1, 1])
        self.enemy_ship.ship.galaxy_position = self.ship.galaxy_position + (spawn_distance * direction)
        self.enemy_ship.ship.galaxy_distance_from_center = self.enemy_ship.ship.galaxy_position

        # Start combat
        from core.combat import CombatState
        self.combat_state = CombatState(self.ship, self.enemy_ship.ship)
        self.last_encounter_time = time.time()

        # Notify
        print(f"\n⚠️  ALERT: Hostile ship detected!")
        print(f"    {self.enemy_ship.ship.name} is attacking!")
        print(f"    Hull: {self.enemy_ship.ship.hull}/{self.enemy_ship.ship.hull_max}")
        print(f"    Shields: {int(self.enemy_ship.ship.shields)}/{self.enemy_ship.ship.shields_max}")
        print()

        if self.on_encounter_start:
            self.on_encounter_start(self.enemy_ship.ship)

        return True

    def update(self, dt: float):
        """
        Update world state.

        Args:
            dt: Delta time in seconds
        """
        # Track previous hull for damage detection
        prev_hull = self.ship.hull
        prev_position = self.ship.galaxy_distance_from_center

        # Update ship position (if moving and not in combat)
        if not (self.combat_state and self.combat_state.active):
            self.ship.update_position(dt)

        # Check if we arrived at a POI
        if abs(self.ship.galaxy_distance_from_center - prev_position) > 0.1:
            poi = self.galaxy.check_poi_proximity(self.ship.galaxy_distance_from_center, threshold=5.0)
            if poi and not poi.visited:
                poi.visited = True
                self._handle_poi_arrival(poi)

        # Update combat if exists (could be active or inactive due to distance)
        if self.combat_state:
            # Run enemy AI if combat is active
            if self.combat_state.active and self.enemy_ship:
                self.enemy_ship.run_ai_turn()

            # Update combat physics (handles engagement/disengagement)
            self.combat_state.update(dt)

            # Check if player took damage (only during active combat)
            if self.combat_state.active and self.ship.hull < prev_hull:
                if self.on_attack_callback:
                    damage_intensity = min(1.0, (prev_hull - self.ship.hull) / 5.0)
                    self.on_attack_callback(damage_intensity, (255, 0, 0))

            # Clean up combat state if truly ended (death or full escape)
            galaxy_distance = abs(self.combat_state.player_galaxy_position - self.combat_state.enemy_galaxy_position)

            if self.ship.hull <= 0:
                print("\n💀 SHIP DESTROYED!")
                print("    Game Over!")
                print()
                self.combat_state = None
                self.enemy_ship = None
            elif self.enemy_ship.ship.hull <= 0:
                print(f"\n✓ {self.enemy_ship.ship.name} destroyed!")
                print(f"  +{self.enemy_ship.ship.scrap} scrap collected")
                print()
                self.ship.scrap += self.enemy_ship.ship.scrap

                if self.on_encounter_end:
                    self.on_encounter_end(victory=True)

                self.combat_state = None
                self.enemy_ship = None
            elif galaxy_distance > self.combat_state.sensor_range:
                # Fully escaped - enemy lost on sensors
                print(f"\n✓ Escaped! Enemy beyond sensor range ({galaxy_distance:.1f} units)")
                print()
                if self.on_encounter_end:
                    self.on_encounter_end(victory=False)

                self.combat_state = None
                self.enemy_ship = None

        # Random encounters (while traveling OR when beacon is active)
        else:
            # Check for random encounter
            # Normally requires movement, but beacon attracts enemies even when stationary!
            is_moving = abs(self.ship.velocity) > 0.1
            if is_moving or self.distress_beacon_active:
                encounter_chance = self.base_encounter_chance * self.encounter_multiplier * dt
                # Higher chance if beacon active or high signature
                if self.distress_beacon_active:
                    encounter_chance *= 10.0
                elif self.scan_signature_high:
                    encounter_chance *= 3.0

                if random.random() < encounter_chance:
                    self.trigger_encounter()

    def get_combat_state(self):
        """Get current combat state (for UI display)"""
        return self.combat_state

    def is_in_combat(self) -> bool:
        """Check if currently in combat"""
        return self.combat_state is not None and self.combat_state.active

    # =========================================================================
    # GALAXY NAVIGATION
    # =========================================================================

    def _handle_poi_arrival(self, poi):
        """Handle what happens when arriving at a POI"""
        print(f"\n{'='*60}")
        print(f"ARRIVED AT: {poi.name.upper()}")
        print(f"Position: {poi.position:.1f} (difficulty: {self.galaxy.get_difficulty(poi.position):.1%})")
        print(f"{'='*60}\n")

        # Handle based on POI type
        if poi.type == POIType.STORE:
            print("🏪 Merchant ship detected!")
            print("Type 'store' to browse their wares")
            print()

        elif poi.type == POIType.REPAIR:
            print("🔧 Repair station found!")
            repair_amount = 10
            old_hull = self.ship.hull
            self.ship.hull = min(self.ship.hull_max, self.ship.hull + repair_amount)
            healed = self.ship.hull - old_hull
            if healed > 0:
                print(f"Hull repaired: +{healed} HP")
            print()

        elif poi.type == POIType.DISTRESS:
            print("📡 Distress beacon detected!")
            print("Someone needs help... or is it a trap?")
            # 50% chance of encounter
            if random.random() < 0.5:
                print("⚠️  It's an ambush!")
                self.trigger_encounter(forced=True)
            else:
                print("✓ Found supplies in the wreckage")
                self._trigger_scrap_reward(random.randint(10, 20))
            print()

        elif poi.type == POIType.NEBULA:
            print("🌫️  Entering nebula...")
            print("⚠️  WARNING: Shields offline in nebula!")
            self.ship.shields = 0
            print()

        elif poi.type == POIType.ASTEROID:
            print("☄️  Asteroid field!")
            print("⚠️  Navigation is hazardous here")
            # Small chance of damage
            if random.random() < 0.3:
                damage = random.randint(1, 3)
                self.ship.hull = max(0, self.ship.hull - damage)
                print(f"💥 Hull damaged by asteroid! -{damage} HP")
            print()

        elif poi.type == POIType.STATION:
            print("🏛️  Space station!")
            print("Safe haven. You can repair and resupply here.")
            print("Type 'store' to browse station inventory")
            print()

        elif poi.type == POIType.DERELICT:
            print("🛸 Derelict ship detected!")
            print("Scanning for salvage...")
            self._trigger_scrap_reward(random.randint(5, 15))

        elif poi.type == POIType.ANOMALY:
            print("🌀 Strange anomaly detected...")
            print("Sensors are going crazy!")
            self._trigger_random_event()

        elif poi.type == POIType.BOSS:
            print("⚠️  ⚠️  ⚠️  BOSS ENCOUNTER! ⚠️  ⚠️  ⚠️")
            print("This is it. The Rebel Flagship!")
            print()
            self.trigger_encounter(enemy_type="rebel_fighter", forced=True)

        # Callback
        if self.on_poi_arrival:
            self.on_poi_arrival(poi)

    def _trigger_scrap_reward(self, amount: int):
        """Give scrap reward to player"""
        print(f"✓ Found {amount} scrap!")
        self.ship.scrap += amount
        print()

    def _trigger_random_event(self):
        """Trigger a random event with choices"""
        events = [
            {
                "description": "You detect a small automated ship adrift...",
                "reward": "Found 10 scrap!",
                "scrap": 10
            },
            {
                "description": "You find a weapons cache floating in space!",
                "reward": "Found 15 scrap worth of parts!",
                "scrap": 15
            },
            {
                "description": "A friendly trader offers supplies...",
                "reward": "Traded for 12 scrap",
                "scrap": 12
            }
        ]

        event = random.choice(events)
        print(event["description"])
        print(f"✓ {event['reward']}")
        self.ship.scrap += event.get("scrap", 0)
        print()

    def get_nearby_pois(self, sensor_range: float = 100.0):
        """Get POIs within sensor range"""
        return self.galaxy.get_nearby_pois(self.ship.galaxy_distance_from_center, sensor_range)

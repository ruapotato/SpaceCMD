"""
World Manager - Controls the game world outside the ship

This is the Python layer that controls:
- World map and navigation
- Enemy spawning
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
from .world_map import WorldMap, NodeType


class WorldManager:
    """
    Manages the game world and enemy encounters.

    This is separate from ShipOS - ShipOS controls the ship,
    WorldManager controls the world around the ship.
    """

    def __init__(self, ship_os, num_sectors: int = 8):
        """
        Initialize world manager.

        Args:
            ship_os: The ShipOS instance (for monitoring ship state)
            num_sectors: Number of sectors in the map
        """
        self.ship_os = ship_os
        self.ship = ship_os.ship

        # World Map
        self.world_map = WorldMap(num_sectors=num_sectors, nodes_per_sector=8)

        # Initialize ship position to starting node
        starting_node = self.world_map.get_current_node()
        if starting_node:
            self.ship.galaxy_distance_from_center = starting_node.distance_from_center

        # Combat state
        self.combat_state = None
        self.enemy_ship = None

        # World state
        self.distress_beacon_active = False  # Ship broadcasting distress
        self.scan_signature_high = False     # Ship has high scan signature
        self.last_encounter_time = 0
        self.encounter_cooldown = 30.0  # Seconds between encounters

        # Callbacks
        self.on_attack_callback = None  # Called when ship takes damage
        self.on_encounter_start = None  # Called when encounter begins
        self.on_encounter_end = None    # Called when encounter ends
        self.on_jump_complete = None    # Called when jump completes

        # Encounter probability
        self.base_encounter_chance = 0.0  # 0% by default
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

    def trigger_encounter(self, enemy_type: str = "gnat", forced: bool = False):
        """
        Spawn an enemy encounter.

        Args:
            enemy_type: Type of enemy to spawn
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

        # Create enemy
        from core.enemy_ships import ENEMY_SHIPS
        from core.combat import CombatState

        if enemy_type in ENEMY_SHIPS:
            self.enemy_ship = ENEMY_SHIPS[enemy_type]()
        else:
            self.enemy_ship = ENEMY_SHIPS["gnat"]()

        # Start combat
        self.combat_state = CombatState(self.ship, self.enemy_ship)
        self.last_encounter_time = time.time()

        # Notify
        print(f"\n⚠️  ALERT: Hostile ship detected!")
        print(f"    {self.enemy_ship.name} is attacking!")
        print(f"    Hull: {self.enemy_ship.hull}/{self.enemy_ship.hull_max}")
        print(f"    Shields: {int(self.enemy_ship.shields)}/{self.enemy_ship.shields_max}")
        print()

        if self.on_encounter_start:
            self.on_encounter_start(self.enemy_ship)

        return True

    def update(self, dt: float):
        """
        Update world state.

        Args:
            dt: Delta time in seconds
        """
        # Track previous hull for damage detection
        prev_hull = self.ship.hull

        # Update combat if active
        if self.combat_state and self.combat_state.active:
            self.combat_state.update(dt)

            # Check if player took damage
            if self.ship.hull < prev_hull:
                if self.on_attack_callback:
                    damage_intensity = min(1.0, (prev_hull - self.ship.hull) / 5.0)
                    self.on_attack_callback(damage_intensity, (255, 0, 0))

            # Check if combat ended
            if not self.combat_state.active:
                if self.ship.hull <= 0:
                    print("\n💀 SHIP DESTROYED!")
                    print("    Game Over!")
                    print()
                elif self.enemy_ship.hull <= 0:
                    print(f"\n✓ {self.enemy_ship.name} destroyed!")
                    print(f"  +{self.enemy_ship.scrap} scrap collected")
                    print()
                    self.ship.scrap += self.enemy_ship.scrap

                    if self.on_encounter_end:
                        self.on_encounter_end(victory=True)

                    self.combat_state = None
                    self.enemy_ship = None

        # Random encounters (if beacon active or high signature)
        else:
            if self.distress_beacon_active or self.scan_signature_high:
                # Check for random encounter
                encounter_chance = self.base_encounter_chance * self.encounter_multiplier * dt
                if random.random() < encounter_chance:
                    self.trigger_encounter("gnat")

    def get_combat_state(self):
        """Get current combat state (for UI display)"""
        return self.combat_state

    def is_in_combat(self) -> bool:
        """Check if currently in combat"""
        return self.combat_state is not None and self.combat_state.active

    # =========================================================================
    # MAP NAVIGATION
    # =========================================================================

    def jump_to_node(self, node_id: str) -> bool:
        """
        Jump to a new node on the map.

        Args:
            node_id: ID of node to jump to

        Returns:
            True if jump successful
        """
        # Can't jump during combat
        if self.is_in_combat():
            return False

        # Try to jump
        if not self.world_map.jump_to_node(node_id):
            return False

        # Use some fuel
        fuel_cost = 1
        if self.ship.dark_matter >= fuel_cost:
            self.ship.dark_matter -= fuel_cost

        # Update ship's galaxy position (distance from center)
        current_node = self.world_map.get_current_node()
        if current_node:
            self.ship.galaxy_distance_from_center = current_node.distance_from_center

        # Handle arrival at new node
        self._handle_node_arrival()

        # Callback
        if self.on_jump_complete:
            self.on_jump_complete(self.world_map.get_current_node())

        return True

    def _handle_node_arrival(self):
        """Handle what happens when arriving at a new node"""
        node = self.world_map.get_current_node()
        if not node:
            return

        print(f"\n{'='*60}")
        print(f"ARRIVED AT: {node.type.value.upper()} (Sector {node.sector + 1})")
        print(f"{'='*60}\n")

        # Handle based on node type
        if node.type == NodeType.EMPTY:
            print("Nothing here. All clear.")
            print()

        elif node.type == NodeType.COMBAT:
            print(f"⚠️  Enemy ship detected!")
            print()
            self.trigger_encounter(node.enemy_type, forced=True)

        elif node.type == NodeType.ELITE_COMBAT:
            print(f"⚠️  ELITE ENEMY detected!")
            print("This will be a tough fight...")
            print()
            self.trigger_encounter(node.enemy_type, forced=True)

        elif node.type == NodeType.STORE:
            print("🏪 Merchant ship detected!")
            print("Type 'store' to browse their wares")
            print()

        elif node.type == NodeType.EVENT:
            print("📡 Receiving transmission...")
            self._trigger_random_event()

        elif node.type == NodeType.DISTRESS:
            print("📡 Distress beacon detected!")
            print("Someone needs help... or is it a trap?")
            print()

        elif node.type == NodeType.REPAIR:
            print("🔧 Repair station found!")
            repair_amount = 5
            old_hull = self.ship.hull
            self.ship.hull = min(self.ship.hull_max, self.ship.hull + repair_amount)
            healed = self.ship.hull - old_hull
            if healed > 0:
                print(f"Hull repaired: +{healed} HP")
            print()

        elif node.type == NodeType.NEBULA:
            print("🌫️  Entering nebula...")
            print("⚠️  WARNING: Shields offline in nebula!")
            self.ship.shields = 0
            print()

        elif node.type == NodeType.ASTEROID:
            print("☄️  Asteroid field!")
            print("⚠️  Navigation is hazardous here")
            print()

        elif node.type == NodeType.BOSS:
            print("⚠️  ⚠️  ⚠️  BOSS ENCOUNTER! ⚠️  ⚠️  ⚠️")
            print("This is it. The final battle!")
            print()
            # TODO: Implement boss encounter

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

    def get_available_jumps(self):
        """Get list of nodes available for jumping"""
        return self.world_map.get_available_jumps()

"""
Linear Galaxy System

A simple 1D galaxy where:
- Position is distance from galactic center (0 = center, higher = outer rim)
- Ships have positions and move continuously
- Points of Interest (POIs) are at specific positions
- Encounters can happen anywhere during travel
- Combat is position-based (can flee, chase, etc.)
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
import random
import math


class POIType(Enum):
    """Types of Points of Interest"""
    STORE = "store"              # Merchant/shop
    REPAIR = "repair"            # Repair station
    DISTRESS = "distress"        # Distress beacon
    NEBULA = "nebula"            # Nebula (shields disabled)
    ASTEROID = "asteroid"        # Asteroid field
    STATION = "station"          # Space station (safe haven)
    ANOMALY = "anomaly"          # Strange phenomena
    DERELICT = "derelict"        # Abandoned ship
    BOSS = "boss"                # Boss location


class PointOfInterest:
    """A point of interest in the galaxy"""

    def __init__(self, poi_id: str, poi_type: POIType, position: float, name: str = None):
        self.id = poi_id
        self.type = poi_type
        self.position = position  # Distance from center
        self.name = name or f"{poi_type.value.title()} {poi_id}"
        self.visited = False
        self.active = True  # Some POIs can be deactivated after visit


class LinearGalaxy:
    """
    1D Galaxy - simple line from center to outer rim.

    Ships travel along this line, encountering POIs and enemies.
    """

    def __init__(self, max_distance: float = 1000.0):
        """
        Initialize galaxy.

        Args:
            max_distance: Maximum distance from center (outer rim)
        """
        self.max_distance = max_distance
        self.center_position = 0.0
        self.outer_rim_position = max_distance

        # Points of Interest
        self.pois: Dict[str, PointOfInterest] = {}
        self.next_poi_id = 0

        # Generate initial POIs
        self._generate_pois()

    def _generate_pois(self):
        """Generate points of interest throughout the galaxy"""
        # Boss at the center
        self.add_poi(POIType.BOSS, 0.0, "Rebel Flagship")

        # Stations every ~150 units (safe havens)
        for i in range(1, int(self.max_distance / 150) + 1):
            pos = i * 150 + random.uniform(-20, 20)
            if pos < self.max_distance:
                self.add_poi(POIType.STATION, pos, f"Station Alpha-{i}")

        # Stores scattered throughout
        num_stores = random.randint(5, 8)
        for i in range(num_stores):
            pos = random.uniform(100, self.max_distance - 50)
            self.add_poi(POIType.STORE, pos, f"Merchant Ship")

        # Repair stations
        num_repair = random.randint(4, 6)
        for i in range(num_repair):
            pos = random.uniform(150, self.max_distance - 50)
            self.add_poi(POIType.REPAIR, pos, "Repair Drone")

        # Nebulas (hazardous areas)
        num_nebula = random.randint(3, 5)
        for i in range(num_nebula):
            pos = random.uniform(200, self.max_distance - 100)
            self.add_poi(POIType.NEBULA, pos, "Ion Nebula")

        # Asteroid fields
        num_asteroid = random.randint(3, 5)
        for i in range(num_asteroid):
            pos = random.uniform(200, self.max_distance - 100)
            self.add_poi(POIType.ASTEROID, pos, "Asteroid Field")

        # Derelict ships (loot opportunities)
        num_derelict = random.randint(6, 10)
        for i in range(num_derelict):
            pos = random.uniform(100, self.max_distance - 50)
            self.add_poi(POIType.DERELICT, pos, "Derelict Ship")

        # Distress beacons (can be traps)
        num_distress = random.randint(3, 5)
        for i in range(num_distress):
            pos = random.uniform(100, self.max_distance - 50)
            self.add_poi(POIType.DISTRESS, pos, "Distress Beacon")

    def add_poi(self, poi_type: POIType, position: float, name: str = None) -> PointOfInterest:
        """Add a point of interest to the galaxy"""
        poi_id = f"POI{self.next_poi_id:03d}"
        self.next_poi_id += 1

        poi = PointOfInterest(poi_id, poi_type, position, name)
        self.pois[poi_id] = poi
        return poi

    def get_nearby_pois(self, position: float, range_distance: float) -> List[PointOfInterest]:
        """
        Get POIs within sensor range of position.

        Args:
            position: Current position
            range_distance: Sensor range

        Returns:
            List of POIs in range, sorted by distance
        """
        nearby = []
        for poi in self.pois.values():
            distance = abs(poi.position - position)
            if distance <= range_distance:
                nearby.append((distance, poi))

        # Sort by distance
        nearby.sort(key=lambda x: x[0])
        return [poi for dist, poi in nearby]

    def get_closest_poi(self, position: float) -> Optional[Tuple[PointOfInterest, float]]:
        """
        Get the closest POI to a position.

        Returns:
            Tuple of (poi, distance) or None if no POIs
        """
        if not self.pois:
            return None

        closest = None
        closest_dist = float('inf')

        for poi in self.pois.values():
            dist = abs(poi.position - position)
            if dist < closest_dist:
                closest_dist = dist
                closest = poi

        return (closest, closest_dist) if closest else None

    def get_difficulty(self, position: float) -> float:
        """
        Get difficulty level at position (0.0 to 1.0).
        Closer to center = harder.

        Args:
            position: Distance from center

        Returns:
            Difficulty from 0.0 (easy, outer rim) to 1.0 (hard, center)
        """
        return 1.0 - (position / self.max_distance)

    def get_enemy_type_for_position(self, position: float) -> str:
        """Get appropriate enemy type for this position"""
        difficulty = self.get_difficulty(position)

        if difficulty < 0.2:
            # Outer rim - easy
            return random.choice(["gnat"])
        elif difficulty < 0.4:
            return random.choice(["gnat", "pirate_scout"])
        elif difficulty < 0.6:
            return random.choice(["pirate_scout", "mantis_fighter"])
        elif difficulty < 0.8:
            return random.choice(["mantis_fighter", "rebel_fighter"])
        else:
            # Near center - hard
            return random.choice(["rebel_fighter", "rebel_fighter"])

    def check_poi_proximity(self, position: float, threshold: float = 5.0) -> Optional[PointOfInterest]:
        """
        Check if at a POI (within threshold distance).

        Args:
            position: Current position
            threshold: Distance threshold for "at" POI

        Returns:
            POI if within threshold, None otherwise
        """
        for poi in self.pois.values():
            if abs(poi.position - position) <= threshold:
                return poi
        return None

    def __repr__(self):
        return f"<LinearGalaxy max_dist={self.max_distance} pois={len(self.pois)}>"

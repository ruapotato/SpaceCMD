#!/usr/bin/env python3
"""
Enemy Ship AI System - Powered by PoohScript
Enemy ships run actual PoohScript automation that can be hacked!
"""

import os
import random
from typing import Dict, List, Optional, Tuple
from core.pooscript import execute_pooscript


class EnemyShipFilesystem:
    """Virtual filesystem for enemy ships with PoohScript AI"""

    def __init__(self, ship_name: str = "PIRATE", ship_type: str = "pirate"):
        self.ship_name = ship_name
        self.ship_type = ship_type
        self.files = {}
        self._create_filesystem()
        self._create_ai_scripts()

    def _create_filesystem(self):
        """Create /proc-style filesystem"""
        self.files = {
            # Ship status (updated each tick)
            "/proc/ship/name": self.ship_name,
            "/proc/ship/hull": "100",
            "/proc/ship/hull_max": "100",
            "/proc/ship/shields": "4",
            "/proc/ship/shields_max": "4",
            "/proc/ship/power": "8",
            "/proc/ship/power_max": "10",
            "/proc/ship/scrap": "50",

            # System status
            "/proc/systems/weapons": "online\npower: 2\ncharge: 0\nmax_charge: 100",
            "/proc/systems/shields": "online\npower: 2\nlayers: 4\nmax: 4",
            "/proc/systems/engines": "online\npower: 1\ndodge: 25\nevasion: 25%",
            "/proc/systems/oxygen": "online\npower: 1\nlevel: 100\nmax: 100",
            "/proc/systems/helm": "online\npower: 1",
            "/proc/systems/medbay": "online\npower: 1\nhealing: 2",
            "/proc/systems/sensors": "online\npower: 1\nrange: 100",

            # Crew status
            "/proc/crew/bot1": "name: Defense-Bot-Alpha\nroom: weapons\nhealth: 100\ntask: operate_weapons\nskills: weapons=2,repair=1",
            "/proc/crew/bot2": "name: Repair-Bot-Beta\nroom: shields\nhealth: 100\ntask: operate_shields\nskills: shields=2,repair=2",
            "/proc/crew/bot3": "name: Tactical-Bot-Gamma\nroom: helm\nhealth: 100\ntask: tactical_analysis\nskills: piloting=2,weapons=1",

            # Enemy (player) detection
            "/proc/enemy/detected": "true",
            "/proc/enemy/shields": "3",
            "/proc/enemy/hull": "30",
            "/proc/enemy/distance": "500",

            # System configuration
            "/etc/ship/config": "auto_fire=true\nauto_repair=true\naggression=high\ntarget_priority=shields",
            "/etc/ship/version": f"{self.ship_name} Combat OS v3.7.2",
            "/etc/cron/enabled": "true",

            # Cron jobs (automation scripts to run)
            "/etc/cron/jobs": "/usr/bin/weapon_control\n/usr/bin/shield_manager\n/usr/bin/damage_control\n/usr/bin/tactical_ai",
        }

    def _create_ai_scripts(self):
        """Create PoohScript AI automation"""

        # Weapon Control AI
        self.files["/usr/bin/weapon_control"] = b"""#!/usr/bin/pooscript
# Automatic Weapons Control System
# Priority: CRITICAL
# Controls weapon charging and firing

# Read weapon status
weapons = vfs.read("/proc/systems/weapons")
if "offline" in weapons:
    exit(0)  # Weapons offline, abort

# Parse weapon charge
charge = 0
for line in weapons.split("\\n"):
    if "charge:" in line:
        charge = int(line.split(":")[1].strip())

# Read enemy status
enemy_shields_str = vfs.read("/proc/enemy/shields")
enemy_shields = int(enemy_shields_str.strip())
enemy_hull_str = vfs.read("/proc/enemy/hull")
enemy_hull = int(enemy_hull_str.strip())

# Firing logic
if charge >= 100:
    # Weapon ready to fire
    if enemy_shields > 0:
        # Target shields first
        print("FIRE: laser shields")
        vfs.write("/proc/systems/weapons", "online\\npower: 2\\ncharge: 0\\nmax_charge: 100")
    else:
        # Target weapons system to disable enemy
        print("FIRE: laser weapons")
        vfs.write("/proc/systems/weapons", "online\\npower: 2\\ncharge: 0\\nmax_charge: 100")
else:
    # Charge weapons
    new_charge = min(100, charge + 10)
    vfs.write("/proc/systems/weapons", f"online\\npower: 2\\ncharge: {new_charge}\\nmax_charge: 100")
"""

        # Shield Management AI
        self.files["/usr/bin/shield_manager"] = b"""#!/usr/bin/pooscript
# Shield Management System
# Priority: HIGH
# Monitors and maintains shield integrity

# Read shield status
shields_data = vfs.read("/proc/systems/shields")
if "offline" in shields_data:
    # Try to repair
    print("REPAIR: shields")
    exit(0)

# Parse shield layers
current_shields = 0
for line in shields_data.split("\\n"):
    if "layers:" in line:
        current_shields = int(line.split(":")[1].strip())

# Read power status
power_data = vfs.read("/proc/ship/power")
available_power = int(power_data.strip())

# Shield maintenance
if current_shields < 2:
    # Critical! Need shields
    print("CRITICAL: Low shields!")

    # Try to add power to shields
    if available_power >= 2:
        print("POWER: shields +1")

    # Move repair bot to shields
    print("MOVE_CREW: bot2 shields")
    print("REPAIR: shields")
elif current_shields < 4:
    # Restore shields if we have power
    if available_power >= 3:
        print("POWER: shields +1")
"""

        # Damage Control AI
        self.files["/usr/bin/damage_control"] = b"""#!/usr/bin/pooscript
# Automatic Damage Control
# Priority: HIGH
# Repairs critical systems and manages hull breaches
# SMART: Sends bots to specific damaged rooms!

# Check hull integrity
hull_str = vfs.read("/proc/ship/hull")
hull_max_str = vfs.read("/proc/ship/hull_max")
hull = int(hull_str.strip())
hull_max = int(hull_max_str.strip())

hull_percent = (hull * 100) // hull_max

# Check each system and send bot to most damaged
systems = ["weapons", "shields", "engines", "oxygen"]
most_damaged_system = None
lowest_health = 100.0

for system in systems:
    try:
        sys_data = vfs.read(f"/proc/systems/{system}")

        # Parse health from system data
        for line in sys_data.split("\\n"):
            if "offline" in line.lower():
                # Critical! This system is offline
                most_damaged_system = system
                lowest_health = 0.0
                break
            # Look for health percentage or damage indicators
            if "damage" in line.lower() or "health" in line.lower():
                # System is damaged, prioritize it
                if most_damaged_system is None:
                    most_damaged_system = system
                    lowest_health = 50.0  # Assume moderate damage

    except:
        pass  # System might not exist

# Send repair bot to most damaged system
if most_damaged_system:
    print(f"PRIORITY REPAIR: {most_damaged_system}")
    print(f"MOVE_CREW: bot2 {most_damaged_system}")
    print(f"REPAIR: {most_damaged_system}")

# Emergency hull repairs if critical
if hull_percent < 30:
    print("EMERGENCY: Critical hull damage!")
    # All crew to repair stations if hull critical
    print("MOVE_CREW: bot3 hull_repair")
elif hull_percent < 60:
    print("WARNING: Hull damage detected")

# Check oxygen levels (always critical)
oxygen_data = vfs.read("/proc/systems/oxygen")
if "offline" in oxygen_data or "level: 0" in oxygen_data:
    print("EMERGENCY: Oxygen failure!")
    print("REPAIR: oxygen")
    print("MOVE_CREW: bot1 oxygen")
"""

        # Tactical AI
        self.files["/usr/bin/tactical_ai"] = b"""#!/usr/bin/pooscript
# Tactical Decision System
# Priority: MEDIUM
# Makes high-level tactical decisions

# Read ship status
hull_str = vfs.read("/proc/ship/hull")
hull_max_str = vfs.read("/proc/ship/hull_max")
hull = int(hull_str.strip())
hull_max = int(hull_max_str.strip())

shields_str = vfs.read("/proc/ship/shields")
shields = int(shields_str.strip())

# Read enemy status
enemy_hull_str = vfs.read("/proc/enemy/hull")
enemy_hull = int(enemy_hull_str.strip())
enemy_shields_str = vfs.read("/proc/enemy/shields")
enemy_shields = int(enemy_shields_str.strip())

# Tactical decisions
hull_percent = (hull * 100) // hull_max

# Retreat if heavily damaged and enemy strong
if hull_percent < 20 and enemy_shields > 0:
    print("TACTICAL: Retreat advised")
    # Check if FTL available
    engines = vfs.read("/proc/systems/engines")
    if "online" in engines:
        print("JUMP: ftl_jump")

# Aggressive tactics if winning
if hull_percent > 60 and enemy_hull < 30:
    print("TACTICAL: Press the attack")
    print("POWER: weapons +1")

# Focus fire strategy
config = vfs.read("/etc/ship/config")
if "target_priority=shields" in config and enemy_shields > 0:
    print("TARGET: shields")
elif enemy_hull < 50:
    print("TARGET: weapons")
"""

        # Power Management (if we want even more automation)
        self.files["/usr/bin/power_manager"] = b"""#!/usr/bin/pooscript
# Power Distribution AI
# Priority: LOW
# Optimizes power allocation

power_str = vfs.read("/proc/ship/power")
power_max_str = vfs.read("/proc/ship/power_max")
power = int(power_str.strip())
power_max = int(power_max_str.strip())

# Check shields
shields_str = vfs.read("/proc/ship/shields")
shields = int(shields_str.strip())

# Power priority: Shields > Weapons > Engines
if shields < 2 and power >= 2:
    print("POWER: shields +1")
    print("POWER: engines -1")
elif power >= 3:
    # Boost weapons if we have spare power
    print("POWER: weapons +1")
"""

    def read_file(self, filepath: str) -> Optional[str]:
        """Read a file from the enemy filesystem"""
        value = self.files.get(filepath, None)
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')
        return value

    def read_file_bytes(self, filepath: str) -> Optional[bytes]:
        """Read a file as bytes"""
        value = self.files.get(filepath, None)
        if isinstance(value, str):
            return value.encode('utf-8')
        return value

    def write_file(self, filepath: str, content: str) -> bool:
        """Write to a file"""
        if filepath in self.files:
            self.files[filepath] = content
            return True
        return False

    def list_directory(self, dirpath: str) -> List[str]:
        """List files in a directory"""
        if not dirpath.endswith('/'):
            dirpath += '/'

        files = []
        subdirs = set()

        for path in self.files.keys():
            if path.startswith(dirpath):
                remainder = path[len(dirpath):]
                if '/' in remainder:
                    # This is in a subdirectory
                    dir_name = remainder.split('/')[0]
                    subdirs.add(dir_name)
                else:
                    # This is a file in this directory
                    files.append(remainder)

        return sorted(list(subdirs) + files)

    def get_all_scripts(self) -> Dict[str, bytes]:
        """Get all executable PoohScript files"""
        scripts = {}
        for path, content in self.files.items():
            if path.startswith('/usr/bin/'):
                if isinstance(content, str):
                    content = content.encode('utf-8')
                if content.startswith(b'#!/usr/bin/pooscript') or content.startswith(b'#!/bin/pooscript'):
                    scripts[path] = content
        return scripts

    def get_cron_jobs(self) -> List[str]:
        """Get list of scripts to run each tick"""
        cron_enabled = self.read_file("/etc/cron/enabled")
        if cron_enabled != "true":
            return []

        jobs_content = self.read_file("/etc/cron/jobs")
        if not jobs_content:
            return []

        return [line.strip() for line in jobs_content.split('\n') if line.strip()]

    def disable_script(self, script_name: str) -> bool:
        """Disable an AI script (hacking result)"""
        # Remove from cron
        jobs = self.get_cron_jobs()
        script_path = f"/usr/bin/{script_name}" if not script_name.startswith('/') else script_name

        if script_path in jobs:
            jobs.remove(script_path)
            self.files["/etc/cron/jobs"] = '\n'.join(jobs)
            return True
        return False

    def steal_script(self, script_name: str) -> Optional[bytes]:
        """Steal a script (returns the code)"""
        script_path = f"/usr/bin/{script_name}" if not script_name.startswith('/') else script_name
        return self.read_file_bytes(script_path)

    def update_status(self, ship_state: Dict):
        """Update /proc files with current ship state"""
        # Update ship stats
        if 'hull' in ship_state:
            self.files['/proc/ship/hull'] = str(ship_state['hull'])
        if 'shields' in ship_state:
            self.files['/proc/ship/shields'] = str(ship_state['shields'])
        if 'power' in ship_state:
            self.files['/proc/ship/power'] = str(ship_state['power'])

        # Update enemy detection
        if 'enemy_hull' in ship_state:
            self.files['/proc/enemy/hull'] = str(ship_state['enemy_hull'])
        if 'enemy_shields' in ship_state:
            self.files['/proc/enemy/shields'] = str(ship_state['enemy_shields'])


def create_enemy_filesystem(ship_type: str = "pirate") -> EnemyShipFilesystem:
    """Factory function to create different enemy types"""
    names = {
        "pirate": "PIRATE RAIDER",
        "mantis": "MANTIS HUNTER",
        "rebel": "REBEL FIGHTER",
        "auto": "AUTO-SCOUT"
    }

    name = names.get(ship_type, "UNKNOWN VESSEL")
    return EnemyShipFilesystem(name, ship_type)


if __name__ == '__main__':
    # Test the enemy filesystem
    enemy = create_enemy_filesystem("pirate")

    print("=== Enemy Ship Filesystem ===")
    print(f"Ship: {enemy.read_file('/proc/ship/name')}")
    print()

    print("Cron Jobs:")
    for job in enemy.get_cron_jobs():
        print(f"  - {job}")
    print()

    print("=== PoohScript AI ===")
    scripts = enemy.get_all_scripts()
    for path, code in scripts.items():
        print(f"\n{path}:")
        print("─" * 40)
        print(code.decode('utf-8'))
        print("─" * 40)

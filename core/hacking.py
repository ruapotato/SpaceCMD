"""
Hacking System - Network Combat for SpaceCMD

This module implements the "Hackers meets FTL" combat mechanics:
- Network scanning to find vulnerabilities
- Hacking enemy systems to disable them
- Deploying malware/viruses
- Firewall defense
- Exploits and backdoors

In SpaceCMD, every ship is a computer running an OS. You can:
1. Scan enemy networks to find open ports
2. Exploit vulnerabilities to gain access
3. Disable enemy systems remotely
4. Plant backdoors for persistent access
5. Deploy viruses that spread and cause damage
"""

import random
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ExploitType(Enum):
    """Types of exploits available"""
    BUFFER_OVERFLOW = "buffer_overflow"      # Crash system
    SQL_INJECTION = "sql_injection"          # Access database
    ZERO_DAY = "zero_day"                    # Unknown vuln, high success
    BACKDOOR = "backdoor"                    # Persistent access
    DOS = "dos"                              # Denial of service
    PRIVILEGE_ESCALATION = "priv_esc"        # Gain root access


class MalwareType(Enum):
    """Types of malware that can be deployed"""
    VIRUS = "virus"              # Spreads between systems
    WORM = "worm"                # Self-replicating, damages over time
    TROJAN = "trojan"            # Hides, steals data
    RANSOMWARE = "ransomware"    # Encrypts systems
    ROOTKIT = "rootkit"          # Hides presence, persistent
    LOGIC_BOMB = "logic_bomb"    # Triggers on condition


class HackingAttempt:
    """Represents a single hacking attempt"""

    def __init__(self, attacker_ship, target_ship, exploit_type: ExploitType, target_system: str = None):
        self.attacker = attacker_ship
        self.target = target_ship
        self.exploit = exploit_type
        self.target_system = target_system  # Which system to target
        self.success = False
        self.detected = False
        self.time_remaining = 3.0  # Seconds to complete hack
        self.progress = 0.0

    def update(self, dt: float) -> bool:
        """
        Update hack progress.
        Returns True when complete.
        """
        self.progress += dt / self.time_remaining

        if self.progress >= 1.0:
            # Hack attempt complete - check success
            self.success = self._calculate_success()
            return True

        return False

    def _calculate_success(self) -> bool:
        """Calculate if hack succeeded based on various factors"""
        # Base success rate
        base_rate = {
            ExploitType.BUFFER_OVERFLOW: 0.7,
            ExploitType.SQL_INJECTION: 0.6,
            ExploitType.ZERO_DAY: 0.9,
            ExploitType.BACKDOOR: 0.5,
            ExploitType.DOS: 0.8,
            ExploitType.PRIVILEGE_ESCALATION: 0.4,
        }

        success_chance = base_rate.get(self.exploit, 0.5)

        # Target system health affects success
        if self.target_system and hasattr(self.target, 'rooms'):
            for room in self.target.rooms.values():
                if room.system_type and self.target_system.lower() in str(room.system_type).lower():
                    # Damaged systems are easier to hack
                    if room.health < 50:
                        success_chance += 0.2
                    break

        # Random roll
        return random.random() < success_chance


class Malware:
    """Active malware on a ship"""

    def __init__(self, malware_type: MalwareType, target_ship, target_system: str = None):
        self.type = malware_type
        self.target = target_ship
        self.target_system = target_system
        self.active = True
        self.ticks = 0
        self.damage_per_tick = 1
        self.spread_chance = 0.2 if malware_type == MalwareType.VIRUS else 0.0

    def update(self, dt: float) -> List[str]:
        """
        Update malware behavior.
        Returns list of effects/messages.
        """
        effects = []
        self.ticks += 1

        if not self.active:
            return effects

        # Different malware types behave differently
        if self.type == MalwareType.WORM:
            # Worms damage hull directly
            if self.ticks % 5 == 0:
                self.target.hull -= self.damage_per_tick
                effects.append(f"🐛 Worm dealing {self.damage_per_tick} damage to {self.target.name}")

        elif self.type == MalwareType.VIRUS:
            # Viruses spread to other systems
            if random.random() < self.spread_chance:
                effects.append(f"🦠 Virus spreading through {self.target.name}'s systems!")
                # Damage random system
                if hasattr(self.target, 'rooms') and self.target.rooms:
                    room = random.choice(list(self.target.rooms.values()))
                    room.health = max(0, room.health - 5)
                    effects.append(f"   {room.name} system damaged!")

        elif self.type == MalwareType.DOS:
            # DOS disables systems temporarily
            if self.target_system and hasattr(self.target, 'rooms'):
                for room in self.target.rooms.values():
                    if room.system_type and self.target_system.lower() in str(room.system_type).lower():
                        room.is_functional = False
                        effects.append(f"💥 DOS attack disabling {room.name}")
                        break

        elif self.type == MalwareType.LOGIC_BOMB:
            # Logic bombs trigger after X ticks
            if self.ticks == 10:
                effects.append(f"💣 LOGIC BOMB DETONATED!")
                # Major damage to target system
                if self.target_system and hasattr(self.target, 'rooms'):
                    for room in self.target.rooms.values():
                        if room.system_type and self.target_system.lower() in str(room.system_type).lower():
                            room.health = max(0, room.health - 30)
                            effects.append(f"   {room.name} critically damaged!")
                            break
                self.active = False  # One-time trigger

        return effects


class HackingSystem:
    """
    Manages all hacking operations in combat.

    This is the main interface for network-based combat.
    """

    def __init__(self):
        self.active_hacks: List[HackingAttempt] = []
        self.deployed_malware: List[Malware] = []
        self.scan_results: Dict[str, List[str]] = {}  # ship_name -> vulnerabilities

    def scan_target(self, attacker_ship, target_ship) -> List[str]:
        """
        Scan target ship for vulnerabilities.
        Returns list of discovered vulnerabilities.
        """
        vulns = []

        # Check system health - damaged systems have vulnerabilities
        if hasattr(target_ship, 'rooms'):
            for room in target_ship.rooms.values():
                if room.health < 100:
                    vuln_level = "HIGH" if room.health < 30 else "MEDIUM" if room.health < 70 else "LOW"
                    vulns.append(f"[{vuln_level}] {room.name} - Health: {room.health}%")

        # Random vulnerabilities
        possible_vulns = [
            "SSH service running on port 22 (outdated version)",
            "Firewall misconfigured - port 8080 open",
            "Unpatched buffer overflow in reactor controller",
            "Weak password on admin account",
            "SQL injection in weapons targeting system",
            "Zero-day exploit in shield generator firmware",
        ]

        # Add 1-3 random vulns
        for _ in range(random.randint(1, 3)):
            if possible_vulns:
                vuln = random.choice(possible_vulns)
                possible_vulns.remove(vuln)
                vulns.append(vuln)

        # Cache results
        self.scan_results[target_ship.name] = vulns

        return vulns

    def initiate_hack(self, attacker_ship, target_ship, exploit: ExploitType, target_system: str = None) -> HackingAttempt:
        """
        Begin a hacking attempt.
        Returns the HackingAttempt object.
        """
        hack = HackingAttempt(attacker_ship, target_ship, exploit, target_system)
        self.active_hacks.append(hack)
        return hack

    def deploy_malware(self, target_ship, malware_type: MalwareType, target_system: str = None) -> Malware:
        """
        Deploy malware to target ship.
        Requires successful hack first (or backdoor access).
        """
        malware = Malware(malware_type, target_ship, target_system)
        self.deployed_malware.append(malware)
        return malware

    def update(self, dt: float) -> List[str]:
        """
        Update all active hacks and malware.
        Returns list of messages/effects.
        """
        messages = []

        # Update active hacks
        completed_hacks = []
        for hack in self.active_hacks:
            if hack.update(dt):
                completed_hacks.append(hack)
                if hack.success:
                    messages.append(f"✓ Hack successful! Exploited {hack.exploit.value} on {hack.target.name}")
                    if hack.target_system:
                        messages.append(f"  → {hack.target_system} system compromised!")
                else:
                    messages.append(f"✗ Hack failed on {hack.target.name} (detected or blocked)")

        # Remove completed hacks
        for hack in completed_hacks:
            self.active_hacks.remove(hack)

        # Update malware
        inactive_malware = []
        for malware in self.deployed_malware:
            effects = malware.update(dt)
            messages.extend(effects)

            if not malware.active:
                inactive_malware.append(malware)

        # Remove inactive malware
        for malware in inactive_malware:
            self.deployed_malware.remove(malware)

        return messages

    def get_hack_progress_display(self) -> str:
        """Get display string for active hacks"""
        if not self.active_hacks:
            return ""

        lines = []
        lines.append("ACTIVE HACKS:")
        for i, hack in enumerate(self.active_hacks):
            progress_bar = "█" * int(hack.progress * 10) + "░" * (10 - int(hack.progress * 10))
            lines.append(f"  {i+1}. {hack.exploit.value:20} [{progress_bar}] {int(hack.progress * 100)}%")

        return "\n".join(lines)

    def get_malware_display(self) -> str:
        """Get display string for deployed malware"""
        if not self.deployed_malware:
            return ""

        lines = []
        lines.append("DEPLOYED MALWARE:")
        for i, malware in enumerate(self.deployed_malware):
            status = "ACTIVE" if malware.active else "INACTIVE"
            lines.append(f"  {i+1}. {malware.type.value:15} on {malware.target.name:15} [{status}]")

        return "\n".join(lines)

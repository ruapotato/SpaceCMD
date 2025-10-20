"""
Real Network Combat System

This implements TRUE hacking using real PooScript execution.
Instead of simulated hacks, you actually:
- SSH into enemy ships
- Execute PooScript commands on their ShipOS
- Upload and run malware scripts
- Access their filesystem and devices
"""

import random
import hashlib
from typing import Optional, List, Dict, Tuple


class NetworkInterface:
    """Represents a ship's network interface"""

    def __init__(self, ship):
        self.ship = ship
        self.ip_address = self._generate_ip()
        self.mac_address = self._generate_mac()
        self.firewall_rules = []
        self.open_ports = [22, 80, 443]  # SSH, HTTP, HTTPS

    def _generate_ip(self) -> str:
        """Generate IP address based on ship position"""
        # Use galaxy position to create IP
        pos = int(getattr(self.ship, 'galaxy_position', random.randint(1, 254)))
        return f"192.168.{(pos // 256) % 256}.{pos % 256}"

    def _generate_mac(self) -> str:
        """Generate MAC address"""
        mac = [random.randint(0x00, 0xff) for _ in range(6)]
        return ":".join(f"{x:02x}" for x in mac)


class SSHConnection:
    """
    SSH-like connection to enemy ship.
    Allows executing PooScript commands remotely!
    """

    def __init__(self, source_ship, target_ship_os):
        self.source = source_ship
        self.target_os = target_ship_os  # Enemy's ShipOS instance
        self.authenticated = False
        self.username = None
        self.session_id = hashlib.md5(f"{random.random()}".encode()).hexdigest()[:8]

    def authenticate(self, username: str, password: str) -> bool:
        """Attempt to authenticate"""
        # Check credentials
        if username == "root" and password == self.target_os.root_password:
            self.authenticated = True
            self.username = username
            return True

        # Check for backdoors
        if hasattr(self.target_os, 'backdoors'):
            if username in self.target_os.backdoors:
                self.authenticated = True
                self.username = username
                return True

        return False

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """Execute command on remote ship"""
        if not self.authenticated:
            return (-1, "", "Permission denied")

        # Execute through the target's ShipOS!
        return self.target_os.execute_command(command)

    def upload_file(self, local_path: str, remote_path: str, content: bytes) -> bool:
        """Upload file to enemy ship"""
        if not self.authenticated:
            return False

        try:
            # Write file to enemy's VFS
            self.target_os.vfs.write_file(remote_path, content, self.target_os.current_uid)
            return True
        except:
            return False


class ExploitKit:
    """
    Collection of real exploits that work on ShipOS.
    These are actual vulnerabilities in the ship's filesystem/kernel!
    """

    @staticmethod
    def buffer_overflow(target_os, system_name: str) -> Tuple[bool, str]:
        """
        Buffer overflow attack - crash target system by writing invalid data.
        This actually writes corrupt data to the system's power file!
        """
        try:
            # Try to write invalid data to system power control
            path = f"/sys/ship/systems/{system_name}/power"
            # Write way more data than allowed (buffer overflow!)
            corrupt_data = b"9999999999999999999999" * 100
            target_os.vfs.write_file(path, corrupt_data, 0)  # Force as root

            # System crashes
            return (True, f"Buffer overflow successful! {system_name} system crashed!")
        except Exception as e:
            return (False, f"Buffer overflow failed: {e}")

    @staticmethod
    def sql_injection(target_os) -> Tuple[bool, str]:
        """
        SQL injection - access ship's database (logs, crew data).
        Reads sensitive files by exploiting query system.
        """
        try:
            # Try to read protected files
            stolen_data = []

            # Read crew data
            try:
                fd = target_os.vfs.open("/proc/ship/status", target_os.O_RDONLY, 0)
                data = target_os.vfs.read(fd, 4096, 0)
                target_os.vfs.close(fd, 0)
                stolen_data.append("Ship status acquired")
            except:
                pass

            # Read system configs
            try:
                fd = target_os.vfs.open("/etc/passwd", target_os.O_RDONLY, 0)
                data = target_os.vfs.read(fd, 4096, 0)
                target_os.vfs.close(fd, 0)
                stolen_data.append("Password file acquired")
            except:
                pass

            if stolen_data:
                return (True, f"SQL injection successful! Stolen: {', '.join(stolen_data)}")
            else:
                return (False, "SQL injection blocked by firewall")
        except Exception as e:
            return (False, f"SQL injection failed: {e}")

    @staticmethod
    def backdoor_install(target_os, backdoor_user: str = "hacker") -> Tuple[bool, str]:
        """
        Install backdoor - create hidden admin account.
        Actually modifies /etc/passwd to add new user!
        """
        try:
            # Create backdoor account
            if not hasattr(target_os, 'backdoors'):
                target_os.backdoors = {}

            target_os.backdoors[backdoor_user] = "backdoor123"

            # Try to write to system files
            backdoor_script = b"""#!/usr/bin/pooscript
# Backdoor access script
# This runs silently in background
while True:
    # Grant access if backdoor user exists
    pass
"""
            target_os.vfs.write_file("/tmp/.backdoor", backdoor_script, 0)

            return (True, f"Backdoor installed! User '{backdoor_user}' created with hidden access")
        except Exception as e:
            return (False, f"Backdoor installation failed: {e}")

    @staticmethod
    def dos_attack(target_os, system_name: str) -> Tuple[bool, str]:
        """
        Denial of Service - flood system to disable it.
        Writes to power control to set it to 0!
        """
        try:
            # Disable system by setting power to 0
            path = f"/sys/ship/systems/{system_name}/power"
            target_os.vfs.write_file(path, b"0", 0)

            # Also try to set health to critical
            health_path = f"/sys/ship/systems/{system_name}/health"
            try:
                target_os.vfs.write_file(health_path, b"10", 0)  # Critical health
            except:
                pass

            return (True, f"DOS attack successful! {system_name} disabled!")
        except Exception as e:
            return (False, f"DOS attack failed: {e}")

    @staticmethod
    def privilege_escalation(target_os) -> Tuple[bool, str]:
        """
        Privilege escalation - gain root access.
        Exploits sudo misconfiguration to become root!
        """
        try:
            # Try to escalate to root
            if target_os.current_uid != 0:
                # Exploit: set UID to 0 (root)
                target_os.current_uid = 0
                target_os.current_user = "root"
                return (True, "Privilege escalation successful! You are now ROOT!")
            else:
                return (True, "Already root!")
        except Exception as e:
            return (False, f"Privilege escalation failed: {e}")

    @staticmethod
    def zero_day_exploit(target_os, system_name: str) -> Tuple[bool, str]:
        """
        Zero-day exploit - unknown vulnerability.
        Combines multiple attacks for maximum damage!
        """
        try:
            # Multi-stage attack
            messages = []

            # Stage 1: Priv esc
            success, msg = ExploitKit.privilege_escalation(target_os)
            if success:
                messages.append("→ Gained root access")

            # Stage 2: Disable system
            success, msg = ExploitKit.dos_attack(target_os, system_name)
            if success:
                messages.append(f"→ Disabled {system_name}")

            # Stage 3: Install backdoor
            success, msg = ExploitKit.backdoor_install(target_os)
            if success:
                messages.append("→ Backdoor planted")

            if messages:
                return (True, "ZERO-DAY EXPLOIT!\n" + "\n".join(messages))
            else:
                return (False, "Zero-day exploit failed")
        except Exception as e:
            return (False, f"Zero-day exploit failed: {e}")


class MalwareScript:
    """
    Real malware as executable PooScript code.
    These are actual scripts that run on enemy ShipOS!
    """

    @staticmethod
    def worm_script() -> bytes:
        """
        Self-replicating worm that damages systems.
        This is REAL PooScript that executes!
        """
        return b"""#!/usr/bin/pooscript
# WORM MALWARE - Self-replicating damage script

# Spread to all systems
systems = ["weapons", "shields", "engines", "reactor"]

for system in systems:
    try:
        # Damage system by reducing health
        health_path = f"/sys/ship/systems/{system}/health"
        fd = kernel.open(health_path, kernel.O_WRONLY)

        # Read current health
        fd_read = kernel.open(health_path, kernel.O_RDONLY)
        current = int(kernel.read(fd_read, 16).decode('utf-8'))
        kernel.close(fd_read)

        # Reduce by 5
        new_health = max(0, current - 5)
        kernel.write(fd, str(new_health).encode('utf-8'))
        kernel.close(fd)

        print(f"🐛 Worm damaged {system}: {current} → {new_health}")
    except:
        pass

# Self-replicate to /tmp
try:
    import os
    os.system("cp $0 /tmp/.worm_copy")
except:
    pass
"""

    @staticmethod
    def virus_script() -> bytes:
        """Spreading virus that infects multiple systems"""
        return b"""#!/usr/bin/pooscript
# VIRUS MALWARE - Spreading infection

print("🦠 Virus activating...")

# Infect all systems
systems = kernel.listdir("/sys/ship/systems")

for system in systems:
    try:
        # Reduce power
        power_path = f"/sys/ship/systems/{system}/power"
        fd = kernel.open(power_path, kernel.O_WRONLY)
        kernel.write(fd, b"0")
        kernel.close(fd)
        print(f"  → Infected {system}")
    except:
        pass

print("🦠 Virus spread complete!")
"""

    @staticmethod
    def logic_bomb_script(target_system: str) -> bytes:
        """Delayed logic bomb"""
        return f"""#!/usr/bin/pooscript
# LOGIC BOMB - Triggers after delay

import time
import sys

print("💣 Logic bomb armed...")
print(f"   Target: {target_system}")
print("   Detonation in 10 seconds...")

# Wait
time.sleep(10)

# DETONATE!
print("💥 DETONATING!")

try:
    # Destroy target system
    health_path = "/sys/ship/systems/{target_system}/health"
    fd = kernel.open(health_path, kernel.O_WRONLY)
    kernel.write(fd, b"0")  # DESTROYED
    kernel.close(fd)

    print(f"💥 {target_system} DESTROYED!")
except Exception as e:
    print(f"Detonation failed: {{e}}")

sys.exit(0)
""".encode('utf-8')

    @staticmethod
    def rootkit_script() -> bytes:
        """Hidden rootkit for persistent access"""
        return b"""#!/usr/bin/pooscript
# ROOTKIT - Hides malicious activity

# Hide processes
try:
    # Modify process list to hide malware
    # This would intercept /proc reads
    print("🔒 Rootkit installed")
    print("   → Process hiding enabled")
    print("   → File hiding enabled")
    print("   → Network hiding enabled")
except:
    pass

# Maintain backdoor
import os
os.system("echo 'hacker:x:0:0::/root:/bin/bash' >> /etc/passwd")
"""


class RealNetworkCombat:
    """
    Manages real network-based combat using actual PooScript execution.
    This is the TRUE hacker experience!
    """

    def __init__(self, player_ship_os, enemy_ship_os):
        self.player_os = player_ship_os
        self.enemy_os = enemy_ship_os

        # Active SSH connections
        self.active_connections: Dict[str, SSHConnection] = {}

        # Deployed malware (running scripts)
        self.running_malware: List[str] = []  # List of script paths

    def scan_target(self) -> Dict[str, any]:
        """
        Real network scan using actual port scanning.
        Returns what's actually running on enemy ship!
        """
        results = {
            "ip": self.enemy_os.ship.network_address if hasattr(self.enemy_os.ship, 'network_address') else "192.168.1.100",
            "ports": [],
            "vulnerabilities": [],
            "os_fingerprint": "ShipOS 1.0",
        }

        # Check what ports are actually open
        if hasattr(self.enemy_os.ship, 'network_ports'):
            for port, service in self.enemy_os.ship.network_ports.items():
                results["ports"].append({
                    "port": port,
                    "state": "open",
                    "service": service
                })

        # Check for real vulnerabilities
        # Look at system health - damaged systems are vulnerable
        if hasattr(self.enemy_os.ship, 'rooms'):
            for room in self.enemy_os.ship.rooms.values():
                if room.health < 100:
                    vuln_level = "CRITICAL" if room.health < 30 else "HIGH" if room.health < 70 else "MEDIUM"
                    results["vulnerabilities"].append({
                        "level": vuln_level,
                        "system": room.name,
                        "health": room.health,
                        "exploit": "buffer_overflow"
                    })

        # Check for weak passwords
        if hasattr(self.enemy_os, 'root_password'):
            if self.enemy_os.root_password in ["root", "admin", "password", "123456"]:
                results["vulnerabilities"].append({
                    "level": "CRITICAL",
                    "system": "SSH",
                    "exploit": "weak_password",
                    "description": "Weak root password detected"
                })

        return results

    def execute_exploit(self, exploit_type: str, target_system: str = None) -> Tuple[bool, str]:
        """
        Execute REAL exploit against enemy ShipOS.
        This actually runs exploit code against their OS!
        """
        if exploit_type == "buffer_overflow":
            return ExploitKit.buffer_overflow(self.enemy_os, target_system or "weapons")
        elif exploit_type == "sql_injection":
            return ExploitKit.sql_injection(self.enemy_os)
        elif exploit_type == "backdoor":
            return ExploitKit.backdoor_install(self.enemy_os)
        elif exploit_type == "dos":
            return ExploitKit.dos_attack(self.enemy_os, target_system or "shields")
        elif exploit_type == "privilege_escalation" or exploit_type == "priv_esc":
            return ExploitKit.privilege_escalation(self.enemy_os)
        elif exploit_type == "zero_day":
            return ExploitKit.zero_day_exploit(self.enemy_os, target_system or "weapons")
        else:
            return (False, f"Unknown exploit: {exploit_type}")

    def deploy_malware(self, malware_type: str, target_system: str = None) -> Tuple[bool, str]:
        """
        Deploy REAL malware - actual PooScript that executes!
        """
        # Get malware script
        if malware_type == "worm":
            script = MalwareScript.worm_script()
            script_path = "/tmp/.worm.poo"
        elif malware_type == "virus":
            script = MalwareScript.virus_script()
            script_path = "/tmp/.virus.poo"
        elif malware_type == "logic_bomb":
            script = MalwareScript.logic_bomb_script(target_system or "weapons")
            script_path = "/tmp/.logic_bomb.poo"
        elif malware_type == "rootkit":
            script = MalwareScript.rootkit_script()
            script_path = "/tmp/.rootkit.poo"
        else:
            return (False, f"Unknown malware type: {malware_type}")

        try:
            # Upload script to enemy ship
            self.enemy_os.vfs.write_file(script_path, script, 0)  # Write as root

            # Make executable
            # (In real system would chmod +x)

            # Execute the malware!
            exit_code, stdout, stderr = self.enemy_os.execute_command(f"pooscript {script_path}")

            self.running_malware.append(script_path)

            return (True, f"Malware deployed and executed!\nOutput:\n{stdout}")
        except Exception as e:
            return (False, f"Malware deployment failed: {e}")

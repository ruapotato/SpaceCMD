"""
ShipOS - Spaceship Operating System
Integrates Ship systems with Unix-like OS architecture
Mounts ship state into VFS for PooScript access
"""

from typing import Optional, Tuple
from core.system import UnixSystem
from core.ship import Ship, Room, SystemType


class ShipOS(UnixSystem):
    """
    Complete operating system for spaceship control
    Extends UnixSystem with ship-specific functionality
    All ship systems accessible via PooScript and virtual files
    """

    def __init__(self, ship: Ship, hostname: str = None):
        """
        Initialize ship operating system

        Args:
            ship: The ship to control
            hostname: OS hostname (defaults to ship name)
        """
        self.ship = ship

        # Use ship name as hostname if not provided
        if hostname is None:
            hostname = ship.name.lower().replace(' ', '-')

        # Initialize Unix system (no network for now - ship is isolated)
        super().__init__(hostname=hostname, ip_or_interfaces=None)

        # World interface (set by external world manager)
        self.world_manager = None  # Set by play.py

        # Mount ship systems into VFS
        self._mount_ship_systems()

        # Create ship control binaries
        self._create_ship_binaries()

        # Customize MOTD for ship
        self._create_ship_motd()

        # Add helpful README in /root/
        self._create_root_readme()

    def _create_ship_motd(self):
        """Create ship-specific MOTD"""
        motd = f"""
╔═══════════════════════════════════════════════════════════════╗
║                      {self.ship.name.upper()} SHIP OS                      ║
║                     {self.ship.ship_class.upper()} CLASS                    ║
╚═══════════════════════════════════════════════════════════════╝

  Welcome to the {self.ship.name} Operating System (ShipOS)

  All ship systems are controlled through device files:

    /dev/ship/         - Hardware devices (hull, shields, reactor)
    /proc/ship/        - Ship state (status, power, crew AI)
    /sys/ship/systems/ - Ship systems (engines, weapons, shields)
    /sys/ship/crew/    - Crew bot status (read-only)
    /sys/ship/rooms/   - Room status (oxygen, fire, venting)

  Crew are AUTONOMOUS BOTS that automatically handle:
    - System repairs
    - Fire suppression
    - Oxygen management
    - System operation

  Everything is a file. Everything is hackable.

  Available commands:
    ls /sys/ship/systems  - List all ship systems
    cat /dev/ship/hull    - Read hull integrity device
    cat /proc/ship/status - Show complete ship status
    power                 - Manage power allocation
    crew                  - View crew roster
    help                  - Show all available commands

  Combat commands (when in combat):
    weapons               - List weapons and status
    enemy                 - Show enemy ship systems
    target <system>       - Target enemy subsystem
    fire <weapon_num>     - Fire weapon at target

  Type 'help' for a complete command reference.
  All systems operational. Good luck, Captain!

═══════════════════════════════════════════════════════════════
""".encode('utf-8')
        self.vfs.write_file('/etc/motd', motd, 1)

    def _create_root_readme(self):
        """Create helpful README.md in /root/ directory"""
        import os
        readme_path = os.path.join(os.path.dirname(__file__), 'resources', 'root_readme.md')

        try:
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            self.vfs.write_file('/root/README.md', readme_content.encode('utf-8'), 1)
        except FileNotFoundError:
            # Fallback if resources file doesn't exist
            fallback_readme = """# Welcome to ShipOS!

Type 'help' to see available commands.
Type 'cat /etc/motd' to see the welcome message.

Try exploring:
- ls /dev/ship
- cat /proc/ship/status
- power

Good luck, Captain!
""".encode('utf-8')
            self.vfs.write_file('/root/README.md', fallback_readme, 1)

    def _mount_ship_systems(self):
        """Mount all ship systems as device files in /dev, /proc, /sys"""
        # Create device directories (like /dev/ship, /sys/ship, etc)
        dirs = [
            '/dev/ship',      # Device files for ship hardware
            '/proc/ship',     # Process-like files for ship state
            '/sys/ship/systems',  # Sysfs-like files for ship systems
            '/sys/ship/crew',     # Crew status
            '/sys/ship/rooms',    # Room status
        ]
        for path in dirs:
            parts = path.strip('/').split('/')
            current = ''
            for part in parts:
                current += '/' + part
                if not self.vfs.stat(current, 1):
                    self.vfs.mkdir(current, 0o755, 0, 0)

        # Mount ship-wide status to /dev/ship (hardware devices)
        self._mount_ship_devices()

        # Mount systems to /sys/ship/systems (sysfs-like)
        self._mount_systems_sysfs()

        # Mount crew to /sys/ship/crew
        self._mount_crew_sysfs()

        # Mount rooms to /sys/ship/rooms
        self._mount_rooms_sysfs()

        # Mount ship state to /proc/ship (process-like state)
        self._mount_ship_procfs()

    def _mount_ship_devices(self):
        """Mount ship hardware as device files in /dev/ship"""
        # These are actual hardware device files (like /dev/sda, /dev/tty)
        device_specs = [
            ('hull', lambda: f"{self.ship.hull}\n"),
            ('shields', lambda: f"{int(self.ship.shields)}\n"),
            ('reactor', lambda: f"{self.ship.reactor_power}\n"),
            ('fuel', lambda: f"{self.ship.fuel}\n"),
        ]

        for device_name, read_func in device_specs:
            device_path = f'/dev/ship/{device_name}'

            # Create device handler
            def make_handlers(rf):
                def read_handler(size):
                    data = rf()
                    return data.encode('utf-8')
                def write_handler(data):
                    return 0  # Read-only hardware
                return (read_handler, write_handler)

            handlers = make_handlers(read_func)
            self.vfs.device_handlers[f'dev_ship_{device_name}'] = handlers
            self.vfs.create_device(device_path, True, 0, 0, device_name=f'dev_ship_{device_name}')

    def _mount_ship_procfs(self):
        """Mount ship state to /proc/ship (like /proc/cpuinfo, /proc/meminfo)"""
        # /proc/ship/status - complete ship status
        def ship_status_read(size):
            status = f"""Ship: {self.ship.name}
Class: {self.ship.ship_class}
Hull: {self.ship.hull}/{self.ship.hull_max}
Shields: {int(self.ship.shields)}/{self.ship.shields_max}
Power: {self.ship.reactor_power - self.ship.power_available}/{self.ship.reactor_power}
Fuel: {self.ship.fuel}
Scrap: {self.ship.scrap}
Crew: {len(self.ship.crew)}
"""
            return status.encode('utf-8')

        self.vfs.device_handlers['proc_ship_status'] = (ship_status_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/status', True, 0, 0, device_name='proc_ship_status')

        # /proc/ship/power - power allocation info
        def power_info_read(size):
            info = f"Total: {self.ship.reactor_power}\n"
            info += f"Available: {self.ship.power_available}\n"
            info += f"Allocated: {self.ship.reactor_power - self.ship.power_available}\n"
            return info.encode('utf-8')

        self.vfs.device_handlers['proc_ship_power'] = (power_info_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/power', True, 0, 0, device_name='proc_ship_power')

        # /proc/ship/crew_ai - AI bot status
        def crew_ai_read(size):
            ai_status = "=== AUTONOMOUS CREW AI ===\n"
            for crew in self.ship.crew:
                location = crew.room.name if crew.room else "Unassigned"
                action = "Idle"

                # Determine what AI is doing
                if crew.room:
                    if crew.room.on_fire:
                        action = "Fighting fire"
                    elif crew.room.health < 1.0:
                        action = "Repairing system"
                    elif crew.room.oxygen_level < 0.8:
                        action = "Monitoring oxygen"
                    else:
                        action = "Operating system"

                ai_status += f"{crew.name:20} @ {location:15} - {action}\n"

            return ai_status.encode('utf-8')

        self.vfs.device_handlers['proc_ship_crew_ai'] = (crew_ai_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/crew_ai', True, 0, 0, device_name='proc_ship_crew_ai')

        # /proc/ship/combat - combat state info
        def combat_read(size):
            if not self.world_manager or not self.world_manager.is_in_combat():
                return b"No active combat\n"

            combat = self.world_manager.combat_state
            enemy = combat.enemy_ship

            info = f"""=== COMBAT STATUS ===
Enemy: {enemy.name}
Hull: {int(enemy.hull)}/{enemy.hull_max}
Shields: {int(enemy.shields)}/{enemy.shields_max}

Target: {combat.player_target if combat.player_target else 'None'}
Turn: {combat.turn}
"""
            return info.encode('utf-8')

        self.vfs.device_handlers['proc_ship_combat'] = (combat_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/combat', True, 0, 0, device_name='proc_ship_combat')

        # /proc/ship/weapons - weapons status
        def weapons_read(size):
            info = "=== WEAPONS ===\n"
            for i, weapon in enumerate(self.ship.weapons):
                status = "READY" if weapon.is_ready() else f"CHARGING ({weapon.charge:.0%})"
                info += f"{i+1}. {weapon.name:15} DMG:{weapon.damage} CD:{weapon.cooldown_time}s [{status}]\n"
            return info.encode('utf-8')

        self.vfs.device_handlers['proc_ship_weapons'] = (weapons_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/weapons', True, 0, 0, device_name='proc_ship_weapons')

        # /proc/ship/enemy - enemy ship details (rooms, systems)
        def enemy_read(size):
            if not self.world_manager or not self.world_manager.is_in_combat():
                return b"No enemy detected\n"

            enemy = self.world_manager.combat_state.enemy_ship
            info = f"""=== ENEMY: {enemy.name} ===
Hull: {int(enemy.hull)}/{enemy.hull_max}
Shields: {int(enemy.shields)}/{enemy.shields_max}

SYSTEMS:
"""
            for room_name, room in enemy.rooms.items():
                status = "OK" if room.health > 0.7 else "DMG" if room.health > 0.3 else "CRIT"
                system = room.system_type.value if room.system_type else "none"
                info += f"  {room_name:15} [{status}] {system:10} HP:{room.health:.0%}\n"

            return info.encode('utf-8')

        self.vfs.device_handlers['proc_ship_enemy'] = (enemy_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/enemy', True, 0, 0, device_name='proc_ship_enemy')

        # /dev/ship/beacon - distress beacon control (attracts enemies!)
        def beacon_read(size):
            if self.world_manager and self.world_manager.distress_beacon_active:
                return b"ACTIVE\n"
            return b"INACTIVE\n"

        def beacon_write(data):
            """Writing '1' activates beacon (attracts enemies!), '0' deactivates"""
            try:
                value = int(data.decode('utf-8').strip())
                if self.world_manager:
                    self.world_manager.set_distress_beacon(bool(value))
                return len(data)
            except:
                return -1

        self.vfs.device_handlers['dev_ship_beacon'] = (beacon_read, beacon_write)
        self.vfs.create_device('/dev/ship/beacon', True, 0, 0, device_name='dev_ship_beacon')

        # /dev/ship/target - set combat target (write room name)
        def target_read(size):
            if not self.world_manager or not self.world_manager.is_in_combat():
                return b"No combat active\n"
            target = self.world_manager.combat_state.player_target
            return f"{target}\n".encode('utf-8') if target else b"None\n"

        def target_write(data):
            """Write room name to target that system"""
            if not self.world_manager or not self.world_manager.is_in_combat():
                return -1

            try:
                room_name = data.decode('utf-8').strip()
                if self.world_manager.combat_state.set_target(room_name):
                    return len(data)
                return -1
            except:
                return -1

        self.vfs.device_handlers['dev_ship_target'] = (target_read, target_write)
        self.vfs.create_device('/dev/ship/target', True, 0, 0, device_name='dev_ship_target')

        # /dev/ship/fire - fire weapon (write weapon number 0-n)
        def fire_read(size):
            return b"Write weapon number (0-based) to fire\n"

        def fire_write(data):
            """Write weapon index to fire it"""
            if not self.world_manager or not self.world_manager.is_in_combat():
                return -1

            # Check if weapons system is functional
            weapons_room = None
            for room_name, room in self.ship.rooms.items():
                if room.system_type == SystemType.WEAPONS:
                    weapons_room = room
                    break

            if not weapons_room:
                return -1  # No weapons system!

            if not weapons_room.is_functional:
                # System damaged - write error to stderr (can't do that from device handler)
                # Return -1 to indicate error (will show as write error)
                return -1

            try:
                weapon_idx = int(data.decode('utf-8').strip())
                if self.world_manager.combat_state.fire_player_weapon(weapon_idx):
                    return len(data)
                return -1
            except:
                return -1

        self.vfs.device_handlers['dev_ship_fire'] = (fire_read, fire_write)
        self.vfs.create_device('/dev/ship/fire', True, 0, 0, device_name='dev_ship_fire')

        # /dev/ship/crew_assign - assign crew to rooms (write "crew_name room_name")
        def crew_assign_read(size):
            return b"Write 'crew_name room_name' to assign crew to a room\n"

        def crew_assign_write(data):
            """Write 'crew_name room_name' to assign a crew member to a room"""
            try:
                parts = data.decode('utf-8').strip().split()
                if len(parts) < 2:
                    return -1

                # Room name is last word (always single word like "Shields", "Weapons")
                # Crew name is everything before that (may have spaces like "Lieutenant Hayes")
                room_name = parts[-1]
                crew_name = ' '.join(parts[:-1])

                # Find the crew member
                crew_member = None
                for crew in self.ship.crew:
                    if crew.name == crew_name:
                        crew_member = crew
                        break

                if not crew_member:
                    return -1  # Crew not found

                # Find the room
                target_room = None
                for r_name, room in self.ship.rooms.items():
                    if r_name == room_name or (room.system_type and room.system_type.value == room_name.lower()):
                        target_room = room
                        break

                if not target_room:
                    return -1  # Room not found

                # Assign crew to room
                crew_member.assign_to_room(target_room)
                return len(data)

            except:
                return -1

        self.vfs.device_handlers['dev_ship_crew_assign'] = (crew_assign_read, crew_assign_write)
        self.vfs.create_device('/dev/ship/crew_assign', True, 0, 0, device_name='dev_ship_crew_assign')

        # /proc/ship/location - current map location
        def location_read(size):
            if not self.world_manager:
                return b"No navigation data\n"

            node = self.world_manager.world_map.get_current_node()
            if not node:
                return b"Unknown location\n"

            info = f"""=== CURRENT LOCATION ===
Node: {node.id}
Type: {node.type.value}
Sector: {node.sector + 1}/{self.world_manager.world_map.num_sectors}
Visited: {'Yes' if node.visited else 'No'}
"""
            return info.encode('utf-8')

        self.vfs.device_handlers['proc_ship_location'] = (location_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/location', True, 0, 0, device_name='proc_ship_location')

        # /proc/ship/jumps - available jump destinations
        def jumps_read(size):
            if not self.world_manager:
                return b"No navigation data\n"

            available = self.world_manager.get_available_jumps()
            if not available:
                return b"No jump destinations available\n"

            info = "=== AVAILABLE JUMPS ===\n"
            for node in available:
                visited = "VISITED" if node.visited else "UNVISITED"
                info += f"  {node.id:8} {node.type.value:12} Sector {node.sector + 1}  [{visited}]\n"

            return info.encode('utf-8')

        self.vfs.device_handlers['proc_ship_jumps'] = (jumps_read, lambda data: 0)
        self.vfs.create_device('/proc/ship/jumps', True, 0, 0, device_name='proc_ship_jumps')

        # /dev/ship/jump - execute jump (write node ID)
        def jump_write(data):
            """Write node ID to jump to that node"""
            if not self.world_manager:
                return -1

            try:
                node_id = data.decode('utf-8').strip()
                if self.world_manager.jump_to_node(node_id):
                    return len(data)
                return -1
            except:
                return -1

        self.vfs.device_handlers['dev_ship_jump'] = (lambda size: b"Write node ID to jump\n", jump_write)
        self.vfs.create_device('/dev/ship/jump', True, 0, 0, device_name='dev_ship_jump')

    def _mount_systems_sysfs(self):
        """Mount ship systems to /sys/ship/systems (like /sys/class/net)"""
        for room_name, room in self.ship.rooms.items():
            if room.system_type == SystemType.NONE:
                continue

            system_name = room.system_type.value
            system_dir = f'/sys/ship/systems/{system_name}'

            # Create system directory
            self.vfs.mkdir(system_dir, 0o755, 0, 0)

            # Create sysfs-like attribute files for this system
            self._create_system_sysfs(system_dir, room)

    def _create_system_sysfs(self, system_dir: str, room: Room):
        """Create sysfs attribute files for a ship system"""
        # Status file
        def status_read():
            status = "ONLINE" if room.is_functional else "OFFLINE"
            return f"{room.name}: {status} HP:{room.health:.0%} PWR:{room.power_allocated}/{room.max_power}\n"

        def status_write(data):
            return 0

        self.vfs.device_handlers[f'sys_{room.system_type.value}_status'] = (
            lambda size, r=status_read: r().encode('utf-8'),
            lambda data: 0
        )
        self.vfs.create_device(f'{system_dir}/status', True, 0, 0,
                              device_name=f'sys_{room.system_type.value}_status')

        # Power file (read/write)
        def power_read():
            return f"{room.power_allocated}\n"

        def power_write(data):
            try:
                value = data.decode('utf-8').strip()
                amount = int(value)
                current = room.power_allocated
                delta = amount - current

                if delta > 0 and delta > self.ship.power_available:
                    return -1  # Not enough power

                if amount > room.max_power:
                    amount = room.max_power

                room.power_allocated = amount
                self.ship.power_available -= delta
                return len(data)
            except:
                return -1

        self.vfs.device_handlers[f'sys_{room.system_type.value}_power'] = (
            lambda size, r=power_read: r().encode('utf-8'),
            power_write
        )
        self.vfs.create_device(f'{system_dir}/power', True, 0, 0,
                              device_name=f'sys_{room.system_type.value}_power')

        # Health file (read-only)
        def health_read():
            return f"{room.health:.2f}\n"

        self.vfs.device_handlers[f'sys_{room.system_type.value}_health'] = (
            lambda size, r=health_read: r().encode('utf-8'),
            lambda data: 0
        )
        self.vfs.create_device(f'{system_dir}/health', True, 0, 0,
                              device_name=f'sys_{room.system_type.value}_health')

    def _mount_crew_sysfs(self):
        """Mount crew to /sys/ship/crew"""
        for crew in self.ship.crew:
            crew_name_safe = crew.name.lower().replace(' ', '_')
            crew_dir = f'/sys/ship/crew/{crew_name_safe}'

            # Create crew directory
            self.vfs.mkdir(crew_dir, 0o755, 0, 0)

            # Create sysfs-like crew attribute files
            self._create_crew_sysfs(crew_dir, crew)

    def _create_crew_sysfs(self, crew_dir: str, crew):
        """Create sysfs attribute files for a crew member"""
        crew_name_safe = crew.name.lower().replace(' ', '_')

        # Name
        self.vfs.device_handlers[f'crew_{crew_name_safe}_name'] = (
            lambda size, c=crew: c.name.encode('utf-8'),
            lambda data: 0
        )
        self.vfs.create_device(f'{crew_dir}/name', True, 0, 0,
                              device_name=f'crew_{crew_name_safe}_name')

        # Race
        self.vfs.device_handlers[f'crew_{crew_name_safe}_race'] = (
            lambda size, c=crew: c.race.encode('utf-8'),
            lambda data: 0
        )
        self.vfs.create_device(f'{crew_dir}/race', True, 0, 0,
                              device_name=f'crew_{crew_name_safe}_race')

        # Health
        self.vfs.device_handlers[f'crew_{crew_name_safe}_health'] = (
            lambda size, c=crew: f"{int(c.health)}\n".encode('utf-8'),
            lambda data: 0
        )
        self.vfs.create_device(f'{crew_dir}/health', True, 0, 0,
                              device_name=f'crew_{crew_name_safe}_health')

        # Location
        self.vfs.device_handlers[f'crew_{crew_name_safe}_location'] = (
            lambda size, c=crew: (c.room.name if c.room else 'None').encode('utf-8') + b'\n',
            lambda data: 0
        )
        self.vfs.create_device(f'{crew_dir}/location', True, 0, 0,
                              device_name=f'crew_{crew_name_safe}_location')

    def _mount_rooms_sysfs(self):
        """Mount rooms to /sys/ship/rooms"""
        for room_name, room in self.ship.rooms.items():
            room_name_safe = room_name.lower().replace(' ', '_')
            room_dir = f'/sys/ship/rooms/{room_name_safe}'

            # Create room directory
            self.vfs.mkdir(room_dir, 0o755, 0, 0)

            # Create sysfs-like room attribute files
            self._create_room_sysfs(room_dir, room)

    def _create_room_sysfs(self, room_dir: str, room: Room):
        """Create sysfs attribute files for a room"""
        room_name_safe = room.name.lower().replace(' ', '_')

        # Oxygen
        self.vfs.device_handlers[f'room_{room_name_safe}_oxygen'] = (
            lambda size, r=room: f"{r.oxygen_level:.2f}\n".encode('utf-8'),
            lambda data: 0
        )
        self.vfs.create_device(f'{room_dir}/oxygen', True, 0, 0,
                              device_name=f'room_{room_name_safe}_oxygen')

        # Fire
        self.vfs.device_handlers[f'room_{room_name_safe}_fire'] = (
            lambda size, r=room: b'1\n' if r.on_fire else b'0\n',
            lambda data: 0
        )
        self.vfs.create_device(f'{room_dir}/fire', True, 0, 0,
                              device_name=f'room_{room_name_safe}_fire')

        # Breach
        self.vfs.device_handlers[f'room_{room_name_safe}_breach'] = (
            lambda size, r=room: b'1\n' if r.breached else b'0\n',
            lambda data: 0
        )
        self.vfs.create_device(f'{room_dir}/breach', True, 0, 0,
                              device_name=f'room_{room_name_safe}_breach')

        # Venting (read/write)
        def vent_write(data):
            try:
                value = int(data.decode('utf-8').strip())
                room.venting = bool(value)
                return len(data)
            except:
                return -1

        self.vfs.device_handlers[f'room_{room_name_safe}_venting'] = (
            lambda size, r=room: b'1\n' if r.venting else b'0\n',
            vent_write
        )
        self.vfs.create_device(f'{room_dir}/venting', True, 0, 0,
                              device_name=f'room_{room_name_safe}_venting')

    def _create_ship_binaries(self):
        """Create PooScript binaries for ship control"""
        # NOTE: These old built-in scripts are kept for compatibility
        # The actual commands are now in scripts/bin/ and use kernel syscalls
        # These will be overwritten by scripts/bin/ during install_scripts()

        # Ensure /tmp exists
        if not self.vfs.stat('/tmp', 1):
            self.vfs.mkdir('/tmp', 0o777, 0, 0, 1)

        # Create a hostile script as a tutorial/easter egg
        hostile_script = """#!/usr/bin/pooscript
# HOSTILE MALWARE - DO NOT RUN!
# This script activates the distress beacon, attracting enemies!
# (Tutorial: demonstrates hostile code execution)

print("⚠️  WARNING: EXECUTING HOSTILE CODE...")
print("🔓 Accessing ship systems...")
sleep(0.5)
print("📡 ACTIVATING DISTRESS BEACON...")
sleep(0.5)

# Activate the distress beacon - this will attract enemies!
vfs.write('/dev/ship/beacon', '1')

print("🔴 DISTRESS BEACON ACTIVE!")
print("⚠️  WARNING: This will attract hostile ships!")
print("")
print("The world will spawn enemies when beacon is active!")
print("To deactivate: echo 0 > /dev/ship/beacon")
print("")
print("Check beacon status: cat /dev/ship/beacon")
print("Check ship status: cat /proc/ship/status")
"""
        # Create the hostile script in /tmp (world-readable and executable)
        self.vfs.create_file('/tmp/hostile.poo', 0o755, 0, 0, hostile_script.encode('utf-8'), 1)

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command in the ship's OS shell
        Returns (exit_code, stdout, stderr) as strings
        """
        if self.shell_pid is None:
            # Auto-login as root if no shell process
            self.login('root', 'root')

        exit_code, stdout, stderr = self.shell.execute(command, self.shell_pid)
        return exit_code, stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore')

    def update_ship_state(self, delta_time: float):
        """
        Update ship state (physics only - combat handled by WorldManager)
        Called by game loop
        """
        # Update ship physics (crew movement, oxygen, etc)
        self.ship.update(delta_time)

        # Virtual device files automatically reflect new state
        # No need to manually update VFS

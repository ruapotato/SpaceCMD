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

        # Mount ship systems into VFS
        self._mount_ship_systems()

        # Create ship control binaries
        self._create_ship_binaries()

        # Customize MOTD for ship
        self._create_ship_motd()

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
    /proc/ship/        - Ship state (status, power info)
    /sys/ship/systems/ - Ship systems (engines, weapons, shields)
    /sys/ship/crew/    - Crew member status
    /sys/ship/rooms/   - Room status (oxygen, fire, venting)

  Everything is a file. Everything is hackable.

  Available commands:
    ls /sys/ship/systems  - List all ship systems
    cat /dev/ship/hull    - Read hull integrity device
    cat /proc/ship/status - Show complete ship status
    power                 - Manage power allocation
    crew                  - View crew roster
    help                  - Show all available commands

  Type 'help' for a complete command reference.
  All systems operational. Good luck, Captain!

═══════════════════════════════════════════════════════════════
""".encode('utf-8')
        self.vfs.write_file('/etc/motd', motd, 1)

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

        # /bin/status - Complete ship status
        status_script = '''#!/usr/bin/pooscript
# Display complete ship status

hull = vfs.read("/ship/hull").strip()
hull_max = vfs.read("/ship/hull_max").strip()
shields = vfs.read("/ship/shields").strip()
shields_max = vfs.read("/ship/shields_max").strip()
fuel = vfs.read("/ship/fuel").strip()
scrap = vfs.read("/ship/scrap").strip()
power_avail = vfs.read("/ship/power_available").strip()
power_total = vfs.read("/ship/power_total").strip()

print("=" * 60)
print(f"=== {vfs.read('/ship/name').strip().upper()} ({vfs.read('/ship/class').strip().upper()}) ===")
print("=" * 60)
print(f"Hull:    {hull}/{hull_max}")
print(f"Shields: {shields}/{shields_max}")
print(f"Power:   {int(power_total) - int(power_avail)}/{power_total} ({power_avail} available)")
print(f"Fuel:    {fuel}")
print(f"Scrap:   {scrap}")
print("=" * 60)
'''.encode('utf-8')

        # /bin/systems - List all systems
        systems_script = '''#!/usr/bin/pooscript
# List all ship systems

print("=" * 60)
print("SHIP SYSTEMS")
print("=" * 60)

systems = vfs.list("/systems")
for system in systems:
    if system in [".", ".."]:
        continue
    status = vfs.read(f"/systems/{system}/status").strip()
    print(f"  {status}")

print("=" * 60)
'''.encode('utf-8')

        # /bin/crew - Crew roster
        crew_script = '''#!/usr/bin/pooscript
# Display crew roster

print("=" * 60)
print("CREW ROSTER")
print("=" * 60)

crew_list = vfs.list("/crew")
for crew_member in crew_list:
    if crew_member in [".", ".."]:
        continue
    name = vfs.read(f"/crew/{crew_member}/name").strip()
    race = vfs.read(f"/crew/{crew_member}/race").strip()
    health = vfs.read(f"/crew/{crew_member}/health").strip()
    location = vfs.read(f"/crew/{crew_member}/location").strip()

    # Health status
    health_val = int(health)
    if health_val > 70:
        status = "HEALTHY"
    elif health_val > 30:
        status = "INJURED"
    else:
        status = "CRITICAL"

    print(f"{name:20} ({race:8}) HP:{health:>3}/{100} [{status:8}] @ {location}")

print("=" * 60)
'''.encode('utf-8')

        # /bin/power - Power management
        power_script = '''#!/usr/bin/pooscript
# Power allocation utility

if len(args) == 0:
    # Show power usage
    print("=" * 60)
    print("POWER ALLOCATION")
    print("=" * 60)

    systems = vfs.list("/systems")
    for system in systems:
        if system in [".", ".."]:
            continue
        power = vfs.read(f"/systems/{system}/power").strip()
        health = vfs.read(f"/systems/{system}/health").strip()
        health_pct = int(float(health) * 100)
        print(f"  {system:12} PWR:{power:1} HP:{health_pct:3}%")

    avail = vfs.read("/ship/power_available").strip()
    total = vfs.read("/ship/power_total").strip()
    print("=" * 60)
    print(f"  Available: {avail}/{total}")
    print("=" * 60)

elif len(args) >= 2:
    # Set power
    system = args[0]
    amount = args[1]

    try:
        vfs.write(f"/systems/{system}/power", amount)
        print(f"Set {system} power to {amount}")
    except Exception as e:
        error(f"Failed to set power: {e}")
        exit(1)
else:
    error("Usage: power [system] [amount]")
    error("       power          - show current allocation")
    exit(1)
'''.encode('utf-8')

        # /bin/rooms - Room status
        rooms_script = '''#!/usr/bin/pooscript
# Display room status

print("=" * 60)
print("ROOM STATUS")
print("=" * 60)

rooms = vfs.list("/rooms")
for room in rooms:
    if room in [".", ".."]:
        continue

    oxygen = vfs.read(f"/rooms/{room}/oxygen").strip()
    fire = vfs.read(f"/rooms/{room}/fire").strip()
    breach = vfs.read(f"/rooms/{room}/breach").strip()
    venting = vfs.read(f"/rooms/{room}/venting").strip()

    oxygen_pct = int(float(oxygen) * 100)

    # Status indicators
    indicators = []
    if fire == "1":
        indicators.append("FIRE!")
    if breach == "1":
        indicators.append("BREACH!")
    if venting == "1":
        indicators.append("VENTING!")

    status_str = " ".join(indicators) if indicators else "OK"

    print(f"{room:15} O2:{oxygen_pct:3}% {status_str}")

print("=" * 60)
'''.encode('utf-8')

        # /bin/vent - Toggle room venting
        vent_script = '''#!/usr/bin/pooscript
# Toggle room venting

if len(args) < 1:
    error("Usage: vent <room_name>")
    error("Example: vent helm")
    exit(1)

room = args[0]
room_path = f"/rooms/{room}/venting"

try:
    current = int(vfs.read(room_path).strip())
    new_value = "0" if current == 1 else "1"
    vfs.write(room_path, new_value)

    if new_value == "1":
        print(f"Opening airlocks in {room} - VENTING!")
    else:
        print(f"Closing airlocks in {room}")
except Exception as e:
    error(f"Failed to toggle venting: {e}")
    error(f"Available rooms: {' '.join([r for r in vfs.list('/rooms') if r not in ['.', '..']])}")
    exit(1)
'''.encode('utf-8')

        # /bin/wait - Wait/advance time
        wait_script = '''#!/usr/bin/pooscript
# Wait for time to pass (game time advancement)

duration = 1.0
if len(args) > 0:
    try:
        duration = float(args[0])
    except:
        error("Usage: wait [seconds]")
        exit(1)

print(f"Waiting {duration} seconds...")
# Note: actual time advancement happens in game loop
# This command just reports the wait
'''.encode('utf-8')

        # Write all binaries
        binaries = {
            '/bin/status': status_script,
            '/bin/systems': systems_script,
            '/bin/crew': crew_script,
            '/bin/power': power_script,
            '/bin/rooms': rooms_script,
            '/bin/vent': vent_script,
            '/bin/wait': wait_script,
        }

        for path, script in binaries.items():
            # Create file with executable permissions
            self.vfs.create_file(path, 0o755, 0, 0, script, 1)

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
        Update ship state (physics, combat, etc)
        Called by game loop
        """
        # This will call ship.update() to advance ship physics
        self.ship.update(delta_time)

        # Virtual device files automatically reflect new state
        # No need to manually update VFS

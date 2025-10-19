"""
spacecmd - Ship Operating System Integration

Mounts ship state into the VFS as virtual device files.
Allows PooScript access to all ship systems.
"""

from typing import Optional
from .ship import Ship, Room, Crew, SystemType


class ShipOSBridge:
    """
    Bridge between Ship class and VFS.
    Mounts ship state as virtual files in /systems/, /crew/, /ship/, etc.
    """

    def __init__(self, ship: Ship, system: 'System'):
        self.ship = ship
        self.system = system
        self.vfs = system.vfs

    def mount_ship(self):
        """Mount all ship systems into VFS"""
        # Create directory structure
        self._create_directories()

        # Mount systems
        self._mount_systems()

        # Mount crew
        self._mount_crew()

        # Mount ship-wide status
        self._mount_ship_status()

        # Mount rooms
        self._mount_rooms()

    def _create_directories(self):
        """Create VFS directory structure for ship"""
        dirs = [
            '/systems',
            '/crew',
            '/ship',
            '/rooms',
            '/combat',
            '/navigation',
        ]

        for dir_path in dirs:
            try:
                self.vfs.create_dir(dir_path, 1)
            except:
                pass  # Dir might exist

    def _mount_systems(self):
        """Mount ship systems as virtual files"""
        for room_name, room in self.ship.rooms.items():
            if room.system_type == SystemType.NONE:
                continue

            system_name = room.system_type.value
            system_path = f'/systems/{system_name}'

            # Create system directory
            try:
                self.vfs.create_dir(system_path, 1)
            except:
                pass

            # Create virtual files for this system
            self._create_virtual_file(f'{system_path}/status',
                                     lambda r=room: self._get_system_status(r))
            self._create_virtual_file(f'{system_path}/power',
                                     lambda r=room: str(r.power_allocated),
                                     lambda v, r=room: self._set_power(r, v))
            self._create_virtual_file(f'{system_path}/health',
                                     lambda r=room: f'{r.health:.2f}')
            self._create_virtual_file(f'{system_path}/crew',
                                     lambda r=room: '\\n'.join(c.name for c in r.crew))

    def _mount_crew(self):
        """Mount crew members as virtual files"""
        for crew in self.ship.crew:
            crew_path = f'/crew/{crew.name.lower().replace(" ", "_")}'

            # Create crew directory
            try:
                self.vfs.create_dir(crew_path, 1)
            except:
                pass

            # Create crew files
            self._create_virtual_file(f'{crew_path}/name',
                                     lambda c=crew: c.name)
            self._create_virtual_file(f'{crew_path}/race',
                                     lambda c=crew: c.race)
            self._create_virtual_file(f'{crew_path}/health',
                                     lambda c=crew: str(int(c.health)))
            self._create_virtual_file(f'{crew_path}/location',
                                     lambda c=crew: c.room.name if c.room else 'None')
            self._create_virtual_file(f'{crew_path}/assign',
                                     lambda c=crew: c.room.name if c.room else 'None',
                                     lambda v, c=crew: self._assign_crew(c, v))

    def _mount_ship_status(self):
        """Mount ship-wide status files"""
        self._create_virtual_file('/ship/hull',
                                 lambda: str(self.ship.hull))
        self._create_virtual_file('/ship/hull_max',
                                 lambda: str(self.ship.hull_max))
        self._create_virtual_file('/ship/shields',
                                 lambda: str(int(self.ship.shields)))
        self._create_virtual_file('/ship/shields_max',
                                 lambda: str(self.ship.shields_max))
        self._create_virtual_file('/ship/fuel',
                                 lambda: str(self.ship.dark_matter))
        self._create_virtual_file('/ship/scrap',
                                 lambda: str(self.ship.scrap))
        self._create_virtual_file('/ship/power_available',
                                 lambda: str(self.ship.power_available))
        self._create_virtual_file('/ship/power_total',
                                 lambda: str(self.ship.reactor_power))

    def _mount_rooms(self):
        """Mount room status files"""
        for room_name, room in self.ship.rooms.items():
            room_path = f'/rooms/{room_name.lower().replace(" ", "_")}'

            # Create room directory
            try:
                self.vfs.create_dir(room_path, 1)
            except:
                pass

            # Create room files
            self._create_virtual_file(f'{room_path}/oxygen',
                                     lambda r=room: f'{r.oxygen_level:.2f}')
            self._create_virtual_file(f'{room_path}/fire',
                                     lambda r=room: '1' if r.on_fire else '0')
            self._create_virtual_file(f'{room_path}/breach',
                                     lambda r=room: '1' if r.breached else '0')
            self._create_virtual_file(f'{room_path}/vent',
                                     lambda r=room: '1' if r.venting else '0',
                                     lambda v, r=room: self._set_vent(r, v))
            self._create_virtual_file(f'{room_path}/crew',
                                     lambda r=room: '\\n'.join(c.name for c in r.crew))

    def _create_virtual_file(self, path: str, read_func, write_func=None):
        """
        Create a virtual file that reads/writes ship state.
        read_func() returns file contents
        write_func(value) handles writes
        """
        # For now, create regular files
        # TODO: Implement true virtual files with callbacks
        try:
            content = read_func()
            self.vfs.write_file(path, content.encode('utf-8'), 1)
        except Exception as e:
            # File might not be creatable yet
            pass

    def update_all_files(self):
        """Update all virtual files with current ship state"""
        # Refresh all virtual files
        # This should be called after ship state changes
        self._mount_systems()
        self._mount_crew()
        self._mount_ship_status()
        self._mount_rooms()

    # Helper methods for write operations

    def _get_system_status(self, room: Room) -> str:
        """Get human-readable system status"""
        status = "ONLINE" if room.is_functional else "OFFLINE"
        return f"{room.name}: {status} HP:{room.health:.0%} PWR:{room.power_allocated}/{room.max_power}"

    def _set_power(self, room: Room, value: str):
        """Set power allocation for a system"""
        try:
            amount = int(value.strip())
            current = room.power_allocated
            delta = amount - current

            if delta > 0 and delta > self.ship.power_available:
                raise ValueError(f"Not enough power (need {delta}, have {self.ship.power_available})")

            if amount > room.max_power:
                amount = room.max_power

            room.power_allocated = amount
            self.ship.power_available -= delta

        except ValueError as e:
            raise ValueError(f"Invalid power value: {value}")

    def _assign_crew(self, crew: Crew, room_name: str):
        """Assign crew member to a room"""
        room_name = room_name.strip().lower()

        # Find room
        for room in self.ship.rooms.values():
            if room.name.lower() == room_name or room.name.lower().replace(" ", "_") == room_name:
                crew.assign_to_room(room)
                return

        raise ValueError(f"Room not found: {room_name}")

    def _set_vent(self, room: Room, value: str):
        """Set room venting state"""
        try:
            vent = bool(int(value.strip()))
            room.venting = vent
        except:
            raise ValueError(f"Invalid vent value: {value} (use 0 or 1)")


def create_ship_binaries(system: 'System', ship: Ship):
    """
    Create ship command binaries in /bin/
    These are PooScript programs for ship operations
    """

    # /bin/status - Display ship status
    status_script = '''#!/usr/bin/pooscript
# Ship status display

hull = vfs.read("/ship/hull")
hull_max = vfs.read("/ship/hull_max")
shields = vfs.read("/ship/shields")
shields_max = vfs.read("/ship/shields_max")
power_used = vfs.read("/ship/power_total") - vfs.read("/ship/power_available")
power_total = vfs.read("/ship/power_total")
fuel = vfs.read("/ship/fuel")

print("=" * 60)
print("SHIP STATUS")
print("=" * 60)
print(f"Hull:    {hull}/{hull_max}")
print(f"Shields: {shields}/{shields_max}")
print(f"Power:   {power_used}/{power_total}")
print(f"Dark Matter:    {fuel}")
print("=" * 60)
'''

    # /bin/systems - List all systems
    systems_script = '''#!/usr/bin/pooscript
# List all ship systems

print("SHIP SYSTEMS:")
print("-" * 60)

systems = vfs.list("/systems")
for system in systems:
    if system in [".", ".."]:
        continue
    status = vfs.read(f"/systems/{system}/status")
    print(f"  {status}")
'''

    # /bin/crew - Crew roster
    crew_script = '''#!/usr/bin/pooscript
# Crew roster

print("CREW ROSTER:")
print("-" * 60)

crew_list = vfs.list("/crew")
for crew in crew_list:
    if crew in [".", ".."]:
        continue
    name = vfs.read(f"/crew/{crew}/name")
    health = vfs.read(f"/crew/{crew}/health")
    location = vfs.read(f"/crew/{crew}/location")
    print(f"  {name:20} HP:{health:>3} @ {location}")
'''

    # /bin/power - Power management
    power_script = '''#!/usr/bin/pooscript
# Power allocation utility

if len(args) == 0:
    # Show power usage
    print("POWER ALLOCATION:")
    print("-" * 60)
    systems = vfs.list("/systems")
    for system in systems:
        if system in [".", ".."]:
            continue
        power = vfs.read(f"/systems/{system}/power")
        print(f"  {system:12} {power} bars")

    avail = vfs.read("/ship/power_available")
    total = vfs.read("/ship/power_total")
    print("-" * 60)
    print(f"  Available: {avail}/{total}")

elif len(args) >= 2:
    # Set power
    system = args[0]
    amount = args[1]
    vfs.write(f"/systems/{system}/power", amount)
    print(f"Set {system} power to {amount}")
else:
    print("Usage: power [system] [amount]")
    print("       power          - show current allocation")
'''

    # Write binaries
    binaries = {
        '/bin/status': status_script,
        '/bin/systems': systems_script,
        '/bin/crew': crew_script,
        '/bin/power': power_script,
    }

    for path, script in binaries.items():
        system.vfs.write_file(path, script.encode('utf-8'), 1)
        # Make executable
        try:
            inode = system.vfs._resolve_path(path, 1)
            if inode:
                system.vfs.inodes[inode]['mode'] |= 0o111  # Add execute permission
        except:
            # File creation might fail, that's OK
            pass

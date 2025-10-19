#!/usr/bin/env python3
"""Test combat commands - with debugging"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager

print("=" * 60)
print("COMBAT COMMANDS DEBUG TEST")
print("=" * 60)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print("\nChecking if scripts are installed:")
exit_code, stdout, stderr = ship_os.execute_command("ls /bin")
print(f"/bin contents:\n{stdout}")

print("\nChecking combat scripts specifically:")
for cmd in ['weapons', 'enemy', 'target', 'fire', 'combat']:
    exit_code, stdout, stderr = ship_os.execute_command(f"ls -la /bin/{cmd}")
    print(f"{cmd}: {stdout.strip() if stdout else 'NOT FOUND'}")

print("\nTesting direct file read:")
exit_code, stdout, stderr = ship_os.execute_command("cat /bin/weapons | head -5")
print(f"First 5 lines of /bin/weapons:\n{stdout}")

print("\nStarting combat...")
success = world_manager.trigger_encounter("gnat", forced=True)

if success:
    print("✓ Combat started")

    # Check device files exist
    print("\nChecking device files:")
    for path in ['/proc/ship/combat', '/proc/ship/weapons', '/proc/ship/enemy',
                 '/dev/ship/target', '/dev/ship/fire']:
        exit_code, stdout, stderr = ship_os.execute_command(f"ls -la {path}")
        print(f"{path}: {stdout.strip() if stdout else 'NOT FOUND'}")

    # Try direct device file reads
    print("\n Testing direct device reads:")
    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/weapons")
    print(f"cat /proc/ship/weapons:\n{stdout}")

    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/enemy")
    print(f"\ncat /proc/ship/enemy:\n{stdout}")

    exit_code, stdout, stderr = ship_os.execute_command("cat /proc/ship/combat")
    print(f"\ncat /proc/ship/combat:\n{stdout}")

    # Now try the commands
    print("\n" + "=" * 60)
    print("Testing actual commands:")
    print("=" * 60)

    exit_code, stdout, stderr = ship_os.execute_command("weapons")
    print(f"\nweapons command (exit={exit_code}):")
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")

    exit_code, stdout, stderr = ship_os.execute_command("enemy")
    print(f"\nenemy command (exit={exit_code}):")
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")

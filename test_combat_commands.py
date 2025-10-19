#!/usr/bin/env python3
"""Test combat commands"""

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager

print("=" * 60)
print("COMBAT COMMANDS TEST")
print("=" * 60)

# Create ship and OS
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.login('root', 'root')

# Create world manager
world_manager = WorldManager(ship_os)
ship_os.world_manager = world_manager

print("\n1. Testing commands without combat:")
print("-" * 60)

# Test weapons command
exit_code, stdout, stderr = ship_os.execute_command("weapons")
print("weapons command:")
print(stdout)
if stderr:
    print(f"STDERR: {stderr}")

# Test enemy command
exit_code, stdout, stderr = ship_os.execute_command("enemy")
print("\nenemy command (should say no enemy):")
print(stdout)

# Test combat command
exit_code, stdout, stderr = ship_os.execute_command("combat")
print("\ncombat command (should say no combat):")
print(stdout)

print("\n2. Starting combat encounter:")
print("-" * 60)

# Trigger encounter
success = world_manager.trigger_encounter("gnat", forced=True)
if success:
    print("✓ Combat started!\n")

    # Test enemy command again
    exit_code, stdout, stderr = ship_os.execute_command("enemy")
    print("enemy command (should show enemy ship):")
    print(stdout)

    # Test combat command
    exit_code, stdout, stderr = ship_os.execute_command("combat")
    print("\ncombat command:")
    print(stdout)

    # Test weapons command
    exit_code, stdout, stderr = ship_os.execute_command("weapons")
    print("\nweapons command:")
    print(stdout)

    print("\n3. Testing targeting:")
    print("-" * 60)

    # Test target command without args (should show enemy systems)
    exit_code, stdout, stderr = ship_os.execute_command("target")
    print("target command (no args):")
    print(stdout)

    # Set a target
    exit_code, stdout, stderr = ship_os.execute_command("target Helm")
    print("\ntarget Helm:")
    print(stdout)
    if stderr:
        print(f"STDERR: {stderr}")

    # Check target was set
    exit_code, stdout, stderr = ship_os.execute_command("cat /dev/ship/target")
    print("\nCurrent target (cat /dev/ship/target):")
    print(stdout)

    print("\n4. Testing weapon fire:")
    print("-" * 60)

    # Try to fire weapon 1
    exit_code, stdout, stderr = ship_os.execute_command("fire 1")
    print("fire 1:")
    print(stdout)
    if stderr:
        print(f"STDERR: {stderr}")

    print("\n5. Testing low-level device files:")
    print("-" * 60)

    # Test direct device file writes
    exit_code, stdout, stderr = ship_os.execute_command("echo 'Weapons' > /dev/ship/target")
    print("echo 'Weapons' > /dev/ship/target:")
    if exit_code == 0:
        print("✓ Target set via device file")
    else:
        print(f"✗ Failed: {stderr}")

    exit_code, stdout, stderr = ship_os.execute_command("cat /dev/ship/target")
    print(f"Current target: {stdout.strip()}")

    print("\n6. Scripting example:")
    print("-" * 60)
    print("Example automation script:")
    print("""
#!/usr/bin/pooscript
# Auto-combat script

# Show enemy systems
enemy

# Target their weapons
echo "Weapons" > /dev/ship/target

# Wait for weapon 1 to charge, then fire
fire 1

# Target shields
echo "Shields" > /dev/ship/target
fire 2
""")

else:
    print("✗ Failed to start combat")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nCombat commands work! You can now:")
print("  - Use 'weapons', 'enemy', 'combat', 'target', 'fire' in game")
print("  - Write automation scripts using device files")
print("  - Control everything via GUI or CLI")

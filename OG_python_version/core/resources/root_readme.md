# Welcome to ShipOS!

You are now logged into the ship's operating system. Everything you see here is real - this is a complete Unix-like operating system running your spacecraft.

## Quick Start Guide

### Basic Commands

```bash
ls              # List files in current directory
pwd             # Print working directory
cd /proc/ship   # Change to ship status directory
cat <file>      # Display file contents
touch <file>    # Create empty file
mkdir <dir>     # Create directory
```

### Ship Status

All ship systems are exposed as virtual device files:

```bash
# View ship hardware status
cat /dev/ship/hull      # Hull integrity
cat /dev/ship/shields   # Shield levels
cat /dev/ship/reactor   # Reactor power
cat /dev/ship/fuel      # Fuel remaining

# View ship information
cat /proc/ship/status   # Complete ship status
cat /proc/ship/power    # Power allocation
cat /proc/ship/crew_ai  # Crew AI bot status
```

### Ship Systems

Control systems via `/sys/ship/systems/`:

```bash
# List all ship systems
ls /sys/ship/systems

# Check a specific system
cat /sys/ship/systems/weapons/status
cat /sys/ship/systems/weapons/power
cat /sys/ship/systems/weapons/health

# Available systems (ship dependent):
# - weapons
# - shields
# - engines
# - oxygen
# - medbay
```

### Ship Commands

High-level commands for ship operations:

```bash
status          # Show complete ship status
power           # View/adjust power allocation
power weapons 3 # Set weapons power to 3
crew            # View crew roster
systems         # List all systems
help            # Show all available commands
```

### File System Layout

```
/               Root directory
├── bin/        Command binaries (PoohScript)
├── dev/        Device files (ship hardware)
│   └── ship/   Ship hardware devices
├── etc/        Configuration files
│   ├── passwd  User database
│   └── motd    Message of the day
├── home/       User home directories
├── proc/       Process/ship state (virtual)
│   └── ship/   Ship status files
├── root/       Root user home
├── sys/        System information (virtual)
│   └── ship/   Ship systems/crew/rooms
├── tmp/        Temporary files
└── usr/        User programs
    └── local/  Local installations
```

## Understanding Virtual Devices

ShipOS uses a Unix-like device file system:

- **/dev/** - Hardware devices (read-only)
- **/proc/** - Dynamic ship state
- **/sys/** - Sysfs-like structured data (some writable)

Example - changing shield power:

```bash
# Read current power
cat /sys/ship/systems/shields/power

# Write new power level
echo 4 > /sys/ship/systems/shields/power

# Or use the high-level command
power shields 4
```

## Autonomous Crew AI

Your crew are autonomous bots that handle ship operations automatically:

```bash
# View what crew AI is doing
cat /proc/ship/crew_ai

# Check individual crew member
ls /sys/ship/crew/
cat /sys/ship/crew/bot1/health
cat /sys/ship/crew/bot1/location
```

Crew bots automatically:
- Repair damaged systems
- Fight fires
- Monitor oxygen
- Operate systems

## PoohScript

All commands are written in **PoohScript** - a real scripting language.

```bash
# View command source code
cat /bin/status
cat /bin/power

# Write your own script
cat > /tmp/test.ps <<'EOF'
#!/usr/bin/pooscript
# Read hull integrity
hull_fd = kernel.open("/dev/ship/hull", kernel.O_RDONLY)
hull = kernel.read(hull_fd, 1024).decode().strip()
kernel.close(hull_fd)
print(f"Hull: {hull}")
EOF

# Make it executable
chmod +x /tmp/test.ps

# Run it
/tmp/test.ps
```

## Tips & Tricks

1. **Tab completion** - Not implemented yet, type carefully!
2. **Command history** - Use UP/DOWN arrows
3. **Readline shortcuts**:
   - Ctrl+A: Move to start of line
   - Ctrl+E: Move to end of line
   - Ctrl+U: Clear line
   - Ctrl+K: Delete to end of line
   - Ctrl+L: Clear screen

4. **Multiple terminals** - Press Ctrl+T to open new terminal windows
5. **Tactical display** - Press Ctrl+D to open ship interior view

## Exploring the System

Start exploring:

```bash
# See what's in /proc/ship
ls /proc/ship
cat /proc/ship/status

# Explore ship systems
ls /sys/ship/systems
for sys in weapons shields engines; do
  echo "=== $sys ==="
  cat /sys/ship/systems/$sys/status
done

# Check crew locations
ls /sys/ship/crew

# Look at rooms
ls /sys/ship/rooms
cat /sys/ship/rooms/helm/oxygen
```

## Need Help?

```bash
help            # List all commands
man <command>   # Manual for command (if available)
cat /etc/motd   # View message of the day
```

## Philosophy

> "Everything is a file. Everything is hackable."

ShipOS follows Unix philosophy:
- Small tools that do one thing well
- Text streams as universal interface
- Device files expose hardware
- Scripts automate everything

Your ship, your rules. Hack the system. Survive.

---

**Good luck, Captain!**

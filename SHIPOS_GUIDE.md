# Ship OS Guide

## What is ShipOS?

ShipOS is a Unix-like operating system that runs on your spaceship's computer. Instead of having separate "game commands", **all gameplay happens through the PooScript shell and Unix commands**. Ship systems are mounted as files in the filesystem, making everything scriptable and automatable.

## Quick Start

```bash
# Launch Ship OS
python3 shipos.py

# Quick start with Kestrel
python3 shipos.py --ship kestrel

# Skip boot animation
python3 shipos.py --ship kestrel --no-intro
```

## Filesystem Layout

When you boot into ShipOS, your ship systems are mounted as files:

```
/systems/        # Ship systems (power, health, status)
/crew/           # Crew members
/ship/           # Ship-wide status (hull, fuel, etc.)
/rooms/          # Room conditions (oxygen, fire, etc.)
/bin/            # Ship command binaries
```

## Basic Usage

### Check Ship Status

```bash
# Use the built-in status command
root@Kestrel:~$ status
============================================================
SHIP STATUS
============================================================
Hull:    30/30
Shields: 4/4
Power:   7/8
Fuel:    20
============================================================

# Or read files directly
root@Kestrel:~$ cat /ship/hull
30

root@Kestrel:~$ cat /ship/shields
4
```

### List Systems

```bash
# Use built-in command
root@Kestrel:~$ systems
SHIP SYSTEMS:
------------------------------------------------------------
  Helm: ONLINE HP:100% PWR:0/2
  Shields: ONLINE HP:100% PWR:2/3
  Weapons: ONLINE HP:100% PWR:2/4
  Engines: ONLINE HP:100% PWR:2/3
  Oxygen: ONLINE HP:100% PWR:1/1

# Or browse the filesystem
root@Kestrel:~$ ls /systems/
helm  shields  weapons  engines  oxygen  medbay  reactor  sensors
```

### Power Management

```bash
# Show current power allocation
root@Kestrel:~$ power
POWER ALLOCATION:
------------------------------------------------------------
  helm           0 bars
  shields        2 bars
  weapons        2 bars
  engines        2 bars
  oxygen         1 bars
------------------------------------------------------------
  Available: 1/8

# Allocate power to shields
root@Kestrel:~$ power shields 4
Set shields power to 4

# Or use file I/O
root@Kestrel:~$ echo 3 > /systems/shields/power

# Check power allocation
root@Kestrel:~$ cat /systems/shields/power
3
```

### Crew Management

```bash
# List crew
root@Kestrel:~$ crew
CREW ROSTER:
------------------------------------------------------------
  Lieutenant Hayes     HP:100 @ Helm
  Chief O'Brien        HP:100 @ Engines
  Sergeant Vega        HP:100 @ Weapons

# Check individual crew member
root@Kestrel:~$ cat /crew/lieutenant_hayes/health
100

root@Kestrel:~$ cat /crew/lieutenant_hayes/location
Helm

# Assign crew to a room
root@Kestrel:~$ echo "weapons" > /crew/lieutenant_hayes/assign
```

### Room Status

```bash
# Check oxygen level in weapons room
root@Kestrel:~$ cat /rooms/weapons/oxygen
1.00

# Check if room is on fire
root@Kestrel:~$ cat /rooms/weapons/fire
0

# Vent a room (emergency!)
root@Kestrel:~$ echo 1 > /rooms/weapons/vent
```

## Advanced Unix Features

### Pipes and Redirection

```bash
# Find all systems with low health
root@Kestrel:~$ grep -r "health" /systems/*/health | grep "0\.[0-4]"

# Save power allocation to a file
root@Kestrel:~$ power > /home/power_snapshot.txt

# Chain commands
root@Kestrel:~$ cat /ship/hull && cat /ship/shields
30
4
```

### Scripting with PooScript

Create automation scripts in `/home/`:

```bash
root@Kestrel:~$ cat > /home/combat_auto.poo << 'EOF'
#!/usr/bin/pooscript
# Auto-combat script

# Read enemy shields
enemy_shields = int(vfs.read("/combat/enemy/shields"))

# Target appropriately
if enemy_shields > 0:
    vfs.write("/combat/target", "shields")
else:
    vfs.write("/combat/target", "weapons")

# Fire all ready weapons
for slot in ["slot1", "slot2"]:
    try:
        charge = float(vfs.read(f"/systems/weapons/{slot}/charge"))
        if charge >= 1.0:
            vfs.write(f"/systems/weapons/{slot}/fire", "1")
            print(f"Fired {slot}!")
    except:
        pass
EOF

root@Kestrel:~$ chmod +x /home/combat_auto.poo
root@Kestrel:~$ /home/combat_auto.poo
```

### Watch for Changes

```bash
# Monitor hull integrity
root@Kestrel:~$ while true; do clear; cat /ship/hull; sleep 1; done

# Alert on low oxygen
root@Kestrel:~$ while true; do
  oxygen=$(cat /rooms/weapons/oxygen)
  if [ "$oxygen" < "0.3" ]; then
    echo "WARNING: Low oxygen in weapons!"
  fi
  sleep 1
done
```

## Built-in Commands

Ship OS includes these built-in commands in `/bin/`:

- `status` - Display ship status
- `systems` - List all systems
- `crew` - Show crew roster
- `power [system] [amount]` - Power management

Plus all standard Unix commands:
- `ls`, `cd`, `pwd`, `cat`, `echo`, `grep`, `find`, etc.
- `chmod`, `chown` - Permission management
- `ps`, `kill` - Process management
- And many more!

## Tips & Tricks

1. **Use Tab Completion**: Press TAB to auto-complete commands and file paths

2. **Command History**: Use UP/DOWN arrows to recall previous commands

3. **Shortcuts**:
   - `Ctrl+C` - Cancel current command
   - `Ctrl+D` - Exit shell (same as `exit`)

4. **Explore**: Use `ls` and `cat` to discover what's available:
   ```bash
   ls /systems/
   cat /systems/shields/status
   ```

5. **Script Everything**: Any command sequence can be saved as a PooScript

6. **Power of Unix**: Combine tools with pipes:
   ```bash
   ls /crew/ | while read crew; do
     echo "$crew: $(cat /crew/$crew/health)"
   done
   ```

## Coming Soon

Future ShipOS features:
- `/combat/` - Combat state and enemy ship info
- `/navigation/` - Sector map and jump controls
- Weapon control files
- Event notifications
- Save/load through filesystem
- Network multiplayer (ship-to-ship SSH!)

## Philosophy

Ship OS follows the Unix philosophy:
- **Everything is a file** - Ship systems, crew, combat state
- **Small tools** - Each command does one thing well
- **Composable** - Pipe commands together
- **Scriptable** - Automate anything with PooScript
- **Transparent** - `cat` any file to see state

This makes spacecmd fully automatable, moddable, and educational!

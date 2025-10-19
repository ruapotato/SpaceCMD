# Ship Operating System Design

## Concept

The ship runs **ShipOS** - a Unix-like operating system where all gameplay happens through PooScript. Ship systems are represented as files/devices, crew are processes, and all ship operations use standard Unix commands and PooScript.

## Filesystem Layout

```
/
├── bin/                    # Ship command binaries
│   ├── status              # Show ship status display
│   ├── systems             # List all systems
│   ├── crew                # Crew management
│   ├── power               # Power allocation
│   ├── fire                # Weapons control
│   ├── target              # Target enemy systems
│   ├── shields             # Shield control
│   ├── jump                # FTL jump
│   └── scan                # Sensor scan
│
├── systems/                # Ship systems (device files)
│   ├── helm/
│   │   ├── status          # Read: system status
│   │   ├── power           # Read/Write: power level
│   │   ├── health          # Read: system health
│   │   └── crew            # Read: crew assigned
│   ├── shields/
│   │   ├── status
│   │   ├── power
│   │   ├── health
│   │   ├── level           # Current shield level
│   │   └── max             # Max shields
│   ├── weapons/
│   │   ├── status
│   │   ├── power
│   │   ├── slot1/          # Weapon slots
│   │   │   ├── type        # "burst_laser_2"
│   │   │   ├── charge      # 0.0-1.0
│   │   │   └── fire        # Write: trigger weapon
│   │   └── slot2/
│   ├── engines/
│   ├── oxygen/
│   ├── reactor/
│   ├── medbay/
│   └── sensors/
│
├── crew/                   # Crew member info
│   ├── hayes/
│   │   ├── name
│   │   ├── race
│   │   ├── health
│   │   ├── location        # Current room
│   │   ├── skills          # JSON skills
│   │   └── assign          # Write: assign to room
│   ├── obrien/
│   └── vega/
│
├── ship/                   # Ship-wide status
│   ├── hull                # Current hull
│   ├── hull_max
│   ├── fuel
│   ├── scrap
│   ├── missiles
│   ├── sector              # Current sector
│   └── beacon              # Current beacon
│
├── rooms/                  # Room status
│   ├── helm/
│   │   ├── oxygen          # Oxygen level
│   │   ├── fire            # On fire? (boolean)
│   │   ├── breach          # Breached? (boolean)
│   │   ├── vent            # Write: open/close airlocks
│   │   └── crew            # List crew in room
│   ├── weapons/
│   └── ...
│
├── combat/                 # Combat state (when in combat)
│   ├── active              # In combat? (boolean)
│   ├── enemy/
│   │   ├── name
│   │   ├── hull
│   │   ├── shields
│   │   └── systems/        # Enemy systems visible
│   └── target              # Write: target enemy system
│
├── navigation/             # Navigation & map
│   ├── sector              # Current sector number
│   ├── beacon              # Current beacon
│   ├── map                 # Available jumps
│   └── jump                # Write: jump to beacon
│
├── var/
│   ├── log/
│   │   ├── combat.log      # Combat events
│   │   ├── ship.log        # Ship events
│   │   └── crew.log        # Crew events
│   └── run/
│       └── shipos.pid      # Ship OS daemon PID
│
└── proc/                   # Crew as processes
    ├── 1001/               # Hayes (pilot process)
    │   ├── cmdline         # Current task
    │   ├── status          # Working/idle
    │   └── stats           # Health, location, etc.
    └── 1002/               # O'Brien (engineer)
```

## Example Gameplay Sessions

### Power Management
```bash
# Check current power allocation
cat /systems/shields/power
# Output: 2

# Allocate 4 power to shields
echo 4 > /systems/shields/power

# Check total power usage
cat /ship/power
# Output: 7/8 (used/total)

# Power down engines
echo 0 > /systems/engines/power
```

### Crew Management
```bash
# List all crew
ls /crew/
# Output: hayes  obrien  vega

# Check crew member status
cat /crew/hayes/health
# Output: 100

cat /crew/hayes/location
# Output: helm

# Assign crew to weapons room
echo "weapons" > /crew/vega/assign

# Check who's in weapons room
cat /rooms/weapons/crew
# Output: vega
```

### Combat
```bash
# Check if in combat
cat /combat/active
# Output: 1

# View enemy ship
cat /combat/enemy/hull
# Output: 15/20

# Target enemy weapons
echo "weapons" > /combat/target

# Fire weapon in slot 1
echo "fire" > /systems/weapons/slot1/fire

# Check weapon charge
cat /systems/weapons/slot1/charge
# Output: 0.75
```

### Ship Status Display
```bash
# Run status display command
status

# Or as PooScript binary:
/bin/status

# Live updating display (like 'top')
status --live

# Minimal display
status --compact
```

### Damage Control
```bash
# Check if room is on fire
cat /rooms/weapons/fire
# Output: 1

# Vent the room
echo 1 > /rooms/weapons/vent

# Check oxygen level
cat /rooms/weapons/oxygen
# Output: 0.45

# Close vents
echo 0 > /rooms/weapons/vent

# Check system health
cat /systems/weapons/health
# Output: 0.52
```

### Scripting Example

Auto-combat script in PooScript:

```python
#!/usr/bin/pooscript
# /home/captain/combat_auto.poo

# Auto-combat routine
while True:
    # Check if in combat
    in_combat = int(vfs.read("/combat/active"))
    if not in_combat:
        break

    # Get enemy shields
    enemy_shields = int(vfs.read("/combat/enemy/shields"))

    # Target based on shields
    if enemy_shields > 0:
        vfs.write("/combat/target", "shields")
    else:
        vfs.write("/combat/target", "weapons")

    # Fire all ready weapons
    for slot in ["slot1", "slot2", "slot3"]:
        charge = float(vfs.read(f"/systems/weapons/{slot}/charge"))
        if charge >= 1.0:
            vfs.write(f"/systems/weapons/{slot}/fire", "1")

    # Manage shields based on incoming
    enemy_weapons_charge = float(vfs.read("/combat/enemy/weapons/charge"))
    if enemy_weapons_charge > 0.8:
        # Full shields when enemy about to fire
        vfs.write("/systems/shields/power", "4")
    else:
        # Reduce to conserve power
        vfs.write("/systems/shields/power", "2")

    # Auto-repair critical systems
    for system in ["weapons", "shields", "oxygen", "engines"]:
        health = float(vfs.read(f"/systems/{system}/health"))
        if health < 0.5:
            print(f"WARNING: {system} damaged!")
            # Try to assign crew
            crew = vfs.read(f"/systems/{system}/crew").strip()
            if not crew:
                # Find idle crew
                for member in ["hayes", "obrien", "vega"]:
                    vfs.write(f"/crew/{member}/assign", system)
                    break

    # Wait for next tick
    process.sleep(0.5)
```

### Navigation
```bash
# View available jumps
cat /navigation/map
# Output:
# 1: Empty beacon
# 2: Distress signal (!)
# 3: Store
# 4: Combat encounter

# Jump to beacon 2
echo 2 > /navigation/jump

# Check current location
cat /navigation/sector
# Output: 3

cat /navigation/beacon
# Output: 2
```

## Ship Commands as PooScript Binaries

All ship commands are PooScript programs in `/bin/`:

### /bin/status
```python
#!/usr/bin/pooscript
# Display ship status

from shipos import render_ship_status

# Read ship state
hull = vfs.read("/ship/hull")
hull_max = vfs.read("/ship/hull_max")
shields = vfs.read("/systems/shields/level")
shields_max = vfs.read("/systems/shields/max")

# Render display
render_ship_status(hull, hull_max, shields, shields_max)
```

### /bin/power
```python
#!/usr/bin/pooscript
# Power allocation utility

if len(args) < 2:
    print("Usage: power <system> <amount>")
    print("       power list")
    exit(1)

if args[0] == "list":
    # Show all power allocations
    for system in ["helm", "shields", "weapons", "engines", "oxygen"]:
        power = vfs.read(f"/systems/{system}/power")
        max_power = vfs.read(f"/systems/{system}/max_power")
        print(f"{system:12} {power}/{max_power}")
else:
    system = args[0]
    amount = int(args[1])
    vfs.write(f"/systems/{system}/power", str(amount))
    print(f"Set {system} power to {amount}")
```

### /bin/crew
```python
#!/usr/bin/pooscript
# Crew management

import os

crew_members = os.listdir("/crew")

for member in crew_members:
    name = vfs.read(f"/crew/{member}/name")
    health = vfs.read(f"/crew/{member}/health")
    location = vfs.read(f"/crew/{member}/location")
    print(f"{name:20} HP:{health:3} @ {location}")
```

## Benefits

1. **Fully Scriptable**: Everything controllable via PooScript
2. **Immersive**: You're using the ship's actual OS
3. **Unix Philosophy**: Small tools that do one thing well
4. **Composable**: Pipe commands together: `cat /systems/*/power | grep 0`
5. **Macros**: Write complex automation scripts
6. **Education**: Learn Unix concepts through gameplay
7. **Debugging**: `cat` files to inspect game state
8. **Modding**: Add new commands, modify behavior

## Implementation Plan

1. **Integrate Ship with System**: Mount ship state into VFS
2. **Create virtual device files**: `/systems/`, `/crew/`, etc.
3. **Ship command binaries**: Write PooScript commands
4. **Update shell**: Launch into ShipOS mode instead of Unix mode
5. **Display integration**: Make `status` command render ship
6. **Combat integration**: `/combat/` appears during battles
7. **Event handling**: Events trigger files/notifications

## Special Features

### Notifications
```bash
# Watch for damage
watch cat /ship/hull

# Alert on low oxygen
/bin/alert --when "/rooms/*/oxygen < 0.3" --msg "Low O2!"
```

### Pipes & Redirection
```bash
# Log all power changes
echo 3 > /systems/shields/power 2>&1 | tee -a /var/log/power.log

# Find damaged systems
grep -l "health.*0\.[0-4]" /systems/*/health

# List crew in weapons room
cat /rooms/weapons/crew | xargs -I{} cat /crew/{}/name
```

This makes spacecmd a true "command-line" game where the command line IS the game!

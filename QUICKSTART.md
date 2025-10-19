# spacecmd Quickstart Guide

## Installation

No dependencies required! Just Python 3.7+

```bash
python3 play.py
```

## Starting the Game

```bash
# Interactive mode (choose your ship)
python3 play.py

# Quick start with Kestrel
python3 play.py --ship kestrel

# Skip intro
python3 play.py --ship kestrel --no-intro
```

## Basic Commands

Once in the game, you'll see your ship display and a command prompt:

```
Kestrel>
```

### Status Commands
- `status` or `s` - Show detailed ship status
- `systems` or `sys` - List all ship systems
- `crew` or `c` - Show crew roster
- `help` or `h` - Show all commands

### Power Management
- `power <system> <amount>` - Allocate power to a system
- Examples:
  - `power shields 3` - Give shields 3 power bars
  - `power weapons 4` - Give weapons 4 power bars
  - `power engines 0` - Power down engines

### Crew Management
- `crew` - List all crew members
- `assign <crew> <room>` - Move crew to a room
- Examples:
  - `assign hayes weapons` - Move Hayes to weapons
  - `assign obrien engines` - Move O'Brien to engines

### Damage Control
- `repair <room>` - Crew in room will repair it
- `vent <room>` - Open airlocks (extinguishes fires, but removes oxygen!)
- Examples:
  - `repair weapons` - Repair weapons system
  - `vent weapons` - Vent the weapons room

### Time
- `wait [seconds]` or `w [seconds]` - Advance time
- Examples:
  - `wait` - Wait 1 second
  - `wait 5` - Wait 5 seconds

### Exit
- `exit` or `quit` or `q` - Exit the game

## Example Session

```
Kestrel> status
=== KESTREL (HUMAN CRUISER) ===
Hull: 30/30 | Shields: 4/4
Power: 7/8 | Fuel: 20

Kestrel> systems
=== SHIP SYSTEMS ===
Helm         [ONLINE ] HP:100% PWR:0/2
Shields      [ONLINE ] HP:100% PWR:2/3
Weapons      [ONLINE ] HP:100% PWR:2/4
Engines      [ONLINE ] HP:100% PWR:2/3

Kestrel> crew
=== CREW ROSTER ===
Lieutenant Hayes     (human  ) HP:100/100 [HEALTHY ] @ Helm
Chief O'Brien        (human  ) HP:100/100 [HEALTHY ] @ Engines
Sergeant Vega        (human  ) HP:100/100 [HEALTHY ] @ Weapons

Kestrel> power shields 3
Allocated 3 power to Shields (+1)

Kestrel> wait 2
Waiting 2.0 seconds...

Kestrel> exit
Exiting spacecmd. Safe travels!
```

## Tips

1. **Manage Power**: You have limited reactor power. Allocate wisely!
2. **Watch Oxygen**: Keep O2 system powered or your crew will suffocate
3. **Station Crew**: Crew in a room provide bonuses to that system
4. **Fight Fires**: Vent rooms to extinguish fires quickly
5. **Repair Damage**: Assign crew to damaged rooms to repair them

## Ship Classes

### Kestrel (Recommended for beginners)
- Balanced stats
- Good shields (4 layers)
- 3 crew members
- Multiple weapon slots

### Shadow (Hard Mode)
- Stealth ship with cloaking
- **NO SHIELDS** - relies on evasion
- 2 crew members
- Fast engines

### Devastator (Aggressive)
- Mantis boarding ship
- Has teleporter for crew raids
- 4 Mantis crew (strong fighters)
- Designed for boarding enemy ships

## What's Next?

Current version focuses on ship management. Coming soon:
- Weapon systems (lasers, missiles, beams)
- Combat with enemy ships
- Random events and encounters
- Sector navigation
- Upgrades and shops
- Save/load system

## PooScript Integration

spacecmd is fully scriptable! You can write automation scripts in PooScript
to automate ship management, combat tactics, and more.

(Documentation coming soon)

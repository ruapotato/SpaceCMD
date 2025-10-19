# spacecmd - Play Modes Guide

spacecmd can be played in three different modes, each offering a unique experience.

## 🎮 Mode 1: Roguelike Game Mode (Recommended for Beginners)

**What**: Complete roguelike spaceship game with tutorial and combat
**Command**: `python3 game.py`

### Features:
- ✓ Interactive tutorial teaching all systems
- ✓ ASCII art combat visualization
- ✓ Turn-based ship-to-ship battles
- ✓ Sector progression (3 sectors in demo)
- ✓ Enemy encounters (pirates, rebels, mantis)
- ✓ Scrap collection and repairs
- ✓ Victory/defeat conditions
- ✓ Beautiful terminal graphics

### Gameplay:
```
1. Follow the tutorial
2. Choose your ship (Kestrel recommended)
3. Jump between beacons
4. Fight enemy ships in tactical combat
5. Manage power, shields, and weapons
6. Collect scrap, repair damage
7. Reach Federation HQ to win!
```

### Combat:
```
  YOUR SHIP: Kestrel              ENEMY: Pirate Scout

    ┏━━━┓                            ┏━━━┓
    ┃ 🎯┃                            ┃ 💀┃
═══ ┃🔴🔴┃ ══                     ══ ┃⚡⚡┃ ═══
    ┃ ⚙️ ┃                            ┃ ⚙️ ┃
    ┗━━━┛                            ┗━━━┛

  HULL:    [████████████] 30/30      HULL:    [████░░░░░░░░] 8/15
  SHIELDS: 🛡️🛡️🛡️🛡️ 4/4                    SHIELDS: 🛡️░ 1/2

  YOUR WEAPONS:
    1. Burst Laser II       [██████████] READY

  [1-9] Fire weapon    [t] Target system    [w] Wait
```

**Perfect for**: First-time players, action-focused gameplay, traditional roguelike experience

---

## 💻 Mode 2: Ship OS (Advanced - Unix Interface)

**What**: Your ship runs a Unix-like OS - interact via shell and PooScript
**Command**: `python3 shipos.py`

### Features:
- ✓ Full Unix shell interface
- ✓ Ship systems mounted as files in `/systems/`, `/crew/`, `/ship/`
- ✓ All standard Unix commands (ls, cat, grep, etc.)
- ✓ Tab completion and command history
- ✓ 100% scriptable with PooScript
- ✓ True "everything is a file" philosophy

### Filesystem Layout:
```
/systems/        # Ship systems (power, health, status)
  /helm/
  /shields/
  /weapons/
  /engines/
  /oxygen/

/crew/           # Crew members
  /lieutenant_hayes/
  /chief_obrien/
  /sergeant_vega/

/ship/           # Ship-wide status
  hull
  shields
  fuel
  scrap

/rooms/          # Room conditions
  /weapons/
    oxygen
    fire
    breach
```

### Example Session:
```bash
# Check hull
root@Kestrel:~$ cat /ship/hull
30

# Allocate power to shields
root@Kestrel:~$ echo 4 > /systems/shields/power

# List crew
root@Kestrel:~$ ls /crew/
lieutenant_hayes  chief_obrien  sergeant_vega

# Check crew health
root@Kestrel:~$ cat /crew/lieutenant_hayes/health
100

# Assign crew to weapons
root@Kestrel:~$ echo weapons > /crew/sergeant_vega/assign

# Use built-in commands
root@Kestrel:~$ status
root@Kestrel:~$ systems
root@Kestrel:~$ crew
root@Kestrel:~$ power shields 3
```

### PooScript Automation:
Create scripts to automate ship management:

```python
#!/usr/bin/pooscript
# Auto power management

# Read current state
shields = int(vfs.read("/systems/shields/power"))
weapons = int(vfs.read("/systems/weapons/power"))

# Adjust based on combat
if in_combat:
    vfs.write("/systems/shields/power", "4")
    vfs.write("/systems/weapons/power", "3")
else:
    vfs.write("/systems/shields/power", "2")
    vfs.write("/systems/weapons/power", "2")
```

**Perfect for**: Unix enthusiasts, scripters, players who want full control, educational use

---

## 🎯 Mode 3: Simple Command Mode

**What**: Streamlined command interface for ship management
**Command**: `python3 play.py`

### Features:
- ✓ Simple text-based interface
- ✓ Direct ship commands (no Unix shell)
- ✓ Real-time ship display
- ✓ Message log
- ✓ Easy to learn

### Commands:
```
status          - Show ship status
systems         - List all systems
crew            - Show crew roster
power <sys> <n> - Allocate power
assign <crew> <room> - Move crew
repair <room>   - Repair system
vent <room>     - Open airlocks
wait [n]        - Advance time
help            - Show commands
exit            - Quit
```

### Example Session:
```
Kestrel> status
=== KESTREL (HUMAN CRUISER) ===
Hull: 30/30 | Shields: 4/4
Power: 7/8 | Fuel: 20

Kestrel> power weapons 4
Allocated 4 power to Weapons (+2)

Kestrel> crew
=== CREW ROSTER ===
Lieutenant Hayes     (human  ) HP:100/100 [HEALTHY ] @ Helm
Chief O'Brien        (human  ) HP:100/100 [HEALTHY ] @ Engines
Sergeant Vega        (human  ) HP:100/100 [HEALTHY ] @ Weapons
```

**Perfect for**: Quick testing, simpler interface preference, learning the basics

---

## Comparison Matrix

| Feature | Game Mode | Ship OS | Simple Mode |
|---------|----------|---------|-------------|
| Tutorial | ✓ Yes | ✗ No | ✗ No |
| Combat | ✓ Visual ASCII | ○ Coming Soon | ○ Coming Soon |
| Ship Management | ○ Limited | ✓ Full Control | ✓ Basic Control |
| Unix Commands | ✗ No | ✓ Full Shell | ✗ No |
| Scriptability | ✗ No | ✓ PooScript | ✗ No |
| Learning Curve | Easy | Advanced | Medium |
| Graphics | ✓✓ Best | ○ Minimal | ✓ Good |

## Recommended Path

**New Players**:
1. Start with `game.py` to learn the game
2. Once comfortable, try `play.py` for ship management
3. Graduate to `shipos.py` for full Unix control and scripting

**Unix/Linux Enthusiasts**:
- Jump straight to `shipos.py` - it's a real Unix system!

**Action Gamers**:
- Stick with `game.py` for roguelike gameplay

---

## Future Integration

Eventually, all three modes will merge:
- Ship OS will include combat and events
- Game mode will offer Unix shell access
- All modes will share the same save format

But for now, choose the mode that fits your play style!

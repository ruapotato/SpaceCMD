# SpaceCMD - Hackable Spaceship Combat Roguelike

A terminal-based spaceship combat game where **every ship runs a Unix-like operating system** and **all AI is implemented in PoohScript** - a real scripting language you can read, hack, steal, and exploit.

```
╔═══════════════════════════════════════════════════════════════╗
║                      KESTREL SHIP OS                          ║
║                   HUMAN CRUISER CLASS                         ║
║              ALL SYSTEMS RUNNING POOHSCRIPT                   ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🚀 What is SpaceCMD?

**SpaceCMD is the world's first roguelike where enemies are controlled by REAL scripts you can hack.**

Every spaceship in the game runs a complete Unix-like operating system (ShipOS). Enemy AI isn't hard-coded in Python - it's **actual PoohScript files** running in `/usr/bin/` on enemy ship computers. You can:

- **Hack into enemy ships** and read their automation scripts
- **Disable their weapon control** by removing scripts from `/etc/cron/jobs`
- **Steal their AI** and run it on your own ship
- **Modify their config files** to change behavior
- **Plant backdoors** to control multiple ships

**IMPORTANT:** This game is built on PoohScript - NOT hard-coded Python game logic. All intelligence, automation, and behaviors are PoohScript files running on virtual Unix systems. This is a core design principle.

### Key Features

- **Full Unix-like OS**: Every ship runs ShipOS with shell, VFS, processes, permissions
- **PoohScript AI**: ALL game logic is PoohScript - enemy AI, automation, everything
- **Hackable Enemy Ships**: Enemy AI runs as actual scripts in `/usr/bin/` you can steal/disable
- **No Hard-coded Python**: Game behavior is defined by PoohScript files, not Python code
- **Device File Interface**: Ship systems exposed as `/dev`, `/proc`, `/sys` files
- **Autonomous Crew Bots**: PoohScript-based crew AI that manage repairs
- **Beautiful Terminal UI**: LCARS-style 3-panel interface showing ship interiors
- **Real Hacking**: Infiltrate enemy filesystems, disable scripts, steal automation

## 🎮 Quick Start

```bash
# Install
git clone https://github.com/ruapotato/SpaceCMD.git
cd SpaceCMD

# Install pygame (required for GUI mode)
pip install pygame

# Launch GUI mode (default - recommended!)
python3 play.py

# Or use CLI mode (for debugging)
python3 play.py --no-gui

# Choose a specific ship
python3 play.py --ship kestrel
```

### 🖥️ GUI Desktop Environment (NEW!)

SpaceCMD now features a beautiful Pygame-based desktop environment:

- **LCARS + GNOME 2 Aesthetic**: Star Trek inspired interface with professional window management
- **Multiple Terminals**: Open multiple terminal windows, all connected to the same ShipOS
- **Tactical Display**: FTL-style ship interior view with interactive crew management
- **Real Unix Integration**: Every terminal runs actual ShipOS commands (`ls`, `pwd`, `cat`, `touch`, etc.)
- **Animated Starfield**: Dynamic background with warp effects
- **Interactive Crew**: Click crew members to select them, click rooms to move them
- **Command Log**: See what commands are being executed in real-time

**Keyboard Shortcuts:**
- `Ctrl+T` - Open new terminal
- `Ctrl+D` - Open tactical display
- `ESC` - Exit

See [GUI_README.md](GUI_README.md) for detailed GUI documentation.

## 📁 The Ship Filesystem (Unix-like)

Every ship runs a complete Unix-like filesystem:

### Your Ship (Player)
```
/proc/ship/          - Ship state (like /proc in Linux)
  ├── name           - Ship name
  ├── hull           - Current hull points
  ├── shields        - Current shield layers
  ├── power          - Available power
  └── scrap          - Currency/resources

/proc/systems/       - System status
  ├── weapons        - Weapon status, charge, power
  ├── shields        - Shield layers, power
  ├── engines        - Engine power, evasion
  ├── oxygen         - O2 levels
  └── medbay         - Medical bay status

/proc/crew/          - Crew member status
  ├── bot1           - Crew bot 1 stats
  ├── bot2           - Crew bot 2 stats
  └── bot3           - Crew bot 3 stats

/usr/local/bin/      - YOUR automation scripts (write your own!)
  ├── auto_repair    - Your repair automation
  └── combat_ai      - Your combat AI (PoohScript!)

/etc/cron/jobs       - Scripts that run automatically
```

### Enemy Ships (Hackable!)
```
/proc/ship/          - Enemy ship state
/proc/systems/       - Enemy system status
/proc/enemy/         - Enemy's view of YOU (your hull, shields)
/usr/bin/            - ENEMY AI SCRIPTS (PoohScript!)
  ├── weapon_control - Their weapon AI
  ├── shield_manager - Their shield AI
  ├── damage_control - Their repair AI
  └── tactical_ai    - Their tactical AI
/etc/ship/config     - Enemy configuration
/etc/cron/jobs       - Enemy automation schedule
```

**You can hack into enemy ships and steal/disable these scripts!**

## 🎯 Game Goals & Modes

### Easy Mode: Command-Line Combat
- Fight through 8 sectors using terminal commands
- Learn ship systems and basic combat
- Use pre-written commands (all PoohScript!)
- **Goal:** Reach Federation HQ with vital intel

### Normal Mode: Hacking & Exploitation
- Enemy AI is smarter (better PoohScript)
- You must hack enemy ships to gain advantage
- Disable their automation scripts
- Steal their AI for your own use
- **Goal:** Survive by superior hacking skills

### Hard Mode: Script to Win
- Enemy AI is EXTREMELY smart (complex PoohScript)
- You MUST write your own combat automation
- Your PoohScripts vs their PoohScripts
- Battle is decided by who wrote better code
- **Goal:** Build better AI than the enemy

### Master Mode: AI Overlord
- All actions must be automated via PoohScript
- Write complete ship automation
- Hack AND control multiple enemy ships
- Build a fleet controlled by your scripts
- **Goal:** Create the ultimate autonomous combat system

## 🤖 Enemy AI System (PoohScript!)

**This is the core innovation of SpaceCMD:** Enemy behavior is NOT hard-coded Python. It's real PoohScript running on enemy ship operating systems.

### Example: Enemy Weapon Control Script

This is ACTUAL code running on enemy ships at `/usr/bin/weapon_control`:

```python
#!/usr/bin/pooscript
# Automatic Weapons Control System

# Read weapon status from /proc
weapons = vfs.read("/proc/systems/weapons")
charge = 0
for line in weapons.split("\n"):
    if "charge:" in line:
        charge = int(line.split(":")[1].strip())

# Read enemy (player) status
enemy_shields = int(vfs.read("/proc/enemy/shields").strip())
enemy_hull = int(vfs.read("/proc/enemy/hull").strip())

# Firing logic
if charge >= 100:
    if enemy_shields > 0:
        print("FIRE: laser shields")  # Target shields first
        vfs.write("/proc/systems/weapons", "online\npower: 2\ncharge: 0\nmax_charge: 100")
    else:
        print("FIRE: laser weapons")  # Disable their weapons
        vfs.write("/proc/systems/weapons", "online\npower: 2\ncharge: 0\nmax_charge: 100")
else:
    # Charge weapons
    new_charge = min(100, charge + 10)
    vfs.write("/proc/systems/weapons", f"online\npower: 2\ncharge: {new_charge}\nmax_charge: 100")
```

**This runs every game tick on the enemy ship's OS. You can hack it, disable it, or steal it!**

### How Enemy AI Works

1. Enemy ship boots up with Unix-like OS
2. Scripts in `/usr/bin/` are loaded
3. `/etc/cron/jobs` lists which scripts run each tick:
   - `weapon_control` - Charges and fires weapons
   - `shield_manager` - Manages shield power
   - `damage_control` - Repairs systems
   - `tactical_ai` - Makes strategic decisions
4. Scripts read `/proc/` to get ship/enemy status
5. Scripts write to `/proc/` or `/sys/` to control systems
6. All output is captured and translated to game actions

**You can hack into enemy ships and disable these scripts!**

## 🛠️ Commands (All PoohScript!)

### Basic Ship Control
```bash
status              # Show ship status (PoohScript in /bin/status)
systems             # List systems (PoohScript in /bin/systems)
crew                # Show crew (PoohScript in /bin/crew)
power <sys> <amt>   # Adjust power (PoohScript in /bin/power)
fire <weapon>       # Fire weapon (PoohScript in /bin/fire)
```

### Hacking Commands (Attack Enemy Ships!)
```bash
# Infiltrate enemy filesystem
hack ls /usr/bin/           # List enemy AI scripts
hack cat /usr/bin/weapon_control  # Read their weapon AI
hack cat /etc/cron/jobs     # See which scripts run

# Disable enemy automation
hack_disable weapon_control # Remove from cron, disable firing
hack_disable shield_manager # Stop shield regeneration
hack_disable damage_control # Prevent repairs

# Steal enemy AI for yourself
hack_steal weapon_control   # Copy to your /usr/local/bin/
hack_steal tactical_ai      # Steal their tactics

# Advanced hacking
hack_edit /etc/ship/config  # Modify enemy behavior
hack_backdoor               # Install persistent access
hack_control <ship>         # Take full control

# View what you've hacked
hacked_ships                # List ships under your control
```

### Unix Commands (Direct Filesystem Access)
```bash
ls /proc/ship/              # List ship status files
cat /proc/ship/hull         # Read hull points
cat /proc/systems/weapons   # Read weapon status
cat /usr/bin/status         # Read the status command source
```

## 🔧 Hacking

**Every command is a PooScript file**. View and modify them:

```bash
# View command source
hack power          # See how power allocation works
cat /bin/status     # Read the status command

# All commands are in /bin
ls /bin

# Write your own scripts
cat > /tmp/autopilot.ps <<EOF
#!/usr/bin/pooscript
# Autonomous power management

# Read hull
hull_fd = kernel.open("/dev/ship/hull", kernel.O_RDONLY)
hull = int(kernel.read(hull_fd, 1024).decode().strip())
kernel.close(hull_fd)

# Emergency: boost shields if hull low
if hull < 15:
    shield_fd = kernel.open("/sys/ship/systems/shields/power", kernel.O_WRONLY)
    kernel.write(shield_fd, b"4")
    kernel.close(shield_fd)
    print("EMERGENCY: Shields to maximum!")
EOF

chmod +x /tmp/autopilot.ps
/tmp/autopilot.ps
```

## 📚 PooScript Examples

### Read ship data with kernel syscalls

```python
#!/usr/bin/pooscript
# Read hull integrity using kernel syscalls

fd = kernel.open("/dev/ship/hull", kernel.O_RDONLY)
hull_data = kernel.read(fd, 1024)
kernel.close(fd)

hull = int(hull_data.decode().strip())
print(f"Hull integrity: {hull}")
```

### Control power allocation

```python
#!/usr/bin/pooscript
# Set shields to maximum power

# Read current shields
fd = kernel.open("/sys/ship/systems/shields/power", kernel.O_RDWR)
current = kernel.read(fd, 1024).decode().strip()

# Write new power level
kernel.write(fd, b"3")
kernel.close(fd)

print("Shields at maximum power!")
```

### Monitor crew bots

```python
#!/usr/bin/pooscript
# Watch what crew bots are doing

fd = kernel.open("/proc/ship/crew_ai", kernel.O_RDONLY)
ai_status = kernel.read(fd, 4096)
kernel.close(fd)

print(ai_status.decode())
```

### List all systems

```python
#!/usr/bin/pooscript
# List all systems and their status

systems = kernel.readdir("/sys/ship/systems")
for system in systems:
    if system not in [".", ".."]:
        fd = kernel.open(f"/sys/ship/systems/{system}/status", kernel.O_RDONLY)
        status = kernel.read(fd, 1024).decode()
        kernel.close(fd)
        print(status.strip())
```

## 🎯 Architecture & Design Principles

### THREE-LAYER ARCHITECTURE

SpaceCMD uses a strict three-layer architecture that enables all three game modes:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: USER INTERFACE                                    │
│  ┌──────────────┬──────────────┬────────────────────────┐   │
│  │  GUI Mode    │ Terminal Mode │  Scripting Mode        │   │
│  │  (Pygame)    │  (CLI/LCARS) │  (PooScript Automation)│   │
│  └──────────────┴──────────────┴────────────────────────┘   │
│         All three modes work because they all read          │
│         the same VFS device files and run PooScript         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: VFS / DEVICE FILES                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  /proc/ship/*  - Ship state (read-only)            │    │
│  │  /dev/ship/*   - Ship hardware (read/write)        │    │
│  │  /sys/ship/*   - System attributes (read/write)    │    │
│  │  scripts/bin/* - PooScript shell commands          │    │
│  └─────────────────────────────────────────────────────┘    │
│         VFS exposes Python state to PooScript               │
│         PooScript commands read/write device files          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: PYTHON CORE (Game Logic)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Ship.py       - Ship physics & movement           │    │
│  │  Combat.py     - Combat physics & damage           │    │
│  │  LinearGalaxy  - 1D galaxy with positions          │    │
│  │  WorldManager  - Enemy spawning & encounters       │    │
│  │  ShipOS        - OS for each ship (player+enemies) │    │
│  └─────────────────────────────────────────────────────┘    │
│         Python handles physics, updates VFS state           │
│         NEVER implements game behavior directly             │
└─────────────────────────────────────────────────────────────┘
```

### CRITICAL: What Goes Where?

#### ✅ PYTHON LAYER (core/*.py)
**Purpose:** Physics, state management, infrastructure
**Examples:**
- Ship position/velocity calculations
- Damage calculations (shields absorb X, hull takes Y-X)
- Engine effectiveness = health × power × (1 + crew_bonus)
- Update VFS device file contents every frame
- Spawn enemies at positions
- Calculate weapon hit/miss

**Rules:**
- NO game behavior decisions (no "if hull < 10 then flee")
- NO AI logic (no "target their weapons first")
- ONLY physics and math
- Updates state, exposes via VFS

#### ✅ VFS LAYER (ShipOS device files)
**Purpose:** Expose Python state to PooScript, accept commands
**Examples:**
- `/proc/ship/sensors` - Read ship position from Python
- `/dev/ship/move` - Write movement commands to Python
- `/dev/ship/target` - Set weapon target
- `/dev/ship/fire` - Trigger weapon

**Rules:**
- Read handlers: Get data from Python objects
- Write handlers: Call Python methods with data
- Device files are the ONLY interface between Python and PooScript

#### ✅ POOSCRIPT LAYER (scripts/bin/*, enemy AI)
**Purpose:** ALL game behavior, decisions, automation
**Examples:**
- `scripts/bin/advance` - Command to move toward center
- `scripts/bin/retreat` - Command to flee combat
- `scripts/bin/fire` - Smart weapon firing logic
- `core/resources/enemy_ai.poo` - Enemy decision making

**Rules:**
- ALL decisions happen here ("should I flee?", "which weapon?")
- Reads `/proc/ship/*` to get state
- Writes `/dev/ship/*` to take actions
- Enemy AI is PooScript running on enemy ShipOS

### Why This Architecture?

1. **Three Game Modes**: GUI, Terminal, Scripting all work because they use same VFS
2. **Hackable Enemies**: Enemy AI is real PooScript you can read/steal/modify
3. **Scriptable Everything**: Players write PooScript to automate
4. **Future Hacking**: Can implement ship-to-ship hacking (access enemy VFS)

### Examples

❌ **WRONG** (Python implementing behavior):
```python
# combat.py - DON'T DO THIS!
def enemy_ai_turn(self):
    if self.enemy_ship.hull < 10:
        self.attempt_flee()  # ❌ Decision in Python!
```

✅ **RIGHT** (PooScript implementing behavior):
```python
# core/resources/enemy_ai.poo
#!/usr/bin/pooscript
# Read our hull
my_hull = int(vfs.read('/dev/ship/hull').strip())

# Decide to flee (decision in PooScript!)
if my_hull < 10:
    vfs.write('/tmp/ai_should_flee', '1')
```

❌ **WRONG** (Python hardcoding command):
```python
# ship_os.py - DON'T DO THIS!
def advance_command(self):
    self.ship.set_course(self.ship.position - 10)  # ❌ Hardcoded!
```

✅ **RIGHT** (PooScript shell command):
```bash
# scripts/bin/advance
#!/usr/bin/pooscript
# Read current position
pos = float(vfs.read('/proc/ship/sensors').split('Position:')[1].split()[0])

# Move toward center (position - 10)
target = pos - 10
vfs.write('/dev/ship/course', str(target))
```

### Core Design Principle: AVOID HARD-CODED PYTHON

**SpaceCMD is script-driven, NOT Python-driven.**

❌ **DON'T:** Write Python functions that implement game behavior
✅ **DO:** Write PoohScript files that implement game behavior

❌ **DON'T:** Create Python AI classes for enemies
✅ **DO:** Create PoohScript files in enemy `/usr/bin/`

❌ **DON'T:** Hard-code combat logic in Python
✅ **DO:** Write PoohScript automation that reads `/proc/` files

**Everything must be hackable. If it's hard-coded in Python, players can't hack it!**

### What's Implemented in PoohScript vs Python

**PoohScript (Hackable):**
- Enemy weapon control AI
- Enemy shield management
- Enemy damage control
- Enemy tactical decisions (flee/fight)
- Player automation scripts
- All commands (`status`, `fire`, `advance`, `retreat`)
- Shell commands in `scripts/bin/*`

**Python (Infrastructure Only):**
- PoohScript interpreter
- VFS/filesystem implementation
- Terminal UI rendering
- Physics calculations (damage, movement, power)
- ShipOS instances (one per ship)
- Device file read/write handlers

**VFS Layer (Bridge):**
- `/proc/ship/*` - Expose Python state to PooScript
- `/dev/ship/*` - Accept PooScript commands to Python
- Device handlers update Python objects

**The rule:** If a player should be able to hack it, it MUST be PoohScript.

---

## 📐 Complete Architecture Guide

### Directory Structure

```
SpaceCMD/
├── core/                      # Python infrastructure layer
│   ├── ship.py               # Ship physics, movement, power systems
│   ├── combat.py             # Combat physics, damage calculations
│   ├── linear_galaxy.py      # 1D galaxy with positions, POIs
│   ├── world_manager.py      # Enemy spawning, encounters
│   ├── ship_os.py            # ShipOS - mounts VFS device files
│   ├── system.py             # Unix system (VFS, processes, shell)
│   ├── pooscript.py          # PoohScript interpreter
│   ├── enemy_ai.py           # Enemy filesystem with AI scripts
│   ├── terminal_ui.py        # LCARS terminal interface
│   └── gui/                  # Pygame GUI components
│       ├── desktop.py        # Window manager
│       ├── terminal_widget.py # Terminal window
│       ├── tactical_widget.py # Ship interior display
│       └── map_widget_v2.py  # Galaxy map with navigation
│
├── scripts/                   # PoohScript command layer
│   └── bin/                  # Shell commands (Layer 2)
│       ├── status            # Show ship status
│       ├── fire              # Fire weapons
│       ├── power             # Manage power allocation
│       ├── advance           # Move toward galaxy center
│       ├── retreat           # Move away from enemy
│       ├── warp_to_center    # Navigate to galactic center
│       ├── warp_from_center  # Navigate to outer rim
│       ├── stop              # Emergency stop
│       └── ...               # 25+ other commands
│
├── play.py                    # Main entry point
└── README.md                  # This file
```

### Layer 1: Python Core (Physics Engine)

**File: `core/ship.py`**
- Ship movement physics (velocity, position, target_position)
- Power system (reactor output, power allocation)
- Crew AI priorities (fire > repair > heal > operate)
- System effectiveness = health × power × (1 + crew_bonus)
- Repair rates (now 1/10th slower for balance)
- Updates ship state every frame (position, hull, shields)

**File: `core/combat.py`**
- Combat distance tracking (0.5 to 10.0 units)
- Sensor range and enemy fade mechanics (30 unit range)
- Chase mechanics (player fleeing, enemy pursuing)
- Damage calculations (shields absorb, then hull/system damage)
- Weapon range checks
- Victory/defeat conditions

**File: `core/linear_galaxy.py`**
- 1D galaxy (position from center: 0 = center, 1000 = outer rim)
- Points of Interest (POIs): stores, repair stations, nebulas
- Difficulty scaling based on distance from center
- Enemy type selection by position

**File: `core/world_manager.py`**
- Spawns enemies at player position during combat
- Manages active encounters
- Handles combat state transitions
- Tracks visited POIs
- Controls enemy pursuit/fade based on distance

**Key Principle:** Python NEVER makes gameplay decisions. It only:
- Calculates physics (damage = shields_absorb(weapon.damage))
- Updates state (ship.position += velocity * dt)
- Checks validity (is weapon in range? does system have power?)

### Layer 2: VFS Device Files (The Bridge)

**File: `core/ship_os.py`** - Creates all device files

#### Read-Only Status Files (`/proc/ship/*`)

```python
/proc/ship/status       # Complete ship overview
/proc/ship/power        # Power allocation details
/proc/ship/crew_ai      # What autonomous bots are doing
/proc/ship/combat       # Current combat status
/proc/ship/weapons      # All weapons and charge status
/proc/ship/enemy        # Enemy ship systems (when in combat)
/proc/ship/location     # Galaxy position and difficulty
/proc/ship/sensors      # Sensor readout (position, velocity, nearby POIs)
/proc/ship_info         # Detailed ship statistics
```

#### Hardware Device Files (`/dev/ship/*`)

```python
/dev/ship/hull          # Read current hull points
/dev/ship/shields       # Read current shield layers
/dev/ship/reactor       # Read reactor power output
/dev/ship/dark_matter   # Read FTL fuel

# Write-capable devices
/dev/ship/target        # Write room name to target enemy system
/dev/ship/fire          # Write weapon index to fire
/dev/ship/move          # Write "closer" or "away" for combat movement
/dev/ship/course        # Write destination position for galaxy travel
/dev/ship/stop          # Write anything to emergency stop
/dev/ship/beacon        # Write 1 to activate distress beacon (attracts enemies!)
/dev/ship/crew_assign   # Write "crew_name room_name" to move crew
```

#### System Attributes (`/sys/ship/systems/*`)

Each system has:
```python
/sys/ship/systems/weapons/status   # "ONLINE" or "OFFLINE"
/sys/ship/systems/weapons/power    # Current power (read/write)
/sys/ship/systems/weapons/health   # Health percentage (read-only)
/sys/ship/systems/shields/...      # Same attributes
/sys/ship/systems/engines/...
/sys/ship/systems/oxygen/...
```

#### Device File Handlers

Device files are implemented as Python functions in `ship_os.py`:

```python
def course_write(data):
    """Handle writing to /dev/ship/course"""
    destination = float(data.decode('utf-8').strip())
    destination = max(0.0, min(world_manager.galaxy.max_distance, destination))
    self.ship.set_course(destination)  # Call Python method
    return len(data)

self.vfs.device_handlers['dev_ship_course'] = (course_read, course_write)
self.vfs.create_device('/dev/ship/course', True, 0, 0, device_name='dev_ship_course')
```

**Key Principle:** Device files are the ONLY interface between Python and PoohScript.

### Layer 3: PoohScript Commands (Game Logic)

**File: `scripts/bin/warp_to_center`**
```python
#!/usr/bin/pooscript
# Set course toward galactic center

# Read current location
fd = kernel.open("/proc/ship/location", kernel.O_RDONLY)
location_data = kernel.read(fd, 4096).decode('utf-8')
kernel.close(fd)

# Parse position
current_pos = 0.0
for line in location_data.split('\n'):
    if "Position:" in line:
        current_pos = float(line.split(':')[1].strip().split()[0])

# Set course to center (position 0)
fd = kernel.open("/dev/ship/course", kernel.O_WRONLY)
kernel.write(fd, b"0")
kernel.close(fd)

print(f"✓ Course set to galactic center")
print(f"  Distance: {current_pos:.1f} units")
```

**File: `scripts/bin/fire`**
```python
#!/usr/bin/pooscript
# Fire weapon at target

# Check if in combat
combat_fd = kernel.open("/proc/ship/combat", kernel.O_RDONLY)
combat_state = kernel.read(combat_fd, 4096).decode('utf-8')
kernel.close(combat_fd)

if "No active combat" in combat_state:
    error("No combat active")
    exit(1)

# Check target
target_fd = kernel.open("/dev/ship/target", kernel.O_RDONLY)
target = kernel.read(target_fd, 1024).decode('utf-8').strip()
kernel.close(target_fd)

# Fire weapon 0
fire_fd = kernel.open("/dev/ship/fire", kernel.O_WRONLY)
bytes_written = kernel.write(fire_fd, b"0")
kernel.close(fire_fd)
```

### Enemy AI Architecture

**File: `core/enemy_ai.py`**

Creates a virtual filesystem for each enemy ship:

```python
class EnemyShipFilesystem:
    def __init__(self, ship_name, ship_type):
        self.files = {
            "/proc/ship/hull": "100",
            "/proc/ship/shields": "4",
            "/proc/enemy/hull": "30",  # What enemy sees about player
            "/proc/enemy/shields": "3",

            # AI Scripts (PoohScript!)
            "/usr/bin/weapon_control": b"#!/usr/bin/pooscript\n...",
            "/usr/bin/shield_manager": b"#!/usr/bin/pooscript\n...",
            "/usr/bin/damage_control": b"#!/usr/bin/pooscript\n...",
            "/usr/bin/tactical_ai": b"#!/usr/bin/pooscript\n...",

            # Automation schedule
            "/etc/cron/jobs": "/usr/bin/weapon_control\n/usr/bin/shield_manager\n..."
        }
```

**Damage Control AI (Smart Bot Management):**
```python
# /usr/bin/damage_control on enemy ships
# Intelligently sends bots to most damaged rooms

systems = ["weapons", "shields", "engines", "oxygen"]
most_damaged_system = None
lowest_health = 100.0

for system in systems:
    sys_data = vfs.read(f"/proc/systems/{system}")
    if "offline" in sys_data:
        most_damaged_system = system
        break
    # Check for damage indicators

if most_damaged_system:
    print(f"MOVE_CREW: bot2 {most_damaged_system}")
    print(f"REPAIR: {most_damaged_system}")
```

### GUI Architecture (Layer 3 Alternative Interface)

**File: `core/gui/desktop.py`**
- Window manager (LCARS + GNOME 2 aesthetic)
- Manages multiple terminal windows
- All terminals connect to same ShipOS

**File: `core/gui/terminal_widget.py`**
- Renders terminal with command history
- Sends commands to ShipOS.execute_command()
- Displays output from PoohScript execution

**File: `core/gui/map_widget_v2.py`**
- Galaxy map with navigation buttons
- Buttons call PoohScript commands:
  - "WARP TOWARD CENTER" → executes `warp_to_center`
  - "WARP AWAY FROM CENTER" → executes `warp_from_center`
  - "STOP" → executes `stop`
- Displays ship position, velocity, POIs

**File: `core/gui/tactical_widget.py`**
- FTL-style ship interior view
- Shows rooms, systems, crew positions
- Displays combat distance and sensor range
- Click crew → click room to move (sends command to ShipOS)

**Key Principle:** GUI never directly modifies ship state. It always:
1. Calls PoohScript commands (`ship_os.execute_command("warp_to_center")`)
2. Or writes to device files (through PoohScript)
3. Reads device files to display state

This ensures GUI, terminal, and scripting modes all work identically.

### Data Flow Examples

#### Example 1: Firing a Weapon (GUI Mode)

```
User clicks "Fire" button in GUI
    ↓
GUI calls: ship_os.execute_command("fire 0")
    ↓
ShipOS runs: /bin/fire (PoohScript)
    ↓
PoohScript opens: /dev/ship/fire
    ↓
Device handler checks: weapons system functional?
    ↓
Device handler calls: combat_state.fire_player_weapon(0)
    ↓
Python combat.py: calculates damage, applies to enemy
    ↓
Python updates: enemy.hull -= damage
    ↓
VFS updates: /proc/ship/combat reflects new state
    ↓
GUI reads: /proc/ship/combat to display updated status
```

#### Example 2: Enemy AI Deciding to Repair

```
Game loop: world_manager.update(dt)
    ↓
For each enemy: run their /etc/cron/jobs scripts
    ↓
Execute: /usr/bin/damage_control (PoohScript)
    ↓
PoohScript reads: /proc/systems/weapons (from enemy VFS)
    ↓
PoohScript detects: weapons offline
    ↓
PoohScript writes: "MOVE_CREW: bot2 weapons"
    ↓
Output parsed by world_manager
    ↓
Python calls: enemy_bot.assign_to_room(weapons_room)
    ↓
Enemy VFS updates: /proc/crew/bot2 location
    ↓
Next frame: bot repairs weapons automatically (in Ship.update())
```

#### Example 3: Galaxy Navigation

```
User clicks "WARP TOWARD CENTER" button in GUI
    ↓
GUI calls: ship_os.execute_command("warp_to_center")
    ↓
ShipOS runs: /bin/warp_to_center (PoohScript)
    ↓
PoohScript opens: /proc/ship/location (reads position)
    ↓
PoohScript opens: /dev/ship/course (writes "0")
    ↓
Device handler calls: ship.set_course(0.0)
    ↓
Python sets: ship.target_position = 0.0
              ship.is_traveling = True
              ship.velocity = -ship.get_current_speed()
    ↓
Each frame: ship.update_position(dt) moves ship toward center
    ↓
GUI map widget reads: /proc/ship/sensors to display position
```

### Combat System Details

**Combat Distance System:**
- Combat starts at distance 5.0 units
- Player can move closer (min 0.5) or away (max 10.0)
- Weapons have ranges (laser: 8.0, missile: 15.0, beam: 6.0)
- Sensors have 30 unit range for detecting enemies

**Pursuit Mechanics:**
- Player can flee combat (`retreat` command repeatedly)
- Enemy pursues based on speed differential
- If player gets beyond sensor range (30 units): enemy fades away
- If player gets beyond escape threshold (50 units): enemy gives up
- If enemy catches up (<2 units): combat re-engages

**Damage System:**
- Shields absorb damage first
- Targeted system damage: each point = 5% system health lost
- System destroyed: 20% of weapon damage spills to hull
- Untargeted shots: full damage to hull
- Systems with crew work at 100% + bonuses
- Systems without crew work at 25% effectiveness

### Power System Architecture

**Power Generation:**
```python
# base_power = reactor_power (e.g., 8)
# reactor_health affects output
available_power = int(reactor_power * reactor.health)

# Crew in reactor add bonus (+1 per crew)
if reactor.crew:
    available_power += len(reactor.crew)
```

**Power Allocation:**
```python
# Each system can receive 0-3 power
# Total allocated cannot exceed available_power
# If reactor damaged: power drops, systems fail
```

**System Effectiveness:**
```python
effectiveness = health × (power / max_power) × (1.0 + crew_bonus)
# Without crew: effectiveness × 0.25 (automated mode)
# With crew: full effectiveness + 10% per skill level
```

### Galaxy System Architecture

**Linear Galaxy (1D):**
```
Outer Rim (pos: 1000) ←→ Galactic Center (pos: 0)
[Easy enemies]            [Hard enemies, boss]

- Ship position: distance from center (0.0 to 1000.0)
- Difficulty: 1.0 - (position / 1000.0)
- POIs scattered throughout at fixed positions
- Ship travels continuously (velocity × dt)
```

**Movement:**
```python
ship.set_course(target_position)
# Each frame:
ship.position += ship.velocity * dt
# When ship.position reaches target_position:
ship.stop_traveling()
```

### Repair Balance

**Recent Change: Repair Speed Reduced**
- Old rate: 0.2 per second (very fast)
- New rate: 0.02 per second (10× slower)
- **Reason:** Rooms were nearly invulnerable if a bot was present
- **Effect:** Focused fire on one system can now destroy it despite repairs
- **Balance:** Makes targeting strategic, rewards player's smart choices

### File Organization Rules

**Adding New Features:**

1. **Physics/Calculation** → `core/*.py`
   - Example: Calculating shield recharge rate
   - Example: Weapon damage falloff with distance

2. **Game Behavior** → `scripts/bin/*` or enemy AI
   - Example: When to repair which system
   - Example: Flee if hull < 20%
   - Example: Target enemy weapons first

3. **Player Commands** → `scripts/bin/command_name`
   - Always PoohScript
   - Always read/write device files
   - Never import Python modules

4. **Device Files** → `core/ship_os.py`
   - Add new /proc/ file to expose Python state
   - Add new /dev/ file to accept commands
   - Device handler bridges PoohScript ↔ Python

5. **GUI Elements** → `core/gui/*`
   - Call ship_os.execute_command() for actions
   - Read device files for display
   - Never call ship methods directly

---

## 🎨 Ships Available

- **Kestrel**: Balanced human cruiser (recommended for beginners)
- **Stealth**: Advanced ship with cloaking, no shields (hard mode)
- **Mantis**: Boarding ship with teleporter, strong crew (aggressive)

## 🌟 What Makes This Special?

Unlike other spaceship sims, SpaceCMD gives you **complete control** through a real scripting interface:

1. **Real Unix System**: Not a fake shell - actual VFS, processes, syscalls
2. **Hackable Commands**: Every command is PooScript you can modify
3. **Device Files**: Ship hardware as `/dev` devices like a real OS
4. **Kernel API**: Use syscalls like `kernel.open()` for low-level access
5. **Autonomous Crew**: AI bots handle repairs so you focus on tactics
6. **Everything Scriptable**: Automate ship operations with PooScript

## 📖 Advanced Topics

### Writing Custom Commands

Create your own command in `/bin`:

```bash
# Create a custom command
cat > /bin/shields_max <<'EOF'
#!/usr/bin/pooscript
# Maximize shield power

fd = kernel.open("/sys/ship/systems/shields/power", kernel.O_WRONLY)
kernel.write(fd, b"4")
kernel.close(fd)
print("SHIELDS AT MAXIMUM!")
EOF

chmod +x /bin/shields_max
shields_max
```

### Accessing Ship State

All ship data is accessible through device files:

```python
# Read various ship metrics
hull_fd = kernel.open("/dev/ship/hull", kernel.O_RDONLY)
shields_fd = kernel.open("/dev/ship/shields", kernel.O_RDONLY)
fuel_fd = kernel.open("/dev/ship/fuel", kernel.O_RDONLY)

hull = kernel.read(hull_fd, 1024)
shields = kernel.read(shields_fd, 1024)
fuel = kernel.read(fuel_fd, 1024)

kernel.close(hull_fd)
kernel.close(shields_fd)
kernel.close(fuel_fd)
```

### Sysfs Attributes

Like Linux's `/sys`, ship systems have attribute files:

```bash
# Each system has attributes
ls /sys/ship/systems/engines/
# status  power  health

# Read attributes
cat /sys/ship/systems/engines/power  # Current power
cat /sys/ship/systems/engines/health # Health percentage
cat /sys/ship/systems/engines/status # Online/offline status

# Write attributes (where supported)
echo 3 > /sys/ship/systems/engines/power  # Set engine power
```

### Crew Bot AI

Crew bots use a priority system:

1. **Fire suppression** (highest priority)
2. **Critical repairs** (systems below 50% health)
3. **Oxygen monitoring** (rooms below 80%)
4. **System operation** (normal duty)

View bot decisions in real-time:
```bash
watch -n 1 'cat /proc/ship/crew_ai'
```

## 🤝 Contributing

This is an experimental project exploring **operating systems as game interfaces**. Contributions welcome!

## 📜 License

GPL-3.0 License

## 🎮 Author

David Hamner - Exploring the intersection of operating systems, scripting languages, and game design.

GitHub: https://github.com/ruapotato/SpaceCMD

---

**"Everything is a file. Everything is hackable. Crew are autonomous bots. Welcome aboard, Captain."**

---

## 🔧 TODO - Active Development Tasks

### Critical Fixes
- [ ] **Fix crew bonuses for weapon damage** - Weapons should do more damage with more crew assigned
- [ ] **Adjust hull damage threshold** - Ship should explode when 75% of systems are destroyed
- [ ] **Fix window maximize and resizing** - Window maximize button and resize functionality broken
- [ ] **Create persistent tactical command terminal** - One terminal window that can't be closed, executes all tactical commands

### Visual Improvements
- [ ] **Enhanced weapon fire graphics** - Show clear lines from weapon rooms to target rooms
- [ ] **FTL-style segmented ship layouts** - Replace rectangle rooms with proper ship shapes like FTL
- [ ] **Multi-enemy tactical display** - Support displaying 2+ enemy ships simultaneously
- [ ] **Better damage indicators** - Show which rooms are being hit in real-time

### New Ship Systems
- [ ] **Add Computer Core component** - Required ship system for all ships
  - Without Computer Core, ship is disabled
  - Can be targeted and destroyed in combat
  - Crew can be teleported to enemy ships to interface with their Computer Core
- [ ] **Add Teleporter module** - Purchasable upgrade
  - Allows crew teleportation to enemy ships
  - Crew can fight enemy crew/robots
  - Crew can hack enemy Computer Core
  - Options: Take over enemy ship, disable it, or destroy it

### Boarding & Hacking Mechanics
- [ ] **Implement crew teleportation** - Send crew to enemy ship
- [ ] **Crew vs. crew combat** - Fighting system when boarding
- [ ] **Computer Core interface** - Hacking minigame or script interface
- [ ] **Ship takeover mechanics** - Control captured enemy ships
- [ ] **Ship disabling** - Leave enemy ship adrift without destroying it

### UI/UX Improvements
- [ ] **Remove/hide galaxy map window** - No longer needed or confusing
- [ ] **Pipe tactical commands to terminal** - Show all tactical clicks as terminal commands
- [ ] **Improve crew assignment UI** - Better visual feedback for crew bonuses
- [ ] **Add ship templates** - Pre-designed ship layouts for variety

### Balance & Polish
- [ ] **Crew skill progression** - Crew gain experience and improve over time
- [ ] **System upgrade tiers** - Weapons/shields/engines can be upgraded
- [ ] **Enemy variety** - More enemy ship types with unique layouts
- [ ] **Boss encounters** - Special enemy ships with unique mechanics

### Documentation
- [x] **Create comprehensive TODO in README** - This section!
- [ ] **Document Computer Core mechanics** - Add to README when implemented
- [ ] **Document Teleporter mechanics** - Add to README when implemented
- [ ] **Update GUI_README.md** - Document new tactical features

---

### Implementation Priority (for fresh context windows)

**Phase 1 - Critical Fixes:**
1. Fix crew weapon damage bonuses (core/weapons.py)
2. Fix hull damage threshold (core/combat.py)
3. Fix window maximize (core/gui/window.py)

**Phase 2 - Tactical Improvements:**
4. Create persistent tactical terminal (core/gui/desktop.py)
5. Enhanced weapon graphics (core/gui/tactical_widget.py)
6. Multi-enemy support (core/gui/tactical_widget.py, core/combat.py)

**Phase 3 - New Systems:**
7. Add Computer Core (core/ship.py, core/ship_os.py)
8. Add Teleporter module (core/ship.py, core/teleporter.py)
9. Implement boarding mechanics (core/boarding.py)

**Phase 4 - Visual Overhaul:**
10. FTL-style ship layouts (core/gui/tactical_widget.py)
11. Remove galaxy map (core/gui/desktop.py)
12. Better damage/combat visuals

---

### How to Continue Development

If starting a fresh context window:
1. Read this README.md for full architecture
2. Check the TODO section above for current priorities
3. Focus on one phase at a time
4. Test each feature thoroughly before moving on

---

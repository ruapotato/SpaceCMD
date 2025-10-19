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

### Core Design Principle: AVOID HARD-CODED PYTHON

**SpaceCMD is script-driven, NOT Python-driven.**

❌ **DON'T:** Write Python functions that implement game behavior
✅ **DO:** Write PoohScript files that implement game behavior

❌ **DON'T:** Create Python AI classes for enemies
✅ **DO:** Create PoohScript files in enemy `/usr/bin/`

❌ **DON'T:** Hard-code combat logic in Python
✅ **DO:** Write PoohScript automation that reads `/proc/` files

**Everything must be hackable. If it's hard-coded in Python, players can't hack it!**

### Architecture

```
┌─────────────────────────────────────┐
│     Game UI (LCARS 3-Panel)         │  Shows ship interiors
├─────────────────────────────────────┤
│   PoohScript Interpreter            │  Executes ALL game logic
├─────────────────────────────────────┤
│     Multiple ShipOS Instances       │  Player + Enemy ships
│  ┌──────────┬──────────┬──────────┐ │
│  │ /proc/   │ /usr/bin/│  VFS +   │ │  Each ship = Unix system
│  │ Status   │ AI Scripts│ Kernel  │ │
│  └──────────┴──────────┴──────────┘ │
├─────────────────────────────────────┤
│   Ship Physics (Minimal Python)     │  Only physics, no AI
└─────────────────────────────────────┘
```

### What's Implemented in PoohScript vs Python

**PoohScript (Hackable):**
- Enemy weapon control AI
- Enemy shield management
- Enemy damage control
- Enemy tactical decisions
- Player automation scripts
- All commands (`status`, `fire`, `power`, etc.)
- Crew bot behavior (future)

**Python (Infrastructure Only):**
- PoohScript interpreter
- VFS/filesystem implementation
- Terminal UI rendering
- Physics calculations (damage, power)
- Network between ship OSes

**The rule:** If a player should be able to hack it, it MUST be PoohScript.

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

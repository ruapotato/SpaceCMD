# SpaceCMD - Hackable Spaceship Operating System

A terminal-based spaceship command simulator powered by **ShipOS** - a complete Unix-like operating system where **everything is a file** and **everything is hackable**.

```
╔═══════════════════════════════════════════════════════════════╗
║                      KESTREL SHIP OS                          ║
║                   HUMAN CRUISER CLASS                         ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🚀 What is SpaceCMD?

SpaceCMD is an FTL-inspired spaceship simulator where you control your ship through a **real scripting language** (PooScript). Every command is a script you can read, modify, and hack. The entire ship is mounted as device files in `/dev`, `/proc`, and `/sys`.

### Key Features

- **Full Unix-like OS**: Shell, VFS, processes, permissions, kernel syscalls
- **PooScript Language**: Python-like scripting language for ship control
- **Everything is Hackable**: All commands are PooScript files you can modify
- **Device File Interface**: Ship systems exposed as `/dev`, `/proc`, `/sys` files
- **Autonomous Crew Bots**: AI-controlled crew that manage repairs and emergencies
- **Beautiful Terminal UI**: LCARS-style interface with animated starfield
- **Real Kernel Syscalls**: Use `kernel.open()`, `kernel.read()`, `kernel.write()`

## 🎮 Quick Start

```bash
# Install (no dependencies beyond Python 3)
git clone https://github.com/ruapotato/SpaceCMD.git
cd SpaceCMD

# Launch the game
python3 play.py

# Or choose a specific ship
python3 play.py --ship kestrel
```

## 📁 The Ship Filesystem

Everything in your ship is accessible as a file:

```
/dev/ship/           - Hardware devices
  ├── hull           - Read hull integrity
  ├── shields        - Read shield strength
  ├── reactor        - Read reactor power
  └── fuel           - Read fuel level

/proc/ship/          - Ship state (like /proc in Linux)
  ├── status         - Complete ship status
  ├── power          - Power allocation info
  └── crew_ai        - Autonomous crew bot status

/sys/ship/           - Ship subsystems (like /sys in Linux)
  ├── systems/       - Individual ship systems
  │   ├── engines/
  │   ├── weapons/
  │   ├── shields/
  │   └── ...
  ├── crew/          - Crew bot status (read-only)
  └── rooms/         - Room status (oxygen, fire, etc)
```

## 🤖 Autonomous Crew Bots

Your crew are **autonomous AI bots** that manage themselves:

- ✅ **Automatically repair** damaged systems
- ✅ **Fight fires** in rooms
- ✅ **Monitor oxygen** levels
- ✅ **Operate systems** efficiently
- ✅ **No manual assignment** needed!

View crew bot activity:
```bash
crew                      # Show what each bot is doing
cat /proc/ship/crew_ai    # View raw AI status
```

Crew bots make intelligent decisions based on ship conditions. You focus on **tactics and power management**, they handle the details!

## 🛠️ Basic Commands

```bash
# Ship status
status              # Show complete ship status
systems             # List all ship systems
crew                # Show autonomous crew bot status
rooms               # Show room status

# Power management
power               # Show power allocation
power shields 3     # Allocate 3 power to shields

# Room control
vent helm           # Toggle venting in helm

# Unix commands
ls /sys/ship/systems    # List systems
cat /dev/ship/hull      # Read hull device
cat /proc/ship/status   # View ship status
cat /proc/ship/crew_ai  # View crew AI activity
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

## 🎯 Architecture

SpaceCMD is built on a layered architecture:

```
┌─────────────────────────────────────┐
│     Game UI (Terminal/LCARS)        │
├─────────────────────────────────────┤
│      PooScript Shell & Commands     │
├─────────────────────────────────────┤
│     ShipOS (Unix-like System)       │
│  ┌──────────┬──────────┬──────────┐ │
│  │   VFS    │ Process  │  Kernel  │ │
│  │          │  Manager │ Syscalls │ │
│  └──────────┴──────────┴──────────┘ │
├─────────────────────────────────────┤
│   Autonomous Crew AI + Ship Physics │
└─────────────────────────────────────┘
```

### Components

- **ShipOS**: Complete Unix-like OS with VFS, processes, permissions
- **PooScript**: Safe Python-subset scripting language
- **Kernel**: Syscall interface (`open`, `read`, `write`, `readdir`)
- **Device Files**: Ship hardware exposed as character devices
- **Crew AI**: Autonomous bots that manage repairs and emergencies
- **Ship Systems**: Physics simulation for power, damage, combat

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

# 💻🚀 SpaceCMD - HACKERS MEET FTL

> A roguelike spaceship game where **every ship is a computer** and you can hack your enemies with real PooScript code.

```
╔═══════════════════════════════════════════════════════════════╗
║                    SPACECMD - HACKERS MEET FTL                ║
║           Command-Line Spaceship Combat Simulator             ║
║                 Every Ship Is A Computer                      ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🎮 What Is SpaceCMD?

**SpaceCMD** is the world's first roguelike where:
- Every ship runs a **real Unix-like OS** (ShipOS)
- You can **hack enemy ships** with actual exploits
- **PooScript programming** is required to win
- Combat combines **FTL-style tactics** with **network hacking**
- All AI and automation is **real executable code**

Think **FTL** meets **Uplink** meets **Unix terminals**.

---

## 🏆 Three Play Modes (Difficulty Progression)

SpaceCMD can be played three ways. **To beat the final boss, you MUST use PooScript automation.**

### 1. 🖥️ GUI Mode (EASY - Visual Learning)

**Best for**: First-time players, learning the game, casual play

**Launch**: `python3 play.py` or `./play_hacker_mode.sh`

**Features:**
- Beautiful desktop environment
- Visual windows and panels
- Tactical ship display
- Galaxy map
- Mouse + keyboard
- Perfect for learning

**You can:** Learn systems, practice combat, explore galaxy
**You cannot:** Beat late-game enemies (too fast for manual play)

```bash
python3 play.py --gui
```

---

### 2. ⌨️ Console Mode (NORMAL - Terminal Mastery)

**Best for**: Terminal users, debugging, practicing commands

**Launch**: `python3 play.py --no-gui --console`

**Features:**
- Pure text interface
- All ship commands
- Real-time combat
- Full hacking system
- Works over SSH
- Professional CLI

**You can:** Master all commands, manual combat, hacking practice
**You cannot:** React fast enough for final boss

```bash
python3 play.py --no-gui --console --ship kestrel
```

**Example session:**
```
Nautilus [COMBAT]> scan
🔍 Enemy has buffer overflow vulnerability

Nautilus [COMBAT]> exploit buffer-overflow weapons
✓ Enemy weapons system crashed!

Nautilus [COMBAT]> malware worm shields
🦠 Worm deployed, damaging shields...

Nautilus [COMBAT]> fire 1
⚡ Hit! Enemy shields down!

Nautilus [COMBAT]> fire 1
💥 Enemy destroyed! +50 scrap
```

---

### 3. 📜 PooScript Mode (HACKER - **REQUIRED TO WIN**)

**Best for**: Programmers, advanced players, BEATING THE GAME

**Launch**: Write `.poo` scripts and execute them

**Features:**
- Full programming language
- Complete filesystem access
- Network hacking automation
- AI combat scripts
- Malware creation
- **THE ONLY WAY TO WIN**

**You can:** Automate everything, write AI, beat final boss
**You must:** Use this mode to win the game!

**Why it's required:**
- ✅ Late-game enemies attack too fast for manual play
- ✅ Final boss has automated defenses
- ✅ Multi-system management needs automation
- ✅ Complex tactics require scripting
- ✅ **Manual play = impossible to win**

**Example combat automation:**
```python
#!/usr/bin/pooscript
# automated_combat.poo - Auto combat script

import os
import time

def auto_combat():
    print("🤖 AUTOMATED COMBAT")

    # Network attack
    os.system("scan")
    os.system("exploit dos weapons")
    os.system("upload-malware worm")

    # Kinetic attack
    os.system("target shields")

    # Auto-fire loop
    while True:
        fd = kernel.open("/proc/ship/weapons", kernel.O_RDONLY)
        weapons = kernel.read(fd, 4096).decode('utf-8')
        kernel.close(fd)

        if "READY" in weapons:
            os.system("fire 1")

        # Check if won
        fd = kernel.open("/proc/ship/enemy", kernel.O_RDONLY)
        enemy = kernel.read(fd, 4096).decode('utf-8')
        kernel.close(fd)

        if "destroyed" in enemy.lower():
            break

        time.sleep(0.5)

    print("✓ Victory!")

auto_combat()
```

**Run it:**
```bash
Nautilus [COMBAT]> pooscript automated_combat.poo
# Sits back and watches automation win
```

---

## 💻 The Hacking System (What Makes This Special)

### Every Ship Is A Computer

- **IP Address**: 192.168.x.x assigned to each ship
- **Open Ports**: SSH (22), HTTP (80), MySQL (3306)
- **Running Services**: Real network services
- **Filesystem**: Complete `/sys/`, `/dev/`, `/proc/` structure
- **Operating System**: Full ShipOS with kernel

### Real Network Hacking

You can actually:
1. **Port scan** enemy ships (nmap-style)
2. **Exploit vulnerabilities** (buffer overflow, SQL injection, etc.)
3. **SSH into enemy ships** for remote access
4. **Upload malware** (real PooScript files!)
5. **Execute code** on their system
6. **Modify their files** to disable systems
7. **Plant backdoors** for persistent access

### Available Exploits

| Exploit | Success | Effect | Real Implementation |
|---------|---------|--------|---------------------|
| **buffer-overflow** | 70% | Crash system | Writes corrupt data to `/sys/ship/systems/X/power` |
| **sql-injection** | 60% | Steal data | Reads `/etc/passwd`, `/proc/ship/status` |
| **backdoor** | 50% | Persistent access | Creates hidden admin user |
| **dos** | 80% | Disable system | Writes `0` to power control file |
| **priv-esc** | 40% | Get root | Sets `current_uid = 0` |
| **zero-day** | 90% | Full compromise | Multi-stage attack combining all |

### Malware Scripts (REAL PooScript Files!)

All malware is **actual executable code** in `/scripts/malware/`:

| Malware | File | What It Does |
|---------|------|--------------|
| **Worm** | `worm.poo` | Self-replicates, damages all systems |
| **Virus** | `virus.poo` | Spreads between systems |
| **Logic Bomb** | `logic_bomb.poo` | Delayed destruction (10sec countdown) |
| **Trojan** | `trojan.poo` | Steals data silently |
| **Rootkit** | `rootkit.poo` | Hides presence, persistent access |
| **Ransomware** | `ransomware.poo` | Encrypts enemy systems |

**Example - worm.poo (REAL PooScript):**
```python
#!/usr/bin/pooscript
# Self-replicating worm

print("🐛 WORM ACTIVATED")

systems = ["weapons", "shields", "engines", "reactor"]
for system in systems:
    # Read current health
    health_path = f"/sys/ship/systems/{system}/health"
    fd = kernel.open(health_path, kernel.O_RDONLY)
    current = int(kernel.read(fd, 16).decode('utf-8'))
    kernel.close(fd)

    # Damage it
    new_health = max(0, current - 10)
    fd = kernel.open(health_path, kernel.O_WRONLY)
    kernel.write(fd, str(new_health).encode('utf-8'))
    kernel.close(fd)

    print(f"✓ Damaged {system}: {current}% → {new_health}%")

# Self-replicate
os.system("cp $0 /tmp/.worm_replica.poo")
print("✓ Replicated to /tmp/")
```

**This code ACTUALLY RUNS on enemy ships and modifies their files!**

---

## 🚀 Quick Start Guide

### Install
```bash
# Clone repo
git clone https://github.com/ruapotato/SpaceCMD.git
cd SpaceCMD

# Install dependencies
pip install pygame  # For GUI mode

# Run game
./play_hacker_mode.sh
```

### Play Modes
```bash
# 1. GUI Mode (Easy - Learn the game)
python3 play.py

# 2. Console Mode (Normal - Master commands)
python3 play.py --no-gui --console --ship kestrel

# 3. Watch Demos
python3 test_hacker_ftl.py        # Hacker gameplay demo
python3 test_real_hacking.py      # Real PooScript demo
```

---

## 📖 Complete Command Reference

### Ship Management
```bash
status              # Full ship status
systems             # List all systems
crew                # Crew roster
power <sys> <n>     # Allocate power to system
assign <crew> <room>  # Assign crew to room
```

### Traditional Combat (FTL-Style)
```bash
target <system>     # Aim weapons at enemy system
fire <n>            # Fire weapon number N
weapons             # List weapons + charge status
enemy               # Enemy ship information
```

### Network Hacking (Unique to SpaceCMD!)
```bash
nmap                # Port scan enemy ship
scan                # Vulnerability scanner
exploit <type> [sys]  # Execute exploit
hack <type> [sys]   # Quick exploit shortcut
malware <type> [sys]  # Deploy malware
ssh-enemy <user>    # SSH into enemy ship
upload-malware <type>  # Upload PooScript malware
hacks               # Show active operations
```

### ShipOS / Filesystem
```bash
ls /systems/        # List ship systems
cat /ship/hull      # Read hull integrity
echo 4 > /systems/shields/power  # Set shield power
cat /proc/ship/status  # Complete status
cat /proc/ship/combat  # Combat state
pooscript script.poo   # Execute PooScript
```

### Galaxy Navigation
```bash
jump <node_id>      # FTL jump to node
cat /proc/ship/location  # Current position
cat /proc/ship/sensors   # Nearby POIs
cat /proc/ship/pois      # Points of interest
```

---

## 🎯 Example Combat Scenarios

### Manual Combat (GUI/Console - Early Game)
```bash
# Turn 1: Recon
Nautilus> scan
[HIGH] Buffer overflow in enemy weapons

# Turn 2: Hack
Nautilus [COMBAT]> exploit buffer-overflow weapons
✓ Enemy weapons crashed!

# Turn 3: Deploy malware
Nautilus [COMBAT]> malware worm shields
🦠 Worm damaging shields over time...

# Turn 4-5: Fire
Nautilus [COMBAT]> target shields
Nautilus [COMBAT]> fire 1
⚡ Hit! Shields 50%

Nautilus [COMBAT]> fire 1
💥 Enemy destroyed! +50 scrap
```

### Automated Combat (PooScript - Required for Late Game)
```python
#!/usr/bin/pooscript
# full_automation.poo

import os, time

print("🤖 FULL COMBAT AUTOMATION")

# Multi-stage network attack
def network_assault():
    os.system("nmap")
    os.system("scan")
    os.system("exploit dos weapons")      # Stop shooting
    os.system("exploit dos shields")      # Drop shields
    os.system("upload-malware worm")      # Constant damage
    os.system("upload-malware logic_bomb weapons")  # Time bomb

# Automated firing
def auto_fire():
    os.system("target shields")

    while True:
        # Check weapon ready
        fd = kernel.open("/proc/ship/weapons", kernel.O_RDONLY)
        w = kernel.read(fd, 4096).decode('utf-8')
        kernel.close(fd)

        if "READY" in w:
            os.system("fire 1")

        # Check enemy status
        fd = kernel.open("/proc/ship/enemy", kernel.O_RDONLY)
        e = kernel.read(fd, 4096).decode('utf-8')
        kernel.close(fd)

        if "destroyed" in e.lower() or "No combat" in e:
            break

        time.sleep(0.5)

# Execute
network_assault()
auto_fire()
print("✓ VICTORY")
```

---

## 🏆 Why PooScript Automation Is REQUIRED

### Early Game (Sectors 1-3)
- ✅ Manual play works fine
- ✅ Enemies are slow
- ✅ Simple tactics sufficient

### Mid Game (Sectors 4-6)
- ⚠️ Enemies get faster
- ⚠️ Manual play becomes difficult
- ✅ Basic scripts help a lot

### Late Game (Sectors 7-8)
- ❌ Manual play nearly impossible
- ❌ Enemies attack instantly
- ✅ Automation required
- ✅ Scripts are the only way

### Final Boss (Rebel Flagship)
- ❌ **IMPOSSIBLE WITHOUT AUTOMATION**
- The flagship has:
  - 4 weapons firing simultaneously
  - Automated repair drones
  - System redundancy
  - Shield regeneration
  - Advanced AI
- You need:
  - Multi-target hacking
  - Auto-repair systems
  - Malware automation
  - Weapon automation
  - **100% scripted combat**

**Manual play will not work. You must learn PooScript to win.**

---

## 📚 Learning Path (Beginner → Expert)

### Week 1: Learn the Game (GUI Mode)
1. Launch GUI mode
2. Complete tutorial
3. Learn ship systems
4. Fight enemies manually
5. Reach sector 3

### Week 2: Master Commands (Console Mode)
1. Switch to console mode
2. Learn all commands
3. Practice hacking
4. Try different ships
5. Reach sector 5

### Week 3: Basic Automation (PooScript)
1. Study `/scripts/bin/*` examples
2. Write first script:
   ```python
   #!/usr/bin/pooscript
   print("My first script!")
   os.system("status")
   ```
3. Create auto-repair script
4. Build auto-fire script
5. Reach sector 6

### Week 4: Advanced Hacking
1. Study `/scripts/malware/*.poo`
2. Write custom exploits
3. Create malware variants
4. Build multi-stage attacks
5. Reach sector 7

### Week 5: Full Automation
1. Combine all skills
2. Create master combat AI
3. Automate everything
4. Beat sector 8
5. **Face the final boss**

### Week 6: VICTORY
1. Deploy full automation
2. Multi-threaded attacks
3. Advanced AI tactics
4. **Defeat the Rebel Flagship**
5. **WIN THE GAME!**

---

## 🎓 PooScript Examples

### Auto-Fire Script
```python
#!/usr/bin/pooscript
# auto_fire.poo - Automatically fire when ready

import time

while True:
    fd = kernel.open("/proc/ship/weapons", kernel.O_RDONLY)
    weapons = kernel.read(fd, 4096).decode('utf-8')
    kernel.close(fd)

    if "READY" in weapons:
        os.system("fire 1")
        print("⚡ Auto-fired weapon 1")

    time.sleep(1)
```

### Auto-Repair Script
```python
#!/usr/bin/pooscript
# auto_repair.poo - Repair critical systems

while True:
    # Check all systems
    fd = kernel.open("/proc/ship/status", kernel.O_RDONLY)
    status = kernel.read(fd, 4096).decode('utf-8')
    kernel.close(fd)

    # If any system < 50% health, repair
    if "health: 49%" in status or "health: 4" in status:
        os.system("repair")
        print("🔧 Auto-repair activated")

    time.sleep(2)
```

### Full Combat AI
```python
#!/usr/bin/pooscript
# combat_ai.poo - Complete combat automation

import os, time

def combat_ai():
    # Phase 1: Recon
    os.system("scan")

    # Phase 2: Disable threats
    os.system("exploit dos weapons")
    os.system("exploit dos shields")

    # Phase 3: Deploy malware
    os.system("upload-malware worm")
    os.system("upload-malware logic_bomb weapons")

    # Phase 4: Attack
    os.system("target shields")

    # Phase 5: Auto-fire loop
    while True:
        fd = kernel.open("/proc/ship/weapons", kernel.O_RDONLY)
        w = kernel.read(fd, 4096).decode('utf-8')
        kernel.close(fd)

        if "READY" in w:
            os.system("fire 1")

        fd = kernel.open("/proc/ship/enemy", kernel.O_RDONLY)
        e = kernel.read(fd, 4096).decode('utf-8')
        kernel.close(fd)

        if "destroyed" in e.lower():
            print("✓ VICTORY")
            break

        time.sleep(0.5)

combat_ai()
```

---

## 🌟 What Makes SpaceCMD Unique

### Traditional Space Games:
```
Click "Fire" → Enemy takes damage → Repeat → Win
```

### SpaceCMD:
```
1. nmap           → Port scan finds SSH open
2. scan           → Buffer overflow detected
3. exploit        → Crash enemy weapons
4. upload worm    → Deploy PooScript malware
5. ssh-enemy      → Get root shell
6. execute code   → Run commands on enemy ship
7. fire weapons   → Finish weakened enemy
8. WIN            → You hacked their ship with REAL code!
```

### Unique Features:
- ✅ **Real programming required** - PooScript is mandatory
- ✅ **Actual exploit execution** - Modify real files
- ✅ **True malware** - Executable PooScript scripts
- ✅ **Network simulation** - Real IPs, ports, services
- ✅ **Complete filesystem** - Unix-like OS
- ✅ **Automation mandatory** - Can't win without scripts
- ✅ **Educational** - Learn hacking + programming
- ✅ **Three difficulty modes** - GUI → Console → PooScript
- ✅ **Hackable enemy AI** - Enemy scripts can be stolen
- ✅ **No Python game logic** - Everything is PooScript

---

## 📁 Project Structure

```
SpaceCMD/
├── play.py                    # Main launcher
├── game.py                    # Roguelike story mode
├── play_hacker_mode.sh        # Quick launcher script
├── core/
│   ├── ship.py               # Ship classes + network config
│   ├── ship_os.py            # ShipOS kernel
│   ├── combat.py             # Combat engine + hacking
│   ├── hacking.py            # Hacking system
│   ├── network_combat.py     # Real PooScript exploits
│   ├── world_manager.py      # Galaxy + encounters
│   ├── game.py               # Game loop
│   └── gui/                  # Desktop environment
├── scripts/
│   ├── bin/                  # Commands (all PooScript)
│   │   ├── nmap             # Port scanner
│   │   ├── scan             # Vulnerability scanner
│   │   ├── exploit          # Exploit execution
│   │   ├── hack             # Quick hack
│   │   ├── malware          # Quick malware
│   │   ├── ssh-enemy        # SSH connection
│   │   ├── upload-malware   # Malware upload
│   │   ├── fire             # Fire weapons
│   │   ├── target           # Target system
│   │   └── status           # Ship status
│   └── malware/              # Malware (all PooScript)
│       ├── worm.poo         # Self-replicating
│       ├── logic_bomb.poo   # Delayed bomb
│       ├── virus.poo        # Spreading virus
│       └── rootkit.poo      # Hidden access
├── test_hacker_ftl.py        # Hacker demo
├── test_real_hacking.py      # Real exploit demo
└── docs/
    ├── README.md             # This file
    ├── HACKERS_FTL_GUIDE.md  # Detailed hacking guide
    ├── REAL_HACKING.md       # PooScript exploit system
    ├── CONSOLE_MODE.md       # Console mode guide
    ├── QUICKSTART_HACKER.md  # 5-minute tutorial
    └── PLAY_MODES.md         # All game modes
```

---

## 🏅 Achievements

- [ ] Complete tutorial
- [ ] Win first combat
- [ ] Reach sector 3 (manual play)
- [ ] Reach sector 5 (console mode)
- [ ] Write first PooScript
- [ ] Deploy all malware types
- [ ] Get root on 10 enemy ships
- [ ] Win combat using only hacking
- [ ] Create automated combat script
- [ ] Reach sector 7 (automation)
- [ ] Beat final boss (full automation)
- [ ] **WIN THE GAME!**

---

## 💡 Pro Tips

1. **Start with GUI** - Learn the game visually
2. **Practice in Console** - Master all commands
3. **Learn PooScript early** - You'll need it
4. **Automate incrementally** - One system at a time
5. **Study examples** - Read `/scripts/bin/*` and `/scripts/malware/*`
6. **Test scripts** - Debug before combat
7. **Save often** - PooScript bugs can be fatal
8. **Network first** - Hack before shooting
9. **Layer attacks** - Combine exploits + malware + weapons
10. **AUTOMATE EVERYTHING** - Required to win

---

## 📖 Documentation

- **README.md** (this file) - Complete overview
- **HACKERS_FTL_GUIDE.md** - Detailed hacking tactics
- **REAL_HACKING.md** - PooScript exploit guide
- **CONSOLE_MODE.md** - Console mode reference
- **QUICKSTART_HACKER.md** - 5-minute quickstart
- **PLAY_MODES.md** - All game modes explained

---

## 🎯 The Philosophy

> **"Every ship is a computer.**
> **Every battle is a network.**
> **Every captain is a hacker.**
> **The best programmer wins."**

SpaceCMD isn't just a game. It's a **programming challenge** where:
- Coding skills give real advantages
- Automation is required to progress
- PooScript knowledge equals power
- The final boss cannot be beaten manually
- **Programming skill = victory**

You're not playing a hacker.
**You ARE a hacker.**

---

## 🚀 Get Started Now

```bash
# Quick start
./play_hacker_mode.sh

# Or choose your mode:
python3 play.py                    # GUI (Easy - Learn)
python3 play.py --no-gui --console # Console (Normal - Master)
# Write PooScript                  # Required to WIN
```

---

## 📝 Remember

1. **GUI Mode** → Learn the game mechanics
2. **Console Mode** → Master all commands
3. **PooScript Mode** → **REQUIRED TO WIN**

**You cannot beat the final boss without automation.**
**Start learning PooScript today!**

---

**Welcome to SpaceCMD.**
**Hack the planet. Hack the galaxy.** 💻🚀

---

*Made with ❤️ by hackers, for hackers*

*"The game that teaches you to automate or die"*

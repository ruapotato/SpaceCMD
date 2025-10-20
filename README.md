# SpaceCMD - Godot Edition

**Hackers meet FTL in 3D space**

A roguelike spaceship game where every ship is a real computer running an OS, and you hack enemies with actual PooScript code - now in full 3D!

## 🎮 Core Concept

You are a **robot crew member** on a spaceship. Every ship (yours and enemies) runs a real operating system with:
- **Unix-like filesystem** (VFS with device files)
- **PooScript processes** (enemy AI, automation scripts)
- **Full OS emulation** per ship (isolated instances)

### Attack Vectors

1. **Physical Boarding** 🤖
   - Walk through your ship in 3D
   - Dock at enemy airlock
   - Fight through their ship
   - Reach their helm terminal
   - Access their OS directly → kill AI processes

2. **Network Exploit** 🔫
   - Purchase exploit (costs scrap)
   - Get within laser range (5-10 units)
   - Fire exploit laser
   - Gain temporary SSH access
   - **Connection lost if you fly too far!**

---

## 📊 Current Status

### ✅ PHASE 1-3 COMPLETE! Combat-Ready System

#### Phase 1: Core OS ✅
**VFS (Virtual File System)** - `core/os/vfs.gd` (~450 lines)
- ✅ Inodes (files, directories, devices, symlinks)
- ✅ Path resolution with permissions
- ✅ Device file support with callbacks
- ✅ Isolated per-ship (each ship has own VFS)

**PooScript Interpreter** - `core/scripting/pooscript.gd` (~270 lines)
- ✅ Process table with PIDs
- ✅ Process states (CREATED, RUNNING, STOPPED, etc.)
- ✅ kill(pid) - Disable enemy AI!
- ✅ Dynamic script execution
- ✅ ps() command

**Kernel Interface** - `core/os/kernel.gd` (~150 lines)
- ✅ File descriptor table (per-process)
- ✅ Syscalls: open/read/write/close/stat/mkdir
- ✅ Safe VFS access from PooScript

#### Phase 2: ShipOS Integration ✅
**ShipOS** - `core/os/ship_os.gd` (~330 lines)
- ✅ VFS + PooScript + Kernel combined per ship
- ✅ 16 device files (/dev/ship/*, /proc/ship/*)
- ✅ Sensor system (nearby_ships, targeting)
- ✅ Weapon firing integration
- ✅ Bi-directional device bridge (ship state ↔ OS)

**Hostile AI** - `scripts/ai/hostile.poo` (~115 lines)
- ✅ Fully autonomous enemy AI
- ✅ Scans sensors for enemies
- ✅ Acquires targets automatically
- ✅ Fires weapons when in range
- ✅ Killable via process termination

#### Phase 3: Combat Manager ✅
**CombatManager** - `core/combat/combat_manager.gd` (~290 lines)
- ✅ Multi-ship battle orchestration
- ✅ Ship management by faction (player/enemy/neutral)
- ✅ Projectile spawning and tracking
- ✅ Collision detection and damage
- ✅ Victory/defeat conditions
- ✅ Signals for game integration

**Projectile** - `core/combat/projectile.gd` (~60 lines)
- ✅ Position/velocity tracking
- ✅ Collision detection
- ✅ Lifetime management

#### Ship Classes
- ✅ **Ship** - Hull, shields, weapons, position (3D combat + 1D galaxy)
- ✅ **Weapon** - Damage, charge, cooldown, firing
- ✅ **Room** - Systems, power, damage states
- ✅ **Crew** - Skills, health, assignments

#### Project Structure
```
SpaceCMD/
├── core/
│   ├── os/          ✅ VFS, Kernel, ShipOS
│   ├── scripting/   ✅ PooScript
│   ├── combat/      ✅ CombatManager, Projectile
│   ├── ship/        ✅ Ship, Weapon, Room, Crew
│   ├── galaxy/      ✅ Stub created
│   └── hacking/     ⏳ To be implemented
├── autoload/        ✅ GameManager, CombatManager
├── tests/           ✅ Comprehensive test suite
├── scripts/ai/      ✅ hostile.poo (working!)
└── project.godot    ✅ Godot 4.4 config
```

**Total Code**: ~2,100 lines | **All Tests**: ✅ Passing

---

## 🚧 Phase 4: Choose Your Direction!

Combat foundation is complete. Pick your next path:

### Option A: Visual Combat (3D Scene) 🎨
- [ ] **Battle scene** (`scenes/combat/battle.tscn`)
  - 3D space environment
  - Camera system
  - Starfield background
- [ ] **Ship visuals**
  - Simple ship models (cubes to start)
  - Engine particle trails
  - Weapon hardpoints
- [ ] **Projectile effects**
  - Laser tracers
  - Hit particles
  - Explosion effects
- [ ] **Combat HUD**
  - Ship status (hull/shields)
  - Target info
  - Weapon charge bars

### Option B: Advanced AI Variants 🤖
- [ ] **aggressive.poo** - Rush tactics, fire constantly
- [ ] **defensive.poo** - Shield focus, retreat when damaged
- [ ] **coward.poo** - Flee on first contact
- [ ] **boss.poo** - Multi-stage attack patterns
- [ ] **kamikaze.poo** - Ram player ship
- [ ] **trader.poo** - Evasive maneuvers only

### Option C: Ship Systems & Power ⚡
- [ ] **Power allocation system**
  - Distribute power between weapons/shields/engines
  - Power affects effectiveness
- [ ] **System damage**
  - Weapons offline when room damaged
  - Engines slow when damaged
  - Shields fail when room breached
- [ ] **Shield recharge**
  - Auto-recharge over time
  - Power allocation affects rate
- [ ] **Crew effectiveness**
  - Skill bonuses to systems
  - Damage/repair mechanics

### Option D: Player Control UI 🎮
- [ ] **Ship status panel**
  - Hull/shields display
  - Power distribution sliders
  - System status indicators
- [ ] **Weapon control**
  - Weapon selection buttons
  - Charge indicators
  - Manual fire controls
- [ ] **Targeting system**
  - Target selection UI
  - Distance/status display
  - Auto-target toggle
- [ ] **Terminal interface**
  - In-game console
  - Command input
  - OS access for hacking

### Option E: Combat Scenarios 🎯
- [ ] **Wave system**
  - Spawn enemies in waves
  - Difficulty progression
  - Reward scrap for victories
- [ ] **Boss encounters**
  - Special boss ships
  - Multi-phase battles
  - Unique AI patterns
- [ ] **Fleet battles**
  - Multiple ships per side
  - Friendly AI ships
  - Formation tactics
- [ ] **Victory conditions**
  - Survive X seconds
  - Protect allied ship
  - Destroy specific target

### Future Phases (Later)
- **Multi-Room Ships** - Interior navigation, room generation
- **Player Bot** - FPS controller, terminal interaction
- **Hacking System** - Network exploits, physical boarding
- **Galaxy Map** - FTL travel, encounters, progression
- **Polish** - Sound, VFX, UI refinement

---

## 🧪 Testing

### Run All Tests
```bash
cd ~/SpaceCMD

# Core systems (VFS, PooScript, Kernel)
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_core_systems.gd

# ShipOS integration (device bridge, sensors, weapons)
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_ship_os.gd

# Hostile AI (autonomous targeting and firing)
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_hostile_ai.gd

# Combat Manager (multi-ship battles, projectiles, damage)
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_combat_simple.gd
```

**Test Coverage**:
- ✅ VFS operations (mkdir, create, read, write, devices)
- ✅ PooScript execution (spawn, kill, ps)
- ✅ Kernel syscalls (open, read, write, close)
- ✅ ShipOS device bridge (16 device files)
- ✅ Sensor system (nearby ships, targeting)
- ✅ Weapon firing integration
- ✅ Hostile AI (scans, targets, fires)
- ✅ Combat orchestration (projectiles, collisions, damage)
- ✅ Victory/defeat conditions

### Quick Demo
```gdscript
# Create ships
var player = Ship.new("USS Enterprise", "Cruiser")
player.position = Vector3(0, 0, 0)
player.os = ShipOS.new(player)

var enemy = Ship.new("Pirate", "Scout")
enemy.position = Vector3(500, 0, 0)
enemy.os = ShipOS.new(enemy)

# Add weapon
var laser = Weapon.new("Burst Laser")
laser.damage = 10.0
laser.charge = 1.0
enemy.weapons.append(laser)

# Register with CombatManager
CombatManager.add_ship(player, "player")
CombatManager.add_ship(enemy, "enemy")
player.os.combat_manager = CombatManager
enemy.os.combat_manager = CombatManager

# Start battle
CombatManager.start_battle()

# Spawn hostile AI
var ai = FileAccess.get_file_as_string("res://scripts/ai/hostile.poo")
enemy.os.vfs.create_file("/bin/hostile.poo", 0x1ED, 0, 0, ai.to_utf8_buffer())
var pid = enemy.os.execute_command("/bin/hostile.poo")

# AI automatically:
# 1. Scans /proc/ship/sensors
# 2. Writes /dev/ship/target
# 3. Fires weapon via /dev/ship/actions/fire
# 4. CombatManager spawns projectile
# 5. Projectile travels and hits player
# 6. Damage applied (shields → hull)

# Player can hack:
enemy.os.kill_process(pid)  # AI disabled!
```

---

## 🎯 Key Architecture Decisions

### 1. PooScript = GDScript
**Decision**: Use GDScript itself as PooScript execution engine

**Why**:
- No need to write Python interpreter in GDScript
- Dynamic script loading/execution built-in
- Full Godot integration
- Still wraps scripts in process isolation

**How**:
```gdscript
# Enemy AI writes a PooScript
var ai_code = """
while true:
    # Fire weapons
    var fd = kernel.sys_open(pid, "/dev/ship/fire", O_WRONLY)
    kernel.sys_write(fd, b"0")
    sleep(1.0)
"""

# PooScript wraps it and executes
var script = GDScript.new()
script.source_code = wrap_as_process(ai_code, pid)
script.reload()
var obj = script.new()
obj.main()  # Runs in background
```

### 2. One OS Instance Per Ship
**Decision**: Each ship gets isolated ShipOS

**Why**:
- True isolation (no shared state bugs)
- Can hack into enemy OS
- Player can board and access different OS
- Different ships can run different AI

**Implementation**:
```gdscript
var player_ship_os = ShipOS.new(player_ship)  # VFS #1
var enemy_ship_os = ShipOS.new(enemy_ship)    # VFS #2

# Completely isolated!
```

### 3. Device Files Bridge Reality
**Decision**: Ship state syncs through device files

**Why**:
- Unix philosophy ("everything is a file")
- PooScript can read/write devices
- GDScript reads devices to render world
- Clean separation of concerns

**Flow**:
```
Enemy AI (PooScript)
  ↓ write("/dev/ship/fire", "0")
Device Handler
  ↓ callback
GDScript
  ↓ fire_weapon_3d(0)
3D World (projectile spawns)
```

---

## 📖 Documentation

- **README.md** (this file) - Overview and TODO
- **ARCHITECTURE.md** - Deep dive into design
- **STATUS.md** - Detailed implementation status
- **project.godot** - Godot 4.4 project config

---

## 🚀 Getting Started (After Tests Pass)

```bash
# 1. Navigate to project root
cd ~/SpaceCMD

# 2. Run tests
../Godot_v4.4.1-stable_linux.x86_64 --headless tests/test_core_systems.gd

# 3. Open in Godot editor
../Godot_v4.4.1-stable_linux.x86_64 --editor .

# 4. (Later) Play the game
# Press F5 in Godot editor
```

---

## 🎮 Gameplay Vision

1. **Start**: You're a bot on your ship. Walk to helm.
2. **Flight**: Access terminal, enter flight mode (3D space).
3. **Encounter**: Enemy ship appears (running hostile.poo AI).
4. **Combat**: Traditional dogfight OR...
5. **Hack**: Buy exploit, fire laser, SSH into enemy OS.
6. **Disable**: `ps aux` → `kill 42` → enemy AI dies.
7. **Board**: Dock, enter their ship, reach helm, take full control.
8. **Control**: Upload friendly.poo, enemy joins your fleet!

---

## 🔥 What Makes This Special

- ✅ **Real OS per ship** - Not fake, actual VFS with processes
- ✅ **Hackable AI** - Kill enemy processes to disable AI
- ✅ **Physical boarding** - Walk through ships in 3D
- ✅ **Scriptable** - Add your own AI/automation
- ✅ **Two attack vectors** - Network exploits OR physical boarding
- ✅ **Range-based hacking** - Maintain connection or lose access
- ✅ **Fully moddable** - Add new AI scripts easily

---

## 📝 Current Status: Phase 3 Complete! 🎉

**Completed**: Combat Manager system
- ✅ Multi-ship battle orchestration
- ✅ Projectile spawning and collision
- ✅ Damage system (shields → hull)
- ✅ Victory/defeat conditions
- ✅ Full AI combat integration

**Next**: Choose Phase 4 direction (see options above)

**Recommended**: Option A (Visual Combat) or Option B (AI Variants) for immediate gameplay impact

---

## 💡 Contributing

This is a demonstration project. Core systems are built, now building the 3D layer on top!

**Want to help?**
- Test the core systems
- Report bugs
- Suggest AI behaviors
- Design ship layouts
- Create PooScript malware scripts

---

**Status**: Phases 1-3 Complete - Combat System Operational! 🚀

*"Every ship is a computer. Every battle is data. Every hit is a syscall."*

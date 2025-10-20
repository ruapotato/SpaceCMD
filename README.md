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

### ✅ COMPLETED (Core Systems)

#### 1. VFS (Virtual File System) - `core/os/vfs.gd`
Complete Unix-like filesystem implementation:
- ✅ Inodes (files, directories, devices, symlinks)
- ✅ Path resolution
- ✅ Permissions (UID/GID, mode bits)
- ✅ Device file support with handlers
- ✅ Complete operations (mkdir, create, read, write, unlink)
- ✅ **Isolated per-ship** (each ship has own VFS)

**Lines**: ~420 | **Tested**: ⏳ Pending

#### 2. PooScript Interpreter - `core/scripting/pooscript.gd`
Process management system for enemy AI:
- ✅ GDScript-powered scripting (PooScript looks like Python/GDScript)
- ✅ Process table with PIDs
- ✅ Process states (CREATED, RUNNING, SLEEPING, STOPPED, ZOMBIE)
- ✅ **kill(pid)** - Kill enemy AI processes!
- ✅ Dynamic script execution
- ✅ Process isolation
- ✅ **ps()** command support

**Lines**: ~270 | **Tested**: ⏳ Pending

**Key Feature**: Player can `kill 42` to stop enemy AI script!

#### 3. Kernel Interface - `core/os/kernel.gd`
Syscall interface for PooScript:
- ✅ File descriptor table (per-process)
- ✅ sys_open/read/write/close
- ✅ sys_stat/mkdir/unlink/readdir
- ✅ Safe VFS access from scripts

**Lines**: ~150 | **Tested**: ⏳ Pending

#### 4. Project Structure
```
SpaceCMD/                    (Godot project root)
├── core/
│   ├── os/          ✅ VFS (420 lines), Kernel (150 lines)
│   ├── scripting/   ✅ PooScript (270 lines)
│   ├── ship/        ✅ Ship, Room, Crew, Weapon classes
│   ├── combat/      ⏳ Stub created
│   ├── hacking/     ⏳ Stub created
│   ├── network/     ⏳ To be implemented
│   └── galaxy/      ⏳ To be implemented
├── autoload/        ✅ GameManager stub
├── tests/           ✅ Test suite created
├── scripts/ai/      ✅ hostile.poo example
├── project.godot    ✅ Godot 4.4 config
└── OG_python_version/  (Original Python implementation)
```

**Total Code**: ~900 lines of core systems ✅

---

## 🚧 TODO

### Phase 1: Testing & Verification ⚠️ **NEXT**
- [ ] **Run test suite headless**
  ```bash
  cd ~/SpaceCMD
  ../Godot_v4.4.1-stable_linux.x86_64 --headless tests/test_core_systems.gd
  ```
- [ ] Fix any VFS bugs
- [ ] Fix any PooScript bugs
- [ ] Fix any Kernel bugs
- [ ] Verify device handlers work

### Phase 2: Integration
- [ ] **Device Bridge** (GDScript ↔ PooScript)
  - Ship state → device file updates
  - Device writes → ship action callbacks
  - Bi-directional sync system
- [ ] **ShipOS Integration** (`core/os/ship_os.gd`)
  - Combine VFS + PooScript + Kernel
  - Mount ship devices (/dev/ship/hull, /proc/ship/status)
  - Auto-spawn init process
  - Update loop (sync ship state ↔ OS state)

### Phase 3: Ship Systems
- [ ] **Complete Ship class** (`core/ship/ship.gd`)
  - Hull, shields, power, resources
  - Rooms dictionary
  - Systems dictionary
  - Crew array
  - Weapons array
- [ ] **Room class** (`core/ship/room.gd`)
  - Position in ship grid
  - System type (HELM, WEAPONS, ENGINES, etc.)
  - Power allocation
  - Health tracking
  - Fire/breach/venting states
- [ ] **Crew class** (`core/ship/crew.gd`)
  - Bot crew members
  - Skills (helm, weapons, shields, etc.)
  - Health tracking
  - Room assignment
- [ ] **Weapon class** (`core/ship/weapon.gd`)
  - Damage, cooldown, charge
  - Range, pierce, missile requirements
  - Weapon types (laser, beam, missile)

### Phase 4: Multi-Room Ship Generation
- [ ] **Ship layout generator** (`core/ship/ship_generator.gd`)
  - Room graph (connectivity)
  - Programmatic generation (like FTL)
  - Different ship classes (Kestrel, Stealth Cruiser, etc.)
- [ ] **3D mesh generation**
  - Room boxes (walls, floor, ceiling)
  - Doorways between connected rooms
  - Terminal positions (helm, weapons, engines)
  - Airlock locations
- [ ] **Interior navigation**
  - Navmesh for bot movement
  - Door collision/interaction
  - Room transitions

### Phase 5: Player Bot Controller
- [ ] **FPS controller** (`scenes/player/player_bot.gd`)
  - CharacterBody3D
  - WASD movement
  - Mouse look
  - Interact with terminals
  - Interact with doors
- [ ] **Terminal interaction**
  - Raycast to detect terminal
  - Prompt to access (E key)
  - Open terminal UI
  - Connected to ShipOS of current ship

### Phase 6: Terminal UI
- [ ] **In-world terminal** (`scenes/ui/terminal.gd`)
  - VT100-style text display
  - Keyboard input capture
  - Command history (up/down arrows)
  - Connected to ShipOS instance
  - Display stdout/stderr
- [ ] **Terminal commands**
  - ls, cd, cat, mkdir
  - ps, kill
  - cat /dev/ship/hull
  - cat /proc/ship/status
  - pooscript /bin/script.poo

### Phase 7: Enemy AI & Scripts
- [ ] **Basic enemy AI** (`scripts/ai/hostile.poo`)
  - Read /proc/ship/weapons
  - Write to /dev/ship/fire
  - Auto-targeting logic
  - Weapon charging checks
- [ ] **Advanced AI variants**
  - `aggressive.poo` - Rush and overwhelm
  - `defensive.poo` - Shields up, retreat when damaged
  - `kamikaze.poo` - Ram player ship
  - `coward.poo` - Run away immediately
- [ ] **AI process spawning**
  - Auto-spawn on ship creation
  - Different AI per ship type
  - Boss ships with multi-stage AI

### Phase 8: Combat System
- [ ] **Combat state** (`core/combat/combat_state.gd`)
  - Turn-based or real-time?
  - Weapon firing logic
  - Damage calculation
  - Shield mechanics
  - System damage
- [ ] **3D combat visuals**
  - Projectile spawning
  - Weapon firing effects
  - Shield hit effects
  - Explosion effects
  - Hull damage visuals

### Phase 9: Hacking System
- [ ] **Network exploits** (`core/hacking/hacking_system.gd`)
  - Exploit types (buffer overflow, zero-day, backdoor)
  - Range-based connection
  - Temporary SSH access
  - Connection drops if too far
- [ ] **Exploit laser weapon**
  - 3D projectile
  - On hit: grant OS access
  - Duration timer
  - Range limits
- [ ] **Physical boarding**
  - Airlock docking
  - Load enemy ship interior
  - Navigate to helm
  - Access terminal → full control

### Phase 10: Galaxy & World
- [ ] **Galaxy manager** (`core/galaxy/galaxy.gd`)
  - 1D linear galaxy (distance from center)
  - POI system (stores, encounters, nebulas)
  - Difficulty scaling
- [ ] **Ship spawning**
  - Random enemy ships
  - Different factions
  - Boss encounters
- [ ] **FTL travel**
  - Jump between locations
  - Dark matter fuel cost
  - Encounters along the way

### Phase 11: 3D Flight & Dogfighting
- [ ] **Player ship 3D** (`scenes/space/player_ship.tscn`)
  - Ship mesh
  - Engine trail particles
  - Weapon hardpoints
- [ ] **Flight controls**
  - WASD thrust
  - Mouse look for aiming
  - Space for primary fire
  - Shift for boost
- [ ] **Manual targeting**
  - Crosshair in 3D space
  - Lead indicator
  - Range indicators
  - Auto-targeting (shorter range)

### Phase 12: Polish & Effects
- [ ] **Sound effects**
  - Weapon firing
  - Explosions
  - Shield hits
  - Engine sounds
  - Terminal beeps
- [ ] **Particle effects**
  - Engine trails
  - Weapon shots
  - Explosions
  - Shield impacts
- [ ] **UI/HUD**
  - Ship status display
  - Weapon charge bars
  - Target info
  - Minimap
- [ ] **Galaxy map**
  - Visual representation
  - POI markers
  - Current location
  - Jump destinations

---

## 🧪 Testing

### Headless Tests (Core Systems)
```bash
# Navigate to project root
cd ~/SpaceCMD

# Run test suite (no graphics needed)
../Godot_v4.4.1-stable_linux.x86_64 --headless tests/test_core_systems.gd
```

**Tests**:
- ✅ VFS operations (mkdir, create, read, write, devices)
- ✅ PooScript execution (spawn, kill, ps)
- ✅ Kernel syscalls (open, read, write, close)

### Expected Output
```
============================================================
SPACECMD CORE SYSTEMS TEST
============================================================

[TEST 1: VFS]
✓ VFS created
✓ Root directory exists
✓ Created /test directory
✓ Created /test/hello.txt
✓ Read file contents: Hello from VFS!
✓ Listed directory, found 3 entries
✓ Device file works: Device data
✅ VFS: ALL TESTS PASSED

[TEST 2: PooScript]
✓ PooScript created
✓ Created test script
[PID 2] Hello from PooScript!
[PID 2] Sum: 30
✓ Spawned script with PID: 2
✓ Process found in table
✓ ps() returned 1 process(es)
  PID: 2 CMD: /test_script.poo STATE: RUNNING
✓ Killed process 2
✓ Process state is STOPPED
✅ PooScript: ALL TESTS PASSED

[TEST 3: Kernel]
✓ Kernel created
✓ Opened file with FD: 3
✓ Read data: Kernel test data
✓ Closed file
✓ Wrote 8 bytes
✓ Verified written data: New data
✓ stat() returned size: 8
✓ Created directory via kernel
✓ readdir() returned 13 entries
✅ Kernel: ALL TESTS PASSED

============================================================
ALL TESTS COMPLETE
============================================================
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

## 📝 Current Sprint: Phase 1 Testing

**Goal**: Verify core systems work correctly

**Tasks**:
1. Run test suite
2. Fix any bugs
3. Document test results
4. Move to Phase 2 (Device Bridge)

**Status**: ⏳ Ready to test

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

**Status**: Core OS complete, building spaceship! 🚀

*"Every ship is a computer. Every computer can be hacked."*

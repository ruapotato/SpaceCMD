# SpaceCMD Architecture

## Core Philosophy

**"Every ship is a computer. Every computer can be hacked."**

### The Two Layers

#### Layer 1: GDScript (Physical Reality)
- 3D world, physics, rendering
- Player bot movement (FPS controller)
- Ship hulls, weapons, projectiles
- **Reads** `/dev/ship/*` device files to display OS state
- **Writes** player actions to device files
- Updates world based on OS state

#### Layer 2: PooScript (Operating System)
- **ALL ship logic** runs as PooScript processes
- Each ship has isolated ShipOS instance
- Enemy AI = hostile PooScript scripts
- Ship automation = PooScript daemons
- Fully hackable, modifiable, killable

## Player is a Bot

- You ARE a crew member (robot)
- Walk around your ship in 3D
- **Helm station** → access ship terminal
- **Weapons station** → manual aiming/firing
- **Engine room** → see power systems
- **Airlock** → board enemy ships

## Multi-Ship OS Instances

```
┌──────────────────────────────────────────────────────────┐
│                     GDScript World                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ 3D Ship #1  │  │ 3D Ship #2  │  │ 3D Ship #3  │      │
│  │ (Player)    │  │ (Enemy)     │  │ (Enemy)     │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
└─────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
     ┌─────────┐       ┌─────────┐       ┌─────────┐
     │ ShipOS  │       │ ShipOS  │       │ ShipOS  │
     │ 192.168 │◄─────►│ 192.168 │◄─────►│ 192.168 │
     │ .1.1    │Network│ .1.2    │Network│ .1.3    │
     └────┬────┘       └────┬────┘       └────┬────┘
          │                 │                 │
     ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
     │ VFS     │       │ VFS     │       │ VFS     │
     │ PooScript│      │ PooScript│      │ PooScript│
     └────┬────┘       └────┬────┘       └────┬────┘
          │                 │                 │
     ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
     │ Processes│      │ Processes│      │ Processes│
     │ ────────│       │ ────────│       │ ────────│
     │ pilot.poo│      │ hostile │       │ kamikaze│
     │ repair.poo│     │ .poo    │       │ .poo    │
     │ auto_fire│      │ (PID 42)│       │ (PID 15)│
     └─────────┘       └─────────┘       └─────────┘
```

Each ship:
1. Has **isolated ShipOS** with own VFS
2. Runs **PooScript processes** (AI, automation)
3. Exposes **/dev/ship/** device files
4. GDScript reads devices to render world

## Attack Vectors

### Vector 1: Physical Boarding 🤖

**Steps:**
1. Maneuver close to enemy ship (3D flight)
2. Dock at their airlock
3. Enter enemy ship (load their interior)
4. Fight through rooms
5. Reach helm terminal
6. Access **their ShipOS** directly
7. Full root control (kill AI, take over)

**Pros:** Permanent access, no resources
**Cons:** Dangerous, crew can fight back, can die

### Vector 2: Network Exploit Laser 🔫

**Steps:**
1. Purchase exploit (costs 50-200 scrap)
2. Get within laser range (5-10 units)
3. Fire exploit laser at enemy
4. Gain **temporary SSH access**
5. Kill enemy AI scripts
6. **Connection lost** if range exceeds limit

**Pros:** Safe, can hack multiple ships
**Cons:** Costs resources, range-limited, temporary

**Exploit Types:**
- **Buffer Overflow** - 50 scrap, range 5, 60 sec duration
- **Zero-Day** - 200 scrap, range 10, 300 sec duration
- **Backdoor** - 150 scrap, permanent (until reboot)

## Device File Bridge

### Reading (PooScript → GDScript)

PooScript writes to device files:
```python
# enemy_ai.poo running on enemy ship
fd = kernel.open("/dev/ship/target", kernel.O_WRONLY)
kernel.write(fd, b"player_ship")  # Target player
kernel.close(fd)

fd = kernel.open("/dev/ship/fire", kernel.O_WRONLY)
kernel.write(fd, b"0")  # Fire weapon 0
kernel.close(fd)
```

GDScript reads device state:
```gdscript
# enemy_ship.gd
func _process(delta):
    var target = ship_os.read_device("/dev/ship/target")
    var fire_cmd = ship_os.read_device("/dev/ship/fire")
    if fire_cmd == "0":
        fire_weapon(0)
```

### Writing (GDScript → PooScript)

Player action updates devices:
```gdscript
# player_controller.gd
func _input(event):
    if event.is_action_pressed("fire"):
        ship_os.write_device("/dev/ship/fire", "0")
```

PooScript reads device:
```python
# auto_fire.poo
fd = kernel.open("/dev/ship/fire", kernel.O_RDONLY)
fire_status = kernel.read(fd, 1024)
kernel.close(fd)
```

## Multi-Room Ship Generation

Ships are generated programmatically with room graph:

```gdscript
# ship_generator.gd
func generate_kestrel_layout() -> Dictionary:
    var rooms = {
        "helm": {
            "system": Room.SystemType.HELM,
            "pos": Vector3(0, 0, 0),
            "size": Vector3(3, 2, 3),
            "connected_to": ["corridor_1", "weapons"]
        },
        "weapons": {
            "system": Room.SystemType.WEAPONS,
            "pos": Vector3(4, 0, 0),
            "size": Vector3(3, 2, 3),
            "connected_to": ["helm", "corridor_2"]
        },
        "engines": {
            "system": Room.SystemType.ENGINES,
            "pos": Vector3(8, 0, 0),
            "size": Vector3(3, 2, 3),
            "connected_to": ["corridor_2"]
        },
        # ... more rooms
    }
    return rooms
```

Each room:
- 3D mesh (walls, floor, ceiling)
- Doors to connected rooms
- System terminals (helm, weapons, etc.)
- Crew spawn points

## Hacking Gameplay Loop

### Scenario: Player vs Enemy Ship

1. **Engagement**
   - Enemy AI script starts: `hostile.poo` (PID 42)
   - Enemy shoots at player automatically

2. **Option A: Buy Exploit**
   - Player: "Purchase Buffer Overflow Exploit" (50 scrap)
   - Get within 5 units
   - Fire exploit laser → gain SSH access
   - Terminal: `ps aux` → see PID 42 `hostile.poo`
   - Terminal: `kill 42` → enemy AI dies
   - Enemy ship now drifting (no AI)

3. **Option B: Board Ship**
   - Maneuver to enemy airlock
   - Exit player ship → EVA in space
   - Enter enemy airlock
   - Fight enemy crew bots
   - Reach enemy helm
   - Access terminal → full control
   - Upload `friendly.poo` → ship joins your fleet

4. **Option C: Traditional Combat**
   - Just shoot them with weapons
   - Destroy systems one by one
   - Eventually destroy ship

## PooScript Process Examples

### Player Ship Automation
```python
#!/usr/bin/pooscript
# auto_repair.poo - Repairs damaged systems

while True:
    # Read all system health
    for system in ["weapons", "shields", "engines"]:
        fd = kernel.open(f"/sys/ship/systems/{system}/health", kernel.O_RDONLY)
        health = float(kernel.read(fd, 16).decode())
        kernel.close(fd)

        if health < 0.5:
            print(f"⚠️ {system} damaged! Repairing...")
            # Repair takes time
            sleep(5.0)
            # Mark as repaired

    sleep(1.0)
```

### Enemy AI Script
```python
#!/usr/bin/pooscript
# hostile.poo - Basic enemy AI

print("🔴 HOSTILE AI ACTIVATED")

while True:
    # Target player
    fd = kernel.open("/dev/ship/target", kernel.O_WRONLY)
    kernel.write(fd, b"player_ship")
    kernel.close(fd)

    # Check weapon ready
    fd = kernel.open("/proc/ship/weapons", kernel.O_RDONLY)
    weapons = kernel.read(fd, 4096).decode()
    kernel.close(fd)

    if "READY" in weapons:
        # Fire!
        fd = kernel.open("/dev/ship/fire", kernel.O_WRONLY)
        kernel.write(fd, b"0")
        kernel.close(fd)

    sleep(0.5)
```

## Implementation Order

1. **VFS + Device Files** ✓
2. **PooScript Interpreter** ✓
3. **Ship Class with Multi-Room Layout**
4. **Device Bridge (GDScript ↔ PooScript)**
5. **Player Bot FPS Controller**
6. **Terminal UI at Helm**
7. **Enemy AI PooScript Processes**
8. **Network Exploit System (range-based)**
9. **Boarding Mechanics (airlock → interior)**

## Key Features

- ✅ Each ship = isolated OS instance
- ✅ All AI = PooScript processes
- ✅ Player = bot walking around ship
- ✅ Helm = terminal access
- ✅ Physical boarding = full access
- ✅ Network exploits = temporary ranged access
- ✅ Kill enemy AI scripts to disable ships
- ✅ Upload your own scripts to control enemies
- ✅ Multi-room 3D ship interiors

---

**Core Loop:**
```
Fly → Engage → Hack/Board → Control → Profit → Upgrade → Repeat
```

# SpaceCMD Architecture Summary

## Proper Layer Separation

The game now follows correct architectural separation:

### **Python Layer (World Control)**
Controls the external world and everything outside the ship:
- **WorldManager** (`core/world_manager.py`)
  - Spawns enemies
  - Manages combat encounters
  - Handles world events
  - Detects damage and triggers screen flashes
  - Responds to ship signals (distress beacons, scans)

### **ShipOS Layer (Ship Control)**
Controls only the ship's internal systems:
- **ShipOS** (`core/ship_os.py`)
  - Ship systems (engines, weapons, shields)
  - Crew management (autonomous bots)
  - Internal OS functions
  - Device files for ship hardware
  - **Does NOT spawn enemies**

## How It Works

### 1. **Enemy Encounters** (Python → ShipOS)
```
[WorldManager] → Spawns enemy → Attacks ship
                                     ↓
                              [ShipOS] Reacts to damage
```

### 2. **Hostile Script** (ShipOS → Python)
```
Player runs: /tmp/hostile.poo
     ↓
Writes to: /dev/ship/beacon
     ↓
[ShipOS] Device file activated
     ↓
[WorldManager] Detects beacon signal
     ↓
[WorldManager] Spawns enemy encounter!
```

### 3. **Combat Flow**
```
[WorldManager]
  ├─ Creates enemy ship
  ├─ Manages CombatState
  ├─ Updates combat (10 FPS)
  └─ Detects damage → Triggers screen flash

[ShipOS]
  └─ Updates ship physics (crew, oxygen, etc)
```

## Key Files

### Created/Modified Files:
1. **`core/world_manager.py`** - NEW! Python world control
2. **`core/gui/file_browser.py`** - Enhanced with gamification
3. **`core/gui/desktop.py`** - Added attack flash effect
4. **`core/enemy_ships.py`** - Added gnat-class enemy
5. **`core/ship_os.py`** - Removed combat logic, added beacon device
6. **`play.py`** - Wired up WorldManager

### Device Files:
- **`/dev/ship/beacon`** - Distress beacon control (read/write)
  - Write `1` to activate (attracts enemies!)
  - Write `0` to deactivate
  - Read to check status

- **`/dev/ship/hull`** - Hull integrity (read-only)
- **`/dev/ship/shields`** - Shield status (read-only)
- **`/proc/ship/status`** - Complete ship status
- **`/proc/ship/crew_ai`** - Autonomous crew AI status

### Scripts:
- **`/tmp/hostile.poo`** - Hostile malware (tutorial)
  - Activates distress beacon
  - Demonstrates hostile code execution
  - World responds by spawning enemies

## Tutorial Enemy: Gnat-Class Drone

Perfect for learning combat:
- **5 HP** (very weak)
- **0 shields** (no defense)
- **0.5 damage** per shot (minimal threat)
- **12s cooldown** (slow firing)
- **5 scrap** reward

## Enhanced Features

### File Browser
- Breadcrumb navigation
- Back/Forward/Up buttons
- Visual flash effects
- Smooth scrolling
- File type icons (🐍 Python, ⚙️ Shell, ⚡ Executable)
- Keyboard shortcuts (Alt+Left/Right, Backspace)

### Screen Flash Effect
- Red flash on damage
- Intensity scales with damage
- Smooth fade-out animation

## How to Play

1. **Launch the game:**
   ```bash
   python3 play.py
   ```

2. **Tutorial enemy spawns after 5 seconds automatically!**

3. **Or manually trigger with hostile script:**
   ```bash
   # In game terminal:
   /tmp/hostile.poo
   ```

4. **Or manually activate beacon:**
   ```bash
   echo 1 > /dev/ship/beacon
   ```

5. **Watch the screen flash red when damaged!**

6. **To stop attracting enemies:**
   ```bash
   echo 0 > /dev/ship/beacon
   ```

## Architecture Benefits

✅ **Separation of Concerns**
  - Python controls world
  - ShipOS controls ship

✅ **Realistic Simulation**
  - Enemies attack from outside
  - Ship reacts to attacks

✅ **Modular Design**
  - Easy to add new enemy types
  - Easy to add world events

✅ **Maintainable**
  - Clear boundaries
  - No mixed responsibilities

## Testing

Run the architecture test:
```bash
python3 test_world_architecture.py
```

This verifies:
- WorldManager controls encounters ✓
- ShipOS controls ship systems ✓
- Beacon device works ✓
- Hostile script exists ✓
- Proper layer separation ✓

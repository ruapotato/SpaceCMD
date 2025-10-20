# Combat Manager Implementation Complete

**Date:** October 20, 2025
**Phase:** Phase 3 - Combat Orchestration

## Summary

Successfully implemented the **Combat Manager** system that orchestrates multi-ship battles in SpaceCMD. The Combat Manager ties together all existing systems (ships, weapons, ShipOS, AI) into a cohesive combat system.

## What Was Built

### 1. Projectile Class (`core/combat/projectile.gd`)

A lightweight class representing fired weapons:
- Position and velocity tracking
- Collision detection
- Damage delivery
- Lifetime management (auto-despawn after 10s)
- ~60 lines of code

**Key Features:**
- `update(delta)` - Updates position each frame
- `check_hit(ship, radius)` - Collision detection
- Stores owner ship, target ship, and damage amount

### 2. CombatManager Singleton (`core/combat/combat_manager.gd`)

The main orchestrator for all combat operations:
- ~290 lines of code
- Registered as autoload in `project.godot`
- Manages all ships, projectiles, and combat state

**Key Responsibilities:**

**Ship Management:**
- Track ships by faction (player, enemy, neutral)
- `add_ship()`, `remove_ship()`, `get_ship_faction()`
- Automatic nearby_ships array updates for all ShipOS instances

**Projectile System:**
- `spawn_projectile()` - Create projectiles when weapons fire
- `process_projectiles()` - Move projectiles and detect hits
- Collision detection with configurable hit radius (default: 50 units)

**Damage System:**
- `apply_damage()` - Handles shields-first, then hull damage
- `handle_ship_destroyed()` - Cleanup when ships die
- Kills all processes on destroyed ship's OS

**Victory Conditions:**
- `check_victory_conditions()` - Checks win/loss each frame
- Emits signals: `battle_won`, `battle_lost`, `all_enemies_destroyed`

**Signals:**
- `ship_added(ship, faction)`
- `ship_destroyed(ship, faction)`
- `projectile_spawned(projectile)`
- `projectile_hit(projectile, target)`
- `battle_won(faction)`
- `battle_lost()`
- `all_enemies_destroyed()`

### 3. Ship Class Updates (`core/ship/ship.gd`)

Extended Ship class to support combat:
- Added `position: Vector3` for 3D combat space (separate from 1D galaxy_position)
- Added `os: ShipOS` reference to store ship's OS
- Added `name` property alias for `ship_name` (convenience for combat system)

### 4. ShipOS Integration (`core/os/ship_os.gd`)

Updated weapon firing to integrate with CombatManager:
- Added `combat_manager` reference (set externally)
- `_write_fire_weapon()` now calls `combat_manager.spawn_projectile()`
- Requires target to be selected before firing
- Automatically spawns projectiles when AI or player fires weapons

## How It Works

### Combat Flow

```
1. Ships register with CombatManager on spawn
   ├─ CombatManager.add_ship(ship, "player" or "enemy")
   └─ Ship added to faction list and all_ships array

2. Battle starts
   ├─ CombatManager.start_battle()
   └─ Activates _process() loop

3. Each frame (_process):
   ├─ Update projectiles → move → check collisions
   ├─ Update nearby_ships for all ShipOS instances
   └─ Check victory/defeat conditions

4. AI/Player fires weapon
   ├─ AI writes to /dev/ship/actions/fire
   ├─ ShipOS._write_fire_weapon() called
   ├─ weapon.fire() consumes charge
   └─ combat_manager.spawn_projectile() creates projectile

5. Projectile travels
   ├─ projectile.update(delta) moves it
   ├─ Checks collision with all ships
   └─ On hit: apply_damage() called

6. Damage applied
   ├─ Shields absorb damage first
   ├─ Remaining damage → hull
   └─ If hull <= 0: ship_destroyed

7. Victory check
   ├─ If all enemies destroyed: battle_won
   ├─ If player destroyed: battle_lost
   └─ Auto end_battle()
```

### Integration Example

```gdscript
# Create ships
var player = Ship.new("USS Enterprise", "Cruiser")
player.position = Vector3(0, 0, 0)
player.os = ShipOS.new(player)

var enemy = Ship.new("Pirate", "Scout")
enemy.position = Vector3(500, 0, 0)
enemy.os = ShipOS.new(enemy)

# Add weapons
var laser = Weapon.new("Burst Laser")
laser.damage = 10.0
laser.charge = 1.0
enemy.weapons.append(laser)

# Register ships with CombatManager
CombatManager.add_ship(player, "player")
CombatManager.add_ship(enemy, "enemy")

# Set combat_manager reference so ShipOS can spawn projectiles
player.os.combat_manager = CombatManager
enemy.os.combat_manager = CombatManager

# Start battle
CombatManager.start_battle()

# Spawn AI on enemy ship
var ai_code = FileAccess.get_file_as_string("res://scripts/ai/hostile.poo")
enemy.os.vfs.create_file("/bin/hostile.poo", 0x1ED, 0, 0, ai_code.to_utf8_buffer())
var ai_pid = enemy.os.execute_command("/bin/hostile.poo")

# Each frame:
# - enemy.os.update(delta) runs AI
# - AI targets player and fires
# - CombatManager spawns projectile
# - Projectile travels and hits player
# - Damage applied to player shields/hull
```

## Test Results

Created `tests/test_combat_simple.gd` - All tests pass:
- ✓ CombatManager initialization
- ✓ Ship registration (player/enemy factions)
- ✓ Projectile spawning
- ✓ Damage system (shields → hull)
- ✓ Ship destruction

**Existing Tests Still Pass:**
- ✓ Core systems (VFS, PooScript, Kernel)
- ✓ ShipOS integration
- ✓ Hostile AI (AI successfully targets and fires weapons)

## Technical Notes

### Coordinate Systems

SpaceCMD uses **two coordinate systems**:

1. **Galaxy Map (1D):** `ship.galaxy_position` (float)
   - Used for navigation between star systems
   - Linear position on galaxy map

2. **Combat Space (3D):** `ship.position` (Vector3)
   - Used during battles
   - Full 3D positioning for combat

CombatManager uses `position` (Vector3) for battles. The `nearby_ships` array in ShipOS currently uses `galaxy_position` for compatibility with existing sensor code, but this can be updated to use 3D distance when needed.

### Projectile Preloading

CombatManager uses `preload()` to load the Projectile class dynamically:
```gdscript
const ProjectileClass = preload("res://core/combat/projectile.gd")
var projectile = ProjectileClass.new(...)
```

This avoids parse-time dependency issues with class_name declarations in Godot 4.4.

### ShipOS Combat Integration

ShipOS stores a reference to CombatManager:
```gdscript
ship.os.combat_manager = CombatManager
```

When weapons fire, ShipOS checks this reference and calls `spawn_projectile()` if available. This allows the system to work with or without CombatManager active.

## Files Created

- `core/combat/projectile.gd` - Projectile class (~60 lines)
- `core/combat/combat_manager.gd` - Combat orchestrator (~290 lines)
- `tests/test_combat_simple.gd` - Basic combat tests (~70 lines)
- `tests/test_combat_manager.gd` - Comprehensive tests (~390 lines)
- `tests/test_minimal.gd` - Minimal smoke test (~15 lines)

## Files Modified

- `core/ship/ship.gd` - Added position (Vector3), os, and name alias
- `core/os/ship_os.gd` - Added combat_manager ref, integrated weapon firing
- `project.godot` - Registered CombatManager as autoload
- Minor fixes to VFS, Kernel, PooScript (octal → hex conversions for Godot 4.4)

## What This Enables

With CombatManager complete, you can now:

✅ **Orchestrate multi-ship battles**
- Add any number of ships to combat
- Automatic faction management (player vs enemy)
- Ships auto-detect nearby enemies via sensors

✅ **Full combat lifecycle**
- Projectile spawning, movement, collision
- Damage application (shields → hull)
- Ship destruction handling
- Victory/defeat detection

✅ **AI-driven combat**
- AI scripts fire weapons via `/dev/ship/actions/fire`
- CombatManager spawns projectiles automatically
- AI can be disabled by killing its process

✅ **Player control integration**
- Players can fire weapons same way as AI
- Manual targeting via `/dev/ship/target`
- Full control over when to fire

## Next Steps (Phase 4 Options)

The combat system foundation is complete. Choose your next direction:

**A. Visual Combat (3D Scene)**
- Create 3D battle scene
- Ship models (basic cubes to start)
- Projectile visuals (tracers, particles)
- Camera system
- Health bars and UI

**B. Advanced AI**
- `aggressive.poo` - Rush tactics
- `defensive.poo` - Shield focus, retreat when damaged
- `coward.poo` - Flee on first hit
- `boss.poo` - Multi-stage attack patterns

**C. Ship Systems**
- Power allocation between weapons/shields/engines
- System damage (weapons go offline when room damaged)
- Crew effectiveness bonuses
- Shield recharge mechanics
- Repair actions

**D. Player Control UI**
- Ship status panel (hull, shields, power)
- Weapon selection and firing buttons
- Target selection UI
- Power allocation sliders
- Console/terminal interface for hacking

**E. Combat Scenarios**
- Waves of enemies
- Boss battles
- Fleet battles (multiple ships per side)
- Different victory conditions (survive X seconds, protect ship, etc.)

## Quick Commands

```bash
# Run combat test
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_combat_simple.gd

# Run hostile AI test (shows AI firing weapons)
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_hostile_ai.gd

# Run full ShipOS test suite
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_ship_os.gd
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    CombatManager                        │
│  (Singleton, Autoload, _process() each frame)           │
├─────────────────────────────────────────────────────────┤
│  Ships:                                                 │
│    ├─ player: [Ship, Ship, ...]                        │
│    ├─ enemy: [Ship, Ship, ...]                         │
│    └─ neutral: [Ship, Ship, ...]                       │
│                                                         │
│  Projectiles: [Projectile, Projectile, ...]           │
│                                                         │
│  Each Frame:                                            │
│    1. Move projectiles → check collisions              │
│    2. Update nearby_ships for all ShipOS              │
│    3. Check victory conditions                          │
└─────────────────────────────────────────────────────────┘
                       │
                       │ manages
                       ↓
    ┌──────────────────────────────────────┐
    │             Ship                     │
    │  ┌────────────────────────────────┐  │
    │  │  ShipOS                        │  │
    │  │  ├─ VFS (device files)        │  │
    │  │  ├─ PooScript (AI processes)   │  │
    │  │  ├─ Kernel (syscalls)         │  │
    │  │  └─ combat_manager ref         │  │
    │  └────────────────────────────────┘  │
    │                                      │
    │  position: Vector3                   │
    │  hull, shields, weapons              │
    └──────────────────────────────────────┘
                       │
                       │ AI fires weapon
                       ↓
          ShipOS._write_fire_weapon()
                       │
                       │ calls
                       ↓
       CombatManager.spawn_projectile()
                       │
                       │ creates
                       ↓
              ┌────────────────┐
              │  Projectile    │
              │  ├─ position   │
              │  ├─ velocity   │
              │  ├─ damage     │
              │  └─ owner/target│
              └────────────────┘
                       │
                       │ travels each frame
                       ↓
              check_hit(ship, radius)
                       │
                       │ on hit
                       ↓
        CombatManager.apply_damage()
                       │
                       ↓
          shields → hull → destroyed
```

---

**Status:** ✅ Phase 3 Complete - Combat Manager Operational
**Next:** Choose Phase 4 direction (Visual, AI, Systems, UI, or Scenarios)

*"Every battle is data. Every hit is a syscall. Every victory is root access."* 🚀

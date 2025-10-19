# SpaceCMD Kernel Architecture

## Core Principle: Python is the Kernel

**The Python layer enforces ALL game rules. PooScripts cannot bypass them.**

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: USER SPACE (PooScripts)                       │
│  - Enemy AI scripts                                     │
│  - Player automation scripts                            │
│  - Shell commands                                       │
│  ⚠️  CAN BE HACKED - don't trust these!                │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: SYSTEM CALLS (ShipOS)                        │
│  - fire weapon                                          │
│  - allocate power                                       │
│  - move crew                                            │
│  → Calls Python kernel for validation                   │
├─────────────────────────────────────────────────────────┤
│  LAYER 1: KERNEL (Python)                              │
│  - Enforces physics rules                               │
│  - Validates all operations                             │
│  - Returns errors when invalid                          │
│  ✅ CANNOT BE BYPASSED                                  │
└─────────────────────────────────────────────────────────┘
```

## How It Works

### Example: Firing a Weapon

**❌ WRONG (Trusting PooScript):**
```python
# PooScript
if has_power and reactor_online:
    fire_weapon()  # ❌ Can be hacked!
```

**✅ CORRECT (Kernel Enforcement):**
```python
# PooScript (untrusted)
fire_weapon()  # Just call it - kernel will validate

# Python Kernel (trusted)
def _fire_weapon(attacker, defender, weapon):
    # KERNEL CHECK 1: Weapons system functional?
    if not weapons_system.is_online():
        return Error("Weapons have no power!")

    # KERNEL CHECK 2: Weapon charged?
    if not weapon.is_ready():
        return Error("Weapon not ready!")

    # KERNEL CHECK 3: Enough reactor power?
    if total_power > available_power:
        return Error("Insufficient power - reactor damaged!")

    # All checks passed - fire!
    return Success()
```

## Kernel Enforcement Points

### 1. **Reactor Power System** (`core/ship.py`)

```python
def get_available_power(self) -> int:
    """
    KERNEL: Calculates available power from reactor health.
    - 100% health = 100% power
    - 50% health = 50% power
    - 0% health = 0% power

    PooScripts CANNOT override this!
    """
    base_power = self.reactor_power

    if SystemType.REACTOR in self.systems:
        reactor_health = self.systems[SystemType.REACTOR].room.health
        base_power = int(base_power * reactor_health)

    return base_power
```

### 2. **System Functionality Checks** (`core/ship.py`)

```python
def is_functional(self) -> bool:
    """
    KERNEL: Checks if a system can operate.

    Checks:
    - System health > 20%
    - Not breached
    - Has power allocated
    - Ship has enough total power from reactor

    Used by: weapons, engines, shields, all systems!
    """
    if self.health <= 0.2:
        return False
    if self.breached:
        return False
    if self.power_allocated <= 0:
        return False

    # CRITICAL: Check total power budget!
    total_power = sum(r.power_allocated for r in ship.rooms.values())
    available = ship.get_available_power()

    if total_power > available:
        # Power budget exceeded - this system fails!
        return False

    return True
```

### 3. **Weapon Firing** (`core/combat.py`)

```python
def _fire_weapon(attacker, defender, weapon):
    """
    KERNEL: Enforces all weapon firing requirements.

    PooScripts call this but CANNOT bypass checks!
    """
    # CHECK 1: Weapons system must be functional
    if not weapons_system.is_online():
        if total_power > available_power:
            return Error("Insufficient power - reactor damaged!")
        return Error("Weapons system offline!")

    # CHECK 2: Weapon must be charged
    if not weapon.is_ready():
        return Error("Weapon not ready!")

    # CHECK 3: In range
    if distance > weapon.range:
        return Error("Out of range!")

    # CHECK 4: Missiles available
    if weapon.requires_missiles and missiles <= 0:
        return Error("No missiles!")

    # All checks passed!
    return Fire()
```

## Why This Matters

### Prevents Cheating
- **Players can't hack PooScripts** to bypass power requirements
- **Enemy AI is equally constrained** - they follow same rules
- **Game is fair** - everyone plays by kernel's rules

### OS-Level Realism
- **Reactor damage has real consequences** - systems fail when power drops
- **Can't just allocate power manually** - kernel enforces budget
- **Systems dependent on reactor** - destroy reactor → systems fail

### Scriptable But Secure
- **PooScripts can automate** - write AI, automation, etc.
- **PooScripts can't cheat** - kernel validates everything
- **Same for everyone** - player, allies, enemies

## Test Results

```bash
$ python3 test_reactor_enforcement.py

Test 1: Healthy reactor (100% health)
  Available power: 8/8
  Weapons functional: True
  Fire weapon: ✅ SUCCESS

Test 2: Damaged reactor (30% health)
  Available power: 2/8
  Weapons functional: False
  Fire weapon: ❌ ERROR - Insufficient power!

Test 3: Destroyed reactor (0% health)
  Available power: 0/8
  Weapons functional: False
  Fire weapon: ❌ ERROR - Insufficient power!
```

**Conclusion:** Python kernel successfully enforces reactor power requirements. PooScripts CANNOT bypass these checks!

## For Developers

When adding new systems:

1. **Add kernel validation** - don't trust PooScripts
2. **Return error messages** - tell user WHY it failed
3. **Check `is_functional()`** - respects power budget
4. **Test with damaged reactor** - ensure it fails correctly

The kernel is the source of truth. PooScripts are user-space programs that can be hacked.

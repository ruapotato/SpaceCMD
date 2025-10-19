# Combat & Crew System Improvements

## Summary

Major improvements to make combat more strategic and crew bonuses more meaningful!

---

## 1. Clear Crew Bonuses for ALL Systems

Every system now has a **clear purpose** when crew is assigned:

### ✅ ALREADY WORKING:
- **SHIELDS**: Crew → Faster shield recharge (10% per skill level)
- **WEAPONS**: Crew → Faster weapon charge (10% per skill level)
- **ENGINES**: Crew → Faster ship speed (10% per skill level)

### 🆕 NEW BONUSES:
- **REACTOR**: Crew → **+1 power per crew member** (huge!)
  - Put 3 crew in reactor = +3 total power available
  - Shows up dynamically in top bar
  - `/proc/ship/power` shows "Reactor Bonus: +X"

- **MEDBAY**: Crew → Faster healing (effectiveness affects heal rate)
- **OXYGEN**: Crew → Better O2 distribution (effectiveness affects O2 regen)
- **HELM**: Crew → Better evasion (effectiveness affects dodge chance)

**Formula**: Without crew = 25% effectiveness (automation). With crew = 100% + (skill × 10%)

---

## 2. Strategic Combat System

### Old System (BROKEN):
- Shields absorb → Hull takes damage → System takes **3%** damage
- Systems were nearly impossible to disable
- Only way to win was destroy hull
- No strategy

### New System (STRATEGIC):

#### Targeting a System:
1. Shields absorb (if any)
2. **System takes FULL damage** (each point = 5% health lost)
3. Minor hull damage (10%)
4. If system destroyed, only 20% spillover to hull

#### Not Targeting (Hull Shot):
1. Shields absorb (if any)
2. Hull takes FULL damage
3. No system damage

### Why This is Better:
- **Disable enemies without killing them**
  - Target weapons → Can't shoot you anymore
  - Target engines → Can't escape
  - Target shields → Break their defenses
  - Target power → Reduce their power

- **Hull is now tougher** (increased enemy hull to 20)
- **Systems are the weak points** (20 damage destroys a system)
- **Real tactical decisions**: "Do I kill them or disable them?"

---

## 3. Redesigned Enemy Ships

### Old Gnat:
- 5 hull (too weak)
- Random messy layout
- Unclear what to target

### New Gnat (STRATEGIC):
```
Hull: 20 (tankier)
Shields: 1 (weak)
Crew: 1 robot running PooScript AI

CLEAR STRATEGIC LAYOUT:
┌─────────┬─────────┐
│ Weapons │ Shields │  ← Row 1
├─────────┼─────────┤
│ Engines │  Power  │  ← Row 2
└─────────┴─────────┘

TARGETS:
✓ Weapons  - Disable their offense
✓ Engines  - Prevent escape/chase
✓ Power    - Reduce power availability
✓ Shields  - Break defenses
```

**ONE robot** manages all systems via hostile PooScript AI

---

## 4. GUI Improvements

### Fixed:
- **Location display** now works! (was showing "unknown")
  - Shows: "1000u from center"
  - Updates in real-time

### Status Bar Updates:
- **Power** now shows reactor bonus from crew
- **Hull/Shields/Power** update dynamically (0.5s polling)

---

## 5. PooScript Integration

### Enemy AI runs REAL PooScript:
- Each enemy has ShipOS instance
- Runs `/root/ai.poo` hostile script
- AI can read `/proc/ship/*` to see status
- AI can write `/dev/ship/*` to control ship
- **Future**: Hack enemy scripts to disable them!

### New VFS Files:
- `/proc/ship/power` - Shows reactor bonus from crew
- `/dev/ship/course` - Set navigation course
- `/proc/ship/pois` - Nearby points of interest
- `/proc/ship/location` - Current galaxy position

---

## Testing

```bash
# Test in terminal mode
python3 play.py --ship kestrel --no-gui

# Try strategic combat:
fight              # Trigger test combat
target weapons     # Target their weapons
fire 0             # Fire weapon

# See crew bonuses:
cat /proc/ship/power
# Shows: "Reactor Bonus: +1 (crew in reactor)"

# Test movement:
cat /proc/ship/sensors
echo "500" > /dev/ship/course  # Navigate to position 500
```

---

## What Players Will Notice

1. **Crew matters MORE**:
   - Moving crew to reactor gives +1 power each
   - Moving crew to engines makes ship faster
   - Clear visual feedback in status bar

2. **Combat is STRATEGIC**:
   - Can disable enemy weapons (no more shooting!)
   - Can disable enemy engines (can't escape!)
   - Don't have to destroy hull to win

3. **Enemy ships make sense**:
   - Clear 4-system layout
   - Easy to understand what to target
   - Hull is tanky, systems are vulnerable

4. **Everything is hackable** (via PooScript):
   - Enemies run real scripts
   - Future: hack their AI
   - Future: steal their scripts

---

## Technical Details

### Combat Damage Formula:
```python
if targeting_system:
    system_damage = damage * 0.05  # Each point = 5% health
    hull_damage = damage * 0.1     # Minor hull damage
    if system.health <= 0:
        hull_damage += damage * 0.2  # 20% spillover
else:
    hull_damage = damage  # Full hull damage
```

### Crew Effectiveness Formula:
```python
if no_crew:
    effectiveness = health × power_ratio × 0.25  # 25% automation
else:
    crew_bonus = max_skill × 0.1  # 10% per skill level
    effectiveness = health × power_ratio × (1.0 + crew_bonus)
```

### Reactor Bonus:
```python
base_power = ship.reactor_power
bonus = len(reactor_room.crew)  # +1 per crew
total_power = base_power + bonus
```

---

## Files Modified

1. `core/ship.py` - Added `get_available_power()`, documented crew bonuses
2. `core/combat.py` - Rewrote damage system for strategic targeting
3. `core/enemy_ships.py` - Redesigned gnat with 4-system layout
4. `core/ship_os.py` - Updated `/proc/ship/power` to show reactor bonus
5. `core/gui/topbar.py` - Fixed location display parsing

---

**Result**: Combat is now strategic, crew bonuses are clear, and enemies are hackable computers running PooScript! 🚀

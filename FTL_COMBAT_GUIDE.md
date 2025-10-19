# FTL-Style Combat Guide

## ✅ What's Been Fixed

### 1. **Tactical Display Shows Enemy Ship**
- Enemy ship appears on the right side when in combat
- Both ships displayed side-by-side (FTL-style!)
- Stats no longer covered up - proper spacing
- Real-time updates from combat state

### 2. **Weapon Targeting System**
- **Click enemy rooms** to target them
- Selected target room **glows yellow** with pulsing effect
- Target info displayed in weapon panel
- All rooms are clickable for targeting

### 3. **Weapon Fire Controls**
- **Weapon buttons** at bottom left of tactical display
- Shows weapon name and charge status
- Green buttons = READY to fire
- Gray buttons = Charging (shows time remaining)
- Click button to fire at selected target

### 4. **Combat Log**
- Bottom right shows all combat events
- Weapon fires, damage dealt, hits, etc.
- Auto-scrolls with new events
- Integrated with combat system

### 5. **Layout Fixed**
- Smaller room size (60px instead of 80px)
- Player ship on left, enemy on right
- Stats displayed above each ship
- No overlap issues

## How to Play (FTL-Style!)

### Starting Combat
1. Launch the game: `python3 play.py`
2. Tutorial enemy spawns after 5 seconds
3. OR run `/tmp/hostile.poo` in terminal

### Combat Controls

#### **Target Enemy Systems:**
1. Click on any enemy room (weapons, shields, engines, etc.)
2. Room will glow yellow when selected
3. Target shown in weapon panel

#### **Fire Weapons:**
1. Wait for weapon to charge (green = READY)
2. Click the weapon button
3. Watch the projectile animation!
4. See damage in combat log

#### **Combat Tips:**
- **Target weapons** to disable their offense
- **Target shields** to reduce their defense
- **Target engines** to prevent escape
- Multiple hits on same room = extra damage

## Visual Indicators

### Ship Colors
- **Player Ship**: Green glow and accent
- **Enemy Ship**: Red glow and accent

### Room Highlights
- **Yellow glow**: Currently targeted room
- **Green**: System operational
- **Orange**: System damaged
- **Red**: System critical

### Weapon Status
- **Green button**: Ready to fire
- **Gray button**: Charging (shows countdown)
- **Pulsing border**: Weapon ready

## Combat Flow

```
1. Enemy Appears
   ↓
2. Click Enemy Room to Target
   ↓
3. Wait for Weapon to Charge
   ↓
4. Click Weapon Button to Fire
   ↓
5. Watch Projectile Hit!
   ↓
6. Screen Flashes Red if You're Hit
   ↓
7. Repeat Until Victory!
```

## Features

✅ **Dual ship display** (player left, enemy right)
✅ **Clickable targeting** (click enemy rooms)
✅ **Weapon controls** (click to fire when ready)
✅ **Real-time charge status** (countdown timers)
✅ **Projectile animations** (laser beams!)
✅ **Combat log** (all events tracked)
✅ **Screen flash on damage** (red flash!)
✅ **Hull/shield bars** (for both ships)
✅ **System health indicators** (per room)

## Technical Details

### Files Modified:
- `core/gui/tactical_widget.py` - FTL-style combat UI
- `core/gui/desktop.py` - Combat state integration
- `play.py` - World manager wiring

### New Methods:
- `TacticalWidget.update_from_combat()` - Syncs with combat
- `TacticalWidget._fire_weapon()` - Fires weapons
- `TacticalWidget._render_command_log()` - Weapon controls UI

### Integration:
- Tactical widget connected to WorldManager
- Combat log auto-updates from CombatState
- Weapon targeting updates combat target
- Real-time stat updates

## Try It Out!

```bash
python3 play.py

# Wait 5 seconds for tutorial enemy
# OR open terminal and run:
/tmp/hostile.poo

# Then in tactical display:
# 1. Click enemy room to target
# 2. Click weapon when green
# 3. Watch combat unfold!
```

## What You'll See

1. **Enemy ship appears** on right side
2. **Weapon panel** shows "Basic Laser - READY"
3. **Target panel** shows "Target: None (click enemy room)"
4. **Click enemy "Weapon Pod"** - it glows yellow
5. **Click weapon button** - projectile fires!
6. **Combat log** shows: "⚡ Fired Basic Laser!"
7. **Enemy health** drops
8. **Screen flashes red** when enemy fires back
9. **Victory** when enemy hull reaches 0!

Enjoy FTL-style combat! 🚀💥

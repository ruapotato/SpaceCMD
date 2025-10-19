# SpaceCMD Updates

## Recent Changes

### Bug Fixes
1. **Fixed weapon firing TypeError** - `is_functional` was being called as a function instead of accessed as a property
2. **Fixed crew assignment** - Now properly handles crew names with spaces (e.g., "Lieutenant Hayes")
3. **Fixed galaxy map rendering** - Corrected dictionary iteration to use `.values()` instead of keys
4. **Fixed starting weapon not ready** - Player's Burst Laser II now starts fully charged (1.0) and ready to fire immediately

### New Features

#### 1. Galaxy Map V2 - Complete Redesign
**Purpose**: Clear progression through 8 sectors with strategic choices

**Features**:
- FTL-style vertical sector layout
- Visual node types with icons:
  - ⚔️ HOSTILE - Combat encounters
  - 💀 ELITE - Harder enemies, better rewards
  - 🛒 STORE - Buy upgrades
  - ❓ UNKNOWN - Random events
  - 📡 DISTRESS - Risky encounters
  - 🔧 REPAIR - Free repairs
  - 🌫️ NEBULA - Shields disabled
  - ☄️ ASTEROID - Evasion penalty
- Click any yellow-highlighted node to jump
- Info panel shows current location and available jumps
- Automatic camera scrolling to follow progression

**Usage**:
- Press `Ctrl+M` or click "Galaxy Map" in APPS menu
- Click yellow nodes to jump
- Each jump costs 1 fuel

#### 2. Synthesized Sound Effects
**All sounds procedurally generated - no audio files needed!**

**Sound Library** (13 unique sounds):
- **Weapon Sounds**: laser_fire, missile_fire, beam_fire
- **Impact Sounds**: shield_hit, hull_hit, explosion
- **Alert Sounds**: system_damage, alarm
- **UI Sounds**: click, select, error
- **Ambient**: engine_hum

**Integration**:
- Automatically plays during combat
- UI clicks when interacting
- Weapon fire sounds
- Shield/hull impact sounds
- Explosions when ships destroyed
- System damage alerts

#### 3. Improved Crew Management
**Features**:
- Click crew members to select them (yellow glow)
- Click any room to move selected crew there
- Works via GUI or command line: `crew assign <name> <room>`
- Real-time sync between GUI and game state
- Autonomous AI bots auto-repair, fight fires, and heal

**Fixes**:
- Crew names with spaces now work correctly
- Added `/dev/ship/crew_assign` device file
- Updated crew command with `assign` subcommand

### Combat Balance Improvements
- Reduced enemy damage (Gnat: 5→2 damage)
- Reduced system fragility (15%→3% of hull damage)
- Systems work until <20% health (was 0%)
- Faster auto-repair: 20%/sec base, 60%/sec with crew AI
- Lower fire chance: 20%→5%
- Lower breach chance: 10%→2%

### How to Play

**Controls**:
- `Ctrl+T` - New terminal
- `Ctrl+D` - Tactical display
- `Ctrl+M` - Galaxy map
- `ESC` - Exit

**Combat**:
1. Open tactical display (`Ctrl+D`)
2. Click enemy rooms to target systems
3. Click weapon buttons to fire
4. Crew automatically repairs damage

**Navigation**:
1. Open galaxy map (`Ctrl+M`)
2. Click yellow nodes to jump
3. Progress through 8 sectors
4. Each sector gets harder but has better rewards

**Crew Management**:
- Click crew member → Click destination room
- Or use command: `crew assign Lieutenant Hayes Weapons`
- Bots automatically handle repairs and fires

### File Structure
```
core/
  audio/
    sound_fx.py          # Procedural sound generator
  gui/
    map_widget_v2.py     # New FTL-style map
    tactical_widget.py   # Updated with sounds and better sync
  combat.py              # Integrated sound effects
  ship.py                # Autonomous crew AI
  ship_os.py             # Crew assignment device file
scripts/
  bin/
    crew                 # Updated crew command
    fire                 # Fixed weapon firing
```

## Testing
```bash
# Test sounds
python3 test_sounds.py

# Test crew assignment
python3 test_crew_assign.py

# Test combat balance
python3 test_balance.py

# Play the game
python3 play.py
```

## Known Issues
None! All major bugs fixed.

## Future Enhancements
- More enemy ship types
- Store/trading system implementation
- More event types
- Save/load system
- Additional weapons
- More ship classes

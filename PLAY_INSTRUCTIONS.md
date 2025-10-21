# How to Play SpaceCMD

## Quick Start

### 1. Open in Godot Editor
```bash
cd ~/SpaceCMD
./Godot_v4.4.1-stable_linux.x86_64 --editor .
```

### 2. Press F5 to Run
The game will:
- Generate a procedural ship layout
- Create 3D rooms (Helm, Reactor, Engine, Weapons, Repair Bay)
- Place consoles in each room
- Spawn you in the Helm room

### 3. Controls

#### 3D Movement Mode
- **W/A/S/D** - Move forward/left/backward/right
- **Mouse** - Look around (mouse is captured)
- **E** - Interact with console (when looking at one)

#### Terminal Mode (after pressing E on console)
- **Type commands** - Execute ship OS commands
- **Up/Down arrows** - Navigate command history
- **Escape** - Exit terminal, return to 3D view

### 4. Try These Commands

When you press E on any console, try:

```bash
# View ship filesystem
ls /
ls /dev/ship
ls /proc/ship

# Check ship status
cat /proc/ship/status
cat /proc/ship/position
cat /proc/ship/sensors

# View weapons
cat /proc/ship/weapons

# View power allocation
cat /proc/ship/power

# Get help
help
```

## Game Architecture

### Dual-Mode Design
- **3D Mode**: Walk around ship interior (FTL-style)
- **Terminal Mode**: Fullscreen command interface
- **Both modes access the same ShipOS** - graphics are just a view layer

### Room Types
Your ship has different rooms, each with a specific console:

1. **Helm** (Bridge)
   - Navigation
   - Sensors
   - Targeting

2. **Reactor Core**
   - Power generation
   - Power distribution

3. **Engine Room**
   - Propulsion systems
   - FTL drive (future)

4. **Weapons Bay**
   - Weapon control
   - Firing systems

5. **Repair Bay**
   - Bot maintenance
   - System repairs

### Procedural Generation
- Each time you run, the ship layout is different
- Rooms are connected automatically
- Grid-based system ensures proper layout

## Current Features

### Working Now
✅ Walk around ship interior
✅ Interact with consoles
✅ Access ShipOS through terminals
✅ File system access (ls, cat)
✅ Command history
✅ Multiple room types
✅ Procedural ship generation

### Coming Soon
⏳ External 3D combat view
⏳ Physical weapons firing
⏳ Ship-to-ship combat
⏳ Boarding mechanics
⏳ Multiple ships

## Troubleshooting

### Can't Move
- Make sure you're not in terminal mode
- Press Escape if you are

### Can't Interact with Console
- Look directly at the console (aim with mouse)
- Get close enough (within 3 meters)
- Press E

### Terminal Won't Close
- Press Escape (not E)

### Mouse Not Captured
- Click on the game window
- Mouse should be captured automatically

## File Structure

```
SpaceCMD/
├── scenes/
│   └── procedural_ship.tscn  ← Main playable scene
├── player/
│   ├── player_bot.tscn       ← Your character
│   └── helm_console.tscn     ← Interactable consoles
├── ui/
│   └── terminal_ui.tscn      ← Terminal interface
└── core/
    ├── os/                   ← ShipOS implementation
    ├── ship/                 ← Ship systems & room generation
    └── combat/               ← Combat systems
```

## Development Notes

### Adding New Room Types
Edit `core/ship/room_system.gd`:
1. Add new RoomType enum value
2. Add room data to ROOM_DATA constant
3. Room will automatically generate!

### Modifying Ship Layout
Edit `core/ship/ship_generator.gd`:
- `generate_basic_ship()` - Predictable layout
- `generate_random_ship()` - Random layout

### Headless Mode
All core functionality works without graphics:
```bash
# Run tests (headless)
./Godot_v4.4.1-stable_linux.x86_64 --headless --script tests/test_ai_movement.gd
```

Note: Some tests may time out due to scene loading in current build.

## Next Steps

Want to contribute? Check out:
- `README.md` - Full project overview
- `PHASE_6_SUMMARY.md` - Latest implementation details
- `ARCHITECTURE.md` - System design

---

**Have fun hacking your ship!** 🚀🤖

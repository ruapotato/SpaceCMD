# SpaceCMD - FTL-Inspired Terminal Spaceship Game

**Command your spaceship through a custom terminal interface. Manage crew, allocate power, and survive tactical combat - all from the command line.**

Inspired by FTL: Faster Than Light, SpaceCMD brings roguelike spaceship combat to your terminal with beautiful ASCII graphics and a custom command-line interface.

```
╔══════════════════════════════════════════════════════════╗
║                  KESTREL - HUMAN CRUISER                 ║
╚══════════════════════════════════════════════════════════╝

  HULL:    [████████████] 30/30
  SHIELDS: [████████████] 4/4
  POWER:   ⚡⚡⚡⚡⚡⚡⚡░ 7/8
  FUEL:    20

  SHIP LAYOUT:

  Helm         🎯 [████████] ░░ 👤
  Shields      🛡️ [████████] ⚡⚡░
  Oxygen       💨 [████████] ⚡
  Weapons      🔴 [████████] ⚡⚡░░ 👤
  Engines      ⚙️ [████████] ⚡⚡░ 👤

Kestrel> power shields 4
Kestrel> fire 1
Kestrel> status
```

## 🎮 How to Play

### Roguelike Mode (Recommended for First Time)

Complete campaign with tutorial, combat, and story:

```bash
python3 game.py
```

Navigate sectors, fight pirates, upgrade your ship, reach Federation HQ!

### Quick Play Mode

Jump straight into ship management:

```bash
python3 play.py --ship kestrel
```

Choose from multiple ship classes and start commanding!

### Advanced Mode (Experimental)

Ship OS mode with filesystem interface (work in progress):

```bash
python3 shipos.py --ship kestrel
```

**Note:** ShipOS mode is experimental and uses a custom command-line interface, not a full Unix emulation.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/ruapotato/SpaceCMD.git
cd SpaceCMD

# Play the roguelike campaign
python3 game.py

# Or quick play mode
python3 play.py --ship kestrel

# Skip intro sequences
python3 play.py --ship kestrel --no-intro
```

**Requirements:** Python 3.7+ (no external dependencies!)

## 🎯 Core Gameplay

### Ship Systems

Your ship has critical systems that need power and crew:

- **🛡️ Shields** - Absorb incoming damage before hull takes hits
- **🔴 Weapons** - Lasers, missiles, ion cannons to destroy enemies
- **⚙️ Engines** - Evasion chance and FTL jump capability
- **💨 Oxygen** - Keep your crew alive (critical!)
- **💉 Medbay** - Heal injured crew members
- **⚡ Reactor** - Limited power - allocate wisely!
- **🎯 Helm** - Navigation and piloting
- **📡 Sensors** - Scan enemy ships
- **🚪 Doors** - Contain fires and breaches

### Resources You Manage

- **Power** - Limited reactor output; choose what systems get power
- **Hull** - Your ship's health; 0 = game over
- **Fuel** - Required for FTL jumps between sectors
- **Scrap** - Currency for upgrades and repairs
- **Missiles** - Limited ammo for missile weapons

### Your Crew

Each crew member is an individual:

- **Skills** - Weapons, piloting, engines, shields, repair, combat
- **Health** - Can be injured in combat or by hazards
- **Position** - Assign crew to rooms for system bonuses
- **Experience** - Crew improve as they work

## 🕹️ Commands

### Basic Commands

```
status          - Show complete ship status
systems         - List all ship systems and power levels
crew            - Show crew roster and positions
help            - Show available commands
exit            - Quit game
```

### Ship Management

```
power <system> <amount>     - Allocate power
  Example: power shields 3

assign <crew> <room>        - Move crew to a room
  Example: assign hayes weapons

repair <system>             - Order crew to repair damaged system
  Example: repair weapons

wait [seconds]              - Advance time
  Example: wait 5
```

### Combat Commands

```
target <system>     - Target enemy weapons/shields/engines
fire <weapon>       - Fire a weapon (1, 2, 3, etc.)
shield <level>      - Raise/lower shields
```

## 🎨 Ship Classes

### Kestrel (Balanced - Recommended for Beginners)
- Balanced stats
- Good shields (4 layers)
- 3 crew members
- Multiple weapon slots
- Great all-around ship

### Stealth Ship (Hard Mode)
- **NO SHIELDS** - relies on cloaking and evasion
- 2 crew members
- Fast engines
- High risk, high reward

### Mantis Cruiser (Boarding Specialist)
- Has teleporter for crew boarding
- 4 Mantis crew (strong fighters)
- Designed for boarding enemy ships
- Unique playstyle

More ships to unlock as you play!

## ⚔️ Combat

Tactical real-time combat with pause:

1. **Target** enemy systems (weapons, shields, engines)
2. **Charge** your weapons take time to power up
3. **Fire** when ready - timing is crucial
4. **Shields** absorb hits before hull damage
5. **Crew** position them for bonuses and repairs
6. **Power** manage reactor allocation on the fly

Enemy ships fight back! Manage damage, fires, breaches, and oxygen while returning fire.

## 🌌 Exploration

- Navigate through **procedurally generated sectors**
- Each sector has multiple **beacons** to jump to
- Random encounters at each location:
  - ⚔️ **Pirates** - Fight or flee
  - 📡 **Distress signals** - Help or trap?
  - 💰 **Merchants** - Buy fuel, weapons, crew
  - ⭐ **Anomalies** - Strange events
  - 🚢 **Abandoned ships** - Scavenge supplies
  - ☄️ **Asteroid fields** - Navigate hazards

## 🎲 Roguelike Elements

- **Permadeath** - One ship, one life
- **Procedural generation** - Every run is different
- **Risk vs. Reward** - Push deeper or play it safe?
- **Unlockables** - New ships and achievements
- **Replayability** - Multiple paths to victory

## 📊 Example Session

```bash
$ python3 play.py --ship kestrel

Kestrel> status
=== KESTREL (HUMAN CRUISER) ===
Hull: 30/30 | Shields: 4/4
Power: 7/8 | Fuel: 20

Kestrel> systems
=== SHIP SYSTEMS ===
Helm         [ONLINE ] HP:100% PWR:0/2
Shields      [ONLINE ] HP:100% PWR:2/3
Weapons      [ONLINE ] HP:100% PWR:2/4
Engines      [ONLINE ] HP:100% PWR:2/3
Oxygen       [ONLINE ] HP:100% PWR:1/1

Kestrel> crew
=== CREW ROSTER ===
Lieutenant Hayes     HP:100/100 @ Helm
Chief O'Brien        HP:100/100 @ Engines
Sergeant Vega        HP:100/100 @ Weapons

Kestrel> power shields 4
Allocated 4 power to Shields (+2)

Kestrel> assign hayes weapons
Hayes assigned to Weapons room

Kestrel> wait 10
Waiting 10 seconds...

Kestrel> exit
Safe travels, Captain!
```

## 🎨 Visual Design

Beautiful ASCII/Unicode ship layouts:

```
           ╔════════════════════════════╗
           ║      KESTREL CRUISER       ║
         ╔═╩════════════════════════════╩═╗
         ║   ┌──────────┬──────────┐     ║
         ║   │  HELM    │ SHIELDS  │     ║
         ║   │   🎯     │   🛡️     │     ║
         ║   │   👤     │   ⚡⚡   │     ║
    ═══  ║   │  [PILOT] │ [SHIELD] │     ║  ═══
         ║   └──────────┴──────────┘     ║
         ╚═╦════════════════════════════╦═╝
           ║       👤 CORRIDOR          ║
         ╔═╩════════════════════════════╩═╗
         ║   ┌──────────┬──────────┐     ║
         ║   │ WEAPONS  │  OXYGEN  │     ║
    🔴━━ ║   │  🔴🔴   │   💨     │     ║ ━━🔴
         ║   │  [WEAPON]│   [O2]   │     ║
         ║   └──────────┴──────────┘     ║
         ╚═╦════════════════════════════╦═╝
         ╔═╩════════════════════════════╩═╗
         ║   ┌──────────┬──────────┐     ║
         ║   │ REACTOR  │ ENGINES  │     ║
         ║   │   ⚡⚡   │   ⚙️⚙️   │     ║
         ║   └──────────┴──────────┘     ║
         ╚═══════════════════════════════╝
```

See `SHIP_DESIGNS.md` for all ship classes!

## 🧪 Testing

Run the automated test suite:

```bash
python3 test_main_programs.py
```

Tests verify:
- ✅ No crashes
- ✅ Clean startup and shutdown
- ✅ All three game modes work
- ✅ Command-line argument handling

## 🛠️ Project Structure

```
SpaceCMD/
├── game.py                 # Roguelike campaign mode
├── play.py                 # Quick play mode
├── shipos.py              # Ship OS mode (experimental)
├── core/
│   ├── ship.py            # Ship state and systems
│   ├── crew.py            # Crew management
│   ├── combat.py          # Combat engine
│   ├── render.py          # ASCII rendering
│   ├── game.py            # Game loop
│   └── ...                # Other modules
├── test_main_programs.py  # Automated tests
└── docs/
    ├── QUICKSTART.md
    ├── SHIP_DESIGNS.md
    └── ...
```

## 🎯 Current Status

### ✅ Working Features
- Three different play modes
- Multiple ship classes (Kestrel, Stealth, Mantis)
- Crew management and assignment
- Power allocation system
- Beautiful ASCII ship rendering
- Turn-based combat prototype
- Ship status displays
- Command-line interface

### 🚧 In Development
- Full combat system with enemy AI
- More weapon types
- Hull breaches and fire mechanics
- Oxygen depletion system
- Enemy ship variety

### 📋 Planned
- Complete sector navigation
- More random events
- Merchant shops
- Ship upgrade system
- Save/load functionality
- More ship classes
- Achievement system

## 🗺️ Roadmap

**Phase 1: Core Gameplay** (Current)
- ✅ Ship systems and management
- ✅ Crew assignment
- ✅ Basic combat
- ✅ ASCII rendering
- 🚧 Enemy AI

**Phase 2: Combat & Events**
- Weapon variety (lasers, missiles, beams, ions)
- Environmental hazards (fire, breaches, oxygen)
- Random encounter system
- Enemy ship types

**Phase 3: Progression**
- Sector navigation
- Shops and trading
- Ship upgrades
- Save/load system

**Phase 4: Polish**
- More ships to unlock
- Achievements
- Sound effects (terminal beeps!)
- Tutorial improvements

## 🤝 Contributing

Contributions welcome! SpaceCMD is open source under GPL-3.0.

Ways to contribute:
- Add new ship designs
- Create new events
- Design weapons
- Improve AI
- Write documentation
- Report bugs

## 📚 Documentation

- **QUICKSTART.md** - Get started in 5 minutes
- **SHIP_DESIGNS.md** - All ship classes and stats
- **PLAY_MODES.md** - Different ways to play
- **SHIPOS_GUIDE.md** - Ship OS mode guide (experimental)
- **TESTING_README.md** - Testing and development

## 📜 License

**GPL-3.0 License**

Copyright (C) 2025 David Hamner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

## 🙏 Credits

**Author:** David Hamner

**Inspired by:**
- FTL: Faster Than Light by Subset Games
- Classic roguelikes (Rogue, NetHack, DCSS)
- Terminal-based games and ASCII art tradition

**Built for:**
- Roguelike fans
- FTL players
- Terminal enthusiasts
- Space sim lovers
- Anyone who wants to command a spaceship from the CLI

## 🔗 Links

- **Repository:** https://github.com/ruapotato/SpaceCMD
- **Issues:** https://github.com/ruapotato/SpaceCMD/issues
- **Discussions:** https://github.com/ruapotato/SpaceCMD/discussions

## 🎮 Tips for New Players

1. **Start with the tutorial** - `python3 game.py` includes a tutorial
2. **Manage power carefully** - You never have enough!
3. **Watch your oxygen** - Keep O2 powered or crew suffocates
4. **Position crew wisely** - They provide bonuses to systems
5. **Target tactically** - Hit enemy weapons to stop their attacks
6. **Don't neglect engines** - Evasion saves hull integrity
7. **Pause is your friend** - Take time to think in combat

---

**Ready to command your ship? Launch now!**

```bash
python3 game.py
```

⭐ Star the repo if you enjoy the game!

Built with ❤️ for the terminal.

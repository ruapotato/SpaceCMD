# spacecmd Conversion Roadmap

This document outlines the conversion from the Unix hacking game to spacecmd - a FTL-like spaceship command simulator.

## Phase 1: Core Architecture Redesign

### 1.1 Ship Structure System (Replaces VFS)
**Current**: Virtual filesystem with inodes, directories, files
**New**: Ship rooms and compartments system

- [ ] Create `core/ship.py` - Ship class with rooms and layout
- [ ] Design room types: Helm, Weapons, Shields, Engines, O2, Medbay, Reactor, Sensors, Doors
- [ ] Room properties: size, coordinates, connections, system installed
- [ ] Hull integrity system (replaces filesystem permissions)
- [ ] Room damage/breach mechanics
- [ ] Airlock and door system

### 1.2 Crew System (Replaces Process Management)
**Current**: Process management with PIDs, signals, process trees
**New**: Crew members with skills and assignments

- [ ] Create `core/crew.py` - Crew member class
- [ ] Crew attributes: name, race, health, skills, experience
- [ ] Skills: Weapons, Piloting, Engines, Shields, Repair, Combat
- [ ] Crew positioning and movement between rooms
- [ ] Skill bonuses when stationed at systems
- [ ] Crew combat system (boarding/defending)
- [ ] Crew experience and leveling
- [ ] Crew injury and death mechanics

### 1.3 Ship Systems (Replaces Commands)
**Current**: Unix commands (ls, cat, grep, etc.)
**New**: Ship system management commands

- [ ] Create `core/systems.py` - System base class
- [ ] System properties: power requirement, health, upgrade level
- [ ] Weapons system (lasers, missiles, beams, ions)
- [ ] Shield system (bubble shields, layer mechanics)
- [ ] Engine system (evasion, FTL charge)
- [ ] Oxygen system (life support, oxygen levels per room)
- [ ] Reactor system (power generation and distribution)
- [ ] Sensors system (enemy ship detection)
- [ ] Helm system (navigation and piloting)
- [ ] Medbay system (crew healing)
- [ ] Door system (airlock control, fire containment)

### 1.4 Resource Management
**Current**: Filesystem storage
**New**: Ship resources

- [ ] Create `core/resources.py` - Resource management
- [ ] Power system (reactor output, system allocation)
- [ ] Hull integrity (ship health)
- [ ] Fuel (FTL jumps)
- [ ] Scrap (currency)
- [ ] Missiles (weapon ammunition)
- [ ] Drone parts
- [ ] Oxygen levels per room

## Phase 2: Combat System

### 2.1 Combat Engine
**Current**: Network packet-based "hacking"
**New**: Tactical ship-to-ship combat

- [ ] Create `core/combat.py` - Combat state machine
- [ ] Turn/tick system (real-time with pause)
- [ ] Weapon charging and cooldown
- [ ] Weapon targeting (specific enemy systems)
- [ ] Shield penetration mechanics
- [ ] Damage calculation and application
- [ ] Fire mechanics (spread, damage, oxygen consumption)
- [ ] Breach mechanics (hull damage, vacuum)
- [ ] Evasion calculation
- [ ] Enemy AI behavior

### 2.2 Weapon Types
- [ ] Laser weapons (fast, low damage, shield depletion)
- [ ] Missile weapons (bypass shields, limited ammo)
- [ ] Ion weapons (system disabling, shield disruption)
- [ ] Beam weapons (pierce shields after depletion)
- [ ] Bomb weapons (teleport through shields)
- [ ] Weapon upgrade system

### 2.3 Enemy Ships
**Current**: Network nodes with services
**New**: Enemy vessels with their own systems

- [ ] Enemy ship templates (Pirate Scout, Mantis Fighter, etc.)
- [ ] Enemy AI targeting logic
- [ ] Enemy crew and boarding parties
- [ ] Enemy surrender mechanics
- [ ] Ship capture/destruction rewards

## Phase 3: Game Flow & Events

### 3.1 Sector Navigation
**Current**: Network topology
**New**: Star map with beacons

- [ ] Create `core/sector.py` - Sector generation
- [ ] Beacon types: Empty, Combat, Event, Store, Distress
- [ ] FTL jump system
- [ ] Rebel fleet advancement (time pressure)
- [ ] Sector progression (8 sectors to finale)
- [ ] Procedural sector generation

### 3.2 Event System
**Current**: Hacking scenarios
**New**: Space encounters

- [ ] Create `core/events.py` - Event handler
- [ ] Event scripting format (JSON + PooScript)
- [ ] Event types:
  - [ ] Combat encounters (pirates, rebels, etc.)
  - [ ] Distress signals (rescue, trap, derelict)
  - [ ] Merchants (buy/sell/trade)
  - [ ] Anomalies (nebula, asteroid field, pulsar)
  - [ ] Story events (quest chains)
  - [ ] Boarding events (send crew to enemy ship)
- [ ] Event choices and consequences
- [ ] Random event pool and weighting

### 3.3 Shop & Upgrade System
**Current**: None
**New**: Merchant beacons and upgrades

- [ ] Store interface
- [ ] Item categories: Weapons, Systems, Augments, Crew, Supplies
- [ ] Dynamic pricing based on sector
- [ ] Ship upgrade mechanics
- [ ] System upgrade levels (1-3 for most systems)
- [ ] Augmentation system (passive bonuses)

## Phase 4: Rendering & Interface

### 4.1 ASCII/Unicode Rendering
**Current**: Text output only
**New**: Beautiful terminal graphics

- [ ] Create `core/render.py` - Display rendering
- [ ] Ship layout renderer (rooms, systems, crew)
- [ ] Status bar (shields, hull, O2, power)
- [ ] Weapon charging indicators
- [ ] Combat view (your ship + enemy ship)
- [ ] System status displays
- [ ] Crew roster display
- [ ] Sector map display
- [ ] Event/dialog boxes
- [ ] Unicode box-drawing characters
- [ ] Color coding (curses/ANSI colors)
- [ ] Animation system (weapon fire, explosions)

### 4.2 Command Interface
**Current**: Unix shell parser
**New**: Spaceship command interface

- [ ] Update `core/shell.py` for space commands
- [ ] Command categories:
  - [ ] Status: `status`, `systems`, `crew`, `sensors`, `map`
  - [ ] Combat: `target`, `fire`, `shields`, `power`, `pause`
  - [ ] Crew: `assign`, `repair`, `board`, `retreat`
  - [ ] Navigation: `jump`, `ftl`, `engage`, `flee`
  - [ ] System: `upgrade`, `vent`, `doors`
  - [ ] Scripting: `script`, `macro`, `auto`
- [ ] Tab completion for commands
- [ ] Command history
- [ ] Help system

## Phase 5: PooScript Integration

### 5.1 Ship Automation API
**Current**: VirtualScript for filesystem access
**New**: PooScript for ship automation

- [ ] Update `core/pooscript.py` (rename from virtualscript)
- [ ] Ship object API:
  - [ ] `ship.systems` - Access all ship systems
  - [ ] `ship.crew` - Crew management
  - [ ] `ship.target(system)` - Weapon targeting
  - [ ] `ship.power(system, amount)` - Power allocation
  - [ ] `ship.fire(weapon)` - Fire weapons
  - [ ] `ship.vent(room)` - Airlock control
- [ ] Enemy object API:
  - [ ] `enemy.systems` - Enemy ship state
  - [ ] `enemy.crew` - Enemy crew positions
  - [ ] `enemy.shields` - Shield status
- [ ] Combat automation scripts
- [ ] Repair macros
- [ ] Power management profiles
- [ ] Crew assignment templates

### 5.2 Modding Support
- [ ] Event scripting in PooScript
- [ ] Custom ship definitions
- [ ] Custom weapon definitions
- [ ] AI behavior scripting
- [ ] Custom event chains

## Phase 6: Persistence & Progression

### 6.1 Save/Load System
**Current**: None
**New**: Full game state persistence

- [ ] JSON serialization of game state
- [ ] Save file format
- [ ] Auto-save on beacon jump
- [ ] Manual save/load commands
- [ ] Continue from last save

### 6.2 Progression System
- [ ] Ship unlocks (achievements to unlock new ships)
- [ ] Achievement tracking
- [ ] High score system
- [ ] Statistics tracking (games played, ships destroyed, etc.)
- [ ] Difficulty levels

## Phase 7: Content Creation

### 7.1 Ship Types
- [ ] Kestrel (balanced starter ship)
- [ ] Engi Cruiser (defense focused, drones)
- [ ] Stealth Cruiser (cloaking, weak shields)
- [ ] Mantis Cruiser (boarding focused)
- [ ] Rock Cruiser (strong hull, slow)
- [ ] Zoltan Cruiser (super shields)

### 7.2 Weapons Library
- [ ] 20+ unique weapons with different properties
- [ ] Weapon rarities and balance
- [ ] Weapon synergies

### 7.3 Events Library
- [ ] 50+ random events
- [ ] Sector-specific events
- [ ] Race-specific events
- [ ] Quest chains

### 7.4 Enemy Ships
- [ ] 30+ enemy ship variants
- [ ] Boss ship (Rebel Flagship)
- [ ] Scaling difficulty by sector

## Phase 8: Polish & Features

### 8.1 Sound & Effects
- [ ] Terminal beep sound effects
- [ ] ASCII explosions
- [ ] Weapon fire animations
- [ ] Screen shake effects (terminal redraw)

### 8.2 Tutorial
- [ ] Interactive tutorial mission
- [ ] Help tooltips
- [ ] Command reference

### 8.3 Quality of Life
- [ ] Auto-fire toggle
- [ ] Quick power presets
- [ ] Crew assignments presets
- [ ] Combat summary/log
- [ ] Pause during events

## Migration Strategy

### What to Keep
- ✅ Shell parser (adapt for new commands)
- ✅ PooScript engine (rename from VirtualScript, expand API)
- ✅ Command system architecture
- ✅ Pure Python philosophy (no dependencies)

### What to Transform
- 🔄 VFS → Ship rooms and layout system
- 🔄 Process system → Crew management
- 🔄 Network layer → Combat and enemy ships
- 🔄 Unix commands → Spaceship commands
- 🔄 File permissions → System power/health
- 🔄 Signals → Game events

### What to Remove
- ❌ Filesystem operations (ls, cat, grep, etc.)
- ❌ Network scanning (nmap, netstat)
- ❌ SSH simulation
- ❌ Unix user/group system
- ❌ Inode system
- ❌ Device files

## Implementation Order

1. **Week 1-2**: Core ship structure, rooms, and basic systems
2. **Week 3-4**: Crew system and assignment mechanics
3. **Week 5-6**: Power management and resource systems
4. **Week 7-8**: Basic rendering (ship display, status bars)
5. **Week 9-10**: Combat system foundation
6. **Week 11-12**: Weapons and shields
7. **Week 13-14**: Enemy ships and AI
8. **Week 15-16**: Events and navigation
9. **Week 17-18**: PooScript API and automation
10. **Week 19-20**: Save/load and progression
11. **Week 21-22**: Content (ships, weapons, events)
12. **Week 23-24**: Polish and testing

## Success Criteria

- [ ] Can play a complete run from sector 1 to final boss
- [ ] All core FTL systems implemented (weapons, shields, crew, etc.)
- [ ] Beautiful ASCII ship visualization
- [ ] Fully scriptable via PooScript
- [ ] Procedural replayability
- [ ] At least 3 unlockable ships
- [ ] 30+ events
- [ ] 20+ weapons
- [ ] Save/load functionality

## Questions to Resolve

- Real-time vs turn-based combat? (Suggest: Real-time with pause)
- How much RNG vs skill? (Suggest: FTL-like balance)
- Permadeath always or optional? (Suggest: Always, true roguelike)
- Terminal size requirements? (Suggest: 80x24 minimum, 120x40 recommended)
- Color requirement? (Suggest: Optional, works in monochrome)
- Mouse support? (Suggest: No, keyboard only for true CLI feel)

# spacecmd Ship Designs

Advanced ship layouts with organic shapes, distinct rooms, and clear visual segmentation.

## Design Philosophy

1. **No boring boxes** - Use Unicode to create interesting hull shapes
2. **Clear room boundaries** - Each room is visually distinct
3. **Functional layout** - Ship design reflects its role (combat, stealth, boarding, etc.)
4. **Visual storytelling** - You can "read" the ship's purpose from its layout
5. **Scalable detail** - Works at different terminal sizes

---

## THE KESTREL - Balanced Cruiser (Human Federation)

**Role**: All-rounder, good starting ship
**Layout**: Classic cruiser design with modular sections

```
                    ╔═══════════════════════════════════════════╗
                    ║  KESTREL-CLASS CRUISER                    ║
                    ║  Hull: 30  Crew: 3  Power: 8             ║
                    ╚═══════════════════════════════════════════╝

           ╔════════════════════════════╗
           ║         FRONT SECTION      ║
         ╔═╩════════════════════════════╩═╗
         ║   ┌──────────┬──────────┐     ║
         ║   │  HELM    │ SHIELDS  │     ║
         ║   │   🎯     │   🛡️     │     ║
         ║   │   👤     │   ⚡⚡   │     ║
    ═══  ║   │  [PILOT] │ [SHIELD] │     ║  ═══  Weapon Hardpoints
         ║   └──────────┴──────────┘     ║
         ╚═╦════════════════════════════╦═╝
           ║      CENTRAL CORRIDOR      ║
           ║  ─────────👤─────────────  ║
         ╔═╩════════════════════════════╩═╗
         ║   ┌──────────┬──────────┐     ║
         ║   │ WEAPONS  │  OXYGEN  │     ║
         ║   │  ⚡⚡⚡  │   💨     │     ║
    🔴━━ ║   │  🔴🔴   │   ⚡     │     ║ ━━🔴  Burst Lasers
         ║   │ [WEAPON] │   [O2]   │     ║
         ║   └──────────┴──────────┘     ║
         ╚═╦════════════════════════════╦═╝
           ║      REAR SECTION          ║
         ╔═╩════════════════════════════╩═╗
         ║   ┌──────────┬──────────┐     ║
         ║   │ REACTOR  │ ENGINES  │     ║
         ║   │   ⚡⚡   │   ⚙️⚙️   │     ║
         ║   │   ⚡⚡   │   👤     │     ║
         ║   │ [POWER]  │ [ENGINE] │     ║
         ║   └──────────┴──────────┘     ║
         ╚═══════════════════════════════╝
              ║  ║  ║  ║  ║  ║
              ╚══╩══╩══╩══╩══╝
                ENGINE THRUST
```

**Stats**:
- Hull: 30 HP
- Reactor: 8 power
- Starting Weapons: Burst Laser II (3 power)
- Starting Systems: Shields (2), Engines (1), Oxygen (1), Weapons (3)
- Starting Crew: 3 humans (1 pilot, 1 engineer, 1 weapons officer)

---

## THE STEALTH SHADOW - Stealth Infiltrator

**Role**: Stealth and precision strikes, weak defense
**Layout**: Sleek, angular design with cloaking bays

```
                 ╔══════════════════════════════╗
                 ║ SHADOW-CLASS STEALTH SHIP    ║
                 ║ Hull: 20  Crew: 2  Power: 6  ║
                 ╚══════════════════════════════╝

                        ▲
                       ╱│╲
                      ╱ │ ╲
                     ╱  │  ╲
                    ╱┌──┴──┐╲
                   ╱ │ HELM│ ╲
                  ╱  │  👤 │  ╲
                 ╱   │ 🎯  │   ╲
              ══╪════┴─────┴════╪══
               ╱│  ┌───────┐   │╲     ◄ Cloaking Field
              ╱ │  │ CLOAK │   │ ╲       Emitters
             ╱  │  │  ⚡⚡ │   │  ╲
            ╱   │  │  ▓▓▓  │   │   ╲
           ╱    │  │ [HIDE]│   │    ╲
          ╱     └──┴───────┴───┘     ╲
      ═══╪═══════════════════════════╪═══
         │ ┌──────────┬──────────┐  │
         │ │ WEAPONS  │ ENGINES  │  │
    ━━━━ │ │   ⚡⚡   │   👤    │  │ ━━━━  Ion Beam
         │ │   ▓━━━━  │  ⚙️⚙️⚙️ │  │
         │ │  [WEAPON]│ [ENGINE] │  │
         │ └──────────┴──────────┘  │
         ╲                           ╱
          ╲         ┌─────┐         ╱
           ╲        │REACT│        ╱
            ╲       │ ⚡⚡ │       ╱
             ╲      └─────┘      ╱
              ╲                 ╱
               ╲               ╱
                ╲             ╱
                 ╲═══════════╱
                  ╲    ║    ╱
                   ╲═══╩═══╱
                      ║║║
```

**Special**: Cloaking device (evade all attacks, but disables weapons)
**Weakness**: Only 20 hull, no shields at start

---

## THE MANTIS DEVASTATOR - Boarding Ship

**Role**: Teleporter-focused, strong crew combat
**Layout**: Wide design with teleporter chambers

```
            ╔════════════════════════════════════════╗
            ║ MANTIS DEVASTATOR - BOARDING CRUISER  ║
            ║ Hull: 25  Crew: 4  Power: 7           ║
            ╚════════════════════════════════════════╝

    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║  ┏━━━━━━━━━━━┓        ┏━━━━━━━━━━━┓            ║
    ║  ┃  WEAPONS  ┃        ┃  SHIELDS  ┃            ║
    ║  ┃    ⚡⚡    ┃        ┃    🛡️     ┃            ║
═══ ║  ┃   🔴━━━   ┃   HELM ┃    ⚡     ┃            ║ ═══
    ║  ┃  [WEAPON] ┃   👤🎯 ┃  [SHIELD] ┃            ║
    ║  ┗━━━━━━━━━━━┛        ┗━━━━━━━━━━━┛            ║
    ║                                                   ║
    ║  ╔═══════════════════════════════════════════╗  ║
    ║  ║      🌀 TELEPORTER BAY 🌀                 ║  ║
    ║  ║     ┏━━━━━━━━━━━━━━━━━━━┓                ║  ║
    ║  ║     ┃  ⚡⚡⚡ CHARGING  ┃                ║  ║
    ║  ║     ┃     👤 👤 👤      ┃  ◄ Boarding     ║  ║
    ║  ║     ┃  [BOARDING PARTY] ┃    Party Ready  ║  ║
    ║  ║     ┗━━━━━━━━━━━━━━━━━━━┛                ║  ║
    ║  ╚═══════════════════════════════════════════╝  ║
    ║                                                   ║
    ║  ┏━━━━━━━━━━━┓        ┏━━━━━━━━━━━┓            ║
    ║  ┃ MEDBAY    ┃        ┃  OXYGEN   ┃            ║
    ║  ┃   💉💉    ┃        ┃    💨     ┃            ║
    ║  ┃   👤      ┃        ┃    ⚡     ┃            ║
    ║  ┃  [HEAL]   ┃        ┃    [O2]   ┃            ║
    ║  ┗━━━━━━━━━━━┛        ┗━━━━━━━━━━━┛            ║
    ║                                                   ║
    ╚═══╦══════════════════════════════════════╦═══════╝
        ║     ┏━━━━━━━━━━┓  ┏━━━━━━━━━━┓    ║
        ║     ┃ REACTOR  ┃  ┃ ENGINES  ┃    ║
        ║     ┃  ⚡⚡⚡⚡ ┃  ┃  ⚙️⚙️   ┃    ║
        ║     ┗━━━━━━━━━━┛  ┗━━━━━━━━━━┛    ║
        ╚══════════════════════════════════════╝
```

**Special**: Teleporter allows crew to board enemy ships
**Tactics**: Weak weapons, send Mantis warriors to wreck enemy systems

---

## THE ROCK FORTRESS - Heavy Battlecruiser

**Role**: Tank - high hull, slow, devastating firepower
**Layout**: Thick, heavily armored appearance

```
            ╔═════════════════════════════════════╗
            ║  ROCK FORTRESS - HEAVY CRUISER     ║
            ║  Hull: 45  Crew: 3  Power: 10      ║
            ╚═════════════════════════════════════╝

         ╔═══════════════════════════════════╗
         ║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║ ◄ Heavy Armor
    ╔════╩═══════════════════════════════════╩════╗
    ║                                              ║
    ║   ╔══════════════════════════════════════╗  ║
    ║   ║  ┌────────────────────────────────┐ ║  ║
    ║   ║  │         HELM / BRIDGE          │ ║  ║
    ║   ║  │           👤 🎯                │ ║  ║
    ║   ║  │         [COMMAND]              │ ║  ║
    ║   ║  └────────────────────────────────┘ ║  ║
    ║   ╚══════════════════════════════════════╝  ║
    ║                                              ║
    ║   ┏━━━━━━━━━━━┓  ╔═══════╗  ┏━━━━━━━━━━━┓ ║
    ║   ┃  SHIELDS  ┃  ║ ARMOR ║  ┃  OXYGEN   ┃ ║
═══ ║   ┃    🛡️🛡️  ┃  ║  ▓▓▓  ║  ┃    💨     ┃ ║
    ║   ┃    ⚡⚡   ┃  ║  ▓▓▓  ║  ┃    ⚡     ┃ ║
    ║   ┃  [SHIELD] ┃  ║  ▓▓▓  ║  ┃    [O2]   ┃ ║
    ║   ┗━━━━━━━━━━━┛  ╚═══════╝  ┗━━━━━━━━━━━┛ ║
    ║                                              ║
    ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
    ║   ┃        HEAVY WEAPONS ARRAY          ┃ ║
    ║   ┃    🔴🔴🔴  ⚡⚡⚡⚡  🚀🚀           ┃ ║
🔴━━╬━━ ┃        👤        👤                 ┃ ║ ━━🚀
    ║   ┃   [MISSILES]  [LASERS]              ┃ ║
    ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
    ║                                              ║
    ║   ┏━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━┓  ║
    ║   ┃   REACTOR      ┃  ┃    ENGINES     ┃  ║
    ║   ┃  ⚡⚡⚡⚡⚡⚡⚡ ┃  ┃     ⚙️⚙️      ┃  ║
    ║   ┃  ⚡⚡⚡        ┃  ┃    (SLOW)      ┃  ║
    ║   ┃   [10 POWER]   ┃  ┃   [ENGINES]    ┃  ║
    ║   ┗━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━┛  ║
    ║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║
    ╚══════════════════════════════════════════════╝
```

**Special**: Extra armor plating (25% damage reduction), huge power reactor
**Weakness**: Engines are slow, evasion is poor

---

## THE ZOLTAN HARMONY - Energy Cruiser

**Role**: Shield-focused, powered by Zoltan crew
**Layout**: Sleek, energy-themed with glowing effects

```
            ╔═══════════════════════════════════╗
            ║  ZOLTAN HARMONY - ENERGY SHIP    ║
            ║  Hull: 28  Crew: 4  Power: 8     ║
            ╚═══════════════════════════════════╝

                      ⚡
                    ╱ │ ╲
                   ╱  │  ╲
                  ╱   │   ╲
           ⚡════╪════╪════╪════⚡  ◄ Zoltan Shield
                 │    │    │
           ┏━━━━━┷━━━━┷━━━━┷━━━━━┓
           ┃  ╔════════════════╗  ┃
           ┃  ║     HELM       ║  ┃
           ┃  ║      🎯👤⚡    ║  ┃
           ┃  ║   [ZOLTAN]     ║  ┃
           ┃  ╚════════════════╝  ┃
           ┃                       ┃
           ┃  ┌──────┬──────────┐ ┃
           ┃  │SHIELD│ WEAPONS  │ ┃
           ┃  │ 🛡️🛡️ │  ⚡⚡⚡  │ ┃
       ⚡══╪══│⚡⚡👤│  🔵━━━  │ ┃ ══⚡ Ion Weapons
           ┃  │ [Z]  │  [WEAPON]│ ┃
           ┃  └──────┴──────────┘ ┃
           ┃                       ┃
           ┃  ╔══════════════════╗ ┃
           ┃  ║   ZOLTAN CORE    ║ ┃
           ┃  ║     ⚡⚡⚡⚡      ║ ┃
           ┃  ║     ⚡👤👤⚡     ║ ┃ ◄ Zoltan provide
           ┃  ║     ⚡⚡⚡⚡      ║ ┃   bonus power
           ┃  ║    [REACTOR]     ║ ┃
           ┃  ╚══════════════════╝ ┃
           ┃                       ┃
           ┃  ┌──────┬──────────┐ ┃
           ┃  │  O2  │ ENGINES  │ ┃
           ┃  │  💨  │  ⚙️⚙️   │ ┃
           ┃  │  ⚡  │   👤⚡   │ ┃
           ┃  │ [O2] │ [ENGINE] │ ┃
           ┃  └──────┴──────────┘ ┃
           ┗━━━━━━━━━━━━━━━━━━━━━━━┛
              ⚡    ⚡    ⚡
               ║    ║    ║
               ╚════╩════╝
```

**Special**: Zoltan Super-Shield (blocks 5 damage before regular shields)
**Unique**: Each Zoltan crew member provides +1 power to their system

---

## THE ENGI SENTINEL - Drone Carrier

**Role**: Drone combat, repair automation
**Layout**: Boxy but functional, drone bays prominent

```
            ╔════════════════════════════════════╗
            ║  ENGI SENTINEL - DRONE CARRIER    ║
            ║  Hull: 30  Crew: 3  Power: 8      ║
            ╚════════════════════════════════════╝

    ╔══════════════════════════════════════════════╗
    ║  ┌─────────┬─────────┬─────────┐            ║
    ║  │  HELM   │SHIELDS  │  DRONE  │            ║
    ║  │   👤🎯  │  🛡️⚡   │   🤖    │ ◄ Combat   ║
    ║  │ [PILOT] │[SHIELD] │  [BAY]  │   Drone    ║
    ║  └─────────┴─────────┴─────────┘            ║
    ║                                              ║
🤖═════════════════════════════════════════════🤖 ◄ Launched
    ║                                              ║   Drones
    ║  ╔═══════════════════════════════════════╗  ║
    ║  ║     DRONE CONTROL CENTER              ║  ║
    ║  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   ║  ║
    ║  ║   ┃   🤖     🤖     🤖     🤖   ┃   ║  ║
    ║  ║   ┃  [DEF]  [ATK] [REPAIR] [?]  ┃   ║  ║
    ║  ║   ┃   ⚡     ⚡     ⚡      -    ┃   ║  ║
    ║  ║   ┃      👤 [ENGI OPERATOR]     ┃   ║  ║
    ║  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   ║  ║
    ║  ╚═══════════════════════════════════════╝  ║
    ║                                              ║
    ║  ┌─────────┬─────────┬─────────┐            ║
    ║  │WEAPONS  │  O2     │MEDBAY   │            ║
    ║  │  ⚡⚡   │  💨     │  💉💉   │            ║
    ║  │ [WEAPON]│  [O2]   │  👤     │            ║
    ║  └─────────┴─────────┴─────────┘            ║
    ║                                              ║
    ╚══╦═══════════════════════════════════════╦══╝
       ║  ┌────────────┬────────────┐         ║
       ║  │  REACTOR   │  ENGINES   │         ║
       ║  │   ⚡⚡⚡⚡  │   ⚙️⚙️    │         ║
       ║  │   👤       │  [ENGINE]  │         ║
       ║  └────────────┴────────────┘         ║
       ╚═════════════════════════════════════╝
```

**Special**: 4 drone slots (defense, combat, repair, boarding)
**Crew**: Engi are best repairers (+50% speed)

---

## ENEMY PIRATE RAIDER - Small & Fast

```
            ╔═══════════════════════════╗
            ║  PIRATE RAIDER           ║
            ║  Hull: 15  Crew: 2       ║
            ╚═══════════════════════════╝

                  ▲
                 ╱│╲
                ╱ │ ╲
            ════╪═╪═╪════
               ╱│ │ │╲
              ╱ │ │ │ ╲
          ═══╪══╪═╪═╪══╪═══
             │┌─┴─┴─┴─┐│
             ││ HELM  ││
             ││ 👤💀  ││
             │├───┬───┤│
        🔴━━━││WPN│O2 ││
             ││⚡ │💨 ││
             ││👤 │   ││
             │└───┴───┘│
             ╲         ╱
              ╲  ⚡⚡  ╱ ◄ Engine
               ╲ ⚙️  ╱
                ╲═══╱
                 ║║║
```

**Tactics**: Hit and run, weak hull but fast

---

## Room Details & Icons

### Room Types with Visual Indicators:

```
HELM/BRIDGE           SHIELDS              WEAPONS
┌─────────┐          ┌─────────┐          ┌─────────┐
│   🎯    │          │   🛡️    │          │  🔴🔴   │
│   👤    │          │   ⚡⚡   │          │   ⚡⚡⚡  │
│ [PILOT] │          │ [SHIELD]│          │ [WEAPON]│
└─────────┘          └─────────┘          └─────────┘

ENGINES              OXYGEN               MEDBAY
┌─────────┐          ┌─────────┐          ┌─────────┐
│  ⚙️⚙️   │          │   💨    │          │   💉    │
│   ⚡⚡   │          │   ⚡    │          │   👤    │
│ [ENGINE]│          │   [O2]  │          │  [HEAL] │
└─────────┘          └─────────┘          └─────────┘

REACTOR              SENSORS              TELEPORTER
┌─────────┐          ┌─────────┐          ┌─────────┐
│  ⚡⚡⚡  │          │   📡    │          │   🌀    │
│  ⚡⚡⚡  │          │   ⚡⚡   │          │  👤👤   │
│ [POWER] │          │ [SCAN]  │          │ [TPORT] │
└─────────┘          └─────────┘          └─────────┘

DRONE BAY            CLOAKING             DOORS
┌─────────┐          ┌─────────┐          ┌─────────┐
│   🤖    │          │   ▓▓▓   │          │  ├─┤    │
│   ⚡⚡   │          │   ⚡⚡   │          │   ⚡    │
│ [DRONES]│          │ [CLOAK] │          │ [DOOR]  │
└─────────┘          └─────────┘          └─────────┘
```

### Room States:

```
NORMAL               DAMAGED              CRITICAL
┌─────────┐          ┌─────────┐          ┌─────────┐
│  ⚡⚡    │          │  ⚡░     │          │  ░░     │
│   👤    │          │   👤    │          │   ⚠️    │
│         │          │  ⚠️     │          │  💀     │
└─────────┘          └─────────┘          └─────────┘

ON FIRE              BREACHED             NO OXYGEN
┌─────────┐          ┌─────────┐          ┌─────────┐
│  🔥🔥   │          │ ░░░░░░░ │          │  ░░░░   │
│   👤💀  │          │ ░👤░░░░ │          │   👤⚠️  │
│  🔥     │          │ BREACH  │          │ 💀  0%  │
└─────────┘          └─────────┘          └─────────┘
```

---

## Combat View Examples

### Side-by-Side Combat

```
╔═══════════════════════════════════════════════════════════════════╗
║              COMBAT: SECTOR 3 - PIRATE AMBUSH                     ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   YOUR KESTREL                        PIRATE RAIDER              ║
║                                                                   ║
║   ┏━━━━━━━━━━┓                           ▲                       ║
║   ┃ HELM 🎯 ┃                          ╱│╲                       ║
║   ┃  👤     ┃                      ════╪═╪═╪════                 ║
║   ┣━━━━━━━━━━┫                        ╱│ │ │╲                    ║
║   ┃ WEAPONS ┃                       ══╪══╪═╪═╪══                 ║
║   ┃ ⚡⚡⚡   ┃                        │┌─┴─┴─┴─┐│                 ║
║   ┃ 🔴🔴▶━━━━━━━━━━━━━━━━━━━━━━━━━━━▶💥👤💀🔥││ ◄ HIT!          ║
║   ┃ [READY] ┃                        │├───┬───┤│                 ║
║   ┣━━━━━━━━━━┫                        ││⚡ │💨 ││                 ║
║   ┃ SHIELDS ┃                        ││👤 │   ││                 ║
║   ┃ 🛡️🛡️🛡️  ┃                        │└───┴───┘│                 ║
║   ┃  ⚡⚡    ┃                        ╲  ⚡⚡  ╱                   ║
║   ┗━━━━━━━━━━┛                         ╲ ⚙️  ╱                    ║
║                                          ╲═══╱                    ║
║   🛡️ SHIELDS: ████ 4/4                  🛡️ SHIELDS: ░░ 0/2       ║
║   ❤️  HULL:    ████████ 28/30            ❤️  HULL:    ██░░ 6/15   ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  > Burst Laser II hit Pirate Weapons for 2 damage!               ║
║  > Enemy weapons disabled! 🎯                                     ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Implementation Notes

### Data Structure

```python
class Room:
    name: str           # "Helm", "Weapons", etc.
    system_type: str    # "helm", "weapons", "shields"
    x, y: int          # Position in ship grid
    width, height: int # Room size
    connections: list  # Connected rooms (for pathfinding)
    power: int         # Power allocated to system
    max_power: int     # Max power this system can use
    health: float      # System health 0.0-1.0
    crew: list         # Crew currently in room
    on_fire: bool
    breached: bool
    oxygen_level: float

class ShipLayout:
    rooms: dict        # Room grid
    hull_shape: list   # Unicode art for hull exterior
    weapon_mounts: list # Positions for weapon hardpoints
```

### Rendering Layers

1. **Hull outline** (border, shape)
2. **Room grid** (boxes, connections)
3. **System icons** (⚡🛡️🔴 etc.)
4. **Crew positions** (👤)
5. **Effects** (🔥💥⚡)
6. **Status overlays** (damage, warnings)

This gives us beautiful, functional, and varied ship designs!

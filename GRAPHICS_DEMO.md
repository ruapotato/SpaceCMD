# spacecmd Graphics System

## ASCII Art Library (libaa-style) Capabilities

spacecmd will use advanced terminal graphics techniques to create the most impressive command-line visuals possible.

## Techniques

### 1. Braille Unicode Characters (2x4 pixel resolution)
- **Resolution**: 80x24 terminal = 160x96 effective pixels
- **Use cases**: Shield effects, weapon beams, particle systems, curved surfaces
- **Character range**: U+2800 to U+28FF (256 characters)

```
Shield bubble effect:
    ⢀⣠⣤⣤⣤⣤⣀⡀
  ⢀⣾⠋⠀⠀⠀⠀⠀⠙⣷⡀
 ⢀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠹⣧⡀
⢠⣿⠀⠀⠀⣿⣿⡄⠀⠀⠀⢿⡄
⣿⡇⠀⠀⠀⣿⣿⡇⠀⠀⠀⢸⣿
⣿⡇⠀⠀⠀⠙⠋⠀⠀⠀⠀⢸⣿
⠘⣷⡀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠃
 ⠘⢷⣄⡀⠀⠀⠀⠀⣀⣴⠏
  ⠈⠙⠛⠿⠿⠿⠛⠋⠁

Laser beam:
⣿⣿⣿⣿⣿⣿━━━━━━━━▶
```

### 2. Box Drawing (Ship Structure)
- **Lines**: ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
- **Double**: ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
- **Rounded**: ╭ ╮ ╰ ╯
- **Heavy**: ━ ┃ ┏ ┓ ┗ ┛

```
Detailed ship layout with rooms:

╔══════════════════════════════════════════════════════════╗
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃  SHIELDS: ████████░░ 8/10   HULL: █████░░░░░ 15/24  ┃ ║
║ ┃  POWER:   ⚡⚡⚡⚡⚡⚡ 6/8      O2: ████████ 100%  ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   ┏━━━━━━━┳━━━━━━━┳━━━━━━━┓                           ║
║   ┃ HELM  ┃SHIELDS┃  O2   ┃   [PLAYER SHIP]            ║
║   ┃  👤   ┃  ⚡⚡ ┃  ⚡   ┃                           ║
║   ┃  🎯   ┃  ▓▓▓  ┃  💨   ┃   Kestrel-Class            ║
║   ┣━━━━━━━╋━━━━━━━╋━━━━━━━┫                           ║
║   ┃WEAPONS┃REACTOR┃ENGINES┃                            ║
║   ┃ ⚡⚡⚡ ┃  ⚡⚡ ┃  👤  ┃                           ║
║   ┃ 🔴🔴▶ ┃  ⚡⚡ ┃  ⚙️   ┃                           ║
║   ┣━━━━━━━╋━━━━━━━╋━━━━━━━┫                           ║
║   ┃ CARGO ┃SENSORS┃MEDBAY ┃                            ║
║   ┃  📦   ┃  📡   ┃  💉   ┃                           ║
║   ┃       ┃       ┃  👤   ┃                           ║
║   ┗━━━━━━━┻━━━━━━━┻━━━━━━━┛                           ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  WEAPONS:  [████░░] [██░░░░] [█████░]                   ║
║            Burst Laser II  |  Beam  |  Missiles         ║
╚══════════════════════════════════════════════════════════╝
```

### 3. Block Elements (Solid Fills & Progress Bars)
- **Full blocks**: █ (100%)
- **Partial**: ▓ (75%), ▒ (50%), ░ (25%)
- **Half blocks**: ▀ (top), ▄ (bottom), ▌ (left), ▐ (right)
- **Quadrants**: ▖ ▗ ▘ ▝ ▞ ▚ ▙ ▟

```
Health bars:
████████████░░░░░░░░  60%  HEALTHY
██████░░░░░░░░░░░░░░  30%  DAMAGED
███░░░░░░░░░░░░░░░░░  15%  CRITICAL

Ship damage visualization:
╔═══════════════╗
║ █████░░░░░░░░ ║  Hull Integrity
║ ████████████  ║  Shields
║ ██████░░░░░░░ ║  Oxygen
╚═══════════════╝

Gradient effects:
████▓▓▓▓▒▒▒▒░░░░ (Heat dissipation)
```

### 4. Geometric Shapes (Combat Effects)
```
Explosions:
    ⚠️
   💥💥💥
  💥🔥🔥💥
   💥💥💥
    💥

Missile trajectory:
🚀 ━━━━━━━━▶ 💥

Shield impact:
⚡ ━━━━━━▶ 🛡️  *BLOCKED*

Fire spreading:
Normal:  ┃     ┃
Burning: ┃ 🔥  ┃ 🔥
Critical:┃🔥🔥🔥┃
```

### 5. Emoji & Unicode Symbols
```
👤 🧑 👨 👩 - Crew members (different races)
⚡ - Power/electricity
🔥 - Fire
💥 - Explosion
🚀 - Missiles
🛡️ - Shields
⚠️ - Warning
💀 - Death/destroyed
💉 - Medical
🔧 - Repair
📡 - Sensors
🎯 - Targeting
⚙️ - Engines
💨 - Venting/oxygen
🔴 🟢 🟡 - Status indicators
━━━▶ - Laser beam
╰━━╯ - Curved connections
```

### 6. Color Schemes (ANSI 256 + TrueColor)

```python
# System states
ONLINE =     "\033[32m"  # Green
DAMAGED =    "\033[33m"  # Yellow
CRITICAL =   "\033[31m"  # Red
DISABLED =   "\033[90m"  # Dark gray
SHIELDED =   "\033[36m"  # Cyan

# Combat effects
LASER_RED =  "\033[91m"
LASER_BLUE = "\033[94m"
ION_PULSE =  "\033[95m"
EXPLOSION =  "\033[93m"
FIRE =       "\033[38;5;208m"  # Orange

# UI elements
BORDER =     "\033[37m"  # White
HIGHLIGHT =  "\033[1;97m"  # Bold bright white
DIM =        "\033[2m"  # Dim text
```

## Combat Visualization Example

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  COMBAT: Pirate Fighter                                   ┃
┃  ⚠️  ENEMY WEAPONS CHARGING! ⚠️                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  YOUR SHIP                           ENEMY SHIP

 ┏━━━━━━━┓                           ┏━━━━━━━┓
 ┃ 🎯    ┃                           ┃ 💀    ┃
 ┃  ⚡⚡ ┃ ━━━━━━━━━━━━━━━━━━━━━━━▶ ┃  ░░   ┃
 ┃ 👤 👤 ┃         FIRING!           ┃ 🔥 👤 ┃
 ┗━━━━━━━┛                           ┗━━━━━━━┛

 SHIELDS: 🛡️🛡️🛡️🛡️ (4)              SHIELDS: 🛡️░░ (1)
 HULL:    ████████ (24/24)          HULL:    ████░░ (8/12)
 O2:      ████████ (100%)           O2:      ███░░░ (60%)

 ⚡ BURST LASER II [████░░] 66%
 ⚡ ION BLAST      [██████] READY → fire ion
 🚀 MISSILE        [██████] READY → fire missile
```

## Animation System

Real-time effects using frame-based animation:

```
Frame 1:  🔴━━━━━━━━━━━━━━━▶ 🛡️
Frame 2:  🔴━━━━━━━━━━━━━━━━━▶ 🛡️
Frame 3:  🔴━━━━━━━━━━━━━━━━━━━▶ 💥
Frame 4:      💥💥💥             ⚡
Frame 5:       💨💨              ░░

Typing effect: L o a d i n g . . .
Blinking: ⚠️ WARNING ⚠️ (toggle on/off)
Spinning: | / ─ \  (loading indicator)
```

## Advanced Effects

### Particle Systems
```python
# Explosion particles
particles = [
    ("💥", x+0, y+0),
    ("*", x+1, y+0),
    ("*", x-1, y+0),
    ("·", x+2, y+1),
    ("·", x-2, y-1),
]

# Fade out over time
opacity = 1.0 → 0.8 → 0.6 → 0.4 → 0.2 → gone
```

### Parallax Background
```
Layer 1 (far):   ·  ·    ·     ·  (slow stars)
Layer 2 (mid):    ·    ·   ·      (medium)
Layer 3 (near):  ·   ·       ·    (fast)
```

### Screen Shake (Impact)
```
Normal position: (0, 0)
Shake frame 1:   (-1, 0)
Shake frame 2:   (1, 1)
Shake frame 3:   (-1, -1)
Shake frame 4:   (0, 0)
```

## Technical Implementation

### Rendering Engine Components

```python
class Renderer:
    - Canvas system (double buffering)
    - Layer management (background, ship, effects, UI, text)
    - Sprite system (pre-rendered ASCII art)
    - Animation queue
    - Color manager (ANSI codes)
    - Camera/viewport

class EffectSystem:
    - Particle emitters
    - Animation sequences
    - Screen shake
    - Flash/fade effects
    - Damage numbers
```

### Performance
- Pre-render static elements (ship layouts)
- Only redraw changed regions (dirty rectangles)
- Double buffering (draw to buffer, then flip)
- Cap at 30 FPS for smooth animation

### Terminal Requirements
- Minimum: 80x24, monochrome, ASCII only
- Recommended: 120x40, 256 colors, Unicode support
- Optimal: 160x50+, TrueColor, Unicode, fast refresh

## Example Ship Designs

### Small Fighter
```
  ╭─╮
  │⚡│
╭─┴─┴─╮
│ 👤  │
╰─┬─┬─╯
  │⚡│
  ╰─╯
```

### Large Cruiser
```
  ┏━━━━━━━━━┓
  ┃  ⚡ ⚡  ┃
┏━┻━━━━━━━━━┻━┓
┃ 👤  💉  👤  ┃
┣━━━━┳━━┳━━━━━┫
┃ ⚡⚡┃📡┃ ⚡⚡ ┃
┗━━━━┻━━┻━━━━━┛
```

### Stealth Ship
```
    ╱╲
   ╱⚡╲
  ╱👤▓╲
 ╱━━━━━╲
╱_______╲
```

## Future Enhancements

1. **Texture mapping** - Use character patterns for "materials"
2. **Dithering** - Floyd-Steinberg for smoother gradients
3. **3D projection** - Rotate ships in 3D space, project to 2D ASCII
4. **Fog of war** - Unknown areas rendered as `?` or `░`
5. **Minimap** - Braille-based tactical overview
6. **Damage decals** - Persistent visual damage on ship hull

## Inspiration

- dwarf fortress (detailed ASCII simulation)
- nethack/ADOM (expressive roguelike graphics)
- ascii-patrol (space combat)
- bb (aalib demo - 3D ASCII)
- cmatrix (animated effects)
- ASCIIQuarium (smooth animations)

---

**Bottom line**: We can create absolutely stunning terminal graphics that rival or exceed classic ASCII games, with modern Unicode giving us 2-4x the resolution of traditional ASCII art!

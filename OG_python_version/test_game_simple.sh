#!/bin/bash
# Automated test of the game with fire command

timeout 5 python3 play.py --ship kestrel --no-intro <<'EOF'
# Wait for combat to start (game auto-triggers encounter)
sleep 2

# Check weapons
weapons

# Target enemy
enemy
target "Weapon Pod"

# Fire weapon
fire 1

# Exit
exit
EOF

#!/bin/bash
# Demo gameplay script - shows spacecmd in action

echo "Starting spacecmd gameplay demo..."
echo ""

# Create command sequence
cat << 'EOF' | python3 play.py --ship kestrel --no-intro

status
systems
crew
power weapons 3
wait 1
damage weapons 0.5
systems
wait 2
assign vega helm
crew
power shields 4
wait 1
exit
EOF

echo ""
echo "Demo complete!"

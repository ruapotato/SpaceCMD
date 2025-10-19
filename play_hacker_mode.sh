#!/bin/bash
# Quick launcher for Hacker FTL mode

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║           SPACECMD - HACKERS MEET FTL                     ║"
echo "║                                                           ║"
echo "║  💻 Hack enemy ships                                      ║"
echo "║  🚀 Fire weapons                                          ║"
echo "║  🦠 Deploy malware                                        ║"
echo "║  🔓 Exploit vulnerabilities                               ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Choose mode:"
echo "  1. Play (Console Mode)"
echo "  2. Demo (Watch hacker gameplay)"
echo "  3. GUI Mode (Full Desktop)"
echo ""
read -p "Select [1-3]: " choice

case $choice in
    1)
        echo "Starting console mode..."
        python3 play.py --no-gui --console --ship kestrel
        ;;
    2)
        echo "Starting hacker demo..."
        python3 test_hacker_ftl.py
        ;;
    3)
        echo "Starting GUI mode..."
        python3 play.py --gui --ship kestrel
        ;;
    *)
        echo "Invalid choice. Starting console mode..."
        python3 play.py --no-gui --console --ship kestrel
        ;;
esac

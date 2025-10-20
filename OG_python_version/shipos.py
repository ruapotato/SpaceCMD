#!/usr/bin/env python3
"""
spacecmd - Ship Operating System

Launch into ShipOS - a Unix-like OS for your spaceship.
All gameplay happens through PooScript and the command line.
"""

import sys
import readline
from core.ships import create_ship, SHIP_TEMPLATES
from core.shipos import ShipOSBridge, create_ship_binaries
from core.system import UnixSystem


def print_shipos_intro():
    """Print ShipOS boot sequence"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                       SHIP OS v1.0                            ║
║                                                               ║
║              Booting ship computer systems...                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

[BOOT] Initializing reactor core...                         [ OK ]
[BOOT] Loading life support systems...                      [ OK ]
[BOOT] Mounting ship filesystems...                         [ OK ]
[BOOT] Starting crew management daemon...                   [ OK ]
[BOOT] Initializing weapons control...                      [ OK ]
[BOOT] Loading navigation systems...                        [ OK ]

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    SHIP OS READY                              ║
║                                                               ║
║  All ship systems are accessible through the command line.   ║
║                                                               ║
║  Try these commands:                                          ║
║    status          - Display ship status                      ║
║    systems         - List all systems                         ║
║    crew            - Show crew roster                         ║
║    power           - Power allocation                         ║
║    ls /systems     - Browse ship systems                      ║
║    cat /ship/hull  - Check hull integrity                     ║
║                                                               ║
║  Type 'help' for shell commands                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

""")


def choose_ship():
    """Let captain choose their ship"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                    SHIP SELECTION                             ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print("Choose your ship:")
    print()

    ship_info = {
        "kestrel": "Balanced cruiser - shields, good crew (RECOMMENDED)",
        "stealth": "Stealth ship - cloaking, no shields (HARD)",
        "mantis": "Boarding ship - teleporter, strong crew (AGGRESSIVE)"
    }

    for i, (ship_type, description) in enumerate(ship_info.items(), 1):
        print(f"  {i}. {ship_type.upper():10} - {description}")

    print()

    while True:
        try:
            choice = input("Select ship (1-3) or name: ").strip().lower()

            if choice in ['1', '2', '3']:
                ship_type = list(ship_info.keys())[int(choice) - 1]
                return ship_type

            if choice in SHIP_TEMPLATES:
                return choice

            print(f"Invalid choice: {choice}")

        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting...")
            sys.exit(0)


def interactive_shipos(system, ship):
    """
    Run interactive ShipOS shell.
    Modified version of the hacking game shell for ship control.
    """
    # Auto-login as root (captain has root access!)
    login_result = system.login('root', 'root')
    if not login_result:
        print('Ship OS login failed!')
        return False

    # Set up tab completion
    def completer(text, state):
        """Tab completion for commands and paths"""
        if state == 0:
            line = readline.get_line_buffer()
            begin_idx = readline.get_begidx()

            process = system.processes.get_process(system.shell_pid)
            if not process:
                return None

            if begin_idx == 0:
                # Complete command names
                matches = []
                for bin_dir in ['/bin', '/usr/bin']:
                    try:
                        entries = system.vfs.list_dir(bin_dir, 1)
                        if entries:
                            for name, _ in entries:
                                if name.startswith(text) and name not in ('.', '..'):
                                    matches.append(name)
                    except:
                        pass
                completer.matches = sorted(set(matches))
            else:
                # Complete file paths
                if '/' in text:
                    last_slash = text.rfind('/')
                    dir_part = text[:last_slash] or '/'
                    file_part = text[last_slash + 1:]
                else:
                    dir_part = '.'
                    file_part = text

                matches = []
                try:
                    entries = system.vfs.list_dir(dir_part, process.cwd)
                    if entries:
                        for name, ino in entries:
                            if name.startswith(file_part) and name not in ('.', '..'):
                                if dir_part == '.':
                                    matches.append(name)
                                elif dir_part == '/':
                                    matches.append('/' + name)
                                else:
                                    matches.append(dir_part + '/' + name)
                except:
                    pass

                completer.matches = sorted(matches)

        try:
            return completer.matches[state]
        except (IndexError, AttributeError):
            return None

    completer.matches = []

    # Configure readline
    readline.set_completer(completer)
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \\t\\n;')

    # Set up I/O callbacks
    def input_callback(prompt):
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            return 'exit'

    def output_callback(text):
        print(text, end='')
        sys.stdout.flush()

    def error_callback(text):
        print(text, end='', file=sys.stderr)
        sys.stderr.flush()

    # Set callbacks
    system.shell.executor.input_callback = input_callback
    system.shell.executor.output_callback = output_callback
    system.shell.executor.error_callback = error_callback

    system.vfs.input_callback = input_callback
    system.vfs.output_callback = output_callback
    system.vfs.error_callback = error_callback

    # Main shell loop
    while True:
        try:
            # Update ship state in VFS before each command
            # (In a real implementation, this would be more efficient)

            exit_code, stdout, stderr = system.shell.execute('/bin/pooshell', system.shell_pid, b'')

            if not system.is_alive():
                print(f'\\n[Ship computer offline]')
                return False

            # Update ship every tick
            ship.update(0.1)

            # Check if we should exit
            if exit_code != 255:
                break

        except KeyboardInterrupt:
            print('\\n^C')
            continue
        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            import traceback
            traceback.print_exc()
            break

    return True


def main():
    """Main entry point for ShipOS"""
    import argparse

    parser = argparse.ArgumentParser(description='ShipOS - Ship Operating System')
    parser.add_argument('--ship', choices=list(SHIP_TEMPLATES.keys()),
                        help='Choose ship type')
    parser.add_argument('--no-intro', action='store_true',
                        help='Skip boot sequence')

    args = parser.parse_args()

    # Print boot sequence
    if not args.no_intro:
        print_shipos_intro()

    # Choose ship
    if args.ship:
        ship_type = args.ship
        print(f"Loading {ship_type.upper()}...")
        print()
    else:
        ship_type = choose_ship()
        print()

    # Create ship
    try:
        ship = create_ship(ship_type)
        print(f"✓ {ship.name} systems online")
        print(f"  Class: {ship.ship_class}")
        print(f"  Hull: {ship.hull}")
        print(f"  Crew: {len(ship.crew)}")
        print()
    except Exception as e:
        print(f"ERROR: Failed to initialize ship: {e}")
        sys.exit(1)

    # Create ship's computer system (VFS, shell, etc.)
    print("Initializing ship computer...")
    system = UnixSystem(ship.name)
    system.boot()

    # Mount ship into VFS
    print("Mounting ship systems into filesystem...")
    bridge = ShipOSBridge(ship, system)
    bridge.mount_ship()

    # Create ship command binaries
    print("Installing ship control software...")
    create_ship_binaries(system, ship)

    print("✓ Ship OS ready")
    print()
    try:
        input("Press Enter to access ship computer...")
    except (EOFError, KeyboardInterrupt):
        pass
    print()

    # Launch shell
    try:
        interactive_shipos(system, ship)
    except Exception as e:
        print(f"\\n\\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║                    Ship OS Shutdown                           ║")
    print("║                                                               ║")
    print("║              Safe travels, Captain.                           ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()


if __name__ == '__main__':
    main()

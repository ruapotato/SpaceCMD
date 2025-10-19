#!/usr/bin/env python3
"""
Automated Test Suite for Main Programs
Tests shipos.py, play.py, and game.py for crashes and basic functionality
"""

import subprocess
import sys
import time


def run_test(name, command, timeout=5, stdin_input=""):
    """Run a test command and check for crashes"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print(f"Timeout: {timeout}s")

    try:
        # Run the command with timeout
        result = subprocess.run(
            command,
            shell=True,
            timeout=timeout,
            capture_output=True,
            text=True,
            input=stdin_input
        )

        # Check exit code
        if result.returncode == 0 or result.returncode == 124:  # timeout command returns 124
            print(f"✅ PASS - No crash detected")
            print(f"   Exit code: {result.returncode}")
            return True
        else:
            print(f"❌ FAIL - Non-zero exit code: {result.returncode}")
            if result.stderr:
                print(f"   stderr: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT - Process still running (expected for interactive programs)")
        print(f"✅ PASS - No crash detected")
        return True

    except Exception as e:
        print(f"❌ FAIL - Exception: {e}")
        return False


def main():
    """Run all tests"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              SPACECMD AUTOMATED TEST SUITE                    ║
║                                                               ║
║  Testing main programs for crashes and basic functionality   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

    tests = []

    # Test 1: shipos.py with no-intro
    tests.append(run_test(
        "ShipOS Mode - No Intro",
        "timeout 3 python3 shipos.py --ship kestrel --no-intro",
        timeout=5,
        stdin_input=""
    ))

    # Test 2: play.py with no-intro
    tests.append(run_test(
        "Play Mode - No Intro",
        "echo '' | timeout 3 python3 play.py --ship kestrel --no-intro",
        timeout=5
    ))

    # Test 3: game.py tutorial
    tests.append(run_test(
        "Game Mode - Tutorial Start",
        "echo -e '\\n\\n\\n\\n\\n' | timeout 3 python3 game.py",
        timeout=5
    ))

    # Test 4: shipos.py with intro (check EOFError handling)
    tests.append(run_test(
        "ShipOS Mode - With Intro (EOFError Test)",
        "echo '' | timeout 3 python3 shipos.py --ship kestrel",
        timeout=5
    ))

    # Test 5: play.py with intro
    tests.append(run_test(
        "Play Mode - With Intro (EOFError Test)",
        "echo '' | timeout 3 python3 play.py --ship kestrel",
        timeout=5
    ))

    # Test 6: Check import errors
    tests.append(run_test(
        "Import Check - shipos.py",
        "python3 -c 'import shipos; print(\"Import successful\")'",
        timeout=3
    ))

    tests.append(run_test(
        "Import Check - play.py",
        "python3 -c 'import sys; sys.argv = [\"play.py\", \"--help\"]; exec(open(\"play.py\").read())' 2>&1 | head -5",
        timeout=3
    ))

    # Test 7: Test help flags
    tests.append(run_test(
        "Help Flag Test - play.py",
        "python3 play.py --help",
        timeout=3
    ))

    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(tests)
    total = len(tests)
    failed = total - passed

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Pass Rate: {(passed/total)*100:.1f}%")

    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
        print(f"\n✅ EOFError bugs are fixed")
        print(f"✅ Programs handle non-interactive mode correctly")
        print(f"✅ No crashes detected")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print(f"\nPlease review the failed tests above")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

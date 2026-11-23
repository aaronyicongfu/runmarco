#!/usr/bin/env python3
"""

My preferred usage:
    python3 keystrkes.py "cmd+v > ctrl+tab > return" -r 10 -d 1.0

Run a series of keystrokes on macOS. No third-party packages needed
(uses the built-in `osascript` / System Events).

Usage examples:
    python3 keystrokes.py                       # runs the default sequence below
    python3 keystrokes.py "ctrl+tab > cmd+v"    # custom sequence
    python3 keystrokes.py "ctrl+tab > cmd+v" -r 5 -d 0.3
    python3 keystrokes.py "cmd+a > cmd+c > right" --dry-run

Sequence syntax:
    Steps are separated by ">" (or "->"). Each step is modifiers + key joined by "+".
    Modifiers: cmd, ctrl, alt/opt, shift
    Keys: any single character (a, v, 1, ...) or a name:
          tab, return, enter, space, esc, delete, left, right, up, down,
          home, end, pageup, pagedown, f1..f12

First run: macOS will ask to grant Accessibility permission to your terminal
(System Settings > Privacy & Security > Accessibility). Enable it, then re-run.
"""

import argparse
import subprocess
import sys
import time

DEFAULT_SEQUENCE = "ctrl+tab > cmd+v > ctrl+tab > cmd+v > ctrl+tab > cmd+v"

MODIFIERS = {
    "cmd": "command down",
    "command": "command down",
    "ctrl": "control down",
    "control": "control down",
    "alt": "option down",
    "opt": "option down",
    "option": "option down",
    "shift": "shift down",
}

KEY_CODES = {
    "tab": 48,
    "return": 36,
    "enter": 36,
    "space": 49,
    "esc": 53,
    "escape": 53,
    "delete": 51,
    "backspace": 51,
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
    "home": 115,
    "end": 119,
    "pageup": 116,
    "pagedown": 121,
    "f1": 122,
    "f2": 120,
    "f3": 99,
    "f4": 118,
    "f5": 96,
    "f6": 97,
    "f7": 98,
    "f8": 100,
    "f9": 101,
    "f10": 109,
    "f11": 103,
    "f12": 111,
}


def parse_step(step: str) -> str:
    """Convert one step like 'ctrl+tab' into an AppleScript command line."""
    parts = [p.strip().lower() for p in step.split("+") if p.strip()]
    if not parts:
        raise ValueError(f"Empty step: {step!r}")

    key, mods = parts[-1], parts[:-1]
    for m in mods:
        if m not in MODIFIERS:
            raise ValueError(f"Unknown modifier {m!r} in step {step!r}")
    using = ""
    if mods:
        using = " using {" + ", ".join(MODIFIERS[m] for m in mods) + "}"

    if key in KEY_CODES:
        return f"key code {KEY_CODES[key]}{using}"
    if len(key) == 1:
        escaped = key.replace("\\", "\\\\").replace('"', '\\"')
        return f'keystroke "{escaped}"{using}'
    raise ValueError(f"Unknown key {key!r} in step {step!r}")


def build_applescript(sequence: str, repeat: int, delay: float) -> str:
    steps = [s.strip() for s in sequence.replace("->", ">").split(">") if s.strip()]
    if not steps:
        raise ValueError("No steps found in sequence.")
    commands = [parse_step(s) for s in steps]

    lines = ['tell application "System Events"']
    for _ in range(repeat):
        for cmd in commands:
            lines.append(f"    {cmd}")
            lines.append(f"    delay {delay}")
    lines.append("end tell")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a series of keystrokes on macOS."
    )
    parser.add_argument(
        "sequence",
        nargs="?",
        default=DEFAULT_SEQUENCE,
        help=f'Keystroke sequence (default: "{DEFAULT_SEQUENCE}")',
    )
    parser.add_argument(
        "-r",
        "--repeat",
        type=int,
        default=1,
        help="Repeat the whole sequence N times (default: 1)",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=0.2,
        help="Seconds to wait after each keystroke (default: 0.2)",
    )
    parser.add_argument(
        "-s",
        "--start-delay",
        type=float,
        default=3.0,
        help="Seconds to wait before starting, so you can focus the target window (default: 3)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated AppleScript instead of running it",
    )
    args = parser.parse_args()

    if sys.platform != "darwin" and not args.dry_run:
        print("This script only runs on macOS.", file=sys.stderr)
        return 1

    try:
        script = build_applescript(args.sequence, args.repeat, args.delay)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(script)
        return 0

    print(f"Starting in {args.start_delay}s — switch to the target window now...")
    time.sleep(args.start_delay)

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        if "not allowed" in result.stderr or "1002" in result.stderr:
            print(
                "\nGrant Accessibility permission to your terminal app in "
                "System Settings > Privacy & Security > Accessibility.",
                file=sys.stderr,
            )
        return result.returncode

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

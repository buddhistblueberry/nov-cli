"""Interactive UI helpers: choose from a list, and view text.

`pick` prefers fzf (the nice fuzzy finder) when available and falls back
to a simple numbered menu. `view` pipes text into `less` so long chapters
can be scrolled; if `less` is missing it just prints.
"""

import subprocess
import sys


def pick(options, prompt: str = "Select"):
    """Pick one item from `options`.

    `options` is a list of either strings or (label, value) tuples.
    Returns the chosen value (or the string itself).
    """
    if not options:
        return None

    labels = [o[0] if isinstance(o, tuple) else str(o) for o in options]
    values = [o[1] if isinstance(o, tuple) else o for o in options]

    try:
        result = subprocess.run(
            ["fzf", "--prompt", f"{prompt}: "],
            input="\n".join(labels),
            text=True,
            capture_output=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            chosen = result.stdout.strip()
            return values[labels.index(chosen)]
    except FileNotFoundError:
        pass  # fzf not installed -> fall through to numbered menu

    print(f"\n{prompt}:")
    for i, label in enumerate(labels, 1):
        print(f"  {i}. {label}")

    while True:
        try:
            raw = input("Choice (number): ").strip()
            index = int(raw) - 1
            if 0 <= index < len(values):
                return values[index]
        except (ValueError, EOFError):
            pass
        print("Invalid choice, try again.")


def view(text: str) -> None:
    """Show `text` in a scrollable pager."""
    try:
        subprocess.run(["less", "-F", "-R", "-K"], input=text, text=True)
    except FileNotFoundError:
        print(text)

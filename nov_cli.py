#!/usr/bin/env python3
"""nov-cli — search and read novels from the web, ani-cli style.

Usage:
    nov-cli "pride and prejudice"        # search, then pick book + part
    nov-cli -p gutenberg "sherlock"      # limit to one provider
    nov-cli -U                           # self-update from git

Type a query, pick a book, pick a readable part, and it opens in `less`.
"""

import argparse
import os
import subprocess
import sys

from core.http import NovHttpError, fetch
from core.ui import pick, view
from providers import PROVIDERS


def search_all(query: str, provider_name: str | None = None) -> list:
    results = []
    for name, provider in PROVIDERS.items():
        if provider_name and name != provider_name:
            continue
        try:
            results.extend(provider.search(query))
        except Exception as exc:  # keep one broken provider from killing all
            print(f"[warn] provider '{name}' failed: {exc}", file=sys.stderr)
    return results


def self_update() -> None:
    """Pull the latest code from the git remote, if we're in a repo."""
    here = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(os.path.join(here, ".git")):
        print("Self-update only works inside a git checkout.", file=sys.stderr)
        return
    try:
        subprocess.run(
            ["git", "-C", here, "pull", "--ff-only"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Updated. Restart nov-cli to use the new version.")
    except FileNotFoundError:
        print("git is not installed; cannot self-update.", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        msg = exc.stderr.strip() or exc.stdout.strip()
        print(f"Self-update failed: {msg}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nov-cli",
        description="Search and read novels from the web (ani-cli style).",
    )
    parser.add_argument("query", nargs="?", help="search query")
    parser.add_argument("-p", "--provider", help="limit to one provider")
    parser.add_argument(
        "-U", "--update", action="store_true", help="self-update via git pull"
    )
    args = parser.parse_args()

    if args.update:
        self_update()
        return 0

    if not args.query:
        parser.print_help()
        return 0

    print(f"Searching for: {args.query}")
    novels = search_all(args.query, args.provider)
    if not novels:
        print("No results found.")
        return 0

    novel = pick(
        [(f"{n.title} — {n.author or 'unknown'}", n) for n in novels], "Novel"
    )
    if not novel:
        return 0

    try:
        chapters = novel.provider.chapters(novel)
    except Exception as exc:
        print(f"[error] could not list parts: {exc}", file=sys.stderr)
        return 1

    chapter = pick([(c.title, c) for c in chapters], "Part")
    if not chapter:
        return 0

    print("Fetching…")
    try:
        text = novel.provider.content(chapter)
    except NovHttpError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    view(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # last-resort guard: never show a raw traceback
        print(f"[error] something went wrong: {exc}", file=sys.stderr)
        sys.exit(1)

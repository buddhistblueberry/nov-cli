#!/usr/bin/env python3
"""nov-cli — search and read novels from the web, ani-cli style.

Usage:
    nov-cli "pride and prejudice"        # search, then pick book + part
    nov-cli -p gutenberg "sherlock"      # limit to one provider
    nov-cli -d "alice"                   # save the chosen part to a .txt file
    nov-cli -r                           # resume the last-read book
    nov-cli -U                           # self-update from git

Type a query, pick a book, pick a readable part, and it opens in `less`.
"""

import argparse
import os
import subprocess
import sys

from core.http import NovHttpError, fetch
from core.ui import pick, view
from core import bookmarks, save
from providers import PROVIDERS
from providers.base import Novel


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


def open_part(novel: Novel, chapter, download: bool) -> int:
    """Fetch a part, then view it (and optionally save it to disk)."""
    print("Fetching…")
    try:
        text = novel.provider.content(chapter)
    except NovHttpError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    if download:
        path = save.save_chapter(novel.title, chapter.title, text)
        print(f"Saved: {path}")

    view(text)
    return 0


def resume() -> int:
    """Let the user jump back into a book they were reading."""
    entries = bookmarks.all_entries()
    if not entries:
        print("No bookmarks yet — read something first.")
        return 0

    chosen = pick(
        [(f"{e['title']} — {e.get('part_title', '?')}", e) for e in entries],
        "Resume",
    )
    if not chosen:
        return 0

    provider = PROVIDERS.get(chosen.get("provider", ""))
    if not provider:
        print(f"[error] provider '{chosen.get('provider')}' is no longer available.")
        return 1

    novel = Novel(
        title=chosen["title"],
        url=chosen["url"],
        author=chosen.get("author"),
        provider=provider,
    )
    try:
        chapters = provider.chapters(novel)
    except Exception as exc:
        print(f"[error] could not list parts: {exc}", file=sys.stderr)
        return 1

    idx = chosen.get("part_index", 0)
    if 0 <= idx < len(chapters):
        chapter = chapters[idx]
    else:
        chapter = pick([(c.title, c) for c in chapters], "Part")
        if not chapter:
            return 0
        idx = chapters.index(chapter)

    bookmarks.record(novel, idx, chapter.title)
    return open_part(novel, chapter, download=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nov-cli",
        description="Search and read novels from the web (ani-cli style).",
    )
    parser.add_argument("query", nargs="?", help="search query")
    parser.add_argument("-p", "--provider", help="limit to one provider")
    parser.add_argument(
        "-d", "--download", action="store_true", help="save the chosen part to a .txt"
    )
    parser.add_argument(
        "-r", "--resume", action="store_true", help="resume a bookmarked book"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="skip the offline cache"
    )
    parser.add_argument(
        "-U", "--update", action="store_true", help="self-update via git pull"
    )
    args = parser.parse_args()

    if args.no_cache:
        # Disable the offline cache for this run.
        import core.http

        core.http.CACHING_ENABLED = False

    if args.update:
        self_update()
        return 0

    if args.resume:
        return resume()

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
    idx = chapters.index(chapter)

    bookmarks.record(novel, idx, chapter.title)
    return open_part(novel, chapter, download=args.download)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # last-resort guard: never show a raw traceback
        print(f"[error] something went wrong: {exc}", file=sys.stderr)
        sys.exit(1)

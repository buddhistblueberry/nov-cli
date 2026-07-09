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
import sys

from core.http import fetch
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


def main() -> None:
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
        os.system('git -C "$(dirname "$0")" pull')
        return

    if not args.query:
        parser.print_help()
        return

    print(f"Searching for: {args.query}")
    novels = search_all(args.query, args.provider)
    if not novels:
        print("No results found.")
        return

    novel = pick(
        [(f"{n.title} — {n.author or 'unknown'}", n) for n in novels], "Novel"
    )
    if not novel:
        return

    chapters = novel.provider.chapters(novel)
    chapter = pick([(c.title, c) for c in chapters], "Part")
    if not chapter:
        return

    print("Fetching…")
    view(novel.provider.content(chapter))


if __name__ == "__main__":
    main()

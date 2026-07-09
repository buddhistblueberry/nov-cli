"""Saving chapters to local .txt files.

Used by the `--download` option so a part (or whole book) can be kept on
the device and read later in any text viewer.
"""

import os
import re


BOOKS_DIR = os.path.join(os.path.expanduser("~"), "nov-cli-books")


def safe_name(name: str) -> str:
    """Turn a title into something safe to use as a filename."""
    cleaned = re.sub(r"[^\w\-]+", "_", name)  # bad chars -> single underscore
    cleaned = re.sub(r"_+", "_", cleaned)       # collapse repeats
    return cleaned.strip("_") or "untitled"


def save_chapter(
    novel_title: str, part_title: str, text: str, directory: str = BOOKS_DIR
) -> str:
    """Write `text` to `<directory>/<novel> - <part>.txt` and return the path."""
    os.makedirs(directory, exist_ok=True)
    filename = f"{safe_name(novel_title)} - {safe_name(part_title)}.txt"
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path

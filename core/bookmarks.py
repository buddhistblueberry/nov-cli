"""Reading-position bookmarks.

We remember the last part you read of each book in a small JSON file
(~/.config/nov-cli/bookmarks.json). That powers `nov-cli --resume`, which
lets you jump straight back to where you left off.
"""

import json
import os


BOOKMARKS_FILE = os.path.join(
    os.path.expanduser("~"), ".config", "nov-cli", "bookmarks.json"
)


def _load() -> dict:
    try:
        with open(BOOKMARKS_FILE, encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"entries": {}}


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(BOOKMARKS_FILE), exist_ok=True)
    with open(BOOKMARKS_FILE, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def record(novel, part_index: int, part_title: str) -> None:
    """Save (or overwrite) the reading position for `novel`."""
    data = _load()
    data["entries"][novel.url] = {
        "title": novel.title,
        "author": novel.author,
        "url": novel.url,
        "provider": novel.provider.name if novel.provider else "",
        "part_index": part_index,
        "part_title": part_title,
    }
    _save(data)


def all_entries() -> list:
    """Return every saved bookmark as a list of dicts."""
    return list(_load()["entries"].values())


def get(novel_url: str) -> dict | None:
    return _load()["entries"].get(novel_url)

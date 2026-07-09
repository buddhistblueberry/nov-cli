"""Offline cache for fetched chapter text.

We cache each successfully downloaded URL on disk (in ~/.cache/nov-cli),
keyed by a hash of the URL. Next time the same chapter is requested we
return the saved copy — faster, and it works with no internet.
"""

import hashlib
import os

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "nov-cli")


def _key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def get(url: str) -> str | None:
    """Return cached text for `url`, or None if not cached."""
    path = os.path.join(CACHE_DIR, _key(url))
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    return None


def set(url: str, text: str) -> None:
    """Store `text` under `url` for later offline use."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, _key(url)), "w", encoding="utf-8") as handle:
        handle.write(text)

"""Tests for core/bookmarks.py — saving and reading reading positions."""

import core.bookmarks


class _Provider:
    name = "gutenberg"


class _Novel:
    title = "Alice's Adventures in Wonderland"
    author = "Lewis Carroll"
    url = "https://www.gutenberg.org/ebooks/11"
    provider = _Provider()


def test_record_and_read_back(monkeypatch, tmp_path):
    monkeypatch.setattr(core.bookmarks, "BOOKMARKS_FILE", str(tmp_path / "bm.json"))

    assert core.bookmarks.all_entries() == []  # starts empty

    core.bookmarks.record(_Novel(), part_index=2, part_title="Read — Plain Text")
    entries = core.bookmarks.all_entries()
    assert len(entries) == 1

    entry = entries[0]
    assert entry["title"] == _Novel.title
    assert entry["provider"] == "gutenberg"
    assert entry["part_index"] == 2

    assert core.bookmarks.get(_Novel.url)["part_title"] == "Read — Plain Text"


def test_record_overwrites_same_book(monkeypatch, tmp_path):
    monkeypatch.setattr(core.bookmarks, "BOOKMARKS_FILE", str(tmp_path / "bm.json"))

    core.bookmarks.record(_Novel(), part_index=0, part_title="start")
    core.bookmarks.record(_Novel(), part_index=5, part_title="later")
    # same url -> single entry, updated
    assert len(core.bookmarks.all_entries()) == 1
    assert core.bookmarks.get(_Novel.url)["part_index"] == 5

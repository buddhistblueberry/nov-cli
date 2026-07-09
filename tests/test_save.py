"""Tests for core/save.py — writing chapters to .txt files."""

import core.save


def test_safe_name_sanitises():
    assert core.save.safe_name("Pride & Prejudice!") == "Pride_Prejudice"
    assert core.save.safe_name("  weird: name?  ") == "weird_name"


def test_save_chapter_writes_file(monkeypatch, tmp_path):
    monkeypatch.setattr(core.save, "BOOKS_DIR", str(tmp_path))
    path = core.save.save_chapter("Alice", "Chapter 1", "once upon a time")
    assert path.endswith("Alice - Chapter_1.txt")
    assert open(path, encoding="utf-8").read() == "once upon a time"

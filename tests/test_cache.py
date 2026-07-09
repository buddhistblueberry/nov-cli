"""Tests for core/cache.py — offline caching by URL."""

import core.cache


def test_set_then_get(monkeypatch, tmp_path):
    monkeypatch.setattr(core.cache, "CACHE_DIR", str(tmp_path))
    assert core.cache.get("http://example.com/a") is None

    core.cache.set("http://example.com/a", "chapter text")
    assert core.cache.get("http://example.com/a") == "chapter text"

    # a different URL is a different key
    assert core.cache.get("http://example.com/b") is None


def test_keys_are_stable(monkeypatch, tmp_path):
    monkeypatch.setattr(core.cache, "CACHE_DIR", str(tmp_path))
    core.cache.set("http://example.com/a", "x")
    # calling get twice for the same url returns the same stored value
    assert core.cache.get("http://example.com/a") == "x"

"""Tests for the Internet Archive provider using saved JSON fixtures."""

from pathlib import Path

import pytest

from providers.internetarchive import InternetArchiveProvider

SEARCH = Path(__file__).parent / "fixtures" / "ia_search.json"
META = Path(__file__).parent / "fixtures" / "ia_meta.json"
SAMPLE_TEXT = "Chapter 1\nIt is a truth universally acknowledged."


@pytest.fixture
def provider():
    return InternetArchiveProvider()


def _fake_fetch(url):
    if "advancedsearch" in url:
        return SEARCH.read_text()
    if "/metadata/" in url:
        return META.read_text()
    return SAMPLE_TEXT  # the .txt download


def test_search_parses_docs(monkeypatch, provider):
    monkeypatch.setattr("providers.internetarchive.fetch", _fake_fetch)

    novels = provider.search("pride")
    titles = {n.title for n in novels}
    assert "Pride and Prejudice" in titles
    assert "A Pride of Lions" in titles

    by_title = {n.title: n for n in novels}
    # creator may be a list or a string; either way it becomes a label
    assert by_title["Pride and Prejudice"].author == "Jane Austen"
    assert by_title["Pride and Prejudice"].url.endswith(
        "/details/prideandprejudice00aust"
    )


def test_chapters_finds_txt_file(monkeypatch, provider):
    monkeypatch.setattr("providers.internetarchive.fetch", _fake_fetch)
    novel = provider.search("pride")[1]  # Pride and Prejudice

    chapters = provider.chapters(novel)
    assert len(chapters) == 1
    assert chapters[0].title.startswith("Read — Plain Text")
    assert chapters[0].url == (
        "https://archive.org/download/prideandprejudice00aust/"
        "prideandprejudice00aust_djvu.txt"
    )


def test_content_returns_text(monkeypatch, provider):
    monkeypatch.setattr("providers.internetarchive.fetch", _fake_fetch)
    chapter = provider.chapters(provider.search("pride")[1])[0]

    assert provider.content(chapter) == SAMPLE_TEXT


def test_chapters_empty_when_no_txt(monkeypatch):
    import json

    meta_no_txt = json.dumps({"files": [{"name": "x.jpg", "format": "Image"}]})
    calls = {"n": 0}

    def fake_fetch(url):
        if "advancedsearch" in url:
            return SEARCH.read_text()
        if "/metadata/" in url:
            return meta_no_txt
        return "unused"

    monkeypatch.setattr("providers.internetarchive.fetch", fake_fetch)
    provider = InternetArchiveProvider()
    novel = provider.search("pride")[0]
    assert provider.chapters(novel) == []

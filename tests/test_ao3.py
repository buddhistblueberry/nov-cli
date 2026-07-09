"""Tests for the AO3 provider using saved HTML fixtures."""

from pathlib import Path

import pytest

from providers.ao3 import AO3Provider

SEARCH = Path(__file__).parent / "fixtures" / "ao3_search.html"
WORK = Path(__file__).parent / "fixtures" / "ao3_work.html"


@pytest.fixture
def provider():
    return AO3Provider()


def _fake_fetch(url):
    if "works/search" in url:
        return SEARCH.read_text()
    return WORK.read_text()


def test_search_parses_works(monkeypatch, provider):
    monkeypatch.setattr("providers.ao3.fetch", _fake_fetch)

    novels = provider.search("magic")
    titles = {n.title for n in novels}
    assert "A Magical Tale" in titles
    assert "Another Story" in titles

    by_title = {n.title: n for n in novels}
    assert by_title["A Magical Tale"].author == "Author"
    assert by_title["A Magical Tale"].url.endswith("/works/36367384")


def test_chapters_single_part_for_one_chapter_work(monkeypatch, provider):
    monkeypatch.setattr("providers.ao3.fetch", _fake_fetch)
    novel = provider.search("magic")[0]

    chapters = provider.chapters(novel)
    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"
    assert chapters[0].url == novel.url


def test_content_extracts_userstuff(monkeypatch, provider):
    monkeypatch.setattr("providers.ao3.fetch", _fake_fetch)
    chapter = provider.chapters(provider.search("magic")[0])[0]

    text = provider.content(chapter)
    assert "Tenko didn't want to believe she was doing this" in text
    assert "Himiko walked beside her" in text

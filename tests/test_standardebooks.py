"""Tests for the Standard Ebooks provider using saved HTML fixtures."""

from pathlib import Path

import pytest

from providers.standardebooks import StandardEbooksProvider

SEARCH = Path(__file__).parent / "fixtures" / "standardebooks_search.html"
TEXT = Path(__file__).parent / "fixtures" / "standardebooks_text.html"


@pytest.fixture
def provider():
    return StandardEbooksProvider()


def test_search_parses_titles_authors_and_urls(monkeypatch, provider):
    monkeypatch.setattr("providers.standardebooks.fetch", lambda url: SEARCH.read_text())

    novels = provider.search("pride")
    titles = {n.title for n in novels}
    assert "Pride and Prejudice" in titles
    assert "The Adventures of Sherlock Holmes" in titles

    by_title = {n.title: n for n in novels}
    assert by_title["Pride and Prejudice"].author == "Jane Austen"
    assert by_title["Pride and Prejudice"].url.endswith(
        "/ebooks/jane-austen/pride-and-prejudice"
    )


def test_chapters_returns_single_text_part(monkeypatch, provider):
    monkeypatch.setattr("providers.standardebooks.fetch", lambda url: SEARCH.read_text())
    novel = provider.search("pride")[0]

    chapters = provider.chapters(novel)
    assert len(chapters) == 1
    assert chapters[0].title == "Read — Plain Text"
    assert chapters[0].url.endswith("/text/single-page")


def test_content_extracts_text_from_main(monkeypatch, provider):
    def fake_fetch(url):
        if "/text/single-page" in url:
            return TEXT.read_text()
        return SEARCH.read_text()

    monkeypatch.setattr("providers.standardebooks.fetch", fake_fetch)
    chapter = provider.chapters(provider.search("pride")[0])[0]

    text = provider.content(chapter)
    assert "truth universally acknowledged" in text
    assert "Mr. Bennet was so odd a mixture" in text

"""Tests for the Gutenberg provider using a saved HTML fixture.

No real network: we replace core.http.fetch with a function that returns
the fixture file, so the parsing logic is tested in isolation.
"""

from pathlib import Path

import pytest

from providers.gutenberg import GutenbergProvider

FIXTURE = Path(__file__).parent / "fixtures" / "gutenberg_search.html"


@pytest.fixture
def provider():
    return GutenbergProvider()


def test_search_parses_titles_and_authors(monkeypatch, provider):
    html = FIXTURE.read_text()
    monkeypatch.setattr("providers.gutenberg.fetch", lambda url: html)

    novels = provider.search("pride")
    titles = {n.title for n in novels}
    assert "Pride and Prejudice" in titles
    assert "Alice's Adventures in Wonderland" in titles

    by_author = {n.title: n.author for n in novels}
    assert by_author["Pride and Prejudice"] == "Jane Austen"
    # strip the leading "by " Gutenberg adds
    assert not any(a and a.startswith("by ") for a in by_author.values())


def test_search_skips_non_ebook_links(monkeypatch, provider):
    html = FIXTURE.read_text()
    monkeypatch.setattr("providers.gutenberg.fetch", lambda url: html)

    novels = provider.search("anything")
    # the fixture's "/catalog/not-a-book" link must be ignored
    assert all(n.url.startswith("https://www.gutenberg.org/ebooks/") for n in novels)


def test_chapters_returns_readable_formats(monkeypatch, provider):
    html = FIXTURE.read_text()
    monkeypatch.setattr("providers.gutenberg.fetch", lambda url: html)

    novel = provider.search("alice")[0]
    chapters = provider.chapters(novel)
    labels = {c.title for c in chapters}
    assert "Read — Plain Text (UTF-8)" in labels
    # chapter URLs point at the book's file directory
    assert all(f"/files/{novel.url.rsplit('/', 1)[1]}/" in c.url for c in chapters)


def test_content_trims_gutenberg_boilerplate(monkeypatch, provider):
    body = "THE STORY STARTS HERE\n*END THE SMALL PRINT! redistribution junk"

    def fake_fetch(url):
        # search() also calls fetch; give it the real fixture so we get novels
        if "search" in url:
            return FIXTURE.read_text()
        return body

    monkeypatch.setattr("providers.gutenberg.fetch", fake_fetch)

    chapter = provider.chapters(provider.search("alice")[0])[0]
    text = provider.content(chapter)
    assert text.startswith("THE STORY STARTS HERE")
    assert "redistribution junk" not in text

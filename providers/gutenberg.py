"""Gutenberg provider — Project Gutenberg (public-domain books).

This is the example provider shipped with nov-cli. Gutenberg is free,
stable, and public domain, which makes it a safe place to learn the
provider pattern. See README.md for how to add your own site.
"""

from urllib.parse import quote

from core.http import fetch
from .base import Novel, Chapter, Provider
from . import register
from bs4 import BeautifulSoup


class GutenbergProvider(Provider):
    name = "gutenberg"

    def search(self, query: str) -> list[Novel]:
        url = "https://www.gutenberg.org/ebooks/search/?query=" + quote(query)
        soup = BeautifulSoup(fetch(url), "html.parser")

        novels: list[Novel] = []
        for item in soup.select("li.booklink"):
            link = item.find("a")
            if not link:
                continue
            href = link.get("href", "")
            if not href.startswith("/ebooks/"):
                continue
            book_id = href.rstrip("/").split("/")[-1]

            title_tag = item.select_one(".title")
            title = (
                title_tag.get_text(strip=True)
                if title_tag
                else link.get_text(strip=True)
            )
            author_tag = item.select_one(".authors")
            author = (
                author_tag.get_text(strip=True).removeprefix("by ")
                if author_tag
                else None
            )

            novels.append(
                Novel(
                    title=title,
                    url="https://www.gutenberg.org" + href,
                    author=author,
                    provider=self,
                )
            )
        return novels

    def chapters(self, novel: Novel) -> list[Chapter]:
        # Gutenberg books are whole texts; we offer the main readable
        # formats as selectable "parts". Plain Text (UTF-8) is the default.
        book_id = novel.url.rstrip("/").split("/")[-1]
        base = f"https://www.gutenberg.org/files/{book_id}/"
        return [
            Chapter("Read — Plain Text (UTF-8)", f"{base}{book_id}-0.txt"),
            Chapter("Read — HTML", f"{base}{book_id}-h.htm"),
        ]

    def content(self, chapter: Chapter) -> str:
        text = fetch(chapter.url)
        if chapter.url.endswith(".txt"):
            # Trim Gutenberg's trailing license/redistribution boilerplate.
            marker = "*END THE SMALL PRINT!"
            if marker in text:
                text = text[: text.index(marker)]
        return text.strip()


register(GutenbergProvider())

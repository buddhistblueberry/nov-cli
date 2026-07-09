"""AO3 provider — https://archiveofourown.org (Archive of Our Own)

Fanfiction community. NOTE: AO3's Terms of Service ask that you not
mass-scrape the site; nov-cli only fetches on your direct request (one
work at a time) and respects each work's public availability. Use it for
personal reading only.

AO3 shows each work's text inside `#chapters > div.userstuff`. Multi-chapter
works link each chapter from an `<ol class="chapter">` index.
"""

from urllib.parse import urlencode

from core.http import fetch
from .base import Novel, Chapter, Provider
from . import register
from bs4 import BeautifulSoup

BASE = "https://archiveofourown.org"


class AO3Provider(Provider):
    name = "ao3"

    def search(self, query: str) -> list[Novel]:
        url = BASE + "/works/search?" + urlencode({"work_search[query]": query})
        soup = BeautifulSoup(fetch(url), "html.parser")

        novels: list[Novel] = []
        for blurb in soup.select("li.work.blurb"):
            heading = blurb.select_one("h4.heading a")
            if not heading:
                continue
            href = heading.get("href", "")
            title = heading.get_text(strip=True)
            author_a = blurb.select_one('h4.heading a[rel="author"]')
            author = author_a.get_text(strip=True) if author_a else None

            novels.append(
                Novel(title=title, url=BASE + href, author=author, provider=self)
            )
        return novels

    def chapters(self, novel: Novel) -> list[Chapter]:
        soup = BeautifulSoup(fetch(novel.url), "html.parser")

        index = soup.select_one("ol.chapter")
        if index:
            found = []
            for link in index.select('a[href*="/chapters/"]'):
                href = link.get("href", "")
                if href:
                    found.append(
                        Chapter(link.get_text(strip=True), BASE + href)
                    )
            if found:
                return found

        # Single-chapter work: the work page itself holds the text.
        return [Chapter("Chapter 1", novel.url)]

    def content(self, chapter: Chapter) -> str:
        soup = BeautifulSoup(fetch(chapter.url), "html.parser")
        container = soup.select_one("#chapters") or soup
        userstuff = container.select_one("div.userstuff")
        if userstuff:
            return userstuff.get_text("\n", strip=True)
        return soup.get_text("\n", strip=True)


register(AO3Provider())

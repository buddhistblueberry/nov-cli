"""Standard Ebooks provider — https://standardebooks.org

Free, public-domain ebooks with clean and stable HTML. Each book is offered
as one plain-text "part" (its `/text/single-page` reading view). This is a
good second provider after Gutenberg: no login, no JS, predictable markup.
"""

from urllib.parse import quote

from core.http import fetch
from .base import Novel, Chapter, Provider
from . import register
from bs4 import BeautifulSoup

BASE = "https://standardebooks.org"


class StandardEbooksProvider(Provider):
    name = "standardebooks"

    def search(self, query: str) -> list[Novel]:
        url = f"{BASE}/ebooks?query=" + quote(query)
        soup = BeautifulSoup(fetch(url), "html.parser")

        novels: list[Novel] = []
        for item in soup.select('ol.ebooks-list.grid li[typeof="schema:Book"]'):
            link = item.select_one('p a[property="schema:url"]')
            if not link:
                continue
            href = link.get("href", "")
            title_span = link.select_one('span[property="schema:name"]')
            title = (
                title_span.get_text(strip=True)
                if title_span
                else link.get_text(strip=True)
            )
            author_span = item.select_one('p.author span[property="schema:name"]')
            author = (
                author_span.get_text(strip=True) if author_span else None
            )

            novels.append(
                Novel(
                    title=title,
                    url=BASE + href,
                    author=author,
                    provider=self,
                )
            )
        return novels

    def chapters(self, novel: Novel) -> list[Chapter]:
        # Standard Ebooks exposes the whole book as one plain-text page.
        text_url = novel.url.rstrip("/") + "/text/single-page"
        return [Chapter("Read — Plain Text", text_url)]

    def content(self, chapter: Chapter) -> str:
        soup = BeautifulSoup(fetch(chapter.url), "html.parser")
        main = soup.select_one("main")
        if main:
            return main.get_text("\n", strip=True)
        return soup.get_text("\n", strip=True)


register(StandardEbooksProvider())

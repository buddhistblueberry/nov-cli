"""Internet Archive provider — https://archive.org

The Internet Archive is a huge library of free books and texts. It has a
clean JSON search API (advancedsearch) and per-item metadata that points at
the plain-text OCR file we read. No HTML scraping needed.
"""

from urllib.parse import urlencode

from core.http import fetch
from .base import Novel, Chapter, Provider
from . import register
import json


SEARCH_URL = "https://archive.org/advancedsearch.php"


class InternetArchiveProvider(Provider):
    name = "internetarchive"

    def search(self, query: str) -> list[Novel]:
        params = {
            "q": f"({query}) AND mediatype:texts",
            "fl[]": ["identifier", "title", "creator"],
            "rows": "20",
            "output": "json",
        }
        url = SEARCH_URL + "?" + urlencode(params, doseq=True)
        data = json.loads(fetch(url))

        novels: list[Novel] = []
        for doc in data.get("response", {}).get("docs", []):
            ident = doc.get("identifier")
            if not ident:
                continue
            creator = doc.get("creator")
            if isinstance(creator, list):
                creator = ", ".join(creator) if creator else None
            novels.append(
                Novel(
                    title=doc.get("title") or ident,
                    url=f"https://archive.org/details/{ident}",
                    author=creator,
                    provider=self,
                )
            )
        return novels

    def chapters(self, novel: Novel) -> list[Chapter]:
        ident = novel.url.rstrip("/").split("/")[-1]
        meta = json.loads(fetch(f"https://archive.org/metadata/{ident}"))

        txt_name = None
        for f in meta.get("files", []):
            name = f.get("name", "")
            if name.endswith(".txt"):
                txt_name = name
                break
        if not txt_name:
            return []

        url = f"https://archive.org/download/{ident}/{txt_name}"
        return [Chapter("Read — Plain Text (OCR)", url)]

    def content(self, chapter: Chapter) -> str:
        # chapter.url is the direct .txt download link
        return fetch(chapter.url).strip()


register(InternetArchiveProvider())

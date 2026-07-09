"""Provider interface shared by every scraping site.

A "provider" knows how to search a site, list a novel's readable parts
(we call them chapters), and fetch the text of one part. Adding support
for a new site means writing one new class that follows this shape and
registering it in providers/__init__.py.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chapter:
    title: str
    url: str


@dataclass
class Novel:
    title: str
    url: str
    author: Optional[str] = None
    provider: Optional["Provider"] = None


class Provider:
    # Subclasses set this to a short unique name, e.g. "gutenberg".
    name: str = ""

    def search(self, query: str) -> List[Novel]:
        raise NotImplementedError

    def chapters(self, novel: Novel) -> List[Chapter]:
        raise NotImplementedError

    def content(self, chapter: Chapter) -> str:
        raise NotImplementedError

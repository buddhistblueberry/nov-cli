"""HTTP helpers for nov-cli.

Every request sends a browser-like User-Agent so sites don't block us,
and raises on HTTP errors so callers can decide what to do.
"""

import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def fetch(url: str, timeout: int = 20) -> str:
    """Download a URL and return its text content.

    Raises requests.HTTPError if the server returns an error status.
    """
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text

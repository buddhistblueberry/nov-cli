"""HTTP helpers for nov-cli.

Every request sends a browser-like User-Agent so sites don't block us.
`fetch` retries a few times on flaky network/5xx errors, then raises a
clean `NovHttpError` so the rest of the app can show a friendly message
instead of a raw Python traceback.
"""

import time

import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


class NovHttpError(Exception):
    """Raised when a URL can't be fetched after retrying.

    Wraps whatever went wrong (no network, timeout, HTTP error status)
    so callers can catch one predictable exception.
    """


def fetch(
    url: str,
    timeout: int = 20,
    retries: int = 3,
    backoff: float = 0.5,
) -> str:
    """Download a URL and return its text content.

    Retries `retries` times on connection errors or 5xx server errors,
    waiting `backoff` seconds (doubling each attempt) between tries.
    Raises NovHttpError if every attempt fails.
    """
    last_exc: Exception | None = None
    delay = backoff
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url, headers=DEFAULT_HEADERS, timeout=timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(delay)
                delay *= 2  # exponential backoff: 0.5s, 1s, 2s…

    # Every attempt failed — surface one clean error.
    if isinstance(last_exc, requests.HTTPError):
        raise NovHttpError(f"HTTP error for {url}: {last_exc}") from last_exc
    raise NovHttpError(f"could not fetch {url}: {last_exc}") from last_exc

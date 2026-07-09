"""Provider registry.

`PROVIDERS` maps a provider name to its instance. Importing this package
also imports every built-in provider so they self-register.
"""

from .base import Provider, Novel, Chapter

PROVIDERS: dict[str, Provider] = {}


def register(provider: Provider) -> None:
    PROVIDERS[provider.name] = provider


# Built-in providers (each registers itself on import).
from . import gutenberg  # noqa: E402,F401

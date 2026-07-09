"""Tests for core/http.py — retries and clean error reporting."""

import pytest
import requests

from core.http import NovHttpError, fetch


class FakeResponse:
    def __init__(self, text="ok", status=200):
        self.text = text
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code}")


def test_fetch_returns_text_on_success(monkeypatch):
    def ok(*args, **kwargs):
        return FakeResponse("hello")

    monkeypatch.setattr("core.http.requests.get", ok)
    assert fetch("http://example.com") == "hello"


def test_fetch_retries_then_succeeds(monkeypatch):
    calls = {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            raise requests.ConnectionError("network down")
        return FakeResponse("recovered")

    monkeypatch.setattr("core.http.requests.get", flaky)
    monkeypatch.setattr("core.http.time.sleep", lambda *_: None)  # no real wait
    assert fetch("http://example.com", retries=3) == "recovered"
    assert calls["n"] == 3


def test_fetch_raises_novhttp_on_persistent_failure(monkeypatch):
    def always_fail(*args, **kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr("core.http.requests.get", always_fail)
    monkeypatch.setattr("core.http.time.sleep", lambda *_: None)
    with pytest.raises(NovHttpError):
        fetch("http://example.com", retries=2)


def test_fetch_wraps_http_error(monkeypatch):
    def server_error(*args, **kwargs):
        return FakeResponse(status=500)

    monkeypatch.setattr("core.http.requests.get", server_error)
    with pytest.raises(NovHttpError):
        fetch("http://example.com", retries=1)

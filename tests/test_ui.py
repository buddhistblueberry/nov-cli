"""Tests for core/ui.py — both the fzf path and the numbered-menu fallback.

We never launch a real pager or fzf; we stub subprocess.run and input.
"""

import builtins
from unittest.mock import MagicMock

import pytest

import core.ui
from core.ui import pick


def test_pick_returns_none_for_empty_list():
    assert pick([]) is None


def test_pick_uses_fzf_when_available(monkeypatch):
    options = [("One", 1), ("Two", 2), ("Three", 3)]

    fake = MagicMock()
    fake.returncode = 0
    fake.stdout = "Two\n"  # user selected the 2nd label

    monkeypatch.setattr(core.ui.subprocess, "run", lambda *a, **k: fake)
    assert pick(options) == 2


def test_pick_falls_back_to_numbered_menu(monkeypatch):
    options = [("One", 1), ("Two", 2), ("Three", 3)]

    monkeypatch.setattr(
        core.ui.subprocess, "run", MagicMock(side_effect=FileNotFoundError)
    )
    monkeypatch.setattr(builtins, "input", lambda *a, **k: "3")  # 3rd item
    assert pick(options) == 3


def test_pick_numbered_menu_rejects_bad_input(monkeypatch):
    options = [("One", 1), ("Two", 2)]

    monkeypatch.setattr(
        core.ui.subprocess, "run", MagicMock(side_effect=FileNotFoundError)
    )
    responses = iter(["abc", "1"])  # first invalid, then valid
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(responses))
    assert pick(options) == 1

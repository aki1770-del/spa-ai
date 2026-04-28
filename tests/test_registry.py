"""Tests for LoomRegistry."""
from __future__ import annotations

from pathlib import Path

import pytest

from spa_ai.looms.base import LoomFinding, LoomPatch
from spa_ai.registry import LoomRegistry, default_registry


class _FakeLoom:
    """Loom-shaped test double."""

    def __init__(self, loom_id: str, vision_id: int) -> None:
        self.loom_id = loom_id
        self.sakichi_vision_id = vision_id

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        return []

    def propose_patch(self, finding: LoomFinding) -> LoomPatch:
        raise NotImplementedError


def test_default_registry_has_pre_commit_formatter() -> None:
    reg = default_registry()
    assert "pre-commit-formatter" in reg


def test_default_registry_has_pre_commit_formatter_rust() -> None:
    reg = default_registry()
    assert "pre-commit-formatter-rust" in reg


def test_default_registry_size_is_six() -> None:
    """v0.5.x ships with six looms (pre-commit-formatter,
    pre-commit-formatter-rust, contributing-md, silent-failure-grepper,
    eof-newline, literature-drift-detector). Guard prevents silent
    additions without an accompanying test + CHANGELOG entry."""
    reg = default_registry()
    assert len(reg) == 6


def test_default_registry_has_contributing_md() -> None:
    reg = default_registry()
    assert "contributing-md" in reg


def test_default_registry_has_silent_failure_grepper() -> None:
    reg = default_registry()
    assert "silent-failure-grepper" in reg


def test_default_registry_has_eof_newline() -> None:
    reg = default_registry()
    assert "eof-newline" in reg


def test_default_registry_has_literature_drift_detector() -> None:
    reg = default_registry()
    assert "literature-drift-detector" in reg


def test_register_rejects_duplicate_id() -> None:
    reg = LoomRegistry()
    reg.register(_FakeLoom("foo", 1))
    with pytest.raises(ValueError, match="already registered"):
        reg.register(_FakeLoom("foo", 1))


def test_register_rejects_invalid_vision_id() -> None:
    reg = LoomRegistry()
    with pytest.raises(ValueError, match="sakichi_vision_id"):
        reg.register(_FakeLoom("zero", 0))
    with pytest.raises(ValueError, match="sakichi_vision_id"):
        reg.register(_FakeLoom("over", 101))


def test_register_accepts_valid_vision_id_range() -> None:
    reg = LoomRegistry()
    reg.register(_FakeLoom("a", 1))
    reg.register(_FakeLoom("b", 100))
    assert len(reg) == 2


def test_get_returns_registered_loom() -> None:
    reg = LoomRegistry()
    loom = _FakeLoom("alpha", 42)
    reg.register(loom)
    assert reg.get("alpha") is loom


def test_get_raises_keyerror_for_unknown() -> None:
    reg = LoomRegistry()
    with pytest.raises(KeyError):
        reg.get("nonexistent")


def test_all_returns_in_registration_order() -> None:
    reg = LoomRegistry()
    a = _FakeLoom("a", 1)
    b = _FakeLoom("b", 2)
    c = _FakeLoom("c", 3)
    reg.register(a)
    reg.register(b)
    reg.register(c)
    assert reg.all() == [a, b, c]

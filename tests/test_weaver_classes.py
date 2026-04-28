"""Tests for the weaver-class registry + alias normalization.

Per LoomDignityFrame design: open string-set with documented canonical
v1 set + alias map. The framework cannot answer "which weaver-classes
are absent from the loom roster?" without this slot — these tests guard
the substrate the doctor surface depends on.
"""
from __future__ import annotations

from spa_ai.looms.weaver_classes import (
    ALIASES,
    KNOWN_WEAVER_CLASSES,
    is_known_weaver_class,
    normalize_weaver_class,
)


def test_canonical_set_contains_v1_seven_classes() -> None:
    """v1 canonical set is the agreed seven classes; guard against silent edits."""
    assert set(KNOWN_WEAVER_CLASSES) == {
        "maintainer",
        "first-contributor",
        "adopter",
        "driver",
        "auditor",
        "sub-agent",
        "integrator",
    }
    # Ordering preserved as a tuple for deterministic snapshot tests.
    assert isinstance(KNOWN_WEAVER_CLASSES, tuple)
    assert len(KNOWN_WEAVER_CLASSES) == 7


def test_normalize_passes_through_canonical_classes() -> None:
    for cls in KNOWN_WEAVER_CLASSES:
        assert normalize_weaver_class(cls) == cls


def test_normalize_is_case_insensitive_for_canonical() -> None:
    assert normalize_weaver_class("Maintainer") == "maintainer"
    assert normalize_weaver_class("DRIVER") == "driver"
    assert normalize_weaver_class("Sub-Agent") == "sub-agent"


def test_normalize_resolves_known_aliases() -> None:
    assert normalize_weaver_class("contributor") == "first-contributor"
    assert normalize_weaver_class("first_contributor") == "first-contributor"
    assert normalize_weaver_class("user") == "driver"
    assert normalize_weaver_class("subagent") == "sub-agent"
    assert normalize_weaver_class("agent") == "sub-agent"
    assert normalize_weaver_class("downstream") == "integrator"


def test_normalize_aliases_case_insensitive() -> None:
    assert normalize_weaver_class("Contributor") == "first-contributor"
    assert normalize_weaver_class("END-USER") == "driver"


def test_normalize_passes_through_unknown_strings() -> None:
    """Open string-set discipline: unknown strings pass through verbatim
    so the doctor surface can flag them as advisory, not break registration."""
    assert normalize_weaver_class("future-cohort") == "future-cohort"
    assert normalize_weaver_class("ml-engineer") == "ml-engineer"


def test_normalize_strips_whitespace() -> None:
    assert normalize_weaver_class("  maintainer  ") == "maintainer"


def test_normalize_empty_returns_empty() -> None:
    assert normalize_weaver_class("") == ""
    assert normalize_weaver_class("   ") == ""


def test_normalize_non_string_returns_empty() -> None:
    """Loom authors might mistakenly pass non-strings; never raise here."""
    assert normalize_weaver_class(None) == ""  # type: ignore[arg-type]
    assert normalize_weaver_class(42) == ""  # type: ignore[arg-type]


def test_is_known_weaver_class_recognises_canonical() -> None:
    for cls in KNOWN_WEAVER_CLASSES:
        assert is_known_weaver_class(cls)


def test_is_known_weaver_class_resolves_aliases_first() -> None:
    assert is_known_weaver_class("contributor")
    assert is_known_weaver_class("user")


def test_is_known_weaver_class_rejects_unknown() -> None:
    assert not is_known_weaver_class("future-cohort")
    assert not is_known_weaver_class("")


def test_aliases_target_canonical_set() -> None:
    """Every alias target must be a canonical class — no dangling aliases."""
    for alias, target in ALIASES.items():
        assert target in KNOWN_WEAVER_CLASSES, (
            f"alias {alias!r} -> {target!r} is not in the canonical set"
        )

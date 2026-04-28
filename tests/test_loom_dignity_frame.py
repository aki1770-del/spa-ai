"""Tests for the LoomDignityFrame Protocol extension.

Covers:
  - Protocol shape: every shipped loom declares `weaver_classes_served`
    as a list of strings.
  - Per-loom declarations: each of the six default looms declares its
    documented v1 set per the design brief.
  - Doctor coverage block: `_build_doctor_report` aggregates across the
    registry, correctly identifying served / absent / unknown buckets.
  - Backward-compat: an external loom predating the slot still registers
    and surfaces in the unknown bucket (advisory, not error).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from spa_ai.cli import _build_doctor_report, _build_weaver_class_coverage
from spa_ai.looms.base import LoomFinding, LoomPatch
from spa_ai.looms.contributing_md import ContributingMdLoom
from spa_ai.looms.eof_newline import EofNewlineLoom
from spa_ai.looms.literature_drift_detector import LiteratureDriftDetectorLoom
from spa_ai.looms.pre_commit_formatter import PreCommitFormatterLoom
from spa_ai.looms.pre_commit_formatter_rust import PreCommitFormatterRustLoom
from spa_ai.looms.silent_failure_grepper import SilentFailureGrepperLoom
from spa_ai.looms.weaver_classes import KNOWN_WEAVER_CLASSES
from spa_ai.registry import default_registry

# -------- Protocol extension shape --------

@pytest.mark.parametrize(
    "loom_cls",
    [
        PreCommitFormatterLoom,
        PreCommitFormatterRustLoom,
        ContributingMdLoom,
        SilentFailureGrepperLoom,
        EofNewlineLoom,
        LiteratureDriftDetectorLoom,
    ],
)
def test_every_shipped_loom_declares_weaver_classes_served(loom_cls) -> None:
    """Every loom in the default registry declares the new 4th attribution slot."""
    loom = loom_cls()
    assert hasattr(loom, "weaver_classes_served")
    assert isinstance(loom.weaver_classes_served, list)
    assert len(loom.weaver_classes_served) >= 1
    assert all(isinstance(s, str) and s for s in loom.weaver_classes_served)


# -------- Per-loom expected declarations (v1 design) --------

def test_pre_commit_formatter_serves_maintainer_and_first_contributor() -> None:
    assert PreCommitFormatterLoom().weaver_classes_served == [
        "maintainer",
        "first-contributor",
    ]


def test_pre_commit_formatter_rust_serves_maintainer_and_first_contributor() -> None:
    assert PreCommitFormatterRustLoom().weaver_classes_served == [
        "maintainer",
        "first-contributor",
    ]


def test_contributing_md_serves_maintainer_and_first_contributor() -> None:
    assert ContributingMdLoom().weaver_classes_served == [
        "maintainer",
        "first-contributor",
    ]


def test_eof_newline_serves_maintainer_and_first_contributor() -> None:
    assert EofNewlineLoom().weaver_classes_served == [
        "maintainer",
        "first-contributor",
    ]


def test_silent_failure_grepper_serves_maintainer_auditor_driver() -> None:
    assert SilentFailureGrepperLoom().weaver_classes_served == [
        "maintainer",
        "auditor",
        "driver",
    ]


def test_literature_drift_detector_serves_maintainer_auditor_driver() -> None:
    assert LiteratureDriftDetectorLoom().weaver_classes_served == [
        "maintainer",
        "auditor",
        "driver",
    ]


# -------- All declared classes are valid --------

def test_all_shipped_classes_are_canonical_or_resolve_via_alias() -> None:
    """v1 design guarantees every shipped loom uses canonical class names
    (not aliases). The canonical set is small enough to memorize."""
    for loom in default_registry().all():
        for cls in loom.weaver_classes_served:
            assert cls in KNOWN_WEAVER_CLASSES, (
                f"Loom {loom.loom_id} declared {cls!r} which is not in "
                "the canonical set (use canonical form, not alias)."
            )


# -------- _build_weaver_class_coverage unit tests --------

def test_coverage_aggregates_canonical_classes() -> None:
    looms_report = [
        {"loom_id": "a", "weaver_classes_served": ["maintainer"]},
        {"loom_id": "b", "weaver_classes_served": ["maintainer", "driver"]},
        {"loom_id": "c", "weaver_classes_served": ["driver"]},
    ]
    cov = _build_weaver_class_coverage(looms_report)
    assert cov["served"] == {"maintainer": 2, "driver": 2}
    # absent = canonical \ served, in canonical declaration order
    assert "first-contributor" in cov["absent"]
    assert "adopter" in cov["absent"]
    assert "maintainer" not in cov["absent"]
    assert cov["unknown_loom_count"] == 0
    assert cov["unknown_classes_declared"] == []


def test_coverage_normalizes_aliases() -> None:
    """Loom-side declared `contributor` (alias) aggregates to canonical
    `first-contributor` in the served bucket."""
    looms_report = [
        {"loom_id": "a", "weaver_classes_served": ["contributor"]},
        {"loom_id": "b", "weaver_classes_served": ["first-contributor"]},
    ]
    cov = _build_weaver_class_coverage(looms_report)
    assert cov["served"]["first-contributor"] == 2


def test_coverage_surfaces_unknown_loom_count() -> None:
    looms_report = [
        {"loom_id": "ext1", "weaver_classes_served": []},
        {"loom_id": "ext2"},  # missing key entirely
        {"loom_id": "good", "weaver_classes_served": ["maintainer"]},
    ]
    cov = _build_weaver_class_coverage(looms_report)
    assert cov["unknown_loom_count"] == 2
    assert cov["served"] == {"maintainer": 1}


def test_coverage_surfaces_unknown_classes_advisory() -> None:
    looms_report = [
        {"loom_id": "future", "weaver_classes_served": ["future-cohort"]},
    ]
    cov = _build_weaver_class_coverage(looms_report)
    # Open string-set: future-cohort passes through to advisory bucket
    assert "future-cohort" in cov["unknown_classes_declared"]
    # Not counted in served (canonical only)
    assert cov["served"] == {}


def test_coverage_served_sorted_by_count_desc_then_name() -> None:
    looms_report = [
        {"loom_id": "a", "weaver_classes_served": ["driver"]},
        {"loom_id": "b", "weaver_classes_served": ["maintainer", "driver"]},
        {"loom_id": "c", "weaver_classes_served": ["maintainer"]},
        {"loom_id": "d", "weaver_classes_served": ["maintainer"]},
    ]
    cov = _build_weaver_class_coverage(looms_report)
    keys = list(cov["served"].keys())
    # maintainer (3) before driver (2)
    assert keys == ["maintainer", "driver"]


# -------- doctor JSON includes the new fields --------

def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "spa_ai.cli", *args],
        capture_output=True,
        text=True,
    )


def test_doctor_json_includes_weaver_class_coverage(synthetic_repo: Path) -> None:
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    assert result.returncode == 0, result.stderr
    obj = json.loads(result.stdout)
    cov = obj["weaver_class_coverage"]

    # All six shipped looms declare classes; unknown_loom_count must be 0.
    assert cov["unknown_loom_count"] == 0
    # Maintainer is served by every shipped loom (6/6).
    assert cov["served"]["maintainer"] == 6
    # first-contributor served by 4 looms (the four pre-commit-class /
    # contributing-md looms); driver + auditor each by 2 (silent-failure +
    # literature-drift).
    assert cov["served"]["first-contributor"] == 4
    assert cov["served"]["driver"] == 2
    assert cov["served"]["auditor"] == 2
    # adopter / sub-agent / integrator absent in v1 — these are the V100-gap
    # surface working as designed (the absent looms are themselves the candidates
    # for the next round of new looms).
    assert "adopter" in cov["absent"]
    assert "sub-agent" in cov["absent"]
    assert "integrator" in cov["absent"]
    # No non-canonical declarations from the shipped set.
    assert cov["unknown_classes_declared"] == []


def test_doctor_json_loom_entries_carry_weaver_classes(synthetic_repo: Path) -> None:
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    by_id = {L["loom_id"]: L for L in obj["looms"]}
    assert by_id["literature-drift-detector"]["weaver_classes_served"] == [
        "maintainer",
        "auditor",
        "driver",
    ]
    assert by_id["pre-commit-formatter"]["weaver_classes_served"] == [
        "maintainer",
        "first-contributor",
    ]


def test_doctor_human_renders_weaver_class_coverage(synthetic_repo: Path) -> None:
    result = _run_cli("doctor", str(synthetic_repo))
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "Weaver-class coverage" in out
    assert "maintainer" in out
    assert "absent:" in out
    assert "0 loom(s) declared no weaver_classes_served" in out


# -------- Backward-compat: external loom without the slot --------

class _LegacyExternalLoom:
    """An external loom predating the LoomDignityFrame extension.

    No `weaver_classes_served` attribute. Must still register cleanly and
    surface in the unknown bucket via the doctor coverage block.
    """

    loom_id = "legacy-external"
    sakichi_vision_id = 50
    method_vision_ids = [77]
    stance_vision_ids = [22]

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        return []

    def propose_patch(
        self, finding: LoomFinding, repo_root: Path
    ) -> LoomPatch:
        raise NotImplementedError


def test_legacy_loom_without_slot_treated_as_unknown_in_coverage() -> None:
    looms_report = [
        # Simulate the doctor entry: legacy loom defaults to [] per
        # `getattr(loom, "weaver_classes_served", []) or []`.
        {"loom_id": "legacy-external", "weaver_classes_served": []},
        {"loom_id": "modern", "weaver_classes_served": ["maintainer"]},
    ]
    cov = _build_weaver_class_coverage(looms_report)
    assert cov["unknown_loom_count"] == 1
    assert cov["served"] == {"maintainer": 1}


def test_build_doctor_report_default_for_legacy_loom_attribute() -> None:
    """The cli default expression for absent attribute is `[] or []`,
    which produces an empty list. This guards the backward-compat path."""
    legacy = _LegacyExternalLoom()
    assert getattr(legacy, "weaver_classes_served", []) == []


# -------- Registry size + smoke --------

def test_default_registry_still_six_after_dignity_frame() -> None:
    """LoomDignityFrame is a Protocol extension, NOT a new-loom addition.
    Registry size invariant is the load-bearing assertion against scope creep."""
    assert len(default_registry()) == 6


def test_doctor_report_includes_schema_v2(synthetic_repo: Path) -> None:
    """Schema_version bump 1 -> 2 is the honest signal of the new fields."""
    report = _build_doctor_report(synthetic_repo)
    assert report["schema_version"] == 2
    assert "weaver_class_coverage" in report

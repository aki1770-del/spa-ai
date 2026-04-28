"""Integration test: LiteratureDriftDetectorLoom against navigation_safety_core.

The fixture at ``tests/fixtures/navigation_safety_config_excerpt.dart`` is a
verbatim excerpt from aki1770-del/SNGNav navigation_safety_core 0.4.0 (lines
46-80 of ``packages/navigation_safety_core/lib/src/navigation_safety_config.dart``,
captured 2026-04-28). It carries inline literature citations next to driver-class
threshold magnitudes — the load-bearing real-world case the loom was designed
to surface.

Per the design brief: "the agent's spec said this is the load-bearing
validation case." This test asserts the loom resolves the known citations in
that excerpt.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from spa_ai.looms.literature_drift_detector import LiteratureDriftDetectorLoom

_FIXTURE = Path(__file__).parent / "fixtures" / "navigation_safety_config_excerpt.dart"


def test_fixture_exists() -> None:
    assert _FIXTURE.exists(), (
        "Fixture file missing — refresh from aki1770-del/SNGNav "
        "navigation_safety_config.dart lines 46-80"
    )


def test_loom_surfaces_navigation_safety_core_citations(synthetic_repo: Path) -> None:
    """Loom must surface the known inline citations in the excerpt."""
    target = synthetic_repo / "navigation_safety_config.dart"
    shutil.copy(_FIXTURE, target)

    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings, "loom should produce a finding on the real-data fixture"

    cached_refs = {f.source_ref for f in loom._cached_findings}

    # The excerpt carries (at minimum) these citation tokens:
    #   - arxiv 2410.06388  (embedded-in-token date 2024-10)
    #   - PubMed 16313881   (lookup-pending; no embedded date)
    #   - PubMed 22664714   (lookup-pending; no embedded date)
    # Verify all three appear in the parsed citation set.
    assert any("2410.06388" in r for r in cached_refs), (
        f"arxiv 2410.06388 missing from cached refs: {cached_refs}"
    )
    assert any("16313881" in r for r in cached_refs), (
        f"PubMed 16313881 missing from cached refs: {cached_refs}"
    )
    assert any("22664714" in r for r in cached_refs), (
        f"PubMed 22664714 missing from cached refs: {cached_refs}"
    )


def test_audit_output_lists_known_citations(synthetic_repo: Path) -> None:
    """Generated audit doc must mention the known sources by name."""
    target = synthetic_repo / "navigation_safety_config.dart"
    shutil.copy(_FIXTURE, target)

    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings
    patch_obj = loom.propose_patch(findings[0], synthetic_repo)

    contents = patch_obj.contents
    assert "navigation_safety_config.dart" in contents
    assert "arxiv 2410.06388" in contents
    # PubMed entries are LOOKUP-REQUIRED but should still appear.
    assert "PubMed 16313881" in contents or "PubMed  16313881" in contents
    assert "PubMed 22664714" in contents or "PubMed  22664714" in contents
    assert "LOOKUP-REQUIRED" in contents


def test_audit_classifies_arxiv_via_embedded_date_source(synthetic_repo: Path) -> None:
    """The arxiv 2410.06388 citation should resolve via embedded-in-token."""
    target = synthetic_repo / "navigation_safety_config.dart"
    shutil.copy(_FIXTURE, target)

    loom = LiteratureDriftDetectorLoom()
    loom.detect(synthetic_repo)

    arxiv_findings = [
        f for f in loom._cached_findings if "2410.06388" in f.source_ref
    ]
    assert arxiv_findings
    assert arxiv_findings[0].date_source == "embedded-in-token"
    # arxiv YYMM=2410 → 2024-10
    assert arxiv_findings[0].cited_date is not None
    assert arxiv_findings[0].cited_date.year == 2024
    assert arxiv_findings[0].cited_date.month == 10

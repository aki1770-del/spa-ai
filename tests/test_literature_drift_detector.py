"""Tests for LiteratureDriftDetectorLoom."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

from spa_ai.looms.base import LoomFinding
from spa_ai.looms.literature_drift_detector import (
    LiteratureDriftDetectorLoom,
    _parse_arxiv_yymm,
    _parse_explicit_date,
)

# ---------------------------------------------------------------------------
# Date parsing helpers
# ---------------------------------------------------------------------------

def test_parse_explicit_date_yyyy_mm() -> None:
    assert _parse_explicit_date("2024-10") == date(2024, 10, 1)


def test_parse_explicit_date_yyyy_mm_dd() -> None:
    assert _parse_explicit_date("2024-10-15") == date(2024, 10, 15)


def test_parse_explicit_date_invalid() -> None:
    assert _parse_explicit_date("not-a-date") is None


def test_parse_arxiv_yymm() -> None:
    # arxiv 2410.06388 → 2024-10
    assert _parse_arxiv_yymm("2410") == date(2024, 10, 1)


def test_parse_arxiv_yymm_invalid_month() -> None:
    assert _parse_arxiv_yymm("2499") is None  # month 99 invalid


def test_parse_arxiv_yymm_non_digit() -> None:
    assert _parse_arxiv_yymm("abcd") is None


# ---------------------------------------------------------------------------
# Vision attribution + Loom contract
# ---------------------------------------------------------------------------

def test_three_slot_vision_attribution() -> None:
    loom = LiteratureDriftDetectorLoom()
    assert loom.sakichi_vision_id == 14
    assert isinstance(loom.method_vision_ids, list)
    assert isinstance(loom.stance_vision_ids, list)
    assert all(1 <= v <= 100 for v in loom.method_vision_ids)
    assert all(1 <= v <= 100 for v in loom.stance_vision_ids)
    # V77 (genchi-genbutsu — actually reads source files) required by base.py contract.
    assert 77 in loom.method_vision_ids
    # V22 (loom-serves-weaver) + V100 (equal-dignity) required.
    assert 22 in loom.stance_vision_ids
    assert 100 in loom.stance_vision_ids


def test_detect_returns_empty_on_clean_repo(synthetic_repo: Path) -> None:
    """No source files = no findings."""
    loom = LiteratureDriftDetectorLoom()
    assert loom.detect(synthetic_repo) == []


def test_propose_patch_does_not_write_to_disk(synthetic_repo: Path) -> None:
    """Loom contract: propose_patch must not write."""
    (synthetic_repo / "src.py").write_text(
        "# per Konstantopoulos 2010 — fog-RT elevation\n"
        "RT_THRESHOLD = 3.58\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings, "fixture should produce a finding"
    _ = loom.propose_patch(findings[0], synthetic_repo)
    assert not (synthetic_repo / ".spa-ai-citation-drift.md").exists()


# ---------------------------------------------------------------------------
# Per-language detection
# ---------------------------------------------------------------------------

_FIXED_TODAY = date(2026, 4, 28)


def _patched_today(monkeypatch_target: str = "spa_ai.looms.literature_drift_detector.date"):
    """Pin date.today() to 2026-04-28 for deterministic drift assertions."""
    return patch(monkeypatch_target)


def test_detect_python_per_author_year_citation(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per Konstantopoulos 2010 — fog-RT elevation in novice drivers\n"
        "RT_THRESHOLD = 3.58\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    assert findings[0].sakichi_vision_id == 14
    assert findings[0].target_path == Path(".spa-ai-citation-drift.md")


def test_detect_dart_arxiv_inline_citation(synthetic_repo: Path) -> None:
    (synthetic_repo / "config.dart").write_text(
        "/// per arxiv 2410.06388 + AAA-FTS — alert-fatigue evidence\n"
        "const double infoTempC = 4.0;\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1


def test_detect_rust_doc_comment_citation(synthetic_repo: Path) -> None:
    (synthetic_repo / "lib.rs").write_text(
        "/// PubMed 16313881 — novice hazard-perception RT 3.58s vs 1.32s experienced\n"
        "pub const NOVICE_RT_S: f64 = 3.58;\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1


def test_detect_cpp_citation(synthetic_repo: Path) -> None:
    (synthetic_repo / "main.cpp").write_text(
        "// per arxiv 2310.12345 — earlier preprint\n"
        "constexpr double K = 0.5;\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1


# ---------------------------------------------------------------------------
# Tiered grammar — STRICT vs PERMISSIVE
# ---------------------------------------------------------------------------

def test_strict_grammar_with_explicit_bracketed_date(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# cite: Smith et al. fog visibility study [2022-01]\n"
        "FOG_VIS_M = 250\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    audit_finding = findings[0]
    assert any(
        f.grammar_tier == "strict-with-date" and f.date_source == "explicit-bracketed"
        for f in loom._cached_findings
    ), "STRICT grammar with explicit-bracketed date-source expected"
    patch_obj = loom.propose_patch(audit_finding, synthetic_repo)
    assert "strict-with-date" in patch_obj.contents
    assert "explicit-bracketed" in patch_obj.contents


def test_permissive_grammar_no_date(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per Konstantopoulos 2010 — RT elevation\n"
        "RT = 3.58\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings
    assert any(
        f.grammar_tier == "permissive-no-date"
        for f in loom._cached_findings
    )


# ---------------------------------------------------------------------------
# Date extraction priority chain
# ---------------------------------------------------------------------------

def test_date_source_explicit_bracketed_takes_priority(synthetic_repo: Path) -> None:
    """STRICT cite tag with explicit date wins over any embedded token."""
    (synthetic_repo / "src.py").write_text(
        "# cite: arxiv 2410.06388 [2024-10]\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    loom.detect(synthetic_repo)
    explicit = [
        f for f in loom._cached_findings if f.date_source == "explicit-bracketed"
    ]
    assert explicit, "explicit-bracketed date should have been resolved"


def test_date_source_embedded_in_token_arxiv(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2410.06388 — alert-fatigue evidence\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    loom.detect(synthetic_repo)
    embedded = [
        f for f in loom._cached_findings if f.date_source == "embedded-in-token"
    ]
    assert embedded
    assert embedded[0].cited_date == date(2024, 10, 1)


def test_date_source_verified_marker_resets_clock(synthetic_repo: Path) -> None:
    """`# verified:` marker on next line wins over (c) git-blame and date-unknown."""
    (synthetic_repo / "src.py").write_text(
        "# per Konstantopoulos 2010 — RT elevation\n"
        "# verified: 2026-04-15\n"
        "RT = 3.58\n"
    )
    loom = LiteratureDriftDetectorLoom()
    loom.detect(synthetic_repo)
    verified = [
        f for f in loom._cached_findings if f.date_source == "verified-marker"
    ]
    assert verified
    assert verified[0].cited_date == date(2026, 4, 15)


def test_lookup_pending_for_pubmed_without_embedded_date(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# PubMed 16313881 — novice fog hazard-perception RT\n"
        "RT = 3.58\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings
    pending = [f for f in loom._cached_findings if f.is_lookup_pending]
    assert pending
    patch_obj = loom.propose_patch(findings[0], synthetic_repo)
    assert "LOOKUP-REQUIRED" in patch_obj.contents


# ---------------------------------------------------------------------------
# 18-month threshold boundary cases
# ---------------------------------------------------------------------------

def test_threshold_boundary_17mo_passes(synthetic_repo: Path, tmp_path: Path) -> None:
    """A citation 17 months old MUST NOT fire under default 18mo threshold."""
    # Today fixed at 2026-04-28; 17mo back = 2024-11.
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2411.00001 — recent preprint\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    # 17mo drift < 18mo threshold → no actionable findings.
    assert findings == []


def test_threshold_boundary_19mo_flags(synthetic_repo: Path) -> None:
    """A citation 19 months old MUST fire under default 18mo threshold."""
    # Today fixed at 2026-04-28; 19mo back = 2024-09.
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2409.00001 — older preprint\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    assert len(findings) == 1


# ---------------------------------------------------------------------------
# `[perpetual]` allowlist + RFC/ISO built-in allowlist
# ---------------------------------------------------------------------------

def test_perpetual_marker_suppresses_drift(synthetic_repo: Path) -> None:
    """Maintainer can mark a citation perpetual to skip the drift clock."""
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2001.00001 [perpetual] — historical reference\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    # Perpetual rows are filtered out — no actionable findings expected.
    assert findings == []


def test_rfc_in_builtin_allowlist(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# RFC 2119 — keyword definitions\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings == []


def test_iso_in_builtin_allowlist(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# ISO 26262-1:2018 functional safety\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings == []


# ---------------------------------------------------------------------------
# Configuration override via .spa-ai-citation-drift.toml
# ---------------------------------------------------------------------------

def test_config_threshold_override(synthetic_repo: Path) -> None:
    """Per-project TOML override: tighten threshold to 12mo."""
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2502.00001 — preprint Feb 2025\n"
        "X = 1\n"
    )
    (synthetic_repo / ".spa-ai-citation-drift.toml").write_text(
        "threshold_months = 12\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    # 14mo old > 12mo configured → fires.
    assert len(findings) == 1


def test_config_extra_allowlist(synthetic_repo: Path) -> None:
    """Maintainer may extend allowlist with own perpetual identifiers."""
    (synthetic_repo / "src.py").write_text(
        "# per Sakichi 1924 — historical loom reference\n"
        "X = 1\n"
    )
    (synthetic_repo / ".spa-ai-citation-drift.toml").write_text(
        "allowlist = ['^Sakichi 1924$']\n"
    )
    loom = LiteratureDriftDetectorLoom()
    findings = loom.detect(synthetic_repo)
    assert findings == []


def test_malformed_config_falls_back_to_defaults(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2409.00001 — older preprint\n"
        "X = 1\n"
    )
    (synthetic_repo / ".spa-ai-citation-drift.toml").write_text(
        "this is not = valid toml = at all = either\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    # Default 18mo threshold still applies; 19mo old still fires.
    assert len(findings) == 1


# ---------------------------------------------------------------------------
# Audit-doc patch format
# ---------------------------------------------------------------------------

def test_audit_doc_contains_required_sections(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2409.00001 — preprint\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    assert findings
    patch_obj = loom.propose_patch(findings[0], synthetic_repo)

    # Audit doc structure
    assert "LiteratureDriftDetectorLoom audit" in patch_obj.contents
    assert "What this file is" in patch_obj.contents
    assert "What you do as the maintainer" in patch_obj.contents
    assert "Configuration" in patch_obj.contents
    assert "Rollback" in patch_obj.contents
    assert "Findings" in patch_obj.contents
    assert "src.py" in patch_obj.contents
    assert "arxiv 2409.00001" in patch_obj.contents

    # PR body Jidoka rationale
    assert "Why this halt" in patch_obj.pr_body
    assert "Vision 14" in patch_obj.pr_body or "vision 14" in patch_obj.pr_body.lower()
    assert "Sakichi" in patch_obj.pr_body
    assert "Rollback" in patch_obj.pr_body
    assert "Provenance" in patch_obj.pr_body


def test_audit_row_records_threshold_that_fired(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2409.00001 — preprint\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    patch_obj = loom.propose_patch(findings[0], synthetic_repo)
    # The row should mention the threshold that flagged it.
    assert "18mo configured" in patch_obj.contents


# ---------------------------------------------------------------------------
# Skip discipline (mirrors SilentFailureGrepperLoom)
# ---------------------------------------------------------------------------

def test_detect_skips_venv_and_build_dirs(synthetic_repo: Path) -> None:
    (synthetic_repo / "venv").mkdir()
    (synthetic_repo / "venv" / "lib.py").write_text(
        "# per arxiv 2409.00001 — vendored\n"
    )
    (synthetic_repo / "build").mkdir()
    (synthetic_repo / "build" / "x.py").write_text(
        "# per arxiv 2409.00001 — built artifact\n"
    )
    loom = LiteratureDriftDetectorLoom()
    assert loom.detect(synthetic_repo) == []


def test_finding_is_a_LoomFinding_instance(synthetic_repo: Path) -> None:
    (synthetic_repo / "src.py").write_text(
        "# per arxiv 2409.00001 — preprint\n"
        "X = 1\n"
    )
    loom = LiteratureDriftDetectorLoom()
    with patch(
        "spa_ai.looms.literature_drift_detector.date"
    ) as mock_date:
        mock_date.today.return_value = _FIXED_TODAY
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        findings = loom.detect(synthetic_repo)
    assert findings
    assert isinstance(findings[0], LoomFinding)

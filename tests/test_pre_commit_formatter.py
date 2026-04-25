"""Tests for PreCommitFormatterLoom."""
from __future__ import annotations

from pathlib import Path

from spa_ai.looms.pre_commit_formatter import PreCommitFormatterLoom


def test_detect_returns_finding_when_config_missing(synthetic_repo: Path) -> None:
    loom = PreCommitFormatterLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.loom_id == "pre-commit-formatter"
    assert finding.target_path == Path(".pre-commit-config.yaml")
    assert finding.sakichi_vision_id == 20
    assert finding.severity == "medium"


def test_detect_returns_empty_when_yaml_present(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    loom = PreCommitFormatterLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_returns_empty_when_yml_present(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yml").write_text("repos: []\n")
    loom = PreCommitFormatterLoom()
    assert loom.detect(synthetic_repo) == []


def test_propose_patch_includes_jidoka_rationale(synthetic_repo: Path) -> None:
    loom = PreCommitFormatterLoom()
    finding = loom.detect(synthetic_repo)[0]
    patch = loom.propose_patch(finding)

    # Promise 2: every halt cites its Jidoka rationale.
    assert "Why this halt" in patch.pr_body
    assert "Sakichi" in patch.pr_body
    assert "Vision 20" in patch.pr_body or "vision 20" in patch.pr_body.lower()

    # The patch must contain the actual hooks the PR claims.
    assert "trailing-whitespace" in patch.contents
    assert "end-of-file-fixer" in patch.contents
    assert "check-yaml" in patch.contents


def test_propose_patch_does_not_write_to_disk(synthetic_repo: Path) -> None:
    """Looms must never write in detect() or propose_patch().

    Per docs/looms/base.py contract — disk writes are restricted to the
    --apply path in the CLI, after human review.
    """
    loom = PreCommitFormatterLoom()
    finding = loom.detect(synthetic_repo)[0]
    _ = loom.propose_patch(finding)
    assert not (synthetic_repo / ".pre-commit-config.yaml").exists()


def test_three_slot_vision_attribution() -> None:
    """Per base.py contract: every loom declares 3 vision-attribution slots.

    sakichi_vision_id (FAILURE-MODE) + method_vision_ids (HOW the loom
    works) + stance_vision_ids (HOW the weaver is treated). The 100
    visions form a graph, not a tag cloud — singular attribution is a
    category error (cross-reference 5-Whys finding 2026-04-25).
    """
    loom = PreCommitFormatterLoom()

    assert loom.sakichi_vision_id == 20
    assert isinstance(loom.method_vision_ids, list)
    assert isinstance(loom.stance_vision_ids, list)
    assert len(loom.method_vision_ids) >= 1
    assert len(loom.stance_vision_ids) >= 1
    assert all(1 <= v <= 100 for v in loom.method_vision_ids)
    assert all(1 <= v <= 100 for v in loom.stance_vision_ids)

    # V77 (genchi genbutsu) — this loom walks the actual repo to detect.
    assert 77 in loom.method_vision_ids
    # V22 (loom-serves-weaver) — every loom must hold this stance.
    assert 22 in loom.stance_vision_ids
    # V25 (autonomation = liberation not replacement) — the anti-replacement
    # declaration that distinguishes a Sakichi loom from a nag-bot or an
    # AI-replaces-the-maintainer tool. Per cross-reference 5-Whys 2026-04-25:
    # belongs in every loom's stance slot.
    assert 25 in loom.stance_vision_ids

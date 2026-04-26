"""Tests for ContributingMdLoom."""
from __future__ import annotations

from pathlib import Path

from spa_ai.looms.contributing_md import ContributingMdLoom


def test_detect_returns_finding_when_contributing_missing(synthetic_repo: Path) -> None:
    loom = ContributingMdLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.loom_id == "contributing-md"
    assert finding.target_path == Path("CONTRIBUTING.md")
    assert finding.sakichi_vision_id == 96
    assert finding.severity == "medium"


def test_detect_returns_empty_when_root_contributing_present(synthetic_repo: Path) -> None:
    (synthetic_repo / "CONTRIBUTING.md").write_text("# Contributing\n")
    loom = ContributingMdLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_returns_empty_when_github_contributing_present(synthetic_repo: Path) -> None:
    (synthetic_repo / ".github").mkdir()
    (synthetic_repo / ".github" / "CONTRIBUTING.md").write_text("# Contributing\n")
    loom = ContributingMdLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_returns_empty_when_docs_contributing_present(synthetic_repo: Path) -> None:
    (synthetic_repo / "docs").mkdir()
    (synthetic_repo / "docs" / "CONTRIBUTING.md").write_text("# Contributing\n")
    loom = ContributingMdLoom()
    assert loom.detect(synthetic_repo) == []


def test_propose_patch_includes_jidoka_rationale(synthetic_repo: Path) -> None:
    loom = ContributingMdLoom()
    finding = loom.detect(synthetic_repo)[0]
    patch = loom.propose_patch(finding)

    # Promise 2: every halt cites its Jidoka rationale.
    assert "Why this halt" in patch.pr_body
    assert "Sakichi" in patch.pr_body
    assert "Vision 96" in patch.pr_body or "vision 96" in patch.pr_body.lower()

    # Patch contents are a real CONTRIBUTING.md, not boilerplate
    assert "# Contributing" in patch.contents
    assert "What contributions are welcome" in patch.contents
    assert "What the maintainer commits to" in patch.contents


def test_propose_patch_does_not_write_to_disk(synthetic_repo: Path) -> None:
    """Looms must never write in detect() or propose_patch().

    Per docs/looms/base.py contract — disk writes are restricted to the
    --apply path in the CLI, after human review.
    """
    loom = ContributingMdLoom()
    finding = loom.detect(synthetic_repo)[0]
    _ = loom.propose_patch(finding)
    assert not (synthetic_repo / "CONTRIBUTING.md").exists()


def test_three_slot_vision_attribution() -> None:
    """Per base.py contract: every loom declares 3 vision-attribution slots.

    sakichi_vision_id (FAILURE-MODE) + method_vision_ids (HOW the loom
    works) + stance_vision_ids (HOW the weaver is treated). Per the
    cross-reference 5-Whys finding 2026-04-25: singular attribution is a
    category error.
    """
    loom = ContributingMdLoom()

    # Failure-mode anchor
    assert loom.sakichi_vision_id == 96  # maintainers are edge developers

    # Method visions
    assert isinstance(loom.method_vision_ids, list)
    assert len(loom.method_vision_ids) >= 1
    assert all(1 <= v <= 100 for v in loom.method_vision_ids)
    assert 77 in loom.method_vision_ids  # genchi-genbutsu — walks repo

    # Stance visions
    assert isinstance(loom.stance_vision_ids, list)
    assert len(loom.stance_vision_ids) >= 1
    assert all(1 <= v <= 100 for v in loom.stance_vision_ids)
    assert 22 in loom.stance_vision_ids   # loom-serves-weaver
    assert 96 in loom.stance_vision_ids   # explicit V96 stance — this loom
                                          # IS the maintainer-dignity loom
    assert 100 in loom.stance_vision_ids  # equal-dignity for every weaver

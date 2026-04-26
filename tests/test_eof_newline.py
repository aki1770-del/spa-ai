"""Tests for EofNewlineLoom — first user of the extended Loom Protocol."""
from __future__ import annotations

from pathlib import Path

from spa_ai.looms.eof_newline import EofNewlineLoom

# Sample baseline pre-commit-config WITHOUT end-of-file-fixer
_CONFIG_WITHOUT_EOF = """\
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: check-yaml
"""

# Sample baseline WITH end-of-file-fixer
_CONFIG_WITH_EOF = """\
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
"""


def test_detect_returns_finding_when_eof_hook_missing(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yaml").write_text(_CONFIG_WITHOUT_EOF)
    loom = EofNewlineLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.loom_id == "eof-newline"
    assert finding.target_path == Path(".pre-commit-config.yaml")
    assert finding.sakichi_vision_id == 15
    assert finding.severity == "low"


def test_detect_returns_empty_when_eof_hook_present(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yaml").write_text(_CONFIG_WITH_EOF)
    loom = EofNewlineLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_returns_empty_when_no_pre_commit_config(synthetic_repo: Path) -> None:
    """No config = no signal for THIS loom (PreCommitFormatterLoom handles that case)."""
    loom = EofNewlineLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_works_with_yml_extension(synthetic_repo: Path) -> None:
    """Both .yaml and .yml are recognized pre-commit-config filenames."""
    (synthetic_repo / ".pre-commit-config.yml").write_text(_CONFIG_WITHOUT_EOF)
    loom = EofNewlineLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    assert findings[0].target_path == Path(".pre-commit-config.yml")


def test_propose_patch_merges_existing_with_eof_hook(synthetic_repo: Path) -> None:
    """First-user-of-extended-Protocol test: propose_patch reads existing
    config from repo_root + appends EOF hook block + returns merged contents."""
    (synthetic_repo / ".pre-commit-config.yaml").write_text(_CONFIG_WITHOUT_EOF)
    loom = EofNewlineLoom()
    finding = loom.detect(synthetic_repo)[0]
    patch = loom.propose_patch(finding, synthetic_repo)

    # Existing hooks PRESERVED
    assert "trailing-whitespace" in patch.contents
    assert "check-yaml" in patch.contents

    # New hook APPENDED
    assert "end-of-file-fixer" in patch.contents

    # Existing structure intact (the original config text is in the merged output)
    assert _CONFIG_WITHOUT_EOF.strip() in patch.contents


def test_propose_patch_includes_jidoka_rationale(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yaml").write_text(_CONFIG_WITHOUT_EOF)
    loom = EofNewlineLoom()
    finding = loom.detect(synthetic_repo)[0]
    patch = loom.propose_patch(finding, synthetic_repo)

    assert "Why this halt" in patch.pr_body
    assert "Sakichi" in patch.pr_body
    assert "Vision 15" in patch.pr_body or "vision 15" in patch.pr_body.lower()
    assert "poka-yoke" in patch.pr_body.lower()


def test_propose_patch_does_not_write_to_disk(synthetic_repo: Path) -> None:
    """Loom contract: no disk writes in propose_patch (read is allowed)."""
    (synthetic_repo / ".pre-commit-config.yaml").write_text(_CONFIG_WITHOUT_EOF)
    original_mtime = (synthetic_repo / ".pre-commit-config.yaml").stat().st_mtime
    loom = EofNewlineLoom()
    finding = loom.detect(synthetic_repo)[0]
    _ = loom.propose_patch(finding, synthetic_repo)
    # File mtime unchanged (no write happened)
    assert (synthetic_repo / ".pre-commit-config.yaml").stat().st_mtime == original_mtime


def test_three_slot_vision_attribution() -> None:
    loom = EofNewlineLoom()
    assert loom.sakichi_vision_id == 15
    assert isinstance(loom.method_vision_ids, list)
    assert isinstance(loom.stance_vision_ids, list)
    assert all(1 <= v <= 100 for v in loom.method_vision_ids)
    assert all(1 <= v <= 100 for v in loom.stance_vision_ids)
    assert 77 in loom.method_vision_ids
    assert 22 in loom.stance_vision_ids

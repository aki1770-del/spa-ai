"""Tests for PreCommitFormatterRustLoom."""
from __future__ import annotations

from pathlib import Path

from spa_ai.looms.pre_commit_formatter_rust import PreCommitFormatterRustLoom


def test_detect_returns_finding_in_rust_repo_without_config(rust_repo: Path) -> None:
    loom = PreCommitFormatterRustLoom()
    findings = loom.detect(rust_repo)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.loom_id == "pre-commit-formatter-rust"
    assert finding.target_path == Path(".pre-commit-config.yaml")
    assert finding.sakichi_vision_id == 20
    assert finding.severity == "medium"
    assert "Cargo.toml" in finding.reason


def test_detect_returns_empty_in_non_rust_repo(synthetic_repo: Path) -> None:
    """Non-Rust repos must not trigger this loom (no Cargo.toml)."""
    loom = PreCommitFormatterRustLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_returns_empty_when_yaml_already_present(rust_repo: Path) -> None:
    (rust_repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    loom = PreCommitFormatterRustLoom()
    assert loom.detect(rust_repo) == []


def test_detect_returns_empty_when_yml_already_present(rust_repo: Path) -> None:
    (rust_repo / ".pre-commit-config.yml").write_text("repos: []\n")
    loom = PreCommitFormatterRustLoom()
    assert loom.detect(rust_repo) == []


def test_propose_patch_includes_rustfmt_hook(rust_repo: Path) -> None:
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    patch = loom.propose_patch(finding)

    # Promise 2: every halt cites its Jidoka rationale.
    assert "Why this halt" in patch.pr_body
    assert "Sakichi" in patch.pr_body
    assert "Vision 20" in patch.pr_body or "vision 20" in patch.pr_body.lower()

    # Rust-specific: rustfmt must be wired in; clippy must NOT be (V20).
    assert "rustfmt" in patch.contents
    assert "cargo fmt" in patch.contents
    assert "clippy" not in patch.contents.lower() or "# " in patch.contents
    # PR body must explain why clippy is excluded.
    assert "clippy" in patch.pr_body.lower()
    assert "ci" in patch.pr_body.lower()


def test_propose_patch_includes_baseline_hooks(rust_repo: Path) -> None:
    """Rust loom inherits the language-agnostic baseline + adds rustfmt."""
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    patch = loom.propose_patch(finding)
    assert "trailing-whitespace" in patch.contents
    assert "end-of-file-fixer" in patch.contents
    assert "check-yaml" in patch.contents
    assert "check-merge-conflict" in patch.contents
    assert "check-added-large-files" in patch.contents


def test_propose_patch_does_not_write_to_disk(rust_repo: Path) -> None:
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    _ = loom.propose_patch(finding)
    assert not (rust_repo / ".pre-commit-config.yaml").exists()

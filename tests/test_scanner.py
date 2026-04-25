"""Tests for RepoScanner."""
from __future__ import annotations

from pathlib import Path

import pytest

from spa_ai.registry import default_registry
from spa_ai.scanner import RepoScanner


def test_scanner_raises_on_nonexistent_path(tmp_path: Path) -> None:
    scanner = RepoScanner(default_registry())
    bogus = tmp_path / "nonexistent"
    with pytest.raises(FileNotFoundError):
        scanner.scan(bogus)


def test_scanner_raises_on_non_git_path(tmp_path: Path) -> None:
    scanner = RepoScanner(default_registry())
    notarepo = tmp_path / "notgit"
    notarepo.mkdir()
    with pytest.raises(ValueError, match="Not a git repo"):
        scanner.scan(notarepo)


def test_scanner_finds_pre_commit_gap_in_synthetic_repo(synthetic_repo: Path) -> None:
    scanner = RepoScanner(default_registry())
    findings = scanner.scan(synthetic_repo)
    assert any(f.loom_id == "pre-commit-formatter" for f in findings)


def test_scanner_returns_empty_when_no_gaps(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    scanner = RepoScanner(default_registry())
    findings = scanner.scan(synthetic_repo)
    assert findings == []


def test_scanner_in_rust_repo_returns_both_pre_commit_findings(rust_repo: Path) -> None:
    """A Rust repo with no config should fire both pre-commit looms.

    The CLI human picks which one to propose by --loom id; the scanner
    just reports all gaps. Both share `target_path = .pre-commit-config.yaml`
    so the human (not the loom) chooses which template to install.
    """
    scanner = RepoScanner(default_registry())
    findings = scanner.scan(rust_repo)
    loom_ids = {f.loom_id for f in findings}
    assert "pre-commit-formatter" in loom_ids
    assert "pre-commit-formatter-rust" in loom_ids

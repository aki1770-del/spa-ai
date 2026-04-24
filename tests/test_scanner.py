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

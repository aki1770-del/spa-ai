"""Tests for the spa-ai CLI."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Invoke `python -m spa_ai.cli` with given args."""
    return subprocess.run(
        [sys.executable, "-m", "spa_ai.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_scan_synthetic_repo_lists_pre_commit_finding(synthetic_repo: Path) -> None:
    result = _run_cli("scan", str(synthetic_repo))
    assert result.returncode == 0, result.stderr
    assert "pre-commit-formatter" in result.stdout
    assert "V20" in result.stdout


def test_scan_clean_repo_reports_no_findings(synthetic_repo: Path) -> None:
    (synthetic_repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    result = _run_cli("scan", str(synthetic_repo))
    assert result.returncode == 0
    assert "No missing looms" in result.stdout


def test_propose_dry_run_default_does_not_write(synthetic_repo: Path) -> None:
    result = _run_cli(
        "propose", str(synthetic_repo), "--loom", "pre-commit-formatter"
    )
    assert result.returncode == 0, result.stderr
    assert "DRY-RUN" in result.stdout
    assert "Why this halt" in result.stdout
    assert not (synthetic_repo / ".pre-commit-config.yaml").exists()


def test_propose_apply_writes_file(synthetic_repo: Path) -> None:
    result = _run_cli(
        "propose",
        str(synthetic_repo),
        "--loom",
        "pre-commit-formatter",
        "--apply",
    )
    assert result.returncode == 0, result.stderr
    assert "WROTE" in result.stdout
    target = synthetic_repo / ".pre-commit-config.yaml"
    assert target.exists()
    assert "trailing-whitespace" in target.read_text()


def test_propose_apply_refuses_to_overwrite_existing(synthetic_repo: Path) -> None:
    target = synthetic_repo / ".pre-commit-config.yaml"
    target.write_text("# pre-existing config\nrepos: []\n")
    result = _run_cli(
        "propose",
        str(synthetic_repo),
        "--loom",
        "pre-commit-formatter",
        "--apply",
    )
    # Detect returns no findings when the file exists, so propose
    # short-circuits with "nothing to propose".
    assert result.returncode == 0
    assert "nothing to propose" in result.stdout
    # And the existing file is untouched.
    assert "pre-existing config" in target.read_text()


def test_propose_unknown_loom_exits_nonzero(synthetic_repo: Path) -> None:
    result = _run_cli(
        "propose", str(synthetic_repo), "--loom", "nope-not-a-loom"
    )
    assert result.returncode == 2
    assert "Unknown loom" in result.stderr


def test_propose_nonexistent_path_exits_nonzero(tmp_path: Path) -> None:
    bogus = tmp_path / "does-not-exist"
    result = _run_cli(
        "propose", str(bogus), "--loom", "pre-commit-formatter"
    )
    assert result.returncode == 2
    assert "does not exist" in result.stderr


def test_propose_non_git_path_exits_nonzero(tmp_path: Path) -> None:
    notgit = tmp_path / "plain-dir"
    notgit.mkdir()
    result = _run_cli(
        "propose", str(notgit), "--loom", "pre-commit-formatter"
    )
    assert result.returncode == 2
    assert "Not a git repo" in result.stderr


def test_no_alert_subcommand_exists(synthetic_repo: Path) -> None:
    """Per Commitment 1, the CLI has no `alert` subcommand."""
    result = _run_cli("alert", str(synthetic_repo))
    assert result.returncode != 0
    assert "invalid choice" in result.stderr.lower() or "alert" in result.stderr

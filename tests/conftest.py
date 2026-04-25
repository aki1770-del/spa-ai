"""Shared test fixtures."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _init_git(repo: Path) -> None:
    """Initialise a synthetic git working tree at `repo` with one commit."""
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        [
            "git",
            "-c", "user.email=test@example.invalid",
            "-c", "user.name=Test",
            "commit", "-q", "-m", "init",
        ],
        cwd=repo,
        check=True,
    )


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    """Minimal synthetic git working tree (one README commit; no language).

    Loom tests add or omit specific files to assert detection behavior.
    """
    repo = tmp_path / "synthetic"
    repo.mkdir()
    (repo / "README.md").write_text("# Synthetic test repo\n")
    _init_git(repo)
    return repo


@pytest.fixture
def rust_repo(tmp_path: Path) -> Path:
    """Synthetic git working tree shaped like a minimal Rust crate.

    Has `Cargo.toml` + `src/lib.rs` so language-detection looms see
    a real Rust signal.
    """
    repo = tmp_path / "rust"
    repo.mkdir()
    (repo / "Cargo.toml").write_text(
        '[package]\nname = "synthetic"\nversion = "0.1.0"\nedition = "2021"\n'
    )
    (repo / "src").mkdir()
    (repo / "src" / "lib.rs").write_text("pub fn placeholder() {}\n")
    _init_git(repo)
    return repo

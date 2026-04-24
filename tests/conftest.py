"""Shared test fixtures."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    """Create a minimal synthetic git working tree for loom tests.

    The repo has one commit (a README) and no other files. Loom tests
    add or omit specific files to assert detection behavior.
    """
    repo = tmp_path / "synthetic"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Synthetic test repo\n")
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
    return repo

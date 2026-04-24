"""RepoScanner — walks a git clone and surfaces loom-candidate findings."""
from __future__ import annotations

from pathlib import Path

from .looms.base import LoomFinding
from .registry import LoomRegistry


class RepoScanner:
    """Runs every registered loom's `detect()` against a target repo."""

    def __init__(self, registry: LoomRegistry) -> None:
        self._registry = registry

    def scan(self, repo_root: Path) -> list[LoomFinding]:
        """Walk the registry, collect findings.

        Raises:
            FileNotFoundError: `repo_root` does not exist.
            ValueError: `repo_root` is not a git working tree (no `.git/`).
        """
        if not repo_root.exists():
            raise FileNotFoundError(f"Repo path does not exist: {repo_root}")
        if not (repo_root / ".git").exists():
            raise ValueError(
                f"Not a git repo (no .git/ directory found at {repo_root})"
            )

        findings: list[LoomFinding] = []
        for loom in self._registry.all():
            findings.extend(loom.detect(repo_root))
        return findings

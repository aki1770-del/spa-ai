"""Loom abstract base + finding/patch dataclasses.

A Loom is a single Jidoka halt SPA AI knows how to detect and install.

Every loom must:
1. Declare its `loom_id` (slug) and `sakichi_vision_id` (1..100, per
   `docs/sakichi_100_visions.md`). The vision id is required by
   commitments.md Commitment 5 — features without lineage do not pass
   review.
2. Implement `detect()` — walk the repo, return a list of LoomFinding.
3. Implement `propose_patch()` — given a finding, return a LoomPatch
   (file contents + PR body).

Looms must not write to disk in `detect()` or `propose_patch()`.
Disk writes are restricted to the `--apply` path in the CLI, after
human review of the proposed patch. Per promises.md Promise 4, the
weaver — not the loom — owns the halt.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class LoomFinding:
    """A detected loom-shaped opportunity in a repo.

    Attributes:
        loom_id: Slug identifying which loom raised the finding.
        target_path: Path relative to the repo root where the loom
            would install its halt.
        reason: Short human-readable description of why this finding
            was raised.
        sakichi_vision_id: Which of the 100 visions grounds this loom
            (per `docs/sakichi_100_visions.md`).
        severity: One of "low", "medium", "high".
    """

    loom_id: str
    target_path: Path
    reason: str
    sakichi_vision_id: int
    severity: str


@dataclass(frozen=True)
class LoomPatch:
    """A generated halt installation, ready for human review.

    Attributes:
        loom_id: Slug identifying which loom generated this patch.
        target_path: Path relative to the repo root where the file
            will be written.
        contents: Full file contents to write at `target_path`.
        pr_body: Markdown PR body explaining the halt — required to
            include a "Why this halt" section per promises.md Promise 2.
    """

    loom_id: str
    target_path: Path
    contents: str
    pr_body: str


class Loom(Protocol):
    """Abstract base for all loom classes."""

    loom_id: str
    sakichi_vision_id: int

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        """Walk `repo_root` and return findings. Must not write to disk."""
        ...

    def propose_patch(self, finding: LoomFinding) -> LoomPatch:
        """Generate a patch for a single finding. Must not write to disk."""
        ...

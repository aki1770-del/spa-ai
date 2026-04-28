"""Loom abstract base + finding/patch dataclasses.

A Loom is a single Jidoka halt SPA AI knows how to detect and install.

Every loom must:
1. Declare three vision-attribution slots (per the 2026-04-25
   cross-reference 5-Whys finding that singular attribution is a
   category error — the 100 visions form a graph, not a tag cloud):

   - `sakichi_vision_id` (int, 1..100) — the FAILURE-MODE vision this
     loom prevents. The single anchor of "what halt is this?". Required.
   - `method_vision_ids` (list[int]) — METHOD visions describing HOW the
     loom does its work (e.g., V77 genchi genbutsu for any loom that
     walks the actual repo; V11 Andon for any loom installing a
     contributor-side cord; V18 5-Whys for any loom whose PR body
     terminates at mechanism). Defaults to [] for backwards compat.
   - `stance_vision_ids` (list[int]) — STANCE/TONE visions describing
     HOW THE WEAVER IS TREATED by the loom (e.g., V22 loom-serves-
     weaver, V32 katei-teki tone, V100 equal dignity). Defaults to [].

   All three slots ground in `docs/sakichi_100_visions.md` and are
   required by commitments.md Commitment 5 for full lineage traceability.

   In addition, a fourth slot names WHO the loom serves (FACT-data,
   distinct from the three vision slots which are stance/method/failure-
   mode declarations):

   - `weaver_classes_served` (list[str]) — the weaver-classes this loom
     directly serves (e.g., `["maintainer", "first-contributor"]`). See
     `weaver_classes.py` for the canonical v1 set and alias map. Defaults
     to `[]` for backward-compat — a loom predating this slot continues
     to register, and the doctor surface reports any such loom in an
     advisory "unknown" bucket so the gap is visible without breaking
     the registry contract. Open-string-set: declarations not in the
     canonical set surface as advisory, not as registration errors.

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
    method_vision_ids: list[int]
    stance_vision_ids: list[int]
    weaver_classes_served: list[str]

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        """Walk `repo_root` and return findings. Must not write to disk."""
        ...

    def propose_patch(self, finding: LoomFinding, repo_root: Path) -> LoomPatch:
        """Generate a patch for a single finding. Must not write to disk.

        `repo_root` is the absolute path to the repository the loom scanned
        in `detect()`. Looms that need to MERGE with existing files (e.g.,
        appending a hook to an existing pre-commit-config) read those files
        via `repo_root / finding.target_path`. Looms that always create
        new files (most loom classes) can ignore `repo_root`.

        Reading from `repo_root` is permitted; writing is forbidden — disk
        writes are restricted to the `--apply` path in the CLI per
        promises.md Promise 4."""
        ...

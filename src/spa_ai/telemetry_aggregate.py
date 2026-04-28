"""Local-only aggregation over `~/.spa-ai/usage_reports.jsonl`.

W4 of the launch plan: the harness shipped in PR #16 + the driver-profile
field shipped in PR #18 give us a local JSONL substrate. This module
makes that substrate actionable: a pure-function aggregator the CLI
calls to produce per-profile / per-loom / per-vision counts the
maintainer can read herself before any future submission slice exists.

Per `commitments.md` and `promises.md`:
  - No network call. Reads only the local JSONL the user opted into
    writing via `--report-anonymous-usage`.
  - Class-level only. `driver_profile` is a self-declared label about
    the app's user-population, never about an individual user.
  - Robust to a partially-malformed file: skip lines that aren't valid
    JSON or that lack the required shape, and surface a count of the
    skipped lines in the result so the maintainer can see drift.

3-slot vision attribution:
  sakichi=99 (write-the-decision-down — the report IS the local
              decision record of which looms fired where, by which
              user-population class, in what shape)
  method=[77, 99] (genchi-genbutsu reads the actual local file /
                   write-it-down structured for the maintainer)
  stance=[22, 96, 100] (loom-serves-weaver — surfaces her own data
                        for her own calibration / V96 maintainers-as-
                        edge-developers / equal-dignity — same opt-in
                        substrate her downstream tools would expect)
"""
from __future__ import annotations

import json
import logging
import os
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_REPORT_DIR = Path.home() / ".spa-ai"
_DEFAULT_REPORT_FILE = _DEFAULT_REPORT_DIR / "usage_reports.jsonl"

_MISSING_PROFILE_KEY = "(unset)"
"""Aggregation key used when a report record has no `driver_profile`.

Records written before PR #18 (and records from invocations without
`--driver-profile`) lack the field entirely. Bucketing them under a
visible sentinel preserves the count without inventing a label.
"""


@dataclass
class AggregateResult:
    """Structured aggregation output. Pure data — CLI layer formats it."""

    schema_version: int = 1
    report_path: str = ""
    record_count: int = 0
    skipped_line_count: int = 0
    by_driver_profile: dict[str, int] = field(default_factory=dict)
    by_loom_id: dict[str, int] = field(default_factory=dict)
    by_sakichi_vision_id: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Return JSON-ready dict (counts sorted by descending value)."""
        return {
            "schema_version": self.schema_version,
            "command": "telemetry-aggregate",
            "report_path": self.report_path,
            "record_count": self.record_count,
            "skipped_line_count": self.skipped_line_count,
            "by_driver_profile": _sorted_desc(self.by_driver_profile),
            "by_loom_id": _sorted_desc(self.by_loom_id),
            "by_sakichi_vision_id": _sorted_desc(self.by_sakichi_vision_id),
        }


def _sorted_desc(counts: dict[str, int]) -> dict[str, int]:
    """Return a dict with the same items, ordered by count descending then key."""
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def resolve_report_path(report_path: Path | None = None) -> Path:
    """Resolve the JSONL path the same way `telemetry.write_report` does.

    Honors `SPA_AI_USAGE_REPORT_PATH` env var when `report_path` is None.
    Mirrors the resolution shipped in PR #16 (`telemetry.py:147-149`)
    so the maintainer reads the same file the harness wrote.
    """
    if report_path is not None:
        return report_path
    env = os.environ.get("SPA_AI_USAGE_REPORT_PATH")
    return Path(env) if env else _DEFAULT_REPORT_FILE


def aggregate(
    report_path: Path | None = None,
    driver_profile_filter: str | None = None,
) -> AggregateResult:
    """Read the JSONL file and return per-axis counts.

    When `driver_profile_filter` is set, only records whose
    `driver_profile` field matches the filter contribute to per-loom
    and per-vision counts. The per-profile axis is still emitted so
    the maintainer can see the filter took effect.

    Records without the field are bucketed under `(unset)` for the
    per-profile axis, and only contribute to per-loom / per-vision
    counts when no filter is applied (matching the unfiltered intent).

    A line that is not valid JSON, or that lacks `findings`, is
    counted in `skipped_line_count` and otherwise ignored — never
    raises. The harness writes line-delimited JSON; one bad line
    should not crash the report.
    """
    resolved = resolve_report_path(report_path)
    result = AggregateResult(report_path=str(resolved))

    if not resolved.exists():
        return result

    by_profile: Counter[str] = Counter()
    by_loom: Counter[str] = Counter()
    by_vision: Counter[str] = Counter()

    with resolved.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                result.skipped_line_count += 1
                logger.warning("skipping malformed JSONL line in %s", resolved)
                continue
            if not isinstance(record, dict) or "findings" not in record:
                result.skipped_line_count += 1
                logger.warning("skipping record without findings field in %s", resolved)
                continue

            profile = record.get("driver_profile", _MISSING_PROFILE_KEY)
            by_profile[profile] += 1

            if driver_profile_filter is not None and profile != driver_profile_filter:
                # Per-loom + per-vision axes respect the filter; per-profile
                # axis stays full so the filter's effect is visible.
                continue

            result.record_count += 1
            findings = record.get("findings") or []
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                loom_id = finding.get("loom_id")
                if isinstance(loom_id, str):
                    by_loom[loom_id] += 1
                vision = finding.get("sakichi_vision_id")
                if vision is not None:
                    by_vision[str(vision)] += 1

    result.by_driver_profile = dict(by_profile)
    result.by_loom_id = dict(by_loom)
    result.by_sakichi_vision_id = dict(by_vision)
    return result

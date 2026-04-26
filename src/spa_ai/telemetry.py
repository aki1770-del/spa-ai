"""SPA AI telemetry harness — opt-in, local-only, no network in v0.4.

W2-4 of the 3-week launch plan. Per principles.md V65 Sekishō-idai
(one stone at a time): this slice ships the harness only. The harness
appends one JSON line per scan to a local file the user can inspect
before any future submission slice exists.

Per commitments.md and promises.md:
  - The flag is opt-in (default OFF).
  - No network calls in v0.4.
  - Repo identifier is sha256 of `git remote get-url origin` (or, if
    no remote, sha256 of the resolved repo path). Same repo hashes
    consistently across scans on the same host without disclosing the
    path.
  - No file contents, no maintainer names, no commit hashes captured.
  - Findings are summarized as (loom_id, sakichi_vision_id, severity)
    triples. The target_path is captured because it's repo-relative
    and reveals nothing about the host.

The user can `cat ~/.spa-ai/usage_reports.jsonl` at any time to see
exactly what the harness has recorded.

Future slice (post-v0.4): an explicit `spa-ai telemetry submit`
subcommand that uploads accumulated reports to a public aggregator
the maintainer chooses. Until that slice exists, the file is local
only — no implicit network behavior.

3-slot vision attribution for the harness itself:
  sakichi=99 (write-the-decision-down — usage data IS the decision
              record of which looms fired where, in what shape)
  method=[77, 99] (genchi-genbutsu walks the actual repo / write-down)
  stance=[22, 25, 100] (loom-serves-weaver — opt-in respects choice /
                        autonomation = liberation not surveillance /
                        equal-dignity — same opt-in standard for our
                        own usage capture as we'd ask of any tool)
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import subprocess
from collections.abc import Iterable
from pathlib import Path

from .looms.base import LoomFinding

_SCHEMA_VERSION = 1
_DEFAULT_REPORT_DIR = Path.home() / ".spa-ai"
_DEFAULT_REPORT_FILE = _DEFAULT_REPORT_DIR / "usage_reports.jsonl"


def _spa_ai_version() -> str:
    """Return the installed spa-ai version, or 'unknown' if not packaged."""
    try:
        from importlib.metadata import version

        return version("spa-ai")
    except Exception:
        return "unknown"


def _hash_repo(repo_root: Path) -> str:
    """Return sha256 of git origin URL if available, else of resolved path.

    The same repo on the same host hashes the same across scans.
    The host's filesystem layout is never disclosed; the git remote URL
    (if present) is hashed not stored.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            material = result.stdout.strip().encode("utf-8")
            return "sha256:" + hashlib.sha256(material).hexdigest()
    except Exception:
        pass
    material = str(repo_root.resolve()).encode("utf-8")
    return "sha256:" + hashlib.sha256(material).hexdigest()


def build_report(repo_root: Path, findings: Iterable[LoomFinding]) -> dict:
    """Build the report dict for a single scan invocation.

    Pure function — no I/O, no side effects. The caller decides whether
    to write it; this lets the CLI print the dict in a future
    `--dry-run-telemetry` mode without ever touching disk.
    """
    return {
        "schema_version": _SCHEMA_VERSION,
        "timestamp": _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds"),
        "spa_ai_version": _spa_ai_version(),
        "repo_hash": _hash_repo(repo_root),
        "findings": [
            {
                "loom_id": f.loom_id,
                "sakichi_vision_id": f.sakichi_vision_id,
                "severity": f.severity,
                "target_path": str(f.target_path),
            }
            for f in findings
        ],
    }


def write_report(
    repo_root: Path,
    findings: Iterable[LoomFinding],
    report_path: Path | None = None,
) -> Path:
    """Append one JSON line for this scan to the report file.

    Returns the path written to. Creates the parent dir if needed.
    `report_path` override lets tests redirect; production callers
    pass None and get the default at ~/.spa-ai/usage_reports.jsonl.

    Honors the SPA_AI_USAGE_REPORT_PATH env var if set, for users who
    want the file somewhere other than ~/.spa-ai/.
    """
    if report_path is None:
        env = os.environ.get("SPA_AI_USAGE_REPORT_PATH")
        report_path = Path(env) if env else _DEFAULT_REPORT_FILE
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(repo_root, list(findings))
    with report_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(report, separators=(",", ":")) + "\n")
    return report_path

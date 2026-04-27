"""SPA AI command-line interface.

Three subcommands in v0.4:

  spa-ai scan <path> [--format=human|json] [--report-anonymous-usage]
      Walk the repo, list missing looms with their Jidoka rationale.

  spa-ai propose <path> --loom <id> [--apply]
      Generate the patch for a specific loom. Without --apply, prints
      the patch (dry-run, the default per promises.md Promise 4 — the
      weaver owns the halt). With --apply, writes the file to disk.

  spa-ai doctor <path> [--format=human|json] [--report-anonymous-usage]
      One-command introspection for the maintainer about her own repo.
      Reports each loom's status (would-fire / clean / not-applicable)
      with sample findings + ordered next-step suggestions. V77 primitive
      (the maintainer goes to her own place — the repo — and observes
      what would change before any patch is proposed).

The CLI deliberately omits `alert` and `submit` subcommands. Per
commitments.md Commitment 1, SPA AI does not surface gaps as alerts;
per V65 Sekishō-idai, we ship one stone at a time.
"""
from __future__ import annotations

import argparse
import json as _json
import sys
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .looms.base import LoomFinding
from .registry import default_registry
from .scanner import RepoScanner
from .telemetry import write_report


def _spa_ai_version() -> str:
    """Return installed spa-ai version, or 'unknown' if not packaged."""
    try:
        return version("spa-ai")
    except PackageNotFoundError:
        return "unknown"


def _classify_loom_status(
    loom_id: str, repo: Path, findings: list[LoomFinding]
) -> tuple[str, str]:
    """Return ('would_fire' | 'clean' | 'not_applicable', reason).

    Per-loom applicability heuristic. v0.4 keeps this in cli.py rather
    than extending the Loom Protocol; if external loom authors emerge
    and need to declare their own applicability, a Protocol extension
    `is_applicable(repo_root) -> bool` becomes justified.
    """
    if findings:
        return ("would_fire", f"{len(findings)} finding(s)")

    # No findings — distinguish CLEAN vs NOT_APPLICABLE per loom.
    if loom_id == "pre-commit-formatter":
        # Applicable to any git repo. No findings = config exists.
        return ("clean", ".pre-commit-config.{yaml,yml} present")

    if loom_id == "pre-commit-formatter-rust":
        if not (repo / "Cargo.toml").exists():
            return ("not_applicable", "no Cargo.toml in repo root")
        return ("clean", ".pre-commit-config.{yaml,yml} present")

    if loom_id == "contributing-md":
        # Applicable always for git repos.
        return ("clean", "CONTRIBUTING.md present at root, .github/, or docs/")

    if loom_id == "silent-failure-grepper":
        py_files = list(repo.rglob("*.py"))
        # Filter venv/build/etc. (mirrors loom's own filtering).
        skip_dirs = ("venv", ".venv", "build", "dist", "__pycache__")
        py_files = [
            p for p in py_files
            if not any(part in skip_dirs for part in p.parts)
            and not any(part.startswith(".") and part != ".github" for part in p.parts)
        ]
        if not py_files:
            return ("not_applicable", "no Python files in repo (after venv/build skips)")
        return ("clean", f"{len(py_files)} Python file(s); no silent-failure shapes detected")

    if loom_id == "eof-newline":
        cfg = (repo / ".pre-commit-config.yaml").exists() or (
            repo / ".pre-commit-config.yml"
        ).exists()
        if not cfg:
            return (
                "not_applicable",
                "no .pre-commit-config; this loom only fires when config exists",
            )
        return ("clean", ".pre-commit-config has end-of-file-fixer hook")

    # Unknown loom (external / future) — default to "clean" rather than fabricate.
    return ("clean", "no findings; applicability heuristic not defined for this loom")


def _build_doctor_report(repo: Path) -> dict:
    """Build the doctor report dict (pure function — no I/O side effects).

    Returns the structured report used for both human and JSON output.
    """
    registry = default_registry()
    scanner = RepoScanner(registry)
    all_findings = scanner.scan(repo)

    findings_by_loom: dict[str, list[LoomFinding]] = {}
    for f in all_findings:
        findings_by_loom.setdefault(f.loom_id, []).append(f)

    looms_report = []
    for loom in registry.all():
        loom_findings = findings_by_loom.get(loom.loom_id, [])
        status, reason = _classify_loom_status(loom.loom_id, repo, loom_findings)
        entry = {
            "loom_id": loom.loom_id,
            "sakichi_vision_id": loom.sakichi_vision_id,
            "status": status,
            "finding_count": len(loom_findings),
            "reason": reason,
        }
        if loom_findings:
            f = loom_findings[0]
            entry["severity"] = f.severity
            entry["sample_finding"] = {
                "target_path": str(f.target_path),
                "reason": f.reason,
            }
            entry["install_command"] = f"spa-ai propose {repo} --loom {loom.loom_id}"
        looms_report.append(entry)

    summary = {
        "total_looms": len(looms_report),
        "would_fire_count": sum(1 for L in looms_report if L["status"] == "would_fire"),
        "clean_count": sum(1 for L in looms_report if L["status"] == "clean"),
        "not_applicable_count": sum(1 for L in looms_report if L["status"] == "not_applicable"),
    }

    return {
        "schema_version": 1,
        "command": "doctor",
        "spa_ai_version": _spa_ai_version(),
        "repo": str(repo),
        "looms": looms_report,
        "summary": summary,
    }


def _print_doctor_human(report: dict) -> None:
    """Render the doctor report in human-readable form."""
    repo = report["repo"]
    summary = report["summary"]
    print(f"SPA AI doctor — {repo}")
    print(f"spa-ai {report['spa_ai_version']}")
    print(
        f"Scanned {summary['total_looms']} loom(s): "
        f"{summary['would_fire_count']} would fire, "
        f"{summary['clean_count']} already clean, "
        f"{summary['not_applicable_count']} not applicable."
    )
    print()

    would_fire = [L for L in report["looms"] if L["status"] == "would_fire"]
    clean = [L for L in report["looms"] if L["status"] == "clean"]
    not_app = [L for L in report["looms"] if L["status"] == "not_applicable"]

    if would_fire:
        print(f"WOULD FIRE ({len(would_fire)}):")
        # Order by finding_count descending (heuristic: more findings = higher leverage)
        for L in sorted(would_fire, key=lambda x: -x["finding_count"]):
            print(
                f"  • {L['loom_id']} (V{L['sakichi_vision_id']}) "
                f"— {L['finding_count']} finding(s) [{L.get('severity', '?')}]"
            )
            sf = L.get("sample_finding", {})
            print(f"      sample: {sf.get('target_path', '?')} — {sf.get('reason', '')}")
            print(f"      install: {L['install_command']}")
        print()

    if clean:
        print(f"ALREADY CLEAN ({len(clean)}):")
        for L in clean:
            print(f"  • {L['loom_id']} (V{L['sakichi_vision_id']}) — {L['reason']}")
        print()

    if not_app:
        print(f"NOT APPLICABLE ({len(not_app)}):")
        for L in not_app:
            print(f"  • {L['loom_id']} (V{L['sakichi_vision_id']}) — {L['reason']}")
        print()

    if would_fire:
        print("Suggested next steps (ordered by finding-count):")
        for i, L in enumerate(
            sorted(would_fire, key=lambda x: -x["finding_count"]), start=1
        ):
            print(f"  {i}. {L['install_command']}")
        print()


def _cmd_scan(args: argparse.Namespace) -> int:
    registry = default_registry()
    scanner = RepoScanner(registry)

    repo = Path(args.path).resolve()
    findings = scanner.scan(repo)

    if args.report_anonymous_usage:
        report_path = write_report(repo, findings, driver_profile=args.driver_profile)
        if args.format != "json":
            print(f"[telemetry] Wrote anonymized usage report to {report_path}")

    if args.format == "json":
        out: dict = {
            "schema_version": 1,
            "command": "scan",
            "spa_ai_version": _spa_ai_version(),
            "repo": str(repo),
            "findings": [
                {
                    "loom_id": f.loom_id,
                    "sakichi_vision_id": f.sakichi_vision_id,
                    "severity": f.severity,
                    "target_path": str(f.target_path),
                    "reason": f.reason,
                }
                for f in findings
            ],
        }
        if args.driver_profile is not None:
            out["driver_profile"] = args.driver_profile
        print(_json.dumps(out, indent=2))
        return 0

    if not findings:
        print("No missing looms detected.")
        return 0

    print(f"Found {len(findings)} missing loom(s) in {repo}:")
    print()
    for f in findings:
        print(f"  [{f.severity}] {f.loom_id} → {f.target_path} (V{f.sakichi_vision_id})")
        print(f"    Reason: {f.reason}")
        print(
            f"    To install: spa-ai propose {repo} --loom {f.loom_id}"
        )
        print()
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    repo = Path(args.path).resolve()
    if not repo.exists():
        print(f"Repo path does not exist: {repo}", file=sys.stderr)
        return 2
    if not (repo / ".git").exists():
        print(f"Not a git repo (no .git/ directory): {repo}", file=sys.stderr)
        return 2

    report = _build_doctor_report(repo)

    # Telemetry uses the same write_report path as scan; for doctor it
    # captures the would-fire findings (clean/not-applicable rows are
    # local-state info that doesn't need durable record).
    if args.report_anonymous_usage:
        registry = default_registry()
        scanner = RepoScanner(registry)
        findings = scanner.scan(repo)
        report_path = write_report(repo, findings, driver_profile=args.driver_profile)
        if args.format != "json":
            print(f"[telemetry] Wrote anonymized usage report to {report_path}")

    if args.driver_profile is not None:
        report["driver_profile"] = args.driver_profile

    if args.format == "json":
        print(_json.dumps(report, indent=2))
        return 0

    _print_doctor_human(report)
    return 0


def _cmd_propose(args: argparse.Namespace) -> int:
    registry = default_registry()

    if args.loom not in registry:
        registered = ", ".join(loom.loom_id for loom in registry.all()) or "(none)"
        print(
            f"Unknown loom: {args.loom!r}. Registered looms: {registered}",
            file=sys.stderr,
        )
        return 2

    repo = Path(args.path).resolve()
    if not repo.exists():
        print(f"Repo path does not exist: {repo}", file=sys.stderr)
        return 2
    if not (repo / ".git").exists():
        print(f"Not a git repo (no .git/ directory): {repo}", file=sys.stderr)
        return 2

    loom = registry.get(args.loom)
    findings = loom.detect(repo)

    if not findings:
        print(f"No findings for loom {args.loom!r}; nothing to propose.")
        return 0

    for finding in findings:
        patch = loom.propose_patch(finding, repo)
        target = repo / patch.target_path

        print(f"## Loom: {patch.loom_id}")
        print(f"## Target: {patch.target_path} (Sakichi vision {finding.sakichi_vision_id})")
        print(f"## Severity: {finding.severity}")
        print()
        print("## Patch contents preview:")
        print("---")
        print(patch.contents)
        print("---")
        print()
        print("## PR body draft:")
        print(patch.pr_body)
        print()

        if args.apply:
            if target.exists():
                print(
                    f"WARN: {target} already exists; refusing to overwrite. "
                    "Skipping this finding."
                )
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(patch.contents)
            print(f"WROTE: {target}")
        else:
            print(f"DRY-RUN: would write {target}. Re-run with --apply to write.")
    return 0


def _add_format_arg(parser: argparse.ArgumentParser) -> None:
    """Add --format=human|json to a subparser."""
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help=(
            "Output format. 'human' (default) is readable text; 'json' is "
            "structured per the v1 schema (schema_version=1) for CI "
            "integrators / IDE plugins / external tools."
        ),
    )


def _add_telemetry_arg(parser: argparse.ArgumentParser) -> None:
    """Add --report-anonymous-usage and --driver-profile to a subparser."""
    parser.add_argument(
        "--report-anonymous-usage",
        action="store_true",
        help=(
            "Opt-in: append an anonymized scan summary to "
            "~/.spa-ai/usage_reports.jsonl (or $SPA_AI_USAGE_REPORT_PATH). "
            "No network call — local-only. Captures: timestamp, "
            "sha256(git origin URL or path), spa-ai version, per-loom "
            "(id, vision, severity, target_path) summary. NOT captured: "
            "file contents, maintainer names, commit hashes."
        ),
    )
    parser.add_argument(
        "--driver-profile",
        type=str,
        default=None,
        help=(
            "Optional free-form label describing the user-population "
            "your app primarily serves (e.g., 'ageing-rural', "
            "'snow-zone-experienced', 'novice-urban', 'professional', "
            "'agricultural-forestry', 'mixed', or any developer-chosen "
            "string). Recorded verbatim in the usage report when "
            "--report-anonymous-usage is set. CLASS-LEVEL only — this "
            "is about your app's user-population, NOT about any "
            "individual user. Never cross-linked to identity."
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spa-ai",
        description=(
            "SPA AI — install Jidoka halts as PRs. "
            "A broken thread must stop the loom."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="Scan a repo for missing looms.")
    scan_p.add_argument("path", help="Path to a git working tree.")
    _add_format_arg(scan_p)
    _add_telemetry_arg(scan_p)
    scan_p.set_defaults(func=_cmd_scan)

    doctor_p = sub.add_parser(
        "doctor",
        help=(
            "Report each loom's status (would-fire / clean / not-applicable) "
            "with sample findings + ordered next-step suggestions."
        ),
    )
    doctor_p.add_argument("path", help="Path to a git working tree.")
    _add_format_arg(doctor_p)
    _add_telemetry_arg(doctor_p)
    doctor_p.set_defaults(func=_cmd_doctor)

    prop_p = sub.add_parser(
        "propose", help="Generate a patch for a specific loom."
    )
    prop_p.add_argument("path", help="Path to a git working tree.")
    prop_p.add_argument("--loom", required=True, help="Loom id to propose.")
    prop_p.add_argument(
        "--apply",
        action="store_true",
        help="Write the patch to disk (default: dry-run only).",
    )
    prop_p.set_defaults(func=_cmd_propose)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())

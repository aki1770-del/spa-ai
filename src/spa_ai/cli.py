"""SPA AI command-line interface.

Two subcommands in v0.1:

  spa-ai scan <path>
      Walk the repo, list missing looms with their Jidoka rationale.

  spa-ai propose <path> --loom <id> [--apply]
      Generate the patch for a specific loom. Without --apply, prints
      the patch (dry-run, the default per promises.md Promise 4 — the
      weaver owns the halt). With --apply, writes the file to disk.

The CLI deliberately omits `alert` and `submit` subcommands in v0.1.
Per commitments.md Commitment 1, SPA AI does not surface gaps as
alerts; per V65 Sekishō-idai, we ship one stone at a time.
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .registry import default_registry
from .scanner import RepoScanner


def _cmd_scan(args: argparse.Namespace) -> int:
    registry = default_registry()
    scanner = RepoScanner(registry)

    repo = Path(args.path).resolve()
    findings = scanner.scan(repo)

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
        patch = loom.propose_patch(finding)
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
    scan_p.set_defaults(func=_cmd_scan)

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

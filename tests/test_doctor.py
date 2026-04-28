"""Tests for `spa-ai doctor` command + `--format=json` on scan/doctor.

W3 of the SPA AI 3-week launch plan. doctor is the maintainer-side
introspection primitive (V77 genchi-genbutsu — the weaver goes to her
own place and observes what would change before any patch is proposed).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "spa_ai.cli", *args],
        capture_output=True,
        text=True,
    )


# -------- doctor: human-readable output --------

def test_doctor_human_output_on_synthetic_repo(synthetic_repo: Path) -> None:
    """synthetic_repo has no pre-commit-config + no CONTRIBUTING.md + no .py.

    Expected:
      - pre-commit-formatter: would_fire (no config)
      - pre-commit-formatter-rust: not_applicable (no Cargo.toml)
      - contributing-md: would_fire (no CONTRIBUTING.md)
      - silent-failure-grepper: not_applicable (no .py)
      - eof-newline: not_applicable (no config to extend)
    """
    result = _run_cli("doctor", str(synthetic_repo))
    assert result.returncode == 0, result.stderr
    out = result.stdout
    # Header + summary present
    assert "SPA AI doctor" in out
    assert "Scanned 6 loom(s)" in out
    assert "would fire" in out
    # Both gap looms appear in WOULD FIRE section
    assert "pre-commit-formatter" in out
    assert "contributing-md" in out
    # Inapplicable looms appear in NOT APPLICABLE section
    assert "NOT APPLICABLE" in out
    assert "no Cargo.toml" in out
    assert "no Python files" in out
    # Suggested next steps
    assert "Suggested next steps" in out
    assert f"spa-ai propose {synthetic_repo}" in out


def test_doctor_human_output_on_rust_repo(rust_repo: Path) -> None:
    """rust_repo has Cargo.toml (no .pre-commit-config / no CONTRIBUTING).

    Both pre-commit looms should fire (no config exists either way).
    """
    result = _run_cli("doctor", str(rust_repo))
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "pre-commit-formatter" in out
    assert "pre-commit-formatter-rust" in out
    assert "WOULD FIRE" in out


def test_doctor_human_output_when_clean(synthetic_repo: Path) -> None:
    """All gaps plugged → all looms either CLEAN or NOT_APPLICABLE; no WOULD FIRE section."""
    (synthetic_repo / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v4.6.0\n"
        "    hooks:\n"
        "      - id: end-of-file-fixer\n"
    )
    (synthetic_repo / "CONTRIBUTING.md").write_text("# Contributing\n")

    result = _run_cli("doctor", str(synthetic_repo))
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "0 would fire" in out
    # Suggested-next-steps section omitted when nothing would fire
    assert "Suggested next steps" not in out


def test_doctor_rejects_nonexistent_path(tmp_path: Path) -> None:
    bogus = tmp_path / "nonexistent"
    result = _run_cli("doctor", str(bogus))
    assert result.returncode == 2
    assert "does not exist" in result.stderr


def test_doctor_rejects_non_git_path(tmp_path: Path) -> None:
    notarepo = tmp_path / "notgit"
    notarepo.mkdir()
    result = _run_cli("doctor", str(notarepo))
    assert result.returncode == 2
    assert "Not a git repo" in result.stderr


# -------- doctor: JSON output --------

def test_doctor_json_schema_v2(synthetic_repo: Path) -> None:
    """Schema bumped 1 -> 2 for the LoomDignityFrame addition.

    All v1 fields remain present; new fields are additive
    (`weaver_classes_served` per loom + `weaver_class_coverage` block).
    """
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    assert result.returncode == 0, result.stderr
    obj = json.loads(result.stdout)
    assert obj["schema_version"] == 2
    assert obj["command"] == "doctor"
    assert "spa_ai_version" in obj
    assert obj["repo"] == str(synthetic_repo.resolve())
    assert "looms" in obj
    assert "summary" in obj
    assert "weaver_class_coverage" in obj


def test_doctor_json_loom_entries_have_required_fields(synthetic_repo: Path) -> None:
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    assert len(obj["looms"]) == 6
    for entry in obj["looms"]:
        assert "loom_id" in entry
        assert "sakichi_vision_id" in entry
        assert entry["status"] in ("would_fire", "clean", "not_applicable")
        assert "finding_count" in entry
        assert "reason" in entry
        # schema_version 2: per-loom weaver_classes_served is required
        # (defaults to [] for any loom that predates the slot).
        assert "weaver_classes_served" in entry
        assert isinstance(entry["weaver_classes_served"], list)


def test_doctor_json_summary_counts_correct(synthetic_repo: Path) -> None:
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    s = obj["summary"]
    assert s["total_looms"] == 6
    # Sum of statuses == total
    assert s["would_fire_count"] + s["clean_count"] + s["not_applicable_count"] == 6
    # synthetic_repo: 2 would fire (pre-commit-formatter + contributing-md);
    # 0 clean; 4 not_applicable (rust / silent-failure / eof / literature-drift-detector)
    assert s["would_fire_count"] == 2
    assert s["clean_count"] == 0
    assert s["not_applicable_count"] == 4


def test_doctor_json_would_fire_entry_includes_sample(synthetic_repo: Path) -> None:
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    fires = [L for L in obj["looms"] if L["status"] == "would_fire"]
    assert len(fires) >= 1
    for f in fires:
        assert "severity" in f
        assert "sample_finding" in f
        assert "target_path" in f["sample_finding"]
        assert "install_command" in f


# -------- scan: --format=json --------

def test_scan_json_output_schema(synthetic_repo: Path) -> None:
    result = _run_cli("scan", str(synthetic_repo), "--format=json")
    assert result.returncode == 0, result.stderr
    obj = json.loads(result.stdout)
    assert obj["schema_version"] == 1
    assert obj["command"] == "scan"
    assert "findings" in obj
    assert isinstance(obj["findings"], list)


def test_scan_json_finding_fields(synthetic_repo: Path) -> None:
    result = _run_cli("scan", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    assert len(obj["findings"]) >= 1
    for f in obj["findings"]:
        for required in ("loom_id", "sakichi_vision_id", "severity", "target_path", "reason"):
            assert required in f, f"missing field: {required}"


def test_scan_human_default_unchanged(synthetic_repo: Path) -> None:
    """Default human format must not regress from pre-W3 behavior."""
    result = _run_cli("scan", str(synthetic_repo))
    assert result.returncode == 0
    assert "{" not in result.stdout[:50]  # no JSON header
    assert "missing loom" in result.stdout


# -------- doctor: classification edge cases --------

def test_silent_failure_loom_clean_with_python_files(synthetic_repo: Path) -> None:
    """When .py files exist but have no silent-failure shapes, classify as 'clean'."""
    (synthetic_repo / "main.py").write_text(
        "def safe():\n"
        "    try:\n"
        "        return compute()\n"
        "    except Exception as e:\n"
        "        raise RuntimeError('failed') from e\n"
    )
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    sfg = next(L for L in obj["looms"] if L["loom_id"] == "silent-failure-grepper")
    assert sfg["status"] == "clean"
    assert "Python file" in sfg["reason"]


def test_eof_newline_clean_when_hook_present(synthetic_repo: Path) -> None:
    """When .pre-commit-config has the hook, eof-newline is 'clean' not 'not_applicable'."""
    (synthetic_repo / ".pre-commit-config.yaml").write_text(
        "repos:\n  - repo: x\n    hooks:\n      - id: end-of-file-fixer\n"
    )
    result = _run_cli("doctor", str(synthetic_repo), "--format=json")
    obj = json.loads(result.stdout)
    eof = next(L for L in obj["looms"] if L["loom_id"] == "eof-newline")
    assert eof["status"] == "clean"

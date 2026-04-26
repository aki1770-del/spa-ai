"""Tests for the W2-4 opt-in telemetry harness."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from spa_ai.looms.base import LoomFinding
from spa_ai.telemetry import build_report, write_report


def _make_finding(loom_id: str = "x", vision: int = 20) -> LoomFinding:
    return LoomFinding(
        loom_id=loom_id,
        target_path=Path("config.yaml"),
        reason="test reason",
        sakichi_vision_id=vision,
        severity="medium",
    )


def test_build_report_has_required_schema_fields(synthetic_repo: Path) -> None:
    report = build_report(synthetic_repo, [_make_finding()])
    assert report["schema_version"] == 1
    assert "timestamp" in report
    assert "spa_ai_version" in report
    assert "repo_hash" in report
    assert report["repo_hash"].startswith("sha256:")
    assert "findings" in report
    assert isinstance(report["findings"], list)


def test_build_report_summarizes_findings_without_leaking_contents(
    synthetic_repo: Path,
) -> None:
    findings = [
        _make_finding(loom_id="loom-a", vision=20),
        _make_finding(loom_id="loom-b", vision=14),
    ]
    report = build_report(synthetic_repo, findings)
    assert len(report["findings"]) == 2
    a = report["findings"][0]
    assert set(a.keys()) == {"loom_id", "sakichi_vision_id", "severity", "target_path"}
    # Make sure no extra fields slip in (no PII, no contents, no commit info).
    assert a["loom_id"] == "loom-a"
    assert a["sakichi_vision_id"] == 20


def test_repo_hash_is_consistent_across_calls(synthetic_repo: Path) -> None:
    r1 = build_report(synthetic_repo, [])
    r2 = build_report(synthetic_repo, [])
    assert r1["repo_hash"] == r2["repo_hash"]


def test_repo_hash_uses_git_origin_when_available(synthetic_repo: Path) -> None:
    """If git remote origin is set, hash that, not the path."""
    subprocess.run(
        ["git", "-C", str(synthetic_repo), "remote", "add", "origin", "https://example.com/x.git"],
        check=True,
        capture_output=True,
    )
    report = build_report(synthetic_repo, [])
    expected = "sha256:" + hashlib.sha256(b"https://example.com/x.git").hexdigest()
    assert report["repo_hash"] == expected


def test_repo_hash_falls_back_to_path_when_no_origin(synthetic_repo: Path) -> None:
    """No origin → hash the resolved path (still consistent across calls)."""
    report = build_report(synthetic_repo, [])
    expected = "sha256:" + hashlib.sha256(str(synthetic_repo.resolve()).encode()).hexdigest()
    assert report["repo_hash"] == expected


def test_write_report_appends_one_jsonl_line(synthetic_repo: Path, tmp_path: Path) -> None:
    target = tmp_path / "subdir" / "reports.jsonl"
    write_report(synthetic_repo, [_make_finding()], report_path=target)
    write_report(synthetic_repo, [_make_finding()], report_path=target)
    assert target.exists()
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    # Each line is valid JSON.
    for line in lines:
        obj = json.loads(line)
        assert obj["schema_version"] == 1


def test_write_report_creates_parent_dir(synthetic_repo: Path, tmp_path: Path) -> None:
    target = tmp_path / "deep" / "nested" / "path" / "reports.jsonl"
    assert not target.parent.exists()
    write_report(synthetic_repo, [], report_path=target)
    assert target.exists()
    assert target.parent.exists()


def test_write_report_honors_env_var(
    synthetic_repo: Path, tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "via_env.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    written = write_report(synthetic_repo, [])
    assert written == target
    assert target.exists()


def test_telemetry_is_off_by_default_in_cli(
    synthetic_repo: Path, tmp_path: Path, monkeypatch
) -> None:
    """CLI scan without --report-anonymous-usage must not write any file."""
    import subprocess as sp
    import sys as _sys

    target = tmp_path / "should_not_exist.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = sp.run(
        [_sys.executable, "-m", "spa_ai.cli", "scan", str(synthetic_repo)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "[telemetry]" not in result.stdout
    assert not target.exists()


def test_cli_scan_with_flag_writes_report(
    synthetic_repo: Path, tmp_path: Path, monkeypatch
) -> None:
    """CLI scan --report-anonymous-usage writes one JSONL line + prints notice."""
    import subprocess as sp
    import sys as _sys

    target = tmp_path / "with_flag.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = sp.run(
        [
            _sys.executable, "-m", "spa_ai.cli",
            "scan", str(synthetic_repo), "--report-anonymous-usage",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "[telemetry] Wrote anonymized usage report to" in result.stdout
    assert target.exists()
    obj = json.loads(target.read_text().strip())
    assert obj["schema_version"] == 1

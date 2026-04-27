"""Tests for the optional --driver-profile field on scan + doctor.

Per WOW v1 Convergence 2 (driver-class telemetry absent at every layer):
when an app developer uses spa-ai, she can declare which driver-class
her app's user-population primarily serves. Spa-ai records the
self-declared label verbatim. Class-level only — never about any
individual user.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from spa_ai.looms.base import LoomFinding
from spa_ai.telemetry import build_report, write_report


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "spa_ai.cli", *args],
        capture_output=True,
        text=True,
    )


def _make_finding() -> LoomFinding:
    return LoomFinding(
        loom_id="x",
        target_path=Path("config.yaml"),
        reason="test reason",
        sakichi_vision_id=20,
        severity="medium",
    )


# -------- build_report function --------


def test_build_report_omits_driver_profile_when_not_provided(synthetic_repo: Path) -> None:
    report = build_report(synthetic_repo, [_make_finding()])
    assert "driver_profile" not in report


def test_build_report_includes_driver_profile_when_provided(synthetic_repo: Path) -> None:
    report = build_report(synthetic_repo, [_make_finding()], driver_profile="ageing-rural")
    assert report["driver_profile"] == "ageing-rural"


def test_build_report_records_arbitrary_string_verbatim(synthetic_repo: Path) -> None:
    """Spa-ai does not validate or constrain driver_profile values."""
    report = build_report(synthetic_repo, [], driver_profile="my-custom-label-2026")
    assert report["driver_profile"] == "my-custom-label-2026"


# -------- write_report function --------


def test_write_report_includes_driver_profile_in_jsonl(
    synthetic_repo: Path, tmp_path: Path
) -> None:
    target = tmp_path / "report.jsonl"
    write_report(
        synthetic_repo,
        [_make_finding()],
        report_path=target,
        driver_profile="snow-zone-experienced",
    )
    obj = json.loads(target.read_text().strip())
    assert obj["driver_profile"] == "snow-zone-experienced"


def test_write_report_omits_driver_profile_when_not_provided(
    synthetic_repo: Path, tmp_path: Path
) -> None:
    target = tmp_path / "report.jsonl"
    write_report(synthetic_repo, [_make_finding()], report_path=target)
    obj = json.loads(target.read_text().strip())
    assert "driver_profile" not in obj


# -------- CLI scan + doctor --------


def test_scan_cli_with_driver_profile_writes_field(
    synthetic_repo: Path, tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "report.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli(
        "scan",
        str(synthetic_repo),
        "--report-anonymous-usage",
        "--driver-profile=novice-urban",
    )
    assert result.returncode == 0, result.stderr
    obj = json.loads(target.read_text().strip())
    assert obj["driver_profile"] == "novice-urban"


def test_scan_cli_without_driver_profile_omits_field(
    synthetic_repo: Path, tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "report.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli("scan", str(synthetic_repo), "--report-anonymous-usage")
    assert result.returncode == 0
    obj = json.loads(target.read_text().strip())
    assert "driver_profile" not in obj


def test_scan_json_output_includes_driver_profile_when_set(synthetic_repo: Path) -> None:
    result = _run_cli(
        "scan",
        str(synthetic_repo),
        "--format=json",
        "--driver-profile=professional",
    )
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["driver_profile"] == "professional"


def test_scan_json_output_omits_driver_profile_when_unset(synthetic_repo: Path) -> None:
    result = _run_cli("scan", str(synthetic_repo), "--format=json")
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert "driver_profile" not in obj


def test_doctor_json_output_includes_driver_profile_when_set(synthetic_repo: Path) -> None:
    result = _run_cli(
        "doctor",
        str(synthetic_repo),
        "--format=json",
        "--driver-profile=agricultural-forestry",
    )
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["driver_profile"] == "agricultural-forestry"


def test_doctor_with_telemetry_writes_driver_profile(
    synthetic_repo: Path, tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "report.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli(
        "doctor",
        str(synthetic_repo),
        "--report-anonymous-usage",
        "--driver-profile=mixed",
    )
    assert result.returncode == 0
    obj = json.loads(target.read_text().strip())
    assert obj["driver_profile"] == "mixed"

"""Tests for `spa-ai telemetry aggregate` and the underlying aggregator.

Covers the pure-function aggregator (`telemetry_aggregate.aggregate`)
and the CLI surface (`spa-ai telemetry aggregate`). The aggregator
reads only the local JSONL the harness wrote (PR #16 + PR #18); no
network call.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from spa_ai.telemetry_aggregate import aggregate, resolve_report_path


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "spa_ai.cli", *args],
        capture_output=True,
        text=True,
    )


def _record(
    *,
    driver_profile: str | None = None,
    findings: list[dict] | None = None,
    extra: dict | None = None,
) -> dict:
    """Build a single JSONL record matching the harness shape."""
    base: dict = {
        "schema_version": 1,
        "timestamp": "2026-04-28T00:00:00+00:00",
        "spa_ai_version": "0.4.0",
        "repo_hash": "sha256:deadbeef",
        "findings": findings if findings is not None else [],
    }
    if driver_profile is not None:
        base["driver_profile"] = driver_profile
    if extra:
        base.update(extra)
    return base


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")


# -------- resolve_report_path --------


def test_resolve_report_path_uses_explicit_argument(tmp_path: Path) -> None:
    target = tmp_path / "explicit.jsonl"
    assert resolve_report_path(target) == target


def test_resolve_report_path_honors_env_var(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "via_env.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    assert resolve_report_path() == target


# -------- aggregate (pure function) --------


def test_aggregate_missing_file_returns_empty_result(tmp_path: Path) -> None:
    target = tmp_path / "absent.jsonl"
    result = aggregate(report_path=target)
    assert result.record_count == 0
    assert result.skipped_line_count == 0
    assert result.by_driver_profile == {}
    assert result.by_loom_id == {}
    assert result.by_sakichi_vision_id == {}
    assert result.report_path == str(target)


def test_aggregate_empty_file_returns_zero_counts(tmp_path: Path) -> None:
    target = tmp_path / "empty.jsonl"
    target.write_text("")
    result = aggregate(report_path=target)
    assert result.record_count == 0
    assert result.skipped_line_count == 0


def test_aggregate_groups_per_profile(tmp_path: Path) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(driver_profile="ageing-rural"),
            _record(driver_profile="ageing-rural"),
            _record(driver_profile="novice-urban"),
        ],
    )
    result = aggregate(report_path=target)
    assert result.record_count == 3
    assert result.by_driver_profile == {"ageing-rural": 2, "novice-urban": 1}


def test_aggregate_buckets_missing_profile_under_unset(tmp_path: Path) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(),
            _record(driver_profile="professional"),
            _record(),
        ],
    )
    result = aggregate(report_path=target)
    assert result.by_driver_profile == {"(unset)": 2, "professional": 1}


def test_aggregate_counts_findings_per_loom_and_vision(tmp_path: Path) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(
                driver_profile="ageing-rural",
                findings=[
                    {
                        "loom_id": "pre-commit-formatter",
                        "sakichi_vision_id": 1,
                        "severity": "medium",
                        "target_path": ".pre-commit-config.yaml",
                    },
                    {
                        "loom_id": "contributing-md",
                        "sakichi_vision_id": 96,
                        "severity": "low",
                        "target_path": "CONTRIBUTING.md",
                    },
                ],
            ),
            _record(
                driver_profile="novice-urban",
                findings=[
                    {
                        "loom_id": "pre-commit-formatter",
                        "sakichi_vision_id": 1,
                        "severity": "medium",
                        "target_path": ".pre-commit-config.yaml",
                    },
                ],
            ),
        ],
    )
    result = aggregate(report_path=target)
    assert result.by_loom_id == {"pre-commit-formatter": 2, "contributing-md": 1}
    assert result.by_sakichi_vision_id == {"1": 2, "96": 1}


def test_aggregate_filter_restricts_loom_and_vision_axes(tmp_path: Path) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(
                driver_profile="ageing-rural",
                findings=[{"loom_id": "loom-A", "sakichi_vision_id": 22}],
            ),
            _record(
                driver_profile="novice-urban",
                findings=[{"loom_id": "loom-B", "sakichi_vision_id": 14}],
            ),
        ],
    )
    result = aggregate(report_path=target, driver_profile_filter="ageing-rural")
    # Per-profile axis is full so the filter's effect is visible.
    assert result.by_driver_profile == {"ageing-rural": 1, "novice-urban": 1}
    # Loom + vision axes only contain the matching record's contribution.
    assert result.record_count == 1
    assert result.by_loom_id == {"loom-A": 1}
    assert result.by_sakichi_vision_id == {"22": 1}


def test_aggregate_skips_malformed_lines(tmp_path: Path) -> None:
    target = tmp_path / "reports.jsonl"
    target.write_text(
        "\n".join(
            [
                json.dumps(_record(driver_profile="x", findings=[])),
                "not valid json",
                json.dumps({"no_findings_key": True}),  # missing findings
                json.dumps(_record(driver_profile="y", findings=[])),
                "",  # blank line ignored, not skipped-counted
            ]
        )
        + "\n"
    )
    result = aggregate(report_path=target)
    assert result.record_count == 2
    assert result.skipped_line_count == 2
    assert result.by_driver_profile == {"x": 1, "y": 1}


def test_aggregate_to_dict_orders_counts_descending(tmp_path: Path) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(driver_profile="a"),
            _record(driver_profile="b"),
            _record(driver_profile="b"),
            _record(driver_profile="b"),
            _record(driver_profile="c"),
            _record(driver_profile="c"),
        ],
    )
    payload = aggregate(report_path=target).to_dict()
    keys = list(payload["by_driver_profile"].keys())
    assert keys == ["b", "c", "a"]
    assert payload["schema_version"] == 1
    assert payload["command"] == "telemetry-aggregate"


# -------- CLI surface --------


def test_cli_telemetry_aggregate_human_message_when_no_file(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "absent.jsonl"
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli("telemetry", "aggregate")
    assert result.returncode == 0, result.stderr
    assert "No telemetry recorded yet" in result.stdout
    assert str(target) in result.stdout


def test_cli_telemetry_aggregate_json_returns_schema(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(
                driver_profile="ageing-rural",
                findings=[{"loom_id": "L1", "sakichi_vision_id": 22}],
            ),
        ],
    )
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli("telemetry", "aggregate", "--format=json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1
    assert payload["command"] == "telemetry-aggregate"
    assert payload["record_count"] == 1
    assert payload["by_driver_profile"] == {"ageing-rural": 1}
    assert payload["by_loom_id"] == {"L1": 1}
    assert payload["by_sakichi_vision_id"] == {"22": 1}


def test_cli_telemetry_aggregate_human_renders_blocks(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(
                driver_profile="ageing-rural",
                findings=[{"loom_id": "L1", "sakichi_vision_id": 22}],
            ),
        ],
    )
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli("telemetry", "aggregate")
    assert result.returncode == 0, result.stderr
    assert "By driver_profile" in result.stdout
    assert "By loom_id" in result.stdout
    assert "By sakichi_vision_id" in result.stdout
    assert "ageing-rural" in result.stdout
    assert "L1" in result.stdout


def test_cli_telemetry_aggregate_filter_flag(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "reports.jsonl"
    _write_jsonl(
        target,
        [
            _record(
                driver_profile="ageing-rural",
                findings=[{"loom_id": "L1", "sakichi_vision_id": 22}],
            ),
            _record(
                driver_profile="novice-urban",
                findings=[{"loom_id": "L2", "sakichi_vision_id": 14}],
            ),
        ],
    )
    monkeypatch.setenv("SPA_AI_USAGE_REPORT_PATH", str(target))
    result = _run_cli(
        "telemetry",
        "aggregate",
        "--format=json",
        "--driver-profile=ageing-rural",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["record_count"] == 1
    assert payload["by_loom_id"] == {"L1": 1}
    # Per-profile axis remains the full distribution.
    assert payload["by_driver_profile"] == {"ageing-rural": 1, "novice-urban": 1}

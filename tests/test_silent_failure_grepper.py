"""Tests for SilentFailureGrepperLoom."""
from __future__ import annotations

from pathlib import Path

from spa_ai.looms.silent_failure_grepper import SilentFailureGrepperLoom


def test_detect_returns_empty_on_clean_repo(synthetic_repo: Path) -> None:
    """No .py files = no findings."""
    loom = SilentFailureGrepperLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_flags_except_return_none(synthetic_repo: Path) -> None:
    """Pattern: except: return None — silent-swallow returning success-shape."""
    (synthetic_repo / "src.py").write_text(
        "def fetch(url):\n"
        "    try:\n"
        "        return urlopen(url).read()\n"
        "    except Exception:\n"
        "        return None\n"
    )
    loom = SilentFailureGrepperLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1
    assert findings[0].sakichi_vision_id == 14
    assert findings[0].target_path == Path(".spa-ai-silent-failures.md")


def test_detect_flags_except_pass(synthetic_repo: Path) -> None:
    """Pattern: except: pass — exception suppressed; no caller signal."""
    (synthetic_repo / "src.py").write_text(
        "def cleanup():\n"
        "    try:\n"
        "        os.remove('tmp')\n"
        "    except OSError:\n"
        "        pass\n"
    )
    loom = SilentFailureGrepperLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1


def test_detect_flags_except_return_empty_list(synthetic_repo: Path) -> None:
    """Pattern: except: return [] — success-shaped sentinel."""
    (synthetic_repo / "src.py").write_text(
        "def query(db):\n"
        "    try:\n"
        "        return db.execute('SELECT 1').fetchall()\n"
        "    except DatabaseError:\n"
        "        return []\n"
    )
    loom = SilentFailureGrepperLoom()
    findings = loom.detect(synthetic_repo)
    assert len(findings) == 1


def test_detect_does_not_flag_except_with_raise(synthetic_repo: Path) -> None:
    """Pattern: except → raise — NOT silent (re-raises after logging)."""
    (synthetic_repo / "src.py").write_text(
        "def fetch(url):\n"
        "    try:\n"
        "        return urlopen(url).read()\n"
        "    except Exception as e:\n"
        "        log.error(e)\n"
        "        raise\n"
    )
    loom = SilentFailureGrepperLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_does_not_flag_except_with_meaningful_value(synthetic_repo: Path) -> None:
    """Pattern: except → return <real-value> (not success-shape) — explicit fallback."""
    (synthetic_repo / "src.py").write_text(
        "def get_or_default(d, k):\n"
        "    try:\n"
        "        return d[k]\n"
        "    except KeyError:\n"
        "        return 'sentinel-value'\n"
    )
    loom = SilentFailureGrepperLoom()
    # 'sentinel-value' is not in success-shape literal list → no flag.
    assert loom.detect(synthetic_repo) == []


def test_detect_skips_venv_and_build_dirs(synthetic_repo: Path) -> None:
    """Vendored code in venv/ or build/ should not be scanned."""
    (synthetic_repo / "venv").mkdir()
    (synthetic_repo / "venv" / "lib.py").write_text(
        "def x():\n  try:\n    pass\n  except:\n    return None\n"
    )
    (synthetic_repo / "build").mkdir()
    (synthetic_repo / "build" / "x.py").write_text(
        "def x():\n  try:\n    pass\n  except:\n    return None\n"
    )
    loom = SilentFailureGrepperLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_skips_dot_dirs_except_github(synthetic_repo: Path) -> None:
    """Hidden dirs (e.g., .git, .pytest_cache) should be skipped, except .github."""
    (synthetic_repo / ".pytest_cache").mkdir()
    (synthetic_repo / ".pytest_cache" / "x.py").write_text(
        "def x():\n  try:\n    pass\n  except:\n    return None\n"
    )
    loom = SilentFailureGrepperLoom()
    assert loom.detect(synthetic_repo) == []


def test_propose_patch_writes_audit_artifact(synthetic_repo: Path) -> None:
    """Patch contents are the audit file; PR body cites V14."""
    (synthetic_repo / "src.py").write_text(
        "def fetch():\n"
        "    try:\n"
        "        return real_data()\n"
        "    except Exception:\n"
        "        return None\n"
    )
    loom = SilentFailureGrepperLoom()
    finding = loom.detect(synthetic_repo)[0]
    patch = loom.propose_patch(finding, synthetic_repo)

    # Audit file structure
    assert "SilentFailureGrepperLoom audit" in patch.contents
    assert "src.py" in patch.contents  # the flagged file appears
    assert "fetch" in patch.contents   # the flagged function name appears
    assert "Findings" in patch.contents

    # PR body Jidoka rationale
    assert "Why this halt" in patch.pr_body
    assert "Vision 14" in patch.pr_body or "vision 14" in patch.pr_body.lower()
    assert "Sakichi" in patch.pr_body
    assert "audit" in patch.pr_body.lower()


def test_propose_patch_does_not_write_to_disk(synthetic_repo: Path) -> None:
    """Loom contract: detect/propose_patch must not write."""
    (synthetic_repo / "src.py").write_text(
        "def x():\n  try:\n    a()\n  except:\n    return None\n"
    )
    loom = SilentFailureGrepperLoom()
    finding = loom.detect(synthetic_repo)[0]
    _ = loom.propose_patch(finding, synthetic_repo)
    assert not (synthetic_repo / ".spa-ai-silent-failures.md").exists()


def test_three_slot_vision_attribution() -> None:
    """3-slot schema per base.py contract."""
    loom = SilentFailureGrepperLoom()

    assert loom.sakichi_vision_id == 14
    assert isinstance(loom.method_vision_ids, list)
    assert isinstance(loom.stance_vision_ids, list)
    assert all(1 <= v <= 100 for v in loom.method_vision_ids)
    assert all(1 <= v <= 100 for v in loom.stance_vision_ids)
    assert 77 in loom.method_vision_ids   # genchi-genbutsu — walks repo .py files
    assert 22 in loom.stance_vision_ids   # loom-serves-weaver
    assert 100 in loom.stance_vision_ids  # equal-dignity for every weaver

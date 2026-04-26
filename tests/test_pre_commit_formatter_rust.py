"""Tests for PreCommitFormatterRustLoom."""
from __future__ import annotations

from pathlib import Path

from spa_ai.looms.pre_commit_formatter_rust import PreCommitFormatterRustLoom


def test_detect_returns_finding_in_rust_repo_without_config(rust_repo: Path) -> None:
    loom = PreCommitFormatterRustLoom()
    findings = loom.detect(rust_repo)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.loom_id == "pre-commit-formatter-rust"
    assert finding.target_path == Path(".pre-commit-config.yaml")
    assert finding.sakichi_vision_id == 20
    assert finding.severity == "medium"
    assert "Cargo.toml" in finding.reason


def test_detect_returns_empty_in_non_rust_repo(synthetic_repo: Path) -> None:
    """Non-Rust repos must not trigger this loom (no Cargo.toml)."""
    loom = PreCommitFormatterRustLoom()
    assert loom.detect(synthetic_repo) == []


def test_detect_returns_empty_when_yaml_already_present(rust_repo: Path) -> None:
    (rust_repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    loom = PreCommitFormatterRustLoom()
    assert loom.detect(rust_repo) == []


def test_detect_returns_empty_when_yml_already_present(rust_repo: Path) -> None:
    (rust_repo / ".pre-commit-config.yml").write_text("repos: []\n")
    loom = PreCommitFormatterRustLoom()
    assert loom.detect(rust_repo) == []


def test_propose_patch_includes_rustfmt_hook(rust_repo: Path) -> None:
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    patch = loom.propose_patch(finding, rust_repo)

    # Promise 2: every halt cites its Jidoka rationale.
    assert "Why this halt" in patch.pr_body
    assert "Sakichi" in patch.pr_body
    assert "Vision 20" in patch.pr_body or "vision 20" in patch.pr_body.lower()

    # Rust-specific: rustfmt must be wired in; clippy must NOT be (V20).
    assert "rustfmt" in patch.contents
    assert "cargo fmt" in patch.contents
    assert "clippy" not in patch.contents.lower() or "# " in patch.contents
    # PR body must explain why clippy is excluded.
    assert "clippy" in patch.pr_body.lower()
    assert "ci" in patch.pr_body.lower()


def test_propose_patch_includes_baseline_hooks(rust_repo: Path) -> None:
    """Rust loom inherits the language-agnostic baseline + adds rustfmt."""
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    patch = loom.propose_patch(finding, rust_repo)
    assert "trailing-whitespace" in patch.contents
    assert "end-of-file-fixer" in patch.contents
    assert "check-yaml" in patch.contents
    assert "check-merge-conflict" in patch.contents
    assert "check-added-large-files" in patch.contents


def test_propose_patch_does_not_write_to_disk(rust_repo: Path) -> None:
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    _ = loom.propose_patch(finding, rust_repo)
    assert not (rust_repo / ".pre-commit-config.yaml").exists()


def test_three_slot_vision_attribution() -> None:
    """Per base.py contract: 3 vision-attribution slots required.

    sakichi_vision_id (FAILURE-MODE) + method_vision_ids (HOW the loom
    works) + stance_vision_ids (HOW the weaver is treated). Cross-
    reference 5-Whys finding 2026-04-25: singular attribution is a
    category error — the 100 visions form a graph.
    """
    loom = PreCommitFormatterRustLoom()

    assert loom.sakichi_vision_id == 20
    assert isinstance(loom.method_vision_ids, list)
    assert isinstance(loom.stance_vision_ids, list)
    assert len(loom.method_vision_ids) >= 1
    assert len(loom.stance_vision_ids) >= 1
    assert all(1 <= v <= 100 for v in loom.method_vision_ids)
    assert all(1 <= v <= 100 for v in loom.stance_vision_ids)

    # V77 (genchi genbutsu) — Rust loom walks the actual repo for Cargo.toml.
    assert 77 in loom.method_vision_ids
    # V22 (loom-serves-weaver) — every loom must hold this stance.
    assert 22 in loom.stance_vision_ids
    # V25 (autonomation = liberation not replacement) — the anti-replacement
    # declaration. Per cross-reference 5-Whys 2026-04-25: belongs in every
    # loom's stance slot. The clippy-in-CI / rustfmt-at-commit split is V25
    # in concrete: the loom liberates the maintainer from formatting-drift
    # vigilance without replacing their judgment on lint policy.
    assert 25 in loom.stance_vision_ids


def test_rustfmt_hook_uses_check_flag(rust_repo: Path) -> None:
    """The rustfmt hook must use --check, not the mutating form.

    Regression guard: an earlier version of this loom shipped
    `entry: cargo fmt --` (no --check), which silently REWRITES files
    and exits 0 on success. That makes the hook a no-op as a halt —
    the opposite of what the loom is meant to do. This test was added
    after the embedded-hal dogfood audit (2026-04-25) caught the
    defect via the external_pr_audit swarm (F-5).

    Per Sakichi vision 20: a halt that does not actually halt is a
    burden wearing the costume of a machine.
    """
    loom = PreCommitFormatterRustLoom()
    finding = loom.detect(rust_repo)[0]
    patch = loom.propose_patch(finding, rust_repo)
    assert "cargo fmt -- --check" in patch.contents, (
        "rustfmt hook must invoke 'cargo fmt -- --check' so the hook halts "
        "on formatting drift instead of silently mutating files."
    )
    # And the body must NOT make false claims about the hook's behaviour.
    body_lower = patch.pr_body.lower()
    assert "staged `.rs` files" not in patch.pr_body, (
        "PR body must not claim the hook 'runs only on staged .rs files' — "
        "with `pass_filenames: false` and `cargo fmt`, the hook checks the "
        "whole workspace."
    )
    halt_phrases = ("does not mutate", "do not mutate", "does not modify", "halt")
    assert any(phrase in body_lower for phrase in halt_phrases), (
        "PR body must explain that --check halts rather than mutating files."
    )

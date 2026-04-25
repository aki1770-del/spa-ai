# Changelog

All notable changes to SPA AI will be documented here.

## [Unreleased] — Phase 1 MVP skeleton

### Added (2026-04-25)
- `pyproject.toml` — Python 3.11+ project; zero runtime deps in v0.1
  (deterministic looms only; Anthropic SDK lands when first
  LLM-driven loom does, per principles.md V65 Sekishō-idai).
- `src/spa_ai/` — package skeleton: `config`, `scanner`, `registry`,
  `cli`, `looms/{base,pre_commit_formatter}`.
- `src/spa_ai/looms/base.py` — `Loom` Protocol + `LoomFinding`,
  `LoomPatch` dataclasses; explicit contract that detect() and
  propose_patch() must not write to disk.
- `src/spa_ai/looms/pre_commit_formatter.py` — first loom; detects
  missing `.pre-commit-config.yaml` (or `.yml`); proposes a
  five-hook default config + Jidoka-rationale PR body. Cites Sakichi
  vision 20 (stopping must be cheap).
- `src/spa_ai/registry.py` — `LoomRegistry` enforces unique loom_id
  + valid sakichi_vision_id (1..100, per commitments.md
  Commitment 5).
- `src/spa_ai/scanner.py` — walks repo; raises clearly on
  non-existent or non-git paths.
- `src/spa_ai/cli.py` — `spa-ai scan` + `spa-ai propose` (dry-run by
  default; `--apply` writes; refuses to overwrite existing files).
  No `alert` or `submit` subcommands per Promise 3 + Commitment 1.
- `tests/` — pytest suite covering loom detect/propose, scanner,
  registry, and CLI end-to-end including dry-run/apply paths.
- `README.md` — install + run sections.

### Phase 1 step coverage (per launch_plan.md)
- Step 11: monorepo layout (CLI-only per Komada 2026-04-25 directive).
- Step 12: Python 3.11+ chosen.
- Step 14: `SPAConfig` class (minimal v0.1 surface).
- Step 15: `PreCommitFormatterLoom` shipped (first loom).
- Step 17: `RepoScanner` shipped.
- Step 18: `LoomRegistry` shipped.
- Step 19: `--dry-run` semantics (default; `--apply` to write).
- Step 20: `spa-ai scan <repo>` shipped.
- Step 21: `spa-ai propose <repo> --loom <id>` shipped.
- Step 22: PR-body template with "Why this halt" + "What you do" +
  rollback + provenance sections.

### Decisions ratified (2026-04-25)
- **License: MIT** (Komada decision). LICENSE file added at repo root;
  `pyproject.toml` `license` field updated. Apache 2.0 was the
  alternative; MIT chosen for permissive simplicity.
- **PyPI name reservation**: deferred — not now. Revisit at Phase 5
  publish time.

### Phase 1 deferred to next slice
- Step 13: Anthropic SDK vendoring (no LLM-driven loom yet, so no dep).
- Step 16: `ContributingMdLoom` (D-VGC158-4 evidence).
- Step 23: Dockerfile.
- Step 24: telemetry surface.
- Step 25: end-to-end test against a real upstream clone (gated on
  ContributingMdLoom shipping).

### Phase 1 slice 2 — Rust language specialization (2026-04-25)

Per the Python-vs-Rust SWOT pass (Komada decision 2026-04-25): Rust
first. Three reasons stacked: (1) verified detection rate in our
portfolio (embassy-rs / embedded-hal / smoltcp lack pre-commit
configs; Python equivalents often already have them); (2) doctrinal
continuity to D3 driver-safety chain via embedded Rust; (3) higher
maintainer-pushback risk in Rust = better proving ground at small
scale (V20 cheap-stop).

- `src/spa_ai/looms/pre_commit_formatter_rust.py` — second loom.
  Detects `Cargo.toml` at root + missing `.pre-commit-config.{yaml,yml}`.
  Proposes the language-agnostic five-hook baseline plus a local
  `rustfmt` hook (uses `cargo fmt --`; respects project
  `rustfmt.toml`). Cites V20.
- **clippy intentionally omitted** from the pre-commit config —
  recompiles, violates V20 ("stopping must be cheap, or operators
  will hesitate"). PR body explains this and recommends clippy
  belongs in CI; provides a reasonable CI snippet.
- Loom architecture: separate class (`PreCommitFormatterRustLoom`)
  rather than internal language detection inside the base loom.
  V65 single-responsibility per loom — the registry now has two
  entries; the human picks `--loom <id>` at propose time.
- `tests/conftest.py` — new `rust_repo` fixture (synthetic Rust
  crate: `Cargo.toml` + `src/lib.rs` + git init).
- `tests/test_pre_commit_formatter_rust.py` — 7 tests covering
  detect/propose semantics + Rust-specific assertions (rustfmt
  present, clippy explicitly absent + explained in PR body,
  baseline hooks inherited).
- `tests/test_scanner.py` — added `test_scanner_in_rust_repo_returns_both_pre_commit_findings`
  to confirm both pre-commit looms fire on a Rust repo (CLI human
  picks which to install).
- `tests/test_registry.py` — added `test_default_registry_size_is_two`
  guard so future loom additions force a CHANGELOG entry.

Step 16 (`ContributingMdLoom`) intentionally still deferred — V65
says one stone at a time, and the language-specialization stone
needed to land first to validate the registry-grows-naturally
pattern before broadening.

### Phase 1 step coverage update
- Step 15 (PreCommitFormatterLoom): shipped in slice 1.
- Step 15-bis (PreCommitFormatterRustLoom): shipped in slice 2.
- Steps 11, 12, 14, 17, 18, 19, 20, 21, 22: shipped in slice 1.
- All 35 tests pass; `ruff check` clean.

## [Unreleased — superseded] Phase 0 identity lock

### Added (2026-04-23)
- Initial repository + README
- `docs/manifesto.md` — product manifesto (draft; human author pending)
- `docs/promises.md` — five load-bearing promises
- `docs/anti_patterns.md` — eight patterns SPA AI must never become
- `docs/mission.md` — 200-word mission statement
- `docs/demo_script.md` — 60-second demo script
- `docs/commitments.md` — operational commitments
- `docs/sakichi_100_visions.md` — doctrinal source (100 Sakichi visions + SPA definition)
- `docs/launch_plan.md` — 100-step implementation plan across 6 phases
- `docs/pain_points.md` — pointer to launch_plan Part 1 (30 pain points catalog)

### Phase 0 commitments honored
- Step 1: name frozen as SPA AI; repo reserved at github.com/aki1770-del/spa-ai
- Step 2: manifesto drafted
- Step 3: Sakichi 100 visions referenced and copied in
- Step 4: five load-bearing promises defined
- Step 5: anti-patterns list enumerated
- Step 6: 200-word mission statement drafted
- Step 7: 60-second demo script drafted
- Step 8: 100% PR-generation commitment documented
- Step 9: contextual disclosure commitment documented
- Step 10: "weaver" not "user" language locked in

### Phase 0 deferred
- Domain reservations (spa-ai.dev, spa-ai.com) — requires Komada purchase
- License selection — deferred to Phase 1 start
- All external-facing copy remains DRAFT pending human author per D-VGC148

---

No released versions yet. First version ships at end of Phase 1.

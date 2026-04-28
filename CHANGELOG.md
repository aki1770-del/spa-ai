# Changelog

All notable changes to SPA AI will be documented here.

## [Unreleased]

### Added

#### `release.yml` — PyPI Trusted Publishing workflow (this PR)

- New workflow `.github/workflows/release.yml` triggers on tag push
  (`v*`) and publishes to PyPI via OIDC Trusted Publishing
  (`pypa/gh-action-pypi-publish@release/v1`). No long-lived API
  tokens are stored in repository secrets.
- Three jobs: `test` (mirrors `ci.yml`'s 3.11 + 3.12 matrix verbatim
  to satisfy OPS-RULE-042 on the tag-push commit), `build`
  (`python -m build --sdist --wheel`), `publish` (downloads the
  artifact, mints the OIDC token, uploads to PyPI). `id-token: write`
  is scoped to the publish job only.
- The `publish` job runs in the `pypi` environment so the publisher
  surfaces in the PyPI dashboard config and required-reviewers /
  branch-protection can be added later without editing the workflow.
- README gets a new **Releasing** section documenting the
  bump → CHANGELOG → push → tag → publish flow plus the one-time
  PyPI dashboard pending-publisher fields the maintainer must enter.

#### Why this exists

- spa-ai 0.4.0 was published manually on 2026-04-27 because PyPI
  deprecated username/password and the maintainer pasted an API
  token by hand at release time. That manual step is the
  load-bearing-by-accident gate — exactly the V20 cheap-stop /
  V14 silent-failure-anti-Jidoka pattern this repo's product was
  built to catch in OTHER repos. We eat our own dog food.
- Per OPS-RULE-041 (Andon-must-produce-loom): pulling the cord on
  manual-publish friction obligates installing the loom that
  catches the same friction next time. This workflow IS that loom.
- Per OPS-RULE-042 (CI-Before-Release Gate): the `test` job
  re-establishes the green-CI invariant on the tag-push SHA before
  any version is published.

#### `release.yml` 3-slot vision

- `sakichi=14` (silent-failure — the manual token paste was a
  human-vigilance gate; the loom replaces it with an automated
  cryptographic identity proof)
- `method=[77, 18, 99]` (genchi-genbutsu the actual PyPI publish
  protocol / 5-Whys to the absent loom / write-it-down as workflow
  yaml)
- `stance=[22, 96, 100]` (loom-serves-weaver — protects future-self
  + future-contributor from token-rotation drift / V96
  maintainers-as-edge-developers — the maintainer of this repo
  deserves the same Jidoka standard we ship to others / V100
  equal-dignity)

---

#### `spa-ai telemetry aggregate` — local-only aggregation report (this PR)

- New subcommand: `spa-ai telemetry aggregate [--driver-profile <label>] [--format=human|json]`.
  Reads the local JSONL the harness wrote (`~/.spa-ai/usage_reports.jsonl`
  by default, or `$SPA_AI_USAGE_REPORT_PATH`) and reports per-axis
  counts: by `driver_profile`, by `loom_id`, by `sakichi_vision_id`.
- `--driver-profile <label>` filters per-loom and per-vision counts to
  records matching the label. The per-profile axis stays full so the
  filter's effect is visible. Records that lack the field bucket under
  `(unset)`.
- **No network call.** Aggregation reads only the local JSONL the user
  opted into writing. Promise 4 (local-only in v0.4) preserved; the
  user can `cat` the file at any time.
- Robust to a partially-malformed file: lines that aren't valid JSON
  or that lack `findings` are counted in `skipped_line_count` and
  otherwise ignored — never raises.
- New module `src/spa_ai/telemetry_aggregate.py`. Pure-function
  `aggregate(report_path=None, driver_profile_filter=None)` returns
  an `AggregateResult` dataclass; CLI layer formats it.
- JSON output follows the established `schema_version: 1` precedent
  (PR #17). Stable fields: `report_path`, `record_count`,
  `skipped_line_count`, `by_driver_profile`, `by_loom_id`,
  `by_sakichi_vision_id` (each axis ordered by count descending then
  key ascending).
- Tests: `tests/test_telemetry_aggregate.py` — 14 tests covering
  missing file, empty file, per-axis grouping, missing-profile bucket,
  filter behavior, malformed-line skipping, count ordering, and the
  CLI surface in both human and JSON modes.

#### `spa-ai telemetry aggregate` 3-slot vision

- `sakichi=99` (write-the-decision-down — the report IS the local
  decision record of which looms fired where, by which user-population
  class, in what shape)
- `method=[77, 99]` (genchi-genbutsu reads the actual local file /
  write-it-down structured for the maintainer)
- `stance=[22, 96, 100]` (loom-serves-weaver — surfaces her own data
  for her own calibration / V96 maintainers-as-edge-developers /
  equal-dignity — same opt-in substrate her downstream tools would
  expect)

---

#### Optional `--driver-profile` field on `scan` + `doctor` (prior PR #18)

- Adds `--driver-profile <label>` CLI flag to both `scan` and `doctor`.
  The label is a free-form string (e.g., `ageing-rural`,
  `snow-zone-experienced`, `novice-urban`, `professional`,
  `agricultural-forestry`, `mixed`, or any developer-chosen string).
  Spa-ai records the label verbatim; no validation, no enum constraint.
- When `--report-anonymous-usage` is also passed, the label is included
  as an additional field (`driver_profile`) in the JSONL telemetry record.
- When `--format=json` is passed (without telemetry), the label is
  included in the JSON output document.
- Class-level only — describes the app's user-population, NOT any
  individual user. Never cross-linked to identity.
- `build_report` and `write_report` in `src/spa_ai/telemetry.py` accept
  optional `driver_profile` keyword.
- Tests: `tests/test_driver_profile_field.py` — 11 tests covering
  build_report omission/inclusion, write_report JSONL output, scan +
  doctor CLI in both telemetry-write mode and JSON-output mode.

#### `spa-ai doctor` + `--format=json` — W3 (prior PR)

- **`spa-ai doctor <repo>`** — new subcommand. One-command introspection for
  the maintainer about her own repo. Reports each loom's status as
  `would_fire` / `clean` / `not_applicable`, with sample finding + ordered
  next-step suggestions for the would-fire set.
  - V77 primitive (the weaver goes to her own place — the repo — and
    observes what would change before any patch is proposed).
  - Distinguishes "already clean" (loom ran, nothing to do) from
    "not applicable" (loom can't apply here, e.g., Rust loom on a
    non-Rust repo) so the maintainer's mental model isn't muddled.
- **`--format=json`** — added to both `scan` and `doctor`. Structured output
  per `schema_version: 1` for CI integrators / IDE plugins / external tools.
  - Schema fields: `schema_version`, `command`, `spa_ai_version`, `repo`,
    `findings` (scan) or `looms` + `summary` (doctor).
- **Telemetry parity**: `--report-anonymous-usage` works on `doctor` too
  (same JSONL append shape as `scan`).
- New module: `src/spa_ai/cli.py` — `_cmd_doctor`, `_build_doctor_report`,
  `_classify_loom_status`, `_print_doctor_human`, plus shared `_add_format_arg`
  / `_add_telemetry_arg` helpers.
- Tests: `tests/test_doctor.py` — 14 tests covering human output, JSON
  output schema, summary counts, classification edge cases (silent-failure
  clean-with-Python vs not-applicable-without-Python; eof-newline
  clean-with-hook vs not-applicable-without-config).

#### `spa-ai doctor` + `--format=json` 3-slot vision

- `sakichi=77` (genchi-genbutsu — the maintainer goes to her own repo
  and observes; doctor surfaces what's there without imposing)
- `method=[77, 99]` (read repo state directly / write-it-down: structured
  output enables external tools)
- `stance=[22, 25, 96, 100]` (loom-serves-weaver — doctor serves her
  introspection, not our scan-counts / autonomation = liberation, not
  surveillance / V96 maintainers-as-edge-developers — doctor treats her
  as the decider / equal-dignity)

---

#### Opt-in telemetry harness — W2-4 (prior PR #16)

- `src/spa_ai/telemetry.py` — new module. `build_report(repo_root, findings)`
  is a pure function returning the report dict (schema_version, timestamp,
  spa_ai_version, repo_hash, findings list). `write_report(...)` appends one
  JSON line to `~/.spa-ai/usage_reports.jsonl` (or
  `$SPA_AI_USAGE_REPORT_PATH` if set).
- `src/spa_ai/cli.py` — `spa-ai scan` accepts `--report-anonymous-usage`
  (default OFF). When passed, the harness appends one JSONL record and
  prints `[telemetry] Wrote anonymized usage report to <path>`. Without
  the flag, no file is touched.
- **No network call in v0.4.** The file is local-only; the user can
  inspect / delete it at any time. A future slice will add an explicit
  `spa-ai telemetry submit` subcommand for users who choose to upload.
- Repo identifier: sha256 of `git remote get-url origin` if present,
  else sha256 of the resolved repo path. Same repo hashes consistently
  across scans on the same host without disclosing the path.
- Captured per finding: `loom_id`, `sakichi_vision_id`, `severity`,
  `target_path` (repo-relative). Not captured: file contents, maintainer
  names, commit hashes, host filesystem paths, environment variables.
- Tests: `tests/test_telemetry.py` — 10 tests covering the report shape,
  hash consistency, env-var override, parent-dir creation, and the CLI's
  off-by-default + on-with-flag behavior.

#### Telemetry harness 3-slot vision

- `sakichi=99` (write-the-decision-down — usage data IS the decision
  record of which looms fired where, in what shape)
- `method=[77, 99]` (genchi-genbutsu walks the actual repo + write-down)
- `stance=[22, 25, 100]` (loom-serves-weaver via opt-in / autonomation =
  liberation not surveillance / equal-dignity — same opt-in standard
  for our own usage capture as we'd ask of any tool)

---

## [0.3.0] — 2026-04-26

Loom Protocol extension + three new looms. Registry size grows 2 → 5.
The Sakichi 100 visions are no longer covered only by V20 (cheap-stop) and
V25 (autonomation) — V14 (silent-failure-anti-Jidoka), V15 (poka-yoke),
and V96 (maintainers-are-edge-developers) now have dedicated looms.

### Added

#### Loom Protocol — `propose_patch` extended with `repo_root` (PR [#13](https://github.com/aki1770-del/spa-ai/pull/13))

- `src/spa_ai/looms/base.py` — `Loom.propose_patch` signature is now
  `propose_patch(self, finding: LoomFinding, repo_root: Path) -> LoomPatch`.
  The new `repo_root` is the absolute path to the repository the loom
  scanned in `detect()`. Looms that **modify** an existing file (read,
  merge, emit) need this to read at patch-compose time. Looms that
  always **create** a new file can ignore `repo_root`.
- Reading from `repo_root` is permitted; writing remains forbidden —
  disk writes are restricted to the CLI `--apply` path per
  `promises.md` Promise 4.
- All four pre-existing looms updated to accept the new signature
  (their bodies unchanged — they ignore `repo_root`). The first user
  of the new parameter is `EofNewlineLoom` (below).
- `src/spa_ai/cli.py` — passes `repo` through to `propose_patch`.
- This is a minor, source-compatible change for anyone using the
  shipped looms; it would be a breaking change for any external loom
  authors implementing the Protocol — but no external loom authors
  exist yet, so the cost of the extension is borne entirely by the
  internal codebase.

#### EofNewlineLoom — V15 poka-yoke (PR [#13](https://github.com/aki1770-del/spa-ai/pull/13))

- `src/spa_ai/looms/eof_newline.py` — new loom. Detects the case
  where the maintainer **has** a `.pre-commit-config.yaml` (or `.yml`)
  but did not include the `end-of-file-fixer` hook. Reads the existing
  config from disk, appends the hook block, returns merged contents.
- Distinct from `PreCommitFormatterLoom` — that loom handles "no
  pre-commit-config at all"; this loom handles "config exists but
  lacks one specific hook."
- 3-slot vision attribution: `sakichi=15`, `method=[77, 18, 99]`,
  `stance=[22, 25, 32, 100]`.
- First user of the extended Loom Protocol — proves the new
  `propose_patch(finding, repo_root)` signature on a real read-merge
  flow.

#### SilentFailureGrepperLoom — V14 silent-failure-anti-Jidoka (PR [#12](https://github.com/aki1770-del/spa-ai/pull/12))

- `src/spa_ai/looms/silent_failure_grepper.py` — AST-based scanner
  for silent-failure shapes in Python. Patterns detected:
  `except: return None/[]/False/""/0`, `except: pass`,
  `except: pass; return value`. The patch IS the audit artifact
  (`.spa-ai-silent-failures.md`) — not an automated rewrite of
  caller code, because catching-then-swallowing is a deliberate
  weaver decision that a tool should surface, not erase.
- Skips `venv/.venv/build/dist/__pycache__` + dot-dirs except `.github`.
- 3-slot vision attribution: `sakichi=14`, `method=[77, 18, 99]`,
  `stance=[22, 25, 32, 100]`.

#### ContributingMdLoom — V96 maintainers-are-edge-developers (PR [#11](https://github.com/aki1770-del/spa-ai/pull/11))

- `src/spa_ai/looms/contributing_md.py` — detects missing
  `CONTRIBUTING.md` at root, `.github/`, or `docs/`. Proposes a
  minimal template adapted from `promises.md` (5-promise pattern).
- 3-slot vision attribution: `sakichi=96`, `method=[77, 18, 99]`,
  `stance=[22, 25, 32, 96, 100]` (V96 in BOTH slots — the failure
  mode AND the stance toward the maintainer are both V96-anchored).
- Built per Komada-voice override of the why-first synthesis verdict
  (option (c)); override record at
  `outputs/governance_transformation/komada_override_why_first_w2_3_2026_04_26.md`.

### Registry

- `default_registry()` size: 4 → 5. New shipping list:
  1. `PreCommitFormatterLoom` (V20)
  2. `PreCommitFormatterRustLoom` (V20)
  3. `ContributingMdLoom` (V96)
  4. `SilentFailureGrepperLoom` (V14)
  5. `EofNewlineLoom` (V15)

### Tests

- 58 tests passing (was 38 in 0.2.0; +20 from the three new looms +
  Protocol-extension regression guards + scanner gap-coverage updates).
- `tests/test_eof_newline.py` — 8 tests including the no-disk-write
  contract regression and the merge-preserves-existing-hooks check.
- `tests/test_silent_failure_grepper.py` — covers all four silent-
  failure shapes + the venv-skip behavior.
- `tests/test_contributing_md.py` — covers all three search paths +
  the case-insensitivity check.

### Behavior change vs 0.2.0

- `RepoScanner.scan()` will now return more findings on most repos
  because three new detectors run. This is the intended growth of
  the Sakichi loom catalog (V65 Sekishō-idai — one stone at a time).
- The CLI `propose --loom <id>` UX is unchanged. Each loom is opt-in
  per id; `scan` reports all gaps, the human picks which to install.

### Deferred to next slice

- W2-4: opt-in telemetry harness (`spa-ai scan --report-anonymous-usage`).
- W2-7: external_pr_audit re-run on each new loom's first dogfood PR.
- Sub-agent fleet (VAA's 4 sensors) — depends on Path B Step 3 bylaws.

---

## [0.2.0] — 2026-04-26

First versioned release. Phase 1 MVP skeleton + Phase 0.5 doctrinal patches +
3-slot vision attribution schema.

### Added (2026-04-25 to 2026-04-26)

#### Loom Protocol — 3-slot vision attribution schema (PR [#6](https://github.com/aki1770-del/spa-ai/pull/6))

- `src/spa_ai/looms/base.py` — `Loom` Protocol extended with two new
  vision-attribution slots:
  - `method_vision_ids: list[int]` — METHOD visions (HOW the loom does
    its work)
  - `stance_vision_ids: list[int]` — STANCE visions (HOW THE WEAVER
    IS TREATED by the loom)
- Both production looms annotated:
  - `sakichi_vision_id = 20` (cheap-stop — failure-mode anchor; existing)
  - `method_vision_ids = [77, 18, 99]` (V77 genchi-genbutsu walks the
    repo; V18 5-Whys-mechanism in PR body; V99 write-the-decision-down
    via the patch itself)
  - `stance_vision_ids = [22, 25, 32, 100]` (V22 loom-serves-weaver +
    V25 autonomation = liberation not replacement + V32 katei-teki
    tone + V100 equal-dignity)
- Tests (`tests/test_pre_commit_formatter.py`,
  `tests/test_pre_commit_formatter_rust.py`):
  `test_three_slot_vision_attribution` regression guard on each loom.
- Rationale: per the 2026-04-25 cross-reference 5-Whys, singular
  vision attribution was a category error — the 100 visions form a
  graph, not a tag cloud.

#### V25 stance slot addition (PR [#7](https://github.com/aki1770-del/spa-ai/pull/7))

- Both production looms now declare `stance_vision_ids = [22, 25, 32, 100]`
  (V25 added — autonomation = human liberation, not replacement).
- Anchored on the cross-reference synthesis GAPS section: V25 was
  the anti-replacement declaration distinguishing SPA AI from any
  AI-replaces-the-maintainer tool.

#### README V1+V22 headline pair (PR [#8](https://github.com/aki1770-del/spa-ai/pull/8))

- `README.md` headline rewritten to the synthesis-recommended public
  pair: *"A broken thread must stop the loom (V1). The loom serves
  the weaver, not the reverse (V22)."*
- V92 framing as corollary: *"When a failure happens, the question
  is never who missed it but which loom was absent."*

#### `pre-commit-formatter-rust` loom — `--check` flag fix (PR [#5](https://github.com/aki1770-del/spa-ai/pull/5))

- `src/spa_ai/looms/pre_commit_formatter_rust.py` — rustfmt hook
  now emits `cargo fmt -- --check` (was `cargo fmt --` in 0.1.0,
  which silently rewrote files instead of halting on drift).
- `tests/test_pre_commit_formatter_rust.py` —
  `test_rustfmt_hook_uses_check_flag` regression guard.
- Caught by external_pr_audit swarm during embedded-hal dogfood
  audit on 2026-04-25; loom that should have caught: the audit
  itself now exists.

#### Doctrinal docs — Phase 0.5 patches (PR [#1](https://github.com/aki1770-del/spa-ai/pull/1))

- `docs/commitments.md` — Commitment 7 (Andon pulls are public)
  refined per V12 weaver-dignity language.
- `docs/mission.md` — replaces tagline with explicit weaver-framing
  (maintainer / rural developer / contributor; all the same person
  in Our model).
- `docs/manifesto.md` — machine-level halt wording + v0.1 ships
  with two loom classes mention.
- `docs/launch_plan.md` — Step 11 reframed as CLI-only v0.1
  (Komada directive 2026-04-25); GitHub App / hosted-service surface
  deferred per V65 sekishō-idai.
- `docs/principles.md` — new file; V65 Sekishō-idai principle anchor.
- `docs/demo_script.md` — fallback-target rule (per dogfood evolution).
- `docs/promises.md` — refined per Phase 0.5 audit.

#### `looms_in_production.md` (PR [#4](https://github.com/aki1770-del/spa-ai/pull/4))

- `docs/looms_in_production.md` — new file; concrete narrative of
  the loom-installation pattern operating outside SPA AI itself.
  Documents Loom #1 (MRA-1, Maintainer Reception Audit Gate),
  Loom #2 (SISE-1, Schema Input-Space Enumeration Gate), and
  Loom #3-candidate (Verify-First Gate, held for VGC-164 docket).

### Behavior change vs 0.1.0

The Rust loom now correctly halts on formatting drift instead of
silently rewriting files. This is a behavior fix, not a breaking
API change. Users of `PreCommitFormatterRustLoom` should regenerate
their `.pre-commit-config.yaml` (re-run `spa-ai propose
<repo-path> --loom pre-commit-formatter-rust --apply` to get the
correct hook entry).

### Tests

- 38 tests passing (was 28 in 0.1.0; +10 from 3-slot schema tests +
  V25 stance tests + rustfmt --check regression guard + others).
- Non-CLI test suite passes cleanly via
  `PYTHONPATH=src python3 -m pytest tests/test_pre_commit_formatter*.py
  tests/test_registry.py tests/test_scanner.py`.
- CLI tests require editable install (`pip install -e .[dev]`); pre-existing
  PEP 668 environment issue blocks `pip install` on some Linux
  distributions but does not affect runtime correctness.

---

## [0.1.0] — 2026-04-25 (Phase 1 MVP skeleton — initial slice)

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

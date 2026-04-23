# SPA AI — Sakichi Principle Actuator AI

**Date**: 2026-04-23
**Mission**: Make git repo developers' lives easier by installing Jidoka — machine-level halts — for failure classes humans currently absorb through vigilance. **Never blame the human. Blame the system that did not stop.**
**Target edge developer**: every maintainer reviewing a PR, every rural developer building navigation for snow roads, every solo dev running overnight CI — all weavers, all entitled to the same loom.
**Core stance**: SPA AI is not an AI assistant. SPA AI is a Sakichi Principle Actuator — a human + AI + governance loom that terminates failures at their point of origin, before they become burden.

---

## Part 0 — The product, in one paragraph

SPA AI is a GitHub-native developer-productivity agent that scans a repo, identifies **missing Jidoka halts** (the loom-absence pattern — places where a defect is only caught downstream by a human), and installs them as PRs. Pre-commit hooks that should exist. Silent-failure patterns that should raise. Type stubs that should be added. Flaky tests that should be quarantined. CI steps that fail-open when they should fail-closed. SPA AI sees where the weaver is standing last-line-of-defense and builds the loom that should have halted instead. The product is marketed not as "write code faster" but as "stop blaming yourself for bugs the system should have caught."

---

## Part 1 — Pain points catalog (30 concrete failure classes humans currently absorb)

Each entry: **Pain** → **Who absorbs it** → **Jidoka halt that should exist**.

### A. Silent failures (the anti-Jidoka)

1. **Function returns success-shaped value when operation failed** (OPS-RULE-029 pattern, e.g. returning `None` or `0` when a fetch 404'd). → Maintainer hunts prod bug. → Halt: lint rule forbidding "return on exception" without explicit-re-raise or typed-error return.
2. **`except: pass` swallowing exceptions**. → Operator debugging a ghost. → Halt: ruff/flake8 rule (B902, E722) enabled + blocked in CI.
3. **API returns 200 + empty body for errors**. → Downstream consumer assumes success. → Halt: contract test asserting error-as-non-200 on known-fail paths.
4. **Background jobs fail without raising**. → Data missing, nobody knows why. → Halt: job-frame wrapper that records run status + alert on last-N-failure-rate.
5. **`unwrap()` / `.unwrap_or_default()` in Rust where error is meaningful**. → Bug surfaces in prod. → Halt: clippy lint `unwrap_used` + `expect_used` enabled at deny-level on critical modules.

### B. Review burden (weaver as last line of defense)

6. **PR contains unrelated formatting churn**. → Reviewer scrolls past real change. → Halt: pre-commit formatter enforced, CI denies unformatted diff.
7. **PR description missing "why" section**. → Reviewer reconstructs intent. → Halt: PR-template enforcement; bot blocks merge until sections present.
8. **Commit messages are `fix`, `wip`, `.`**. → Bisect unusable. → Halt: commit-msg hook enforcing conventional-commit format.
9. **PR touches 40 files across 6 domains**. → Reviewer cannot hold it in head. → Halt: size-limit bot comments when diff > N hunks; suggests split.
10. **PR author is also the primary maintainer of the reviewed file** (no fresh eyes). → Missed bug. → Halt: CODEOWNERS-enforced cross-review; halt merge if only author approved.

### C. Drift / stale state

11. **CHANGELOG not updated when changing public API**. → Downstream surprise. → Halt: CI job that diffs public-API surface vs CHANGELOG; fails on delta without entry.
12. **Docs drift from code**. → Wrong answer given to users. → Halt: doctest enforcement; CI runs all code blocks in README/docs.
13. **Deps with known CVEs**. → Security debt accumulates silently. → Halt: `cargo audit` / `npm audit` / `pip-audit` in CI with fail-on-high.
14. **Deprecation warnings ignored**. → Break at next major upgrade. → Halt: CI job fails on any new deprecation warning (comparing to baseline).
15. **Unused code accumulates**. → Cognitive tax on all readers. → Halt: `vulture` / `knip` / `ts-unused-exports` integrated + fail-on-new-dead-code.

### D. Tests and contracts

16. **Flaky tests marked `skip` without ticket**. → Real regression masked. → Halt: `skip_if_` decorator requires linked-issue arg; CI fails otherwise.
17. **New module ships without tests**. → Critical path untested. → Halt: coverage diff fails if new lines < N% covered.
18. **Tests exist but don't run in CI** (wrong path, disabled). → False green. → Halt: `pytest --collect-only` count checked against previous build.
19. **Property tests with only 10 runs in CI**. → Not enough to surface bug. → Halt: hypothesis/quickcheck config enforces ≥N runs in CI vs local.
20. **Performance regressions silent**. → Prod slows over months. → Halt: bench-on-PR bot comments delta; fails if > X% regression on hot path.

### E. Ecosystem friction

21. **Issue filed, no maintainer response in 30 days**. → Filer ghosted. → Halt: triage bot auto-labels stale-unanswered; maintainer dashboard surfaces.
22. **Duplicate issue filed because search found nothing**. → Maintainer closes as dup. → Halt: issue-form pre-flight auto-searches similar; suggests existing.
23. **PR submitted against outdated base**. → Merge conflict at review time. → Halt: PR-open-time auto-rebase preview; warn if base > N commits behind.
24. **Dependency bump PR untested against downstream**. → Regression surfaces weeks later. → Halt: auto-trigger downstream test suites on bump PRs.
25. **License file missing / non-SPDX**. → Legal uncertainty. → Halt: `licensee` CI check + SPDX header presence enforced.

### F. Onboarding / documentation

26. **README setup instructions out of date**. → New contributor gives up. → Halt: `setup-in-docker` CI job that executes README commands from scratch weekly.
27. **`CONTRIBUTING.md` absent or 404** (our Loop 16 evidence!). → Contributor guesses conventions. → Halt: repo-health bot files PR proposing template if missing.
28. **First-issue label untagged**. → New contributors repelled. → Halt: monthly bot surveys issues tagged "bug" + size-label; suggests "good-first-issue" for small ones.
29. **Code of Conduct absent**. → Contributor unsure of norms. → Halt: repo-health bot proposes standard CoC if missing.
30. **Build instructions diverge across OSes**. → Mac/Linux contributor friction. → Halt: matrix CI that runs the documented install path on each target OS.

Each pain point = a loom-shaped opportunity. SPA AI's job is to see these at scan time and either (a) install the loom directly via PR, or (b) advise the maintainer that a loom is missing.

---

## Part 2 — PR opportunity list (concrete repos where SPA AI could file a PR today)

Scanned against our current portfolio + public repos. Each is a specific loom that could be installed TODAY as a PR.

| # | Repo | Loom proposed | Pain class (from Part 1) |
|--:|------|---------------|---|
| 1 | eclipse-kuksa/kuksa-common | Add `pre-commit` config (currently trailing-whitespace drift hit our PR #15) | A6 (formatter enforcement) |
| 2 | eclipse-kuksa/kuksa-common | Add `.github/CONTRIBUTING.md` (D-VGC158-4 found it missing) | F27 |
| 3 | rust-embedded/embedded-hal | Add `CONTRIBUTING.md` (Loop 16 verified 404) | F27 |
| 4 | embassy-rs/embassy | Add `CONTRIBUTING.md` | F27 |
| 5 | foxglove/mcap | Add `CONTRIBUTING.md` | F27 |
| 6 | smoltcp-rs/smoltcp | Add `CONTRIBUTING.md` | F27 |
| 7 | knurling-rs/defmt | Add `CONTRIBUTING.md` | F27 |
| 8 | riebl/vanetza | Add `CONTRIBUTING.md` | F27 |
| 9 | COVESA/vss-tools | Add `SECURITY.md` (repo currently has no documented vuln-report path) | E25-adjacent |
| 10 | ros2/rcl | Add CODEOWNERS file for rcl/src/rcl/node.c area (currently PR review routing ad-hoc) | B10 |
| 11 | ros2/rclpy | Add `deprecation-check` CI step (hidmic's TODO comment in arguments.c is 5+ years old) | C14 |
| 12 | ros-navigation/navigation2 | Add `panic-budget` tracker on SMAC smoother (Sprint 127 T2 evidence) | A4 |
| 13 | eclipse-zenoh/zenoh-pico | Add `clippy --deny warnings` CI job (warnings currently advisory) | A5 |
| 14 | eProsima/Fast-DDS | Add stale-issue auto-label bot (many issues are stale-fixes — OPS-RULE-029 pattern) | E21 |
| 15 | autowarefoundation/autoware | Add `bench-on-PR` for perception latency (planner-change perf regressions silent) | D20 |
| 16 | tier4/scenario_simulator_v2 | Add `README-setup-in-docker` weekly CI (setup drift probable) | F26 |
| 17 | rallista/valhalla-mobile | Add pub.dev example app in `example/` (onboarding friction for Flutter devs) | F26 |
| 18 | simolus3/drift | Add `pytest --collect-only` count guard (test discovery flakes historically) | D18 |
| 19 | ros2/rcutils | Add `thread-sanitizer` CI job for logging subsystem (Sprint 127 T3 race pattern) | A1 |
| 20 | GIScience/openrouteservice | Filename fallback note in docs (`CONTRIBUTE.md` vs `CONTRIBUTING.md` caught us Loop 16) | F26 |

These 20 are shovel-ready. SPA AI would generate the PR body + the loom config + the test evidence + the Jidoka-framing rationale, Komada authors the cover, human posts.

---

## Part 3 — 100-step implementation method to publish SPA AI

Organized into 6 phases. Each step is concrete, verifiable, and sized to < 1 day of focused work.

### Phase 0 — Identity lock-in (steps 1–10)

1. Freeze the project name: **SPA AI** (Sakichi Principle Actuator AI). Reserve github.com/spa-ai, spa-ai.dev, spa-ai.com domains.
2. Write the product manifesto (single page): "We don't blame humans. We blame systems that didn't halt. A broken thread must stop the loom."
3. Reference `UNTITLED/outputs/sakichi_100_visions/synthesis.md` as the doctrinal source; link from manifesto.
4. Define the 5 load-bearing promises: (i) never blame the human; (ii) every halt cites the Jidoka rationale; (iii) the loom is a PR, not an alert; (iv) the weaver owns the halt; (v) if the loom is wrong, we remove it, not defend it.
5. Draft an "Anti-patterns" list — things SPA AI must never become: a nag bot, a karma-score, an AI-slop pipeline, a surveillance tool.
6. Write a 200-word mission statement for the landing page, rooted in Sakichi's mother-at-the-hand-loom origin.
7. Write a 60-second demo script: scan a repo → identify 3 missing looms → offer to install as PR → human reviews + submits.
8. Commit to **100% PR-generation target** — SPA AI never just alerts; it always offers to install the halt.
9. Commit to **contextual disclosure** per OPS-RULE-008 v3 re-read under SPA lens: every SPA-generated PR body explains the loom's Jidoka rationale AND the human's role in reviewing it.
10. Define first-100 edge developers as "weavers" in all product copy; ban the word "users."

### Phase 1 — MVP skeleton (steps 11–25)

11. Create monorepo `spa-ai/` with `/core` (loom detection), `/looms` (loom templates), `/cli` (developer entry), `/server` (GitHub app), `/docs`.
12. Choose language: Python 3.11+ for core (matches Claude SDK ergonomics; matches our sky/bento stack).
13. Vendor `anthropic` SDK; choose Claude Sonnet 4.6 as default model (our CT scout precedent); Opus 4.7 for synthesis.
14. Implement `SPAConfig` class: holds API keys, rate-limit budgets, loom-library path, governance-hash lock (per OPS-RULE-024 PSG-A shape).
15. Write the first loom: `PreCommitFormatterLoom` — scan for missing `.pre-commit-config.yaml`, generate one, output as patch.
16. Write the second loom: `ContributingMdLoom` — scan for missing `CONTRIBUTING.md` (+ fallback chain per D-VGC158-4).
17. Write `RepoScanner` that walks a git clone + surfaces loom-candidate findings with evidence.
18. Implement `LoomRegistry` — registry of loom classes, each declaring `detect()`, `propose_patch()`, `render_pr_body()`.
19. Add `--dry-run` mode by default; SPA AI never writes without `--apply` flag.
20. Write CLI entry: `spa-ai scan <repo-path>` → prints missing looms + rationale.
21. Write CLI entry: `spa-ai propose <repo-path> --loom <id>` → generates PR patch as `.patch` file.
22. Write the loom-rationale template: every PR body section includes "**Why this halt**" + "**What the weaver does**" + "**What the loom does now**".
23. Ship a Dockerfile for reproducible scans (reviewers can verify).
24. Add telemetry off-by-default; if on, stream to self-hosted endpoint only (never to third parties).
25. Write the first end-to-end test: scan `eclipse-kuksa/kuksa-common` clone, generate patch for `PreCommitFormatterLoom`, verify patch applies.

### Phase 2 — Loom detection engine (steps 26–45)

26. Build a **governance-hash lock** (per OPS-RULE-024 PSG-A): the loom registry must have a SHA-256 signature; CLI refuses to run with mismatch.
27. Implement **OPS-RULE-031 v2 output contract** in every loom's `propose_patch()` — structured response required, fail-closed.
28. Implement **OPS-RULE-032 scope-classification** at loom time: parse target issue for "how would you prefer?" signals; cap confidence / flag for human judgment.
29. Add 10 more loom classes for Pain Points 1–10 (silent failures, review burden):
   - `ExceptSwallowLoom` (A2)
   - `ReturnOnExceptionLoom` (A1)
   - `UnwrapUsedLoom` (A5, Rust-specific)
   - `BackgroundJobWrapperLoom` (A4)
   - `PRTemplateLoom` (B7)
   - `CommitMsgFormatLoom` (B8)
   - `PRSizeLimitLoom` (B9)
   - `CodeownersCrossReviewLoom` (B10)
   - `ContractTest404Loom` (A3)
   - `FormatterEnforceLoom` (B6)
30. For each loom, write: (a) detector unit test, (b) patch-generation test, (c) 3 real-world repo fixtures.
31. Implement the **loom-absence priority score** — each detected gap gets a severity (based on how much weaver-attention it currently consumes).
32. Write the **loom conflict resolver** — if two looms would conflict (e.g. two different pre-commit configs), prefer the narrower + show both to human.
33. Add **LoomGovernor** — the meta-loom that audits loom proposals before they're shown (the loom pointed at the loom-builders per vision 98).
34. Implement `spa-ai scan --format=json` for machine consumption.
35. Add 10 more loom classes for Pain Points 11–20 (drift, tests, contracts).
36. Add 10 more loom classes for Pain Points 21–30 (ecosystem, onboarding).
37. Write `LoomContextLoader` — pulls repo metadata (push date, CONTRIBUTING status, maintainer activity) using the D-VGC158-4 fallback.
38. Implement **competitor pre-scan** per D-VGC158-2b: if an open upstream PR already proposes the same loom, SPA AI steps aside.
39. Implement **self-portfolio check** per OPS-RULE-030: never propose a loom in a repo where the same author has open PRs on the same loom class.
40. Write `LoomSignalRouter` — chooses which looms to propose first based on maintainer-responsiveness history.
41. Add `spa-ai audit` subcommand — scans without proposing, just reports loom gaps with rationale.
42. Add `spa-ai coach` subcommand — for maintainers: "here are the looms that would reduce your weekly review load by N hours."
43. Write the **rationale-doc generator**: every loom's PR body includes a one-paragraph explanation of *why this halt, why now, what happens if you reject*.
44. Add **PAUSE protocol** — any loom can pull an Andon if it detects its own proposal would harm more than help; surfaces to human + halts that loom for the session.
45. Freeze Phase 2 API; write migration docs for Phase 3.

### Phase 3 — Loom installation engine (steps 46–65)

46. Build the **PR preparation pipeline**: clone → branch → apply patch → run upstream's own tests → commit (DCO signed) → push to fork.
47. Implement **fork auto-setup**: if user has no fork, prompt to fork via `gh api`; never force-fork.
48. Enforce **single-preference authorship** per our embassy-#5944 retrospective: every PR body has the author's one-line preference, not a 4-option buffet.
49. Enforce **personal-voice signal** — a concrete detail that shows the human reviewed (debugging history, domain context). SPA AI asks the human for this; never fabricates.
50. Add **PSG-1 pre-submit gate** to every generated PR: (a) caller audit, (b) factual-claim audit, (c) semantic-scope audit (OPS-RULE-021 shape).
51. Add **OPS-RULE-011 test-before-submit gate** — no PR opened without documented test evidence.
52. Add **OPS-RULE-016 existing-behavior audit** section to every PR body.
53. Integrate `pre-commit` hook execution locally before push — catch upstream ruff version pinning (per Loop 17 T2 CI-fix learning).
54. Build **version-matched lint runner**: parse `.pre-commit-config.yaml` for pinned ruff/black/etc versions; run exact versions locally.
55. Add `spa-ai submit <loom-id>` — runs PSG-1 → opens PR via `gh pr create` with body prepared by human.
56. Reserve PR body authorship to human per D-VGC148; SPA AI proposes, human edits + submits.
57. Generate a **rollback patch** alongside every loom PR: "if this halt turns out wrong, here's the exact revert."
58. Write integration test: end-to-end scan → propose → human-approve → push → open PR against a scratch test repo.
59. Add `spa-ai withdraw <pr-url>` — if maintainer objects or a competing PR opens, SPA AI politely closes our PR + posts a one-line deferral.
60. Implement **gentle inquiry protocol** per OPS-RULE-022: if our PR sits without review for 14 days, SPA AI proposes a human-authored inquiry draft; human decides whether to post.
61. Add **status dashboard**: `spa-ai status` shows all open PRs + their ack-window state.
62. Write **maintainer respect scorecard** — visible to user: "this maintainer has X PRs in flight; consider holding before filing Nth."
63. Add **concurrency cap** per maintainer (≤2 per repo per maintainer, adopted from VGC-157 Option 3).
64. Publish v0.1 on GitHub with `Beta` tag.
65. Announce to 5 trusted reviewers for early feedback (no public launch yet).

### Phase 4 — PR-generation engine polish (steps 66–80)

66. Incorporate early-reviewer feedback: top 5 friction points → patches.
67. Add loom-class contribution guide — external contributors can propose new looms via PR with rationale template.
68. Build **loom library curator** — meta-maintainer role; only audited looms ship in releases.
69. Publish v0.2 with 40 loom classes covering Part 1's 30 pain points (some pain points get multiple looms).
70. Add **progressive disclosure** in CLI: first-run user sees the 3 most-impactful looms for their repo; expert mode shows all.
71. Add **language detection**: Python / Rust / TypeScript / Go / Dart / C++ handlers for each loom where relevant.
72. Specific Flutter/Dart loom support (our D3/SC #22 aligned): pub.dev metadata checks, `example/` app validator, analysis_options presence.
73. Specific ROS2 loom support (our Sprint-130-series aligned): package.xml correctness, CMakeLists.txt lint, C++ clang-tidy config.
74. Specific COVESA/VSS loom support: VSS spec validation, strict.py integration, tests/vspec fixture conventions.
75. Add **loom telemetry** (opt-in, self-hosted): which looms get accepted, rejected, amended by maintainers; feedback loop.
76. Build **accepted-loom gallery**: catalog of merged SPA-AI PRs with maintainer testimonials.
77. Write case-study: "How SPA AI caught 3 silent failures before Sprint 130's T2 shipped." (our own dogfood evidence)
78. Publish v0.3 with telemetry + gallery.
79. Set a **merge-rate north-star metric**: % of SPA-AI-proposed PRs that get merged (target: ≥60%).
80. Track merge-rate per loom class; retire looms with <40% merge rate (they're not earning their keep).

### Phase 5 — Publishing + go-to-market (steps 81–95)

81. Stand up spa-ai.dev landing page with: manifesto (step 6), Sakichi lineage (link to synthesis.md), 60-second demo (step 7), install instructions, first-loom showcase.
82. Record a 2-minute demo video: real repo scan, real PR generated, real halt installed. No cuts, no VFX; raw craft.
83. Write 5 blog posts:
   - "We don't blame humans. We blame systems that didn't halt."
   - "Your PR review backlog is a Jidoka gap."
   - "Why a 1920s loom invention still runs your CI."
   - "Install the loom, not the nag bot: how SPA AI generates halts as PRs."
   - "What a Sakichi Principle Actuator is (and why it isn't an AI assistant)."
84. Submit `SPA AI` to Show HN with the manifesto; engage comments directly (human-authored per D-VGC148).
85. Submit to r/programming, r/rust, r/Python, r/esp32 (overlap with embassy/embedded-hal targets).
86. Submit to Lobste.rs.
87. Reach out to 20 Sakichi-curious individuals by name: Mary Poppendieck, Gene Kim, Taiichi Ohno scholars, Toyota Industries historians, 3 lean-software practitioners.
88. Engage Claude/Anthropic developer-relations for partnership exposure.
89. Present at a local Sakichi/lean-manufacturing meetup (Nagoya or Shizuoka has active chapters).
90. Apply for 1 funded program (e.g. GitHub Accelerator, Y Combinator) only if strategic — not as fuel.
91. Keep a public changelog in the repo; every released loom gets a dated entry.
92. Launch `spa-ai.dev/blog` with RSS.
93. Publish v1.0.0 with SemVer promise: breaking changes → major bump, new loom → minor, bugfix → patch.
94. File the first batch of 20 PRs from Part 2's list using SPA AI itself — dogfood the tool on real repos.
95. Publish the dogfood results: merge rate, maintainer feedback, loom acceptance matrix.

### Phase 6 — Community + scale (steps 96–100)

96. Incorporate maintainer scorecard from accepted PRs: who is the most loom-friendly maintainer; surface publicly (with consent).
97. Enable plugin system: external contributors can publish loom packages (`spa-ai-loom-X`).
98. Write governance doc for SPA AI itself: what goes into a new rule, who ratifies, how PAUSE works. Mirror our VGC cadence.
99. Plan v2.0: cross-repo loom coordination (same loom absent in 5 repos → one meta-PR campaign with consent from each maintainer).
100. Establish the *Sakichi Memorial Loom-Builder of the Year* award — recognize 1 external contributor each year who installed the most high-impact looms. Prize funded by SPA AI hosting revenue; honoree named on spa-ai.dev homepage.

---

## Part 4 — Success criteria (SPA AI works when)

- **Maintainer-load reduction**: 20% reduction in trivial-review minutes per week on repos running SPA AI (measured via anonymized survey; opt-in).
- **Merge rate ≥ 60%**: SPA-AI-proposed PRs get merged, not closed.
- **Zero "AI slop" complaints** on merged PRs (the embassy #5944 pattern never recurs; if it does, loom gap named + installed within 48h).
- **Sakichi alignment**: every merged PR body traceable to a specific Jidoka principle + specific Vision from the 100.
- **Dignity signal**: maintainers report SPA AI made their life easier, not harder.
- **D3 alignment**: installed looms trace back to edge developers' lives (PR from a snow-road navigation repo → a safety-critical loom).

---

## Part 5 — Failure modes to watch for (Andon pulls built in)

- **SPA AI becomes a nag**: if any repo's SPA-AI-PR acceptance rate drops below 20% for 2 weeks, auto-pause that repo + human retrospective.
- **SPA AI becomes a competitor**: if we propose a loom that duplicates a maintainer's in-flight work, withdraw with apology + note to self (update competitor-pre-scan).
- **SPA AI becomes performative**: if "AI disclosure" becomes boilerplate-everywhere instead of contextual, prune it per OPS-RULE-008 v3.
- **SPA AI grinds itself**: if we ship 3 looms per day without the weaver (Komada) reviewing, PAUSE. No automation beats D-VGC146-F workload cap.
- **SPA AI loses the household origin**: if we ever pitch SPA AI as "efficiency" without naming the weaver whose hand it's lifting, PAUSE and rewrite the copy.

---

## Part 6 — Governance overlay

SPA AI inherits the toyota-flutter-masterplan governance stack:

| Our rule | SPA AI application |
|---|---|
| OPS-RULE-021 PSG-1 | Every SPA-generated PR passes caller / factual-claim / semantic-scope audit |
| OPS-RULE-024 PSG-A | Every SPA scan passes preflight hash-lock on loom registry |
| OPS-RULE-031 v2 | SPA's output artifact includes SCOUT CONCLUSION footer per loom proposal |
| OPS-RULE-032 | SPA halts proposing when target issue has discussion-invited signal |
| OPS-RULE-030 | SPA never proposes loom X in repo R if SPA or human has open PR X in R |
| D-VGC148 | Human authors PR body and comments; SPA proposes drafts only |
| D-VGC146-F | SPA's own dev cadence respects workload cap on maintainer (Komada) |
| §0 Sakichi identity | Failures in SPA AI itself trace to missing looms, never to user error |

---

## Part 7 — What happens next session

If Komada says "ship it":
1. Create `github.com/aki1770-del/spa-ai` repo (or preferred org)
2. Execute Phase 0 steps 1–10 — identity lock
3. Scaffold Phase 1 steps 11–25 — MVP skeleton
4. Use SPA AI on its own repo (`aki1770-del/spa-ai`) as first dogfood: scan, propose looms, install
5. Write the 5 blog posts from step 83 as 5 separate outputs, one per sprint

If Komada says "hold":
- This plan lives at `UNTITLED/outputs/spa_ai_launch_plan/plan.md`
- Revisit after a specific trigger (e.g. vss-tools #512 merged, or 100 edge developers using our D3 Flutter pub.dev packages)

---

## The Sakichi line at the bottom of every SPA AI page

> *A broken thread must stop the loom. The loom serves the weaver. Never blame the human — build the loom that should have caught it.*
>
> — Toyoda Sakichi, 1867–1930 (paraphrased into modern operating doctrine)

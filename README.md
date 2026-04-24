# SPA AI

**Sakichi Principle Actuator AI** — a GitHub-native developer agent that installs Jidoka halts for failure classes developers currently absorb through vigilance.

> A broken thread must stop the loom. The loom serves the weaver. Never blame the human — build the loom that should have caught it.

**Status**: Phase 1 — MVP skeleton (CLI; one loom: `pre-commit-formatter`). Launch target: Phase 5 completion.

---

## What SPA AI does

SPA AI scans a git repository, finds **missing Jidoka halts** — places where a defect is only caught downstream by a human — and installs them as pull requests. Pre-commit hooks that should exist. Silent-failure patterns that should raise. Type stubs that should be added. Flaky tests that should be quarantined. CI steps that fail-open when they should fail-closed. SPA AI sees where the weaver is standing last-line-of-defense and builds the loom that should have halted instead.

## What SPA AI is not

Not an AI assistant. Not a nag bot. Not a karma-scoring surveillance tool. Not a "write code faster" pitch. Not a replacement for the developer.

## The doctrinal source

All of SPA AI traces to Toyoda Sakichi (1867–1930), inventor of the Type G automatic loom — the first machine to stop itself when a thread broke. The principle: *the operator must not be the last line of defense against defects*. See [`docs/sakichi_100_visions.md`](docs/sakichi_100_visions.md) for the full lineage.

## Install (v0.1, dev)

```bash
git clone https://github.com/aki1770-del/spa-ai.git
cd spa-ai
pip install -e ".[dev]"
```

Requires Python 3.11+. v0.1 has zero runtime dependencies — the first
two looms are deterministic detectors. The Anthropic SDK lands when
the first LLM-driven loom does, per `docs/principles.md` Principle 1
(*Sekishō-idai* — accumulate one stone at a time).

## Run

Scan a git repo for missing looms:

```bash
spa-ai scan /path/to/some/repo
```

Generate the patch for a specific loom (dry-run by default):

```bash
spa-ai propose /path/to/some/repo --loom pre-commit-formatter
```

Write the patch to disk (the weaver still owns the merge — SPA AI
proposes; the human commits and opens the PR):

```bash
spa-ai propose /path/to/some/repo --loom pre-commit-formatter --apply
```

There is intentionally no `spa-ai alert` or `spa-ai issue-open`
subcommand. Per `docs/promises.md` Promise 3, the loom is a pull
request, not an alert; if we cannot offer a PR, we do not speak.

## Run the test suite

```bash
pytest
```

## Roadmap

| Phase | Focus | Steps |
|:-:|---|---|
| 0 | Identity lock | 1–10 (this commit) |
| 1 | MVP skeleton | 11–25 |
| 2 | Detection engine | 26–45 |
| 3 | Installation engine | 46–65 |
| 4 | Polish | 66–80 |
| 5 | Publishing | 81–95 |
| 6 | Community | 96–100 |

Full plan: [`docs/launch_plan.md`](docs/launch_plan.md).

## License

TBD — to be set before Phase 1.

# SPA AI

**Sakichi Principle Actuator AI** — a GitHub-native developer agent that installs Jidoka halts for failure classes developers currently absorb through vigilance.

> A broken thread must stop the loom. The loom serves the weaver. Never blame the human — build the loom that should have caught it.

**Status**: Phase 0 — identity lock. Not yet functional. Launch target: ~3 weeks from 2026-04-23.

---

## What SPA AI does

SPA AI scans a git repository, finds **missing Jidoka halts** — places where a defect is only caught downstream by a human — and installs them as pull requests. Pre-commit hooks that should exist. Silent-failure patterns that should raise. Type stubs that should be added. Flaky tests that should be quarantined. CI steps that fail-open when they should fail-closed. SPA AI sees where the weaver is standing last-line-of-defense and builds the loom that should have halted instead.

## What SPA AI is not

Not an AI assistant. Not a nag bot. Not a karma-scoring surveillance tool. Not a "write code faster" pitch. Not a replacement for the developer.

## The doctrinal source

All of SPA AI traces to Toyoda Sakichi (1867–1930), inventor of the Type G automatic loom — the first machine to stop itself when a thread broke. The principle: *the operator must not be the last line of defense against defects*. See [`docs/sakichi_100_visions.md`](docs/sakichi_100_visions.md) for the full lineage.

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

# SPA AI — 60-Second Demo Script

*Draft — Komada to record final. No cuts, no VFX; raw craft per Promise/anti-pattern posture.*

---

## Setup

A terminal. Green text on black. A real open-source repo cloned locally — primary target `eclipse-kuksa/kuksa-common` (small, real, pre-commit gap known at recording time).

**Fallback target rule**: if the primary repo's pre-commit gap closes before recording (likely if SPA AI files PR #1 from the dogfood list — that's the point), pivot to the next repo in the dogfood roster whose `.pre-commit-config.yaml` is still absent. Verify the gap with `spa-ai scan <path>` immediately before each recording session — the demo claim must match the live repo state on the day. If no dogfood repo has the gap any more, that is itself the launch story; record a different demo (e.g. `ContributingMdLoom` against a still-missing target).

## Script (read aloud, 60 seconds max)

> *[0:00]* This is SPA AI. It finds the machine-level halts your repo is missing.
>
> *[0:06]* Here's the kuksa-common repo. It has a formatting drift — 19 trailing-whitespace lines on a markdown file nobody's touched in months.
>
> *[0:14]* If I open a pull request here, the formatter catches the drift *after* I push. That's vigilance in the wrong place.
>
> *[0:22]* Watch.
>
> `$ spa-ai scan .`
>
> *[0:26]* SPA AI found three missing halts: no `.pre-commit-config.yaml`, no CODEOWNERS file, no CHANGELOG enforcement.
>
> *[0:34]* I want the first one.
>
> `$ spa-ai propose . --loom pre-commit-formatter`
>
> *[0:40]* SPA AI generates a pull request. The `.pre-commit-config.yaml` pins the exact versions. The PR body explains: this halt catches formatting drift at source, so the maintainer never sees it again. A rollback patch ships alongside.
>
> *[0:52]* The maintainer reviews. Merges. Done.
>
> *[0:57]* Next time a thread breaks, the loom catches it.
>
> *[1:00]* That's SPA AI.

## Post-roll slate

> A broken thread must stop the loom. The loom serves the weaver.
> Never blame the human — build the loom that should have caught it.
>
> spa-ai.dev

## What NOT to include

- No dramatic music
- No "AI-powered" framing — we name Jidoka, not AI
- No before/after metrics flashed on screen
- No individual names
- No logos of big tech companies we're trying to impress

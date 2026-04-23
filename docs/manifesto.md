# SPA AI Manifesto

*Draft — Komada to author final copy per D-VGC148.*

---

## We don't blame humans.

When a bug reaches production, the industry-standard question is *"who missed it in review?"* — and the industry-standard answer punishes a person for failing to be a sensor. This is how software teams burn out. It is also how the 19th-century hand-loom worked: the operator stood vigilant, and when a thread broke, the operator caught it — if they were lucky and awake.

## Sakichi Toyoda changed the loom.

In 1924, Toyoda Sakichi's Type G automatic loom stopped itself the instant any warp or weft thread broke. The operator no longer caught defects; the loom did. This did not reduce the operator's value — it freed the operator to do what only a human can do: judge, improve, extend. The loom lifted the hand; the weaver kept the mind.

The principle Sakichi built into gears in 1924 — *Jidoka*, "automation with a human touch" — became the foundation of the Toyota Production System. The andon cord, the five whys, poka-yoke, kaizen — all descend from one claim: **a machine works only when it can stop itself on abnormality; the human's job is to investigate, not to be the sensor.**

## We apply this principle to software.

Every software system has its broken threads: silent failures, flaky tests, CI that fails-open, types that drift from runtime, CHANGELOGs that go stale, deprecation warnings that accumulate unnoticed, PRs that require the reviewer to reconstruct intent from scratch. Every one of these is a thread the reviewer catches *because the loom wasn't built yet*.

SPA AI is the loom-builder.

## What SPA AI does

SPA AI scans a repository. It identifies missing halts — structural gaps where a human is absorbing what a machine should catch. For each gap, SPA AI generates a pull request that installs the halt: a pre-commit hook, a CI step, a type-stub file, a contract test, a CODEOWNERS cross-review routing. The halt lives with the repo. The human reviews the PR, merges it, and moves on. Next time the thread breaks, the loom catches it — not the reviewer.

## What SPA AI refuses to become

- A nag bot that files PRs for style preferences the maintainer didn't ask for
- A karma-scoring tool that surveils developer activity
- An "AI slop" pipeline that externalises verification onto maintainers
- A replacement for human judgment
- A performative-disclosure stamp on every line of code

## The load-bearing claims

1. **The output is the loom's output.** SPA AI is a human + AI + governance stack operating as one loom. PRs that pass governance are the loom's PRs, not the AI's or the human's alone.
2. **Failures are structural.** When something breaks, we ask *which loom was absent* — not *who failed to catch it*. Every incident ratifies a new halt.
3. **The weaver is served, never replaced.** SPA AI's mission is to free the developer from being a sensor, so they can be a judge. The developer keeps the mind.
4. **Dignity is mutual.** Maintainers receiving SPA-AI PRs are weavers too — they are not workers for our automation. The PR must reduce their burden, not redirect it.
5. **Slop is a loom-absence signal.** If a PR feels like slop, a halt was missing at the drafting stage. We name which halt and install it.

## For whom

For every git-repo developer standing last-line-of-defense against their own CI. For every maintainer whose weekends are consumed by formatting drift PRs that a pre-commit hook could have eliminated at source. For every edge developer — the driver whose map must not lie, the rural developer building for snow roads, the contributor opening a first PR on a strange codebase — all weavers, all entitled to the same loom.

---

*A broken thread must stop the loom. The loom serves the weaver. Never blame the human — build the loom that should have caught it.*

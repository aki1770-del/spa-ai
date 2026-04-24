# SPA AI — Operational Principles

*Draft — Komada to author final copy per D-VGC148.*

These are the six Sakichi visions that govern *how* SPA AI is built and shipped, distinct from *what* it does (manifesto + mission) or *what it promises* (promises + commitments). They are the character ground for the engineering practice. Where promises constrain output and commitments constrain behavior, principles constrain method.

Each principle is grounded in a specific vision from `docs/sakichi_100_visions.md`. They are listed in the order they bind: scoping (V65), shipping (V42), reflection (V82), self-monitoring (V95), recording (V99), and stopping (V20).

---

## Principle 1 — *Sekishō-idai*: accumulate small things to achieve great things (Vision 65)

> *Ninomiya Sontoku's maxim, the ancestor of kaizen's small-step philosophy.*

SPA AI ships in small, durable steps — a CLI before a GitHub App, two looms before forty, one merged dogfood PR before twenty. We do not skip steps to look further along; the foundation must be laid one stone at a time. If a sprint plan asks for a leap, we break it into stones first.

**Application to v0.1**: the launch architecture is **CLI first**, not hosted service. Every loom class earns its place in the registry through one merged dogfood PR. Phase 1 ships when two loom classes work end-to-end, not when ten exist on paper.

## Principle 2 — *Shitsujitsu-gōken*: substantive strength without ornament (Vision 42, Toyoda Kōryō Precept 3)

> *Sakichi's third precept: be practical and avoid frivolousness.*

We do not gold-plate. We do not stamp every output with disclosure ritual. We do not put dramatic music on the demo video. We do not brand the CLI in colors. The product is the loom, not the wrapping. When a feature is not needed yet, we do not pre-build it; when copy is needed, we write it once and don't decorate it.

**Application to v0.1**: anti-pattern 6 (performative disclosure) is downstream of this principle; the demo's "no dramatic music, no VFX" is downstream of this principle. When in doubt: trim.

## Principle 3 — *Hansei*: reflection that names shortfall before celebrating success (Vision 82)

> *Reflection is gratitude inverted — one cannot be grateful without first seeing clearly what one owes.*

After every shipped loom, every merged PR, every released version, the SPA AI team writes a short hansei note: *what went well, what fell short, which loom was absent that we will install before the next ship*. The note is written before the celebration, not after — because by the time celebration is over, the shortfall is invisible.

**Application to v0.1**: every Phase milestone closes with a hansei note in `docs/hansei/<phase>.md`. The note must name at least one shortfall before the milestone is considered closed. *No shortfall named* fails the close criterion.

## Principle 4 — Effort-asymmetry is a thread-break signal (Vision 95)

> *If generation takes seconds and review takes hours, the loom is absent on the generator side; slow the generator, or add the halt.*

This is the SPA AI self-check. Every artifact SPA AI produces — a scan report, a PR draft, a comment — is measured against the time the recipient would need to verify it. If review-time exceeds generation-time by an order of magnitude, the artifact is signaling that the SPA AI side is missing a halt. We slow the generator (more PSG-1 audit, more factual-claim verification) until the asymmetry closes.

**Application to v0.1**: PSG-1 (b) factual-claim audit at PR draft time is the first effort-asymmetry halt. If a maintainer rejects a PR for an avoidable factual error, the post-mortem MUST add a generator-side halt — never "human will catch it next time."

## Principle 5 — *Write the decision down*: a detector not installed cannot detect (Vision 99)

> *OPS-RULE-007 in project idiom; in Sakichi idiom, the detector that exists in someone's head and is not installed in the loom is not a detector.*

Every Andon pull, every loom retirement, every spec change, every architecture decision is written down in the same session in which it is made. Not later. Not "I'll remember." Not in a private note. The doc lives in the repo, in `docs/`, with a date and a rationale. Decisions outside the docs do not exist for the loom.

**Application to v0.1**: Phase 0.5 (this doc set) is the first instance — the decision to extract these six principles is itself recorded by extracting them. Every subsequent governance change to SPA AI follows the same rule; if it isn't in the repo, it isn't ratified.

## Principle 6 — Stopping must be cheap, or operators will hesitate (Vision 20)

> *Design the halt to cost less than the defect.*

If pulling the Andon takes a meeting, no one will pull it. If retiring a loom requires a debate, no one will retire it. If reverting a PR takes a hand-built patch, no one will revert. SPA AI's defaults are biased toward *make-stopping-cheap*: every halt PR ships its rollback patch, every loom in the registry has a one-command retirement path, every Andon is a single CLI command. The operator must never be tempted to run through a halt because the halt is too expensive.

**Application to v0.1**: Promise 5 (rollback PR alongside every halt) is downstream of this principle. The CLI's `withdraw` and `pause-on-repo` are downstream of this principle. Whenever a stopping mechanism gains friction across versions, that is a Sakichi regression — fix it before adding new looms.

---

## Why these six and not others

The 100 visions doc covers eight sections; these six are drawn from the ones that govern the *engineering practice* rather than the *product mission*. Section I (Jidoka core) and Section VIII (modern translation) are picked up in `manifesto.md`, `mission.md`, and `promises.md`. Section II (household origin) lives in `mission.md` and anti-pattern 8. Sections III (Toyoda Kōryō), V (failure/perseverance), and VII (investigative half) are the underground roots that govern *how we work*; this doc surfaces six of their visions explicitly so the practice doesn't drift.

Other visions worth periodic re-grounding (not yet codified as principles, but on the roadmap):

- **V32 — *katei-teki*** (the workshop is home-like): for v1.0+ when SPA AI has multiple maintainers.
- **V44, V49, V70 — invention as service / fund the next mission / hand proceeds forward**: for v2.0+ when SPA AI generates revenue.
- **V61 — exile is the condition for the masterpiece**: held in reserve; if the project is ever forced to pivot away from a Phase, this is the lens.
- **V77 — *genchi genbutsu***: covered structurally by PSG-1 (b) factual-claim audit; codify as a principle when a future incident shows the audit isn't enough.

---

*A broken thread must stop the loom. The loom serves the weaver. Never blame the human — build the loom that should have caught it.*

# Loom Authoring Guide

How to write a new loom for SPA AI. The minimum viable loom is ≤200 LOC of
Python — one file, two methods, three vision-attribution slots, one PR body
template. This guide walks the existing `PreCommitFormatterLoom` as the
canonical example.

> *V65 sekishō-idai — accumulate one stone at a time. The goal is not the
> grandest loom; it is the next honest loom.*

---

## What a loom IS

A loom is a single Jidoka halt SPA AI knows how to detect and install. It is
not an alert, not a notification, not a karma score. Per [`promises.md`](promises.md)
Promise 3: a loom is a pull request. If We cannot offer a PR, We do not speak.

Four contracts every loom honors (per [`looms/base.py`](../src/spa_ai/looms/base.py)):

1. **Three vision-attribution slots** — `sakichi_vision_id` (failure-mode the
   loom prevents), `method_vision_ids` (HOW the loom works), `stance_vision_ids`
   (HOW the weaver is treated). All three required.
2. **One weaver-class declaration slot** — `weaver_classes_served` (WHO the
   loom directly serves; canonical strings from
   [`weaver_classes.py`](../src/spa_ai/looms/weaver_classes.py); see the
   "Weaver-class declaration" section below). Optional with `[]` default for
   backward-compat; documented as required for any new loom.
3. **`detect(repo_root: Path) -> list[LoomFinding]`** — walk the repo, return
   findings. Must not write to disk.
4. **`propose_patch(finding: LoomFinding) -> LoomPatch`** — given a finding,
   return a patch (file contents + PR body). Must not write to disk.

Disk writes are restricted to the `--apply` path in the CLI, after human
review of the proposed patch. Per [`promises.md`](promises.md) Promise 4: the
weaver — not the loom — owns the halt.

---

## Minimum viable loom (≤200 LOC)

The shape, line by line, from `PreCommitFormatterLoom`:

```python
"""<LoomName> — one-line summary of the halt this loom installs.

<2-3 sentence rationale grounded in a Sakichi vision number>
"""
from __future__ import annotations
from pathlib import Path
from .base import LoomFinding, LoomPatch

_DEFAULT_CONFIG = """\
# The actual file contents the loom will write to the target repo.
# Include comments citing the Sakichi vision so the maintainer
# encounters the rationale in their own tree.
...
"""

_PR_BODY_TEMPLATE = """\
## What this PR adds
<concrete description of the artifact installed>

## Why this halt
<Jidoka rationale; what burden the maintainer absorbs today>

## Sakichi vision
<vision number + verbatim text from sakichi_100_visions.md>

## What you do as the maintainer
<numbered steps the maintainer takes after merge>

## Rollback
<single-command rollback per Promise 5>

## Provenance
<who drafted; who reviewed; SPA AI proposes, the human commits>
"""


class <LoomName>:
    """Detects <gap> and proposes <halt>."""

    loom_id = "<kebab-case-slug>"
    sakichi_vision_id = <int 1..100>
    method_vision_ids = [<int>, <int>, <int>]
    stance_vision_ids = [<int>, <int>, <int>]

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        # Walk repo_root. Return [] if no finding.
        # Cite specific files / signals checked.
        ...

    def propose_patch(self, finding: LoomFinding) -> LoomPatch:
        return LoomPatch(
            loom_id=self.loom_id,
            target_path=finding.target_path,
            contents=_DEFAULT_CONFIG,
            pr_body=_PR_BODY_TEMPLATE,
        )
```

That is the entire skeleton. The two production looms in `src/spa_ai/looms/`
fit in 124 and 177 lines respectively.

---

## Vision attribution — the three slots

Per the 2026-04-25 cross-reference 5-Whys finding: singular attribution is a
category error. The 100 visions form a graph; one loom serves multiple
visions in distinct roles.

### `sakichi_vision_id` (int, 1..100) — the FAILURE-MODE

The single anchor of *what halt is this?* This is the failure the loom
prevents. Required. Must be in `1..100`. Validated by `LoomRegistry`.

Both production looms use V20 (cheap-stop): the failure mode is "stopping
costs more than the defect; operator hesitates; halt skipped."

### `method_vision_ids` (list[int]) — HOW the loom works

The visions describing the method. Examples:
- **V77 genchi-genbutsu** — for any loom that walks the actual repo.
- **V18 5-Whys-mechanism** — for any loom whose PR body terminates at
  mechanism, not at blame.
- **V99 write-decision-down** — for any loom whose patch IS the recorded
  decision.

Both production looms declare `[77, 18, 99]`.

### `stance_vision_ids` (list[int]) — HOW THE WEAVER IS TREATED

The visions describing the loom's posture toward the maintainer:
- **V22 loom-serves-weaver** — every loom must hold this stance.
- **V25 autonomation = liberation, not replacement** — the anti-replacement
  declaration that distinguishes SPA AI from any AI-replaces-the-maintainer
  tool.
- **V32 katei-teki tone** — warm, family-like; not legalistic.
- **V100 equal-dignity** — for every weaver, regardless of project class.

Both production looms declare `[22, 25, 32, 100]`.

---

## Weaver-class declaration — what the loom serves

In addition to the three vision-attribution slots above, every loom declares
a fourth slot naming WHO it directly serves. This is FACT-data — which
classes of weaver receive the halt this loom installs — distinct from the
stance/method/failure-mode visions which are posture declarations.

### `weaver_classes_served` (list[str]) — the WHO

A list of canonical weaver-class strings. Defaults to `[]` for backward-compat;
omitting it does not break registration, but the doctor surface reports any
loom with an empty list in an advisory bucket so the gap is visible.

The v1 canonical set lives in
[`src/spa_ai/looms/weaver_classes.py`](../src/spa_ai/looms/weaver_classes.py)
as `KNOWN_WEAVER_CLASSES`:

| Class | Substance |
|---|---|
| `maintainer` | Receives the PR; reviews; merges or closes. The repo's gatekeeper. |
| `first-contributor` | Files first PR or first issue against the repo. |
| `adopter` | Has the loom-output installed in their own repo (e.g., `.pre-commit-config.yaml` lives in their tree). |
| `driver` | Downstream end-user whose map / route / safety depends on the stack the loom protects. |
| `auditor` | Reads provenance / SBOM / compliance data; not necessarily a coder. |
| `sub-agent` | AI sub-agent operating within an SPA-Actuator-class unit. |
| `integrator` | Combines this package with other packages into a downstream product. |

Examples (each shipped loom declares its own set):

```python
class PreCommitFormatterLoom:
    weaver_classes_served = ["maintainer", "first-contributor"]

class SilentFailureGrepperLoom:
    weaver_classes_served = ["maintainer", "auditor", "driver"]
```

### Aliases and case-insensitivity

The same module exports an `ALIASES` map for short / common variants:
`"contributor" → "first-contributor"`, `"user" → "driver"`, `"agent" →
"sub-agent"`, etc. `normalize_weaver_class("Contributor")` returns
`"first-contributor"`. The doctor surface aggregates by canonical form, so
a loom that declares an alias still aggregates under its canonical bucket.

For new looms, prefer canonical strings directly — the canonical set is small
enough to memorize and avoids one indirection at read time.

### Open string-set discipline (declaring a class not yet canonical)

A loom may declare a class that is not in `KNOWN_WEAVER_CLASSES` (for example,
`"future-cohort"` per OPS-RULE-046, or a class specific to a domain the v1 set
does not yet cover). The class will:

- pass through the registry and registration without error,
- appear in the doctor surface's `unknown_classes_declared` advisory bucket,
- not contribute to the `served` aggregation (which counts canonical classes
  only).

If a non-canonical class becomes well-established in practice (multiple looms
declare it; the substance is clear; no synonym already covers it), it can be
promoted to canonical via governance review. This protects future-cohort
exploration while keeping the v1 vocabulary documented.

### How the doctor renders this

`spa-ai doctor <repo>` aggregates declarations across the registry and prints
a single block at the end:

```
Weaver-class coverage (6 loom(s)):
  served:   maintainer (6/6), first-contributor (4/6), driver (2/6), auditor (2/6)
  absent:   adopter (0/6), sub-agent (0/6), integrator (0/6)
  unknown:  0 loom(s) declared no weaver_classes_served
```

The `absent` line is the load-bearing surface: any canonical class with zero
loom support identifies a candidate for the next round of new looms. JSON
output adds a `weaver_class_coverage` block under the same shape; schema is
documented as `schema_version: 2` (v1 fields remain present and unchanged).

---

## PR body template — what each section MUST contain

Per [`promises.md`](promises.md) Promise 2 + the conventions enforced in
existing loom tests:

| Section | Must contain | Why |
|---|---|---|
| **What this PR adds** | The concrete artifact + filename(s) | V99 write-decision-down |
| **Why this halt** | The Jidoka rationale (failure mode + cost the maintainer absorbs today) | V18 terminate at mechanism |
| **Sakichi vision** | The vision number AND verbatim text from `sakichi_100_visions.md` | V77 grounding in source |
| **What you do as the maintainer** | Numbered steps after merge | V22 loom-serves-weaver |
| **Rollback** | A single-command rollback | V20 cheap-stop on the maintainer side |
| **Provenance** | Who drafted, who reviewed | V42 + V96 transparency |

Existing tests assert these sections appear (e.g., `test_propose_patch_includes_jidoka_rationale`).

---

## Tests every loom must pass

Per the conventions in `tests/test_pre_commit_formatter*.py`:

1. **`test_detect_returns_finding_when_<gap>_missing`** — happy path.
2. **`test_detect_returns_empty_when_<gap>_already_present`** — idempotence
   (loom does not propose what's already there).
3. **`test_propose_patch_includes_jidoka_rationale`** — PR body has "Why this
   halt" + cites the Sakichi vision number.
4. **`test_propose_patch_does_not_write_to_disk`** — Promise 4 contract.
5. **`test_three_slot_vision_attribution`** — all three slots declared,
   non-empty, IDs in `1..100`, V77 in `method_vision_ids`, V22 in
   `stance_vision_ids`.

---

## Registering a loom

Add to `src/spa_ai/registry.py` — `LoomRegistry` enforces unique `loom_id`
and valid `sakichi_vision_id`. Tests guard against accidental size changes:
update `test_default_registry_size_is_N` when adding.

---

## What this guide does NOT cover yet

- **LLM-driven looms** — the first deterministic looms ship without
  Anthropic SDK; LLM-driven looms land in a later slice. Per
  [`principles.md`](principles.md) Principle 1 — V65 sekishō-idai.
- **Multi-target patches** — current loom contract assumes one
  `target_path` per finding. Multi-file looms are a future extension.
- **Pre-commit hook authoring versus CI workflow authoring** — the existing
  two looms are commit-time halts; CI-time halts (per OPS-RULE-037 + the
  W2 candidate `EofNewlineLoom` extension) follow the same Protocol but
  target `.github/workflows/`.

---

## Anti-patterns when authoring a loom

- **Don't propose what is not a halt.** Documentation suggestions, formatting
  preferences, naming conventions — these are not Jidoka halts. A loom
  installs a *machine-level catch*; if there is no catch, there is no loom.
- **Don't make the maintainer's first interaction adversarial.** The PR body
  starts with "What this PR adds" — concrete value first. Sakichi rationale
  follows. Per V32 katei-teki tone.
- **Don't lock the maintainer in.** Rollback must be a single command. Per
  V20 cheap-stop applied to the maintainer side: removing the loom must
  cost less than installing it.
- **Don't simulate consent the maintainer hasn't given.** Per OPS-RULE-037
  Ask-First Gate: a cold tooling PR must file an issue first. The loom
  drafts the PR; the human (or an authorized AI agent under post-on-behalf
  delegation) decides whether to engage that maintainer at all.
- **Don't ship more than one new loom per slice.** Per V65: small stones.

---

## The next loom

The Phase 1 loom queue (per [`launch_plan.md`](launch_plan.md)):

| # | Loom | Sakichi anchor | Status |
|---|---|---|---|
| 1 | `PreCommitFormatterLoom` | V20 | Shipped 0.1.0 |
| 2 | `PreCommitFormatterRustLoom` | V20 | Shipped 0.1.0 |
| 3 | `SilentFailureGrepperLoom` | V14 | Queued (W2-1) |
| 4 | `EofNewlineLoom` | V15 | Queued (W2-2) |
| 5 | `ContributingMdLoom` | V96 | Queued (W2-3) |
| 6 | `DcoSignoffLoom` | V18 | Queued (W3-1) |
| 7 | `IssueBeforePrLoom` | V96 + V20 | Queued (W3-2) |
| 8 | `ChangelogPresenceLoom` | V99 | Queued (W3-3) |

Pick one. Walk an actual repo first (V77). Write the loom. Open a PR.

# The Five Load-Bearing Promises

*Draft — Komada to author final copy per D-VGC148.*

These are the five promises SPA AI is built under. If any is violated, the system must PAUSE until the violation is resolved. These are inviolable.

---

## Promise 1 — We never blame the human.

When SPA AI encounters a failure — a broken CI run, a merged regression, a maintainer rejection, a user-reported bug — the question is always *which loom was absent*, never *who was careless*. **Five Whys is the investigative half of Jidoka** (Visions 18, 80): the stop is only half the discipline; the other half is asking *why* until the answer is structural. The chain terminates at a missing mechanism, never at a person. If our post-mortem reaches "the reviewer should have noticed," the post-mortem is unfinished — keep asking why.

## Promise 2 — Every halt cites its Jidoka rationale.

Every pull request SPA AI generates includes a *"Why this halt"* section that explains, in one paragraph, what thread-break this halt catches, which Sakichi principle it derives from, and what the weaver does differently after the halt is installed. No halt ships without its rationale. No rationale is boilerplate — each is specific to the context it's installed into.

## Promise 3 — The loom is a pull request, not an alert.

SPA AI does not send alerts. SPA AI does not file issues. SPA AI does not ping maintainers with "your repo is missing X." SPA AI generates the **fix** — as a ready-to-merge PR, with the loom wired in, with tests, with a rollback patch. The maintainer reviews and merges; they do not receive another thing to do. If we cannot offer a PR, we do not speak.

**Single carve-out** — *gentle inquiry* (per OPS-RULE-022 inherited from the parent project): if a SPA AI PR sits without any maintainer signal for 14+ days, SPA AI may *propose* a human-authored gentle-inquiry draft in an internal output file. The human, not SPA AI, decides whether to post and writes the final wording. The artifact that reaches the maintainer is the human's. SPA AI does not initiate maintainer contact — it can only draft, never post.

## Promise 4 — The weaver owns the halt.

SPA AI never installs a halt without the maintainer's explicit merge action. We propose; they decide. If they reject, we do not re-propose with different framing — we retire the loom for that repo and file a note for retrospection. The halt lives in their repo, under their license, subject to their governance. We are guests.

## Promise 5 — If the loom is wrong, we remove it, not defend it.

When a halt turns out to be wrong — false positive rate too high, maintainer complaint, unintended interaction with other gates — we generate the reversion PR first and discuss second. The default bias is toward removal, because a loom that annoys the weaver is not Sakichi-consistent; it is the nag pattern SPA AI exists to reject.

---

## Enforcement

- Promise 1 is enforced by post-mortem review: every incident report must name a missing mechanism, not a person.
- Promise 2 is enforced by the PR-template validator: no PR opens without a *"Why this halt"* section.
- Promise 3 is enforced by the SPA AI CLI: there is no `spa-ai alert` or `spa-ai issue-open` subcommand. Only `propose` and `submit`.
- Promise 4 is enforced by the maintainer-respect scorecard: if our propose-to-merge ratio on a repo drops below 20%, auto-pause for that repo and retrospect.
- Promise 5 is enforced by the rollback-PR requirement: every halt PR ships alongside its reversion patch. We are always one command from undo. *Stopping must be cheap, or operators will hesitate (Vision 20)* — the rollback patch is the cheap-stop.
- **Loom retirement preserves Sakichi lineage** (resolves the Promise 5 / Commitment 5 tension): when a loom is retired, the registry preserves (a) the loom-id, (b) the original Sakichi vision citation, (c) the evidence that triggered retirement, (d) the rollback PR. The vision itself is not retired; only this specific application of it. *A detector not installed cannot detect, but a removed detector that wasn't recorded cannot be re-installed either (Vision 99).*

If any of these five is violated, any actor (human, AI agent, governance gate) may pull the Andon and halt the pipeline. Only the human anchor (the project owner) lifts a halt.

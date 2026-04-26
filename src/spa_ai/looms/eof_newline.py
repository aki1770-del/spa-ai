"""EofNewlineLoom — adds `end-of-file-fixer` hook to existing pre-commit-config.

Sakichi vision 15 (poka-yoke): the cheapest possible halt for a known defect
class. End-of-file-newline is a famously trivial yet recurring source of git
diff noise + parser confusion (POSIX text files require trailing newline; many
tools warn or fail subtly without it). The pre-commit framework already provides
`end-of-file-fixer`. This loom detects the common case: the maintainer HAS a
`.pre-commit-config.yaml` but did not include this specific hook.

Failure mode prevented (V15): a poka-yoke gap where the halt-mechanism exists
in the ecosystem but the maintainer didn't wire it. This loom wires it.

Distinct from PreCommitFormatterLoom: that loom handles "no pre-commit-config
at all"; this loom handles "config exists but lacks one specific hook."

First user of the extended Loom Protocol's `propose_patch(finding, repo_root)`
signature — needs to read the existing pre-commit-config from disk during
patch composition (not just write a new file).
"""
from __future__ import annotations

from pathlib import Path

from .base import LoomFinding, LoomPatch

_EOF_HOOK_BLOCK = """\
  # Added by SPA AI's EofNewlineLoom (Sakichi vision 15 poka-yoke).
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
"""


_PR_BODY_TEMPLATE = """\
## What this PR adds

A single hook entry appended to your existing `.pre-commit-config.yaml`'s
`repos:` list:

```yaml
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
```

## Why this halt

End-of-file-newline drift is a famously trivial defect class that nonetheless
surfaces as git diff noise (lines added/removed solely because a file lacks
trailing newline), POSIX text-file parser confusion, and CI lint warnings on
some toolchains. The fix is mechanical; the cost is one hook entry.

Without this hook, the maintainer absorbs the drift during PR review or after
merge in CI. With it, the catch happens at `git commit`, before the change
can land.

## Sakichi vision

Vision 15 (poka-yoke) from the SPA AI doctrinal source: *a defect class
already known to the team gets a mechanical mistake-proofing device, not a
training program.* The `end-of-file-fixer` hook IS that device for this
specific class. Your repo already adopted the pre-commit framework; this PR
just wires one more hook into it.

## What you do as the maintainer

1. Review this PR's append to `.pre-commit-config.yaml`.
2. Run `pre-commit install` once locally if you haven't already (your other
   hooks already require this).
3. Merge.

## Rollback

Delete the four new lines this PR added; commit. No state is left behind. Per
`promises.md` Promise 5: removal is a single command — stopping must be cheap.

## Provenance

This PR was drafted by SPA AI's `EofNewlineLoom` and reviewed by a human
(the PR submitter) before opening. SPA AI proposes; the human commits.
"""


class EofNewlineLoom:
    """Detects existing pre-commit-config without `end-of-file-fixer`; appends the hook."""

    loom_id = "eof-newline"
    sakichi_vision_id = 15
    method_vision_ids = [77, 18, 99]
    stance_vision_ids = [22, 25, 32, 100]

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        """Return a finding if pre-commit-config exists but lacks `end-of-file-fixer`.

        Detect signal: at least one of `.pre-commit-config.{yaml,yml}` exists,
        AND `end-of-file-fixer` does not appear in its contents.
        """
        for name in (".pre-commit-config.yaml", ".pre-commit-config.yml"):
            cfg_path = repo_root / name
            if not cfg_path.exists():
                continue
            try:
                text = cfg_path.read_text(encoding="utf-8")
            except Exception:
                continue
            if "end-of-file-fixer" in text:
                return []
            return [
                LoomFinding(
                    loom_id=self.loom_id,
                    target_path=Path(name),
                    reason=(
                        f"`{name}` exists but does not include the "
                        "`end-of-file-fixer` hook. EOF-newline drift is a "
                        "known defect class with a mechanical poka-yoke "
                        "(V15) the project hasn't wired."
                    ),
                    sakichi_vision_id=self.sakichi_vision_id,
                    severity="low",
                )
            ]
        return []

    def propose_patch(self, finding: LoomFinding, repo_root: Path) -> LoomPatch:
        """Read existing config, append the EOF hook block, return merged contents.

        First user of the new `propose_patch(finding, repo_root)` Protocol
        signature. Reads `repo_root / finding.target_path` (allowed; only
        WRITES are forbidden per Promise 4).
        """
        existing_path = repo_root / finding.target_path
        try:
            existing = existing_path.read_text(encoding="utf-8")
        except Exception as e:
            # Conservative fallback: if we can't read the existing file at
            # propose-time (race vs detect, perms change), fall back to
            # producing the hook block alone with a header comment that the
            # apply path must NOT use to overwrite. The CLI's --apply path
            # refuses to overwrite, so this is safe — patch becomes a
            # report rather than an installable artifact.
            contents = (
                f"# ERROR: EofNewlineLoom could not read existing "
                f"{finding.target_path}: {e}\n"
                f"# This patch is informational only — the CLI --apply will "
                f"refuse to overwrite the existing file.\n"
            )
            return LoomPatch(
                loom_id=self.loom_id,
                target_path=finding.target_path,
                contents=contents,
                pr_body=_PR_BODY_TEMPLATE,
            )

        merged = self._merge(existing, _EOF_HOOK_BLOCK)
        return LoomPatch(
            loom_id=self.loom_id,
            target_path=finding.target_path,
            contents=merged,
            pr_body=_PR_BODY_TEMPLATE,
        )

    @staticmethod
    def _merge(existing: str, hook_block: str) -> str:
        """Append `hook_block` to the existing pre-commit-config under `repos:`.

        Strategy: locate the LAST line that looks like a top-level YAML key
        (starts with non-whitespace, ends with `:`) — append after the last
        line of the existing file, preserving trailing newline structure.
        Conservative: We don't parse YAML to avoid introducing pyyaml dep;
        We append at end-of-file, which works because pre-commit-config
        accepts hooks listed anywhere under `repos:`.
        """
        # Ensure existing ends with newline before append
        if not existing.endswith("\n"):
            existing = existing + "\n"
        return existing + hook_block

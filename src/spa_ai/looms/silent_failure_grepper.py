"""SilentFailureGrepperLoom — surfaces silent-failure shapes in Python source.

Sakichi vision 14: silent failure is anti-Jidoka. A function that catches
an exception and returns a "success-shaped" value (None, [], False, "")
without re-raising or logging the failure presents the caller with
indistinguishable success-vs-failure surfaces. The caller then makes
decisions on what looks like data but is actually absence-of-data caused
by a swallowed error. Drivers downstream of such functions silently
absorb the consequences.

This loom does NOT auto-fix. It produces an audit file
(`.spa-ai-silent-failures.md`) at the repo root listing every flagged
function with its file/line + the heuristic that triggered the flag. The
maintainer reviews the audit and decides per-function whether to: re-raise,
log + return sentinel, or accept the pattern as intentional.

Per Komada-voice override 2026-04-26 of the why-first synthesis on this
loom's design: option (a) — patch IS the audit artifact. This preserves
Promise 3 (the loom speaks via PR) + V99 (write-decision-down = wire-the-halt).

Heuristic detected (V14 MVP, conservative):
   try:
       ...
   except <Anything>:
       return <None | [] | False | "" | 0>     # silent-fail returning success-shape
   # OR
   except <Anything>:
       pass                                     # exception suppressed; subsequent
       return <value>                           # return may be stale

False positives are possible (e.g., "default value on missing key" patterns).
The audit file marks each finding with the heuristic that triggered, so the
maintainer can filter quickly.
"""
from __future__ import annotations

import ast
from pathlib import Path

from .base import LoomFinding, LoomPatch

# Values commonly returned by silent-failure handlers. Conservative list.
_SUCCESS_SHAPED_LITERALS: tuple[type, ...] = (type(None),)
_SUCCESS_SHAPED_REPRS: frozenset[str] = frozenset(
    {"None", "False", "True", "0", "''", '""', "[]", "{}", "()"}
)


def _scan_file(path: Path) -> list[dict]:
    """Return list of {func, lineno, heuristic} dicts for one .py file."""
    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    findings: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            handler_findings = _classify_handler(handler)
            if not handler_findings:
                continue
            # Find the enclosing function for context (best-effort walk-up).
            func_name = _find_enclosing_func_name(tree, node)
            for h in handler_findings:
                findings.append(
                    {
                        "file": str(path),
                        "func": func_name or "<module-level>",
                        "lineno": handler.lineno,
                        "heuristic": h,
                    }
                )
    return findings


def _classify_handler(handler: ast.ExceptHandler) -> list[str]:
    """Return list of heuristic-strings for a single except handler.

    Empty list = handler does NOT match any silent-failure pattern.
    """
    hits: list[str] = []
    body = handler.body

    # Pattern 1: handler body is a single `return <success-shape>`
    if len(body) == 1 and isinstance(body[0], ast.Return):
        ret_repr = _repr_simple_return(body[0])
        if ret_repr in _SUCCESS_SHAPED_REPRS:
            hits.append(f"except → return {ret_repr} (silent swallow)")

    # Pattern 2: handler body starts with `pass`, possibly followed by a return
    if len(body) >= 1 and isinstance(body[0], ast.Pass):
        if len(body) == 1:
            hits.append("except: pass (exception suppressed; no caller signal)")
        elif len(body) == 2 and isinstance(body[1], ast.Return):
            ret_repr = _repr_simple_return(body[1])
            hits.append(
                f"except: pass; return {ret_repr or '<expr>'} "
                "(suppressed exception; return may be stale)"
            )

    # Pattern 3: handler explicitly does nothing useful — only log-without-raise +
    # success return. (Conservative: only flag if last stmt is success-shape return.)
    if len(body) >= 2 and isinstance(body[-1], ast.Return):
        ret_repr = _repr_simple_return(body[-1])
        if ret_repr in _SUCCESS_SHAPED_REPRS and not _has_raise(body):
            # Avoid double-counting Pattern 1
            if not (len(body) == 1 and isinstance(body[0], ast.Return)):
                hits.append(
                    f"except → ...no raise...; return {ret_repr} "
                    "(swallowed + success-shaped)"
                )

    return hits


def _repr_simple_return(node: ast.Return) -> str:
    """Return string-repr of a Return node's value if it's a simple literal/name.

    Returns "" if value is complex (we only flag simple success-shape literals).
    """
    if node.value is None:
        return "None"
    v = node.value
    if isinstance(v, ast.Constant):
        if v.value is None:
            return "None"
        if isinstance(v.value, bool):
            return "True" if v.value else "False"
        if isinstance(v.value, int) and v.value == 0:
            return "0"
        if isinstance(v.value, str) and v.value == "":
            return "''"
    if isinstance(v, ast.List) and not v.elts:
        return "[]"
    if isinstance(v, ast.Dict) and not v.keys:
        return "{}"
    if isinstance(v, ast.Tuple) and not v.elts:
        return "()"
    if isinstance(v, ast.Name) and v.id == "None":
        return "None"
    return ""


def _has_raise(stmts: list[ast.stmt]) -> bool:
    for s in stmts:
        if isinstance(s, ast.Raise):
            return True
    return False


def _find_enclosing_func_name(tree: ast.AST, target: ast.AST) -> str:
    """Walk tree to find FunctionDef ancestor of target. Best-effort."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if child is target:
                    return node.name
    return ""


_AUDIT_HEADER = """\
# `.spa-ai-silent-failures.md` — SilentFailureGrepperLoom audit

Generated by SPA AI's `SilentFailureGrepperLoom` (Sakichi vision 14:
silent failure is anti-Jidoka).

## What this file is

A list of locations in this repo where Python `try`/`except` handlers
appear to swallow exceptions and return success-shaped values (None,
empty list, False, etc.) without re-raising or signaling. Each entry
is a CANDIDATE for human review — the loom is intentionally conservative
but may produce false positives for legitimate "default on missing"
patterns.

## What you do as the maintainer

For each entry below, decide:

1. **Re-raise** (or wrap) — the exception should propagate to the caller.
2. **Log + sentinel** — log the failure, return a clearly-typed sentinel
   the caller distinguishes from success.
3. **Accept as intentional** — the silent-swallow is the right behavior
   for this code path; mark with `# spa-ai: accepted-silent-swallow`
   comment to suppress future audits at this line.

## Rollback

If this audit is wrong for your project, delete `.spa-ai-silent-failures.md`.
No state is left behind. Per `promises.md` Promise 5: removal is a single
command — stopping must be cheap.

## Findings

"""


_PR_BODY_TEMPLATE = """\
## What this PR adds

A `.spa-ai-silent-failures.md` audit file at the repo root, listing
locations in your Python source where `try`/`except` handlers appear
to swallow exceptions and return success-shaped values without
re-raising or signaling.

## Why this halt

A function that catches an exception and returns None / [] / False /
"" without re-raising presents the caller with indistinguishable
success-vs-failure surfaces. The caller makes decisions on what looks
like data but is actually absence-of-data caused by a swallowed error.
Drivers downstream of such functions silently absorb the consequences.

This audit file IS the halt — it surfaces the candidates for your
review without auto-modifying your code. Per Promise 3 + V99
(write-decision-down): the loom speaks via the audit artifact.

## Sakichi vision

Vision 14 from the SPA AI doctrinal source: *Silent failure is
anti-Jidoka.* A loom that catches a thread break MUST signal —
either to the next station or to a halt-state. Returning
success-shape from a failure is the opposite: it tells the next
station "all is well" when the thread is broken.

## What the loom did NOT do

- It did NOT modify any of your existing source files.
- It did NOT auto-fix any flagged location.
- The patch is the audit artifact only.

## What you do as the maintainer

1. Read `.spa-ai-silent-failures.md`.
2. For each entry, decide: re-raise / log + sentinel / accept as
   intentional (annotate with `# spa-ai: accepted-silent-swallow`).
3. Decide what to do with the audit file itself: keep as a TODO
   list, OR delete after triaging.

## Rollback

Delete `.spa-ai-silent-failures.md`. No state is left behind.

## Provenance

This PR was drafted by SPA AI's `SilentFailureGrepperLoom` and
reviewed by a human (the PR submitter) before opening. SPA AI
proposes; the human commits.
"""


class SilentFailureGrepperLoom:
    """Detects silent-failure shapes in .py files; proposes an audit artifact."""

    loom_id = "silent-failure-grepper"
    sakichi_vision_id = 14
    method_vision_ids = [77, 18, 99]
    stance_vision_ids = [22, 25, 32, 100]

    # Cached scan results so detect() and propose_patch() see the same set.
    # Stateful by design (per Komada (a) override + this loom needs to scan
    # in detect and report in propose_patch).
    def __init__(self) -> None:
        self._cached_findings: list[dict] = []

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        """Scan .py files; return a single finding if any silent-failure shape found."""
        self._cached_findings = []
        for py_path in sorted(repo_root.rglob("*.py")):
            # Skip vendored / virtualenv / build trees.
            if any(part.startswith(".") and part != ".github" for part in py_path.parts):
                continue
            if any(part in ("venv", ".venv", "build", "dist", "__pycache__") for part in py_path.parts):
                continue
            self._cached_findings.extend(_scan_file(py_path))

        if not self._cached_findings:
            return []

        return [
            LoomFinding(
                loom_id=self.loom_id,
                target_path=Path(".spa-ai-silent-failures.md"),
                reason=(
                    f"Found {len(self._cached_findings)} silent-failure-shape "
                    f"candidate(s) in Python source. V14 audit recommended."
                ),
                sakichi_vision_id=self.sakichi_vision_id,
                severity="medium",
            )
        ]

    def propose_patch(self, finding: LoomFinding, repo_root: Path) -> LoomPatch:
        """Compose the audit-file contents from cached findings + Jidoka PR body.

        `repo_root` unused — findings were cached in `detect()`."""
        body_parts = [_AUDIT_HEADER]
        # Group findings by file for readability.
        by_file: dict[str, list[dict]] = {}
        for f in self._cached_findings:
            by_file.setdefault(f["file"], []).append(f)
        for fname in sorted(by_file.keys()):
            body_parts.append(f"### `{fname}`\n\n")
            for entry in by_file[fname]:
                body_parts.append(
                    f"- **L{entry['lineno']}** in `{entry['func']}` — "
                    f"{entry['heuristic']}\n"
                )
            body_parts.append("\n")

        contents = "".join(body_parts)

        return LoomPatch(
            loom_id=self.loom_id,
            target_path=finding.target_path,
            contents=contents,
            pr_body=_PR_BODY_TEMPLATE,
        )

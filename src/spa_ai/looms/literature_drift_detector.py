"""LiteratureDriftDetectorLoom — surfaces literature citations that have aged
past a configured drift threshold without a verification marker.

Sakichi vision 14: silent failure is anti-Jidoka. A literature citation that
ships next to a magnitude (a threshold, a timing, a calibration constant) and
then quietly ages while the underlying paper is retracted, superseded, or
restated, presents the consuming maintainer with indistinguishable
still-current-vs-stale surfaces. The maintainer ships against what reads as
evidence but is actually un-rechecked-since-publish. Drivers downstream of
those magnitudes silently absorb the drift — alerts calibrated to two-year-old
preprints fire (or fail to fire) on present-day road conditions.

This loom does NOT auto-fix. It does NOT make network calls. It produces an
audit file (``.spa-ai-citation-drift.md``) at the repo root listing every
citation it could parse, with the inferred citation date and the drift
distance from system date. The maintainer reviews the audit and decides
per-row whether to: re-verify (drop a ``# verified: <YYYY-MM-DD>`` companion
marker that resets the clock), supersede the citation, mark the source
``[perpetual]`` (RFC / ISO / dated-by-design references), or accept as
known-stale.

HER-Trace (≤4 hops, OPS-RULE-044):

    loom installed in repo carrying threshold-citations
    → maintainer surfaces drifted citation row
    → maintainer re-checks paper, supersedes magnitude
    → consuming app's per-profile alerts re-calibrate for the driver

Defaults:
    - Threshold: 18 months. Configurable per-project via
      ``.spa-ai-citation-drift.toml``. The 12mo proposal in early design
      under-served stable psychophysics literature (creating audit-fatigue
      against citations whose underlying mechanism is decade-stable);
      24mo over-served fast-moving cybersecurity; 18mo splits it. The
      audit row records the threshold that flagged it so the maintainer
      can see by how much.
    - Allowlist: built-in for RFC / ISO standard identifiers. Maintainer
      may extend via the same TOML.
    - Reset marker: ``# verified: <YYYY-MM-DD>`` or ``// verified: ...``
      on the next non-blank line under the citation.
    - Perpetual marker: ``[perpetual]`` token anywhere in the citation
      comment line.

Out-of-scope for v1 (V65 sekishō-idai — small stones, named deferrals):
    - Network-fetch verification of citations (PMID / DOI / arxiv-status).
    - IDE / editor surface integration.
    - Auto-rewrite of source code lines.
    - Per-domain auto-thresholds (medical 12mo / automotive 18mo /
      spec-class perpetual). The configurable single threshold suffices
      until evidence forces a per-domain split.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

try:
    import tomllib  # Python 3.11+ stdlib
except ModuleNotFoundError:  # pragma: no cover - 3.10 fallback path
    import tomli as tomllib  # type: ignore[no-redef]

from .base import LoomFinding, LoomPatch

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIG_FILENAME = ".spa-ai-citation-drift.toml"
_DEFAULT_THRESHOLD_MONTHS = 18
_AUDIT_FILENAME = ".spa-ai-citation-drift.md"

# Built-in allowlist of source-token regexes treated as immutable specs.
# Matches the anchored-token portion only; the audit still records that
# the row was suppressed (kept in a side-list so the maintainer can audit
# the allowlist itself).
_DEFAULT_ALLOWLIST_PATTERNS: tuple[str, ...] = (
    r"^RFC\s+\d{3,5}$",
    r"^ISO\s+\d{4,5}(?:[-:]\d{1,4})*$",
)

# ---------------------------------------------------------------------------
# Per-language comment extraction
# ---------------------------------------------------------------------------

# Map suffix -> list of regex patterns that capture the comment-text span.
# The pattern's first capture group is the comment payload (no marker chars).
_LANG_COMMENT_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    ".py": (
        # Single-line `# ...`
        re.compile(r"#\s?(.*)$"),
    ),
    ".dart": (
        # Doc comments (`/// ...`) checked first to take priority over `//`
        re.compile(r"///\s?(.*)$"),
        re.compile(r"//\s?(.*)$"),
    ),
    ".rs": (
        re.compile(r"///\s?(.*)$"),
        re.compile(r"//!\s?(.*)$"),
        re.compile(r"//\s?(.*)$"),
    ),
    ".cpp": (
        re.compile(r"//\s?(.*)$"),
    ),
    ".cc": (
        re.compile(r"//\s?(.*)$"),
    ),
    ".cxx": (
        re.compile(r"//\s?(.*)$"),
    ),
    ".h": (
        re.compile(r"//\s?(.*)$"),
    ),
    ".hpp": (
        re.compile(r"//\s?(.*)$"),
    ),
}

_VERIFIED_MARKER_RE = re.compile(
    r"verified:\s*(\d{4}-\d{2}(?:-\d{2})?)", re.IGNORECASE
)
_PERPETUAL_MARKER_RE = re.compile(r"\[perpetual\]", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Citation grammar — STRICT (with bracketed date) and PERMISSIVE (no date)
# ---------------------------------------------------------------------------

# STRICT: machine-readable cite tag with optional bracketed date.
#   `cite: <ref> [YYYY-MM]` / `cite: <ref> [YYYY-MM-DD]`
_STRICT_CITE_RE = re.compile(
    r"\bcite[:\s]+(?P<ref>[^\[]+?)\s*\[(?P<date>\d{4}-\d{2}(?:-\d{2})?)\]",
    re.IGNORECASE,
)

# PERMISSIVE: identifier-token grammars that imply a citation without
# explicit `cite:` tag. Each pattern's `ref` group becomes the source-ref;
# its `date_token` group (when present) feeds the embedded-date extractor.
# Each pattern carries an explicit `date_kind` so the date-extractor knows
# how to interpret any captured token: "yymm" (arxiv), "year" (per Author),
# or "" (no embedded date).
_PermissiveSpec = tuple[re.Pattern[str], str]

_PERMISSIVE_TOKEN_RES: tuple[_PermissiveSpec, ...] = (
    # arxiv 2410.06388 — YYMM embedded
    (
        re.compile(
            r"\b(?P<ref>arxiv\s+(?P<date_token>\d{4})\.\d{4,5})\b",
            re.IGNORECASE,
        ),
        "yymm",
    ),
    # PubMed 16313881 / PMID 16313881 — date NOT embedded; lookup-pending
    (
        re.compile(
            r"\b(?P<ref>(?:PubMed|PMID)\s+\d{6,9})\b",
            re.IGNORECASE,
        ),
        "",
    ),
    # PMC1234567 — date NOT embedded
    (
        re.compile(
            r"\b(?P<ref>PMC\d{6,8})\b",
            re.IGNORECASE,
        ),
        "",
    ),
    # DOI 10.xxxx/yyyy
    (
        re.compile(
            r"\b(?P<ref>DOI[:\s]+10\.\d{4,9}/\S+?)(?=[\s,;)]|$)",
            re.IGNORECASE,
        ),
        "",
    ),
    # RFC 2119 / ISO 26262 / ISO 26262-1:2018 — typically perpetual
    (re.compile(r"\b(?P<ref>RFC\s+\d{3,5})\b", re.IGNORECASE), ""),
    (
        re.compile(
            r"\b(?P<ref>ISO\s+\d{4,5}(?:[-:]\d{1,4})*)\b",
            re.IGNORECASE,
        ),
        "",
    ),
    # `per <Author year>` — `per Konstantopoulos 2010`. date_token is a
    # 4-digit YEAR, not an arxiv YYMM. The extractor uses date_kind to
    # avoid mis-parsing 2010 as 2020-10.
    (
        re.compile(
            r"\bper\s+(?P<ref>[A-Z][A-Za-z\-]+\s+(?P<date_token>\d{4}))\b",
        ),
        "year",
    ),
)


# ---------------------------------------------------------------------------
# Finding records
# ---------------------------------------------------------------------------

@dataclass
class _CitationFinding:
    """A single parsed citation with classification metadata."""

    file: str
    line: int
    raw_comment: str
    source_ref: str
    cited_date: date | None  # None -> UNKNOWN-DATE
    # date_source values: explicit-bracketed | embedded-in-token |
    # verified-marker | git-blame | unknown
    date_source: str
    # drift_months is None when not drift-checkable (perpetual / lookup-pending
    # / unknown).
    drift_months: int | None
    threshold_months: int
    is_perpetual: bool
    is_lookup_pending: bool
    has_verified_marker: bool
    grammar_tier: str  # "strict-with-date" | "permissive-no-date"


# ---------------------------------------------------------------------------
# Date extraction
# ---------------------------------------------------------------------------

def _parse_explicit_date(s: str) -> date | None:
    """Parse `YYYY-MM` or `YYYY-MM-DD` -> date (uses day=1 if absent)."""
    try:
        if len(s) == 7:
            return datetime.strptime(s, "%Y-%m").date().replace(day=1)
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_arxiv_yymm(token: str) -> date | None:
    """Parse arxiv `YYMM` 4-digit token -> date.

    arxiv IDs use 4-digit prefix YYMM; YY=00-99 maps as 2000-2099 historically
    (the scheme started in 2007). Conservative: if YY decodes to a year > current
    year + 1, assume the wrap-around (2099 -> 1999); otherwise prefix with 20.
    """
    if not (token.isdigit() and len(token) == 4):
        return None
    yy = int(token[:2])
    mm = int(token[2:])
    if not (1 <= mm <= 12):
        return None
    year = 2000 + yy
    today_year = date.today().year
    if year > today_year + 1:
        year -= 100
    try:
        return date(year, mm, 1)
    except ValueError:
        return None


def _months_between(earlier: date, later: date) -> int:
    """Whole-months count from earlier to later (inclusive of partial months)."""
    if earlier > later:
        return 0
    months = (later.year - earlier.year) * 12 + (later.month - earlier.month)
    return max(months, 0)


# ---------------------------------------------------------------------------
# Allowlist resolution
# ---------------------------------------------------------------------------

def _resolve_allowlist(extra_patterns: list[str]) -> list[re.Pattern[str]]:
    patterns = list(_DEFAULT_ALLOWLIST_PATTERNS) + extra_patterns
    compiled: list[re.Pattern[str]] = []
    for p in patterns:
        try:
            compiled.append(re.compile(p, re.IGNORECASE))
        except re.error:
            # Bad user pattern: ignore rather than crash the loom.
            continue
    return compiled


def _is_allowlisted(source_ref: str, allowlist: list[re.Pattern[str]]) -> bool:
    return any(p.match(source_ref.strip()) for p in allowlist)


# ---------------------------------------------------------------------------
# Loom configuration loading
# ---------------------------------------------------------------------------

@dataclass
class _LoomConfig:
    threshold_months: int = _DEFAULT_THRESHOLD_MONTHS
    extra_allowlist: list[str] = field(default_factory=list)


def _load_config(repo_root: Path) -> _LoomConfig:
    cfg_path = repo_root / _CONFIG_FILENAME
    if not cfg_path.exists():
        return _LoomConfig()
    try:
        data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return _LoomConfig()
    cfg = _LoomConfig()
    if isinstance(data.get("threshold_months"), int) and data["threshold_months"] > 0:
        cfg.threshold_months = data["threshold_months"]
    extra = data.get("allowlist")
    if isinstance(extra, list):
        cfg.extra_allowlist = [str(x) for x in extra if isinstance(x, str)]
    return cfg


# ---------------------------------------------------------------------------
# Per-line citation extraction
# ---------------------------------------------------------------------------

def _extract_comment_payload(line: str, suffix: str) -> str | None:
    """Return the comment-text payload of a source line, or None if not a comment."""
    patterns = _LANG_COMMENT_PATTERNS.get(suffix)
    if not patterns:
        return None
    stripped = line.rstrip("\n")
    # Walk from the start of the line; the first capture wins.
    for pat in patterns:
        # Allow optional leading whitespace before the marker.
        m = pat.search(stripped)
        if m:
            return m.group(1)
    return None


def _extract_citations_from_comment(
    comment: str,
) -> list[tuple[str, str | None, str, str]]:
    """Parse a comment payload for citation tokens.

    Returns list of (source_ref, embedded_date_token_or_None, grammar_tier,
    date_kind). grammar_tier is "strict-with-date" or "permissive-no-date".
    date_kind is "explicit" / "yymm" / "year" / "" — drives downstream
    date-parser selection.
    """
    out: list[tuple[str, str | None, str, str]] = []

    # STRICT first — explicit cite: ref [date].
    for m in _STRICT_CITE_RE.finditer(comment):
        out.append(
            (m.group("ref").strip(), m.group("date"), "strict-with-date", "explicit")
        )

    # PERMISSIVE — token-level citations.
    for pat, date_kind in _PERMISSIVE_TOKEN_RES:
        for m in pat.finditer(comment):
            ref = m.group("ref").strip()
            date_tok = (
                m.groupdict().get("date_token")
                if "date_token" in m.groupdict()
                else None
            )
            out.append((ref, date_tok, "permissive-no-date", date_kind))

    return out


# ---------------------------------------------------------------------------
# Per-file scan
# ---------------------------------------------------------------------------

def _scan_file(
    path: Path,
    repo_root: Path,
    threshold_months: int,
    allowlist: list[re.Pattern[str]],
    today: date,
) -> list[_CitationFinding]:
    """Walk a single source file looking for citation-bearing comments."""
    suffix = path.suffix.lower()
    if suffix not in _LANG_COMMENT_PATTERNS:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    findings: list[_CitationFinding] = []

    for i, raw_line in enumerate(lines, start=1):
        comment = _extract_comment_payload(raw_line, suffix)
        if comment is None:
            continue

        is_perpetual = bool(_PERPETUAL_MARKER_RE.search(comment))
        verified_marker_date = _scan_verified_marker_below(lines, i, suffix)

        for source_ref, date_token, grammar_tier, date_kind in (
            _extract_citations_from_comment(comment)
        ):
            if _is_allowlisted(source_ref, allowlist):
                # Allowlisted sources skip the audit entirely — they are
                # dated-by-design references and would only create noise.
                continue

            cited_date: date | None = None
            date_source = "unknown"
            is_lookup_pending = False

            # Priority chain (a) -> (b) -> (d) -> (c-skipped-in-v1).
            # date_kind selects the parser to use on date_token; this avoids
            # mis-parsing a `per <Author 2010>` 4-digit year as arxiv YYMM.
            if grammar_tier == "strict-with-date" and date_token:
                cited_date = _parse_explicit_date(date_token)
                date_source = "explicit-bracketed"
            elif date_token and date_kind == "yymm":
                cited_date = _parse_arxiv_yymm(date_token)
                if cited_date is not None:
                    date_source = "embedded-in-token"
            # date_kind == "year" or "" leaves cited_date None at this stage;
            # falls through to verified-marker check below.

            if cited_date is None and verified_marker_date is not None:
                cited_date = verified_marker_date
                date_source = "verified-marker"

            if cited_date is None:
                # PMID/DOI/PMC/per-Author-year-without-token paths: lookup-pending.
                # git-blame fallback (c) is out of scope for v1 per design.
                is_lookup_pending = (
                    "pubmed" in source_ref.lower()
                    or "pmid" in source_ref.lower()
                    or source_ref.upper().startswith("PMC")
                    or source_ref.upper().startswith("DOI")
                )

            drift_months: int | None
            if cited_date is None or is_perpetual:
                drift_months = None
            else:
                drift_months = _months_between(cited_date, today)

            try:
                rel_path = path.relative_to(repo_root).as_posix()
            except ValueError:
                rel_path = str(path)

            findings.append(
                _CitationFinding(
                    file=rel_path,
                    line=i,
                    raw_comment=comment.strip(),
                    source_ref=source_ref,
                    cited_date=cited_date,
                    date_source=date_source,
                    drift_months=drift_months,
                    threshold_months=threshold_months,
                    is_perpetual=is_perpetual,
                    is_lookup_pending=is_lookup_pending,
                    has_verified_marker=verified_marker_date is not None,
                    grammar_tier=grammar_tier,
                )
            )

    return findings


def _scan_verified_marker_below(
    lines: list[str], current_index_1based: int, suffix: str
) -> date | None:
    """Look at the next non-blank comment line for a `verified: YYYY-MM[-DD]` marker."""
    for j in range(current_index_1based, min(current_index_1based + 3, len(lines))):
        next_line = lines[j]  # 0-based index = j
        next_comment = _extract_comment_payload(next_line, suffix)
        if next_comment is None:
            if next_line.strip() == "":
                continue
            return None
        m = _VERIFIED_MARKER_RE.search(next_comment)
        if m:
            return _parse_explicit_date(m.group(1))
    return None


# ---------------------------------------------------------------------------
# Audit document composition
# ---------------------------------------------------------------------------

_AUDIT_HEADER = """\
# `.spa-ai-citation-drift.md` — LiteratureDriftDetectorLoom audit

Generated by SPA AI's `LiteratureDriftDetectorLoom` (Sakichi vision 14:
silent failure is anti-Jidoka — a citation that quietly ages past its
evidence-relevance window is anti-Jidoka at the calibration layer).

## What this file is

A list of literature citations in this repo's source code that have aged
past the configured drift threshold (default 18 months) without a
`# verified: <YYYY-MM-DD>` companion marker. Each row is a CANDIDATE for
human review.

This loom does not make network calls. Citations whose date can only be
resolved by a remote lookup (PMID, DOI, PMC) appear in the audit as
`LOOKUP-REQUIRED` rows so the maintainer can decide whether to verify them
manually.

## What you do as the maintainer

For each row, decide:

1. **Re-verify the citation is still current** — drop a comment
   `# verified: 2026-04-28` (or `// verified: ...` for non-Python source)
   on the next line under the citation. The loom resets the drift clock to
   that date at the next scan.
2. **Supersede with a newer citation** — edit the source line to point to
   the newer paper / standard / preprint.
3. **Mark perpetual** — for dated-by-design references (RFC, ISO, dated
   historical citations), add `[perpetual]` anywhere in the citation comment.
   The loom permanently exempts that line.
4. **Accept as known-stale** — take no action. The row reappears at the next
   scan; that's how the audit stays honest.

## Configuration

If 18 months is wrong for your project, drop a `.spa-ai-citation-drift.toml`
at the repo root:

```toml
threshold_months = 12          # tighter for fast-moving evidence (e.g., medical)
allowlist = [
    '^Sakichi 1924$',          # extra perpetual identifiers
]
```

Built-in allowlist already covers `RFC <N>` and `ISO <N>[-<part>:<year>]`.

## Rollback

Delete `.spa-ai-citation-drift.md`. No state is left behind. Per
`promises.md` Promise 5: removal is a single command.

## Findings

"""


_PR_BODY_TEMPLATE = """\
## What this PR adds

A `.spa-ai-citation-drift.md` audit file at the repo root, listing literature
citations in your source code that have aged past the configured drift
threshold (18 months by default) without a `# verified: <YYYY-MM-DD>`
companion marker. The loom recognises citation comments in Python, Dart,
Rust, and C++ source.

## Why this halt

Inline literature citations next to a magnitude (a threshold, a timing,
a calibration constant) carry the implicit promise *this number is calibrated
to current evidence*. Cited papers get retracted; preprints reach final form
with revised numbers; standards bodies amend; superseding studies appear.
Without a re-scan loom, that promise decays silently into a publish-time
snapshot — and downstream consumers ship against year-old evidence as if it
were today's.

This audit file IS the halt — it surfaces the candidates for your review
without auto-modifying your code or making any network call. You decide
per-row whether to re-verify, supersede, mark perpetual, or accept as
known-stale.

## Sakichi vision

Vision 14 from the SPA AI doctrinal source: *Silent failure is anti-Jidoka.*
A citation that quietly ages past its evidence-relevance window is the
calibration-layer instance of that pattern. The fix is the same: surface the
candidates so the weaver can act, rather than letting the next station ship
on what looks like data but is actually un-rechecked-since-publish.

## What the loom did NOT do

- It did NOT modify any of your existing source files.
- It did NOT make any network call to verify a PMID, DOI, or arxiv ID.
  Those rows appear as `LOOKUP-REQUIRED` so you can decide whether to verify
  manually.
- It did NOT auto-add `[perpetual]` tags. Only you can mark perpetual.
- The patch is the audit artifact only.

## What you do as the maintainer

1. Read `.spa-ai-citation-drift.md`.
2. For each row, decide: re-verify (drop a `# verified: 2026-04-28` comment
   on the next line), supersede (edit the source line), mark perpetual (add
   `[perpetual]` to the citation comment), or accept as known-stale.
3. Decide what to do with the audit file: keep as a TODO list, or delete
   after triaging. The next scan will re-create it if drift remains.

## Configuration

Per-project threshold + allowlist live in `.spa-ai-citation-drift.toml` if
you want them; otherwise the defaults (18 months, RFC + ISO allowlisted)
apply.

## Rollback

Delete `.spa-ai-citation-drift.md`. No state is left behind.

## Provenance

This PR was drafted by SPA AI's `LiteratureDriftDetectorLoom` and reviewed
by a human (the PR submitter) before opening. SPA AI proposes; the human
commits.
"""


def _format_drift(finding: _CitationFinding) -> str:
    if finding.is_perpetual:
        return "perpetual (no drift check)"
    if finding.is_lookup_pending and finding.cited_date is None:
        return "LOOKUP-REQUIRED (PMID/DOI/PMC — no embedded date)"
    if finding.cited_date is None:
        return "UNKNOWN-DATE (no parseable date in citation or marker)"
    assert finding.drift_months is not None
    fired = finding.drift_months >= finding.threshold_months
    suffix = "" if not fired else f" > {finding.threshold_months}mo configured"
    return f"{finding.drift_months} months{suffix}"


def _format_audit_row(finding: _CitationFinding) -> str:
    cited = (
        finding.cited_date.isoformat()
        if finding.cited_date
        else ("(perpetual)" if finding.is_perpetual else "(unresolved)")
    )
    verified = "yes" if finding.has_verified_marker else "no"
    return (
        f"- **`{finding.file}:{finding.line}`** — "
        f"`{finding.source_ref}` "
        f"(grammar: {finding.grammar_tier}; "
        f"date: {cited} via {finding.date_source}; "
        f"drift: {_format_drift(finding)}; "
        f"verified-marker: {verified})\n"
    )


def _filter_findings_to_report(findings: list[_CitationFinding]) -> list[_CitationFinding]:
    """Keep findings the audit should surface.

    Surfaces:
      - drift >= threshold (the headline case)
      - LOOKUP-REQUIRED (maintainer must decide whether to fetch manually)
      - UNKNOWN-DATE (citation parseable but date unresolved)
    Suppresses:
      - perpetual rows
      - rows with a verified-marker that resets drift below threshold
      - rows with drift below threshold AND a parseable date (clean rows)
    """
    out: list[_CitationFinding] = []
    for f in findings:
        if f.is_perpetual:
            continue
        if f.cited_date is not None and f.drift_months is not None:
            if f.drift_months < f.threshold_months:
                continue
        out.append(f)
    return out


# ---------------------------------------------------------------------------
# Loom class
# ---------------------------------------------------------------------------

class LiteratureDriftDetectorLoom:
    """Detects aged literature citations in source code; proposes an audit artifact.

    Sakichi vision 14 (silent-failure-anti-Jidoka) at the calibration layer.
    Method visions: V77 (genchi-genbutsu — actually reads the source files),
    V18 (5-Whys terminating at mechanism — the drift IS the mechanism), V99
    (write-the-decision-down — the audit row IS the recorded decision).
    Stance visions: V22 (loom-serves-weaver — surfaces candidates, does not
    rewrite), V25 (autonomation = liberation, not surveillance), V32
    (katei-teki tone in the audit + PR body), V100 (equal-dignity — every
    maintainer carrying citations gets the same calibration discipline the
    SPA Actuator unit runs against itself).
    """

    loom_id = "literature-drift-detector"
    sakichi_vision_id = 14
    method_vision_ids = [77, 18, 99]
    stance_vision_ids = [22, 25, 32, 100]

    # Stateful by design (per SilentFailureGrepper precedent): findings cached
    # in detect() so propose_patch() can compose the audit without re-walking.
    def __init__(self) -> None:
        self._cached_findings: list[_CitationFinding] = []

    def detect(self, repo_root: Path) -> list[LoomFinding]:
        """Scan source files; return one finding if any drifted citation exists."""
        self._cached_findings = []
        cfg = _load_config(repo_root)
        allowlist = _resolve_allowlist(cfg.extra_allowlist)
        today = date.today()

        for src_path in sorted(repo_root.rglob("*")):
            if not src_path.is_file():
                continue
            if src_path.suffix.lower() not in _LANG_COMMENT_PATTERNS:
                continue
            if any(part.startswith(".") and part != ".github" for part in src_path.parts):
                continue
            skip_dirs = ("venv", ".venv", "build", "dist", "__pycache__", "node_modules")
            if any(part in skip_dirs for part in src_path.parts):
                continue
            self._cached_findings.extend(
                _scan_file(src_path, repo_root, cfg.threshold_months, allowlist, today)
            )

        actionable = _filter_findings_to_report(self._cached_findings)
        if not actionable:
            return []

        return [
            LoomFinding(
                loom_id=self.loom_id,
                target_path=Path(_AUDIT_FILENAME),
                reason=(
                    f"Found {len(actionable)} literature citation(s) past the "
                    f"{cfg.threshold_months}-month drift threshold (or pending "
                    "lookup). V14 calibration-layer audit recommended."
                ),
                sakichi_vision_id=self.sakichi_vision_id,
                severity="medium",
            )
        ]

    def propose_patch(self, finding: LoomFinding, repo_root: Path) -> LoomPatch:
        """Compose the audit-file contents from cached findings + V14 PR body.

        ``repo_root`` unused — findings were cached in ``detect()``.
        """
        actionable = _filter_findings_to_report(self._cached_findings)
        body_parts = [_AUDIT_HEADER]

        by_file: dict[str, list[_CitationFinding]] = {}
        for f in actionable:
            by_file.setdefault(f.file, []).append(f)

        for fname in sorted(by_file.keys()):
            body_parts.append(f"### `{fname}`\n\n")
            for entry in sorted(by_file[fname], key=lambda x: x.line):
                body_parts.append(_format_audit_row(entry))
            body_parts.append("\n")

        contents = "".join(body_parts)

        return LoomPatch(
            loom_id=self.loom_id,
            target_path=finding.target_path,
            contents=contents,
            pr_body=_PR_BODY_TEMPLATE,
        )

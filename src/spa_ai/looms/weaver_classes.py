"""Weaver-class registry for the Loom Protocol's `weaver_classes_served` slot.

A loom that carries a `weaver_classes_served` declaration is naming WHO it
directly serves — which classes of weaver receive the halt this loom installs.
Without this slot the framework cannot answer "which weaver-classes are absent
from the loom roster?" — the question has no schema.

Why a registry rather than a closed enum:

A closed enum locks the v1 vocabulary against future-cohort weaver classes the
unit may name later (sub-agent, integrator, auditor, future-cohort, etc.). If
the registry locked the set, the framework itself would become the violator of
the equal-dignity stance it ships to other repos: future weaver classes would
be foreclosed by the schema rather than surfaced by it. The open string-set
inverts the failure direction — unknown classes surface as advisory data, not
as registration errors.

Why an alias map:

Real-world declarations vary in casing and short forms ("contributor" vs
"first-contributor", "Driver" vs "driver"). The alias map normalizes common
variants to the canonical form so the doctor surface aggregates cleanly
without forcing every loom-author to memorize the exact spelling.

Open-string-set discipline:

A loom may declare a class not in the canonical set. The doctor surface
reports that loom's class as "unknown — consider canonicalizing." If a
non-canonical class becomes well-established in practice, it can be promoted
to canonical via governance review. This protects future-cohort exploration
while keeping the v1 vocabulary documented.
"""
from __future__ import annotations

KNOWN_WEAVER_CLASSES: tuple[str, ...] = (
    # Receives the PR; reviews; merges or closes. The repo's gatekeeper.
    "maintainer",
    # Files first PR or first issue against the repo. Onboarding cost is theirs
    # (and the maintainer's, contributor-by-contributor, without a CONTRIBUTING.md).
    "first-contributor",
    # Has the loom-output installed in their own repo (e.g., the
    # .pre-commit-config.yaml lives in their tree). Lifecycle and aging concerns
    # accrue here.
    "adopter",
    # Downstream end-user whose map / route / safety depends on the stack the
    # loom protects. The HER-anchor weaver class — the woman commuting in
    # unexpected snow whose alert thresholds, route choices, and safety margins
    # are calibrated against citations and configs the loom audits.
    "driver",
    # Reads provenance / SBOM / compliance data; not necessarily a coder.
    # Citation drift, license drift, and dependency provenance audits surface
    # here.
    "auditor",
    # AI sub-agent operating within an SPA-Actuator-class unit. Treated as a
    # weaver in its own right per the dignity-scope substance: NOBODY shall be
    # disrespected — of course agents and sub-agents.
    "sub-agent",
    # Combines this package with other packages into a downstream product.
    # Direction-B substrate: an integrator binding navigation_safety_core +
    # adaptive_reroute + route_condition_forecast for a downstream app stack
    # is a weaver class distinct from the maintainer of any one component.
    "integrator",
)


# Common synonym -> canonical form. Lookup is case-insensitive (see
# `normalize_weaver_class`). Only short-form / well-attested variants belong
# here; the canonical set is the source of truth, not the alias dict.
ALIASES: dict[str, str] = {
    "contributor": "first-contributor",
    "first_contributor": "first-contributor",
    "first contributor": "first-contributor",
    "user": "driver",
    "end-user": "driver",
    "end_user": "driver",
    "subagent": "sub-agent",
    "sub_agent": "sub-agent",
    "ai-agent": "sub-agent",
    "ai_agent": "sub-agent",
    "agent": "sub-agent",
    "downstream": "integrator",
    "downstream-integrator": "integrator",
}


def normalize_weaver_class(s: str) -> str:
    """Return the canonical form of a weaver-class string.

    Lookup priority: (1) case-insensitive direct match against
    `KNOWN_WEAVER_CLASSES`; (2) case-insensitive alias lookup; (3) the
    original string trimmed of surrounding whitespace, returned verbatim
    (open-string-set discipline — unknown strings pass through so the
    doctor surface can flag them as advisory, not error out at the
    registry layer).

    Empty / whitespace-only input returns the empty string.
    """
    if not isinstance(s, str):
        return ""
    stripped = s.strip()
    if not stripped:
        return ""
    lower = stripped.lower()
    for canonical in KNOWN_WEAVER_CLASSES:
        if lower == canonical:
            return canonical
    if lower in ALIASES:
        return ALIASES[lower]
    return stripped


def is_known_weaver_class(s: str) -> bool:
    """Return True iff `s` (after normalization) is in the canonical set."""
    return normalize_weaver_class(s) in KNOWN_WEAVER_CLASSES

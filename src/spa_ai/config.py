"""SPA AI runtime configuration.

Held minimal in v0.1 — most decisions are deferred until the first
LLM-driven loom needs them. Per principles.md V65 (Sekishō-idai),
do not pre-build configuration surface for futures we have not earned.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SPAConfig:
    """SPA AI configuration.

    Attributes:
        anthropic_api_key: API key for the Anthropic SDK. Unused in v0.1
            (the first two looms are deterministic), present so the
            shape exists for future LLM-driven looms.
    """

    anthropic_api_key: str | None = None

    @classmethod
    def from_env(cls) -> SPAConfig:
        """Load config from environment variables."""
        return cls(anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"))

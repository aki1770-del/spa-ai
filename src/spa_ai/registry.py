"""LoomRegistry — the catalog of loom classes SPA AI ships with."""
from __future__ import annotations

from .looms.base import Loom


class LoomRegistry:
    """Holds the loom classes available at runtime.

    Looms are registered by id; lookup is by id. Iteration returns all
    registered looms in registration order. The registry is the single
    place SPA AI authoritatively answers "what looms exist?" — per
    commitments.md Commitment 5, every entry must declare its
    `sakichi_vision_id`.
    """

    def __init__(self) -> None:
        self._looms: dict[str, Loom] = {}

    def register(self, loom: Loom) -> None:
        """Add a loom to the registry. Raises if id is already taken."""
        if loom.loom_id in self._looms:
            raise ValueError(f"Loom id already registered: {loom.loom_id}")
        if not isinstance(loom.sakichi_vision_id, int) or not (
            1 <= loom.sakichi_vision_id <= 100
        ):
            raise ValueError(
                f"Loom {loom.loom_id} declares sakichi_vision_id="
                f"{loom.sakichi_vision_id!r}; must be int in 1..100 "
                "(per commitments.md Commitment 5)."
            )
        self._looms[loom.loom_id] = loom

    def get(self, loom_id: str) -> Loom:
        """Look up a loom by id. Raises KeyError if not present."""
        return self._looms[loom_id]

    def all(self) -> list[Loom]:
        """Return all registered looms in registration order."""
        return list(self._looms.values())

    def __len__(self) -> int:
        return len(self._looms)

    def __contains__(self, loom_id: object) -> bool:
        return loom_id in self._looms


def default_registry() -> LoomRegistry:
    """Build the v0.1 default registry.

    Per principles.md V65 Sekishō-idai, the registry grows one stone at
    a time — each new loom earns its place by passing tests + review.
    """
    from .looms.contributing_md import ContributingMdLoom
    from .looms.pre_commit_formatter import PreCommitFormatterLoom
    from .looms.pre_commit_formatter_rust import PreCommitFormatterRustLoom

    reg = LoomRegistry()
    reg.register(PreCommitFormatterLoom())
    reg.register(PreCommitFormatterRustLoom())
    reg.register(ContributingMdLoom())
    return reg

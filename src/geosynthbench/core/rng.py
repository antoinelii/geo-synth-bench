from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from random import Random
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RNG:
    """Thin wrapper around random.Random for deterministic sampling."""

    seed: int

    def _r(self) -> Random:
        # Create a local Random instance so RNG stays immutable/pure.
        return Random(self.seed)

    def randint(self, a: int, b: int) -> int:
        return self._r().randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        return self._r().uniform(a, b)

    def choice(self, xs: Sequence[T]) -> T:
        if not xs:
            raise ValueError("choice() on empty sequence")
        return self._r().choice(list(xs))

    def sample(self, xs: Sequence[T], k: int) -> list[T]:
        if k < 0:
            raise ValueError("sample() k must be >= 0")
        if k > len(xs):
            raise ValueError("sample() k must be <= len(xs)")
        return self._r().sample(list(xs), k)

    def shuffle(self, xs: list[T]) -> list[T]:
        r = self._r()
        out = list(xs)
        r.shuffle(out)
        return out

    def split(self, salt: str) -> RNG:
        """
        Create a deterministic sub-RNG from this seed + a salt label.
        This makes it easy to derive independent streams (roads/buildings/etc.)
        without global mutable state.
        """
        # Simple stable mixing: hash is salted per-process, so avoid built-in hash().
        mixed = _mix_seed(self.seed, salt)
        return RNG(seed=mixed)


def _mix_seed(seed: int, salt: str) -> int:
    """
    Deterministic mixing function (stable across runs/processes).
    Uses a small manual hash over the salt string.
    """
    h = 2166136261  # FNV-1a basis
    for ch in salt:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    # Combine
    return (seed ^ h) & 0x7FFFFFFF

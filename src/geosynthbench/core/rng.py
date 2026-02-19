from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from random import Random
from typing import TypeVar

T = TypeVar("T")


@dataclass
class RNG:
    """Deterministic, stateful RNG with convenient substreams."""

    seed: int
    _random: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._random = Random(self.seed)

    def randint(self, a: int, b: int) -> int:
        return self._random.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        return self._random.uniform(a, b)

    def choice(self, xs: Sequence[T]) -> T:
        if not xs:
            raise ValueError("choice() on empty sequence")
        return self._random.choice(list(xs))

    def sample(self, xs: Sequence[T], k: int) -> list[T]:
        if k < 0:
            raise ValueError("sample() k must be >= 0")
        if k > len(xs):
            raise ValueError("sample() k must be <= len(xs)")
        return self._random.sample(list(xs), k)

    def shuffle(self, xs: list[T]) -> list[T]:
        out = list(xs)
        self._random.shuffle(out)
        return out

    def split(self, salt: str) -> RNG:
        """Create an independent deterministic RNG stream."""
        return RNG(seed=_mix_seed(self.seed, salt))


def _mix_seed(seed: int, salt: str) -> int:
    # Stable deterministic mixing (no built-in hash() because that is process-salted).
    h = 2166136261  # FNV-1a basis
    for ch in salt:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return (seed ^ h) & 0x7FFFFFFF

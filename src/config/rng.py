from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Final

import numpy as np


def _stable_uint64(*parts: str) -> int:
    """
    Deterministically hash strings into an unsigned 64-bit integer.
    """
    h = hashlib.blake2b(digest_size=8)
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x1f")
    return int.from_bytes(h.digest(), byteorder="little", signed=False)


@dataclass(frozen=True)
class RNGRegistry:
    """
    Deterministic RNG factory based on a single run seed.

    Key idea:
    - each "component name" gets its own independent Generator
    - each sample can further spawn a stable child RNG: spawn(component, sample_idx)

    This avoids accidental cross-talk between modules and makes debugging easier.
    """

    seed: int

    _ALGO: Final[str] = "pcg64dxsm"

    def rng(self, component: str) -> np.random.Generator:
        """
        Component-level RNG (shared across the whole run).
        """
        seed64 = _stable_uint64(str(self.seed), "component", component)
        bitgen = np.random.PCG64DXSM(seed64)
        return np.random.Generator(bitgen)

    def spawn(self, component: str, sample_idx: int) -> np.random.Generator:
        """
        Per-sample RNG for a component.
        """
        seed64 = _stable_uint64(str(self.seed), "component", component, "sample", str(sample_idx))
        bitgen = np.random.PCG64DXSM(seed64)
        return np.random.Generator(bitgen)

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from geosynthbench.config.schemas import SceneConfig
from geosynthbench.core.types import RegionId
from geosynthbench.core.versioning import GENERATOR_VERSION, SCHEMA_VERSION
from geosynthbench.world.entities import Entity


def empty_region_stats() -> dict[RegionId, RegionStats]:
    return {}


def emmpty_entities() -> list[Entity]:
    return []


class Provenance(BaseModel):
    """Captures reproducibility + versioning."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int = Field(..., ge=0)
    schema_version: str = Field(default=SCHEMA_VERSION)
    generator_version: str = Field(default=GENERATOR_VERSION)


class RegionStats(BaseModel):
    """Stats for one region (quadrant) used for prompts/answers/metrics."""

    model_config = ConfigDict(extra="forbid")

    # Pixel-space or world-space areas; for MVP we can use pixel counts later.
    building_count: int = 0
    road_length_px: float = 0.0
    vegetation_area_px: int = 0
    water_area_px: int = 0

    # Extensible aggregate stats
    extras: dict[str, Any] = Field(default_factory=dict)


class GlobalStats(BaseModel):
    """Scene-wide stats."""

    model_config = ConfigDict(extra="forbid")

    building_count: int = 0
    road_length_px: float = 0.0
    vegetation_area_px: int = 0
    water_area_px: int = 0

    extras: dict[str, Any] = Field(default_factory=dict)


class DerivedState(BaseModel):
    """Computed properties derived from entities (filled later by stats module)."""

    model_config = ConfigDict(extra="forbid")

    region_stats: dict[RegionId, RegionStats] = Field(default_factory=empty_region_stats)
    global_stats: GlobalStats = Field(default_factory=GlobalStats)

    # Example relational structure (MVP can leave empty):
    # building_id -> list of road_ids considered adjacent/nearest
    adjacency: dict[str, list[str]] = Field(default_factory=dict)

    # Any other computed fields (density maps, distance transforms, etc.)
    extras: dict[str, Any] = Field(default_factory=dict)


class WorldState(BaseModel):
    """Canonical structured world state. Images/labels are rendered from this."""

    model_config = ConfigDict(extra="forbid")

    scene: SceneConfig
    entities: list[Entity] = Field(default_factory=emmpty_entities)

    # Derived is optional until you run stat computation
    derived: DerivedState | None = None

    provenance: Provenance

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from geosynthbench.core.types import EntityId, LayerType, Polygon, Polyline


class EntityBase(BaseModel):
    """Base entity for a world state. Subclasses define geometry + layer."""

    model_config = ConfigDict(extra="forbid")

    id: EntityId
    layer: LayerType

    # Free-form extensibility for future (materials, classes, confidence, etc.)
    properties: dict[str, Any] = Field(default_factory=dict)


class RoadEntity(EntityBase):
    kind: Literal["road"] = "road"
    layer: LayerType = LayerType.ROADS

    # Centerline polyline in world coordinates (floats). Renderer decides pixel mapping.
    polyline: Polyline

    # Visual width in pixels (MVP). Later could be meters.
    width_px: int = Field(6, ge=1)


class BuildingEntity(EntityBase):
    kind: Literal["building"] = "building"
    layer: LayerType = LayerType.BUILDINGS

    # Footprint polygon (list of points)
    polygon: Polygon


class VegetationEntity(EntityBase):
    kind: Literal["vegetation"] = "vegetation"
    layer: LayerType = LayerType.VEGETATION

    polygon: Polygon


class WaterEntity(EntityBase):
    kind: Literal["water"] = "water"
    layer: LayerType = LayerType.WATER

    polygon: Polygon


# Discriminated union for easy parsing/serialization
Entity = RoadEntity | BuildingEntity | VegetationEntity | WaterEntity

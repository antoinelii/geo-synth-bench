from __future__ import annotations

from enum import StrEnum
from typing import NewType

# ---- Strongly-typed identifiers ----
SampleId = NewType("SampleId", str)
EntityId = NewType("EntityId", str)


# ---- Core enums ----
class TaskMode(StrEnum):
    STATIC = "static"
    TEMPORAL = "temporal"


class LayerType(StrEnum):
    ROADS = "roads"
    BUILDINGS = "buildings"
    VEGETATION = "vegetation"
    WATER = "water"


class RegionId(StrEnum):
    # MVP uses quadrants; later you can add tiles (e.g. "r3c2") without breaking schema.
    NW = "NW"
    NE = "NE"
    SW = "SW"
    SE = "SE"


class ChangeType(StrEnum):
    ADD_BUILDING = "add_building"
    REMOVE_BUILDING = "remove_building"
    EXTEND_ROAD = "extend_road"
    CLEAR_VEG = "clear_veg"
    # CLEAR_WATER = "clear_water"
    # ADD_VEG = "add_veg"
    # ADD_WATER = "add_water"


# ---- Geometry aliases (MVP) ----
# Using floats allows later "meters" coordinates; renderer can map to px.
type Point = tuple[float, float]
type Polyline = list[Point]
type Polygon = list[Point]

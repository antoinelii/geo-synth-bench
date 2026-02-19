from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from geosynthbench.core.types import Point, RegionId


class RegionPartition(BaseModel):
    """
    Region partitioning for the scene. MVP uses quadrants.
    This structure supports future partitions (tiles, polygons) without changing API.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    width_px: int = Field(..., ge=1)
    height_px: int = Field(..., ge=1)

    kind: str = "quadrants"


def region_for_point_quadrants(p: Point, width_px: int, height_px: int) -> RegionId:
    """
    Assign a point to a quadrant using image coordinate system:
    - x increases to the right
    - y increases downward
    """
    x, y = p
    mid_x = width_px / 2.0
    mid_y = height_px / 2.0

    is_west = x < mid_x
    is_north = y < mid_y

    if is_north and is_west:
        return RegionId.NW
    if is_north and not is_west:
        return RegionId.NE
    if not is_north and is_west:
        return RegionId.SW
    return RegionId.SE


def regions_quadrants() -> list[RegionId]:
    return [RegionId.NW, RegionId.NE, RegionId.SW, RegionId.SE]

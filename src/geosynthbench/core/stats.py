from __future__ import annotations

from geosynthbench.core.geometry import bbox_of_polygon, polyline_length_px
from geosynthbench.core.regions import region_for_point_quadrants, regions_quadrants
from geosynthbench.core.types import RegionId
from geosynthbench.world.entities import (
    BuildingEntity,
    RoadEntity,
    VegetationEntity,
    WaterEntity,
)
from geosynthbench.world.world_state import (
    DerivedState,
    GlobalStats,
    RegionStats,
    WorldState,
)


def _empty_region_stats_dict() -> dict[RegionId, RegionStats]:
    return {r: RegionStats() for r in regions_quadrants()}


def compute_derived_state(state: WorldState) -> DerivedState:
    width = state.scene.width_px
    height = state.scene.height_px

    region_stats = _empty_region_stats_dict()
    global_stats = GlobalStats()

    for entity in state.entities:
        if isinstance(entity, BuildingEntity):
            cx, cy = _centroid(entity.polygon)
            region = region_for_point_quadrants((cx, cy), width, height)

            region_stats[region].building_count += 1
            global_stats.building_count += 1

        elif isinstance(entity, RoadEntity):
            length = polyline_length_px(entity.polyline)
            global_stats.road_length_px += length

        elif isinstance(entity, VegetationEntity):
            area = _bbox_area(entity.polygon)
            cx, cy = _centroid(entity.polygon)
            region = region_for_point_quadrants((cx, cy), width, height)

            region_stats[region].vegetation_area_px += area
            global_stats.vegetation_area_px += area

        elif isinstance(entity, WaterEntity):  # pyright: ignore[reportUnnecessaryIsInstance]
            area = _bbox_area(entity.polygon)
            cx, cy = _centroid(entity.polygon)
            region = region_for_point_quadrants((cx, cy), width, height)

            region_stats[region].water_area_px += area
            global_stats.water_area_px += area

    return DerivedState(
        region_stats=region_stats,
        global_stats=global_stats,
        adjacency={},  # fill later if needed
        extras={},
    )


def attach_derived_state(state: WorldState) -> WorldState:
    derived = compute_derived_state(state)
    return state.model_copy(update={"derived": derived})


def _centroid(polygon: list[tuple[float, float]]) -> tuple[float, float]:
    sx = sum(p[0] for p in polygon)
    sy = sum(p[1] for p in polygon)
    n = float(len(polygon)) if polygon else 1.0
    return (sx / n, sy / n)


def _bbox_area(polygon: list[tuple[float, float]]) -> int:
    x1, y1, x2, y2 = bbox_of_polygon(polygon)
    return int(max(0.0, x2 - x1) * max(0.0, y2 - y1))

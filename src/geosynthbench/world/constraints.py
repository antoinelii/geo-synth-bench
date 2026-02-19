from __future__ import annotations

from geosynthbench.core.geometry import bbox_of_polygon
from geosynthbench.world.entities import BuildingEntity, WaterEntity
from geosynthbench.world.world_state import WorldState


def validate_world_state(state: WorldState) -> list[str]:
    issues: list[str] = []

    # Basic: ensure at least 1 road and some buildings (MVP expectations)
    road_count = sum(1 for e in state.entities if e.layer.value == "roads")
    bld_count = sum(1 for e in state.entities if e.layer.value == "buildings")
    if road_count < 1:
        issues.append("No roads generated.")
    if bld_count < 5:
        issues.append("Too few buildings generated (<5).")

    # Basic: prevent buildings entirely inside water bbox (cheap heuristic)
    waters = [e for e in state.entities if isinstance(e, WaterEntity)]
    buildings = [e for e in state.entities if isinstance(e, BuildingEntity)]

    water_bboxes = [bbox_of_polygon(w.polygon) for w in waters]
    for b in buildings:
        bx1, by1, bx2, by2 = bbox_of_polygon(b.polygon)
        for wx1, wy1, wx2, wy2 in water_bboxes:
            if _bbox_inside(bx1, by1, bx2, by2, wx1, wy1, wx2, wy2):
                issues.append(f"Building {b.id} bbox inside water bbox (heuristic).")

    return issues


def _bbox_inside(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    x1_ref: float,
    y1_ref: float,
    x2_ref: float,
    y2_ref: float,
) -> bool:
    return x1 >= x1_ref and y1 >= y1_ref and x2 <= x2_ref and y2 <= y2_ref

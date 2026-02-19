from __future__ import annotations

import math

from geosynthbench.config.schemas import SceneConfig
from geosynthbench.core.geometry import (
    clamp_polygon,
    clamp_polyline,
    distance,
    point_to_polyline_distance,
    polygon_centroid,
    rect_polygon,
)
from geosynthbench.core.rng import RNG
from geosynthbench.core.stats import attach_derived_state
from geosynthbench.core.types import EntityId, Point
from geosynthbench.world.entities import (
    BuildingEntity,
    Entity,
    RoadEntity,
    VegetationEntity,
    WaterEntity,
)
from geosynthbench.world.world_state import Provenance, WorldState


def generate_world_state_t1(scene: SceneConfig, seed: int) -> WorldState:
    rng = RNG(seed)
    roads_rng = rng.split("roads")
    buildings_rng = rng.split("buildings")
    veg_rng = rng.split("vegetation")
    water_rng = rng.split("water")

    entities: list[Entity] = []

    # --- Roads ---
    roads = _generate_roads(scene, roads_rng)
    entities.extend(roads)

    # --- Buildings (biased near roads) ---
    buildings = _generate_buildings(scene, buildings_rng, roads)
    entities.extend(buildings)

    # --- Vegetation ---
    veg_patches = _generate_vegetation(scene, veg_rng)
    entities.extend(veg_patches)

    # --- Water (optional) ---
    if water_rng.uniform(0.0, 1.0) < 0.35:
        water = _generate_water(scene, water_rng)
        entities.append(water)

    prov = Provenance(seed=seed)
    state = WorldState(scene=scene, entities=entities, derived=None, provenance=prov)
    state = attach_derived_state(state)
    return state


def _new_entity_id(prefix: str, idx: int) -> EntityId:
    return EntityId(f"{prefix}_{idx:05d}")


def _generate_roads(scene: SceneConfig, rng: RNG) -> list[RoadEntity]:
    width = scene.width_px
    height = scene.height_px

    num_roads = 1 if rng.uniform(0.0, 1.0) < 0.7 else 2
    roads: list[RoadEntity] = []

    for i in range(num_roads):
        # Choose an entry and exit edge
        # MVP: road roughly crosses scene with mild curvature.
        start = _sample_edge_point(rng, width, height)
        end = _sample_edge_point(rng, width, height)

        # Ensure start/end not too close
        attempts = 0
        while distance(start, end) < min(width, height) * 0.4 and attempts < 10:
            end = _sample_edge_point(rng, width, height)
            attempts += 1

        mid = ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0)

        # Add a bend near the mid point
        bend_strength = rng.uniform(0.05, 0.18) * min(width, height)
        angle = rng.uniform(0.0, 2.0 * math.pi)
        bend = (mid[0] + bend_strength * math.cos(angle), mid[1] + bend_strength * math.sin(angle))

        polyline = clamp_polyline([start, bend, end], width, height)

        road = RoadEntity(
            id=_new_entity_id("road", i),
            polyline=polyline,
            width_px=rng.randint(5, 9),
            properties={"class": "primary" if i == 0 else "secondary"},
        )
        roads.append(road)

    return roads


def _generate_buildings(
    scene: SceneConfig, rng: RNG, roads: list[RoadEntity]
) -> list[BuildingEntity]:
    width = scene.width_px
    height = scene.height_px

    # MVP: more buildings if road exists
    target = rng.randint(30, 80) if roads else rng.randint(10, 30)

    buildings: list[BuildingEntity] = []
    max_attempts = target * 25

    # Building size distribution (px)
    size_buckets = [
        (8, 12),
        (12, 18),
        (18, 26),
    ]

    # Encourage buildings near roads but allow some scatter
    p_near_road = 0.82
    near_thresh_px = 18.0  # must be within this distance to a road (for "near road" samples)
    min_sep_px = 6.0  # simplistic separation to reduce heavy overlap

    attempts = 0
    while len(buildings) < target and attempts < max_attempts:
        attempts += 1

        # Sample candidate center
        cx = rng.uniform(0.0, float(width - 1))
        cy = rng.uniform(0.0, float(height - 1))
        center: Point = (cx, cy)

        # If near-road required, enforce distance
        if roads and rng.uniform(0.0, 1.0) < p_near_road:
            d = min(point_to_polyline_distance(center, r.polyline) for r in roads)
            if d > near_thresh_px:
                continue

        # Choose size bucket
        w_lo, w_hi = rng.choice(size_buckets)
        h_lo, h_hi = rng.choice(size_buckets)
        w_px = float(rng.randint(w_lo, w_hi))
        h_px = float(rng.randint(h_lo, h_hi))

        # Mild rotation
        angle = rng.uniform(-0.4, 0.4)

        poly = rect_polygon(center=center, w_px=w_px, h_px=h_px, angle_rad=angle)
        poly = clamp_polygon(poly, width, height)

        # Simple overlap avoidance via centroid distance
        if any(
            distance(center, polygon_centroid(b.polygon)) < (max(w_px, h_px) / 2.0 + min_sep_px)
            for b in buildings
        ):
            continue

        bid = _new_entity_id("bld", len(buildings))
        buildings.append(
            BuildingEntity(
                id=bid,
                polygon=poly,
                properties={"class": rng.choice(["residential", "industrial", "commercial"])},
            )
        )

    return buildings


def _generate_vegetation(scene: SceneConfig, rng: RNG) -> list[VegetationEntity]:
    width = scene.width_px
    height = scene.height_px

    n = rng.randint(2, 5)
    vegs: list[VegetationEntity] = []

    for i in range(n):
        cx = rng.uniform(0.0, float(width - 1))
        cy = rng.uniform(0.0, float(height - 1))
        w_px = float(rng.randint(60, 160))
        h_px = float(rng.randint(60, 160))
        angle = rng.uniform(0.0, 2.0 * math.pi)

        poly = rect_polygon(center=(cx, cy), w_px=w_px, h_px=h_px, angle_rad=angle)
        poly = clamp_polygon(poly, width, height)

        vegs.append(
            VegetationEntity(
                id=_new_entity_id("veg", i),
                polygon=poly,
                properties={"density": rng.choice(["low", "medium", "high"])},
            )
        )

    return vegs


def _generate_water(scene: SceneConfig, rng: RNG) -> WaterEntity:
    width = scene.width_px
    height = scene.height_px

    cx = rng.uniform(0.0, float(width - 1))
    cy = rng.uniform(0.0, float(height - 1))
    w_px = float(rng.randint(80, 200))
    h_px = float(rng.randint(80, 200))
    angle = rng.uniform(0.0, 2.0 * math.pi)

    poly = rect_polygon(center=(cx, cy), w_px=w_px, h_px=h_px, angle_rad=angle)
    poly = clamp_polygon(poly, width, height)

    return WaterEntity(
        id=_new_entity_id("water", 0),
        polygon=poly,
        properties={"type": "lake"},
    )


def _sample_edge_point(rng: RNG, width_px: int, height_px: int) -> Point:
    # Pick one of 4 edges uniformly
    edge = rng.randint(0, 3)
    if edge == 0:  # top
        return (rng.uniform(0.0, float(width_px - 1)), 0.0)
    elif edge == 1:  # right
        return (float(width_px - 1), rng.uniform(0.0, float(height_px - 1)))
    elif edge == 2:  # bottom
        return (rng.uniform(0.0, float(width_px - 1)), float(height_px - 1))
    else:  # left
        return (0.0, rng.uniform(0.0, float(height_px - 1)))

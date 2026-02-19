from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from geosynthbench.core.geometry import clamp_polygon, polygon_centroid, rect_polygon
from geosynthbench.core.regions import region_for_point_quadrants
from geosynthbench.core.rng import RNG
from geosynthbench.core.types import ChangeType, EntityId, RegionId
from geosynthbench.world.entities import BuildingEntity, VegetationEntity
from geosynthbench.world.world_state import WorldState


class ChangeResult(Protocol):
    """Marker protocol for operator results (kept simple)."""


@dataclass(frozen=True)
class OpResult:
    """Normalized operator return (lint-friendly)."""

    state_t2: WorldState
    added: tuple[EntityId, ...] = ()
    removed: tuple[EntityId, ...] = ()
    modified: tuple[EntityId, ...] = ()
    params: dict[str, str] | None = None


def _empty_params() -> dict[str, str]:
    return {}


@dataclass(frozen=True)
class ChangeOperator(Protocol):
    change_type: ChangeType

    def apply(self, state_t1: WorldState, rng: RNG, region: RegionId) -> OpResult: ...


@dataclass(frozen=True)
class AddBuildingOp:
    change_type: ChangeType = ChangeType.ADD_BUILDING

    def apply(self, state_t1: WorldState, rng: RNG, region: RegionId) -> OpResult:
        w, h = state_t1.scene.width_px, state_t1.scene.height_px

        # Place building inside target quadrant by rejection sampling
        for _ in range(250):
            cx = rng.uniform(0.0, float(w - 1))
            cy = rng.uniform(0.0, float(h - 1))
            if region_for_point_quadrants((cx, cy), w, h) != region:
                continue

            bw = float(rng.randint(10, 22))
            bh = float(rng.randint(10, 22))
            angle = rng.uniform(-0.4, 0.4)

            poly = rect_polygon(center=(cx, cy), w_px=bw, h_px=bh, angle_rad=angle)
            poly = clamp_polygon(poly, w, h)

            new_id = EntityId(f"bld_added_{rng.randint(0, 2_000_000_000)}")
            ent = BuildingEntity(id=new_id, polygon=poly, properties={"class": "new"})

            new_entities = list(state_t1.entities)
            new_entities.append(ent)
            new_state = state_t1.model_copy(update={"entities": new_entities, "derived": None})

            params = _empty_params()
            params["w_px"] = f"{bw:.2f}"
            params["h_px"] = f"{bh:.2f}"
            return OpResult(state_t2=new_state, added=(new_id,), params=params)

        # fail softly: return identity state but with no added/removed; applier will retry
        return OpResult(state_t2=state_t1, params={"failed": "true"})


@dataclass(frozen=True)
class RemoveBuildingOp:
    change_type: ChangeType = ChangeType.REMOVE_BUILDING

    def apply(self, state_t1: WorldState, rng: RNG, region: RegionId) -> OpResult:
        w, h = state_t1.scene.width_px, state_t1.scene.height_px

        buildings = [e for e in state_t1.entities if isinstance(e, BuildingEntity)]
        candidates: list[BuildingEntity] = []
        for b in buildings:
            c = polygon_centroid(b.polygon)
            if region_for_point_quadrants(c, w, h) == region:
                candidates.append(b)

        if not candidates:
            return OpResult(
                state_t2=state_t1, params={"failed": "true", "reason": "no_buildings_in_region"}
            )

        victim = rng.choice(candidates)
        new_entities = [e for e in state_t1.entities if e.id != victim.id]
        new_state = state_t1.model_copy(update={"entities": new_entities, "derived": None})

        return OpResult(state_t2=new_state, removed=(victim.id,), params=_empty_params())


@dataclass(frozen=True)
class ClearVegetationOp:
    change_type: ChangeType = ChangeType.CLEAR_VEG

    def apply(self, state_t1: WorldState, rng: RNG, region: RegionId) -> OpResult:
        w, h = state_t1.scene.width_px, state_t1.scene.height_px

        vegs = [e for e in state_t1.entities if isinstance(e, VegetationEntity)]
        candidates: list[VegetationEntity] = []
        for v in vegs:
            c = polygon_centroid(v.polygon)
            if region_for_point_quadrants(c, w, h) == region:
                candidates.append(v)

        if not candidates:
            return OpResult(
                state_t2=state_t1, params={"failed": "true", "reason": "no_veg_in_region"}
            )

        victim = rng.choice(candidates)
        new_entities = [e for e in state_t1.entities if e.id != victim.id]
        new_state = state_t1.model_copy(update={"entities": new_entities, "derived": None})

        return OpResult(state_t2=new_state, removed=(victim.id,), params=_empty_params())

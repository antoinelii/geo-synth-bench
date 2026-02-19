from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from geosynthbench.config.schemas import RenderConfig
from geosynthbench.core.types import LayerType
from geosynthbench.render.annotations import RenderOutput
from geosynthbench.render.palettes import CLASS_ID_TO_RGB, LAYER_TO_CLASS_ID
from geosynthbench.world.entities import (
    BuildingEntity,
    Entity,
    RoadEntity,
    VegetationEntity,
    WaterEntity,
)
from geosynthbench.world.world_state import WorldState


def _empty_extras() -> dict[str, Any]:
    return {}


class RasterRenderer:
    """
    MVP renderer: outputs
      - RGB visualization
      - semantic mask (uint8 ids)
    """

    def __init__(self, render_cfg: RenderConfig) -> None:
        self._cfg = render_cfg
        if self._cfg.style != "flat_rgb":
            raise ValueError(f"Unsupported render style: {self._cfg.style}")

    def render_t1(self, state: WorldState, out_dir: Path, sample_id: str) -> RenderOutput:
        out_dir.mkdir(parents=True, exist_ok=True)

        rgb_path = out_dir / f"{sample_id}_t1_rgb.png"
        sem_path = out_dir / f"{sample_id}_t1_semantic.png"

        rgb_img, sem_img = _render(state)

        rgb_img.save(rgb_path)
        sem_img.save(sem_path)

        return RenderOutput(
            rgb_path=rgb_path,
            semantic_mask_path=sem_path,
            width_px=state.scene.width_px,
            height_px=state.scene.height_px,
            extras=_empty_extras(),
        )


def _render(state: WorldState) -> tuple[Image.Image, Image.Image]:
    w = state.scene.width_px
    h = state.scene.height_px

    # Semantic mask as L mode (0-255)
    sem = Image.new("L", (w, h), color=0)
    sem_draw = ImageDraw.Draw(sem)

    # Render order matters (roads under buildings, etc.)
    # MVP order: vegetation, water, roads, buildings (so buildings appear on top)
    ents = _sort_entities_for_render(state.entities)

    for e in ents:
        _draw_entity_semantic(sem_draw, e)

    sem_np = np.array(sem, dtype=np.uint8)

    # Convert semantic → RGB visualization using palette
    rgb_np = np.zeros((h, w, 3), dtype=np.uint8)
    for class_id, rgb in CLASS_ID_TO_RGB.items():
        mask = sem_np == class_id
        rgb_np[mask] = np.array(rgb, dtype=np.uint8)

    rgb = Image.fromarray(rgb_np, mode="RGB")
    sem_out = Image.fromarray(sem_np, mode="L")
    return rgb, sem_out


def _sort_entities_for_render(entities: list[Entity]) -> list[Entity]:
    priority: dict[LayerType, int] = {
        LayerType.VEGETATION: 10,
        LayerType.WATER: 20,
        LayerType.ROADS: 30,
        LayerType.BUILDINGS: 40,
    }

    return sorted(entities, key=lambda e: priority.get(e.layer, 99))


def _draw_entity_semantic(draw: ImageDraw.ImageDraw, e: Entity) -> None:
    class_id = LAYER_TO_CLASS_ID[e.layer]
    fill = int(class_id)

    if isinstance(e, RoadEntity):
        # Draw polyline with width
        xy = [(float(x), float(y)) for (x, y) in e.polyline]
        # Pillow line supports width
        draw.line(xy, fill=fill, width=int(e.width_px))
        return

    if isinstance(e, BuildingEntity | VegetationEntity | WaterEntity):  # pyright: ignore[reportUnnecessaryIsInstance]
        xy = [(float(x), float(y)) for (x, y) in e.polygon]
        draw.polygon(xy, fill=fill)
        return

    # Fallback: ignore unknown entities (future-proof)

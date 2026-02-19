from __future__ import annotations

from pathlib import Path

from geosynthbench.config.schemas import AppConfig
from geosynthbench.core.logging import get_logger
from geosynthbench.render.annotations import RenderOutput
from geosynthbench.render.raster_renderer import RasterRenderer
from geosynthbench.world.constraints import validate_world_state
from geosynthbench.world.generator import generate_world_state_t1
from geosynthbench.world.world_state import WorldState

logger = get_logger()


def generate_one_t1(
    cfg: AppConfig,
    seed: int,
    sample_id: str,
    assets_dir: Path,
    max_retries: int = 10,
) -> tuple[WorldState, RenderOutput]:
    """
    Generate one valid T1 sample. Retries by incrementing seed until constraints pass.
    """
    renderer = RasterRenderer(cfg.render)

    for attempt in range(max_retries):
        attempt_seed = seed + attempt
        state = generate_world_state_t1(scene=cfg.scene, seed=attempt_seed)

        issues = validate_world_state(state)
        if issues:
            logger.warning(
                f"⚠️ Invalid sample (seed={attempt_seed}) attempt {attempt+1}/{max_retries}"
            )
            for issue in issues:
                logger.warning(f"  - {issue}")
            continue

        render_out = renderer.render_t1(state=state, out_dir=assets_dir, sample_id=sample_id)
        logger.success(f"✅ Sample valid (seed={attempt_seed})")
        return state, render_out

    raise ValueError(f"Failed to generate a valid sample after {max_retries} retries.")

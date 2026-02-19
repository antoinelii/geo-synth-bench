from __future__ import annotations

from geosynthbench.config.schemas import AppConfig
from geosynthbench.core.logging import get_logger, setup_logging
from geosynthbench.pipeline.generate_one import generate_one_t1

logger = get_logger()


def main() -> None:
    setup_logging()

    cfg = AppConfig()

    out_assets = cfg.dataset.assets_dir
    out_assets.mkdir(parents=True, exist_ok=True)

    seed = 42
    sample_id = "debug_00001"

    logger.info("🚀 Generating debug sample...")

    state, render_out = generate_one_t1(
        cfg=cfg, seed=seed, sample_id=sample_id, assets_dir=out_assets
    )

    logger.success("✅ Rendered sample")
    logger.info(f"📌 seed: {seed}")
    logger.info(f"🆔 sample_id: {sample_id}")
    logger.info(f"🖼 RGB: {render_out.rgb_path}")
    logger.info(f"🗺 Semantic mask: {render_out.semantic_mask_path}")

    if state.derived is not None:
        logger.info(f"📊 Global stats: {state.derived.global_stats.model_dump()}")


if __name__ == "__main__":
    main()

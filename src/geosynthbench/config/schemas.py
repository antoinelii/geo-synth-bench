from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from geosynthbench.core.types import TaskMode


class SceneConfig(BaseModel):
    """Global scene parameters (world distribution). Frozen to defaults in MVP, but extensible."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    width_px: int = Field(512, ge=64)
    height_px: int = Field(512, ge=64)
    meters_per_px: float = Field(1.0, gt=0.0, le=30.0)

    biome: Literal["temperate"] = (
        "temperate"  # Reserved for future: "desert", "tropical", "arctic", etc.
    )
    terrain: Literal["flat"] = "flat"  # Reserved for future: "hilly", "mountainous", etc.

    # MVP: quadrants. Later: "tiles", "admin_regions", custom grids...
    region_partition: Literal["quadrants"] = "quadrants"


class RenderConfig(BaseModel):
    """Rendering configuration. MVP uses a simple flat RGB style."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    style: Literal["flat_rgb"] = "flat_rgb"
    # Reserved for future: sensor type, illumination model, domain randomization, etc.


class DatasetConfig(BaseModel):
    """Dataset generation parameters (I/O, sizes, splits)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_samples: int = Field(500, ge=1)
    # split_seed: int = Field(1337, ge=0)

    # Output layout (can be overridden by CLI)
    out_dir: Path = Path("data/out")
    assets_dir: Path = Path("data/out/assets")
    jsonl_dir: Path = Path("data/out/jsonl")

    # train_fraction: float = Field(0.9, gt=0.0, lt=1.0)


class TaskConfig(BaseModel):
    """Task selection and knobs. MVP will freeze this to one temporal task."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str = "temporal.localized_change_v1"
    mode: TaskMode = TaskMode.TEMPORAL

    # Reserved for future: difficulty scaling, template families, confounders
    difficulty: Literal["easy", "medium", "hard"] = "easy"


class AppConfig(BaseModel):
    """Convenience top-level config bundling all configs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scene: SceneConfig = SceneConfig(
        width_px=512,
        height_px=512,
        meters_per_px=1.0,
        biome="temperate",
        terrain="flat",
        region_partition="quadrants",
    )
    render: RenderConfig = RenderConfig()
    dataset: DatasetConfig = DatasetConfig(
        num_samples=10,
        out_dir=Path("data/out"),
        assets_dir=Path("data/out/assets"),
        jsonl_dir=Path("data/out/jsonl"),
    )
    task: TaskConfig = TaskConfig()

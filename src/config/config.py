from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class WorldConfig(BaseModel):
    """
    Defines the abstract world coordinate system used to generate geometry.

    We keep it simple for the MVP:
    - world units are arbitrary "meters-like" units
    - extent is a rectangle [0, width] x [0, height]
    - optional grid controls snapping / discretization for some generators
    """

    width: float = Field(default=512.0, gt=0)
    height: float = Field(default=512.0, gt=0)

    grid_size: float = Field(default=1.0, gt=0)
    crs: str | None = Field(default=None, description="Optional CRS label (e.g., EPSG:3857)")

    max_entities: int = Field(default=2000, ge=1)

    @model_validator(mode="after")
    def _check_grid(self) -> WorldConfig:
        # ensure grid is not absurdly larger than the world
        if self.grid_size > min(self.width, self.height):
            raise ValueError("grid_size must be <= min(width, height)")
        return self


class RenderConfig(BaseModel):
    """
    Defines how the world is rasterized into an image.
    """

    image_size_px: int = Field(default=512, ge=32)
    units_per_px: float = Field(default=1.0, gt=0)

    # optional "style" knobs for MVP; keep deterministic downstream
    antialias: bool = Field(default=True)
    background: Literal["light", "dark"] = Field(default="light")


class DatasetConfig(BaseModel):
    """
    Defines the dataset writing layout.
    """

    output_dir: Path = Field(default=Path("outputs"))
    name: str = Field(default="geosynthbench")

    num_samples: int = Field(default=50, ge=1)

    # optional train/val split (kept simple)
    val_fraction: float = Field(default=0.1, ge=0.0, le=0.9)

    # writing options
    image_format: Literal["png"] = Field(default="png")
    write_json: bool = Field(default=True)

    @model_validator(mode="after")
    def _check_out(self) -> DatasetConfig:
        # Keep paths normalized; don't create dirs here (side-effect free model)
        self.output_dir = self.output_dir.expanduser()
        return self


class RunConfig(BaseModel):
    """
    Top-level config used by the CLI.
    """

    seed: int = Field(default=0, ge=0)

    world: WorldConfig = Field(default_factory=WorldConfig)
    render: RenderConfig = Field(default_factory=RenderConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)

    @model_validator(mode="after")
    def _check_consistency(self) -> RunConfig:
        # Basic sanity: raster footprint covers the world in roughly expected way.
        # (Not a strict constraint, just catches obvious mistakes.)
        world_min_dim = min(self.world.width, self.world.height)
        raster_min_dim_units = self.render.image_size_px * self.render.units_per_px
        if raster_min_dim_units < 0.25 * world_min_dim:
            raise ValueError(
                "RenderConfig seems inconsistent: image too small vs world extent "
                "(image_size_px * units_per_px << world size)."
            )
        return self

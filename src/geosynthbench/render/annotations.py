from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def empty_bboxes() -> list[BBox]:
    return []


class BBox(BaseModel):
    """Optional bounding box annotation."""

    model_config = ConfigDict(extra="forbid")

    # xyxy in pixel coordinates
    x1: int
    y1: int
    x2: int
    y2: int

    label: str
    entity_id: str | None = None


class RenderOutput(BaseModel):
    """References rendered assets + lightweight metadata."""

    model_config = ConfigDict(extra="forbid")

    rgb_path: Path
    semantic_mask_path: Path

    # Optional / future
    instance_mask_path: Path | None = None
    change_mask_path: Path | None = None
    bboxes: list[BBox] = Field(default_factory=empty_bboxes)

    width_px: int
    height_px: int

    # Renderer-specific extras (palette, class ids, etc.)
    extras: dict[str, Any] = Field(default_factory=dict)

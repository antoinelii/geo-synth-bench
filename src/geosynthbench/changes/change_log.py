from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from geosynthbench.core.types import ChangeType, EntityId, RegionId


def empty_ids() -> list[EntityId]:
    return []


class ChangeLog(BaseModel):
    """Ground-truth record of what was changed between T1 and T2."""

    model_config = ConfigDict(extra="forbid")

    change_type: ChangeType
    region: RegionId

    added_ids: list[EntityId] = Field(default_factory=empty_ids)
    removed_ids: list[EntityId] = Field(default_factory=empty_ids)
    modified_ids: list[EntityId] = Field(default_factory=empty_ids)

    # Operator parameters (e.g., "num_buildings": 2, "road_extension_px": 40)
    params: dict[str, Any] = Field(default_factory=dict)

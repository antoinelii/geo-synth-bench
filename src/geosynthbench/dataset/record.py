from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from geosynthbench.changes.change_log import ChangeLog
from geosynthbench.config.schemas import SceneConfig
from geosynthbench.core.types import RegionId, SampleId, TaskMode
from geosynthbench.core.versioning import GENERATOR_VERSION, SCHEMA_VERSION


class AssetPaths(BaseModel):
    """All file references for one sample."""

    model_config = ConfigDict(extra="forbid")

    t1_rgb: str
    t1_semantic_mask: str

    # Temporal optional
    t2_rgb: str | None = None
    t2_semantic_mask: str | None = None
    change_mask: str | None = None


class Labels(BaseModel):
    """Primary labels for quick filtering/stratification."""

    model_config = ConfigDict(extra="forbid")

    region: RegionId | None = None
    change_type: str | None = None
    difficulty: str | None = None

    extras: dict[str, Any] = Field(default_factory=dict)


class Verification(BaseModel):
    """Optional verifier output (LLM/VLM)."""

    model_config = ConfigDict(extra="forbid")

    passed: bool | None = None
    score: float | None = None
    notes: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class SampleRecord(BaseModel):
    """One JSONL row representing a supervised multimodal example."""

    model_config = ConfigDict(extra="forbid")

    id: SampleId
    task_id: str
    mode: TaskMode

    scene: SceneConfig
    assets: AssetPaths

    prompt: str

    # The ground truth used for evaluation (always structured)
    answer_structured: dict[str, Any]

    # Optional: a human-readable short answer (template/LLM-generated)
    answer_text: str | None = None

    labels: Labels = Field(default_factory=Labels)

    # Temporal optional
    change_log: ChangeLog | None = None

    # Store small derived stats useful for debugging/training (optional)
    derived: dict[str, Any] = Field(default_factory=dict)

    verification: Verification | None = None

    schema_version: str = Field(default=SCHEMA_VERSION)
    generator_version: str = Field(default=GENERATOR_VERSION)

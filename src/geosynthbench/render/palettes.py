from __future__ import annotations

from dataclasses import dataclass

from geosynthbench.core.types import LayerType


@dataclass(frozen=True)
class ClassDef:
    name: str
    class_id: int
    rgb: tuple[int, int, int]


# MVP: simple semantic classes
BACKGROUND = ClassDef("background", 0, (0, 0, 0))
ROADS = ClassDef("roads", 1, (220, 220, 220))
BUILDINGS = ClassDef("buildings", 2, (200, 80, 80))
VEGETATION = ClassDef("vegetation", 3, (80, 170, 80))
WATER = ClassDef("water", 4, (70, 120, 220))


MVP_CLASSES: list[ClassDef] = [BACKGROUND, ROADS, BUILDINGS, VEGETATION, WATER]

LAYER_TO_CLASS_ID: dict[LayerType, int] = {
    LayerType.ROADS: ROADS.class_id,
    LayerType.BUILDINGS: BUILDINGS.class_id,
    LayerType.VEGETATION: VEGETATION.class_id,
    LayerType.WATER: WATER.class_id,
}


CLASS_ID_TO_RGB: dict[int, tuple[int, int, int]] = {c.class_id: c.rgb for c in MVP_CLASSES}

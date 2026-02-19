from __future__ import annotations

import itertools
import math
from collections.abc import Iterable

from geosynthbench.core.types import Point, Polygon, Polyline


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def clamp_point(p: Point, width_px: int, height_px: int) -> Point:
    x, y = p
    return (clamp(x, 0.0, float(width_px - 1)), clamp(y, 0.0, float(height_px - 1)))


def clamp_polyline(polyline: Polyline, width_px: int, height_px: int) -> Polyline:
    return [clamp_point(p, width_px, height_px) for p in polyline]


def clamp_polygon(polygon: Polygon, width_px: int, height_px: int) -> Polygon:
    return [clamp_point(p, width_px, height_px) for p in polygon]


def polyline_length_px(polyline: Polyline) -> float:
    if len(polyline) < 2:
        return 0.0
    total = 0.0
    for (x1, y1), (x2, y2) in itertools.pairwise(polyline):
        dx = x2 - x1
        dy = y2 - y1
        total += math.hypot(dx, dy)
    return total


def bbox_of_points(points: Iterable[Point]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for x, y in points:
        xs.append(x)
        ys.append(y)
    if not xs:
        raise ValueError("bbox_of_points() requires at least one point")
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_of_polygon(polygon: Polygon) -> tuple[float, float, float, float]:
    return bbox_of_points(polygon)


def polygon_centroid(polygon: Polygon) -> Point:
    # Simple average centroid (MVP). Good enough for rectangles/blobs.
    if not polygon:
        raise ValueError("polygon_centroid() requires non-empty polygon")
    sx = sum(p[0] for p in polygon)
    sy = sum(p[1] for p in polygon)
    n = float(len(polygon))
    return (sx / n, sy / n)


def rect_polygon(center: Point, w_px: float, h_px: float, angle_rad: float = 0.0) -> Polygon:
    """
    Returns a rectangle polygon (4 points) centered at center.
    Angle is rotation around center.
    """
    cx, cy = center
    hw = w_px / 2.0
    hh = h_px / 2.0

    # axis-aligned corners
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]

    if angle_rad == 0.0:
        return [(cx + dx, cy + dy) for dx, dy in corners]

    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    def rot(dx: float, dy: float) -> Point:
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        return (cx + rx, cy + ry)

    return [rot(dx, dy) for dx, dy in corners]


def distance(p1: Point, p2: Point) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def point_to_segment_distance(p: Point, a: Point, b: Point) -> float:
    """
    Distance from point p to segment ab.
    """
    px, py = p
    ax, ay = a
    bx, by = b

    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay

    ab_len2 = abx * abx + aby * aby
    if ab_len2 == 0.0:
        return distance(p, a)

    t = (apx * abx + apy * aby) / ab_len2
    t = clamp(t, 0.0, 1.0)

    cx = ax + t * abx
    cy = ay + t * aby
    return distance(p, (cx, cy))


def point_to_polyline_distance(p: Point, polyline: Polyline) -> float:
    if len(polyline) < 2:
        return float("inf")
    dmin = float("inf")
    for a, b in itertools.pairwise(polyline):
        d = point_to_segment_distance(p, a, b)
        if d < dmin:
            dmin = d
    return dmin

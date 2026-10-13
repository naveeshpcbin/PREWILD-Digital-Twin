"""Geometry utilities — boundary intersection, distance, ETA calculations.

All coordinates are in metres in a 2-D plane.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Point:
    """A 2-D point in metres."""
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def scale(self, s: float) -> "Point":
        return Point(self.x * s, self.y * s)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


@dataclass(frozen=True)
class Segment:
    """A line segment from *a* to *b*."""
    a: Point
    b: Point

    @property
    def length(self) -> float:
        return self.a.distance_to(self.b)

    @property
    def direction(self) -> Point:
        L = self.length
        if L < 1e-12:
            return Point(0.0, 0.0)
        return Point((self.b.x - self.a.x) / L, (self.b.y - self.a.y) / L)


@dataclass
class BoundaryIntersection:
    """Result of a ray–segment intersection test."""
    intersects: bool
    point: Optional[Point] = None
    time_s: Optional[float] = None     # estimated time to reach intersection
    distance_m: Optional[float] = None


def ray_segment_intersection(
    origin: Point,
    velocity: Point,
    seg: Segment,
) -> BoundaryIntersection:
    """Compute where the ray (origin + t*velocity) intersects segment *seg*.

    Returns *BoundaryIntersection* with ``intersects=True`` only when the
    intersection lies in the future (t >= 0) **and** on the segment.

    Parameters
    ----------
    origin : Point
        Current (estimated) position.
    velocity : Point
        Velocity vector (m/s in each axis).
    seg : Segment
        The boundary segment.

    Returns
    -------
    BoundaryIntersection
    """
    # Direction of the segment
    dx_seg = seg.b.x - seg.a.x
    dy_seg = seg.b.y - seg.a.y

    denom = velocity.x * dy_seg - velocity.y * dx_seg

    if abs(denom) < 1e-12:
        # Ray is (near-)parallel to the segment
        return BoundaryIntersection(intersects=False)

    dx_oa = seg.a.x - origin.x
    dy_oa = seg.a.y - origin.y

    t = (dx_oa * dy_seg - dy_oa * dx_seg) / denom   # ray parameter
    u = (dx_oa * velocity.y - dy_oa * velocity.x) / denom  # segment parameter

    if t < 0 or u < 0 or u > 1:
        return BoundaryIntersection(intersects=False)

    ix = origin.x + t * velocity.x
    iy = origin.y + t * velocity.y
    pt = Point(ix, iy)
    dist = origin.distance_to(pt)
    return BoundaryIntersection(
        intersects=True,
        point=pt,
        time_s=t,
        distance_m=dist,
    )


def estimate_eta(
    position: Point,
    velocity: Point,
    boundary: Segment,
) -> BoundaryIntersection:
    """Estimate time-to-boundary along the current velocity vector.

    Wrapper around :func:`ray_segment_intersection` with additional
    guards for zero / near-zero speed.
    """
    speed = math.hypot(velocity.x, velocity.y)
    if speed < 1e-6:
        return BoundaryIntersection(intersects=False)
    return ray_segment_intersection(position, velocity, boundary)


def point_in_fov(
    camera_pos: Point,
    camera_orientation_deg: float,
    fov_deg: float,
    max_range_m: float,
    target: Point,
) -> bool:
    """Check whether *target* falls within a camera's field of view cone."""
    d = camera_pos.distance_to(target)
    if d > max_range_m or d < 1e-9:
        return False
    angle_to_target = math.degrees(
        math.atan2(target.y - camera_pos.y, target.x - camera_pos.x)
    )
    diff = (angle_to_target - camera_orientation_deg + 180) % 360 - 180
    return abs(diff) <= fov_deg / 2.0


def closest_point_on_segment(p: Point, seg: Segment) -> Point:
    """Return the closest point on *seg* to *p*."""
    ax, ay = seg.a.x, seg.a.y
    bx, by = seg.b.x, seg.b.y
    dx, dy = bx - ax, by - ay
    if dx * dx + dy * dy < 1e-12:
        return seg.a
    t = max(0.0, min(1.0, ((p.x - ax) * dx + (p.y - ay) * dy) / (dx * dx + dy * dy)))
    return Point(ax + t * dx, ay + t * dy)


def distance_to_boundary(p: Point, boundary: Segment) -> float:
    """Shortest distance from *p* to the boundary segment."""
    cp = closest_point_on_segment(p, boundary)
    return p.distance_to(cp)

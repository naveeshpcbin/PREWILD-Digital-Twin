"""Tests for geometry utilities."""

import math
import pytest

from prw_wild.geometry import (
    Point, Segment, ray_segment_intersection, estimate_eta,
    point_in_fov, distance_to_boundary, closest_point_on_segment,
    BoundaryIntersection,
)


class TestPoint:
    def test_distance(self):
        assert Point(0, 0).distance_to(Point(3, 4)) == 5.0

    def test_add_sub(self):
        p = Point(1, 2) + Point(3, 4)
        assert p.x == 4 and p.y == 6
        q = Point(5, 5) - Point(1, 2)
        assert q.x == 4 and q.y == 3


class TestRaySegmentIntersection:
    def test_direct_hit(self):
        """Ray heading right should hit a vertical segment."""
        origin = Point(0, 5)
        vel = Point(1, 0)
        seg = Segment(Point(10, 0), Point(10, 10))
        r = ray_segment_intersection(origin, vel, seg)
        assert r.intersects
        assert abs(r.point.x - 10) < 0.01
        assert abs(r.time_s - 10) < 0.01

    def test_miss_above(self):
        origin = Point(0, 15)
        vel = Point(1, 0)
        seg = Segment(Point(10, 0), Point(10, 10))
        r = ray_segment_intersection(origin, vel, seg)
        assert not r.intersects

    def test_parallel(self):
        origin = Point(5, 5)
        vel = Point(0, 1)
        seg = Segment(Point(10, 0), Point(10, 10))
        r = ray_segment_intersection(origin, vel, seg)
        assert not r.intersects

    def test_going_away(self):
        origin = Point(15, 5)
        vel = Point(1, 0)  # moving away
        seg = Segment(Point(10, 0), Point(10, 10))
        r = ray_segment_intersection(origin, vel, seg)
        assert not r.intersects


class TestEstimateETA:
    def test_zero_speed(self):
        r = estimate_eta(Point(5, 5), Point(0, 0), Segment(Point(10, 0), Point(10, 10)))
        assert not r.intersects

    def test_approaching(self):
        r = estimate_eta(
            Point(5, 5), Point(2, 0),
            Segment(Point(10, 0), Point(10, 10)),
        )
        assert r.intersects
        assert abs(r.time_s - 2.5) < 0.01

    def test_no_intersection_direction_away(self):
        r = estimate_eta(
            Point(5, 5), Point(-2, 0),
            Segment(Point(10, 0), Point(10, 10)),
        )
        assert not r.intersects


class TestPointInFov:
    def test_inside_fov(self):
        assert point_in_fov(Point(0, 0), 0, 90, 50, Point(30, 5))

    def test_outside_fov_angle(self):
        assert not point_in_fov(Point(0, 0), 0, 30, 50, Point(10, 30))

    def test_outside_range(self):
        assert not point_in_fov(Point(0, 0), 0, 90, 10, Point(30, 0))


class TestDistanceToBoundary:
    def test_perpendicular(self):
        seg = Segment(Point(10, 0), Point(10, 10))
        d = distance_to_boundary(Point(5, 5), seg)
        assert abs(d - 5.0) < 0.01

    def test_on_boundary(self):
        seg = Segment(Point(10, 0), Point(10, 10))
        d = distance_to_boundary(Point(10, 5), seg)
        assert d < 0.01

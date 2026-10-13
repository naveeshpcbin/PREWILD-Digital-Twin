"""Tests for sensor fusion."""

import pytest
from prw_wild.fusion import SensorFusion
from prw_wild.config import DEFAULT_CONFIG


def _make_fusion():
    return SensorFusion(DEFAULT_CONFIG)


class TestSensorFusion:
    def test_empty_gives_low_confidence(self):
        f = _make_fusion()
        r = f.fuse(10.0)
        assert r.fused_confidence < 0.3

    def test_single_sensor_partial_confidence(self):
        f = _make_fusion()
        f.add_observation(10.0, "rf_csi", 0.8, [50.0, 50.0], 5.0)
        r = f.fuse(10.5)
        assert r.fused_confidence > 0.1
        assert r.observation_count == 1

    def test_multi_sensor_higher_confidence(self):
        f = _make_fusion()
        f.add_observation(10.0, "rf_csi", 0.8, [50.0, 50.0], 5.0)
        f.add_observation(10.1, "pir", 0.9)
        f.add_observation(10.2, "acoustic", 0.7, [52.0, 51.0], 8.0)
        r = f.fuse(10.5)
        assert r.fused_confidence > 0.4

    def test_old_observations_pruned(self):
        f = _make_fusion()
        f.add_observation(1.0, "rf_csi", 0.9)
        r = f.fuse(100.0)  # way past window
        assert r.observation_count == 0

    def test_decay(self):
        f = _make_fusion()
        f.add_observation(10.0, "rf_csi", 0.8)
        r1 = f.fuse(10.5)
        f.fuse(10.5)  # set last_confidence
        r2 = f.fuse(20.0)  # long gap, no new obs
        assert r2.fused_confidence < r1.fused_confidence

    def test_position_estimate_from_single(self):
        f = _make_fusion()
        f.add_observation(10.0, "rf_csi", 0.8, [50.0, 60.0], 5.0)
        r = f.fuse(10.5)
        assert r.estimated_position_xy is not None
        assert abs(r.estimated_position_xy[0] - 50.0) < 1

    def test_contradictory_weak_score(self):
        """Single weak observation should not produce high confidence."""
        f = _make_fusion()
        f.add_observation(10.0, "vibration", 0.15)
        r = f.fuse(10.5)
        assert r.fused_confidence < 0.2

    def test_reset(self):
        f = _make_fusion()
        f.add_observation(10.0, "rf_csi", 0.9)
        f.reset()
        r = f.fuse(10.5)
        assert r.observation_count == 0

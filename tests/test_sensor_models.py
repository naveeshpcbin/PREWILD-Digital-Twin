"""Tests for sensor observation models."""

import random
import pytest

from prw_wild.geometry import Point
from prw_wild.sensor_models import (
    SensorNode, SensorParams, generate_observation,
    build_sensor_nodes, get_sensor_params,
)
from prw_wild.config import DEFAULT_CONFIG


class TestGenerateObservation:
    def _make_node_and_params(self):
        node = SensorNode("rf_01", "rf_csi", Point(50, 50))
        params = SensorParams(
            detection_range_m=30.0,
            detection_probability=0.90,
            false_trigger_rate_per_s=0.005,
            noise_std=0.1,
            delay_s=0.1,
            outage_intervals=[],
        )
        return node, params

    def test_in_range_detection(self):
        node, params = self._make_node_and_params()
        rng = random.Random(42)
        detections = 0
        for _ in range(100):
            obs = generate_observation(
                node, params,
                true_position=Point(45, 50),
                true_speed=1.5,
                time_s=10.0,
                dt=0.5,
                rng=rng,
            )
            if obs is not None and "detection" in obs.provenance:
                detections += 1
        # At 5m distance, should detect most of the time
        assert detections > 50

    def test_out_of_range_no_true_detection(self):
        node, params = self._make_node_and_params()
        rng = random.Random(42)
        true_detections = 0
        for _ in range(100):
            obs = generate_observation(
                node, params,
                true_position=Point(200, 200),  # far away
                true_speed=1.5,
                time_s=10.0,
                dt=0.5,
                rng=rng,
            )
            if obs is not None and "detection" in obs.provenance:
                true_detections += 1
        assert true_detections == 0

    def test_false_triggers_occur(self):
        node, params = self._make_node_and_params()
        params.false_trigger_rate_per_s = 0.5  # very high
        rng = random.Random(42)
        false_count = 0
        for _ in range(200):
            obs = generate_observation(
                node, params,
                true_position=Point(200, 200),
                true_speed=0,
                time_s=10.0,
                dt=0.5,
                rng=rng,
            )
            if obs is not None and "false" in obs.provenance:
                false_count += 1
        assert false_count > 10

    def test_outage_blocks_observation(self):
        node, params = self._make_node_and_params()
        params.outage_intervals = [[5.0, 15.0]]
        rng = random.Random(42)
        obs = generate_observation(
            node, params,
            true_position=Point(48, 50),
            true_speed=1.0,
            time_s=10.0,
            dt=0.5,
            rng=rng,
        )
        assert obs is None

    def test_observation_has_timestamp(self):
        node, params = self._make_node_and_params()
        rng = random.Random(42)
        for _ in range(50):
            obs = generate_observation(
                node, params,
                true_position=Point(48, 50),
                true_speed=1.0,
                time_s=10.0,
                dt=0.5,
                rng=rng,
            )
            if obs is not None:
                assert obs.timestamp_s >= 10.0
                break


class TestBuildSensorNodes:
    def test_from_default_config(self):
        nodes = build_sensor_nodes(DEFAULT_CONFIG)
        assert len(nodes) == 5
        types = {n.sensor_type for n in nodes}
        assert "rf_csi" in types
        assert "pir" in types

    def test_get_params(self):
        params = get_sensor_params(DEFAULT_CONFIG, "rf_csi")
        assert params.detection_range_m == 30.0
        assert 0 <= params.detection_probability <= 1

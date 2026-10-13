"""Tests for configuration loading and validation."""

import json
import copy
import pytest
from pathlib import Path

from prw_wild.config import (
    DEFAULT_CONFIG, load_config, validate_config,
    ConfigError, _deep_merge, save_config,
)


def test_default_config_is_valid():
    """Default config must pass validation without errors."""
    warnings = validate_config(DEFAULT_CONFIG)
    # Warnings are OK; errors would raise ConfigError


def test_deep_merge_preserves_base():
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"c": 99}}
    merged = _deep_merge(base, override)
    assert merged["a"] == 1
    assert merged["b"]["c"] == 99
    assert merged["b"]["d"] == 3
    # Original unchanged
    assert base["b"]["c"] == 2


def test_missing_scenario_id():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    del cfg["scenario_id"]
    with pytest.raises(ConfigError, match="scenario_id"):
        validate_config(cfg)


def test_invalid_probability():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["sensors"]["rf_csi"]["detection_probability"] = 1.5
    with pytest.raises(ConfigError, match="probability"):
        validate_config(cfg)


def test_negative_range():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["sensors"]["pir"]["detection_range_m"] = -5
    with pytest.raises(ConfigError, match="positive"):
        validate_config(cfg)


def test_time_step_exceeds_duration():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["simulation"]["time_step_s"] = 200.0
    with pytest.raises(ConfigError, match="exceed"):
        validate_config(cfg)


def test_duplicate_sensor_id():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["sensors"]["nodes"][1]["id"] = cfg["sensors"]["nodes"][0]["id"]
    with pytest.raises(ConfigError, match="duplicate"):
        validate_config(cfg)


def test_insufficient_waypoints():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["animals"][0]["waypoints"] = [[10.0, 10.0]]
    with pytest.raises(ConfigError, match="waypoints"):
        validate_config(cfg)


def test_watch_threshold_above_high():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["risk"]["thresholds"]["watch"] = 0.9
    cfg["risk"]["thresholds"]["high"] = 0.5
    with pytest.raises(ConfigError, match="watch must be < high"):
        validate_config(cfg)


def test_boundary_start_equals_end():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["world"]["boundary"]["end"] = cfg["world"]["boundary"]["start"]
    with pytest.raises(ConfigError, match="differ"):
        validate_config(cfg)


def test_save_and_load(tmp_path):
    """Round-trip: save then load config."""
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    p = tmp_path / "test_config.json"
    save_config(cfg, p)
    loaded = load_config(p)
    assert loaded["scenario_id"] == cfg["scenario_id"]
    assert loaded["simulation"]["duration_s"] == cfg["simulation"]["duration_s"]


def test_load_nonexistent():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_file_xyz.json")


def test_fusion_weights_warning():
    """Weights not summing to 1 should produce a warning, not an error."""
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["fusion"]["weights"]["rf_csi"] = 0.01
    warnings = validate_config(cfg)
    assert any("sum" in w for w in warnings)

"""Configuration loading, validation, and defaults for PRW-Wild simulations.

Configuration is stored as versioned JSON.  This module provides a
canonical default, a loader that deep-merges user overrides, and a
validator that rejects invalid or inconsistent settings early.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: dict[str, Any] = {
    "config_version": 1,
    "scenario_id": "default",
    "random_seed": 42,
    "simulation": {
        "duration_s": 120.0,
        "time_step_s": 0.5,
    },
    "world": {
        "width_m": 200.0,
        "height_m": 200.0,
        "boundary": {
            "type": "line",
            "start": [100.0, 0.0],
            "end": [100.0, 200.0],
        },
        "corridors": [
            {
                "id": "corridor_1",
                "center_y_m": 100.0,
                "width_m": 40.0,
                "weight": 1.5,
            }
        ],
        "obstacles": [],
    },
    "animals": [
        {
            "id": "animal_0",
            "species": "elephant",
            "waypoints": [
                [20.0, 100.0],
                [60.0, 100.0],
                [110.0, 100.0],
                [150.0, 100.0],
            ],
            "speed_m_s": 1.5,
            "pause_s": 0.0,
        }
    ],
    "sensors": {
        "nodes": [
            {"id": "rf_01", "type": "rf_csi", "position": [70.0, 90.0]},
            {"id": "rf_02", "type": "rf_csi", "position": [70.0, 110.0]},
            {"id": "pir_01", "type": "pir", "position": [85.0, 100.0]},
            {"id": "vib_01", "type": "vibration", "position": [95.0, 100.0]},
            {"id": "aco_01", "type": "acoustic", "position": [80.0, 100.0]},
        ],
        "rf_csi": {
            "detection_range_m": 30.0,
            "detection_probability": 0.85,
            "false_trigger_rate_per_s": 0.005,
            "noise_std": 0.15,
            "delay_s": 0.1,
            "outage_intervals": [],
        },
        "pir": {
            "detection_range_m": 15.0,
            "detection_probability": 0.90,
            "false_trigger_rate_per_s": 0.008,
            "noise_std": 0.10,
            "delay_s": 0.05,
            "outage_intervals": [],
        },
        "vibration": {
            "detection_range_m": 20.0,
            "detection_probability": 0.70,
            "false_trigger_rate_per_s": 0.01,
            "noise_std": 0.20,
            "delay_s": 0.05,
            "outage_intervals": [],
        },
        "acoustic": {
            "detection_range_m": 40.0,
            "detection_probability": 0.75,
            "false_trigger_rate_per_s": 0.003,
            "noise_std": 0.18,
            "delay_s": 0.2,
            "outage_intervals": [],
        },
    },
    "fusion": {
        "time_window_s": 3.0,
        "weights": {
            "rf_csi": 0.30,
            "pir": 0.25,
            "vibration": 0.15,
            "acoustic": 0.15,
            "ecology": 0.15,
        },
        "min_confidence": 0.20,
        "decay_rate_per_s": 0.05,
    },
    "tracker": {
        "process_noise_std": 0.5,
        "measurement_noise_std": 5.0,
        "max_stale_s": 8.0,
        "max_jump_m": 50.0,
        "min_observations": 2,
    },
    "ecology": {
        "enabled": True,
        "corridor_boost": 0.15,
        "neutral_prior": 0.5,
    },
    "risk": {
        "thresholds": {
            "watch": 0.35,
            "high": 0.60,
        },
        "hysteresis": 0.05,
        "boundary_weight": 0.35,
        "eta_weight": 0.25,
        "confidence_weight": 0.25,
        "track_quality_weight": 0.15,
    },
    "camera": {
        "nodes": [
            {
                "id": "cam_01",
                "position": [100.0, 100.0],
                "orientation_deg": 270.0,
                "fov_deg": 60.0,
                "max_range_m": 50.0,
            }
        ],
        "startup_delay_s": 1.5,
        "capture_latency_s": 0.5,
        "capture_failure_probability": 0.05,
        "detection_probability": 0.90,
        "classification_accuracy": 0.80,
        "misclassification_species": ["cattle", "vehicle", "unknown"],
        "cooldown_s": 10.0,
        "activation_risk_threshold": 0.55,
        "activation_confidence_threshold": 0.30,
    },
    "alert": {
        "min_risk_for_alert": 0.60,
        "cooldown_s": 15.0,
        "channels": ["dashboard", "sms_event", "deterrent"],
    },
    "power": {
        "sensor_sleep_w": 0.001,
        "sensor_active_w": 0.05,
        "camera_sleep_w": 0.005,
        "camera_active_w": 2.5,
        "gateway_idle_w": 0.1,
        "gateway_transmit_w": 0.5,
        "note": "ESTIMATED values; not measured on physical hardware.",
    },
    "policies": {
        "active": "predictive",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into a copy of *base*."""
    merged = copy.deepcopy(base)
    for key, val in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(val, dict):
            merged[key] = _deep_merge(merged[key], val)
        else:
            merged[key] = copy.deepcopy(val)
    return merged


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class ConfigError(Exception):
    """Raised when configuration is invalid."""


def _require(cfg: dict, *keys: str, ctx: str = "config") -> Any:
    """Navigate nested keys and raise if missing."""
    node = cfg
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            raise ConfigError(f"{ctx}: missing required key '{'.'.join(keys)}'")
        node = node[k]
    return node


def _check_probability(value: Any, name: str) -> None:
    if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
        raise ConfigError(f"{name} must be a probability in [0, 1]; got {value!r}")


def _check_positive(value: Any, name: str) -> None:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ConfigError(f"{name} must be positive; got {value!r}")


def _check_non_negative(value: Any, name: str) -> None:
    if not isinstance(value, (int, float)) or value < 0:
        raise ConfigError(f"{name} must be non-negative; got {value!r}")


def _check_point(pt: Any, name: str) -> None:
    if (not isinstance(pt, (list, tuple)) or len(pt) != 2
            or not all(isinstance(c, (int, float)) for c in pt)):
        raise ConfigError(f"{name} must be [x, y] numeric pair; got {pt!r}")


def validate_config(cfg: dict) -> list[str]:
    """Validate *cfg* and return a list of warnings.  Raises ConfigError on hard failures."""
    warnings: list[str] = []

    # Top-level
    _require(cfg, "scenario_id")
    _require(cfg, "random_seed")

    # Simulation timing
    sim = _require(cfg, "simulation")
    _check_positive(sim.get("duration_s"), "simulation.duration_s")
    _check_positive(sim.get("time_step_s"), "simulation.time_step_s")
    if sim["time_step_s"] > sim["duration_s"]:
        raise ConfigError("time_step_s cannot exceed duration_s")

    # World
    world = _require(cfg, "world")
    _check_positive(world.get("width_m"), "world.width_m")
    _check_positive(world.get("height_m"), "world.height_m")
    bnd = _require(cfg, "world", "boundary")
    _check_point(bnd.get("start"), "boundary.start")
    _check_point(bnd.get("end"), "boundary.end")
    if bnd["start"] == bnd["end"]:
        raise ConfigError("Boundary start and end must differ")

    # Animals
    animals = _require(cfg, "animals")
    if not isinstance(animals, list) or len(animals) == 0:
        raise ConfigError("At least one animal must be defined")
    for i, a in enumerate(animals):
        ctx = f"animals[{i}]"
        if "id" not in a:
            raise ConfigError(f"{ctx}: missing 'id'")
        wps = a.get("waypoints", [])
        if not isinstance(wps, list) or len(wps) < 2:
            raise ConfigError(f"{ctx}: need at least 2 waypoints")
        for j, wp in enumerate(wps):
            _check_point(wp, f"{ctx}.waypoints[{j}]")
        _check_positive(a.get("speed_m_s", -1), f"{ctx}.speed_m_s")
        _check_non_negative(a.get("pause_s", 0), f"{ctx}.pause_s")

    # Sensor nodes
    sensors = _require(cfg, "sensors")
    nodes = sensors.get("nodes", [])
    if not isinstance(nodes, list) or len(nodes) == 0:
        raise ConfigError("At least one sensor node is required")
    seen_ids: set[str] = set()
    for i, n in enumerate(nodes):
        ctx = f"sensors.nodes[{i}]"
        nid = n.get("id")
        if not nid:
            raise ConfigError(f"{ctx}: missing 'id'")
        if nid in seen_ids:
            raise ConfigError(f"{ctx}: duplicate sensor id '{nid}'")
        seen_ids.add(nid)
        _check_point(n.get("position"), f"{ctx}.position")
        if n.get("type") not in ("rf_csi", "pir", "vibration", "acoustic"):
            raise ConfigError(f"{ctx}: unknown sensor type '{n.get('type')}'")

    # Sensor type parameters
    for stype in ("rf_csi", "pir", "vibration", "acoustic"):
        sp = sensors.get(stype)
        if sp is None:
            continue
        _check_positive(sp.get("detection_range_m", -1), f"sensors.{stype}.detection_range_m")
        _check_probability(sp.get("detection_probability", -1), f"sensors.{stype}.detection_probability")
        _check_non_negative(sp.get("false_trigger_rate_per_s", -1), f"sensors.{stype}.false_trigger_rate_per_s")

    # Fusion weights
    fw = _require(cfg, "fusion", "weights")
    total = sum(fw.values())
    if not (0.99 <= total <= 1.01):
        warnings.append(f"fusion.weights sum to {total:.4f}, expected ~1.0")

    # Risk thresholds
    rt = _require(cfg, "risk", "thresholds")
    if rt.get("watch", 0) >= rt.get("high", 1):
        raise ConfigError("risk.thresholds.watch must be < high")

    # Camera nodes
    cam = _require(cfg, "camera")
    cnodes = cam.get("nodes", [])
    for i, cn in enumerate(cnodes):
        _check_point(cn.get("position"), f"camera.nodes[{i}].position")
        _check_positive(cn.get("fov_deg", -1), f"camera.nodes[{i}].fov_deg")
        _check_positive(cn.get("max_range_m", -1), f"camera.nodes[{i}].max_range_m")

    return warnings


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON config file, merge with defaults, validate, and return."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        user_cfg = json.load(f)
    cfg = _deep_merge(DEFAULT_CONFIG, user_cfg)
    warnings = validate_config(cfg)
    for w in warnings:
        print(f"[config WARNING] {w}")
    return cfg


def save_config(cfg: dict[str, Any], path: str | Path) -> None:
    """Write *cfg* to *path* as pretty-printed JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

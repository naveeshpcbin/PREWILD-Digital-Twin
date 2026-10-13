"""Synthetic sensor observation models.

Each model may inspect hidden ground truth internally to decide
whether a detection occurs, but emits only what a real sensor would
plausibly report: a score/flag, timestamp, and optionally a noisy
estimated position.

All configurable parameters (range, probability, noise, etc.) are
drawn from the scenario configuration and are explicitly *synthetic
assumptions* until calibrated against physical hardware.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional

from prw_wild.geometry import Point
from prw_wild.event_log import Event, EventType


@dataclass
class SensorNode:
    """A deployed sensor node with a position and type."""
    sensor_id: str
    sensor_type: str   # rf_csi | pir | vibration | acoustic
    position: Point


@dataclass
class SensorParams:
    """Configurable observation-model parameters for one sensor type."""
    detection_range_m: float
    detection_probability: float
    false_trigger_rate_per_s: float
    noise_std: float
    delay_s: float
    outage_intervals: list[list[float]]   # [[start_s, end_s], …]


def _is_in_outage(t: float, outage_intervals: list[list[float]]) -> bool:
    for interval in outage_intervals:
        if interval[0] <= t <= interval[1]:
            return True
    return False


def generate_observation(
    node: SensorNode,
    params: SensorParams,
    true_position: Point,
    true_speed: float,
    time_s: float,
    dt: float,
    rng: random.Random,
    scenario_id: str = "",
    run_id: str = "",
) -> Optional[Event]:
    """Attempt to generate a sensor observation at the current time step.

    Returns an Event if a detection or false trigger occurs, else None.
    """

    # Sensor outage — no observation possible
    if _is_in_outage(time_s, params.outage_intervals):
        return None

    distance = node.position.distance_to(true_position)
    in_range = distance <= params.detection_range_m

    detected = False
    is_false_trigger = False
    score = 0.0

    if in_range:
        # Real detection attempt — probability modulated by distance
        range_factor = max(0.0, 1.0 - (distance / params.detection_range_m) ** 2)
        effective_prob = params.detection_probability * range_factor
        if rng.random() < effective_prob:
            detected = True
            # Score: higher when closer, with noise
            raw = range_factor * (0.7 + 0.3 * min(true_speed / 3.0, 1.0))
            score = max(0.0, min(1.0, raw + rng.gauss(0, params.noise_std)))

    # False trigger check (independent of real target)
    if not detected:
        if rng.random() < params.false_trigger_rate_per_s * dt:
            is_false_trigger = True
            score = max(0.0, min(1.0, rng.gauss(0.25, params.noise_std)))

    if not detected and not is_false_trigger:
        return None

    # Noisy position estimate — only RF/CSI and acoustic have crude localisation
    est_pos: Optional[list[float]] = None
    meas_unc: Optional[float] = None
    if node.sensor_type in ("rf_csi", "acoustic") and detected:
        # Synthetic noisy position near the sensor, biased toward true position
        noise_m = params.noise_std * params.detection_range_m
        est_x = true_position.x + rng.gauss(0, noise_m)
        est_y = true_position.y + rng.gauss(0, noise_m)
        est_pos = [round(est_x, 2), round(est_y, 2)]
        meas_unc = round(noise_m * 2, 2)  # ~2-sigma uncertainty

    prov = "synthetic_detection" if detected else "synthetic_false_trigger"

    return Event(
        timestamp_s=round(time_s + params.delay_s, 4),
        event_type=EventType.SENSOR_OBSERVATION.value,
        scenario_id=scenario_id,
        run_id=run_id,
        sensor_id=node.sensor_id,
        sensor_type=node.sensor_type,
        score=round(score, 4),
        confidence=round(score, 4),
        observation_quality=round(1.0 - (params.noise_std / 0.5), 2) if detected else 0.3,
        estimated_position_xy=est_pos,
        measurement_uncertainty=meas_unc,
        provenance=prov,
        metadata={"distance_m": round(distance, 2)} if detected else {},
    )


def build_sensor_nodes(cfg: dict) -> list[SensorNode]:
    """Create SensorNode instances from config."""
    nodes = []
    for n in cfg["sensors"]["nodes"]:
        nodes.append(SensorNode(
            sensor_id=n["id"],
            sensor_type=n["type"],
            position=Point(*n["position"]),
        ))
    return nodes


def get_sensor_params(cfg: dict, sensor_type: str) -> SensorParams:
    """Extract SensorParams for a given type from config."""
    sp = cfg["sensors"][sensor_type]
    return SensorParams(
        detection_range_m=sp["detection_range_m"],
        detection_probability=sp["detection_probability"],
        false_trigger_rate_per_s=sp["false_trigger_rate_per_s"],
        noise_std=sp["noise_std"],
        delay_s=sp["delay_s"],
        outage_intervals=sp.get("outage_intervals", []),
    )

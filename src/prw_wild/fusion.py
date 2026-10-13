"""Temporal sensor fusion.

Combines observations from heterogeneous sensors within configurable
time windows into a fused confidence score.  The baseline is a
weighted-sum heuristic — explicitly *not* a calibrated probabilistic
model until validated against real data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FusedResult:
    """Output of the sensor fusion step."""
    timestamp_s: float
    fused_confidence: float
    contributing_sensors: dict[str, float]  # sensor_type → latest score
    observation_count: int
    estimated_position_xy: list[float] | None = None
    position_uncertainty: float | None = None
    provenance: str = "synthetic_fusion"


class SensorFusion:
    """Time-windowed weighted sensor fusion.

    Accumulates observations and produces a fused confidence score.
    Scores decay over time when not refreshed.

    The formula is a *heuristic*:
        C = Σ  w_type * max_score_in_window(type)  +  w_eco * eco_prior
    normalised to [0, 1].
    """

    def __init__(self, cfg: dict):
        fc = cfg["fusion"]
        self.time_window_s: float = fc["time_window_s"]
        self.weights: dict[str, float] = dict(fc["weights"])
        self.min_confidence: float = fc["min_confidence"]
        self.decay_rate: float = fc["decay_rate_per_s"]

        # Observation buffer: sensor_type → list of (timestamp, score, pos, unc)
        self._buffer: dict[str, list[tuple[float, float, Any, Any]]] = {}
        self._last_fused: float = 0.0
        self._last_confidence: float = 0.0

    def add_observation(
        self,
        timestamp_s: float,
        sensor_type: str,
        score: float,
        estimated_position_xy: list[float] | None = None,
        measurement_uncertainty: float | None = None,
    ) -> None:
        """Buffer a sensor observation."""
        if sensor_type not in self._buffer:
            self._buffer[sensor_type] = []
        self._buffer[sensor_type].append(
            (timestamp_s, score, estimated_position_xy, measurement_uncertainty)
        )

    def fuse(self, current_time_s: float, eco_prior: float = 0.5) -> FusedResult:
        """Produce a fused confidence from buffered observations.

        Parameters
        ----------
        current_time_s : float
            Simulation time at which fusion is computed.
        eco_prior : float
            Ecological context prior in [0, 1].  Default 0.5 (neutral).
        """
        cutoff = current_time_s - self.time_window_s

        # Prune old observations
        for stype in list(self._buffer.keys()):
            self._buffer[stype] = [
                obs for obs in self._buffer[stype] if obs[0] >= cutoff
            ]

        contributing: dict[str, float] = {}
        positions: list[tuple[list[float], float]] = []  # (pos, weight)
        obs_count = 0

        for stype in ("rf_csi", "pir", "vibration", "acoustic"):
            w = self.weights.get(stype, 0.0)
            obs_list = self._buffer.get(stype, [])
            if obs_list:
                # Use the maximum score in the window for this type
                best = max(obs_list, key=lambda o: o[1])
                contributing[stype] = best[1]
                obs_count += len(obs_list)
                # Collect position estimates for weighted average
                for _, _, pos, unc in obs_list:
                    if pos is not None:
                        pw = w / (unc if unc and unc > 0 else 1.0)
                        positions.append((pos, pw))
            else:
                contributing[stype] = 0.0

        # Ecological prior
        eco_w = self.weights.get("ecology", 0.0)

        # Weighted sum
        raw = sum(
            self.weights.get(st, 0.0) * sc
            for st, sc in contributing.items()
        ) + eco_w * eco_prior

        # Clamp
        fused = max(0.0, min(1.0, raw))

        # Decay if no new observations
        if obs_count == 0 and self._last_confidence > 0:
            dt = current_time_s - self._last_fused
            fused = max(0.0, self._last_confidence - self.decay_rate * dt)

        self._last_fused = current_time_s
        self._last_confidence = fused

        # Weighted-average position estimate
        est_pos = None
        pos_unc = None
        if positions:
            total_w = sum(pw for _, pw in positions)
            if total_w > 0:
                avg_x = sum(p[0] * pw for p, pw in positions) / total_w
                avg_y = sum(p[1] * pw for p, pw in positions) / total_w
                est_pos = [round(avg_x, 2), round(avg_y, 2)]
                # Rough uncertainty from spread
                if len(positions) > 1:
                    var = sum(
                        pw * ((p[0] - avg_x)**2 + (p[1] - avg_y)**2)
                        for p, pw in positions
                    ) / total_w
                    pos_unc = round(math.sqrt(var), 2)
                else:
                    # Single position — use measurement uncertainty
                    pos_unc = positions[0][1]

        return FusedResult(
            timestamp_s=current_time_s,
            fused_confidence=round(fused, 4),
            contributing_sensors=contributing,
            observation_count=obs_count,
            estimated_position_xy=est_pos,
            position_uncertainty=pos_unc,
        )

    def reset(self) -> None:
        """Clear all buffered observations."""
        self._buffer.clear()
        self._last_fused = 0.0
        self._last_confidence = 0.0

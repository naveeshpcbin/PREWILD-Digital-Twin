"""Spatiotemporal tracker — constant-velocity Kalman filter baseline.

The tracker receives position observations from sensor fusion and
maintains an estimated state (position, velocity, uncertainty).  It
must *never* receive ground-truth positions directly.

This is a simplified 2-D constant-velocity tracker suitable for a
single target.  Multi-target tracking is a future extension.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from prw_wild.geometry import Point


@dataclass
class TrackState:
    """Estimated track state at a given time."""
    timestamp_s: float
    estimated_x: float
    estimated_y: float
    estimated_vx: float
    estimated_vy: float
    position_uncertainty: float   # rough 1-sigma in metres
    velocity_uncertainty: float
    track_confidence: float       # [0, 1]
    observation_count: int
    is_valid: bool = True
    stale: bool = False

    @property
    def position(self) -> Point:
        return Point(self.estimated_x, self.estimated_y)

    @property
    def velocity(self) -> Point:
        return Point(self.estimated_vx, self.estimated_vy)

    @property
    def speed(self) -> float:
        return math.hypot(self.estimated_vx, self.estimated_vy)


class Tracker:
    """Constant-velocity Kalman filter tracker.

    State vector: [x, y, vx, vy]
    Observation: [x, y] (noisy position from fusion)

    Parameters come from the ``tracker`` section of the config.
    """

    def __init__(self, cfg: dict):
        tc = cfg["tracker"]
        self.process_noise_std: float = tc["process_noise_std"]
        self.measurement_noise_std: float = tc["measurement_noise_std"]
        self.max_stale_s: float = tc["max_stale_s"]
        self.max_jump_m: float = tc["max_jump_m"]
        self.min_observations: int = tc["min_observations"]

        # Kalman state
        self._x: Optional[np.ndarray] = None   # [x, y, vx, vy]
        self._P: Optional[np.ndarray] = None   # 4×4 covariance
        self._last_update_t: float = 0.0
        self._obs_count: int = 0
        self._initialised: bool = False

        # Observation matrix H (we observe position only)
        self._H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=float)

        # Measurement noise R
        r = self.measurement_noise_std ** 2
        self._R = np.array([
            [r, 0],
            [0, r],
        ], dtype=float)

    def _make_F(self, dt: float) -> np.ndarray:
        """State transition matrix for constant velocity."""
        return np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1],
        ], dtype=float)

    def _make_Q(self, dt: float) -> np.ndarray:
        """Process noise covariance."""
        q = self.process_noise_std ** 2
        dt2 = dt * dt
        dt3 = dt2 * dt / 2
        dt4 = dt2 * dt2 / 4
        return q * np.array([
            [dt4, 0,   dt3, 0  ],
            [0,   dt4, 0,   dt3],
            [dt3, 0,   dt2, 0  ],
            [0,   dt3, 0,   dt2],
        ], dtype=float)

    def predict(self, current_time_s: float) -> TrackState:
        """Time-update (prediction) step.  Returns predicted state."""
        if not self._initialised:
            return TrackState(
                timestamp_s=current_time_s,
                estimated_x=0, estimated_y=0,
                estimated_vx=0, estimated_vy=0,
                position_uncertainty=999,
                velocity_uncertainty=999,
                track_confidence=0,
                observation_count=0,
                is_valid=False,
            )

        dt = current_time_s - self._last_update_t
        if dt <= 0:
            dt = 0.001

        F = self._make_F(dt)
        Q = self._make_Q(dt)

        self._x = F @ self._x
        self._P = F @ self._P @ F.T + Q

        return self._build_state(current_time_s)

    def update(
        self,
        timestamp_s: float,
        obs_x: float,
        obs_y: float,
        measurement_uncertainty: float | None = None,
    ) -> TrackState:
        """Measurement-update step."""
        z = np.array([obs_x, obs_y])

        if not self._initialised:
            # Initialise state from first observation
            self._x = np.array([obs_x, obs_y, 0.0, 0.0])
            self._P = np.eye(4) * (self.measurement_noise_std ** 2) * 10
            self._last_update_t = timestamp_s
            self._obs_count = 1
            self._initialised = True
            return self._build_state(timestamp_s)

        # Predict to observation time first
        dt = timestamp_s - self._last_update_t
        if dt > 0:
            F = self._make_F(dt)
            Q = self._make_Q(dt)
            self._x = F @ self._x
            self._P = F @ self._P @ F.T + Q

        # Gate check — reject implausible jumps
        innovation = z - self._H @ self._x
        jump_dist = math.hypot(innovation[0], innovation[1])
        if jump_dist > self.max_jump_m:
            # Observation rejected — too far from predicted position
            self._last_update_t = timestamp_s
            state = self._build_state(timestamp_s)
            state.stale = True
            return state

        # Kalman update
        R = self._R.copy()
        if measurement_uncertainty is not None and measurement_uncertainty > 0:
            R = np.eye(2) * (measurement_uncertainty ** 2)

        S = self._H @ self._P @ self._H.T + R
        K = self._P @ self._H.T @ np.linalg.inv(S)
        self._x = self._x + K @ innovation
        self._P = (np.eye(4) - K @ self._H) @ self._P

        self._last_update_t = timestamp_s
        self._obs_count += 1
        return self._build_state(timestamp_s)

    def _build_state(self, t: float) -> TrackState:
        stale = (t - self._last_update_t) > self.max_stale_s
        pos_unc = math.sqrt(self._P[0, 0] + self._P[1, 1])
        vel_unc = math.sqrt(self._P[2, 2] + self._P[3, 3])

        # Simple confidence heuristic based on observation count and staleness
        conf = min(1.0, self._obs_count / max(self.min_observations * 2, 1))
        if stale:
            conf *= 0.3
        if pos_unc > 50:
            conf *= 0.5

        return TrackState(
            timestamp_s=t,
            estimated_x=round(float(self._x[0]), 4),
            estimated_y=round(float(self._x[1]), 4),
            estimated_vx=round(float(self._x[2]), 4),
            estimated_vy=round(float(self._x[3]), 4),
            position_uncertainty=round(pos_unc, 4),
            velocity_uncertainty=round(vel_unc, 4),
            track_confidence=round(conf, 4),
            observation_count=self._obs_count,
            is_valid=self._obs_count >= self.min_observations,
            stale=stale,
        )

    @property
    def is_initialised(self) -> bool:
        return self._initialised

    def reset(self) -> None:
        self._x = None
        self._P = None
        self._last_update_t = 0.0
        self._obs_count = 0
        self._initialised = False

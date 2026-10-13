"""Risk assessment engine.

Combines fused sensor confidence, track state, boundary-prediction
information, and optional ecological context into a risk level.

The risk score is a *heuristic* in [0, 1] — not a calibrated
probability — until validated against field data.

Risk levels: LOW, WATCH, HIGH.  Hysteresis prevents rapid oscillation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from prw_wild.event_log import RiskLevel
from prw_wild.geometry import BoundaryIntersection
from prw_wild.tracker import TrackState


@dataclass
class RiskAssessment:
    """Result of one risk evaluation."""
    timestamp_s: float
    risk_score: float
    risk_level: RiskLevel
    previous_level: RiskLevel
    components: dict[str, float]
    reason: str


class RiskEngine:
    """Configurable heuristic risk engine with hysteresis."""

    def __init__(self, cfg: dict):
        rc = cfg["risk"]
        self.watch_threshold: float = rc["thresholds"]["watch"]
        self.high_threshold: float = rc["thresholds"]["high"]
        self.hysteresis: float = rc["hysteresis"]
        self.boundary_weight: float = rc["boundary_weight"]
        self.eta_weight: float = rc["eta_weight"]
        self.confidence_weight: float = rc["confidence_weight"]
        self.track_quality_weight: float = rc["track_quality_weight"]

        self._current_level = RiskLevel.LOW
        self._history: list[RiskAssessment] = []

    def evaluate(
        self,
        timestamp_s: float,
        fused_confidence: float,
        track: TrackState,
        boundary_pred: BoundaryIntersection,
        eco_prior: float = 0.5,
        camera_species_severity: float | None = None,
    ) -> RiskAssessment:
        """Evaluate risk and apply hysteresis."""

        # Component: fused sensor confidence
        c_conf = fused_confidence

        # Component: boundary intersection probability proxy
        if boundary_pred.intersects and track.is_valid:
            c_boundary = min(1.0, track.track_confidence * 0.7 + 0.3)
        else:
            c_boundary = 0.0

        # Component: urgency from ETA
        c_eta = 0.0
        if boundary_pred.intersects and boundary_pred.time_s is not None:
            eta = boundary_pred.time_s
            if eta < 5:
                c_eta = 1.0
            elif eta < 15:
                c_eta = 0.7
            elif eta < 30:
                c_eta = 0.4
            elif eta < 60:
                c_eta = 0.2

        # Component: track quality
        c_track = 0.0
        if track.is_valid:
            c_track = track.track_confidence
            if track.stale:
                c_track *= 0.3

        # Weighted sum
        raw_score = (
            self.confidence_weight * c_conf
            + self.boundary_weight * c_boundary
            + self.eta_weight * c_eta
            + self.track_quality_weight * c_track
        )

        # Optional severity boost from camera classification
        if camera_species_severity is not None:
            raw_score = min(1.0, raw_score * (0.8 + 0.4 * camera_species_severity))

        raw_score = max(0.0, min(1.0, raw_score))

        # Determine level with hysteresis
        prev = self._current_level
        new_level = self._apply_hysteresis(raw_score, prev)
        self._current_level = new_level

        # Reason string
        reasons = []
        if c_conf > 0.3:
            reasons.append(f"sensor_conf={c_conf:.2f}")
        if c_boundary > 0:
            reasons.append(f"boundary_pred={c_boundary:.2f}")
        if c_eta > 0:
            reasons.append(f"eta_urgency={c_eta:.2f}")
        if c_track > 0:
            reasons.append(f"track_qual={c_track:.2f}")
        reason = "; ".join(reasons) if reasons else "insufficient_evidence"

        assessment = RiskAssessment(
            timestamp_s=timestamp_s,
            risk_score=round(raw_score, 4),
            risk_level=new_level,
            previous_level=prev,
            components={
                "fused_confidence": round(c_conf, 4),
                "boundary": round(c_boundary, 4),
                "eta_urgency": round(c_eta, 4),
                "track_quality": round(c_track, 4),
            },
            reason=reason,
        )
        self._history.append(assessment)
        return assessment

    def _apply_hysteresis(self, score: float, current: RiskLevel) -> RiskLevel:
        """Apply hysteresis thresholds to prevent oscillation."""
        if current == RiskLevel.LOW:
            if score >= self.watch_threshold:
                return RiskLevel.WATCH
            return RiskLevel.LOW
        elif current == RiskLevel.WATCH:
            if score >= self.high_threshold:
                return RiskLevel.HIGH
            if score < self.watch_threshold - self.hysteresis:
                return RiskLevel.LOW
            return RiskLevel.WATCH
        else:  # HIGH
            if score < self.high_threshold - self.hysteresis:
                if score < self.watch_threshold - self.hysteresis:
                    return RiskLevel.LOW
                return RiskLevel.WATCH
            return RiskLevel.HIGH

    @property
    def current_level(self) -> RiskLevel:
        return self._current_level

    @property
    def history(self) -> list[RiskAssessment]:
        return list(self._history)

    def reset(self) -> None:
        self._current_level = RiskLevel.LOW
        self._history.clear()

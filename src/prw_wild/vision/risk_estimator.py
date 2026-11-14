"""Visual Boundary Crossing Risk Estimator for PRW-Wild.

Estimates boundary crossing risk and ETA strictly from visual tracking vectors
and camera perspective geometry, completely independent of hidden simulation ground truth.

Maintains strict separation between:
- Detection Confidence (visual detection quality)
- Boundary Crossing Risk (trajectory extrapolation and spatial proximity)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class TrackRiskAssessment:
    track_id: int
    class_name: str
    detection_confidence: float
    confidence_calibration: str  # "RAW (NOT CALIBRATED)"
    crossing_risk_score: float   # [0.0, 1.0] experimental risk score
    heading_deg: float
    eta_seconds: Optional[float]
    boundary_distance_est_m: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    trajectory_intersects_boundary: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "detection_confidence": round(self.detection_confidence, 3),
            "confidence_calibration": self.confidence_calibration,
            "crossing_risk_score": round(self.crossing_risk_score, 3),
            "heading_deg": round(self.heading_deg, 1),
            "eta_seconds": round(self.eta_seconds, 1) if self.eta_seconds is not None else None,
            "boundary_distance_est_m": round(self.boundary_distance_est_m, 1),
            "risk_level": self.risk_level,
            "trajectory_intersects_boundary": self.trajectory_intersects_boundary
        }


class VisualRiskEstimator:
    """Estimates boundary crossing risk from visual track state vectors."""

    def __init__(self, boundary_pixel_x: float = 540.0, frame_width: float = 640.0):
        self.boundary_pixel_x = boundary_pixel_x
        self.frame_width = frame_width

    def evaluate_track(self, track: Dict[str, Any]) -> TrackRiskAssessment:
        bbox = track["bbox"]  # [x1, y1, x2, y2]
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        vx, vy = track.get("velocity_px", [0.0, 0.0])

        speed_px = math.hypot(vx, vy)
        heading_rad = math.atan2(vy, vx) if speed_px > 0.1 else 0.0
        heading_deg = (math.degrees(heading_rad) + 360.0) % 360.0

        # Pixel distance to boundary line on camera screen
        pixel_dist_to_fence = self.boundary_pixel_x - cx
        
        # Approximate metric distance (scale factor: ~15 pixels per meter at standard camera distance)
        est_dist_m = max(0.5, pixel_dist_to_fence / 15.0)

        # Check trajectory direction towards boundary (positive vx moves right towards boundary line)
        moving_towards_boundary = (vx > 0.2)
        intersects_boundary = (moving_towards_boundary and pixel_dist_to_fence > 0)

        # ETA calculation
        eta_s = None
        if moving_towards_boundary and vx > 0.5:
            # frames to fence / 30 fps
            frames_to_fence = pixel_dist_to_fence / vx
            eta_s = max(0.5, frames_to_fence / 15.0)

        # Experimental crossing risk calculation
        # Risk increases with proximity to fence and eastward velocity
        proximity_factor = max(0.0, min(1.0, 1.0 - (est_dist_m / 40.0)))
        velocity_factor = max(0.0, min(1.0, vx / 5.0)) if moving_towards_boundary else 0.0
        
        # Risk score is an experimental composite
        risk_score = 0.6 * proximity_factor + 0.4 * velocity_factor
        if not moving_towards_boundary:
            risk_score *= 0.3  # Moving away or stationary reduces risk

        risk_score = round(max(0.0, min(1.0, risk_score)), 3)

        if risk_score >= 0.75 or (est_dist_m < 5.0 and moving_towards_boundary):
            risk_level = "CRITICAL"
        elif risk_score >= 0.50:
            risk_level = "HIGH"
        elif risk_score >= 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return TrackRiskAssessment(
            track_id=track["track_id"],
            class_name=track["class_name"],
            detection_confidence=track["confidence"],
            confidence_calibration="RAW (NOT CALIBRATED)",
            crossing_risk_score=risk_score,
            heading_deg=heading_deg,
            eta_seconds=eta_s,
            boundary_distance_est_m=est_dist_m,
            risk_level=risk_level,
            trajectory_intersects_boundary=intersects_boundary
        )


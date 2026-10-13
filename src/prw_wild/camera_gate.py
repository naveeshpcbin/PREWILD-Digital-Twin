"""Selective camera gate and camera emulator.

The camera gate decides *when* to activate a camera based on risk and
confidence.  The camera emulator produces a *simulated* observation
(species classification with uncertainty), not a real image.

The controller does NOT receive ground-truth species directly.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional

from prw_wild.geometry import Point, point_in_fov
from prw_wild.event_log import Event, EventType, RiskLevel


# ---------------------------------------------------------------------------
# Camera node
# ---------------------------------------------------------------------------

@dataclass
class CameraNode:
    """A camera with position, orientation, FOV, and state."""
    camera_id: str
    position: Point
    orientation_deg: float
    fov_deg: float
    max_range_m: float
    state: str = "sleep"   # sleep | waking | active | cooldown
    wake_time_s: float = 0.0
    last_activation_s: float = -999.0
    activation_count: int = 0


# ---------------------------------------------------------------------------
# Camera gate
# ---------------------------------------------------------------------------

class CameraGate:
    """Decides when to activate cameras based on risk policy."""

    def __init__(self, cfg: dict):
        cam = cfg["camera"]
        self.risk_threshold: float = cam["activation_risk_threshold"]
        self.confidence_threshold: float = cam["activation_confidence_threshold"]
        self.startup_delay_s: float = cam["startup_delay_s"]
        self.cooldown_s: float = cam["cooldown_s"]

        self.cameras: list[CameraNode] = []
        for cn in cam.get("nodes", []):
            self.cameras.append(CameraNode(
                camera_id=cn["id"],
                position=Point(*cn["position"]),
                orientation_deg=cn["orientation_deg"],
                fov_deg=cn["fov_deg"],
                max_range_m=cn["max_range_m"],
            ))

    def should_activate(
        self,
        risk_score: float,
        risk_level: RiskLevel,
        fused_confidence: float,
        current_time_s: float,
    ) -> Optional[CameraNode]:
        """Return the best camera to activate, or None."""
        if risk_score < self.risk_threshold:
            return None
        if fused_confidence < self.confidence_threshold:
            return None

        for cam in self.cameras:
            if cam.state == "sleep":
                elapsed = current_time_s - cam.last_activation_s
                if elapsed >= self.cooldown_s:
                    return cam
        return None

    def activate(self, cam: CameraNode, current_time_s: float, reason: str = "") -> None:
        """Trigger camera wake-up."""
        cam.state = "waking"
        cam.wake_time_s = current_time_s
        cam.activation_count += 1

    def step(self, current_time_s: float) -> None:
        """Update camera states (wake-up delay, cooldown)."""
        for cam in self.cameras:
            if cam.state == "waking":
                if current_time_s - cam.wake_time_s >= self.startup_delay_s:
                    cam.state = "active"
            elif cam.state == "cooldown":
                if current_time_s - cam.last_activation_s >= self.cooldown_s:
                    cam.state = "sleep"

    def deactivate(self, cam: CameraNode, current_time_s: float) -> None:
        """Return camera to cooldown."""
        cam.state = "cooldown"
        cam.last_activation_s = current_time_s

    def get_total_activations(self) -> int:
        return sum(c.activation_count for c in self.cameras)


# ---------------------------------------------------------------------------
# Camera emulator
# ---------------------------------------------------------------------------

class CameraEmulator:
    """Simulated camera observation model.

    Uses ground truth internally to produce a *simulated* classification
    result.  The emulator may fail to detect or misclassify.

    All outputs are labelled 'simulated_camera'.
    """

    def __init__(self, cfg: dict):
        cam = cfg["camera"]
        self.capture_latency_s: float = cam["capture_latency_s"]
        self.capture_failure_prob: float = cam["capture_failure_probability"]
        self.detection_prob: float = cam["detection_probability"]
        self.classification_accuracy: float = cam["classification_accuracy"]
        self.misclass_species: list[str] = cam.get("misclassification_species",
                                                    ["unknown"])

    def capture(
        self,
        cam: CameraNode,
        true_position: Point,
        true_species: str,
        current_time_s: float,
        rng: random.Random,
        scenario_id: str = "",
        run_id: str = "",
    ) -> Optional[Event]:
        """Attempt a simulated camera capture.

        Returns an Event with classification result, or None on failure.
        """
        if cam.state != "active":
            return None

        # Check if target is in FOV
        if not point_in_fov(cam.position, cam.orientation_deg,
                            cam.fov_deg, cam.max_range_m, true_position):
            return Event(
                timestamp_s=round(current_time_s + self.capture_latency_s, 4),
                event_type=EventType.CAMERA_RESULT.value,
                camera_id=cam.camera_id,
                classification="not_in_fov",
                confidence=0.0,
                provenance="simulated_camera",
                scenario_id=scenario_id,
                run_id=run_id,
            )

        # Capture failure
        if rng.random() < self.capture_failure_prob:
            return Event(
                timestamp_s=round(current_time_s + self.capture_latency_s, 4),
                event_type=EventType.CAMERA_RESULT.value,
                camera_id=cam.camera_id,
                classification="capture_failed",
                confidence=0.0,
                provenance="simulated_camera",
                scenario_id=scenario_id,
                run_id=run_id,
            )

        # Detection
        if rng.random() > self.detection_prob:
            return Event(
                timestamp_s=round(current_time_s + self.capture_latency_s, 4),
                event_type=EventType.CAMERA_RESULT.value,
                camera_id=cam.camera_id,
                classification="no_detection",
                confidence=0.0,
                provenance="simulated_camera",
                scenario_id=scenario_id,
                run_id=run_id,
            )

        # Classification
        if rng.random() < self.classification_accuracy:
            species = true_species
            conf = round(0.7 + rng.random() * 0.25, 4)
        else:
            species = rng.choice(self.misclass_species)
            conf = round(0.3 + rng.random() * 0.3, 4)

        return Event(
            timestamp_s=round(current_time_s + self.capture_latency_s, 4),
            event_type=EventType.CAMERA_RESULT.value,
            camera_id=cam.camera_id,
            classification=species,
            confidence=conf,
            provenance="simulated_camera",
            scenario_id=scenario_id,
            run_id=run_id,
            metadata={"note": "Simulated classification; not from a real image model."},
        )

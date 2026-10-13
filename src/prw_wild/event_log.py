"""Event logging — JSONL event stream and structured event types.

Every observation, prediction, alert, and ground-truth record flows
through this module to produce a reproducible, traceable event log.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class EventType(str, Enum):
    SENSOR_OBSERVATION = "sensor_observation"
    FUSION_RESULT = "fusion_result"
    TRACK_UPDATE = "track_update"
    BOUNDARY_PREDICTION = "boundary_prediction"
    RISK_CHANGE = "risk_change"
    CAMERA_ACTIVATION = "camera_activation"
    CAMERA_RESULT = "camera_result"
    ALERT = "alert"
    DETERRENT = "deterrent"
    BOUNDARY_BREACH = "boundary_breach"
    DISPATCH = "dispatch"
    GROUND_TRUTH = "ground_truth"
    SYSTEM = "system"


class RiskLevel(str, Enum):
    LOW = "LOW"
    WATCH = "WATCH"
    HIGH = "HIGH"
    BREACH = "BREACH"


@dataclass
class Event:
    """Canonical event record written to the JSONL log."""
    timestamp_s: float
    event_type: str          # EventType value
    scenario_id: str = ""
    run_id: str = ""
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    sensor_id: str = ""
    sensor_type: str = ""
    score: float = 0.0
    confidence: float = 0.0
    observation_quality: float = 1.0
    estimated_position_xy: Optional[list[float]] = None
    measurement_uncertainty: Optional[float] = None
    risk_level: str = ""
    predicted_crossing_xy: Optional[list[float]] = None
    eta_s: Optional[float] = None
    camera_id: str = ""
    classification: str = ""
    provenance: str = "synthetic"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Strip None values for compact JSONL
        return {k: v for k, v in d.items() if v is not None and v != "" and v != {}}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventLogger:
    """Append-only JSONL writer for simulation events."""

    def __init__(self, path: Path, scenario_id: str = "", run_id: str = ""):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.scenario_id = scenario_id
        self.run_id = run_id
        self._file = open(self.path, "w", encoding="utf-8")
        self._count = 0

    def log(self, event: Event) -> None:
        if not event.scenario_id:
            event.scenario_id = self.scenario_id
        if not event.run_id:
            event.run_id = self.run_id
        self._file.write(event.to_json() + "\n")
        self._count += 1

    @property
    def count(self) -> int:
        return self._count

    def close(self) -> None:
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class GroundTruthLogger:
    """Separate JSONL writer for ground-truth records.

    Ground truth is NEVER read by the controller at runtime.
    """

    def __init__(self, path: Path, scenario_id: str = "", run_id: str = ""):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.scenario_id = scenario_id
        self.run_id = run_id
        self._file = open(self.path, "w", encoding="utf-8")

    def log(self, timestamp_s: float, animal_id: str,
            true_x: float, true_y: float,
            true_vx: float, true_vy: float,
            crossed: bool = False,
            metadata: dict | None = None) -> None:
        record = {
            "timestamp_s": round(timestamp_s, 4),
            "event_type": EventType.GROUND_TRUTH.value,
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "animal_id": animal_id,
            "true_x": round(true_x, 4),
            "true_y": round(true_y, 4),
            "true_vx": round(true_vx, 4),
            "true_vy": round(true_vy, 4),
            "crossed": crossed,
        }
        if metadata:
            record["metadata"] = metadata
        self._file.write(json.dumps(record) + "\n")

    def close(self) -> None:
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def load_events(path: Path) -> list[dict[str, Any]]:
    """Load all events from a JSONL file."""
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events

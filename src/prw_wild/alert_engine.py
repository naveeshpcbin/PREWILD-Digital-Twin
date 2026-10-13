"""Alert and deterrent engine.

Generates simulated alert events when risk criteria are met.
Does NOT connect to real notification services or physical outputs.

Species-appropriate deterrent selection is a *future* component.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from prw_wild.event_log import Event, EventType, RiskLevel


@dataclass
class AlertRecord:
    alert_id: str
    timestamp_s: float
    risk_level: str
    risk_score: float
    estimated_position_xy: Optional[list[float]]
    predicted_crossing_xy: Optional[list[float]]
    eta_s: Optional[float]
    sensor_evidence: dict
    camera_result: str
    channels: list[str]
    deterrent_command: str


class AlertEngine:
    """Simulated alert generation with cooldown."""

    def __init__(self, cfg: dict):
        ac = cfg["alert"]
        self.min_risk: float = ac["min_risk_for_alert"]
        self.cooldown_s: float = ac["cooldown_s"]
        self.channels: list[str] = ac["channels"]
        self._last_alert_t: float = -999.0
        self._alerts: list[AlertRecord] = []

    def evaluate(
        self,
        timestamp_s: float,
        risk_score: float,
        risk_level: RiskLevel,
        estimated_position: list[float] | None,
        predicted_crossing: list[float] | None,
        eta_s: float | None,
        sensor_evidence: dict,
        camera_result: str = "",
    ) -> Optional[Event]:
        """Generate an alert event if criteria are met and cooldown has elapsed."""

        if risk_score < self.min_risk:
            return None
        if timestamp_s - self._last_alert_t < self.cooldown_s:
            return None

        alert_id = uuid.uuid4().hex[:12]
        self._last_alert_t = timestamp_s

        # Determine deterrent suggestion
        deterrent = ""
        if "deterrent" in self.channels and risk_level == RiskLevel.HIGH:
            deterrent = "simulated_acoustic_deterrent"

        record = AlertRecord(
            alert_id=alert_id,
            timestamp_s=timestamp_s,
            risk_level=risk_level.value,
            risk_score=risk_score,
            estimated_position_xy=estimated_position,
            predicted_crossing_xy=predicted_crossing,
            eta_s=eta_s,
            sensor_evidence=sensor_evidence,
            camera_result=camera_result,
            channels=[c for c in self.channels if c != "deterrent" or deterrent],
            deterrent_command=deterrent,
        )
        self._alerts.append(record)

        ev = Event(
            timestamp_s=timestamp_s,
            event_type=EventType.ALERT.value,
            event_id=alert_id,
            risk_level=risk_level.value,
            score=risk_score,
            estimated_position_xy=estimated_position,
            predicted_crossing_xy=predicted_crossing,
            eta_s=eta_s,
            provenance="simulated_alert",
            metadata={
                "channels": record.channels,
                "camera_result": camera_result,
                "deterrent_command": deterrent,
                "note": "Simulated alert; no real notification sent.",
            },
        )

        # Deterrent event (separate log entry)
        if deterrent:
            self._deterrent_event = Event(
                timestamp_s=timestamp_s,
                event_type=EventType.DETERRENT.value,
                event_id=uuid.uuid4().hex[:12],
                risk_level=risk_level.value,
                provenance="simulated_deterrent",
                metadata={
                    "command": deterrent,
                    "note": "Simulated deterrent command; effectiveness not validated.",
                },
            )
        else:
            self._deterrent_event = None

        return ev

    @property
    def last_deterrent_event(self) -> Optional[Event]:
        return self._deterrent_event

    @property
    def alerts(self) -> list[AlertRecord]:
        return list(self._alerts)

    @property
    def alert_count(self) -> int:
        return len(self._alerts)

    def reset(self) -> None:
        self._last_alert_t = -999.0
        self._alerts.clear()

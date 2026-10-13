"""Alert dispatch and recipient routing layer for PRW-Wild.

Implements nearest-recipient selection, authority notification routing,
local simulation-mode dispatch, delivery deduplication, and optional provider adapters.

All simulated deliveries are explicitly marked:
"SIMULATED DELIVERY — NOT SENT TO A REAL PERSON"
"""

from __future__ import annotations

import math
import os
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class SimulatedRecipient:
    """A configured simulated person near the farm or buffer zone."""
    id: str
    name: str
    role: str  # "farmer", "resident", "worker", "patrol"
    position_xy: list[float]  # [x, y] in simulation meters
    channels: list[str] = field(default_factory=lambda: ["in_app", "sms"])
    notification_radius_m: float = 160.0
    zone: str = "farm_zone"
    is_simulated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuthorityRecipient:
    """A configured simulated wildlife/emergency authority."""
    id: str
    name: str
    role: str  # "wildlife_authority", "forest_dept", "emergency_coord"
    jurisdiction: str = "all_zones"
    channels: list[str] = field(default_factory=lambda: ["in_app", "email", "radio"])
    is_simulated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DispatchRecord:
    """Record of a dispatched notification (simulated or real)."""
    dispatch_id: str
    alert_id: str
    timestamp_s: float
    recipient_id: str
    recipient_name: str
    role: str
    distance_m: Optional[float]
    severity: str  # "WARNING", "CRITICAL_BREACH", "INFO"
    channel: str
    status: str  # "SIMULATED", "QUEUED", "ACCEPTED_BY_PROVIDER", "FAILED", "DISABLED", "NOT_CONFIGURED"
    message_text: str
    is_simulated: bool = True
    provider_response: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Default simulated community contacts (coordinates matched to farm/settlement layout)
DEFAULT_RECIPIENTS: list[SimulatedRecipient] = [
    SimulatedRecipient(
        id="FARM_OPERATOR_01",
        name="Arun Kumar (Lead Farm Operator)",
        role="farmer",
        position_xy=[115.0, 105.0],
        notification_radius_m=160.0,
        zone="protected_farm_zone",
    ),
    SimulatedRecipient(
        id="FIELD_WORKER_01",
        name="Ramu & Crop Field Crew",
        role="worker",
        position_xy=[108.0, 92.0],
        notification_radius_m=120.0,
        zone="protected_farm_zone",
    ),
    SimulatedRecipient(
        id="LOCAL_RESIDENT_01",
        name="Priya Sharma (North Hamlet)",
        role="resident",
        position_xy=[130.0, 75.0],
        notification_radius_m=180.0,
        zone="farm_adjacent",
    ),
    SimulatedRecipient(
        id="LOCAL_RESIDENT_02",
        name="Devraj Singh (South Homestead)",
        role="resident",
        position_xy=[120.0, 140.0],
        notification_radius_m=160.0,
        zone="farm_adjacent",
    ),
    SimulatedRecipient(
        id="PATROL_UNIT_01",
        name="Ranger Patrol Unit Alpha",
        role="patrol",
        position_xy=[85.0, 45.0],
        notification_radius_m=200.0,
        zone="buffer_corridor",
    ),
]

# Default simulated authority endpoints
DEFAULT_AUTHORITIES: list[AuthorityRecipient] = [
    AuthorityRecipient(
        id="WILDLIFE_CONTROL_ROOM",
        name="State Wildlife 24/7 Rapid Response Desk",
        role="wildlife_authority",
        jurisdiction="all_zones",
    ),
    AuthorityRecipient(
        id="FOREST_RANGE_OFFICE",
        name="Forest Range Office — Sector 4 Buffer Zone",
        role="forest_dept",
        jurisdiction="protected_farm_zone",
    ),
    AuthorityRecipient(
        id="LOCAL_EMERGENCY_COORDINATION",
        name="District Agro-Wildlife Emergency Cell",
        role="emergency_coord",
        jurisdiction="all_zones",
    ),
]


class AlertRouter:
    """Manages recipient selection, message generation, and dispatch routing."""

    def __init__(
        self,
        recipients: list[SimulatedRecipient] | None = None,
        authorities: list[AuthorityRecipient] | None = None,
        max_people_to_notify: int = 3,
        dedup_cooldown_s: float = 15.0,
    ):
        self.recipients = list(recipients or DEFAULT_RECIPIENTS)
        self.authorities = list(authorities or DEFAULT_AUTHORITIES)
        self.max_people = max_people_to_notify
        self.cooldown_s = dedup_cooldown_s
        self._last_alert_t: float = -999.0
        self._last_notified: dict[str, float] = {}  # recipient_id -> last_timestamp_s
        self._dispatch_history: list[DispatchRecord] = []

    def route_alert(
        self,
        alert_id: str,
        timestamp_s: float,
        severity: str,
        estimated_position: list[float] | None,
        eta_s: float | None = None,
        species: str = "ELEPHANT",
        risk_score: float = 0.8,
    ) -> list[DispatchRecord]:
        """Select nearest eligible people + relevant authorities, and create dispatches."""
        # Prevent rapid warning alert spam within cooldown window
        if severity != "CRITICAL_BREACH" and (timestamp_s - self._last_alert_t) < self.cooldown_s:
            return []

        self._last_alert_t = timestamp_s
        dispatches: list[DispatchRecord] = []

        # Reference location for distance (use estimated position or default boundary intercept)
        ref_x = estimated_position[0] if estimated_position else 100.0
        ref_y = estimated_position[1] if estimated_position else 100.0

        # 1. Calculate distances to all community recipients
        recipient_distances: list[tuple[float, SimulatedRecipient]] = []
        for r in self.recipients:
            dx = r.position_xy[0] - ref_x
            dy = r.position_xy[1] - ref_y
            dist = math.hypot(dx, dy)
            recipient_distances.append((dist, r))

        # Sort by proximity
        recipient_distances.sort(key=lambda x: x[0])

        # Filter by radius and deduplication cooldown
        selected_people: list[tuple[float, SimulatedRecipient]] = []
        in_radius = [(dist, r) for dist, r in recipient_distances if dist <= r.notification_radius_m]
        candidates = in_radius if in_radius else recipient_distances[:self.max_people]

        for dist, r in candidates:
            last_t = self._last_notified.get(r.id, -999.0)
            if (timestamp_s - last_t) >= self.cooldown_s or severity == "CRITICAL_BREACH":
                selected_people.append((dist, r))
                if len(selected_people) >= self.max_people:
                    break

        # 2. Build messages and dispatch records for selected people
        for dist, r in selected_people:
            self._last_notified[r.id] = timestamp_s

            if severity == "CRITICAL_BREACH":
                msg = (
                    f"PRW-Wild CRITICAL BREACH: Boundary fence breach confirmed at perimeter! "
                    f"Target: {species.upper()}. Estimated Location: ({ref_x:.1f}m, {ref_y:.1f}m). "
                    f"Time: {timestamp_s:.1f}s. Immediate response protocol active. Event: {alert_id}. "
                    f"[SIMULATED DELIVERY — NOT SENT TO A REAL PERSON]"
                )
            else:
                eta_str = f"{eta_s:.1f}s" if eta_s is not None else "imminent"
                msg = (
                    f"PRW-Wild WARNING: Possible {species.lower()} approach detected near boundary. "
                    f"Risk: {severity} ({risk_score:.2f}). ETA to fence: {eta_str}. "
                    f"Estimated Location: ({ref_x:.1f}m, {ref_y:.1f}m). Event: {alert_id}. "
                    f"Follow configured local safety procedure. [SIMULATED DELIVERY — NOT SENT TO A REAL PERSON]"
                )

            rec = DispatchRecord(
                dispatch_id=uuid.uuid4().hex[:10],
                alert_id=alert_id,
                timestamp_s=timestamp_s,
                recipient_id=r.id,
                recipient_name=r.name,
                role=r.role,
                distance_m=round(dist, 1),
                severity=severity,
                channel="simulated_sms",
                status="SIMULATED",
                message_text=msg,
                is_simulated=True,
            )
            dispatches.append(rec)
            self._dispatch_history.append(rec)

        # 3. Build messages and dispatch records for authorities
        for auth in self.authorities:
            last_t = self._last_notified.get(auth.id, -999.0)
            if (timestamp_s - last_t) < self.cooldown_s and severity != "CRITICAL_BREACH":
                continue

            self._last_notified[auth.id] = timestamp_s

            if severity == "CRITICAL_BREACH":
                auth_msg = (
                    f"[AUTHORITY URGENT] PRW-Wild: Boundary breach confirmed at coordinates ({ref_x:.1f}, {ref_y:.1f}). "
                    f"Target species: {species.upper()}. Controller event ID: {alert_id}. "
                    f"Jurisdiction: {auth.jurisdiction}. Automated escalation dispatches issued. "
                    f"[SIMULATED DELIVERY — NOT SENT TO A REAL PERSON]"
                )
            else:
                auth_msg = (
                    f"[AUTHORITY DISPATCH] PRW-Wild: Perimeter approach tracking active. "
                    f"Species: {species.upper()}. Location: ({ref_x:.1f}, {ref_y:.1f}). ETA: {eta_s or 'N/A'}. "
                    f"Risk Score: {risk_score:.2f}. Nearest residents alerted. "
                    f"[SIMULATED DELIVERY — NOT SENT TO A REAL PERSON]"
                )

            auth_rec = DispatchRecord(
                dispatch_id=uuid.uuid4().hex[:10],
                alert_id=alert_id,
                timestamp_s=timestamp_s,
                recipient_id=auth.id,
                recipient_name=auth.name,
                role=auth.role,
                distance_m=None,
                severity=severity,
                channel="simulated_control_radio",
                status="SIMULATED",
                message_text=auth_msg,
                is_simulated=True,
            )
            dispatches.append(auth_rec)
            self._dispatch_history.append(auth_rec)

        return dispatches

    @property
    def history(self) -> list[DispatchRecord]:
        return list(self._dispatch_history)

    def reset(self) -> None:
        self._last_notified.clear()
        self._dispatch_history.clear()

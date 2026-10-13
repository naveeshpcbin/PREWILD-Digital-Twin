"""Unit tests for the Alert Routing and Recipient Dispatch layer."""

import pytest
from prw_wild.dispatch import (
    SimulatedRecipient, AuthorityRecipient, DispatchRecord,
    AlertRouter, DEFAULT_RECIPIENTS, DEFAULT_AUTHORITIES,
)


def test_recipients_initialized():
    assert len(DEFAULT_RECIPIENTS) >= 4
    for r in DEFAULT_RECIPIENTS:
        assert len(r.position_xy) == 2
        assert r.is_simulated is True

    assert len(DEFAULT_AUTHORITIES) >= 2
    for a in DEFAULT_AUTHORITIES:
        assert a.is_simulated is True


def test_nearest_recipient_selection():
    router = AlertRouter(max_people_to_notify=2)
    # Target near [110, 100] -> FARM_OPERATOR_01 at [115, 105] and FIELD_WORKER_01 at [108, 92] are closest
    dispatches = router.route_alert(
        alert_id="test_alert_01",
        timestamp_s=10.0,
        severity="WARNING",
        estimated_position=[110.0, 100.0],
        eta_s=14.5,
        species="elephant",
    )

    assert len(dispatches) >= 2
    # Check that community recipients are sorted by distance
    people_dispatches = [d for d in dispatches if d.role in ("farmer", "worker", "resident", "patrol")]
    assert len(people_dispatches) == 2
    assert people_dispatches[0].distance_m <= people_dispatches[1].distance_m

    # Check authority dispatch is present
    auth_dispatches = [d for d in dispatches if d.role in ("wildlife_authority", "forest_dept", "emergency_coord")]
    assert len(auth_dispatches) >= 1

    # Check simulation notice in messages
    for d in dispatches:
        assert "SIMULATED DELIVERY" in d.message_text
        assert d.status == "SIMULATED"
        assert d.is_simulated is True


def test_critical_breach_escalation():
    router = AlertRouter()
    dispatches = router.route_alert(
        alert_id="breach_01",
        timestamp_s=50.0,
        severity="CRITICAL_BREACH",
        estimated_position=[100.0, 100.0],
        species="elephant",
    )

    assert len(dispatches) > 0
    for d in dispatches:
        assert d.severity == "CRITICAL_BREACH"
        assert "CRITICAL" in d.message_text or "URGENT" in d.message_text


def test_deduplication_cooldown():
    router = AlertRouter(dedup_cooldown_s=20.0)
    # First alert at t = 5.0
    d1 = router.route_alert("alert_1", 5.0, "WARNING", [100.0, 100.0])
    count1 = len(d1)
    assert count1 > 0

    # Rapid second warning at t = 8.0 (within cooldown) -> deduplicated
    d2 = router.route_alert("alert_2", 8.0, "WARNING", [100.0, 100.0])
    people2 = [d for d in d2 if d.role != "wildlife_authority" and d.role != "emergency_coord"]
    assert len(people2) == 0

    # Later alert at t = 30.0 (past cooldown) -> notified again
    d3 = router.route_alert("alert_3", 30.0, "WARNING", [100.0, 100.0])
    assert len(d3) > 0

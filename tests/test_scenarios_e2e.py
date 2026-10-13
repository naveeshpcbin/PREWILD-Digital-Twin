"""End-to-End Scenario Verification Test Suite for PRW-Wild.

Executes all 5 mandatory operational scenarios:
A. approach_crossing (Animal approaches and crosses perimeter)
B. turns_away (Animal approaches, turns away; no breach alarm)
C. nuisance_triggers (Noise pulses; rejected without breach alarm)
D. degraded_network (Sensor dropouts/outages; robust degradation)
E. camera_gating (Policy comparison: predictive vs reactive vs always-on)
"""

import pytest
from prw_wild.web.server import execute_simulation


def test_scenario_a_approach_crossing():
    """Scenario A: Animal approaches and crosses perimeter."""
    res = execute_simulation("approach_crossing", seed=42)
    assert res["success"] is True

    metrics = res["metrics"]
    events = res["events"]
    dispatches = res["dispatches"]

    # 1. Ground truth crossings
    assert metrics["actual_crossings"] == 1
    assert metrics["true_positive_detections"] >= 1
    assert metrics["crossing_recall"] == 1.0

    # 2. Warning lead time must be positive (warning preceded crossing)
    lead_time = metrics["mean_warning_lead_time_s"]
    assert lead_time is not None
    assert lead_time > 0.0, f"Warning must precede crossing, got lead time {lead_time}s"

    # 3. Boundary breach and dispatches generated
    event_types = [e.get("event_type") for e in events]
    assert "boundary_breach" in event_types
    assert "dispatch" in event_types
    assert len(dispatches) > 0

    # 4. Critical dispatches present
    crit_dispatches = [d for d in dispatches if d["severity"] == "CRITICAL_BREACH"]
    assert len(crit_dispatches) > 0


def test_scenario_b_turns_away():
    """Scenario B: Animal approaches and turns away."""
    res = execute_simulation("turns_away", seed=42)
    assert res["success"] is True

    metrics = res["metrics"]
    events = res["events"]

    # No actual crossing
    assert metrics["actual_crossings"] == 0

    # No boundary breach event must occur
    event_types = [e.get("event_type") for e in events]
    assert "boundary_breach" not in event_types

    # Lead time is undefined (None) when no crossing occurs
    assert metrics["mean_warning_lead_time_s"] is None


def test_scenario_c_nuisance_triggers():
    """Scenario C: Nuisance sensor triggers without animal crossing."""
    res = execute_simulation("nuisance_triggers", seed=42)
    assert res["success"] is True

    metrics = res["metrics"]
    events = res["events"]

    assert metrics["actual_crossings"] == 0
    event_types = [e.get("event_type") for e in events]
    assert "boundary_breach" not in event_types


def test_scenario_d_degraded_network():
    """Scenario D: Sensor outages and high packet loss."""
    res = execute_simulation("degraded_network", seed=42)
    assert res["success"] is True
    assert "metrics" in res
    assert "events" in res
    assert len(res["events"]) > 0


def test_scenario_e_camera_gating_policy_comparison():
    """Scenario E: Camera-gating policy comparison under identical seed."""
    seed = 42
    res_pred = execute_simulation("approach_crossing", seed=seed, overrides={"policies": {"active": "predictive"}})
    res_pir = execute_simulation("approach_crossing", seed=seed, overrides={"policies": {"active": "pir_only"}})
    res_always = execute_simulation("approach_crossing", seed=seed, overrides={"policies": {"active": "always_on"}})

    m_pred = res_pred["metrics"]
    m_pir = res_pir["metrics"]
    m_always = res_always["metrics"]

    # Always-on camera must consume significantly more energy than predictive gating
    assert m_always["estimated_energy_j"] > m_pred["estimated_energy_j"]
    assert m_always["camera_activations"] >= m_pred["camera_activations"]

    # Energy values are estimated, not measured
    assert "Estimated" in m_pred["energy_note"]

"""Tests for the PRW-Wild Web Dashboard and API."""

import json
from pathlib import Path
from prw_wild.web.server import get_all_scenarios, execute_simulation, STATIC_DIR

def test_static_assets_exist():
    assert (STATIC_DIR / "index.html").exists()
    assert (STATIC_DIR / "style.css").exists()
    assert (STATIC_DIR / "app.js").exists()
    assert (STATIC_DIR / "vendor" / "three.min.js").exists()
    assert (STATIC_DIR / "vendor" / "OrbitControls.js").exists()
    assert (STATIC_DIR / "vendor" / "GLTFLoader.js").exists()
    project_root = STATIC_DIR.parent.parent.parent.parent
    assert (project_root / "ASSETS.md").exists()

def test_get_all_scenarios():
    scenarios = get_all_scenarios()
    assert len(scenarios) >= 5
    ids = [s["id"] for s in scenarios]
    assert "approach_crossing" in ids
    assert "turns_away" in ids
    assert "nuisance_triggers" in ids

def test_execute_simulation():
    res = execute_simulation("approach_crossing", seed=42)
    assert res["success"] is True
    assert "metrics" in res
    assert "ground_truth" in res
    assert len(res["ground_truth"]) > 0
    assert "events" in res
    assert len(res["events"]) > 0
    assert res["metrics"]["actual_crossings"] == 1
    assert "dispatches" in res
    assert len(res["dispatches"]) > 0
    event_types = [e.get("event_type") for e in res["events"]]
    assert "dispatch" in event_types
    assert "boundary_breach" in event_types

def test_counterfactual_policies():
    """Verify that multiple policies run deterministically on the same seed."""
    res_pred = execute_simulation("approach_crossing", seed=42, overrides={"policies": {"active": "predictive"}})
    res_always = execute_simulation("approach_crossing", seed=42, overrides={"policies": {"active": "always_on"}})
    res_pir = execute_simulation("approach_crossing", seed=42, overrides={"policies": {"active": "pir_only"}})
    res_rf = execute_simulation("approach_crossing", seed=42, overrides={"policies": {"active": "rf_only"}})

    assert res_pred["success"] is True
    assert res_always["success"] is True
    assert res_pir["success"] is True
    assert res_rf["success"] is True

    # Always-on camera must have equal or more camera activations than selective predictive gating
    assert res_always["metrics"]["camera_activations"] >= res_pred["metrics"]["camera_activations"]
    assert res_always["metrics"]["estimated_energy_j"] >= res_pred["metrics"]["estimated_energy_j"]


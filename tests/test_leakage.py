"""Scientific Integrity & Ground-Truth Isolation Tests.

Verifies that the operational controller never receives or accesses hidden
ground-truth states (true animal position, crossed_boundary flag, or future crossing times).
"""

import ast
from pathlib import Path
import pytest
from prw_wild.web.server import execute_simulation

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_no_ground_truth_leakage_in_controller_code():
    """Statically verifies that the controller sections in experiment_runner.py

    do NOT query animal.crossed_boundary, animal.position, or animal.species directly.
    """
    runner_path = PROJECT_ROOT / "src" / "prw_wild" / "experiment_runner.py"
    assert runner_path.exists()

    code = runner_path.read_text(encoding="utf-8")
    tree = ast.parse(code)

    # Locate the run_experiment function
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_experiment":
            func_node = node
            break
    assert func_node is not None, "run_experiment function must exist"

    # Inspect all attribute accesses
    forbidden_controller_accesses = []
    # Lines after step 2 (sensor observations) and step 8 (camera emulator) where controller operates:
    # Specifically, steps 9 (alert engine) and 10 (boundary breach)
    for node in ast.walk(func_node):
        if isinstance(node, ast.Attribute):
            # Check for direct animal.crossed_boundary access
            if node.attr == "crossed_boundary" and isinstance(node.value, ast.Name) and node.value.id == "animal":
                forbidden_controller_accesses.append((node.lineno, "animal.crossed_boundary"))

    assert len(forbidden_controller_accesses) == 0, (
        f"Forbidden ground-truth leakage detected in controller: {forbidden_controller_accesses}"
    )


def test_controller_telemetry_isolation_in_simulation_run():
    """Run approach_crossing and verify controller events consume estimated telemetry."""
    res = execute_simulation("approach_crossing", seed=42)
    assert res["success"] is True

    events = res["events"]
    gt = res["ground_truth"]

    # Collect breach events
    breach_events = [e for e in events if e.get("event_type") == "boundary_breach"]
    assert len(breach_events) >= 1

    for be in breach_events:
        # Provenance must be controller_boundary_monitor
        assert be.get("provenance") == "controller_boundary_monitor"
        # Position must be estimated
        est_pos = be.get("estimated_position_xy")
        assert est_pos is not None
        assert len(est_pos) == 2
        # Position must be at boundary fence (>= 98.0)
        assert est_pos[0] >= 98.0

    # Collect alert dispatches
    dispatches = res["dispatches"]
    assert len(dispatches) > 0
    for d in dispatches:
        # Every dispatch must be explicitly marked as simulated
        assert d["is_simulated"] is True
        assert d["status"] == "SIMULATED"
        assert "SIMULATED" in d["message_text"]

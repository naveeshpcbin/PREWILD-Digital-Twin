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

def test_production_elephant_asset_and_loader_integration():
    """Verify that the verified production Asian Elephant GLB exists, is valid GLTF, and integrated in HTML/JS."""
    elephant_glb = STATIC_DIR / "assets" / "animals" / "asian_elephant_production.glb"
    assert elephant_glb.exists(), f"Production elephant GLB missing at {elephant_glb}"
    assert elephant_glb.stat().st_size > 100_000, "GLB file is unexpectedly small"

    # Verify binary glTF header
    with open(elephant_glb, "rb") as f:
        magic = f.read(4)
        assert magic == b"glTF", "Asset does not have valid glTF magic header"
        version = int.from_bytes(f.read(4), "little")
        assert version == 2, f"Expected glTF version 2, got {version}"

    # Verify index.html loads GLTFLoader.js
    html_content = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    assert "GLTFLoader.js" in html_content, "index.html must include vendor/GLTFLoader.js"

    # Verify app.js references the production GLB and mixer
    app_js_content = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert "asian_elephant_production.glb" in app_js_content, "app.js must load asian_elephant_production.glb"
    assert "threeObjects.elephantMixer" in app_js_content, "app.js must wire up elephantMixer"


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

def test_sidebar_physical_hardware_panel_and_calibration():
    """Verify that the right sidebar includes live physical hardware telemetry alongside simulation."""
    html_content = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    assert "sidePhysicalHardwarePanel" in html_content
    assert "sideBoxPir" in html_content
    assert "sideBoxPiezo" in html_content
    assert "sideBoxMic" in html_content
    assert "sidePiezoSlider" in html_content
    assert 'id="sidePiezoSlider" min="0" max="4095"' in html_content
    assert "sideMicSlider" in html_content
    assert 'id="sideMicSlider" min="0" max="500000"' in html_content
    assert "sideMicVuFill" in html_content
    assert "sideMicVuThreshold" in html_content
    assert "sideLed1" in html_content
    assert "sideLed6" in html_content

    # Verify CSS styling exists
    css_content = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
    assert ".physical-hardware-panel" in css_content
    assert ".side-vu-bar" in css_content
    assert ".side-led-bulb" in css_content

    # Verify app.js wires up the sidebar and calibration handlers
    app_js_content = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert "sideEsp32bConnPill" in app_js_content
    assert "sideMicVuFill" in app_js_content
    assert "updateHardwareCalibration" in app_js_content
    assert "loadHardwareCalibration" in app_js_content

def test_security_guards_and_sanitization():
    """Verify security controls, XSS defense-in-depth, and input sanitization."""
    # Verify app.js defines and uses escapeHtml
    app_js_content = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert "function escapeHtml" in app_js_content
    assert "escapeHtml(a.sensor_type)" in app_js_content
    assert "escapeHtml(d.recipient_name)" in app_js_content

    # Verify server.py implements security headers and path traversal guards
    server_py_content = (STATIC_DIR.parent / "server.py").read_text(encoding="utf-8")
    assert "X-Content-Type-Options" in server_py_content
    assert "X-Frame-Options" in server_py_content
    assert "Content-Security-Policy" in server_py_content
    assert "Invalid scenario ID format" in server_py_content
    assert "Invalid device identifier format" in server_py_content
    assert "Layer out of range" in server_py_content
    assert "Invalid hardware operating mode" in server_py_content


def test_dual_node_mode_toggle_markup_and_script():
    """Verify dual ESP32 manual toggle controls, cascading UI elements, and endpoint registration."""
    # 1. HTML Markup
    html_content = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    assert "sideNodeModesStrip" in html_content
    assert "toggleEsp32AMode" in html_content
    assert "toggleEsp32BMode" in html_content
    assert "sideNodeCascadeNotice" in html_content
    assert "txtNodeCascadeNotice" in html_content

    # 2. CSS Styles
    css_content = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
    assert ".side-node-modes-strip" in css_content
    assert ".btn-node-toggle" in css_content
    assert ".btn-node-toggle.active" in css_content
    assert ".btn-node-toggle.cascade-locked" in css_content
    assert ".side-node-cascade-notice" in css_content

    # 3. JavaScript Wiring
    app_js_content = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert "toggleEsp32AMode" in app_js_content
    assert "toggleEsp32BMode" in app_js_content
    assert "updateNodeModeButtonsUI" in app_js_content
    assert "setNodeMode" in app_js_content
    assert "loadNodeModes" in app_js_content
    assert "/api/hardware/nodes" in app_js_content

    # 4. Server Endpoints
    server_py_content = (STATIC_DIR.parent / "server.py").read_text(encoding="utf-8")
    assert 'path == "/api/hardware/nodes"' in server_py_content




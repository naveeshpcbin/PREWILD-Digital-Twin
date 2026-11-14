"""Tests for PRW-Wild Hardware Reference Registry, Pin Mappings, and Schemas.

Includes strict regression tests asserting official Espressif ESP32-S3-DevKitC-1 v1.1
header assignments against the manufacturer hardware guide:
https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html
"""

import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HARDWARE_DIR = PROJECT_ROOT / "hardware" / "devices"
STATIC_HW_DIR = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "hardware"


def test_hardware_directory_and_files_exist():
    """Verify all required hardware reference JSON files exist in both root and web static mirrors."""
    assert HARDWARE_DIR.exists()
    required_files = [
        "esp32_s3_devkitc1_v1_1.json",
        "hc_sr501_reference.json",
        "sw420_reference.json",
        "inmp441_breakout_reference.json",
        "ai_thinker_esp32_cam_ov2640.json",
        "wifi_access_point_reference.json",
        "camera_reference.json",
        "power_system_reference.json",
    ]
    for rf in required_files:
        fp = HARDWARE_DIR / rf
        assert fp.exists(), f"Missing required hardware reference file: {rf}"
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "device_id" in data
            assert "name" in data

        # Check web static mirror
        static_fp = STATIC_HW_DIR / "devices" / rf
        assert static_fp.exists(), f"Missing static mirror hardware reference file: {rf}"


def test_esp32_s3_devkitc1_v1_1_official_pinout():
    """Verify ESP32-S3-DevKitC-1 v1.1 pinout matches official Espressif User Guide v1.1 exactly."""
    fp = HARDWARE_DIR / "esp32_s3_devkitc1_v1_1.json"
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["board_revision"] == "v1.1"
    assert data["module_variant"] == "ESP32-S3-WROOM-1"

    # --- Header J1 (Left Rail, 22 pins) ---
    j1 = data["headers"]["J1"]
    assert len(j1) == 22, "Header J1 must have exactly 22 pins"

    official_j1_signals = [
        (1, "3V3", "Power"),
        (2, "3V3", "Power"),
        (3, "RST", "Input"),
        (4, "GPIO4", "I/O"),
        (5, "GPIO5", "I/O"),
        (6, "GPIO6", "I/O"),
        (7, "GPIO7", "I/O"),
        (8, "GPIO15", "I/O"),
        (9, "GPIO16", "I/O"),
        (10, "GPIO17", "I/O"),
        (11, "GPIO18", "I/O"),
        (12, "GPIO8", "I/O"),
        (13, "GPIO3", "I/O"),
        (14, "GPIO46", "Input"),
        (15, "GPIO9", "I/O"),   # Pin 15 is GPIO9 (INMP441 SCK)
        (16, "GPIO10", "I/O"),
        (17, "GPIO11", "I/O"),
        (18, "GPIO12", "I/O"),
        (19, "GPIO13", "I/O"),
        (20, "GPIO14", "I/O"),
        (21, "5V", "Power"),    # Pin 21 is 5V (HC-SR501 VCC)
        (22, "GND", "Power"),   # Pin 22 is GND
    ]

    for pos, expected_sig, expected_type in official_j1_signals:
        idx = pos - 1
        assert j1[idx]["pos"] == pos, f"J1 pin {pos} position mismatch"
        assert j1[idx]["signal"] == expected_sig, f"J1 pin {pos} expected {expected_sig}, got {j1[idx]['signal']}"
        assert j1[idx]["type"] == expected_type, f"J1 pin {pos} expected type {expected_type}, got {j1[idx]['type']}"

    # Explicit critical regressions for J1
    assert j1[20]["signal"] == "5V", "J1 pin 21 MUST be 5V power supply"
    assert j1[21]["signal"] == "GND", "J1 pin 22 MUST be Ground"
    assert j1[14]["signal"] == "GPIO9", "J1 pin 15 MUST be GPIO9 (INMP441 SCK)"

    # --- Header J3 (Right Rail, 22 pins) ---
    j3 = data["headers"]["J3"]
    assert len(j3) == 22, "Header J3 must have exactly 22 pins"

    official_j3_signals = [
        (1, "GND", "Power"),     # Pin 1 is Ground (SW-420 GND)
        (2, "GPIO43", "I/O"),    # TX
        (3, "GPIO44", "I/O"),    # RX
        (4, "GPIO1", "I/O"),
        (5, "GPIO2", "I/O"),
        (6, "GPIO42", "I/O"),
        (7, "GPIO41", "I/O"),
        (8, "GPIO40", "I/O"),
        (9, "GPIO39", "I/O"),
        (10, "GPIO38", "I/O"),   # WS2812 RGB LED on v1.1
        (11, "GPIO37", "Reserved"),
        (12, "GPIO36", "Reserved"),
        (13, "GPIO35", "Reserved"),
        (14, "GPIO0", "I/O"),    # BOOT button
        (15, "GPIO45", "I/O"),
        (16, "GPIO48", "I/O"),   # Pin 16 is GPIO48 (SPICLK_N)
        (17, "GPIO47", "I/O"),   # Pin 17 is GPIO47 (SPICLK_P)
        (18, "GPIO21", "I/O"),
        (19, "GPIO20", "I/O"),   # USB_D+
        (20, "GPIO19", "I/O"),   # USB_D- (GPIO19)
        (21, "GND", "Power"),    # Pin 21 is Ground (INMP441 GND & L/R)
        (22, "GND", "Power"),    # Pin 22 is Ground (HC-SR501 GND)
    ]

    for pos, expected_sig, expected_type in official_j3_signals:
        idx = pos - 1
        assert j3[idx]["pos"] == pos, f"J3 pin {pos} position mismatch"
        assert j3[idx]["signal"] == expected_sig, f"J3 pin {pos} expected {expected_sig}, got {j3[idx]['signal']}"
        assert j3[idx]["type"] == expected_type, f"J3 pin {pos} expected type {expected_type}, got {j3[idx]['type']}"

    # Explicit critical regressions for J3
    assert j3[0]["signal"] == "GND", "J3 pin 1 MUST be Ground"
    assert j3[9]["signal"] == "GPIO38", "J3 pin 10 MUST be GPIO38 (WS2812 RGB LED on v1.1)"
    assert j3[15]["signal"] == "GPIO48", "J3 pin 16 MUST be GPIO48"
    assert j3[16]["signal"] == "GPIO47", "J3 pin 17 MUST be GPIO47"
    assert j3[18]["signal"] == "GPIO20", "J3 pin 19 MUST be GPIO20 (USB_D+)"
    assert j3[19]["signal"] == "GPIO19", "J3 pin 20 MUST be GPIO19 (USB_D-)"
    assert j3[20]["signal"] == "GND", "J3 pin 21 MUST be Ground"
    assert j3[21]["signal"] == "GND", "J3 pin 22 MUST be Ground"

    # Verify proposed sensor wiring mappings in device JSON
    proposed = {w["sensor"] + "_" + w["module_pin"]: w for w in data["proposed_sensor_wiring"]}
    assert "HC-SR501 Passive Infrared (PIR) Sensor_VCC" in proposed
    assert "J1-21 (5V)" in proposed["HC-SR501 Passive Infrared (PIR) Sensor_VCC"]["esp32_pin"]

    assert "INMP441 Omnidirectional Digital I2S Microphone Breakout_L/R" in proposed
    assert "J3-21 (GND)" in proposed["INMP441 Omnidirectional Digital I2S Microphone Breakout_L/R"]["esp32_pin"]

    assert "INMP441 Omnidirectional Digital I2S Microphone Breakout_SCK" in proposed
    assert "J1-15 (GPIO9)" in proposed["INMP441 Omnidirectional Digital I2S Microphone Breakout_SCK"]["esp32_pin"]


def test_ai_thinker_esp32_cam_pinout():
    """Verify ESP32-CAM OV2640 dedicated camera bus separation."""
    fp = HARDWARE_DIR / "ai_thinker_esp32_cam_ov2640.json"
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)

    cam_pins = data["dedicated_camera_pin_map"]
    assert cam_pins["D0"] == "GPIO5"
    assert cam_pins["D1"] == "GPIO18"
    assert cam_pins["D2"] == "GPIO19"
    assert cam_pins["D3"] == "GPIO21"
    assert cam_pins["D4"] == "GPIO36"
    assert cam_pins["D5"] == "GPIO39"
    assert cam_pins["D6"] == "GPIO34"
    assert cam_pins["D7"] == "GPIO35"
    assert cam_pins["XCLK"] == "GPIO0"
    assert cam_pins["PCLK"] == "GPIO22"
    assert cam_pins["VSYNC"] == "GPIO25"
    assert cam_pins["HREF"] == "GPIO23"
    assert cam_pins["FLASH_LED"] == "GPIO4"


def test_wiring_manifest_strict_validity():
    """Verify centralized wiring manifest: all 11 nets reference valid, non-conflicting pins."""
    manifest_paths = [
        PROJECT_ROOT / "hardware" / "wiring_manifest.json",
        STATIC_HW_DIR / "wiring_manifest.json",
    ]

    for manifest_path in manifest_paths:
        assert manifest_path.exists(), f"{manifest_path} must exist"
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["manifest_version"] == "1.0.0"
        assert data["board_revision"] == "ESP32-S3-DevKitC-1 v1.1"
        assert data["module_variant"] == "ESP32-S3-WROOM-1"

        summary = data["verification_summary"]
        assert summary["total_nets"] == 11
        assert summary["verified_nets"] == 11
        assert summary["conflicts_found"] == 0
        assert summary["strapping_pin_violations"] == 0
        assert summary["memory_bus_violations"] == 0

        nets = data["wiring_nets"]
        assert len(nets) == 11

        net_by_id = {n["net_id"]: n for n in nets}

        # Net 1: HC-SR501 VCC connected to Header J1 Pin 21 (5V)
        n_5v = net_by_id["NET_5V_PIR_PWR"]
        assert n_5v["source"]["connector"] == "Header J1"
        assert n_5v["source"]["pin_position"] == 21
        assert n_5v["source"]["pin_signal"] == "5V"
        assert n_5v["source"]["rel_coord_3d"][0] == pytest.approx(-1.14, abs=0.01)
        assert n_5v["source"]["rel_coord_3d"][2] == pytest.approx(2.42, abs=0.05)
        assert n_5v["voltage_domain_v"] == 5.0
        assert n_5v["destination"]["pin_signal"] == "VCC"

        # Net 2: HC-SR501 GND connected to Header J3 Pin 22 (GND)
        n_gnd_pir = net_by_id["NET_GND_PIR"]
        assert n_gnd_pir["source"]["connector"] == "Header J3"
        assert n_gnd_pir["source"]["pin_position"] == 22
        assert n_gnd_pir["source"]["pin_signal"] == "GND"
        assert n_gnd_pir["voltage_domain_v"] == 0.0

        # Net 8: INMP441 GND & L/R connected to Header J3 Pin 21 (GND)
        n_gnd_mic = net_by_id["NET_GND_INMP441"]
        assert n_gnd_mic["source"]["connector"] == "Header J3"
        assert n_gnd_mic["source"]["pin_position"] == 21
        assert n_gnd_mic["source"]["pin_signal"] == "GND"
        assert n_gnd_mic["source"]["rel_coord_3d"][0] == pytest.approx(1.14, abs=0.01)
        assert n_gnd_mic["source"]["rel_coord_3d"][2] == pytest.approx(2.42, abs=0.05)
        assert n_gnd_mic["voltage_domain_v"] == 0.0

        # Net 11: INMP441 SCK connected to Header J1 Pin 15 (GPIO9)
        n_sck = net_by_id["NET_I2S_MIC_SCK"]
        assert n_sck["source"]["connector"] == "Header J1"
        assert n_sck["source"]["pin_position"] == 15
        assert n_sck["source"]["pin_signal"] == "GPIO9"
        assert n_sck["source"]["rel_coord_3d"][0] == pytest.approx(-1.14, abs=0.01)
        assert n_sck["source"]["rel_coord_3d"][2] == pytest.approx(0.90, abs=0.05)
        assert n_sck["voltage_domain_v"] == 3.3

        # Assert no nets use reserved Octal Flash/PSRAM pins (GPIO35, GPIO36, GPIO37)
        reserved_signals = {"GPIO35", "GPIO36", "GPIO37"}
        for net in nets:
            assert net["source"]["pin_signal"] not in reserved_signals
            assert net["destination"]["pin_signal"] not in reserved_signals

        # Assert all nets have 3D coordinates and official verification
        for net in nets:
            assert len(net["source"]["rel_coord_3d"]) == 3
            assert len(net["destination"]["rel_coord_3d"]) == 3
            assert net["verification_status"] == "VERIFIED_OFFICIAL_DOCUMENTATION"


def test_app_js_wiring_manifest_and_fallback_consistency():
    """Verify src/prw_wild/web/static/app.js embeds the exact verified pinout and nets."""
    app_js_path = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "app.js"
    assert app_js_path.exists()
    content = app_js_path.read_text(encoding="utf-8")

    # Verify HC-SR501 VCC is routed to Header J1 Pin 21 (5V) in app.js
    assert 'connector: "Header J1"' in content
    assert 'pin_position: 21,\n          pin_signal: "5V"' in content or 'pin_position: 21,\r\n          pin_signal: "5V"' in content

    # Verify INMP441 GND is routed to Header J3 Pin 21 (GND) in app.js
    assert 'connector: "Header J3",\n          pin_position: 21,\n          pin_signal: "GND"' in content or \
           'connector: "Header J3",\r\n          pin_position: 21,\r\n          pin_signal: "GND"' in content

    # Verify INMP441 SCK is routed to Header J1 Pin 15 (GPIO9) in app.js
    assert 'connector: "Header J1",\n          pin_position: 15,\n          pin_signal: "GPIO9"' in content or \
           'connector: "Header J1",\r\n          pin_position: 15,\r\n          pin_signal: "GPIO9"' in content

    # Verify J3 Pin 16 is GPIO48 and J3 Pin 17 is GPIO47 in app.js fallback
    assert "{ pos: 16, signal: 'GPIO48'" in content
    assert "{ pos: 17, signal: 'GPIO47'" in content

    # Verify J3 Pin 20 is GPIO19 and J3 Pin 21 is GND in app.js fallback
    assert "{ pos: 20, signal: 'GPIO19'" in content
    assert "{ pos: 21, signal: 'GND'" in content
    assert "{ pos: 22, signal: 'GND'" in content


def test_authoritative_device_controller_synchronization():
    """Verify single authoritative device controller and diagnostics in HTML/CSS/JS."""
    app_js_path = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "app.js"
    index_html_path = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "index.html"
    style_css_path = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "style.css"

    js_content = app_js_path.read_text(encoding="utf-8")
    html_content = index_html_path.read_text(encoding="utf-8")
    css_content = style_css_path.read_text(encoding="utf-8")

    # Single authoritative state variable and controller
    assert "let selectedDeviceId =" in js_content
    assert "async function setSelectedHardwareDevice(deviceId, options = {})" in js_content

    # Dynamic camera fitting and aspect NaN guard
    assert "function fitHardwareCameraToObject(object, fovMultiplier = 1.35)" in js_content
    assert "let aspect = width / height;" in js_content
    assert "if (!isFinite(aspect) || aspect <= 0)" in js_content

    # Viewport diagnostics overlay and fallback error banner
    assert 'id="hwDiagnosticsOverlay"' in html_content
    assert 'id="hw3DErrorBanner"' in html_content
    assert ".hw-3d-diagnostics" in css_content
    assert ".hw-3d-error-banner" in css_content

    # ResizeObserver attachment
    assert "new ResizeObserver" in js_content


def test_all_device_tabs_and_3d_builders_exist():
    """Verify that every hardware device has a dedicated 3D procedural builder and tab binding."""
    app_js_path = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "app.js"
    js_content = app_js_path.read_text(encoding="utf-8")

    device_builders = [
        ("workbench", "createMultiBoardWiringWorkbench"),
        ("esp32_s3_devkitc1_v1_1", "createESP32DevKitModel"),
        ("hc_sr501_reference", "createPIRSensorModel"),
        ("sw420_reference", "createVibrationSensorModel"),
        ("inmp441_breakout_reference", "createMicrophoneModel"),
        ("ai_thinker_esp32_cam_ov2640", "createESP32CamModel"),
        ("wifi_access_point_reference", "createRouterModelDetails"),
        ("power_system_reference", "createSolarPowerModel"),
    ]

    for dev_id, builder_name in device_builders:
        assert f"function {builder_name}" in js_content, f"Missing builder {builder_name}"
        assert f"deviceId === '{dev_id}'" in js_content or f"targetDev = '{dev_id}'" in js_content, f"Device {dev_id} not handled in device controller"


def test_3d_tube_geometry_cables_in_workbench():
    """Verify all 11 nets use 3D TubeGeometry meshes with Catmull-Rom spline curves."""
    app_js_path = PROJECT_ROOT / "src" / "prw_wild" / "web" / "static" / "app.js"
    js_content = app_js_path.read_text(encoding="utf-8")

    assert "THREE.CatmullRomCurve3" in js_content
    assert "THREE.TubeGeometry(curve, 36, 0.042, 8, false)" in js_content
    assert "THREE.MeshStandardMaterial({" in js_content
    assert "wireMesh.userData = {" in js_content
    assert "hwWireMeshes.push(wireMesh);" in js_content


def test_all_five_hardware_glb_models_exist_and_valid():
    """Verify all 5 Blender-authored GLB hardware models exist and are valid binary glTF v2."""
    hw_assets_dir = STATIC_HW_DIR.parent / "assets" / "hardware"
    assert hw_assets_dir.exists(), f"Hardware assets directory missing: {hw_assets_dir}"

    models = [
        "esp32_s3_devkitc1_v1_1.glb",
        "esp32_cam_ov2640.glb",
        "hc_sr501_pir.glb",
        "sw420_vibration.glb",
        "inmp441_microphone.glb",
    ]

    for m in models:
        fp = hw_assets_dir / m
        assert fp.exists(), f"Model {m} does not exist at {fp}"
        assert fp.stat().st_size > 10_000, f"Model {m} is smaller than 10KB ({fp.stat().st_size} bytes)"

        with open(fp, "rb") as f:
            magic = f.read(4)
            assert magic == b"glTF", f"Model {m} missing glTF binary magic"
            version = int.from_bytes(f.read(4), "little")
            assert version == 2, f"Model {m} expected glTF v2, got {version}"


def test_pubg_tactical_hud_elements_and_fullscreen():
    """Verify PUBG-inspired tactical inspection HUD elements and fullscreen controls."""
    index_html = (STATIC_HW_DIR.parent / "index.html").read_text(encoding="utf-8")
    assert "pubg-hud-bracket" in index_html, "index.html must include tactical corner brackets"
    assert "pubg-center-reticle" in index_html, "index.html must include inspection reticle"
    assert "pubg-telemetry-stamp" in index_html, "index.html must include inspection telemetry stamp"
    assert "btnHwFullscreen" in index_html, "index.html must include fullscreen toggle button"

    style_css = (STATIC_HW_DIR.parent / "style.css").read_text(encoding="utf-8")
    assert ".pubg-hud-bracket" in style_css, "style.css must style tactical corner brackets"
    assert ".pubg-center-reticle" in style_css, "style.css must style inspection reticle"
    assert "#hardwareLab3DContainer:fullscreen" in style_css, "style.css must handle fullscreen container layout"


def test_hardware_pinouts_and_manifest_coordinates_consistency():
    """Verify that all 11 nets in wiring_manifest.json connect accurately without floating offsets."""
    manifest_fp = PROJECT_ROOT / "hardware" / "wiring_manifest.json"
    with open(manifest_fp, "r", encoding="utf-8") as f:
        data = json.load(f)

    nets = data["wiring_nets"]
    assert len(nets) == 11

    for net in nets:
        src_coord = net["source"]["rel_coord_3d"]
        dst_coord = net["destination"]["rel_coord_3d"]
        assert len(src_coord) == 3, f"Source coord invalid in {net['net_id']}"
        assert len(dst_coord) == 3, f"Destination coord invalid in {net['net_id']}"
        # Pin height is 0.35
        assert src_coord[1] == pytest.approx(0.35, abs=0.01)
        assert dst_coord[1] == pytest.approx(0.35, abs=0.01)




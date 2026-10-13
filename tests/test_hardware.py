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

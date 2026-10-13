"""Tests for PRW-Wild Hardware Reference Registry and Schemas."""

import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HARDWARE_DIR = PROJECT_ROOT / "hardware" / "devices"


def test_hardware_directory_and_files_exist():
    """Verify all required hardware reference JSON files exist."""
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


def test_esp32_s3_devkitc1_v1_1_specification():
    """Verify ESP32-S3-DevKitC-1 v1.1 pinout and revision-specific constraints."""
    fp = HARDWARE_DIR / "esp32_s3_devkitc1_v1_1.json"
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["board_revision"] == "v1.1"
    assert data["module_variant"] == "ESP32-S3-WROOM-1"

    # Verify Header J1 has exactly 22 pins
    j1 = data["headers"]["J1"]
    assert len(j1) == 22
    assert j1[0]["signal"] == "3V3"
    assert j1[3]["signal"] == "GPIO4"  # HC-SR501 OUT
    assert j1[4]["signal"] == "GPIO5"  # SW-420 DO
    assert j1[6]["signal"] == "GPIO7"  # INMP441 SD
    assert j1[11]["signal"] == "GPIO8" # INMP441 WS
    assert j1[16]["signal"] == "GPIO9" # INMP441 SCK

    # Verify Header J3 has exactly 22 pins
    j3 = data["headers"]["J3"]
    assert len(j3) == 22
    assert j3[0]["signal"] == "GND"
    # On v1.1, GPIO38 is assigned to onboard RGB LED (position 10)
    assert j3[9]["signal"] == "GPIO38"
    assert "RGB" in j3[9]["desc"]
    # Internal Octal Flash/PSRAM bus pins reserved
    assert j3[10]["signal"] == "GPIO37" and j3[10]["type"] == "Reserved"
    assert j3[11]["signal"] == "GPIO36" and j3[11]["type"] == "Reserved"
    assert j3[12]["signal"] == "GPIO35" and j3[12]["type"] == "Reserved"
    # 5V VBUS rail is at J3 pos 21
    assert j3[20]["signal"] == "5V"

    # Verify proposed sensor wiring mappings
    sensor_wirings = {w["sensor"]: w for w in data["proposed_sensor_wiring"]}
    assert any("HC-SR501" in k for k in sensor_wirings)
    assert any("SW-420" in k for k in sensor_wirings)
    assert any("INMP441" in k for k in sensor_wirings)


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


def test_wiring_manifest_specification():
    """Verify centralized machine-readable wiring manifest and 11 verified nets."""
    manifest_path = PROJECT_ROOT / "hardware" / "wiring_manifest.json"
    assert manifest_path.exists(), "wiring_manifest.json must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_version"] == "1.0.0"
    assert data["board_revision"] == "ESP32-S3-DevKitC-1 v1.1"
    assert data["module_variant"] == "ESP32-S3-WROOM-1"

    summary = data["verification_summary"]
    assert summary["total_nets"] == 11
    assert summary["verified_nets"] == 11
    assert summary["conflicts_found"] == 0

    nets = data["wiring_nets"]
    assert len(nets) == 11

    # Check required net IDs
    net_ids = {n["net_id"] for n in nets}
    expected_net_ids = {
        "NET_5V_PIR_PWR",
        "NET_GND_PIR",
        "NET_SIG_PIR_OUT",
        "NET_3V3_SW420_PWR",
        "NET_GND_SW420",
        "NET_SIG_SW420_DO",
        "NET_3V3_INMP441_PWR",
        "NET_GND_INMP441",
        "NET_I2S_MIC_SD",
        "NET_I2S_MIC_WS",
        "NET_I2S_MIC_SCK",
    }
    assert net_ids == expected_net_ids

    # Validate coordinate completeness and electrical parameters for every net
    for net in nets:
        assert "rel_coord_3d" in net["source"]
        assert len(net["source"]["rel_coord_3d"]) == 3
        assert "rel_coord_3d" in net["destination"]
        assert len(net["destination"]["rel_coord_3d"]) == 3
        assert net["voltage_domain_v"] in [0.0, 3.3, 5.0]
        assert net["verification_status"] == "VERIFIED_OFFICIAL_DOCUMENTATION"


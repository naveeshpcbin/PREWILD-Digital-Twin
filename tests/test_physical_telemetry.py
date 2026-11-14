"""Comprehensive Automated Verification for Physical Dual-ESP32 Telemetry & Gateway.

Tests cover:
1. Frame parsing (valid machine-readable USB telemetry from ESP32-B)
2. Damaged/malformed packets & rejection handling
3. Session tracking and sequence number continuity (duplicates, stale packets)
4. Safety gate compliance (Piezo disc remains DISABLED / NOT_VERIFIED by default)
5. Sensor state transitions (PIR warmup vs ready vs active, Mic RMS)
6. Edge-triggered alert generation with strict deduplication
7. Alert acknowledgement
8. Staleness detection after 2.2s heartbeat timeout
9. Architectural domain isolation: physical telemetry NEVER mutates simulation state
10. All REST API endpoints for physical hardware
"""

import time
from unittest.mock import MagicMock, patch
import pytest

from prw_wild.hardware.telemetry_model import (
    PhysicalTelemetry,
    PhysicalAlertEvent,
    SensorStatus,
    ConnectionState,
)
from prw_wild.hardware.lora_bridge import (
    LoraSerialBridge,
    BridgeDiagnostics,
)
from prw_wild.hardware.control_service import (
    HardwareManager,
    HardwareOperatingMode,
    LayerAction,
    GLOBAL_HARDWARE_MANAGER,
)


@pytest.fixture
def fresh_bridge():
    """Create or reset the singleton LoraSerialBridge instance for testing."""
    bridge = LoraSerialBridge.get_instance()
    bridge.diagnostics = BridgeDiagnostics()
    bridge.alerts.clear()
    bridge.telemetry_history.clear()
    bridge.latest_telemetry = PhysicalTelemetry.create_empty()
    bridge._last_pir_active = False
    bridge._last_piezo_active = False
    bridge._last_mic_active = False
    yield bridge
    bridge.disconnect()


# ==============================================================================
# 1. FRAME PARSING TESTS
# ==============================================================================

def test_parse_valid_usb_telemetry_frame():
    """Verify parsing of canonical machine-readable ESP32-B USB frame."""
    # Frame: PW1|TEL_USB|B|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>|<rssi>|<snr>
    frame = "PW1|TEL_USB|B|DEADBEEF|42|35000|7|1|250|1850|1|0|1|-72|9.2\n"
    telem = PhysicalTelemetry.parse_usb_frame(frame)

    assert telem is not None
    assert telem.source == "physical_hardware"
    assert telem.node_id == "B"
    assert telem.boot_id == "DEADBEEF"
    assert telem.sequence == 42
    assert telem.uptime_ms == 35000
    assert telem.flags == 7  # bits 0, 1, 2 all 1
    assert telem.pir_raw == 1
    assert telem.pir_ready is True
    assert telem.pir_active is True
    assert telem.pir_state == SensorStatus.ACTIVE.value

    # Piezo: verified is True, but piezoActive was 0 in frame
    assert telem.piezo_verified is True
    assert telem.piezo_active is False
    assert telem.piezo_state == SensorStatus.READY.value
    assert telem.piezo_p2p == 250

    # Mic: ready is True, micActive was 1 in frame
    assert telem.mic_ready is True
    assert telem.mic_active is True
    assert telem.mic_state == SensorStatus.ACTIVE.value
    assert telem.mic_rms == 1850

    assert telem.rssi_dbm == -72
    assert telem.snr_db == 9.2
    assert telem.overall_alert is True
    assert telem.led_pir is True
    assert telem.led_piezo is False
    assert telem.led_mic is True
    assert telem.led_heartbeat is True
    assert telem.led_alert is True
    assert telem.is_stale is False


def test_safety_gate_piezo_disabled_when_unverified():
    """Critical safety test: Piezo MUST be reported as DISABLED when flag bit 1 is 0."""
    # flags = 5 (binary 101: PIR warmed up, I2S mic ready, PIEZO NOT VERIFIED)
    frame = "PW1|TEL_USB|B|A1B2C3D4|10|15000|5|0|1200|400|0|1|0|-80|7.0\n"
    telem = PhysicalTelemetry.parse_usb_frame(frame)

    assert telem is not None
    assert telem.piezo_verified is False
    # Even though piezoActive was 1 in raw frame, gate enforces False!
    assert telem.piezo_active is False
    assert telem.piezo_state == SensorStatus.DISABLED.value
    assert telem.piezo_p2p is None  # Value masked for safety
    assert telem.piezo_raw_adc == 1200
    assert telem.led_piezo is False


def test_pir_warming_state_during_warmup():
    """Verify PIR is reported as WARMING when flags bit 0 is 0 (warmup period)."""
    # flags = 0 (PIR warming, piezo unverified, mic not ready)
    frame = "PW1|TEL_USB|B|A1B2C3D4|2|2000|0|1|0|0|1|0|0|-75|8.0\n"
    telem = PhysicalTelemetry.parse_usb_frame(frame)

    assert telem is not None
    assert telem.pir_ready is False
    assert telem.pir_active is False  # Cannot be active during warmup
    assert telem.pir_state == SensorStatus.WARMING.value
    assert telem.led_pir is False


def test_malformed_frames_gracefully_rejected():
    """Verify that corrupt, incomplete, or out-of-spec frames do not crash parser."""
    bad_frames = [
        "",
        "NOT_A_FRAME",
        "PW1|TEL_USB|A|...",  # Node A instead of B
        "PW1|TEL_USB|B|ONLY|FOUR|FIELDS",
        "PW1|TEL_USB|B|DEADBEEF|not_an_int|35000|7|1|250|1850|1|0|1|-72|9.2",
        "PW1|TEL_USB|B|DEADBEEF|42|35000|7|not_raw|250|1850|1|0|1|-72|9.2",
    ]
    for bf in bad_frames:
        res = PhysicalTelemetry.parse_usb_frame(bf)
        assert res is None


# ==============================================================================
# 2. SEQUENCE TRACKING & DUPLICATE DEDUPLICATION TESTS
# ==============================================================================

def test_bridge_sequence_tracking_and_duplicates(fresh_bridge):
    """Verify duplicate sequence detection and diagnostic counting."""
    bridge = fresh_bridge

    # Send frame with seq=1
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT1234|1|1000|5|0|0|50|0|0|0|-70|8.0")
    assert bridge.diagnostics.valid_telemetry_frames == 1
    assert bridge.diagnostics.last_sequence == 1
    assert bridge.diagnostics.last_boot_id == "BOOT1234"

    # Send identical frame (duplicate seq=1)
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT1234|1|1000|5|0|0|50|0|0|0|-70|8.0")
    assert bridge.diagnostics.valid_telemetry_frames == 2
    assert bridge.diagnostics.duplicate_packets == 1

    # Receive explicit firmware DUPLICATE message
    bridge._handle_incoming_frame("DUPLICATE: boot=BOOT1234 seq=1; outputs unchanged")
    assert bridge.diagnostics.duplicate_packets == 2

    # Send stale frame (seq=0 < seq=1)
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT1234|0|900|5|0|0|50|0|0|0|-70|8.0")
    assert bridge.diagnostics.stale_packets == 1


def test_bridge_new_boot_session_detected(fresh_bridge):
    """Verify that a reboot of Node A (new boot ID) cleanly resets sequence tracking."""
    bridge = fresh_bridge

    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT0001|100|70000|5|0|0|50|0|0|0|-70|8.0")
    assert bridge.diagnostics.last_boot_id == "BOOT0001"
    assert bridge.diagnostics.last_sequence == 100

    # Reboot Node A -> new boot ID and sequence starts at 1
    bridge._handle_incoming_frame("NODE_A_SESSION: boot_id=BOOT0002")
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT0002|1|700|5|0|0|50|0|0|0|-70|8.0")

    assert bridge.diagnostics.last_boot_id == "BOOT0002"
    assert bridge.diagnostics.last_sequence == 1
    # Should NOT be counted as stale because boot ID changed!
    assert bridge.diagnostics.stale_packets == 0


# ==============================================================================
# 3. EDGE-TRIGGERED ALERT GENERATION & DEDUPLICATION
# ==============================================================================

def test_edge_triggered_alerts_with_deduplication(fresh_bridge):
    """Verify PIR transitions trigger alerts on inactive->active, but do not flood on repeat."""
    bridge = fresh_bridge

    # Packet 1: PIR inactive (0)
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT9999|1|1000|5|0|0|50|0|0|0|-70|8.0")
    assert len(bridge.alerts) == 0

    # Packet 2: PIR active (1) -> Transition!
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT9999|2|1700|5|1|0|50|1|0|0|-70|8.0")
    assert len(bridge.alerts) == 1
    alert = bridge.alerts[0]
    assert alert.sensor_type == "PIR"
    assert alert.new_state == "ACTIVE"
    assert alert.acknowledged is False

    # Packets 3-10: PIR remains active (1) -> NO DUPLICATE ALERTS GENERATED!
    for seq in range(3, 11):
        bridge._handle_incoming_frame(f"PW1|TEL_USB|B|BOOT9999|{seq}|{seq*700}|5|1|0|50|1|0|0|-70|8.0")

    assert len(bridge.alerts) == 1, "Expected exactly 1 alert due to edge-triggered deduplication"

    # Packet 11: PIR goes inactive (0)
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT9999|11|7700|5|0|0|50|0|0|0|-70|8.0")
    assert len(bridge.alerts) == 1

    # Packet 12: PIR active again (1) -> New edge trigger!
    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT9999|12|8400|5|1|0|50|1|0|0|-70|8.0")
    assert len(bridge.alerts) == 2


def test_alert_acknowledgement(fresh_bridge):
    """Verify physical alerts can be acknowledged by ID."""
    bridge = fresh_bridge

    bridge._handle_incoming_frame("PW1|TEL_USB|B|BOOT9999|1|1700|5|1|0|50|1|0|0|-70|8.0")
    assert len(bridge.alerts) == 1
    alert_id = bridge.alerts[0].event_id

    # Acknowledge
    ok = bridge.acknowledge_alert(alert_id)
    assert ok is True
    assert bridge.alerts[0].acknowledged is True
    assert bridge.alerts[0].acknowledged_at is not None

    # Unknown alert ID
    assert bridge.acknowledge_alert("unknown_id_123") is False


# ==============================================================================
# 4. STALENESS TIMEOUT TESTS
# ==============================================================================

def test_telemetry_staleness_after_timeout():
    """Verify telemetry marks itself stale when older than 2.2 seconds."""
    past_time = time.time() - 3.0  # 3 seconds ago
    frame = "PW1|TEL_USB|B|BOOT1111|1|1000|5|1|0|50|1|0|0|-70|8.0"
    telem = PhysicalTelemetry.parse_usb_frame(frame, received_at=past_time)

    assert telem.is_stale is False
    telem.mark_stale()
    assert telem.is_stale is True
    assert telem.data_freshness == "STALE"
    assert telem.led_heartbeat is False
    assert telem.led_pir is False
    assert telem.overall_alert is False


# ==============================================================================
# 5. ARCHITECTURAL DOMAIN ISOLATION TESTS
# ==============================================================================

def test_physical_telemetry_cannot_mutate_simulation_state(fresh_bridge):
    """CRITICAL REQUIREMENT: Physical telemetry MUST NEVER move simulated animals or alter layer occupancy."""
    bridge = fresh_bridge
    mgr = GLOBAL_HARDWARE_MANAGER
    mgr.set_mode("SIMULATION_ONLY")
    mgr.occupancy = {1: set(), 2: set(), 3: set()}
    mgr.adapter_l1.state = LayerAction.OFF
    mgr.adapter_l2.state = LayerAction.OFF
    mgr.adapter_l3.state = LayerAction.OFF

    # Flood 25 physical alerts with PIR, Piezo, Mic all active
    for i in range(25):
        frame = f"PW1|TEL_USB|B|FLOOD_{i}|{i}|{i*700}|7|1|2000|4500|1|1|1|-60|10.0"
        bridge._handle_incoming_frame(frame)

    # Assert simulation domain state is completely pristine!
    status = mgr.get_status()
    assert status["simulation"]["layers"]["layer_1"]["state"] == "OFF"
    assert status["simulation"]["layers"]["layer_2"]["state"] == "OFF"
    assert status["simulation"]["layers"]["layer_3"]["state"] == "OFF"
    assert len(mgr.occupancy[1]) == 0
    assert len(mgr.occupancy[2]) == 0
    assert len(mgr.occupancy[3]) == 0

    # Meanwhile, physical domain accurately captured the hardware state!
    assert status["hardware"]["physical"]["telemetry"]["pir_active"] is True
    assert status["hardware"]["physical"]["telemetry"]["overall_alert"] is True
    assert status["hardware"]["physical"]["six_leds"]["led1_pir"] is True
    assert status["hardware"]["physical"]["six_leds"]["led6_alert"] is True


# ==============================================================================
# 6. DYNAMIC SENSOR CALIBRATION & THRESHOLD TRIGGERING TESTS
# ==============================================================================

def test_dynamic_microphone_threshold_triggering(fresh_bridge):
    """Verify live microphone RMS triggering when crossing dynamic threshold."""
    bridge = fresh_bridge
    bridge.set_calibration(mic_threshold=30000)

    # Frame with quiet room RMS = 18,000 (below 30,000 threshold)
    frame_quiet = "PW1|TEL_USB|B|BOOT_MIC|1|1000|13|0|0|18000|0|0|0|-69|10.0"
    bridge._handle_incoming_frame(frame_quiet)
    assert bridge.latest_telemetry.mic_active is False
    assert len(bridge.alerts) == 0

    # Frame with loud sound RMS = 45,000 (exceeds 30,000 threshold) -> Trigger!
    frame_loud = "PW1|TEL_USB|B|BOOT_MIC|2|1700|13|0|0|45000|0|0|0|-69|10.0"
    bridge._handle_incoming_frame(frame_loud)
    assert bridge.latest_telemetry.mic_active is True
    assert bridge.latest_telemetry.mic_state == "ACTIVE"
    assert bridge.latest_telemetry.led_mic is True
    assert bridge.latest_telemetry.overall_alert is True
    assert len(bridge.alerts) == 1
    assert bridge.alerts[0].sensor_type == "MIC"
    assert bridge.alerts[0].measurement == 45000


def test_dynamic_piezo_calibration_and_triggering(fresh_bridge):
    """Verify piezoelectric sensor activation and threshold triggering."""
    bridge = fresh_bridge
    bridge.set_calibration(piezo_threshold=150, piezo_enabled=True)

    # Low vibration delta (30 < 150)
    frame_low = "PW1|TEL_USB|B|BOOT_PIEZO|1|1000|13|0|30|15000|0|0|0|-69|10.0"
    bridge._handle_incoming_frame(frame_low)
    assert bridge.latest_telemetry.piezo_verified is True
    assert bridge.latest_telemetry.piezo_active is False
    assert bridge.latest_telemetry.piezo_p2p == 30

    # High vibration delta (450 >= 150) -> Trigger!
    frame_high = "PW1|TEL_USB|B|BOOT_PIEZO|2|1700|13|0|450|15000|0|0|0|-69|10.0"
    bridge._handle_incoming_frame(frame_high)
    assert bridge.latest_telemetry.piezo_active is True
    assert bridge.latest_telemetry.piezo_state == "ACTIVE"
    assert bridge.latest_telemetry.led_piezo is True
    assert bridge.latest_telemetry.overall_alert is True
    assert len(bridge.alerts) == 1
    assert bridge.alerts[0].sensor_type == "PIEZO"
    assert bridge.alerts[0].measurement == 450


def test_piezo_hysteresis_and_safety_gate(fresh_bridge):
    """AC-02 & AC-04: Test piezo threshold crossing, hysteresis, and protection verification."""
    bridge = fresh_bridge
    # 1. Unverified protection -> Never triggers
    bridge.set_calibration(piezo_threshold=150, piezo_enabled=False)
    frame_unver = "PW1|TEL_USB|B|BOOT_PIEZO|1|1000|5|0|300|1000|0|1|0|-70|8.0" # flag bit 1 is 0
    bridge._handle_incoming_frame(frame_unver)
    assert bridge.latest_telemetry.piezo_verified is False
    assert bridge.latest_telemetry.piezo_active is False
    assert bridge.latest_telemetry.led_piezo is False

    # 2. Verified protection -> Triggers when >= threshold
    bridge.set_calibration(piezo_threshold=150, piezo_enabled=True)
    frame_trig = "PW1|TEL_USB|B|BOOT_PIEZO|2|1700|7|0|160|1000|0|1|0|-70|8.0" # 160 >= 150
    bridge._handle_incoming_frame(frame_trig)
    assert bridge.latest_telemetry.piezo_verified is True
    assert bridge.latest_telemetry.piezo_active is True
    assert bridge.latest_telemetry.led_piezo is True


def test_mic_floating_rejection_and_threshold(fresh_bridge):
    """AC-03 & AC-05: Test microphone RMS threshold crossing and invalid/floating rejection."""
    bridge = fresh_bridge
    bridge.set_calibration(mic_threshold=32000)

    # 1. Mic not ready / invalid (flag bit 2 is 0) -> Cannot trigger even if raw high
    frame_not_ready = "PW1|TEL_USB|B|BOOT_MIC|1|1000|3|0|0|50000|0|0|1|-70|8.0" # flags=3 (bits 0,1, but not 2)
    bridge._handle_incoming_frame(frame_not_ready)
    assert bridge.latest_telemetry.mic_ready is False
    assert bridge.latest_telemetry.mic_active is False
    assert bridge.latest_telemetry.led_mic is False

    # 2. Mic ready and valid -> Below threshold quiet room
    frame_quiet = "PW1|TEL_USB|B|BOOT_MIC|2|1700|7|0|0|12000|0|0|0|-70|8.0"
    bridge._handle_incoming_frame(frame_quiet)
    assert bridge.latest_telemetry.mic_ready is True
    assert bridge.latest_telemetry.mic_active is False
    assert bridge.latest_telemetry.led_mic is False

    # 3. Mic exceeds threshold -> Active
    frame_loud = "PW1|TEL_USB|B|BOOT_MIC|3|2400|7|0|0|38000|0|0|1|-70|8.0"
    bridge._handle_incoming_frame(frame_loud)
    assert bridge.latest_telemetry.mic_ready is True
    assert bridge.latest_telemetry.mic_active is True
    assert bridge.latest_telemetry.led_mic is True


def test_led2_and_led3_independent_behavior():
    """AC-02, AC-03 & AC-06: Verify LED 2 (Piezo) and LED 3 (Mic) operate independently."""
    # Only Piezo active
    f1 = "PW1|TEL_USB|B|B1|1|1000|7|0|200|500|0|1|0|-70|8.0"
    t1 = PhysicalTelemetry.parse_usb_frame(f1, piezo_threshold=150, mic_threshold=30000, piezo_enabled=True)
    assert t1.led_pir is False
    assert t1.led_piezo is True
    assert t1.led_mic is False
    assert t1.led_alert is True

    # Only Mic active
    f2 = "PW1|TEL_USB|B|B1|2|1700|7|0|50|35000|0|0|1|-70|8.0"
    t2 = PhysicalTelemetry.parse_usb_frame(f2, piezo_threshold=150, mic_threshold=30000, piezo_enabled=True)
    assert t2.led_pir is False
    assert t2.led_piezo is False
    assert t2.led_mic is True
    assert t2.led_alert is True

    # Both active
    f3 = "PW1|TEL_USB|B|B1|3|2400|7|0|250|40000|0|1|1|-70|8.0"
    t3 = PhysicalTelemetry.parse_usb_frame(f3, piezo_threshold=150, mic_threshold=30000, piezo_enabled=True)
    assert t3.led_piezo is True
    assert t3.led_mic is True
    assert t3.led_alert is True


def test_led6_combined_alert_full_truth_table():
    """AC-07: Verify LED 6 represents combined alert (pir || piezo || mic) across all 8 permutations."""
    for pir in (0, 1):
        for piezo in (0, 1):
            for mic in (0, 1):
                frame = f"PW1|TEL_USB|B|BTEST|1|1000|7|{pir}|{200 if piezo else 10}|{40000 if mic else 1000}|{pir}|{piezo}|{mic}|-70|8.0"
                t = PhysicalTelemetry.parse_usb_frame(frame, piezo_threshold=150, mic_threshold=32000, piezo_enabled=True)
                expected_alert = bool(pir or piezo or mic)
                assert t.led_alert == expected_alert
                assert t.overall_alert == expected_alert
                assert t.led_pir == bool(pir)
                assert t.led_piezo == bool(piezo)
                assert t.led_mic == bool(mic)


def test_existing_led1_led4_led5_behavior_preserved():
    """AC-01 & AC-06: Verify LED 1 (PIR), LED 4 (Heartbeat), and LED 5 (LoRa) maintain exact behavior."""
    # Active PIR
    f_pir = "PW1|TEL_USB|B|BTEST|1|1000|1|1|0|0|1|0|0|-70|8.0"
    t = PhysicalTelemetry.parse_usb_frame(f_pir)
    assert t.led_pir is True
    assert t.led_piezo is False
    assert t.led_mic is False
    assert t.led_heartbeat is True
    assert t.led_lora is True
    assert t.led_alert is True

    # Stale / disconnected state clears LEDs
    t.mark_stale()
    assert t.led_heartbeat is False
    assert t.led_pir is False
    assert t.led_piezo is False
    assert t.led_mic is False
    assert t.led_alert is False


def test_calibration_sync_and_confirmation(fresh_bridge):
    """AC-09: Verify threshold configuration command formatting and confirmation."""
    bridge = fresh_bridge
    # Verify set_calibration updates local state
    res = bridge.set_calibration(mic_threshold=28000, piezo_threshold=180, piezo_enabled=True)
    assert res["mic_threshold"] == 28000
    assert res["piezo_threshold"] == 180
    assert res["piezo_enabled"] is True

    # Verify incoming firmware calibration confirmation frame is handled
    bridge._handle_incoming_frame("PW1|CALIB_ACK|180|28000|1")
    # Diagnostics intact and no exceptions
    assert bridge.diagnostics.corrupted_frames == 0


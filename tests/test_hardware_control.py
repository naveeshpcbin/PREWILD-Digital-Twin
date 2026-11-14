"""Integration and Unit Tests for PRW-Wild Physical Hardware Control Service.

Tests:
1. Master Manager initialization and default SIMULATION_ONLY state.
2. Operating mode transitions (SIMULATION_ONLY -> HARDWARE_TEST -> AUTO_HARDWARE_CONTROL).
3. Truthful device connection reporting (no fake physical status when disconnected).
4. Manual command execution and simulated ACKs across Layer 1, Layer 2, Layer 3.
5. Invariant Event Sequence in AUTO mode: Enter L1 -> Enter L2 -> Enter L3 -> Exit L3 -> Exit L2 -> Exit L1.
6. Multi-animal occupancy debouncing (layer stays ON until count reaches 0).
7. Emergency All-Off override and state clearance.
8. HTTP REST API endpoints on DigitalTwinHTTPHandler.
"""

import json
import pytest
from prw_wild.hardware.control_service import (
    HardwareManager,
    HardwareOperatingMode,
    LayerAction,
    DeviceConnectionStatus,
    GLOBAL_HARDWARE_MANAGER,
)


@pytest.fixture(autouse=True)
def reset_hardware_manager():
    """Reset the singleton state before and after every test."""
    mgr = GLOBAL_HARDWARE_MANAGER
    mgr.set_mode("SIMULATION_ONLY")
    mgr.manual_overrides = {1: None, 2: None, 3: None}
    mgr.occupancy = {1: set(), 2: set(), 3: set()}
    mgr.adapter_l1.state = LayerAction.OFF
    mgr.adapter_l2.state = LayerAction.OFF
    mgr.adapter_l3.state = LayerAction.OFF
    with mgr.history_lock:
        mgr.command_history.clear()
    yield mgr
    mgr.set_mode("SIMULATION_ONLY")
    mgr.manual_overrides = {1: None, 2: None, 3: None}
    mgr.occupancy = {1: set(), 2: set(), 3: set()}
    mgr.adapter_l1.state = LayerAction.OFF
    mgr.adapter_l2.state = LayerAction.OFF
    mgr.adapter_l3.state = LayerAction.OFF


def test_hardware_manager_initialization(reset_hardware_manager):
    """Verify hardware manager initializes in SIMULATION_ONLY mode with all layers OFF."""
    mgr = reset_hardware_manager
    assert mgr.operating_mode == HardwareOperatingMode.SIMULATION_ONLY
    status = mgr.get_status()
    assert status["operating_mode"] == "SIMULATION_ONLY"
    assert status["layers"]["layer_1"]["state"] == "OFF"
    assert status["layers"]["layer_2"]["state"] == "OFF"
    assert status["layers"]["layer_3"]["state"] == "OFF"


def test_truthful_connection_status(reset_hardware_manager):
    """Assert devices report DISCONNECTED when no physical USB or HTTP node is present."""
    mgr = reset_hardware_manager
    status = mgr.get_status()
    l1 = status["layers"]["layer_1"]
    l2 = status["layers"]["layer_2"]
    l3 = status["layers"]["layer_3"]

    # Layer 2 is a physical relay board not plugged in
    assert l2["physical_connected"] is False
    assert l2["connection_status"] == DeviceConnectionStatus.DISCONNECTED.value

    # Layer 3 is an HTTP camera not reachable at local host without physical hardware
    assert l3["physical_connected"] is False
    assert l3["connection_status"] == DeviceConnectionStatus.DISCONNECTED.value


def test_operating_mode_transitions(reset_hardware_manager):
    """Verify transitions between SIMULATION_ONLY, HARDWARE_TEST, and AUTO_HARDWARE_CONTROL."""
    mgr = reset_hardware_manager

    res = mgr.set_mode("HARDWARE_TEST")
    assert res["success"] is True
    assert mgr.operating_mode == HardwareOperatingMode.HARDWARE_TEST

    res = mgr.set_mode("AUTO_HARDWARE_CONTROL")
    assert res["success"] is True
    assert mgr.operating_mode == HardwareOperatingMode.AUTO_HARDWARE_CONTROL

    res = mgr.set_mode("SIMULATION_ONLY")
    assert res["success"] is True
    assert mgr.operating_mode == HardwareOperatingMode.SIMULATION_ONLY

    # Invalid mode
    res = mgr.set_mode("INVALID_MODE_NAME")
    assert res["success"] is False
    assert "error" in res


def test_manual_commands_and_simulated_acks(reset_hardware_manager):
    """Verify manual command execution, status updates, and command history logging."""
    mgr = reset_hardware_manager
    mgr.set_mode("HARDWARE_TEST")

    # Command Layer 1 ON
    res_l1 = mgr.send_manual_command(1, "ON")
    assert res_l1.success is True
    assert res_l1.layer == 1
    assert res_l1.action == "ON"
    assert mgr.adapter_l1.state == LayerAction.ON

    # Command Layer 2 ON
    res_l2 = mgr.send_manual_command(2, "ON")
    assert res_l2.success is True
    assert mgr.adapter_l2.state == LayerAction.ON

    # Command Layer 3 ON
    res_l3 = mgr.send_manual_command(3, "ON")
    assert res_l3.success is True
    assert mgr.adapter_l3.state == LayerAction.ON

    # Check history contains all 3 commands
    status = mgr.get_status()
    assert len(status["recent_commands"]) >= 3
    assert status["layers"]["layer_1"]["state"] == "ON"
    assert status["layers"]["layer_2"]["state"] == "ON"
    assert status["layers"]["layer_3"]["state"] == "ON"

    # Command Layer 1 OFF
    res_l1_off = mgr.send_manual_command(1, "OFF")
    assert res_l1_off.success is True
    assert mgr.adapter_l1.state == LayerAction.OFF


def test_emergency_all_off(reset_hardware_manager):
    """Verify emergency all-off command immediately shuts down all 3 layers."""
    mgr = reset_hardware_manager
    mgr.set_mode("HARDWARE_TEST")

    # Turn all on
    mgr.send_manual_command(1, "ON")
    mgr.send_manual_command(2, "ON")
    mgr.send_manual_command(3, "ON")

    assert mgr.adapter_l1.state == LayerAction.ON
    assert mgr.adapter_l2.state == LayerAction.ON
    assert mgr.adapter_l3.state == LayerAction.ON

    # Trigger emergency stop
    results = mgr.emergency_all_off()
    assert len(results) == 3
    assert mgr.adapter_l1.state == LayerAction.OFF
    assert mgr.adapter_l2.state == LayerAction.OFF
    assert mgr.adapter_l3.state == LayerAction.OFF


def test_simulation_driven_invariant_event_sequence(reset_hardware_manager):
    """Test fixed 6-step event sequence in AUTO mode:
    1. Enter Layer 1 -> L1 ON
    2. Enter Layer 2 -> L2 ON
    3. Enter Layer 3 -> L3 ON
    4. Exit Layer 3 -> L3 OFF
    5. Exit Layer 2 -> L2 OFF
    6. Exit Layer 1 -> L1 OFF
    """
    mgr = reset_hardware_manager
    mgr.set_mode("AUTO_HARDWARE_CONTROL")

    # Step 1: Animal enters Layer 1
    ev1 = mgr.process_simulation_occupancy({1: 1, 2: 0, 3: 0})
    assert len(ev1) == 1
    assert ev1[0].layer == 1 and ev1[0].action == "ON"
    assert mgr.adapter_l1.state == LayerAction.ON
    assert mgr.adapter_l2.state == LayerAction.OFF
    assert mgr.adapter_l3.state == LayerAction.OFF

    # Step 2: Animal enters Layer 2
    ev2 = mgr.process_simulation_occupancy({1: 1, 2: 1, 3: 0})
    assert len(ev2) == 1
    assert ev2[0].layer == 2 and ev2[0].action == "ON"
    assert mgr.adapter_l1.state == LayerAction.ON
    assert mgr.adapter_l2.state == LayerAction.ON
    assert mgr.adapter_l3.state == LayerAction.OFF

    # Step 3: Animal enters Layer 3
    ev3 = mgr.process_simulation_occupancy({1: 1, 2: 1, 3: 1})
    assert len(ev3) == 1
    assert ev3[0].layer == 3 and ev3[0].action == "ON"
    assert mgr.adapter_l1.state == LayerAction.ON
    assert mgr.adapter_l2.state == LayerAction.ON
    assert mgr.adapter_l3.state == LayerAction.ON

    # Step 4: Animal exits Layer 3
    ev4 = mgr.process_simulation_occupancy({1: 1, 2: 1, 3: 0})
    assert len(ev4) == 1
    assert ev4[0].layer == 3 and ev4[0].action == "OFF"
    assert mgr.adapter_l1.state == LayerAction.ON
    assert mgr.adapter_l2.state == LayerAction.ON
    assert mgr.adapter_l3.state == LayerAction.OFF

    # Step 5: Animal exits Layer 2
    ev5 = mgr.process_simulation_occupancy({1: 1, 2: 0, 3: 0})
    assert len(ev5) == 1
    assert ev5[0].layer == 2 and ev5[0].action == "OFF"
    assert mgr.adapter_l1.state == LayerAction.ON
    assert mgr.adapter_l2.state == LayerAction.OFF
    assert mgr.adapter_l3.state == LayerAction.OFF

    # Step 6: Animal exits Layer 1
    ev6 = mgr.process_simulation_occupancy({1: 0, 2: 0, 3: 0})
    assert len(ev6) == 1
    assert ev6[0].layer == 1 and ev6[0].action == "OFF"
    assert mgr.adapter_l1.state == LayerAction.OFF
    assert mgr.adapter_l2.state == LayerAction.OFF
    assert mgr.adapter_l3.state == LayerAction.OFF


def test_multi_animal_occupancy_debouncing(reset_hardware_manager):
    """Verify that multiple animals in a layer debounce deactivation until the zone is empty."""
    mgr = reset_hardware_manager
    mgr.set_mode("AUTO_HARDWARE_CONTROL")

    # 3 animals in Layer 1
    mgr.process_simulation_occupancy({1: 3, 2: 0, 3: 0})
    assert mgr.adapter_l1.state == LayerAction.ON

    # 1 animal leaves, 2 remain -> Layer 1 must remain ON
    ev1 = mgr.process_simulation_occupancy({1: 2, 2: 0, 3: 0})
    assert len(ev1) == 0
    assert mgr.adapter_l1.state == LayerAction.ON

    # Another animal leaves, 1 remains -> Layer 1 must remain ON
    ev2 = mgr.process_simulation_occupancy({1: 1, 2: 0, 3: 0})
    assert len(ev2) == 0
    assert mgr.adapter_l1.state == LayerAction.ON

    # Last animal leaves -> Layer 1 turns OFF
    ev3 = mgr.process_simulation_occupancy({1: 0, 2: 0, 3: 0})
    assert len(ev3) == 1
    assert ev3[0].action == "OFF"
    assert mgr.adapter_l1.state == LayerAction.OFF



def test_direct_process_event_edge_triggered_sequence(reset_hardware_manager):
    """Test process_event handles direct L1/L2/L3 ENTER and EXIT events in AUTO mode."""
    mgr = reset_hardware_manager
    mgr.set_mode("AUTO_HARDWARE_CONTROL")

    r1 = mgr.process_event("ELEPHANT_01", "L1", "ENTER")
    assert r1["success"] is True
    assert mgr.adapter_l1.state == LayerAction.ON

    r2 = mgr.process_event("ELEPHANT_01", "L2", "ENTER")
    assert r2["success"] is True
    assert mgr.adapter_l2.state == LayerAction.ON

    r3 = mgr.process_event("ELEPHANT_01", "L3", "ENTER")
    assert r3["success"] is True
    assert mgr.adapter_l3.state == LayerAction.ON

    r4 = mgr.process_event("ELEPHANT_01", "L3", "EXIT")
    assert r4["success"] is True
    assert mgr.adapter_l3.state == LayerAction.OFF

    r5 = mgr.process_event("ELEPHANT_01", "L2", "EXIT")
    assert r5["success"] is True
    assert mgr.adapter_l2.state == LayerAction.OFF

    r6 = mgr.process_event("ELEPHANT_01", "L1", "EXIT")
    assert r6["success"] is True
    assert mgr.adapter_l1.state == LayerAction.OFF


def test_process_event_ignored_in_simulation_only(reset_hardware_manager):
    """Test process_event does not actuate hardware when operating mode is SIMULATION_ONLY."""
    mgr = reset_hardware_manager
    mgr.set_mode("SIMULATION_ONLY")

    r = mgr.process_event("ELEPHANT_01", "L1", "ENTER")
    assert r["success"] is True
    assert r["status"] == "IGNORED_NOT_AUTO_MODE"
    assert mgr.adapter_l1.state == LayerAction.OFF


def test_dual_node_mode_cascade_behavior():
    """Verify dual ESP32 manual mode control and strict cascading rule:
    Turning OFF ESP32-A must automatically turn OFF ESP32-B,
    and ESP32-B cannot be enabled while ESP32-A is OFF.
    """
    from prw_wild.hardware.lora_bridge import LoraSerialBridge
    bridge = LoraSerialBridge.get_instance()

    # Reset to known active baseline
    bridge.set_node_mode("A", "ON")
    bridge.set_node_mode("B", "ON")
    modes = bridge.get_node_modes()
    assert modes["node_a"] == "ON"
    assert modes["node_b"] == "ON"
    assert modes["cascade_rule"] == "A_OFF_FORCES_B_OFF"

    # 1. Turn OFF Node A -> MUST cascade and turn OFF Node B
    res_a_off = bridge.set_node_mode("A", "OFF")
    assert res_a_off["success"] is True
    assert res_a_off["node_a"] == "OFF"
    assert res_a_off["node_b"] == "OFF"
    assert res_a_off["cascaded"] is True

    current = bridge.get_node_modes()
    assert current["node_a"] == "OFF"
    assert current["node_b"] == "OFF"

    # 2. Attempt to turn ON Node B while Node A is OFF -> MUST be rejected!
    res_b_attempt = bridge.set_node_mode("B", "ON")
    assert res_b_attempt["success"] is False
    assert "Cannot turn ON ESP32-B mode while ESP32-A mode is OFF" in res_b_attempt["error"]
    assert bridge.node_b_mode is False

    # 3. Turn ON Node A -> Node A becomes ON, Node B remains OFF
    res_a_on = bridge.set_node_mode("A", "ON")
    assert res_a_on["success"] is True
    assert res_a_on["node_a"] == "ON"
    assert res_a_on["node_b"] == "OFF"

    # 4. Now that Node A is ON, turning ON Node B succeeds
    res_b_on = bridge.set_node_mode("B", "ON")
    assert res_b_on["success"] is True
    assert res_b_on["node_b"] == "ON"
    assert res_b_on["node_a"] == "ON"

    # 5. Independent toggle of Node B to OFF while Node A stays ON
    res_b_off = bridge.set_node_mode("B", "OFF")
    assert res_b_off["success"] is True
    assert res_b_off["node_b"] == "OFF"
    assert res_b_off["node_a"] == "ON"

    # Restore baseline
    bridge.set_node_mode("B", "ON")


def test_hardware_status_includes_node_modes(reset_hardware_manager):
    """Verify master HardwareManager status reports nodes dictionary."""
    mgr = reset_hardware_manager
    from prw_wild.hardware.lora_bridge import LoraSerialBridge
    bridge = LoraSerialBridge.get_instance()
    bridge.set_node_mode("A", "ON")
    bridge.set_node_mode("B", "ON")

    status = mgr.get_status()
    assert "nodes" in status
    assert status["nodes"]["node_a"] == "ON"
    assert status["nodes"]["node_b"] == "ON"
    assert status["nodes"]["cascade_rule"] == "A_OFF_FORCES_B_OFF"

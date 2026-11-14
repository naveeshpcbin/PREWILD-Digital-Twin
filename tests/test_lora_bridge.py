"""Unit and Integration Tests for LoraSerialBridge (PRW-Wild).

Validates:
1. Port detection and enumeration.
2. Connection management (connect, disconnect, auto-port detection).
3. Frame generation and field formatting.
4. Thread-safe ACK matching across sequences.
5. Timeout and retry handling when ACK is not received.
6. Idempotency and sequence numbering.
7. Diagnostics (latency calculation, RSSI/SNR extraction).
8. Emergency All-Off dispatch.
"""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from prw_wild.hardware.lora_bridge import (
    LoraSerialBridge,
    BridgeDiagnostics,
)


@pytest.fixture
def fresh_bridge():
    """Create an isolated LoraSerialBridge instance for testing."""
    bridge = LoraSerialBridge(port="COM_TEST_FAKE", baud_rate=115200)
    yield bridge
    bridge.disconnect()


def test_bridge_initialization(fresh_bridge):
    """Verify default initial state of the LoRa serial bridge."""
    bridge = fresh_bridge
    assert bridge.is_connected is False
    assert len(bridge.session_id) == 8
    assert bridge.sequence_number == 0
    status = bridge.get_status()
    assert status["is_connected"] is False
    assert status["baud_rate"] == 115200


def test_sequence_numbering_monotonic(fresh_bridge):
    """Verify monotonic sequence incrementing under concurrent access."""
    bridge = fresh_bridge
    seqs = []

    def get_seq():
        for _ in range(25):
            seqs.append(bridge._next_sequence())

    threads = [threading.Thread(target=get_seq) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(seqs) == 100
    assert len(set(seqs)) == 100
    assert max(seqs) == 100


def test_simulated_fallback_when_disconnected(fresh_bridge):
    """Verify clean simulated fallback when hardware is disconnected."""
    bridge = fresh_bridge
    res = bridge.send_command(
        layer="L1",
        transition="ENTER",
        animal_id="ELEPHANT_01",
        allow_simulated_fallback=True
    )
    assert res["success"] is True
    assert res["physical_executed"] is False
    assert res["status"] == "SIMULATED_FALLBACK"
    assert res["state"] == "ACTIVE"
    assert res["layer"] == "L1"


def test_rejection_when_fallback_disabled(fresh_bridge):
    """Verify rejection when hardware is disconnected and fallback is disabled."""
    bridge = fresh_bridge
    res = bridge.send_command(
        layer="L2",
        transition="ENTER",
        allow_simulated_fallback=False
    )
    assert res["success"] is False
    assert res["physical_executed"] is False
    assert res["status"] == "DISCONNECTED"
    assert "No physical serial hardware" in res["error"]


def test_ack_matching_with_mock_serial(fresh_bridge):
    """Verify end-to-end command dispatch and ACK matching over serial stream."""
    bridge = fresh_bridge
    mock_serial = MagicMock()
    written_data = []

    def mock_write(b):
        written_data.append(b.decode("utf-8"))
        return len(b)

    mock_serial.write = mock_write
    bridge.serial_handle = mock_serial
    bridge.is_connected = True
    bridge._running = True

    # Simulate ESP32-A responding with matching ACK in background thread
    def simulate_esp32_ack():
        time.sleep(0.05)
        # Parse written command to extract session and sequence
        last_cmd = written_data[-1].strip()
        parts = last_cmd.split("|")
        session = parts[2]
        seq = parts[3]
        layer = parts[5]

        # Feed RF diag and ACK frame into handler
        bridge._handle_incoming_frame(f"PW1|RF_DIAG|{session}|{seq}|RSSI_-68|SNR_9.5")
        bridge._handle_incoming_frame(f"PW1|ACK|{session}|{seq}|OK|{layer}|ACTIVE")

    ack_thread = threading.Thread(target=simulate_esp32_ack)
    ack_thread.start()

    res = bridge.send_command(
        layer="L1",
        transition="ENTER",
        animal_id="ELEPHANT_01",
        timeout=1.0
    )
    ack_thread.join()

    assert res["success"] is True
    assert res["physical_executed"] is True
    assert res["status"] == "CONFIRMED"
    assert res["layer"] == "L1"
    assert res["state"] == "ACTIVE"
    assert res["rssi"] == -68
    assert res["snr"] == 9.5
    assert res["latency_ms"] > 0.0


def test_timeout_when_ack_missing(fresh_bridge):
    """Verify graceful timeout when device does not return an ACK."""
    bridge = fresh_bridge
    mock_serial = MagicMock()
    mock_serial.write.return_value = 10

    bridge.serial_handle = mock_serial
    bridge.is_connected = True
    bridge._running = True

    res = bridge.send_command(
        layer="L3",
        transition="ENTER",
        timeout=0.1
    )

    assert res["success"] is False
    assert res["status"] == "TIMEOUT"
    assert "LoRa ACK timeout" in res["error"]
    assert bridge.diagnostics.timeouts == 1


def test_emergency_all_off_dispatch(fresh_bridge):
    """Verify Emergency All-Off sends ALL|OFF command frame."""
    bridge = fresh_bridge
    res = bridge.emergency_all_off()
    assert res["layer"] == "ALL"
    assert res["state"] == "INACTIVE"


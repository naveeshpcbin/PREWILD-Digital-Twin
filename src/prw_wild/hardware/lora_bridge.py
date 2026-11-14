"""PRW-Wild — Unified Python USB-Serial Bridge for LoRa Transceiver (ESP32-A / ESP32-B).

Implements bidirectional communication and telemetry reception between the Python Digital Twin
backend and the physical ESP32-B gateway over USB Serial (CP2102/CH340):
- Receives machine-readable telemetry from ESP32-B:
  PW1|TEL_USB|B|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>|<rssi>|<snr>
- Edge-triggered physical sensor alert generation with deduplication
- Dispatches optional PW1 command frames: PW1|CMD|<session>|<seq>|<animal>|<layer>|<trans>
- Receives PW1 acknowledgements: PW1|ACK|<session>|<seq>|OK|<layer>|<state>
- Captures physical RF telemetry: RSSI, SNR, packet loss, duplicate packets, and round-trip latency
- Thread-safe command queue and non-blocking background reader thread
- Absolute domain isolation: physical telemetry never mutates simulated digital twin state
- Graceful fallback when physical microcontroller is disconnected
"""

from __future__ import annotations

import collections
import logging
import os
import queue
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from prw_wild.hardware.telemetry_model import (
    PhysicalTelemetry,
    PhysicalAlertEvent,
    SensorStatus,
    ConnectionState,
)

logger = logging.getLogger("prw_wild.hardware.lora_bridge")

try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False
    serial = None


@dataclass
class BridgeDiagnostics:
    total_commands: int = 0
    successful_acks: int = 0
    timeouts: int = 0
    errors: int = 0
    total_frames_received: int = 0
    valid_telemetry_frames: int = 0
    corrupted_frames: int = 0
    duplicate_packets: int = 0
    stale_packets: int = 0
    rejected_packets: int = 0
    last_rssi_dbm: Optional[int] = None
    last_snr_db: Optional[float] = None
    last_ack_time: Optional[float] = None
    last_latency_ms: Optional[float] = None
    last_packet_time: Optional[float] = None
    last_sequence: Optional[int] = None
    last_boot_id: Optional[str] = None
    latency_samples: List[float] = field(default_factory=list)

    def record_latency(self, latency_ms: float) -> None:
        self.last_latency_ms = round(latency_ms, 2)
        self.latency_samples.append(self.last_latency_ms)
        if len(self.latency_samples) > 100:
            self.latency_samples.pop(0)

    def get_latency_stats(self) -> Dict[str, Any]:
        if not self.latency_samples:
            return {"min_ms": None, "median_ms": None, "mean_ms": None, "max_ms": None, "samples": 0}
        s = sorted(self.latency_samples)
        n = len(s)
        med = s[n // 2] if n % 2 != 0 else (s[n // 2 - 1] + s[n // 2]) / 2.0
        return {
            "min_ms": round(s[0], 2),
            "median_ms": round(med, 2),
            "mean_ms": round(sum(s) / n, 2),
            "max_ms": round(s[-1], 2),
            "samples": n
        }

    def to_dict(self) -> Dict[str, Any]:
        stats = self.get_latency_stats()
        return {
            "total_commands": self.total_commands,
            "successful_acks": self.successful_acks,
            "timeouts": self.timeouts,
            "errors": self.errors,
            "total_frames_received": self.total_frames_received,
            "valid_telemetry_frames": self.valid_telemetry_frames,
            "corrupted_frames": self.corrupted_frames,
            "duplicate_packets": self.duplicate_packets,
            "stale_packets": self.stale_packets,
            "rejected_packets": self.rejected_packets,
            "last_rssi_dbm": self.last_rssi_dbm,
            "last_snr_db": self.last_snr_db,
            "last_ack_time": self.last_ack_time,
            "last_latency_ms": self.last_latency_ms,
            "last_packet_time": self.last_packet_time,
            "last_sequence": self.last_sequence,
            "last_boot_id": self.last_boot_id,
            "latency_stats": stats
        }


class LoraSerialBridge:
    """Thread-safe USB-Serial bridge connecting ESP32-B gateway and Python Digital Twin."""

    _instance: Optional["LoraSerialBridge"] = None
    _singleton_lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> "LoraSerialBridge":
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self, port: Optional[str] = None, baud_rate: int = 115200, timeout: float = 0.2):
        self.configured_port = port or os.environ.get("PRW_SERIAL_PORT", None)
        self.baud_rate = baud_rate
        self.read_timeout = timeout

        self.serial_handle: Optional[Any] = None
        self.connected_port: Optional[str] = None
        self.is_connected: bool = False
        self.last_error: Optional[str] = None

        # Session tracking
        self.session_id: str = uuid.uuid4().hex[:8].upper()
        self.sequence_number: int = 0
        self.seq_lock = threading.Lock()

        # Outstanding command synchronization
        self._pending_lock = threading.Lock()
        self._pending_acks: Dict[Tuple[str, int], Tuple[threading.Event, Dict[str, Any]]] = {}

        # Background reader thread
        self._running: bool = False
        self._reader_thread: Optional[threading.Thread] = None
        self._bridge_lock = threading.RLock()

        # Telemetry storage
        self._telemetry_lock = threading.RLock()
        self.latest_telemetry: PhysicalTelemetry = PhysicalTelemetry.create_empty()
        self.telemetry_history: collections.deque = collections.deque(maxlen=100)

        # Edge-triggered physical alerts
        self._alerts_lock = threading.RLock()
        self.alerts: collections.deque = collections.deque(maxlen=100)
        self._last_pir_active: bool = False
        self._last_piezo_active: bool = False
        self._last_mic_active: bool = False

        # Calibration & Physical Hardware Realization Profile
        # In the physical bench hardware, only PIR motion (GPIO 32), LED 4 (Heartbeat/Connect),
        # and LED 5 (LoRa RX Pulse) are physically implemented.
        # Piezoelectric vibration and INMP441 microphone sensors are NOT installed on the bench.
        self.mic_threshold: int = 0
        self.piezo_threshold: int = 0
        self.piezo_enabled: bool = False

        # Dual-Node Manual Operating Modes (ESP32-A and ESP32-B)
        # Cascading Rule: Turning OFF ESP32-A automatically turns OFF ESP32-B.
        self.node_a_mode: bool = True
        self.node_b_mode: bool = True

        # Diagnostic metrics
        self.diagnostics = BridgeDiagnostics()

    # =========================================================================
    # PORT DISCOVERY AND CONNECTION
    # =========================================================================

    def detect_ports(self) -> List[Dict[str, str]]:
        """List available serial communication ports on the host system."""
        if not HAS_PYSERIAL:
            return []
        try:
            ports = list(serial.tools.list_ports.comports())
            res = []
            for p in ports:
                desc = p.description or ""
                hwid = p.hwid or ""
                is_esp = any(k in desc.lower() or k in hwid.lower() for k in ["cp210", "ch340", "espressif", "usb serial", "uart"])
                res.append({
                    "device": p.device,
                    "description": desc,
                    "hwid": hwid,
                    "is_probable_esp32": is_esp
                })
            return res
        except Exception as e:
            logger.error(f"Error enumerating serial ports: {e}")
            return []

    def connect(self, port: Optional[str] = None) -> bool:
        """Establish connection to ESP32-B over specified or auto-detected serial port."""
        with self._bridge_lock:
            if self.is_connected and self.serial_handle:
                return True

            if not HAS_PYSERIAL:
                self.last_error = "PySerial library not installed"
                self.is_connected = False
                return False

            target_port = port or self.configured_port
            if not target_port:
                detected = self.detect_ports()
                esp_ports = [p["device"] for p in detected if p.get("is_probable_esp32")]
                if esp_ports:
                    target_port = esp_ports[0]
                elif detected:
                    target_port = detected[0]["device"]

            if not target_port:
                self.last_error = "No serial port specified or detected"
                self.is_connected = False
                self.latest_telemetry.connection_state = ConnectionState.DISCONNECTED.value
                return False

            try:
                self.serial_handle = serial.Serial(
                    port=target_port,
                    baudrate=self.baud_rate,
                    timeout=self.read_timeout,
                    write_timeout=1.0
                )
                self.connected_port = target_port
                self.is_connected = True
                self.last_error = None
                self.latest_telemetry.connection_state = ConnectionState.CONNECTED.value

                # Start background serial reader
                self._running = True
                self._reader_thread = threading.Thread(
                    target=self._serial_read_loop,
                    name="LoraBridgeReader",
                    daemon=True
                )
                self._reader_thread.start()

                logger.info(f"[PRW-Wild LoRa Bridge] Connected to ESP32-B Gateway on {target_port} @ {self.baud_rate} baud")
                return True
            except Exception as e:
                self.last_error = f"Failed to connect to {target_port}: {e}"
                self.is_connected = False
                self.serial_handle = None
                self.connected_port = None
                self.latest_telemetry.connection_state = ConnectionState.ERROR.value
                logger.warning(f"[PRW-Wild LoRa Bridge] Connection failure: {self.last_error}")
                return False

    def disconnect(self) -> None:
        """Safely close serial port and terminate background reader."""
        with self._bridge_lock:
            self._running = False
            if self.serial_handle:
                try:
                    self.serial_handle.close()
                except Exception:
                    pass
            self.serial_handle = None
            self.connected_port = None
            self.is_connected = False
            self.latest_telemetry.mark_stale()
            self.latest_telemetry.connection_state = ConnectionState.DISCONNECTED.value
            logger.info("[PRW-Wild LoRa Bridge] Disconnected")

    def reconnect(self, port: Optional[str] = None) -> bool:
        """Force a clean reconnection cycle."""
        self.disconnect()
        time.sleep(0.1)
        return self.connect(port)

    def configure_port(self, port: str, baud_rate: int = 115200) -> bool:
        """Explicitly reconfigure COM port and reconnect."""
        self.configured_port = port
        self.baud_rate = baud_rate
        return self.reconnect(port)

    # =========================================================================
    # LOW-LEVEL SERIAL READER LOOP
    # =========================================================================

    def _write_raw(self, line: str) -> bool:
        if not self.serial_handle or not self.is_connected:
            return False
        try:
            self.serial_handle.write(line.encode("utf-8"))
            self.serial_handle.flush()
            return True
        except Exception as e:
            logger.error(f"[PRW-Wild LoRa Bridge] Write error: {e}")
            self.last_error = f"Write error: {e}"
            self.disconnect()
            return False

    def _serial_read_loop(self) -> None:
        buffer = ""
        while self._running and self.serial_handle and self.is_connected:
            try:
                data = self.serial_handle.read(64)
                if data:
                    buffer += data.decode("utf-8", errors="ignore")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            self._handle_incoming_frame(line)
                else:
                    time.sleep(0.01)
            except Exception as e:
                if self._running:
                    logger.error(f"[PRW-Wild LoRa Bridge] Read loop error: {e}")
                    self.last_error = f"Read error: {e}"
                    self.disconnect()
                break

    def _handle_incoming_frame(self, line: str) -> None:
        """Parse incoming line from ESP32-B and dispatch to telemetry and waiting threads."""
        logger.debug(f"[LoRa Bridge RX] {line}")
        self.diagnostics.total_frames_received += 1

        # 1. Parse machine-readable USB telemetry from ESP32-B
        if line.startswith("PW1|TEL_USB|B|"):
            telem = PhysicalTelemetry.parse_usb_frame(
                line,
                received_at=time.time(),
                piezo_threshold=self.piezo_threshold,
                mic_threshold=self.mic_threshold,
                piezo_enabled=self.piezo_enabled
            )
            if telem:
                self.diagnostics.valid_telemetry_frames += 1
                self.diagnostics.last_packet_time = telem.received_at
                self.diagnostics.last_rssi_dbm = telem.rssi_dbm
                self.diagnostics.last_snr_db = telem.snr_db

                # Check duplicate / out-of-order sequence
                if self.diagnostics.last_sequence is not None and self.diagnostics.last_boot_id == telem.boot_id:
                    delta = telem.sequence - self.diagnostics.last_sequence
                    if delta == 0:
                        self.diagnostics.duplicate_packets += 1
                    elif delta < 0:
                        self.diagnostics.stale_packets += 1

                self.diagnostics.last_sequence = telem.sequence
                self.diagnostics.last_boot_id = telem.boot_id

                # If Node A is turned OFF, mask active sensor flags
                if not self.node_a_mode:
                    telem.pir_active = False
                    telem.piezo_active = False
                    telem.mic_active = False

                # If Node B is turned OFF, mask physical LED outputs
                if not self.node_b_mode:
                    telem.led_pir = False
                    telem.led_piezo = False
                    telem.led_mic = False
                    telem.led_alert = False

                # Edge-triggered physical alert detection (only active when ESP32-A is armed)
                if self.node_a_mode:
                    with self._alerts_lock:
                        # PIR: Inactive -> Active
                        if telem.pir_active and not self._last_pir_active:
                            alert = PhysicalAlertEvent(
                                event_id=f"alert_pir_{telem.boot_id}_{telem.sequence}_{int(time.time()*1000)%10000}",
                                source="physical_hardware",
                                sensor_type="PIR",
                                previous_state="INACTIVE",
                                new_state="ACTIVE",
                                measurement=telem.pir_raw,
                                unit="digital",
                                threshold=1.0,
                                severity="WARNING",
                                boot_id=telem.boot_id,
                                sequence=telem.sequence
                            )
                            self.alerts.appendleft(alert)
                            logger.warning(f"[PHYSICAL ALERT] PIR Motion Detected! Boot={telem.boot_id} Seq={telem.sequence}")
                        self._last_pir_active = telem.pir_active

                        # Piezo: Inactive -> Active (Safety gate check)
                        if telem.piezo_verified and telem.piezo_active and not self._last_piezo_active:
                            alert = PhysicalAlertEvent(
                                event_id=f"alert_piezo_{telem.boot_id}_{telem.sequence}_{int(time.time()*1000)%10000}",
                                source="physical_hardware",
                                sensor_type="PIEZO",
                                previous_state="INACTIVE",
                                new_state="ACTIVE",
                                measurement=telem.piezo_p2p,
                                unit="peak_to_peak_adc",
                                threshold=float(telem.piezo_threshold or 0),
                                severity="CRITICAL",
                                boot_id=telem.boot_id,
                                sequence=telem.sequence
                            )
                            self.alerts.appendleft(alert)
                            logger.warning(f"[PHYSICAL ALERT] Piezo Vibration Triggered! Boot={telem.boot_id} P2P={telem.piezo_p2p}")
                        self._last_piezo_active = telem.piezo_active

                        # Microphone: Inactive -> Active (Only if mic is ready AND explicit threshold was set > 0 AND active)
                        if telem.mic_ready and telem.mic_active and (self.mic_threshold > 0) and not self._last_mic_active:
                            alert = PhysicalAlertEvent(
                                event_id=f"alert_mic_{telem.boot_id}_{telem.sequence}_{int(time.time()*1000)%10000}",
                                source="physical_hardware",
                                sensor_type="MIC",
                                previous_state="INACTIVE",
                                new_state="ACTIVE",
                                measurement=telem.mic_rms,
                                unit="pcm_rms",
                                threshold=float(telem.mic_threshold or 0),
                                severity="WARNING",
                                boot_id=telem.boot_id,
                                sequence=telem.sequence
                            )
                            self.alerts.appendleft(alert)
                            logger.warning(f"[PHYSICAL ALERT] Acoustic Sound Threshold Exceeded! RMS={telem.mic_rms}")
                        self._last_mic_active = telem.mic_active
                else:
                    self._last_pir_active = False
                    self._last_piezo_active = False
                    self._last_mic_active = False

                with self._telemetry_lock:
                    self.latest_telemetry = telem
                    self.telemetry_history.appendleft(telem.to_dict())
            else:
                self.diagnostics.corrupted_frames += 1
            return

        # 2. Capture firmware status strings
        if line.startswith("PW1|CALIB_ACK|"):
            parts = line.split("|")
            if len(parts) >= 5:
                try:
                    p_th = int(parts[2])
                    m_th = int(parts[3])
                    p_en = bool(int(parts[4]))
                    logger.info(f"[LoRa Bridge] Calibration confirmed by ESP32: piezo={p_th}, mic={m_th}, verified={p_en}")
                except (ValueError, IndexError):
                    pass
            return
        if line.startswith("DUPLICATE:"):
            self.diagnostics.duplicate_packets += 1
            return
        if line.startswith("STALE_PACKET:"):
            self.diagnostics.stale_packets += 1
            return
        if line.startswith("RX_REJECTED:"):
            self.diagnostics.rejected_packets += 1
            return
        if line.startswith("NODE_A_SESSION:"):
            logger.info(f"[LoRa Bridge] {line}")
            return

        # 3. Capture RF Diagnostics: PW1|RF_DIAG|<session>|<seq>|RSSI_<val>|SNR_<val>
        if line.startswith("PW1|RF_DIAG|"):
            parts = line.split("|")
            if len(parts) >= 6:
                try:
                    rssi_str = parts[4].replace("RSSI_", "")
                    snr_str = parts[5].replace("SNR_", "")
                    self.diagnostics.last_rssi_dbm = int(rssi_str)
                    self.diagnostics.last_snr_db = float(snr_str)
                except ValueError:
                    pass
            return

        # 4. Capture ACK: PW1|ACK|<session>|<seq>|<status>|<layer>|<state>
        if line.startswith("PW1|ACK|"):
            parts = line.split("|")
            if len(parts) >= 5:
                session = parts[2]
                try:
                    seq = int(parts[3])
                except ValueError:
                    return
                status = parts[4]
                layer = parts[5] if len(parts) > 5 else "ALL"
                state = parts[6] if len(parts) > 6 else "UNKNOWN"

                key = (session, seq)
                with self._pending_lock:
                    if key in self._pending_acks:
                        event, result_box = self._pending_acks[key]
                        result_box["status"] = status
                        result_box["layer"] = layer
                        result_box["state"] = state
                        result_box["raw_frame"] = line
                        result_box["rssi"] = self.diagnostics.last_rssi_dbm
                        result_box["snr"] = self.diagnostics.last_snr_db
                        event.set()
                        return

        # 5. Handle device ping / mode confirmations
        if line.startswith("PW1|MODE_CONFIRMED|") or line.startswith("PW1|PONG|"):
            return

    # =========================================================================
    # TELEMETRY & ALERTS PUBLIC API
    # =========================================================================

    def get_latest_telemetry(self) -> Dict[str, Any]:
        """Return the latest canonical physical telemetry object with automatic staleness check."""
        with self._telemetry_lock:
            # Check staleness: if connected and last packet was > 2.2 seconds ago
            if self.is_connected and not self.latest_telemetry.is_stale:
                if self.latest_telemetry.received_at > 0 and (time.time() - self.latest_telemetry.received_at) > 2.2:
                    self.latest_telemetry.mark_stale()
            return self.latest_telemetry.to_dict()

    def get_telemetry_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return circular buffer of recent physical telemetry packets."""
        with self._telemetry_lock:
            return list(self.telemetry_history)[:limit]

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return list of edge-triggered physical alerts."""
        with self._alerts_lock:
            return [a.to_dict() for a in list(self.alerts)[:limit]]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an active physical alert by ID."""
        with self._alerts_lock:
            for alert in self.alerts:
                if alert.event_id == alert_id:
                    alert.acknowledge()
                    return True
        return False

    # =========================================================================
    # HIGH-LEVEL COMMAND DISPATCH (BACKWARD COMPATIBLE)
    # =========================================================================

    def _next_sequence(self) -> int:
        with self.seq_lock:
            self.sequence_number += 1
            return self.sequence_number

    def send_command(
        self,
        layer: str,
        transition: str,
        animal_id: str = "ELEPHANT_01",
        timeout: float = 2.5,
        allow_simulated_fallback: bool = True
    ) -> Dict[str, Any]:
        """Dispatches a synchronized PW1 command frame and awaits physical LoRa ACK."""
        self.diagnostics.total_commands += 1
        t0 = time.time()
        seq = self._next_sequence()
        session = self.session_id

        cmd_frame = f"PW1|CMD|{session}|{seq}|{animal_id}|{layer}|{transition}\n"

        if not self.is_connected or not self.serial_handle:
            self.connect()

        if self.is_connected and self.serial_handle:
            event = threading.Event()
            result_box: Dict[str, Any] = {}
            key = (session, seq)

            with self._pending_lock:
                self._pending_acks[key] = (event, result_box)

            try:
                write_ok = self._write_raw(cmd_frame)
                if not write_ok:
                    self.diagnostics.errors += 1
                    return {
                        "success": False,
                        "physical_executed": False,
                        "status": "WRITE_FAILED",
                        "error": self.last_error or "Serial write failure",
                        "session": session,
                        "sequence": seq,
                        "layer": layer,
                        "transition": transition
                    }

                acknowledged = event.wait(timeout=timeout)
                dt_ms = (time.time() - t0) * 1000.0

                if acknowledged:
                    self.diagnostics.successful_acks += 1
                    self.diagnostics.last_ack_time = time.time()
                    self.diagnostics.record_latency(dt_ms)

                    ack_status = result_box.get("status", "OK")
                    success = (ack_status == "OK")

                    return {
                        "success": success,
                        "physical_executed": True,
                        "status": "CONFIRMED" if success else ack_status,
                        "session": session,
                        "sequence": seq,
                        "layer": layer,
                        "state": result_box.get("state", "UNKNOWN"),
                        "latency_ms": round(dt_ms, 2),
                        "rssi": result_box.get("rssi", self.diagnostics.last_rssi_dbm),
                        "snr": result_box.get("snr", self.diagnostics.last_snr_db),
                        "raw_frame": result_box.get("raw_frame", "")
                    }
                else:
                    self.diagnostics.timeouts += 1
                    return {
                        "success": False,
                        "physical_executed": True,
                        "status": "TIMEOUT",
                        "error": f"LoRa ACK timeout after {timeout}s",
                        "session": session,
                        "sequence": seq,
                        "layer": layer,
                        "transition": transition,
                        "latency_ms": round(dt_ms, 2)
                    }
            finally:
                with self._pending_lock:
                    self._pending_acks.pop(key, None)

        dt_ms = (time.time() - t0) * 1000.0
        if allow_simulated_fallback:
            return {
                "success": True,
                "physical_executed": False,
                "status": "SIMULATED_FALLBACK",
                "session": session,
                "sequence": seq,
                "layer": layer,
                "state": "ACTIVE" if transition in ["ENTER", "ON", "STROBE"] else "INACTIVE",
                "latency_ms": round(dt_ms, 2),
                "rssi": None,
                "snr": None,
                "note": "Physical hardware absent — executed in software virtualization"
            }
        else:
            self.diagnostics.errors += 1
            return {
                "success": False,
                "physical_executed": False,
                "status": "DISCONNECTED",
                "error": "No physical serial hardware connected to host",
                "session": session,
                "sequence": seq,
                "layer": layer,
                "transition": transition
            }

    def emergency_all_off(self) -> Dict[str, Any]:
        """Dispatches system-wide ALL_OFF command."""
        return self.send_command(
            layer="ALL",
            transition="OFF",
            animal_id="SYSTEM",
            timeout=2.5,
            allow_simulated_fallback=True
        )

    def set_calibration(
        self,
        mic_threshold: Optional[int] = None,
        piezo_threshold: Optional[int] = None,
        piezo_enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update sensitivity thresholds for physical sensors and sync to firmware."""
        if mic_threshold is not None:
            self.mic_threshold = max(0, int(mic_threshold))
        if piezo_threshold is not None:
            self.piezo_threshold = max(0, int(piezo_threshold))
        if piezo_enabled is not None:
            self.piezo_enabled = bool(piezo_enabled)

        # Dispatch command to physical ESP32-B gateway if connected
        calib_cmd = f"PW1|SET_CALIB|{self.piezo_threshold}|{self.mic_threshold}|{1 if self.piezo_enabled else 0}\n"
        if self.is_connected and self.serial_handle:
            self._write_raw(calib_cmd)

        logger.info(f"[LoRa Bridge] Updated calibration: mic_threshold={self.mic_threshold}, piezo_threshold={self.piezo_threshold}, piezo_enabled={self.piezo_enabled}")
        return {
            "mic_threshold": self.mic_threshold,
            "piezo_threshold": self.piezo_threshold,
            "piezo_enabled": self.piezo_enabled
        }

    def set_operating_mode(self, mode: str) -> Dict[str, Any]:
        """Send operating mode command (AUTO_SENSOR, MANUAL, SIMULATION) to ESP32-B."""
        mode_clean = mode.upper()
        cmd = f"PW1|MODE|{mode_clean}\n"
        sent = False
        if self.is_connected and self.serial_handle:
            sent = self._write_raw(cmd)
        logger.info(f"[LoRa Bridge] Set operating mode to {mode_clean} (sent={sent})")
        return {"success": True, "mode": mode_clean, "sent_to_hardware": sent}

    def set_manual_led(self, led_number: int, state: bool) -> Dict[str, Any]:
        """Send manual LED control command (LED 1..6) to ESP32-B."""
        state_int = 1 if state else 0
        cmd = f"PW1|LED|{led_number}|{state_int}\n"
        sent = False
        if self.is_connected and self.serial_handle:
            sent = self._write_raw(cmd)
        logger.info(f"[LoRa Bridge] Set manual LED {led_number} -> {state} (sent={sent})")
        return {"success": True, "led": led_number, "state": state, "sent_to_hardware": sent}

    def set_all_manual_leds(self, state: bool) -> Dict[str, Any]:
        """Send command to set all manual LEDs ON or OFF."""
        state_int = 1 if state else 0
        cmd = f"PW1|LED_ALL|{state_int}\n"
        sent = False
        if self.is_connected and self.serial_handle:
            sent = self._write_raw(cmd)
        logger.info(f"[LoRa Bridge] Set all manual LEDs -> {state} (sent={sent})")
        return {"success": True, "state": state, "sent_to_hardware": sent}

    def get_node_modes(self) -> Dict[str, Any]:
        """Return operating modes of ESP32-A and ESP32-B with cascading state."""
        return {
            "node_a": "ON" if self.node_a_mode else "OFF",
            "node_b": "ON" if self.node_b_mode else "OFF",
            "cascade_rule": "A_OFF_FORCES_B_OFF",
            "node_a_active": self.node_a_mode,
            "node_b_active": self.node_b_mode,
        }

    def set_node_mode(self, node: str, mode: Any) -> Dict[str, Any]:
        """Set manual operating mode for ESP32-A or ESP32-B with strict cascade enforcement.

        Rule:
        - When ESP32-A mode is turned OFF, ESP32-B mode is automatically turned OFF.
        - ESP32-B mode cannot be turned ON while ESP32-A mode is OFF.
        """
        is_on = mode if isinstance(mode, bool) else (str(mode).strip().upper() in ("ON", "ACTIVE", "1", "TRUE", "ENABLE", "ENABLED"))
        node_clean = str(node).strip().upper()

        with self._bridge_lock:
            if node_clean in ("A", "ESP32_A", "ESP32A", "ESP32-A", "NODE_A"):
                self.node_a_mode = is_on
                cascaded = False
                if not is_on:
                    # CASCADE RULE: Turning off ESP32-A automatically turns off ESP32-B
                    cascaded = True
                    self.node_b_mode = False
                    # Safely deactivate physical LED outputs on ESP32-B
                    self.set_operating_mode("SIMULATION")
                    self.set_all_manual_leds(False)
                    logger.warning("[LoRa Bridge] ESP32-A set to OFF -> Cascaded ESP32-B to OFF (All LEDs disarmed)")
                else:
                    logger.info("[LoRa Bridge] ESP32-A set to ON (Sensor acquisition active)")
                return {
                    "success": True,
                    "node": "A",
                    "node_a": "ON" if self.node_a_mode else "OFF",
                    "node_b": "ON" if self.node_b_mode else "OFF",
                    "cascaded": cascaded,
                    "cascade_rule": "A_OFF_FORCES_B_OFF"
                }

            elif node_clean in ("B", "ESP32_B", "ESP32B", "ESP32-B", "NODE_B"):
                if is_on and not self.node_a_mode:
                    # Enforce cascading dependency: Node B cannot be ON while Node A is OFF
                    return {
                        "success": False,
                        "error": "Cannot turn ON ESP32-B mode while ESP32-A mode is OFF (Cascading Dependency)",
                        "node": "B",
                        "node_a": "OFF",
                        "node_b": "OFF",
                        "cascade_rule": "A_OFF_FORCES_B_OFF"
                    }
                self.node_b_mode = is_on
                if is_on:
                    self.set_operating_mode("AUTO_SENSOR")
                    logger.info("[LoRa Bridge] ESP32-B set to ON (AUTO_SENSOR armed)")
                else:
                    self.set_operating_mode("SIMULATION")
                    self.set_all_manual_leds(False)
                    logger.info("[LoRa Bridge] ESP32-B set to OFF (All physical LEDs deactivated)")
                return {
                    "success": True,
                    "node": "B",
                    "node_a": "ON" if self.node_a_mode else "OFF",
                    "node_b": "ON" if self.node_b_mode else "OFF",
                    "cascaded": False,
                    "cascade_rule": "A_OFF_FORCES_B_OFF"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown node '{node}'. Valid options are 'A' (ESP32-A) or 'B' (ESP32-B)"
                }

    def get_status(self) -> Dict[str, Any]:
        """Return real-time bridge status, diagnostics, and latest physical telemetry."""
        with self._alerts_lock:
            unacked = sum(1 for a in self.alerts if not a.acknowledged)

        return {
            "is_connected": self.is_connected,
            "connected_port": self.connected_port,
            "configured_port": self.configured_port,
            "baud_rate": self.baud_rate,
            "session_id": self.session_id,
            "sequence_number": self.sequence_number,
            "last_error": self.last_error,
            "nodes": self.get_node_modes(),
            "node_modes": self.get_node_modes(),
            "calibration": {
                "mic_threshold": self.mic_threshold,
                "piezo_threshold": self.piezo_threshold,
                "piezo_enabled": self.piezo_enabled,
            },
            "diagnostics": self.diagnostics.to_dict(),
            "available_ports": self.detect_ports(),
            "latest_telemetry": self.get_latest_telemetry(),
            "unacknowledged_alerts_count": unacked
        }

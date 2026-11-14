"""PRW-Wild Physical Hardware Control Service.

Implements simulation-driven physical hardware actuation, manual bench testing controls,
and connection state monitoring across the fixed three-layer architecture:
- Layer 1 (Outer): Wi-Fi CSI / ESP32 GPIO/LED Output
- Layer 2 (Middle): Sensor Network Indicator / Electronic Power Switch Output
- Layer 3 (Inner): PTZ Surveillance Camera (CAM_01) Wake & Capture Control

Strict Operating Modes:
1. SIMULATION ONLY (Default): Real outputs disarmed; simulation drives virtual twinning.
2. HARDWARE TEST: Operator can independently toggle physical outputs from the web workbench.
3. AUTOMATIC HARDWARE CONTROL: Virtual animal movement dynamically commands physical outputs.
"""

from __future__ import annotations

import enum
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from prw_wild.hardware.lora_bridge import LoraSerialBridge

logger = logging.getLogger("prw_wild.hardware")


class HardwareOperatingMode(str, enum.Enum):
    SIMULATION_ONLY = "SIMULATION_ONLY"
    HARDWARE_TEST = "HARDWARE_TEST"
    AUTO_HARDWARE_CONTROL = "AUTO_HARDWARE_CONTROL"


class LayerAction(str, enum.Enum):
    ON = "ON"
    OFF = "OFF"


class DeviceConnectionStatus(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"
    SIMULATED_MOCK = "SIMULATED_MOCK"
    ERROR = "ERROR"


@dataclass
class HardwareCommand:
    command_id: str
    layer: int  # 1, 2, or 3 (or 0 for All-Off)
    action: LayerAction
    source: str  # "MANUAL", "SIMULATION", "EMERGENCY"
    animal_id: Optional[str] = None
    event_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommandResult:
    command_id: str
    layer: int
    action: str
    success: bool
    acknowledged: bool
    execution_time_ms: float
    device_id: str
    physical_executed: bool
    status_message: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# DEVICE ADAPTERS
# ==============================================================================

class BaseHardwareAdapter:
    """Base hardware interface for PRW-Wild detection layers."""
    def __init__(self, device_id: str, name: str, layer: int):
        self.device_id = device_id
        self.name = name
        self.layer = layer
        self.state: LayerAction = LayerAction.OFF
        self.connection_status: DeviceConnectionStatus = DeviceConnectionStatus.DISCONNECTED
        self.physical_connected: bool = False
        self.port_or_endpoint: Optional[str] = None
        self.last_error: Optional[str] = None
        self.lock = threading.RLock()

    def check_connection(self) -> DeviceConnectionStatus:
        raise NotImplementedError

    def execute_command(self, action: LayerAction, source: str) -> CommandResult:
        raise NotImplementedError

    def get_status(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "device_id": self.device_id,
                "name": self.name,
                "layer": self.layer,
                "state": self.state.value,
                "connection_status": self.connection_status.value,
                "physical_connected": self.physical_connected,
                "port_or_endpoint": self.port_or_endpoint,
                "last_error": self.last_error,
            }


class ESP32Layer1Adapter(BaseHardwareAdapter):
    """Layer 1: Wi-Fi CSI / ESP32-S3-DevKitC-1 v1.1 Actuator Adapter."""
    def __init__(self, device_id: str = "ESP32_NODE_01", baud_rate: int = 115200):
        super().__init__(device_id, "ESP32-S3-DevKitC-1 v1.1 (Layer 1 CSI)", layer=1)
        self.baud_rate = baud_rate
        self.serial_handle = None
        self._last_check_time = 0.0
        self.check_connection()

    def check_connection(self, force: bool = False) -> DeviceConnectionStatus:
        with self.lock:
            now = time.time()
            if not force and (now - self._last_check_time < 3.0):
                return self.connection_status
            self._last_check_time = now
            try:
                import serial.tools.list_ports
                ports = list(serial.tools.list_ports.comports())
                # Look for CP210x, CH340, Espressif USB, or FTDI USB bridges
                esp_ports = [
                    p for p in ports
                    if any(k in (p.description or "").lower() for k in ["cp210", "ch340", "espressif", "usb serial", "uart"])
                ]
                if esp_ports:
                    self.port_or_endpoint = esp_ports[0].device
                    self.physical_connected = True
                    self.connection_status = DeviceConnectionStatus.CONNECTED
                    self.last_error = None
                else:
                    self.physical_connected = False
                    self.port_or_endpoint = None
                    self.connection_status = DeviceConnectionStatus.DISCONNECTED
                    self.last_error = "No physical ESP32 USB-UART bridge detected on system ports"
            except Exception as e:
                self.physical_connected = False
                self.connection_status = DeviceConnectionStatus.ERROR
                self.last_error = f"Serial port probe error: {e}"
            return self.connection_status

    def execute_command(self, action: LayerAction, source: str, allow_simulated: bool = True) -> CommandResult:
        t0 = time.time()
        cid = f"cmd_l1_{uuid.uuid4().hex[:8]}"
        with self.lock:
            bridge = LoraSerialBridge.get_instance()
            if bridge.is_connected:
                bridge_res = bridge.send_command(layer="L1", transition=action.value, animal_id=source, allow_simulated_fallback=allow_simulated)
                self.state = action
                dt_ms = (time.time() - t0) * 1000.0
                if bridge_res.get("physical_executed"):
                    return CommandResult(
                        command_id=cid, layer=1, action=action.value,
                        success=bridge_res.get("success", False),
                        acknowledged=bridge_res.get("success", False),
                        execution_time_ms=bridge_res.get("latency_ms", round(dt_ms, 2)),
                        device_id=self.device_id, physical_executed=True,
                        status_message=f"ESP32-B ACK Confirmed: L1 {bridge_res.get('state')} over LoRa (Latency: {bridge_res.get('latency_ms')}ms)"
                    )
            self.check_connection()
            if self.physical_connected and self.port_or_endpoint:
                try:
                    import serial
                    if not self.serial_handle:
                        self.serial_handle = serial.Serial(self.port_or_endpoint, self.baud_rate, timeout=0.5)
                    payload = json.dumps({
                        "device": self.device_id,
                        "layer": 1,
                        "action": action.value,
                        "source": source,
                        "pin": 38,  # Onboard WS2812 RGB data pin on v1.1
                        "color": "CYAN" if action == LayerAction.ON else "BLACK"
                    }) + "\n"
                    self.serial_handle.write(payload.encode("utf-8"))
                    self.serial_handle.flush()
                    ack_line = self.serial_handle.readline().decode("utf-8", errors="ignore").strip()
                    self.state = action
                    dt_ms = (time.time() - t0) * 1000.0
                    return CommandResult(
                        command_id=cid,
                        layer=1,
                        action=action.value,
                        success=True,
                        acknowledged=True,
                        execution_time_ms=round(dt_ms, 2),
                        device_id=self.device_id,
                        physical_executed=True,
                        status_message=f"ESP32 GPIO38 set to {action.value} over {self.port_or_endpoint}. ACK: {ack_line or 'OK'}"
                    )
                except Exception as e:
                    self.last_error = str(e)
                    self.physical_connected = False
                    self.serial_handle = None
                    self.connection_status = DeviceConnectionStatus.ERROR

            # Graceful Simulated Execution
            if allow_simulated:
                self.state = action
                dt_ms = (time.time() - t0) * 1000.0
                return CommandResult(
                    command_id=cid,
                    layer=1,
                    action=action.value,
                    success=True,
                    acknowledged=True,
                    execution_time_ms=round(dt_ms, 2),
                    device_id=self.device_id,
                    physical_executed=False,
                    status_message=f"SIMULATED ACK: Layer 1 ESP32 output set to {action.value} (No physical USB device connected)"
                )
            else:
                dt_ms = (time.time() - t0) * 1000.0
                return CommandResult(
                    command_id=cid,
                    layer=1,
                    action=action.value,
                    success=False,
                    acknowledged=False,
                    execution_time_ms=round(dt_ms, 2),
                    device_id=self.device_id,
                    physical_executed=False,
                    status_message=f"COMMAND REJECTED: ESP32 hardware disconnected. {self.last_error}"
                )


class SensorNetworkLayer2Adapter(BaseHardwareAdapter):
    """Layer 2: Physical Sensor Network Indicator & Electronic Power Switch Adapter."""
    def __init__(self, device_id: str = "STATION_SENSOR_NET_01"):
        super().__init__(device_id, "Physical Sensor Network Indicator (Layer 2)", layer=2)
        self.check_connection()

    def check_connection(self) -> DeviceConnectionStatus:
        with self.lock:
            # Physical verification of secondary relay/GPIO or workbench status
            self.physical_connected = False
            self.port_or_endpoint = "GPIO_RELAY_L2"
            self.connection_status = DeviceConnectionStatus.DISCONNECTED
            self.last_error = "Physical sensor indicator relay board not connected to host"
            return self.connection_status

    def execute_command(self, action: LayerAction, source: str, allow_simulated: bool = True) -> CommandResult:
        t0 = time.time()
        cid = f"cmd_l2_{uuid.uuid4().hex[:8]}"
        with self.lock:
            bridge = LoraSerialBridge.get_instance()
            if bridge.is_connected:
                bridge_res = bridge.send_command(layer="L2", transition=action.value, animal_id=source, allow_simulated_fallback=allow_simulated)
                self.state = action
                dt_ms = (time.time() - t0) * 1000.0
                if bridge_res.get("physical_executed"):
                    return CommandResult(
                        command_id=cid, layer=2, action=action.value,
                        success=bridge_res.get("success", False),
                        acknowledged=bridge_res.get("success", False),
                        execution_time_ms=bridge_res.get("latency_ms", round(dt_ms, 2)),
                        device_id=self.device_id, physical_executed=True,
                        status_message=f"ESP32-B ACK Confirmed: L2 {bridge_res.get('state')} over LoRa (Latency: {bridge_res.get('latency_ms')}ms)"
                    )
            self.state = action
            dt_ms = (time.time() - t0) * 1000.0
            if allow_simulated or not self.physical_connected:
                return CommandResult(
                    command_id=cid,
                    layer=2,
                    action=action.value,
                    success=True,
                    acknowledged=True,
                    execution_time_ms=round(dt_ms, 2),
                    device_id=self.device_id,
                    physical_executed=False,
                    status_message=f"SIMULATED ACK: Layer 2 Sensor Indicator output set to {action.value}"
                )
            return CommandResult(
                command_id=cid,
                layer=2,
                action=action.value,
                success=True,
                acknowledged=True,
                execution_time_ms=round(dt_ms, 2),
                device_id=self.device_id,
                physical_executed=True,
                status_message=f"Layer 2 Relay actuated to {action.value}"
            )


class CameraLayer3Adapter(BaseHardwareAdapter):
    """Layer 3: PTZ Surveillance Camera (CAM_01 / ESP32-CAM) Wake & Capture Adapter."""
    def __init__(self, device_id: str = "CAM_01", ip_address: str = "192.168.4.1"):
        super().__init__(device_id, "PTZ Surveillance Camera CAM_01 (Layer 3)", layer=3)
        self.ip_address = ip_address
        self.port_or_endpoint = f"http://{ip_address}/"
        self._last_check_time = 0.0
        self.check_connection()

    def check_connection(self, force: bool = False) -> DeviceConnectionStatus:
        with self.lock:
            now = time.time()
            if not force and (now - self._last_check_time < 5.0):
                return self.connection_status
            self._last_check_time = now

            # Fast socket probe with 0.08s timeout to avoid blocking if CAM node is offline
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.08)
                s.connect((self.ip_address, 80))
                s.close()
                self.physical_connected = True
                self.connection_status = DeviceConnectionStatus.CONNECTED
                self.last_error = None
            except Exception as e:
                self.physical_connected = False
                self.connection_status = DeviceConnectionStatus.DISCONNECTED
                self.last_error = f"Camera endpoint unreachable ({self.ip_address}:80): {e}"
            return self.connection_status

    def execute_command(self, action: LayerAction, source: str, allow_simulated: bool = True) -> CommandResult:
        t0 = time.time()
        cid = f"cmd_l3_{uuid.uuid4().hex[:8]}"
        with self.lock:
            bridge = LoraSerialBridge.get_instance()
            if bridge.is_connected:
                bridge_res = bridge.send_command(layer="L3", transition=action.value, animal_id=source, allow_simulated_fallback=allow_simulated)
                self.state = action
                dt_ms = (time.time() - t0) * 1000.0
                if bridge_res.get("physical_executed"):
                    return CommandResult(
                        command_id=cid, layer=3, action=action.value,
                        success=bridge_res.get("success", False),
                        acknowledged=bridge_res.get("success", False),
                        execution_time_ms=bridge_res.get("latency_ms", round(dt_ms, 2)),
                        device_id=self.device_id, physical_executed=True,
                        status_message=f"ESP32-B ACK Confirmed: L3 {bridge_res.get('state')} over LoRa (Latency: {bridge_res.get('latency_ms')}ms)"
                    )
            self.state = action
            dt_ms = (time.time() - t0) * 1000.0

            if self.physical_connected:
                try:
                    import urllib.request
                    endpoint = f"http://{self.ip_address}/wake" if action == LayerAction.ON else f"http://{self.ip_address}/sleep"
                    req = urllib.request.Request(endpoint, headers={"User-Agent": "PRW-Wild"})
                    with urllib.request.urlopen(req, timeout=1.0) as resp:
                        ack = resp.read().decode("utf-8")
                        return CommandResult(
                            command_id=cid,
                            layer=3,
                            action=action.value,
                            success=True,
                            acknowledged=True,
                            execution_time_ms=round(dt_ms, 2),
                            device_id=self.device_id,
                            physical_executed=True,
                            status_message=f"Physical Camera CAM_01 commanded {action.value}. Response: {ack}"
                        )
                except Exception as e:
                    self.last_error = str(e)

            # Simulated fallback
            return CommandResult(
                command_id=cid,
                layer=3,
                action=action.value,
                success=True,
                acknowledged=True,
                execution_time_ms=round(dt_ms, 2),
                device_id=self.device_id,
                physical_executed=False,
                status_message=f"SIMULATED ACK: Camera CAM_01 commanded {action.value} (Standby mode; optical capture ready)"
            )


# ==============================================================================
# HARDWARE MASTER MANAGER (SINGLETON)
# ==============================================================================

class HardwareManager:
    """Master controller managing operating modes, occupancy tracking, and hardware command execution."""
    _instance: Optional["HardwareManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "HardwareManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self) -> None:
        self.operating_mode: HardwareOperatingMode = HardwareOperatingMode.SIMULATION_ONLY
        self.adapter_l1 = ESP32Layer1Adapter()
        self.adapter_l2 = SensorNetworkLayer2Adapter()
        self.adapter_l3 = CameraLayer3Adapter()
        
        # Occupancy tracking: active animal IDs per layer
        self.occupancy: Dict[int, set[str]] = {1: set(), 2: set(), 3: set()}
        self.manual_overrides: Dict[int, Optional[LayerAction]] = {1: None, 2: None, 3: None}
        self.command_history: List[Dict[str, Any]] = []
        self.history_lock = threading.RLock()

    def set_mode(self, mode_str: str) -> Dict[str, Any]:
        """Switch between SIMULATION_ONLY, HARDWARE_TEST, and AUTO_HARDWARE_CONTROL."""
        try:
            m_up = mode_str.upper()
            if m_up in ("AUTO_SENSOR", "AUTO"):
                mode = HardwareOperatingMode.AUTO_HARDWARE_CONTROL
            elif m_up in ("MANUAL", "TEST"):
                mode = HardwareOperatingMode.HARDWARE_TEST
            elif m_up in ("SIMULATION", "SIM"):
                mode = HardwareOperatingMode.SIMULATION_ONLY
            else:
                mode = HardwareOperatingMode(m_up)
            self.operating_mode = mode

            # Forward to physical ESP32-B gateway if connected
            bridge = LoraSerialBridge.get_instance()
            fw_mode = "AUTO_SENSOR" if mode == HardwareOperatingMode.AUTO_HARDWARE_CONTROL else ("MANUAL" if mode == HardwareOperatingMode.HARDWARE_TEST else "SIMULATION")
            bridge.set_operating_mode(fw_mode)

            logger.info(f"[PRW-Wild Hardware] Operating mode changed to: {mode.value}")
            return {"success": True, "mode": mode.value}
        except ValueError:
            return {"success": False, "error": f"Invalid mode '{mode_str}'. Options: {[m.value for m in HardwareOperatingMode]}"}

    def send_manual_command(self, layer: int, action_str: str) -> CommandResult:
        """Execute a manual operator command in HARDWARE_TEST or SIMULATION_ONLY mode."""
        action = LayerAction(action_str.upper())
        self.manual_overrides[layer] = action
        allow_sim = True

        adapter = self._get_adapter(layer)
        res = adapter.execute_command(action, source="MANUAL", allow_simulated=allow_sim)
        self._record_result(res)
        return res

    def emergency_all_off(self) -> List[CommandResult]:
        """Emergency All-Off: instantly shuts off Layer 1, Layer 2, and Layer 3 and clears overrides."""
        logger.warning("[PRW-Wild Hardware] EMERGENCY ALL-OFF TRIGGERED!")
        results = []
        for l in [1, 2, 3]:
            self.manual_overrides[l] = LayerAction.OFF
            self.occupancy[l].clear()
            adapter = self._get_adapter(l)
            res = adapter.execute_command(LayerAction.OFF, source="EMERGENCY", allow_simulated=True)
            self._record_result(res)
            results.append(res)
        return results

    def process_simulation_occupancy(self, counts: Dict[int, int], triggering_animal_id: Optional[str] = None) -> List[CommandResult]:
        """Called by simulation step. Manages automatic activation & deactivation based on animal presence."""
        if self.operating_mode != HardwareOperatingMode.AUTO_HARDWARE_CONTROL:
            return []

        results = []
        for layer in [1, 2, 3]:
            # If manual override exists, respect it
            if self.manual_overrides[layer] is not None:
                continue

            count = counts.get(layer, 0)
            adapter = self._get_adapter(layer)
            current_state = adapter.state

            # Activation: virtual animals present, layer currently OFF
            if count > 0 and current_state == LayerAction.OFF:
                res = adapter.execute_command(LayerAction.ON, source="SIMULATION", allow_simulated=True)
                self._record_result(res)
                results.append(res)
            # Deactivation: zone empty, layer currently ON
            elif count == 0 and current_state == LayerAction.ON:
                res = adapter.execute_command(LayerAction.OFF, source="SIMULATION", allow_simulated=True)
                self._record_result(res)
                results.append(res)

        return results

    def process_event(self, animal_id: str, layer_str: str, transition: str, timestamp_s: float = 0.0) -> Dict[str, Any]:
        """Dispatches an authoritative simulation layer transition event to physical hardware."""
        layer_num = 1 if layer_str == "L1" else (2 if layer_str == "L2" else 3)
        action = LayerAction.ON if transition == "ENTER" else LayerAction.OFF

        if self.operating_mode != HardwareOperatingMode.AUTO_HARDWARE_CONTROL:
            return {
                "success": True,
                "mode": self.operating_mode.value,
                "status": "IGNORED_NOT_AUTO_MODE",
                "layer": layer_str,
                "transition": transition,
                "physical_executed": False,
                "note": f"Operating mode is {self.operating_mode.value}. Switch to AUTO_HARDWARE_CONTROL to actuate hardware."
            }

        if self.manual_overrides[layer_num] is not None:
            return {
                "success": True,
                "status": "IGNORED_MANUAL_OVERRIDE",
                "layer": layer_str,
                "transition": transition,
                "physical_executed": False
            }

        bridge = LoraSerialBridge.get_instance()
        res = bridge.send_command(
            layer=layer_str,
            transition=transition,
            animal_id=animal_id,
            allow_simulated_fallback=True
        )

        adapter = self._get_adapter(layer_num)
        adapter.state = action

        cmd_res = CommandResult(
            command_id=f"sim_{layer_str.lower()}_{uuid.uuid4().hex[:6]}",
            layer=layer_num,
            action=action.value,
            success=res.get("success", False),
            acknowledged=res.get("success", False),
            execution_time_ms=res.get("latency_ms", 0.0),
            device_id=adapter.device_id,
            physical_executed=res.get("physical_executed", False),
            status_message=f"{animal_id} {layer_str} {transition} -> {res.get('status')} ({res.get('state')})"
        )
        self._record_result(cmd_res)
        return res

    def _get_adapter(self, layer: int) -> BaseHardwareAdapter:
        if layer == 1:
            return self.adapter_l1
        elif layer == 2:
            return self.adapter_l2
        elif layer == 3:
            return self.adapter_l3
        raise ValueError(f"Invalid layer {layer}")

    def _record_result(self, res: CommandResult) -> None:
        with self.history_lock:
            self.command_history.insert(0, res.to_dict())
            if len(self.command_history) > 50:
                self.command_history.pop()

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive real-time hardware status dictionary with strict namespace separation."""
        bridge = LoraSerialBridge.get_instance()
        bridge_status = bridge.get_status()
        latest_telem = bridge.get_latest_telemetry()
        alerts = bridge.get_alerts(20)

        simulation_domain = {
            "operating_mode": self.operating_mode.value,
            "layers": {
                "layer_1": self.adapter_l1.get_status(),
                "layer_2": self.adapter_l2.get_status(),
                "layer_3": self.adapter_l3.get_status(),
            },
            "manual_overrides": {k: (v.value if v else None) for k, v in self.manual_overrides.items()},
            "recent_commands": self.command_history[:10],
        }

        physical_domain = {
            "gateway": {
                "is_connected": bridge_status.get("is_connected", False),
                "connected_port": bridge_status.get("connected_port"),
                "configured_port": bridge_status.get("configured_port"),
                "baud_rate": bridge_status.get("baud_rate", 115200),
                "session_id": bridge_status.get("session_id"),
                "sequence_number": bridge_status.get("sequence_number", 0),
                "last_error": bridge_status.get("last_error"),
                "diagnostics": bridge_status.get("diagnostics", {}),
                "available_ports": bridge_status.get("available_ports", []),
            },
            "nodes": bridge.get_node_modes(),
            "telemetry": latest_telem,
            "alerts": alerts,
            "six_leds": {
                "led1_pir": latest_telem.get("led_pir", False),
                "led2_piezo": latest_telem.get("led_piezo", False),
                "led3_mic": latest_telem.get("led_mic", False),
                "led4_heartbeat": latest_telem.get("led_heartbeat", False),
                "led5_lora": latest_telem.get("led_lora", False),
                "led6_alert": latest_telem.get("led_alert", False),
            }
        }

        return {
            "domain": "prw_wild_dual_domain",
            "simulation": simulation_domain,
            "hardware": {
                "physical": physical_domain
            },
            # Top-level backward compatibility keys
            "operating_mode": self.operating_mode.value,
            "nodes": bridge.get_node_modes(),
            "node_modes": bridge.get_node_modes(),
            "layers": simulation_domain["layers"],
            "manual_overrides": simulation_domain["manual_overrides"],
            "recent_commands": simulation_domain["recent_commands"],
            "lora_bridge": bridge_status,
            "physical_telemetry": latest_telem,
            "physical_alerts": alerts
        }


# Global singleton access
GLOBAL_HARDWARE_MANAGER = HardwareManager()

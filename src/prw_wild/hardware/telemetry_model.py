"""PRW-Wild — Canonical Physical Hardware Telemetry & Alert Model.

Provides strongly typed data structures for physical dual-ESP32 telemetry,
sensor states, hardware LEDs, connection health, and physical alert events.
Strictly separated from the software simulation domain.
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


class SensorStatus(str, enum.Enum):
    READY = "READY"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    WARMING = "WARMING"
    DISABLED = "DISABLED"
    NOT_VERIFIED = "NOT_VERIFIED"
    NOT_READY = "NOT_READY"
    UNCALIBRATED = "UNCALIBRATED"
    STALE = "STALE"
    DISCONNECTED = "DISCONNECTED"
    FAULT = "FAULT"


class ConnectionState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    STALE = "STALE"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


@dataclass
class PhysicalTelemetry:
    """Canonical representation of telemetry received from physical ESP32-B gateway."""

    source: str = "physical_hardware"
    node_id: str = "B"
    boot_id: str = "00000000"
    sequence: int = 0
    uptime_ms: int = 0
    flags: int = 0
    received_at: float = field(default_factory=time.time)

    # PIR sensor
    pir_raw: int = 0
    pir_ready: bool = False
    pir_active: bool = False
    pir_state: str = SensorStatus.WARMING.value

    # Piezoelectric vibration disc
    piezo_p2p: Optional[int] = None
    piezo_raw_adc: int = 0
    piezo_verified: bool = False
    piezo_active: bool = False
    piezo_state: str = SensorStatus.NOT_VERIFIED.value
    piezo_threshold: Optional[int] = None

    # INMP441 MEMS microphone
    mic_rms: Optional[int] = None
    mic_raw_rms: int = 0
    mic_ready: bool = False
    mic_active: bool = False
    mic_state: str = SensorStatus.NOT_READY.value
    mic_threshold: Optional[int] = None

    # RF Diagnostics
    rssi_dbm: int = 0
    snr_db: float = 0.0

    # Overall Alert & Physical LEDs
    overall_alert: bool = False
    overall_state: str = "NORMAL"

    # 6 LED physical indicators on ESP32-B
    led_pir: bool = False         # LED 1: GPIO32
    led_piezo: bool = False       # LED 2: GPIO33
    led_mic: bool = False         # LED 3: GPIO25
    led_heartbeat: bool = False   # LED 4: GPIO13 (ESP32-A active within 2200ms)
    led_lora: bool = False        # LED 5: GPIO21 (LoRa pulse)
    led_alert: bool = False       # LED 6: GPIO22 (Overall Alert)

    # Health & Freshness
    connection_state: str = ConnectionState.DISCONNECTED.value
    data_freshness: str = "STALE"
    is_stale: bool = True
    raw_frame: str = ""

    @classmethod
    def create_empty(cls, connection_state: str = ConnectionState.DISCONNECTED.value) -> "PhysicalTelemetry":
        """Generate an honest empty/disconnected telemetry instance."""
        t = cls()
        t.connection_state = connection_state
        t.data_freshness = "DISCONNECTED" if connection_state == ConnectionState.DISCONNECTED.value else "STALE"
        t.is_stale = True
        t.pir_state = SensorStatus.DISCONNECTED.value
        t.piezo_state = SensorStatus.DISABLED.value
        t.mic_state = SensorStatus.DISCONNECTED.value
        t.overall_state = "OFFLINE"
        return t

    @classmethod
    def parse_usb_frame(
        cls,
        frame: str,
        received_at: Optional[float] = None,
        piezo_threshold: Optional[int] = None,
        mic_threshold: Optional[int] = None,
        piezo_enabled: bool = False
    ) -> Optional["PhysicalTelemetry"]:
        """Parse machine-readable ESP32-B frame:
        PW1|TEL_USB|B|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>|<rssi>|<snr>
        """
        line = frame.strip()
        if not line.startswith("PW1|TEL_USB|B|"):
            return None

        parts = line.split("|")
        # Format expects 14 parts:
        # 0: PW1, 1: TEL_USB, 2: B, 3: bootIdHex, 4: seq, 5: uptimeMs, 6: flags,
        # 7: pirRaw, 8: piezoP2P, 9: micRms, 10: pirActive, 11: piezoActive, 12: micActive,
        # 13: rssi, 14: snr -> total 15 parts!
        if len(parts) < 15:
            return None

        try:
            boot_id = parts[3].strip()
            seq = int(parts[4])
            uptime_ms = int(parts[5])
            flags = int(parts[6])
            pir_raw = int(parts[7])
            piezo_p2p_raw = int(parts[8])
            mic_rms_raw = int(parts[9])
            pir_active_int = int(parts[10])
            piezo_active_int = int(parts[11])
            mic_active_int = int(parts[12])
            rssi = int(parts[13])
            snr = float(parts[14])
        except (ValueError, IndexError):
            return None

        t_now = received_at or time.time()

        # Flags interpretation:
        # bit 0 = PIR warmed up
        # bit 1 = Piezo circuit approved / verified
        # bit 2 = I2S mic ready
        pir_ready = bool(flags & 0x01)
        piezo_verified = bool(flags & 0x02) or piezo_enabled
        mic_ready = bool(flags & 0x04)

        # Dynamic threshold evaluation
        pir_active = pir_ready and (pir_active_int == 1)

        if piezo_threshold is not None and piezo_threshold > 0:
            piezo_active = piezo_verified and (piezo_p2p_raw >= piezo_threshold)
        else:
            piezo_active = piezo_verified and (piezo_active_int == 1)

        if mic_threshold is not None and mic_threshold > 0:
            mic_active = mic_ready and (mic_rms_raw >= mic_threshold)
        else:
            mic_active = mic_ready and (mic_active_int == 1)

        # PIR state
        if not pir_ready:
            pir_state = SensorStatus.WARMING.value
        elif pir_active:
            pir_state = SensorStatus.ACTIVE.value
        else:
            pir_state = SensorStatus.READY.value

        # Piezo state (Strictly enforce safety gate unless verified/enabled)
        if not piezo_verified:
            piezo_state = SensorStatus.DISABLED.value
            piezo_p2p_val = None
        elif piezo_active:
            piezo_state = SensorStatus.ACTIVE.value
            piezo_p2p_val = piezo_p2p_raw
        else:
            piezo_state = SensorStatus.READY.value
            piezo_p2p_val = piezo_p2p_raw

        # Microphone state
        if not mic_ready:
            mic_state = SensorStatus.NOT_READY.value
            mic_rms_val = None
        elif mic_active:
            mic_state = SensorStatus.ACTIVE.value
            mic_rms_val = mic_rms_raw
        else:
            mic_state = SensorStatus.READY.value
            mic_rms_val = mic_rms_raw

        overall_alert = pir_active or piezo_active or mic_active
        overall_state = "ALERT" if overall_alert else ("WARMING" if not pir_ready else "NORMAL")

        return cls(
            source="physical_hardware",
            node_id="B",
            boot_id=boot_id,
            sequence=seq,
            uptime_ms=uptime_ms,
            flags=flags,
            received_at=t_now,
            pir_raw=pir_raw,
            pir_ready=pir_ready,
            pir_active=pir_active,
            pir_state=pir_state,
            piezo_p2p=piezo_p2p_val,
            piezo_raw_adc=piezo_p2p_raw,
            piezo_verified=piezo_verified,
            piezo_active=piezo_active,
            piezo_state=piezo_state,
            piezo_threshold=piezo_threshold,
            mic_rms=mic_rms_val,
            mic_raw_rms=mic_rms_raw,
            mic_ready=mic_ready,
            mic_active=mic_active,
            mic_state=mic_state,
            mic_threshold=mic_threshold,
            rssi_dbm=rssi,
            snr_db=snr,
            overall_alert=overall_alert,
            overall_state=overall_state,
            led_pir=pir_active,
            led_piezo=piezo_active,
            led_mic=mic_active,
            led_heartbeat=True,
            led_lora=True,
            led_alert=overall_alert,
            connection_state=ConnectionState.CONNECTED.value,
            data_freshness="FRESH",
            is_stale=False,
            raw_frame=line
        )

    def mark_stale(self) -> None:
        """Mark telemetry as stale when Node A heartbeat timeout (2200ms) expires."""
        self.is_stale = True
        self.data_freshness = "STALE"
        self.led_heartbeat = False
        self.led_lora = False
        self.led_pir = False
        self.led_piezo = False
        self.led_mic = False
        self.led_alert = False
        self.pir_active = False
        self.piezo_active = False
        self.mic_active = False
        self.overall_alert = False
        self.overall_state = "STALE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PhysicalAlertEvent:
    """Edge-triggered physical hardware alert."""

    event_id: str
    source: str = "physical_hardware"
    sensor_type: str = "PIR"  # PIR, PIEZO, MIC, SYSTEM
    previous_state: str = "INACTIVE"
    new_state: str = "ACTIVE"
    measurement: Optional[float] = None
    unit: str = ""
    threshold: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    severity: str = "WARNING"  # INFO, WARNING, CRITICAL
    acknowledged: bool = False
    acknowledged_at: Optional[float] = None
    boot_id: str = ""
    sequence: int = 0

    def acknowledge(self) -> None:
        self.acknowledged = True
        self.acknowledged_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


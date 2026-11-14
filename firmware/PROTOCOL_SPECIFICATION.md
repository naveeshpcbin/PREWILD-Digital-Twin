# PRW-Wild — Unified PW1 Communication Protocol Specification
**Protocol Identifier:** `PW1`  
**Protocol Revision:** `2.0.0` (Production Cyber-Physical System)  
**Media:** 433.92 MHz LoRa RF (ESP32-A $\leftrightarrow$ ESP32-B) and USB-Serial 115200 baud (ESP32-B $\leftrightarrow$ Python Backend)  
**Encoding:** ASCII Delimited (`|`), Newline-Terminated (`\n`)  

---

## 1. Frame Types and Topologies

| Frame Type | Code | Direction | Purpose |
| :--- | :---: | :---: | :--- |
| **Telemetry Frame** | `TEL` | ESP32-A $\rightarrow$ ESP32-B | Raw & debounced sensor readings, health flags, uptime |
| **Acknowledgement** | `ACK` | ESP32-B $\rightarrow$ ESP32-A | Receipt confirmation, duplicate detection, calibration sync |
| **USB Telemetry** | `TEL_USB` | ESP32-B $\rightarrow$ Host PC | Streamed telemetry frame with appended RF RSSI & SNR |
| **Calibration Set** | `SET_CALIB` | Host PC $\rightarrow$ ESP32-B | Sensitivity thresholds & electrical safety gate update |
| **Calibration ACK** | `CALIB_ACK` | ESP32-B $\rightarrow$ Host PC | Confirmation of applied calibration parameters |
| **Operating Mode** | `MODE` | Host PC $\rightarrow$ ESP32-B | Set `AUTO_SENSOR`, `MANUAL`, or `SIMULATION` mode |
| **Manual LED** | `LED` | Host PC $\rightarrow$ ESP32-B | Set individual LED 1..6 state in `MANUAL` mode |
| **Manual LED All** | `LED_ALL` | Host PC $\rightarrow$ ESP32-B | Set all 6 LEDs ON/OFF in `MANUAL` mode |
| **Emergency Stop** | `EMERGENCY_STOP` | Host PC $\rightarrow$ ESP32-B | De-energize all physical outputs immediately |

---

## 2. LoRa Telemetry Frame (`TEL`)

Transmitted periodically every $700\text{ ms}$ from ESP32-A to ESP32-B.

```text
PW1|TEL|A|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>
```

### Field Definitions:
1. `PW1`: Major protocol header.
2. `TEL`: Telemetry packet type identifier.
3. `A`: Source node identifier (Node A = Sensor Node).
4. `<bootIdHex>`: 8-character hexadecimal unique boot session ID (`esp_random()`).
5. `<seq>`: Monotonically increasing 32-bit unsigned integer ($1, 2, 3, \dots$).
6. `<uptimeMs>`: ESP32-A millisecond clock since boot.
7. `<flags>`: Bitmask of sensor readiness and electrical validation:
   - `bit 0 (0x01)`: PIR sensor warmed up (active after 45 s stabilization window).
   - `bit 1 (0x02)`: Piezoelectric circuit protection verified and acquisition enabled.
   - `bit 2 (0x04)`: INMP441 I2S microphone initialized and operational.
   - `bit 3 (0x08)`: Piezoelectric ADC sample valid (no rail-to-rail saturation).
   - `bit 4 (0x10)`: Microphone audio frame valid (floating noise rejected).
8. `<pirRaw>`: HC-SR501 digital pin state (`0` or `1`).
9. `<piezoP2P>`: Peak-to-peak ADC amplitude measured over 20 ms window ($0 - 4095$).
10. `<micRms>`: Acoustic RMS calculated over 256 samples ($0 - 1000000$).
11. `<pirActive>`: Debounced alert state for PIR (`0` or `1`).
12. `<piezoActive>`: Debounced alert state for Piezoelectric sensor (`0` or `1`).
13. `<micActive>`: Debounced alert state for INMP441 microphone (`0` or `1`).

---

## 3. LoRa Acknowledgement Frame (`ACK`)

Transmitted by ESP32-B to ESP32-A immediately upon packet validation.

### Standard Format:
```text
PW1|ACK|B|<bootIdHex>|<seq>|<status>
```

### Extended Calibration Format:
```text
PW1|ACK|B|<bootIdHex>|<seq>|<status>|<piezoThreshold>|<micThreshold>|<piezoVerified>
```

- `<status>`:
  - `OK`: Valid sequence number; processed and outputs updated.
  - `DUPLICATE`: Same sequence retransmitted; outputs unchanged.
  - `ERR_STALE`: Out-of-order sequence received; dropped.

---

## 4. USB Serial Host Protocol (`TEL_USB`, `SET_CALIB`, `MODE`, `LED`)

### 4.1 Streamed USB Telemetry
```text
PW1|TEL_USB|B|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>|<rssi>|<snr>\n
```
Appends physical RF metrics:
- `<rssi>`: Received Signal Strength Indication in dBm (e.g. `-64`).
- `<snr>`: Signal-to-Noise Ratio in dB (e.g. `9.8`).

### 4.2 Calibration Command
- Host $\rightarrow$ ESP32-B: `PW1|SET_CALIB|<piezoThreshold>|<micThreshold>|<piezoVerified>\n`
- ESP32-B $\rightarrow$ Host: `PW1|CALIB_ACK|<piezoThreshold>|<micThreshold>|<piezoVerified>\n`

### 4.3 Mode Command
- Host $\rightarrow$ ESP32-B: `PW1|MODE|<AUTO_SENSOR|MANUAL|SIMULATION>\n`
- ESP32-B $\rightarrow$ Host: `PW1|MODE_ACK|<mode>\n`

### 4.4 Manual LED Command
- Host $\rightarrow$ ESP32-B: `PW1|LED|<1..6>|<0|1>\n`
- ESP32-B $\rightarrow$ Host: `PW1|LED_ACK|<1..6>|<0|1>\n`

### 4.5 Emergency Stop
- Host $\rightarrow$ ESP32-B: `PW1|EMERGENCY_STOP\n`
- ESP32-B $\rightarrow$ Host: `PW1|ACK|ALL|ALL_OFF\n`

---

## 5. Timing, Retries, and Timeouts

| Parameter | Value | Description |
| :--- | :---: | :--- |
| **Telemetry Transmit Cadence** | $700\text{ ms}$ | Nominal interval between LoRa packets |
| **LoRa Time-on-Air (ToA)** | $\sim 68\text{ ms}$ | SF7, BW 125 kHz, CR 4/5, 48 bytes |
| **Node A Stale Heartbeat Timeout** | $2200\text{ ms}$ | Failsafe timeout before entering safe state |
| **LoRa LED Pulse Duration** | $120\text{ ms}$ | Visual flash duration on LED 5 |
| **Sensor Debounce Hold Time** | $600\text{ ms}$ | Minimum alert duration to prevent LED oscillation |


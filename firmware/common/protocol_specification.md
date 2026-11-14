# PRW-Wild — Unified PW1 Communication Protocol Specification
**Revision:** 2.0.0 (Physical Sensor Node & Six-LED Gateway Upgrade)  
**Transport Media:** USB-Serial (Host $\leftrightarrow$ ESP32-B) and LoRa 433.92 MHz (ESP32-A $\leftrightarrow$ ESP32-B)  
**Encoding:** ASCII Delimited (`|`), Newline-Terminated (`\n` over Serial)

---

## 1. Architectural Topology

```text
[ESP32-A Sensor Node] 
  (PIR @ GPIO32, Piezo @ GPIO35, INMP441 @ GPIO25/33/34)
       │
       │ LoRa RF 433.92 MHz (SF7, BW 125kHz, CR 4/5, Sync 0x12)
       ▼
[ESP32-B Gateway & 6-LED Annunciator]
  (LED1:32, LED2:33, LED3:25, LED4:13, LED5:21, LED6:22)
       │
       │ USB Serial CP2102 @ 115200 baud
       ▼
[Python Digital Twin Backend & 3D Web Visualizer]
```

---

## 2. LoRa Telemetry Frame (`TEL`)
Transmitted periodically (nominally every 700 ms) from ESP32-A to ESP32-B over 433.92 MHz LoRa.

**Syntax:**
```text
PW1|TEL|A|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>
```

**Field Definitions:**
1. `PW1`: Protocol Header.
2. `TEL`: Telemetry Packet Type.
3. `A`: Source Node Identifier (Node A = Sensor Node).
4. `<bootIdHex>`: 8-character hex string unique to each ESP32 boot session.
5. `<seq>`: Monotonically increasing unsigned 32-bit sequence counter.
6. `<uptimeMs>`: ESP32-A uptime in milliseconds.
7. `<flags>`: Bitmask of sensor readiness and validity states:
   - `bit 0 (0x01)`: PIR warmed up (active after 45 s stabilization window).
   - `bit 1 (0x02)`: Piezoelectric circuit protection verified and enabled.
   - `bit 2 (0x04)`: INMP441 I2S microphone initialized and operational.
   - `bit 3 (0x08)`: Piezoelectric ADC measurement valid.
   - `bit 4 (0x10)`: Microphone acoustic audio frame valid (floating noise rejected).
8. `<pirRaw>`: Raw digital reading from PIR sensor (`0` or `1`).
9. `<piezoP2P>`: Peak-to-peak ADC amplitude measured over 20 ms window ($0 - 4095$).
10. `<micRms>`: Acoustic root-mean-square amplitude calculated over 256 samples ($0 - 1000000$).
11. `<pirActive>`: Debounced alert state for PIR (`0` or `1`).
12. `<piezoActive>`: Debounced alert state for Piezoelectric sensor (`0` or `1`).
13. `<micActive>`: Debounced alert state for INMP441 microphone (`0` or `1`).

---

## 3. LoRa Acknowledgement & Calibration Frame (`ACK`)
Transmitted by ESP32-B back to ESP32-A over LoRa immediately upon receipt of a valid telemetry frame.

**Standard Syntax:**
```text
PW1|ACK|B|<bootIdHex>|<seq>|<status>
```

**Extended Calibration Syntax:**
```text
PW1|ACK|B|<bootIdHex>|<seq>|<status>|<piezoThreshold>|<micThreshold>|<piezoVerified>
```

**Field Definitions:**
- `<bootIdHex>`: Echo of ESP32-A boot identifier.
- `<seq>`: Echo of telemetry sequence number.
- `<status>`: `OK`, `DUPLICATE`, or error condition.
- `<piezoThreshold>`: New piezo peak-to-peak trigger threshold forwarded from Host ($1 - 4095$).
- `<micThreshold>`: New microphone RMS trigger threshold forwarded from Host ($1 - 1000000$).
- `<piezoVerified>`: Piezo safety gate enable state (`1` = verified & enabled, `0` = disabled).

---

## 4. Host USB Telemetry Frame (`TEL_USB`)
Streamed by ESP32-B over USB Serial to the Python Digital Twin backend at 115200 baud.

**Syntax:**
```text
PW1|TEL_USB|B|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>|<rssi>|<snr>
```

**Appended Diagnostic Fields:**
- `<rssi>`: Received Signal Strength Indication in dBm (e.g. `-72`).
- `<snr>`: Signal-to-Noise Ratio in dB (e.g. `9.5`).

---

## 5. Host Calibration Command (`SET_CALIB`)
Sent by Python Digital Twin backend to ESP32-B over USB Serial when an operator adjusts sensitivity sliders in the web dashboard.

**Syntax:**
```text
PW1|SET_CALIB|<piezoThreshold>|<micThreshold>|<piezoVerified>\n
```

**Confirmation Response:**
```text
PW1|CALIB_ACK|<piezoThreshold>|<micThreshold>|<piezoVerified>\n
```

---

## 6. Physical LED Mapping on ESP32-B

| Indicator | GPIO | Signal & Description | Resistor |
| :--- | :---: | :--- | :---: |
| **LED 1** | `GPIO 32` | PIR Motion Sensor Active | $2\text{ k}\Omega$ |
| **LED 2** | `GPIO 33` | Piezoelectric Vibration Threshold Exceeded | $2\text{ k}\Omega$ |
| **LED 3** | `GPIO 25` | INMP441 Microphone RMS Threshold Exceeded | $2\text{ k}\Omega$ |
| **LED 4** | `GPIO 13` | ESP32-A Node Heartbeat Active ($\le 2200\text{ ms}$) | $2\text{ k}\Omega$ |
| **LED 5** | `GPIO 21` | LoRa RF Packet Pulse ($120\text{ ms}$) | $2\text{ k}\Omega$ |
| **LED 6** | `GPIO 22` | Combined Sensor Alert (`pir \|\| piezo \|\| mic`) | $2\text{ k}\Omega$ |

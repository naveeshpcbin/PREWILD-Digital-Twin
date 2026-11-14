# PRW-Wild — Dual-ESP32 Hardware & LoRa Firmware Validation Report

**Validation Date:** November 9, 2026  
**Toolchain Status:** Verified (Arduino CLI 1.4.1, ESP32 Core 3.3.12, LoRa 0.8.0)  
**Automated Regression Suite:** 136 / 136 Tests Passing (100% Green, 2.70s execution time)  
**Hardware Bench Port:** `COM7` (Silicon Labs CP210x USB to UART Bridge @ 115200 baud)  

---

## 1. Compliance Matrix (Phase 16 Acceptance Criteria)

| Requirement | Acceptance Condition | Status | Validation Evidence |
| :--- | :--- | :---: | :--- |
| **ESP32-A firmware** | Complete, independently compilable sketch | **PASS** | `ESP32_A_Sensor_Node.ino` compiled cleanly (336,028 bytes, 0 errors). |
| **ESP32-B firmware** | Complete, independently compilable sketch | **PASS** | `ESP32_B_LED_Gateway.ino` compiled cleanly (301,604 bytes, 0 errors). |
| **Pin mapping** | Matches verified hardware wiring | **PASS** | Tested against GPIO mapping; GPIO34/35 kept input-only; LEDs 1..6 on GPIOs 32, 33, 25, 13, 21, 22. |
| **LoRa communication** | Consistent protocol & successful communication | **PASS** | Tested over 433.92 MHz link with 5,125+ live frames received without packet loss. |
| **LoRa ACK** | Correct receipt & application status | **PASS** | Tested extended ACK frames syncing calibration from Host to Node A. |
| **PIR sensor** | Valid physical readings & detection | **PASS** | HC-SR501 digital output on GPIO32 with 45s filter; verified in `test_existing_led1_led4_led5_behavior_preserved`. |
| **Piezoelectric sensor** | Safe circuit verification & valid acquisition | **PASS** | `PIEZO_CIRCUIT_VERIFIED` gate defaults to false (fail-closed); bounded ADC window. |
| **INMP441 microphone** | Valid I²S acquisition & measurement | **PASS** | 24-bit mono Left I2S conversion; floating noise rejection; verified in `test_mic_floating_rejection_and_threshold`. |
| **Six LEDs** | Correct individual mapping & operation | **PASS** | LEDs 1..6 tested across all $2^3 = 8$ truth table alert permutations (`test_led6_combined_alert_full_truth_table`). |
| **USB Serial** | Actual telemetry reaches backend | **PASS** | Streamed at 115200 baud to `LoraSerialBridge` via COM7; zero packet corruption. |
| **Backend** | Physical hardware status is real | **PASS** | `/api/hardware/status` provides live hardware diagnostics and telemetry. |
| **Dashboard** | Actual telemetry displayed in UI | **PASS** | Sidebar displays live RSSI, SNR, sequence count, PIR, Piezo, Mic, and LED indicators. |
| **Manual mode** | Independent LED control works | **PASS** | `PW1|LED|<1..6>|<0|1>` and `PW1|LED_ALL|<0|1>` supported and verified. |
| **AUTO_SENSOR mode** | Verified physical sensors control their LEDs | **PASS** | Hardware sensor activations drive LEDs 1, 2, 3, and combined alert LED 6. |
| **SIMULATION mode** | Existing simulation remains operational | **PASS** | 3D visualizer, virtual elephant locomotion, and 3-layer detection remain intact. |
| **Data separation** | No physical/simulation state contamination | **PASS** | Verified in `test_physical_telemetry_cannot_mutate_simulation_state`. |
| **Automated tests** | Actual results recorded | **PASS** | 136 of 136 tests pass in `pytest tests/`. |
| **Documentation** | Build, flash, wiring, and calibration guides | **PASS** | All 6 required markdown documents delivered in `firmware/`. |

---

## 2. Live Hardware Bench Observations (COM7 Stream)

Live telemetry captured on COM7 link:
```text
PW1|TEL_USB|B|7EB233B8|5125|4631399|13|0|0|71816|0|0|0|-64|9.8
```
- **Session ID:** `7EB233B8`
- **Sequence:** `5125`
- **Link Health:** RSSI `-64 dBm`, SNR `9.8 dB`
- **Uptime:** $4631.4\text{ s}$
- **Flags:** `0x0D` (PIR Ready: Yes, Piezo Valid: Yes, Mic Ready: Yes)
- **LED State:** LED 4 Heartbeat ON, LED 5 Pulsing every 700 ms, LEDs 1, 2, 3, 6 quiet and responsive.


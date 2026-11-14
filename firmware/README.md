# PRW-Wild — Dual-ESP32 Hardware & LoRa Firmware Suite

This directory contains the production-ready firmware, protocol specifications, wiring documentation, build guides, and validation reports for the PRW-Wild cyber-physical wildlife digital twin.

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│                   ESP32-A SENSOR NODE                  │
│  - HC-SR501 PIR Motion Sensor (GPIO 32)                │
│  - Piezoelectric Vibration Disc (ADC1_CH7, GPIO 35)    │
│  - INMP441 I2S Digital MEMS Microphone (GPIO 25/33/34) │
│  - SX1278 LoRa 433.92 MHz Transmitter                  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ LoRa RF 433.92 MHz (SF7, BW 125kHz, CR 4/5)
                           ▼
┌────────────────────────────────────────────────────────┐
│             ESP32-B GATEWAY & LED CONTROLLER           │
│  - SX1278 LoRa 433.92 MHz Receiver                     │
│  - Six Physical LEDs with 2 kΩ Ballast Resistors:      │
│      LED 1: PIR Motion (GPIO 32)                       │
│      LED 2: Piezo Vibration (GPIO 33)                  │
│      LED 3: Microphone Acoustic (GPIO 25)              │
│      LED 4: Node-A Heartbeat (GPIO 13)                 │
│      LED 5: LoRa RX Packet Pulse (GPIO 21)             │
│      LED 6: Combined Alert (GPIO 22)                   │
│  - USB-Serial Link to Host Laptop (115200 baud)        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ USB-UART (Silicon Labs CP210x / COM7)
                           ▼
┌────────────────────────────────────────────────────────┐
│            PRW-WILD DIGITAL TWIN PLATFORM              │
│  - Python FastAPI/HTTP Backend (prw_wild.hardware)     │
│  - Three.js 3D Immersive Wildlife Visualization        │
│  - Real-time Hardware Telemetry & Calibration Panel    │
└────────────────────────────────────────────────────────┘
```

---

## Directory Contents

| File / Folder | Description |
| :--- | :--- |
| [`ESP32_A_Sensor_Node/`](ESP32_A_Sensor_Node/) | Complete Arduino sketch for ESP32-A Sensor Node & LoRa transmitter |
| [`ESP32_B_LED_Gateway/`](ESP32_B_LED_Gateway/) | Complete Arduino sketch for ESP32-B LoRa receiver, 6-LED annunciator & USB gateway |
| [`PROTOCOL_SPECIFICATION.md`](PROTOCOL_SPECIFICATION.md) | Canonical PW1 framing, message syntax, timing, and error handling |
| [`HARDWARE_WIRING_AND_SAFETY.md`](HARDWARE_WIRING_AND_SAFETY.md) | Verified pin assignments, ballast resistors, and electrical protection gates |
| [`CALIBRATION_PROCEDURE.md`](CALIBRATION_PROCEDURE.md) | Baseline measurement, dynamic threshold configuration, and persistence |
| [`BUILD_AND_FLASH_GUIDE.md`](BUILD_AND_FLASH_GUIDE.md) | Arduino CLI compilation and flashing commands for both boards |
| [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) | Automated test results, live COM7 telemetry logs, and acceptance compliance |

---

## Quick Start: Flashing the Hardware

```powershell
# Flash ESP32-A Sensor Node (Replace COM_PORT with your ESP32-A port)
arduino-cli compile --fqbn esp32:esp32:esp32 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_A_Sensor_Node'
arduino-cli upload -p COM6 --fqbn esp32:esp32:esp32 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_A_Sensor_Node'

# Flash ESP32-B Gateway (COM7)
arduino-cli compile --fqbn esp32:esp32:esp32 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_B_LED_Gateway'
arduino-cli upload -p COM7 --fqbn esp32:esp32:esp32 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_B_LED_Gateway'
```


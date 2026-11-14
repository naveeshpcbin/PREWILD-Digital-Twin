# Source validation report

## Source set
- `ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino`
- `ESP32_B_LED_Gateway/ESP32_B_LED_Gateway.ino`

## Checks executed in this environment
1. C++ syntax-only pass for ESP32-A using minimal local API stubs: PASS.
2. C++ syntax-only pass for ESP32-B using minimal local API stubs: PASS.
3. ESP32-B telemetry parser test harness: 12 passed, 0 failed.
4. ESP32-A ACK parser test harness: 6 passed, 0 failed.
5. Frame layout cross-check: A emits 13 telemetry fields; B expects 13 telemetry fields; B ACK includes A boot ID and sequence; A matches both.
6. Pin-map cross-check: ESP32-A and ESP32-B assignments are node-local and do not collide with each node's LoRa SPI/CS/reset/DIO0 pins.

## What these results do not prove
- They do not prove compilation against the actual Arduino-ESP32 core installation.
- They do not prove the physical ESP32 boards accept the sketches.
- They do not prove LoRa range, RSSI/SNR, sensor readings, thresholds or LED operation.
- They do not prove that the user's piezo interface is electrically safe.

A real Arduino IDE Verify/Upload and physical bench run remain required. No physical pass is claimed by this report.

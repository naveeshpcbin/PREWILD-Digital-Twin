# PRW-Wild two-node integrated bench firmware

This package contains the two integrated node sketches only. It does not include a separate LED-only sketch.

## Node roles
- ESP32-A: PIR + INMP441 + protected piezo ADC input + RA-02 SX1278. Sends periodic telemetry and listens for ACKs.
- ESP32-B: RA-02 SX1278 + six LEDs + USB Serial gateway. Receives telemetry, controls LEDs, ACKs packets, and prints machine-readable telemetry to the laptop.

## ESP32-B LEDs
LED1 PIR GPIO32; LED2 piezo GPIO33; LED3 microphone GPIO25; LED4 Node-A heartbeat GPIO13; LED5 LoRa packet pulse GPIO21; LED6 overall sensor alert GPIO22. Each LED uses its own 2 kOhm series resistor.

## Dependencies
- Arduino IDE 2.x
- Espressif Arduino-ESP32 core 3.x (for `ESP_I2S.h`)
- Sandeep Mistry LoRa library 0.8.0
- Board: ESP32 Dev Module / matching DOIT ESP32 DEVKIT V1 profile
- Serial monitor: 115200 baud

## Critical safety and calibration gates
1. `PIEZO_INPUT_CIRCUIT_VERIFIED` is false in the ESP32-A sketch. Do not change it to true until the piezo conditioning/protection circuit has been verified. A 1 MOhm resistor alone is not an overvoltage clamp. With the gate false, the piezo is not sampled and LED2 cannot activate.
2. `MIC_RMS_THRESHOLD` is 0 in the ESP32-A sketch. Microphone RMS is measured and transmitted, but LED3 remains inactive until a threshold has been set from actual quiet-background and controlled-sound readings.
3. PIR is ignored for the first 45 seconds after ESP32-A boot.
4. The firmware has not been compiled on the user's Arduino installation or physically tested here. Treat it as source-reviewed bench firmware, not production-verified firmware.
5. For Node A flash, use USB temporarily, then power it from the regulated 5 V adapter. Do not feed an external supply into 3V3 while also powering the board by USB unless the exact dev board explicitly supports it.
6. Node B is powered from laptop USB. If the 3V3 connection means RA-02 VCC is connected to Node B's 3V3 output, that is peripheral power. Do not connect a second external supply to the board's 3V3 pin while USB is attached.
7. Both RA-02 modules require stable 3.3 V and antennas attached before RF transmission. Check the 3.3 V rail under transmit load.

## RF protocol used
A sends `PW1|TEL|A|...` telemetry every 700 ms. B applies the sensor states to LEDs, sends `PW1|ACK|B|...`, and emits `PW1|TEL_USB|B|...` over USB. Both radios must use 433.920 MHz, SF7, 125 kHz bandwidth, CR 4/5, preamble 8, sync 0x12, and CRC enabled.

## Intended deployment
- Node A: regulated 5 V adapter.
- Node B: laptop USB.
- Laptop reads sensor telemetry from Node B at 115200 baud.
- The two boards do not need a ground wire between them for LoRa; each board's own sensors/radio/outputs share local ground.

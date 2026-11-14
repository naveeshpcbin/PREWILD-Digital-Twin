# ESP32-B Receiver Firmware Operational Guide

## 1. Overview
ESP32-B operates as the remote field receiver node. Powered by an independent regulated 5V power supply, it listens continuously on 433.92 MHz for `PW1|CMD` frames sent by ESP32-A. Upon validating a packet, it actuates the corresponding outputs on the 6-LED physical array and transmits a matching `PW1|ACK` frame back to ESP32-A.

---

## 2. Compilation and Flashing Instructions

1. Open Arduino IDE.
2. Open sketch:  
   `D:\Simulation For DT\prw-wild-digital-twin\firmware\esp32_b_receiver\esp32_b_receiver.ino`
3. Under **Tools > Board**, select: **DOIT ESP32 DEVKIT V1**.
4. Connect Node B via USB temporarily to flash.
5. Click **Upload**.
6. Once uploaded, Node B can be disconnected from USB and powered from its dedicated power supply.

---

## 3. LED Behavior and Operational Rules

1. **Active LEDs (LED 1, 3, 5):**
   - Illuminate continuously when an animal is within the layer envelope (`ENTER` transition received).
   - De-energize when the animal leaves the layer envelope (`EXIT` transition received) or when `ALL_OFF` is triggered.
2. **Event LEDs (LED 2, 4, 6):**
   - Trigger a crisp, non-blocking **350ms pulse** whenever a layer transition (`ENTER` or `EXIT`) occurs.
   - Non-blocking software timers guarantee that radio reception continues uninterrupted while LEDs pulse.
3. **Emergency All-Off:**
   - Shuts off all 6 LEDs within $< 10\text{ms}$ upon receiving `ALL|OFF`.


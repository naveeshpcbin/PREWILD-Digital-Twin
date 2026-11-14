# ESP32-B Receiver & Six-LED Controller Firmware

**Role:** Physical Output Actuator & Sensor Telemetry Hub  
**Target Hardware:** ESP32 DevKit V1 (ESP32-WROOM-32) + Ai-Thinker RA-02 SX1278 (433.92 MHz)  
**Output Actuation:** Six Discrete Green LEDs (with 2k ohm ballast resistors)  
**Power Supply:** Regulated 5V External Adapter or Bench Power Supply

---

## 1. Six-LED Functional Mapping

| LED Identifier | Target GPIO | Layer | Functional State | Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **LED 1** | GPIO15 | L1 | Layer 1 Active | Steady ON while animal is inside 80m–120m corridor |
| **LED 2** | GPIO2 | L1 | Layer 1 Event | 350ms non-blocking blink on ENTER / EXIT transition |
| **LED 3** | GPIO4 | L2 | Layer 2 Active | Steady ON while animal is inside 30m–80m boundary |
| **LED 4** | GPIO16 | L2 | Layer 2 Event | 350ms non-blocking blink on ENTER / EXIT transition |
| **LED 5** | GPIO17 | L3 | Layer 3 Active | Steady ON while animal is within <30m fence zone |
| **LED 6** | GPIO13 | L3 | Layer 3 Event | 350ms non-blocking strobe on ENTER / EXIT transition |

---

## 2. Sensor Interconnects

| Sensor Net | ESP32 GPIO | Direction | Purpose |
| :--- | :--- | :--- | :--- |
| **HC-SR501 PIR** | GPIO32 | Digital Input | Thermal infrared movement confirmation |
| **Piezoelectric Disc** | GPIO35 | Analog Input (`ADC1_CH7`) | Soil seismic impact transient sampling |
| **INMP441 I2S BCLK** | GPIO25 | Digital Output | Audio serial bit clock |
| **INMP441 I2S WS** | GPIO33 | Digital Output | Audio word select clock |
| **INMP441 I2S SD** | GPIO34 | Digital Input | 24-bit PCM acoustic sample stream |

---

## 3. Operating Principle

1. Listens continuously on 433.92 MHz (Sync Word `0x12`, CRC enabled).
2. On receiving `PW1|CMD|<session>|<seq>|<animal>|<layer>|<transition>`:
   - Validates session and monotonic sequence number.
   - Detects duplicate packets (re-sends ACK without re-triggering event LEDs).
   - Updates target layer's active state and triggers a 350ms event pulse.
   - Responds with `PW1|ACK|<session>|<seq>|OK|<layer>|<state>`.
3. Fully non-blocking loop: radio reception continues uninterrupted while LEDs pulse.


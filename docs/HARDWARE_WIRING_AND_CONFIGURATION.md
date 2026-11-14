# PRW-Wild — Hardware Wiring, Pin Mappings & Configuration Specification

## 1. Specification Overview

This document specifies the exact physical hardware pin mappings, electrical interconnects, power distribution, and communication protocols for the **PRW-Wild Embedded Hardware Suite**.

All pin assignments match the official Espressif user documentation for the **ESP32-S3-DevKitC-1 v1.1** development board:
[Espressif ESP32-S3-DevKitC-1 v1.1 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html).

---

## 2. Master Microcontroller: ESP32-S3-DevKitC-1 v1.1

### 2.1 Hardware Identity & Silicon Variant
- **SoC:** ESP32-S3 (Dual-core Xtensa LX7 @ 240 MHz with vector instructions for edge DSP / TinyML).
- **Module:** ESP32-S3-WROOM-1 (N8R8 variant: 8 MB Quad SPI Flash, 8 MB Octal SPI PSRAM).
- **Board Revision:** v1.1.
- **RF Subsystem:** 2.4 GHz Wi-Fi 802.11 b/g/n (Wi-Fi CSI frame extraction enabled) + Bluetooth 5 (LE).

### 2.2 Critical Revision Difference (v1.1 vs v1.0)
> [!IMPORTANT]
> **RGB LED Pin Assignment:**
> - On **v1.1**, the onboard addressable WS2812 RGB LED data input is routed to **GPIO38**.
> - On older **v1.0** boards, it was routed to **GPIO48**.
>
> **Octal Memory Pin Reservation:**
> - GPIO35, GPIO36, and GPIO37 are internally bonded to the high-speed Octal PSRAM bus (`SPIDQS`, `SPIIO6`, `SPIIO7`).
> - These pins MUST NOT be connected to external sensors.

---

## 3. Header Pinout & Sensor Interconnect Manifest

The DevKitC-1 board provides two 22-pin dual-row headers: **J1 (Left Rail)** and **J3 (Right Rail)**.

```
                    ESP32-S3-DevKitC-1 v1.1
                     +-------------------+
            3V3 [01] |                   | [01] GND
            3V3 [02] |                   | [02] TX / GPIO43
            RST [03] |                   | [03] RX / GPIO44
 GPIO4 (PIR) [04] |                   | [04] GPIO1
GPIO5 (SW420) [05] |   [ESP32-S3-     | [05] GPIO2
          GPIO6 [06] |    WROOM-1]       | [06] GPIO42
          GPIO7 [07] |                   | [07] GPIO41
         GPIO15 [08] |                   | [08] GPIO40
         GPIO16 [09] |                   | [09] GPIO39
         GPIO17 [10] |                   | [10] GPIO38 (WS2812 RGB)
         GPIO18 [11] |                   | [11] GPIO37 (PSRAM RESERVED)
          GPIO8 [12] |                   | [12] GPIO36 (PSRAM RESERVED)
          GPIO3 [13] |                   | [13] GPIO35 (PSRAM RESERVED)
         GPIO46 [14] |                   | [14] GPIO0
GPIO9 (I2S SCK) [15] |                   | [15] GPIO45
GPIO10 (I2S WS) [16] |                   | [16] GPIO48
GPIO11 (I2S SD) [17] |                   | [17] GPIO47
         GPIO12 [18] |                   | [18] GPIO21
         GPIO13 [19] |                   | [19] GPIO14
         GPIO14 [20] |                   | [20] GPIO20
     5V (VBUS) [21] |                   | [21] GPIO19
            GND [22] |                   | [22] GND
                     +-------------------+
```

### 3.1 Interconnect Wiring Table

| Signal Net | Source Device Pin | ESP32 Header | Pin # | Signal Name | Voltage Rail | Purpose in PRW-Wild |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **5V_VBUS_POWER** | 5V DC Supply Rail | Header J1 | Pin 21 | `5V` (VBUS) | 5.0V DC | Powers HC-SR501 PIR sensor and ESP32-CAM |
| **3V3_SYS_POWER** | 3.3V LDO Output | Header J1 | Pin 01 | `3V3` | 3.3V DC | Powers SW-420 vibration sensor module |
| **3V3_MIC_POWER** | 3.3V LDO Output | Header J1 | Pin 02 | `3V3` | 3.3V DC | Dedicated low-noise power for INMP441 mic |
| **COMMON_GND** | System Ground | Header J1 / J3 | J1:22, J3:01 | `GND` | 0.0V | Star-ground return for all peripheral modules |
| **PIR_MOTION_TRIGGER** | HC-SR501 `OUT` | Header J1 | Pin 04 | `GPIO4` | 3.3V Logic | Middle-layer infrared motion detection |
| **VIBRATION_DIGITAL_OUT** | SW-420 `DO` | Header J1 | Pin 05 | `GPIO5` | 3.3V Logic | Seismic / soil vibration trigger for heavy fauna |
| **I2S_AUDIO_SCK** | INMP441 `SCK` | Header J1 | Pin 15 | `GPIO9` | 3.3V Logic | I2S continuous serial bit clock |
| **I2S_AUDIO_WS** | INMP441 `WS` | Header J1 | Pin 16 | `GPIO10` | 3.3V Logic | I2S word select / channel framing clock |
| **I2S_AUDIO_SD** | INMP441 `SD` | Header J1 | Pin 17 | `GPIO11` | 3.3V Logic | I2S 24-bit acoustic sample stream data |
| **LAYER1_RGB_ACTUATOR** | Onboard WS2812 | Internal PCB | Pin 10 | `GPIO38` | 3.3V Logic | Actuates visual CSI perimeter alert |

---

## 4. Communication & Serial Protocols

### 4.1 USB-UART Protocol (ESP32 Node 01)
- **Port Detection:** Scans for CP2102N, CH340, FTDI, or Espressif USB Serial VID/PID.
- **Baud Rate:** `115200` bps, 8 data bits, 1 stop bit, no parity (8-N-1).
- **Command Schema (Host $\rightarrow$ ESP32):**
  ```json
  {
    "device": "ESP32_NODE_01",
    "layer": 1,
    "action": "ON",
    "source": "SIMULATION",
    "pin": 38,
    "color": "CYAN"
  }
  ```
- **Acknowledgment Schema (ESP32 $\rightarrow$ Host):**
  ```json
  {
    "status": "ACK",
    "device": "ESP32_NODE_01",
    "layer": 1,
    "state": "ON",
    "ack_time_ms": 2.4
  }
  ```

### 4.2 Camera HTTP Interface (CAM_01 / ESP32-CAM)
- **IP Address:** `192.168.4.1` (Default AP mode) or assigned DHCP lease on reserve LAN.
- **Endpoints:**
  - `GET /status` — Handshake and battery telemetry.
  - `GET /wake` — Wakes CMOS sensor from deep sleep; returns capture confirmation.
  - `GET /sleep` — Puts camera into low-power standby ($< 6\,\text{mA}$).
  - `GET /capture` — Fetches latest JPEG frame buffer (UXGA / SVGA).

---

## 5. Truthful Status Diagnostics & Troubleshooting

| Visual Symptom | Report in Web UI | Hardware Root Cause | Resolution Action |
| :--- | :--- | :--- | :--- |
| Web UI shows `SIMULATED (NO USB)` | `physical_connected: false` | No CP2102N USB cable connected to PC | Normal for SIL simulation. To test physical board, connect micro-USB to UART port. |
| Layer 3 shows `SIMULATED (STANDBY)` | `physical_connected: false` | ESP32-CAM node offline or ping timeout | Ensure camera Wi-Fi AP is powered and host PC is joined to `PRW-Wild-CAM` network. |
| WS2812 RGB LED doesn't light on v1.0 board | `ACK: OK` but no light | Firmware compiled for v1.1 GPIO38 instead of v1.0 GPIO48 | Recompile firmware with `-DCONFIG_WS2812_PIN=48` if using older v1.0 DevKit. |


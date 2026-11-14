# PRW-Wild — Build, Compilation, and Flashing Guide

**Toolchain:** Arduino CLI 1.4.1  
**Board Core:** `esp32:esp32` version 3.3.12 (Arduino ESP32 Core 3.x)  
**Required Libraries:**
- `LoRa` by Sandeep Mistry (Version 0.8.0)
- `ESP_I2S` (Included with ESP32 Core 3.x)
- `SPI` (Standard Arduino SPI library)

---

## 1. Environment Verification

Ensure Arduino CLI is installed and can locate the ESP32 core:
```powershell
& "C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" core list
```
Expected output:
```text
ID          Installed Latest Name
esp32:esp32 3.3.12    3.3.12 esp32
```

---

## 2. Compile Firmware Targets

### Target 1: ESP32-A Sensor Node
```powershell
cd 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_A_Sensor_Node'

& "C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" compile `
  --fqbn esp32:esp32:esp32 .
```
- **Program Storage:** ~336,028 bytes (25% of 1,310,720 bytes)
- **Dynamic RAM:** ~22,668 bytes (6% of 327,680 bytes)

### Target 2: ESP32-B LED Gateway
```powershell
cd 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_B_LED_Gateway'

& "C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" compile `
  --fqbn esp32:esp32:esp32 .
```
- **Program Storage:** ~301,604 bytes (23% of 1,310,720 bytes)
- **Dynamic RAM:** ~22,316 bytes (6% of 327,680 bytes)

---

## 3. Flashing Commands

### Step A: Flash ESP32-A Sensor Node
1. Connect ESP32-A to USB.
2. Identify assigned port in Windows Device Manager (e.g. `COM6`).
3. Execute upload:
```powershell
& "C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" upload `
  -p COM6 --fqbn esp32:esp32:esp32 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_A_Sensor_Node'
```

### Step B: Flash ESP32-B LED Gateway
1. Connect ESP32-B to laptop via USB.
2. Confirm port `COM7` (Silicon Labs CP210x USB to UART Bridge).
3. Execute upload:
```powershell
& "C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" upload `
  -p COM7 --fqbn esp32:esp32:esp32 'D:\Simulation For DT\prw-wild-digital-twin\firmware\ESP32_B_LED_Gateway'
```

---

## 4. Post-Flashing Verification

Open a serial monitor on COM7 @ 115200 baud to observe startup:
```text
===============================================
PRW-WILD ESP32-B RECEIVER + SIX-LED USB GATEWAY
===============================================
LED map: PIR=32 PIEZO=33 MIC=25 HEARTBEAT=13 LORA=21 ALERT=22
Do not connect LEDs to GPIO34 or GPIO35 (input-only pins).
Operating Mode: AUTO_SENSOR (Default)
RA-02 SX1278: READY
Waiting for ESP32-A sensor telemetry...
```
Upon receiving telemetry packets from ESP32-A:
```text
PW1|TEL_USB|B|7EB233B8|5125|4631399|13|0|0|71816|0|0|0|-64|9.8
SENSOR_STATE: PIR=READY PIEZO=DISABLED MIC=READY OVERALL=NORMAL RSSI=-64 SNR=9.8
ACK_TX: PW1|ACK|B|7EB233B8|5125|OK result=OK
```


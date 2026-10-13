# PRW-Wild Hardware Reference Manual & Verified Pinout Register

This document serves as the verified electrical engineering and hardware specification register for the **PRW-Wild (Predictive RF-Wildlife) Digital Twin & Interactive Hardware Laboratory**.

---

## 1. Primary Reference Board: Espressif ESP32-S3-DevKitC-1 v1.1

### 1.1 Specification & Variant Identification
* **Board Revision:** ESP32-S3-DevKitC-1 **v1.1**
* **Module Variant:** ESP32-S3-WROOM-1 (with PCB antenna)
* **Microcontroller:** Espressif ESP32-S3 (Xtensa® dual-core 32-bit LX7 @ up to 240 MHz, 512 KB SRAM, 384 KB ROM)
* **Wireless Capabilities:** 2.4 GHz Wi-Fi (802.11 b/g/n, 20MHz/40MHz, Channel State Information / CSI capture supported), Bluetooth® 5 (LE)
* **Official User Guide:** [Espressif ESP32-S3-DevKitC-1 v1.1 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html)
* **Official Datasheet:** [ESP32-S3 Datasheet (PDF)](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)
* **ESP-CSI Repository:** [Espressif ESP-CSI Firmware Library](https://github.com/espressif/esp-csi)
* **Verification Status:** `VERIFIED_OFFICIAL_DOCUMENTATION`

### 1.2 Critical Revision Differences (v1.1 vs v1.0)
1. **Onboard Addressable RGB LED:**
   * **v1.1:** The WS2812 / SK6812 RGB LED data input is hardwired to **GPIO38**.
   * **v1.0 (Legacy):** The RGB LED was connected to **GPIO48**.
   * *In this PRW-Wild reference implementation, GPIO38 is strictly reserved for the onboard status RGB indicator, and GPIO48 remains an accessible general I/O header pin on J3 pin 17.*
2. **Octal SPI Memory Bus Pin Restrictions:**
   * On module variants with Octal flash and/or Octal PSRAM (e.g. ESP32-S3-WROOM-1-N8R8), pins **GPIO35, GPIO36, and GPIO37** are utilized internally by the high-speed Octal SPI bus (`SPIIO6`, `SPIIO7`, `SPIDQS`).
   * *These pins must NOT be connected externally to sensors or actuators.*
3. **Strapping Pins:**
   * **GPIO0:** Strapping pin for UART Download mode (wired to BOOT push-button).
   * **GPIO45:** Strapping pin for internal LDO voltage selection (VDD_SPI).
   * **GPIO46:** Input-only strapping pin controlling ROM code printouts.

---

## 2. Complete Header Pinout Register: Headers J1 & J3

### Header J1 (Left Rail, 22 Pins)
| Pin # | Silk / Signal | Type | Default Peripheral | Voltage | PRW-Wild Assignment | Verification Status | Notes |
|:-----:|:-------------:|:----:|:------------------:|:-------:|:-------------------:|:-------------------:|:------|
| 1 | 3V3 | Power | 3.3V Output Rail | 3.3V DC | SW-420 VCC Supply | `VERIFIED` | Max 500mA aggregate |
| 2 | 3V3 | Power | 3.3V Output Rail | 3.3V DC | INMP441 VDD Supply | `VERIFIED` | Auxiliary 3.3V power |
| 3 | RST | Input | CHIP_PU (Reset) | 3.3V | Unused (Tactile SW) | `VERIFIED` | Active-low reset |
| 4 | GPIO4 | I/O | ADC1_CH3, TOUCH4 | 3.3V | **HC-SR501 PIR OUT** | `VERIFIED` | 3.3V TTL active high input |
| 5 | GPIO5 | I/O | ADC1_CH4, TOUCH5 | 3.3V | **SW-420 DO (Vibration)** | `VERIFIED` | Seismic shock digital pulse |
| 6 | GPIO6 | I/O | ADC1_CH5, TOUCH6 | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 7 | GPIO7 | I/O | ADC1_CH6, TOUCH7 | 3.3V | **INMP441 SD (I2S Data)**| `VERIFIED` | I2S0_DATA_IN (24-bit PCM) |
| 8 | GPIO15| I/O | ADC2_CH4, TOUCH14 | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 9 | GPIO16| I/O | ADC2_CH5 | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 10| GPIO17| I/O | ADC2_CH6 | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 11| GPIO18| I/O | ADC2_CH7, USB JTAG D- | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 12| GPIO8 | I/O | ADC1_CH7 | 3.3V | **INMP441 WS (I2S LRCLK)**| `VERIFIED` | I2S0_WS (16 kHz frame sync) |
| 13| GPIO19| I/O | USB D- | 3.3V | Native USB D- | `VERIFIED` | Direct USB OTG port |
| 14| GPIO20| I/O | USB D+ | 3.3V | Native USB D+ | `VERIFIED` | Direct USB OTG port |
| 15| GPIO3 | I/O | ADC1_CH2, TOUCH3 | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 16| GPIO46| Input | Boot Strapping | 3.3V | Unassigned | `VERIFIED` | Input only, strapping |
| 17| GPIO9 | I/O | ADC1_CH8, FSPIHD | 3.3V | **INMP441 SCK (I2S Clock)**| `VERIFIED` | I2S0_BCLK (1.024 MHz) |
| 18| GPIO10| I/O | ADC1_CH9, FSPICS0 | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O / SPI CS |
| 19| GPIO11| I/O | ADC2_CH0, FSPID | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O / SPI MOSI |
| 20| GPIO12| I/O | ADC2_CH1, FSPICLK| 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O / SPI CLK |
| 21| GPIO13| I/O | ADC2_CH2, FSPIQ | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O / SPI MISO |
| 22| GPIO14| I/O | ADC2_CH3, FSPIWP | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O / SPI WP |

### Header J3 (Right Rail, 22 Pins)
| Pin # | Silk / Signal | Type | Default Peripheral | Voltage | PRW-Wild Assignment | Verification Status | Notes |
|:-----:|:-------------:|:----:|:------------------:|:-------:|:-------------------:|:-------------------:|:------|
| 1 | GND | Power | Common Ground | 0.0V | **SW-420 GND** | `VERIFIED` | Common return |
| 2 | GPIO43| I/O | U0TXD | 3.3V | UART0 TX (Debug) | `VERIFIED` | CP2102N UART bridge |
| 3 | GPIO44| I/O | U0RXD | 3.3V | UART0 RX (Debug) | `VERIFIED` | CP2102N UART bridge |
| 4 | GPIO1 | I/O | ADC1_CH0, TOUCH1 | 3.3V | Unassigned (Spare) | `VERIFIED` | High-precision ADC |
| 5 | GPIO2 | I/O | ADC1_CH1, TOUCH2 | 3.3V | Unassigned (Spare) | `VERIFIED` | High-precision ADC |
| 6 | GPIO42| I/O | MTMS (JTAG) | 3.3V | Unassigned | `VERIFIED` | JTAG debugging |
| 7 | GPIO41| I/O | MTDI (JTAG) | 3.3V | Unassigned | `VERIFIED` | JTAG debugging |
| 8 | GPIO40| I/O | MTDO (JTAG) | 3.3V | Unassigned | `VERIFIED` | JTAG debugging |
| 9 | GPIO39| I/O | MTCK (JTAG) | 3.3V | Unassigned | `VERIFIED` | JTAG debugging |
| 10| GPIO38| I/O | RGB LED Data | 3.3V | **Onboard WS2812 RGB** | `VERIFIED` | Hardwired to RGB LED on v1.1 |
| 11| GPIO37| Res. | SPIDQS (Octal Bus) | 3.3V | **RESERVED / DO NOT USE**| `VERIFIED` | Consumed by Octal Flash/PSRAM |
| 12| GPIO36| Res. | SPIIO7 (Octal Bus) | 3.3V | **RESERVED / DO NOT USE**| `VERIFIED` | Consumed by Octal Flash/PSRAM |
| 13| GPIO35| Res. | SPIIO6 (Octal Bus) | 3.3V | **RESERVED / DO NOT USE**| `VERIFIED` | Consumed by Octal Flash/PSRAM |
| 14| GPIO0 | I/O | BOOT Button | 3.3V | Unused (Tactile SW) | `VERIFIED` | Strapping pin, low = flash mode |
| 15| GPIO45| I/O | Strapping Pin | 3.3V | Unassigned | `VERIFIED` | VDD_SPI strapping |
| 16| GPIO47| I/O | SPICLK_P | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O |
| 17| GPIO48| I/O | SPICLK_N | 3.3V | Unassigned (Spare) | `VERIFIED` | General I/O on v1.1 (RGB on v1.0) |
| 18| GPIO21| I/O | RTC_GPIO21 | 3.3V | Unassigned (Spare) | `VERIFIED` | Low-power domain GPIO |
| 19| NC/GND| Power | No Connect / GND | 0.0V | Unassigned | `VERIFIED` | Secondary ground |
| 20| GND | Power | Common Ground | 0.0V | **INMP441 GND & L/R** | `VERIFIED` | Tied low for left audio channel |
| 21| 5V | Power | USB VBUS 5V Rail | 5.0V DC | **HC-SR501 PIR VCC** | `VERIFIED` | Required for onboard 7133 LDO |
| 22| GND | Power | Common Ground | 0.0V | **HC-SR501 PIR GND** | `VERIFIED` | Common return |

---

## 3. Sensor Modules: Electrical Validation & Wiring

### 3.1 HC-SR501 Passive Infrared (PIR) Sensor
* **Datasheet:** [HC-SR501 Technical Specification](https://www.epitran.it/ebayDrive/datasheet/HC-SR501.pdf)
* **Supply Voltage:** 4.5V to 12V DC.
  * *Electrical Note:* The module incorporates an onboard 7133-1 3.3V LDO regulator with an inline protection diode. Supplying 3.3V directly to VCC results in a voltage drop down to ~2.6V, causing oscillator failure or spurious triggering. Therefore, **VCC must be powered from the ESP32-S3 5V rail (J3 Pin 21)**.
* **Output Signal:** 3.3V TTL logic level (derived from the 7133 regulator). Safe for direct input to **GPIO4 (J1 Pin 4)**.

### 3.2 SW-420 Seismic / Vibration Sensor
* **Datasheet:** [SW-420 Sensor Wiki](https://www.waveshare.com/wiki/Vibration_Sensor)
* **Supply Voltage:** 3.3V to 5.0V DC. Connected to **3V3 (J1 Pin 1)** for matched 3.3V logic levels.
* **Comparator:** LM393 dual comparator with onboard 10k potentiometer threshold adjustment.
* **Output Signal:** Digital open-collector with 10k pull-up to VCC. Output pulses HIGH when spring contact opens under mechanical ground shockwaves. Connected to **GPIO5 (J1 Pin 5)**.

### 3.3 INMP441 Omnidirectional Digital I2S Microphone
* **Datasheet:** [InvenSense / TDK INMP441 Datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
* **Supply Voltage:** 1.62V to 3.63V DC (Connected to **3V3 (J1 Pin 2)**).
* **Interface:** Industry standard I2S digital audio bus.
  * **SCK / BCLK:** Serial bit clock -> **GPIO9 (J1 Pin 17)**.
  * **WS / LRCLK:** Word select / frame sync -> **GPIO8 (J1 Pin 12)**.
  * **SD / DOUT:** Serial data output -> **GPIO7 (J1 Pin 7)**.
  * **L/R:** Tied to **GND (J3 Pin 20)** to configure Left channel mono stream.
* *Bandwidth Note:* Captures infrasonic acoustic fundamentals down to ~15 Hz, crucial for African elephant rumbles.

---

## 4. Optical Sensor Node: AI-Thinker ESP32-CAM (Node `CAM_01`)
* **Reference Guide:** [Espressif esp32-camera Pinout Configuration](https://github.com/espressif/esp32-camera/blob/master/examples/camera_example/main/camera_pinout.h)
* **SoC:** ESP32-D0WD (Dual-core LX6) with 4MB external PSRAM.
* **Camera Sensor:** OmniVision OV2640 (2 Megapixel UXGA, 66° FOV).
* **Dedicated Camera Bus:**
  * `D0`: GPIO5 | `D1`: GPIO18 | `D2`: GPIO19 | `D3`: GPIO21 | `D4`: GPIO36 | `D5`: GPIO39 | `D6`: GPIO34 | `D7`: GPIO35
  * `XCLK`: GPIO0 (20 MHz master clock)
  * `PCLK`: GPIO22 (Pixel clock)
  * `VSYNC`: GPIO25 (Vertical sync)
  * `HREF`: GPIO23 (Horizontal reference)
  * `SIOD`: GPIO26 (SCCB Data) | `SIOC`: GPIO27 (SCCB Clock)
  * `PWDN`: GPIO32 (Power down control)
  * `FLASH_LED`: GPIO4 (High-power illumination)
* *Architectural Separation:* The ESP32-CAM is an autonomous optical verification mast, waking up over Wi-Fi only when gated by the PRW-Wild predictive tracker.

---

## 5. Wi-Fi Access Point (`WIFI_AP_01`)
* **Role:** Continuous 802.11n 2.4 GHz OFDM transmitter (Channel 6).
* **Designation:** `REPRESENTATIVE WI-FI ACCESS POINT — NOT A SELECTED PURCHASED SKU`.
* **CSI Physics:** Transmits 100 Hz probe packets. Megafauna traversing the Fresnel zone cause subcarrier-dependent phase rotation and amplitude shadow fading.

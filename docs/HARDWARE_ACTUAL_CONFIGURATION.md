# PRW-Wild — Actual Physical Hardware Configuration Specification

## 1. System Topology Overview
The PRW-Wild prototype hardware configuration differs from the early single-board ESP32-S3 specification by deploying a distributed dual-microcontroller architecture connected over a long-range sub-GHz LoRa radio link:

```
               WORKSTATION (HOST)
                       │ USB Serial (CP2102 @ 115200)
                       ▼
       ┌───────────────────────────────┐
       │   ESP32-A NODE (TRANSMITTER)  │
       │   ESP32 DevKit V1 (WROOM-32)  │
       │   Ai-Thinker RA-02 (SX1278)   │
       └───────────────┬───────────────┘
                       │
                       │ 433.92 MHz LoRa RF Link (SF7, BW 125kHz, CRC)
                       │
                       ▼
       ┌───────────────────────────────┐
       │     ESP32-B NODE (RECEIVER)   │
       │   ESP32 DevKit V1 (WROOM-32)  │
       │   Ai-Thinker RA-02 (SX1278)   │
       └───────┬───────────────┬───────┘
               │               │
               ▼               ▼
     6x Green LED Array   Sensor Suite
     (2kΩ Resistors)     (PIR, Piezo, INMP441)
```

---

## 2. Microcontroller Hardware Specifications

| Component | Node A (Transmitter) | Node B (Receiver) |
| :--- | :--- | :--- |
| **Development Board** | ESP32 DevKit V1 (30-pin) | ESP32 DevKit V1 (30-pin) |
| **Module / Silicon** | ESP32-WROOM-32 (Dual-core Xtensa @ 240 MHz) | ESP32-WROOM-32 (Dual-core Xtensa @ 240 MHz) |
| **Operating Voltage** | 3.3V Logic / 5.0V USB VBUS | 3.3V Logic / 5.0V External DC Supply |
| **Primary Connection** | USB Serial to Host Laptop (`115200` baud) | LoRa Transceiver + 6-LED Array + Sensors |
| **Power Source** | Laptop USB Port via CP2102 Bridge | Regulated 5V / 2A Wall Power Adapter |

---

## 3. Radio Frequency (RF) Configuration

Both nodes use the Ai-Thinker RA-02 module powered by the Semtech SX1278 transceiver:
- **Frequency:** `433.92 MHz` (Within Indian WPC 433.05–434.79 MHz deregulated band).
- **Modulation:** LoRa CSS (Chirp Spread Spectrum).
- **Spreading Factor:** `SF7`.
- **Bandwidth:** `125 kHz`.
- **Coding Rate:** `4/5`.
- **Preamble Length:** `8` symbols.
- **Sync Word:** `0x12` (Private network).
- **CRC:** Enabled (`LoRa.enableCrc()`).
- **Transmit Power:** `PA_OUTPUT_PA_BOOST_PIN`, Level `2` (bench calibrated).

---

## 4. Hardware Pin Mapping

### 4.1 Node A & Node B LoRa Interface (Hardware VSPI)
| Signal Name | ESP32 GPIO | RA-02 Breakout Pin |
| :--- | :--- | :--- |
| SPI SCK | GPIO18 | SCK |
| SPI MISO | GPIO19 | MISO |
| SPI MOSI | GPIO23 | MOSI |
| SPI NSS / CS | GPIO27 | NSS |
| RESET | GPIO14 | RST |
| DIO0 IRQ | GPIO26 | DIO0 |

### 4.2 Node B Output Actuators (Six Discrete Green LEDs)
Each LED is connected in series with a **2 kΩ (2000 Ω)** resistor to ground:
| Output Net | ESP32 GPIO | Layer | Indication Role |
| :--- | :--- | :--- | :--- |
| **LED 1** | GPIO15 | Layer 1 | Outer Perimeter Monitoring Active (Steady ON) |
| **LED 2** | GPIO2 | Layer 1 | Outer Perimeter Event Triggered (350ms Pulse) |
| **LED 3** | GPIO4 | Layer 2 | Middle Boundary Monitoring Active (Steady ON) |
| **LED 4** | GPIO16 | Layer 2 | Middle Boundary Event Triggered (350ms Pulse) |
| **LED 5** | GPIO17 | Layer 3 | Fence Deterrent Armed (Steady ON) |
| **LED 6** | GPIO13 | Layer 3 | Fence Deterrent Actuated / Strobe (350ms Pulse) |

### 4.3 Node B Sensor Interconnects
| Sensor Net | ESP32 GPIO | Direction | Type |
| :--- | :--- | :--- | :--- |
| HC-SR501 PIR | GPIO32 | Digital Input | Motion trigger pulse |
| Piezo Ceramic Disc | GPIO35 | Analog Input (`ADC1_CH7`) | Impact transient (1MΩ load resistor) |
| INMP441 BCLK | GPIO25 | Digital Output | I2S Bit Clock |
| INMP441 WS | GPIO33 | Digital Output | I2S Word Select Clock |
| INMP441 SD | GPIO34 | Digital Input | I2S 24-bit PCM Audio Stream |


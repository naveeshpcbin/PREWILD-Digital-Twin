# PRW-Wild — Hardware Wiring, Pin Assignments, and Electrical Safety

**Document Version:** 2.0.0  
**Target Hardware:** Two ESP32-WROOM-32 DevKit V1 Boards  

---

## 1. ESP32-A Sensor Node Pinout

| Peripheral | Signal | ESP32 Pin | Direction | Electrical Specifications & Protection |
| :--- | :--- | :---: | :---: | :--- |
| **SX1278 LoRa** | SPI SCK | `GPIO 18` | Output | 3.3V Logic SPI Clock |
| **SX1278 LoRa** | SPI MISO | `GPIO 19` | Input | 3.3V Logic SPI Master In |
| **SX1278 LoRa** | SPI MOSI | `GPIO 23` | Output | 3.3V Logic SPI Master Out |
| **SX1278 LoRa** | CS / NSS | `GPIO 27` | Output | Active Low Chip Select |
| **SX1278 LoRa** | RESET | `GPIO 14` | Output | Active Low Reset |
| **SX1278 LoRa** | DIO0 | `GPIO 26` | Input | Interrupt pin for RX/TX done |
| **HC-SR501 PIR** | OUT | `GPIO 32` | Input | Digital 3.3V Output from onboard regulator. 45s warmup filter. |
| **Piezoelectric Disc** | ADC Output | `GPIO 35` | **Input Only** | **ADC1_CH7**. Must be protected via dual Schottky diodes (BAT54S) and divider. |
| **INMP441 Mic** | BCLK | `GPIO 25` | Output | I²S Bit Clock |
| **INMP441 Mic** | WS / LRCLK | `GPIO 33` | Output | I²S Word Select |
| **INMP441 Mic** | SD / DOUT | `GPIO 34` | **Input Only** | I²S Serial Data Out from mic (Left channel, L/R tied to GND) |

> [!WARNING]
> **GPIO 34 and GPIO 35 are strictly input-only** on ESP32-WROOM-32. They have no internal pull-up/pull-down resistors or output driver stages. Never configure them with `pinMode(pin, OUTPUT)`.

---

## 2. Piezoelectric Signal Conditioning & Protection Circuit

Raw, unconditioned piezoelectric ceramic discs produce destructive transient voltage spikes ranging from **$-30\text{ V}$ to $+50\text{ V}$** upon direct mechanical impact, exceeding the ESP32 absolute maximum input rating ($-0.3\text{ V}$ to $+3.6\text{ V}$).

A $1\text{ M}\Omega$ resistor alone is **not sufficient protection**.

### Required Conditioning Circuit:
```text
           Piezo (+) ──┬──────────┬───────────┬───────── GPIO 35 (ADC1_CH7)
                       │          │           │
                     [1MΩ]     [BAT54S]       │
                       │     (D1: to 3.3V) [100nF]
                       │     (D2: to GND)     │
           Piezo (-) ──┴──────────┴───────────┴───────── GND
```
- **Clamping Diodes:** BAT54S low-forward-drop Schottky diode pair clamps voltage between $-0.2\text{ V}$ and $+3.5\text{ V}$.
- **DC Bias Divider:** Optional $470\text{ k}\Omega / 470\text{ k}\Omega$ divider biases the baseline to $1.65\text{ V}$ to capture both positive and negative half-cycles.
- **Fail-Closed Safety Gate:** `PIEZO_CIRCUIT_VERIFIED` in `ESP32_A_Sensor_Node.ino` defaults to `0` (`false`). Bounded ADC sampling is locked out until the circuit is physically verified.

---

## 3. ESP32-B Gateway & Annunciator Pinout

| Indicator | Signal | ESP32 Pin | Ballast Resistor | Function & Behavior |
| :--- | :--- | :---: | :---: | :--- |
| **LED 1** | PIR Active | `GPIO 32` | $2\text{ k}\Omega$ | Illuminates when HC-SR501 detects human/animal motion |
| **LED 2** | Piezo Active | `GPIO 33` | $2\text{ k}\Omega$ | Illuminates when seismic vibration P2P exceeds threshold |
| **LED 3** | Mic Active | `GPIO 25` | $2\text{ k}\Omega$ | Illuminates when acoustic sound RMS exceeds threshold |
| **LED 4** | Node Heartbeat | `GPIO 13` | $2\text{ k}\Omega$ | Continuous solid illumination while Node A is alive ($\le 2200\text{ ms}$) |
| **LED 5** | LoRa RX Pulse | `GPIO 21` | $2\text{ k}\Omega$ | Brief $120\text{ ms}$ pulse upon receiving each valid LoRa frame |
| **LED 6** | Combined Alert | `GPIO 22` | $2\text{ k}\Omega$ | Illuminates when `PIR \|\| Piezo \|\| Mic` is active |

Each LED is connected in active-high configuration:  
`ESP32 GPIO ─── [2 kΩ Resistor] ─── [Anode (+) LED Cathode (-)] ─── GND`

The $2\text{ k}\Omega$ ballast resistor restricts current to $\approx 0.8\text{ mA}$ per LED, ensuring total current draw across all 6 LEDs remains well below the ESP32 VDD limit ($< 10\text{ mA}$).


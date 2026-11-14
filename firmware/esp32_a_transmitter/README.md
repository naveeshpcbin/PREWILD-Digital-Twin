# ESP32-A Event Transmitter Firmware

**Role:** Master Hardware Link for PRW-Wild Digital Twin  
**Target Hardware:** ESP32 DevKit V1 (ESP32-WROOM-32) + Ai-Thinker RA-02 SX1278 (433.92 MHz)  
**Host Interface:** USB-UART Bridge (`115200` bps, 8-N-1)

---

## 1. Operating Modes

### Mode A: `HOST_CONTROL` (Default)
In this mode, ESP32-A listens to the Host Python backend over USB Serial:
1. Python writes: `PW1|CMD|<sessionID>|<seq>|<animalID>|<layer>|<transition>\n`
2. ESP32-A transmits the packet over 433.92 MHz LoRa using SF7, BW 125 kHz, and CRC.
3. ESP32-A waits for matching `PW1|ACK|<sessionID>|<seq>|...` from ESP32-B.
4. ESP32-A forwards the ACK back to Python: `PW1|ACK|<sessionID>|<seq>|OK|<layer>|<state>\n` along with `PW1|RF_DIAG|...` reporting RSSI and SNR.

### Mode B: `STANDALONE_DEMO`
Autonomous 6-step loop demonstration (`L1 ENTER` $\rightarrow$ `L2 ENTER` $\rightarrow$ `L3 ENTER` $\rightarrow$ `L3 EXIT` $\rightarrow$ `L2 EXIT` $\rightarrow$ `L1 EXIT`) for independent bench validation without host connection.
Switchable via serial command: `PW1|SET_MODE|STANDALONE\n`.

---

## 2. Pin Configuration

| Pin Function | ESP32 GPIO | RA-02 Pin |
| :--- | :--- | :--- |
| SPI SCK | GPIO18 | SCK |
| SPI MISO | GPIO19 | MISO |
| SPI MOSI | GPIO23 | MOSI |
| SPI NSS / CS | GPIO27 | NSS |
| Hardware RESET | GPIO14 | RST |
| DIO0 IRQ | GPIO26 | DIO0 |
| Ground | GND | GND |
| Power | 3.3V | 3.3V |


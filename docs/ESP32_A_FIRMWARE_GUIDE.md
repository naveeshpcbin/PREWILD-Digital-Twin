# ESP32-A Transmitter Firmware Operational Guide

## 1. Overview
ESP32-A serves as the master communication bridge between the Python Digital Twin host application and the remote ESP32-B actuator node. It operates in two software-switchable modes:
- **`MODE_HOST_CONTROL`:** Accepts live simulation commands from the Python backend over USB Serial and translates them into LoRa packets.
- **`MODE_STANDALONE_DEMO`:** Executes an autonomous 6-step wildlife demonstration cycle for independent bench validation.

---

## 2. Compilation and Flashing Instructions

1. Open Arduino IDE (located at `C:\Program Files\Arduino IDE\Arduino IDE.exe`).
2. Open sketch:  
   `D:\Simulation For DT\prw-wild-digital-twin\firmware\esp32_a_transmitter\esp32_a_transmitter.ino`
3. Under **Tools > Board**, select: **DOIT ESP32 DEVKIT V1** (or ESP32 Dev Module).
4. Under **Tools > Port**, select the active USB Serial port (e.g., `COM7`).
5. Ensure the Sandeep Mistry `LoRa` library (v0.8.0) is selected in the Library Manager.
6. Click **Upload**.

---

## 3. Serial Interface Protocol (115200 Baud)

### Input Commands (Host to ESP32-A):
- `PW1|PING\n` $\rightarrow$ Responds with `PW1|PONG|MODE|SESSION|VERSION\n`.
- `PW1|SET_MODE|HOST_CONTROL\n` $\rightarrow$ Switches to master simulation link.
- `PW1|SET_MODE|STANDALONE\n` $\rightarrow$ Switches to autonomous bench test loop.
- `PW1|CMD|<session>|<seq>|<animal>|<layer>|<transition>\n` $\rightarrow$ Dispatches LoRa command and waits for ACK.

### Output Responses (ESP32-A to Host):
- `PW1|TX_SENT|<session>|<seq>|ATTEMPT_X\n` $\rightarrow$ Confirms RF packet dispatch.
- `PW1|ACK|<session>|<seq>|OK|<layer>|<state>\n` $\rightarrow$ Forwards confirmed ACK from ESP32-B.
- `PW1|RF_DIAG|<session>|<seq>|RSSI_<val>|SNR_<val>\n` $\rightarrow$ Reports link metrics.
- `PW1|ACK|<session>|<seq>|ERR_TIMEOUT|<layer>|TIMEOUT\n` $\rightarrow$ Returned after 3 failed retries.


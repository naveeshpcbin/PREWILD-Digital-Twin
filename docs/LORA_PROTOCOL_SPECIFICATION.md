# PRW-Wild — Unified PW1 Communication Protocol Specification

**Protocol Version:** 1.0.0  
**Transmission Media:** USB-Serial (Host $\leftrightarrow$ ESP32-A) and 433.92 MHz LoRa (ESP32-A $\leftrightarrow$ ESP32-B)  
**Encoding:** ASCII Delimited (`|`), Newline-Terminated (`\n`)

---

## 1. Frame Grammar

### 1.1 Command Packet (`CMD`)
```text
PW1|CMD|<sessionID>|<sequence>|<animalID>|<layer>|<transition>
```
- `<sessionID>`: 8-character hexadecimal session identifier.
- `<sequence>`: Monotonically increasing unsigned 32-bit integer ($1, 2, 3, \dots$).
- `<animalID>`: Unique identifier of animal entity (e.g., `ELEPHANT_01`, `SYSTEM`).
- `<layer>`: Target detection zone (`L1`, `L2`, `L3`, `ALL`).
- `<transition>`: State transition (`ENTER`, `EXIT`, `ON`, `OFF`, `STROBE`).

### 1.2 Acknowledgement Packet (`ACK`)
```text
PW1|ACK|<sessionID>|<sequence>|<status>|<layer>|<state>
```
- `<status>`: Execution status (`OK`, `ERR_TIMEOUT`, `ERR_BAD_SYNTAX`, `ERR_INVALID_LAYER`).
- `<layer>`: Echo of target layer (`L1`, `L2`, `L3`, `ALL`).
- `<state>`: Confirmed state (`ACTIVE`, `INACTIVE`, `ALL_OFF`, `TIMEOUT`).

### 1.3 RF Diagnostics Packet (`RF_DIAG`)
```text
PW1|RF_DIAG|<sessionID>|<sequence>|RSSI_<value>|SNR_<value>
```
Transmitted by ESP32-A to Host Serial after receiving a valid LoRa ACK, reporting actual RF link measurements.

---

## 2. Invariant Wildlife Demonstration Sequence

During standard approach and crossing scenarios, the sequence strictly follows:

1. `PW1|CMD|<sess>|1|ELEPHANT_01|L1|ENTER` $\rightarrow$ `PW1|ACK|<sess>|1|OK|L1|ACTIVE`
2. `PW1|CMD|<sess>|2|ELEPHANT_01|L2|ENTER` $\rightarrow$ `PW1|ACK|<sess>|2|OK|L2|ACTIVE`
3. `PW1|CMD|<sess>|3|ELEPHANT_01|L3|ENTER` $\rightarrow$ `PW1|ACK|<sess>|3|OK|L3|ACTIVE`
4. `PW1|CMD|<sess>|4|ELEPHANT_01|L3|EXIT`  $\rightarrow$ `PW1|ACK|<sess>|4|OK|L3|INACTIVE`
5. `PW1|CMD|<sess>|5|ELEPHANT_01|L2|EXIT`  $\rightarrow$ `PW1|ACK|<sess>|5|OK|L2|INACTIVE`
6. `PW1|CMD|<sess>|6|ELEPHANT_01|L1|EXIT`  $\rightarrow$ `PW1|ACK|<sess>|6|OK|L1|INACTIVE`

---

## 3. Idempotency and Deduplication
1. A transaction key is formed by `(sessionID, sequence)`.
2. ESP32-B tracks the last successfully processed transaction.
3. If an identical packet arrives:
   - Event LED pulse is **not** re-triggered.
   - Current layer state is preserved.
   - Matching ACK is retransmitted immediately.


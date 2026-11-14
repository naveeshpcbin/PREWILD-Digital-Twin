# PRW-Wild — Software-Hardware Integration Architecture Specification

## 1. System Architecture Principles
The PRW-Wild digital twin architecture is **simulation-authoritative**:
1. **Virtual Motion Drives Hardware:** Real-world deterrent LEDs and alarm outputs are controlled directly by virtual wildlife kinematics simulated in the digital twin.
2. **Deterministic Edge Triggers:** Commands are dispatched solely upon discrete layer transition events (`L1 ENTER`, `L2 ENTER`, `L3 ENTER`, `L3 EXIT`, `L2 EXIT`, `L1 EXIT`) rather than continuous per-frame polling.
3. **Closed-Loop Acknowledgement:** Physical state changes are only confirmed on the UI dashboard after receiving an explicit `PW1|ACK` frame returned by ESP32-B across the LoRa link.

---

## 2. End-to-End Dataflow Chain

```
┌────────────────────────────────────────────────────────┐
│               THREE.JS 3D DIGITAL TWIN                 │
│  • Asian Elephant Kinematics Along Spline Trajectory   │
│  • Layer Envelopes: L1 (45-100m), L2 (70-100m), L3 (85-100m)
│  • Edge-triggered transition detector:                 │
│    checkSimulationLayerTransitions(x, t, animalId)     │
└───────────────────────────┬────────────────────────────┘
                            │ POST /api/hardware/event
                            ▼
┌────────────────────────────────────────────────────────┐
│            PYTHON WEB SERVER & REST API                │
│  • Validates payload and dispatches to HardwareManager │
│  • Enforces operating mode constraints                │
└───────────────────────────┬────────────────────────────┘
                            │ HardwareManager.process_event()
                            ▼
┌────────────────────────────────────────────────────────┐
│             LORA SERIAL BRIDGE (PYTHON)                │
│  • Assigns unique (sessionID, sequenceNumber) key      │
│  • Transmits frame: PW1|CMD|<session>|<seq>|<A>|<L>|<T>│
│  • Asynchronous reader thread awaits matching ACK      │
└───────────────────────────┬────────────────────────────┘
                            │ USB Serial (115200 baud)
                            ▼
┌────────────────────────────────────────────────────────┐
│              ESP32-A TRANSMITTER NODE                  │
│  • Parses USB Serial command stream                    │
│  • Transmits over LoRa 433.92 MHz with CRC             │
│  • Awaits matching ACK from ESP32-B (2.2s timeout)     │
└───────────────────────────┬────────────────────────────┘
                            │ 433.92 MHz CSS Chirp (~67ms ToA)
                            ▼
┌────────────────────────────────────────────────────────┐
│               ESP32-B RECEIVER NODE                    │
│  • Validates packet integrity, session, and sequence   │
│  • Idempotency check: deduplicates retransmissions     │
│  • Actuates 6-LED Array via GPIO outputs               │
│  • Transmits ACK: PW1|ACK|<session>|<seq>|OK|<L>|<S>   │
└───────────────────────────┬────────────────────────────┘
                            │ 433.92 MHz ACK Chirp (~52ms ToA)
                            ▼
┌────────────────────────────────────────────────────────┐
│              ESP32-A RECEIVES & FORWARDS               │
│  • Serial Print: PW1|ACK|<session>|<seq>|OK|<L>|<S>    │
│  • Serial Print: PW1|RF_DIAG|... (RSSI & SNR)          │
└───────────────────────────┬────────────────────────────┘
                            │ Serial Read
                            ▼
┌────────────────────────────────────────────────────────┐
│             LORA SERIAL BRIDGE (HOST)                  │
│  • Matches sequence, unblocks waiting thread           │
│  • Records round-trip latency, RSSI, and SNR           │
│  • Updates HardwareManager status dictionary           │
└───────────────────────────┬────────────────────────────┘
                            │ GET /api/hardware/status
                            ▼
┌────────────────────────────────────────────────────────┐
│               BROWSER DASHBOARD & HUD                  │
│  • Six-LED Visualizer illuminates active/pulse bulbs   │
│  • Latency & RF Link diagnostics updated in real-time  │
│  • Live hardware telemetry log records transaction     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Operating Modes and Precedence

### 3.1 `SIMULATION_ONLY` (Default SIL Mode)
- Real hardware outputs disarmed.
- Digital twin simulation runs unrestricted.
- Commands return `SIMULATED_FALLBACK` acknowledgements.
- Zero radio transmissions.

### 3.2 `HARDWARE_TEST` (Manual Workbench Bench Mode)
- Operator independently toggles Layer 1, Layer 2, and Layer 3 outputs.
- Commands dispatch through the real Python $\rightarrow$ USB $\rightarrow$ LoRa chain.
- Operates independently of virtual animal movement.

### 3.3 `AUTO_HARDWARE_CONTROL` (Integrated Master Mode)
- Live virtual wildlife movement generates edge-triggered transition events.
- Physical LEDs actuate dynamically as the animal crosses spatial boundaries.
- Manual overrides take precedence: if an operator explicitly overrides a layer, automatic commands for that layer are suppressed until reset.

### 3.4 Emergency All-Off
- Overrides all active operations.
- Dispatches `PW1|CMD|<session>|<seq>|SYSTEM|ALL|OFF`.
- De-energizes all 6 LED outputs across both physical and virtual domains.


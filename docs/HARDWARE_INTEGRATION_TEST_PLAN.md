# PRW-Wild — Hardware Integration Test Plan

## 1. Test Scope and Acceptance Targets
This plan defines the end-to-end verification procedures for the integrated PRW-Wild Digital Twin hardware-software suite, spanning unit tests, software-in-the-loop (SIL) virtualization, and physical hardware loopback over LoRa.

---

## 2. Test Phases and Test Cases

### Phase 1: Software Unit & Regression Tests (Automated)
- **TC-01:** Full Pytest regression baseline (116 passing tests).
- **TC-02:** LoRa serial bridge frame validation and sequence monotonicity.
- **TC-03:** Disconnected SIL fallback and truthful error reporting.

### Phase 2: Hardware Loopback Verification (Manual Bench Execution)
- **TC-04: Port Enumeration & Identity Check**
  - Verify ESP32-A is connected on designated COM port.
  - Query ping endpoint: verify `PW1|PONG|HOST_CONTROL` response.
- **TC-05: Manual Layer Actuation**
  - Toggle Layer 1 ON $\rightarrow$ Verify Node B LED 1 (Active) steady ON and LED 2 (Event) 350ms pulse.
  - Toggle Layer 2 ON $\rightarrow$ Verify Node B LED 3 steady ON and LED 4 pulse.
  - Toggle Layer 3 ON $\rightarrow$ Verify Node B LED 5 steady ON and LED 6 pulse.
  - Trigger Emergency All-Off $\rightarrow$ Verify all 6 LEDs de-energize instantly.

### Phase 3: Simulation-Authoritative Invariant Sequence
- **TC-06: Automatic Digital Twin Scenario Execution**
  - Switch system mode to `AUTO_HARDWARE_CONTROL`.
  - Run `approach_crossing` scenario.
  - Observe elephant advancing along trajectory towards fence ($X = 100\text{m}$):
    1. Elephant crosses $X = 45\text{m}$ $\rightarrow$ Dispatches `L1 ENTER` $\rightarrow$ Physical LED 1 ON.
    2. Elephant crosses $X = 70\text{m}$ $\rightarrow$ Dispatches `L2 ENTER` $\rightarrow$ Physical LED 3 ON.
    3. Elephant crosses $X = 85\text{m}$ $\rightarrow$ Dispatches `L3 ENTER` $\rightarrow$ Physical LED 5 ON.
    4. Elephant retreats $X < 85\text{m}$ $\rightarrow$ Dispatches `L3 EXIT` $\rightarrow$ Physical LED 5 OFF.
    5. Elephant retreats $X < 70\text{m}$ $\rightarrow$ Dispatches `L2 EXIT` $\rightarrow$ Physical LED 3 OFF.
    6. Elephant retreats $X < 45\text{m}$ $\rightarrow$ Dispatches `L1 EXIT` $\rightarrow$ Physical LED 1 OFF.
  - Verify every transition produces a confirmed `PW1|ACK` frame and updates HUD latency metrics.


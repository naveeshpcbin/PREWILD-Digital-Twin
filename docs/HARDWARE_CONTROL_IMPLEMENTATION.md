# PRW-Wild — Physical Hardware Control Implementation Report

## 1. Executive Summary

This report documents the architectural design, software implementation, and automated verification of the **PRW-Wild Physical Hardware Control Subsystem**.

The subsystem realizes the mandatory **Simulation-Driven Hardware Control Prototype**, where virtual wildlife movement in the digital twin acts as the master event controller that commands real-world embedded physical outputs across the **fixed three-layer perimeter architecture**.

All implementations adhere strictly to the principle of **Truthful Connection Reporting**: under no circumstances does the application report active physical communication when devices are disconnected from the host.

---

## 2. Fixed Three-Layer Architecture & Actuation Hierarchy

The three detection layers are topologically ordered from the western deep forest towards the eastern farmland fence at $X = 100\,\text{m}$:

| Layer | Ring / Zone | Spatial Boundary ($X$) | Hardware Target Device | Actuation Output / Signal | Role in PRW-Wild |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Layer 1** | **Outer Layer** | $45.0\,\text{m} \le X < 70.0\,\text{m}$ | **ESP32-S3-DevKitC-1 v1.1** | GPIO38 / WS2812 RGB LED (Cyan / Black) | Wi-Fi CSI RF perimeter presence alert & precursor corroboration |
| **Layer 2** | **Middle Layer** | $70.0\,\text{m} \le X < 85.0\,\text{m}$ | **STATION_SENSOR_NET_01** | Relay CH1 / Sensor Bus Indicator (Amber / Off) | Secondary multi-sensor network corroboration (PIR, acoustic, vibration) |
| **Layer 3** | **Inner Layer** | $85.0\,\text{m} \le X \le 100.0\,\text{m}$ | **CAM_01 (ESP32-CAM OV2640)** | Wake & Frame Capture Trigger (Purple / Standby) | Optical visual confirmation & AI bounding-box tracking before fence line |

---

## 3. Strict Operating Modes

The hardware control engine (`HardwareManager`) enforces three mutually exclusive operating modes:

### 3.1 Mode 1: `SIMULATION_ONLY` (Default Safe State)
- **Behavior:** Physical outputs are strictly disarmed.
- **Function:** Virtual animals move through the 3D twin; ground envelopes visualize detection boundaries; simulated ACKs are returned for web controls with `physical_executed: false`.
- **Purpose:** Safe software-in-the-loop (SIL) evaluation without requiring connected bench hardware.

### 3.2 Mode 2: `HARDWARE_TEST` (Manual Bench Testing Mode)
- **Behavior:** The operator has direct manual command over each layer from the web interface.
- **Controls:** Independent `[ON]` / `[OFF]` toggle buttons for Layer 1, Layer 2, and Layer 3.
- **Telemetry:** Round-trip command acknowledgment latency is measured and reported in milliseconds (`ACK: xx.x ms`).
- **Safety:** Truthful connection status indicates whether the command executed over real serial/HTTP or simulated fallback.

### 3.3 Mode 3: `AUTO_HARDWARE_CONTROL` (Simulation-Driven Dynamic Mode)
- **Behavior:** The Python wildlife simulation engine dynamically commands hardware outputs based on live animal coordinates.
- **Event Flow:**
  1. Virtual animal enters Layer 1 ($X \ge 45\,\text{m}$) $\rightarrow$ Layer 1 output triggers **ON**.
  2. Animal enters Layer 2 ($X \ge 70\,\text{m}$) $\rightarrow$ Layer 2 output triggers **ON**.
  3. Animal enters Layer 3 ($X \ge 85\,\text{m}$) $\rightarrow$ Layer 3 camera wakes and triggers **ON**.
  4. Animal retreats / exits Layer 3 ($X < 85\,\text{m}$) $\rightarrow$ Layer 3 returns to **STANDBY/OFF**.
  5. Animal exits Layer 2 ($X < 70\,\text{m}$) $\rightarrow$ Layer 2 turns **OFF**.
  6. Animal exits Layer 1 ($X < 45\,\text{m}$) $\rightarrow$ Layer 1 turns **OFF**.

---

## 4. Multi-Animal Occupancy Tracking & Debouncing

In an open-world ecosystem with 75 autonomous animals across 16 species, multiple animals can occupy a detection zone simultaneously.

To prevent rapid oscillation and premature deactivation:
1. **Debounced Zone Counting:** The simulation engine computes real-time occupancy counts $C_1, C_2, C_3$ for each layer during every tick:
   $$\text{Layer 1 Count} = \sum_{a \in \text{Agents}} \mathbb{I}(45.0 \le X_a < 70.0)$$
   $$\text{Layer 2 Count} = \sum_{a \in \text{Agents}} \mathbb{I}(70.0 \le X_a < 85.0)$$
   $$\text{Layer 3 Count} = \sum_{a \in \text{Agents}} \mathbb{I}(X_a \ge 85.0)$$
2. **Hysteresis Rule:**
   - If $C_k > 0$ and $\text{State}_k == \text{OFF} \implies \text{Actuate } \text{ON}$.
   - If $C_k == 0$ and $\text{State}_k == \text{ON} \implies \text{Actuate } \text{OFF}$.
   - If $C_k$ decreases but remains $> 0 \implies \text{Remain } \text{ON}$ (debounced).

---

## 5. Emergency All-Off Safety Mechanism

The subsystem implements a fail-safe **Emergency All-Off** routine (`emergency_all_off()`):
- Accessible via the prominent **🚨 EMERGENCY ALL-OFF** button on both the modal workbench and the tactical 3D quickbar.
- Immediately issues `OFF` commands to Layer 1, Layer 2, and Layer 3 adapters.
- Clears all manual overrides and pending simulation activations.
- Logs a critical emergency record to the hardware telemetry stream.

---

## 6. REST API Reference

The web backend in `src/prw_wild/web/server.py` exposes the following endpoints:

### `GET /api/hardware/status`
Returns full hardware system status dictionary:
```json
{
  "operating_mode": "SIMULATION_ONLY",
  "layers": {
    "layer_1": {
      "device_id": "ESP32_NODE_01",
      "name": "ESP32-S3-DevKitC-1 v1.1 (Layer 1 CSI)",
      "layer": 1,
      "state": "OFF",
      "connection_status": "DISCONNECTED",
      "physical_connected": false,
      "port_or_endpoint": null,
      "last_error": "No physical ESP32 USB-UART bridge detected on system ports"
    },
    "layer_2": { ... },
    "layer_3": { ... }
  },
  "manual_overrides": { "1": null, "2": null, "3": null },
  "recent_commands": [ ... ]
}
```

### `POST /api/hardware/mode`
Switches operating mode (`{"mode": "HARDWARE_TEST"}`).

### `POST /api/hardware/command`
Sends manual toggle command (`{"layer": 1, "action": "ON"}`).

### `POST /api/hardware/emergency_stop`
Instantly deactivates all 3 layers.

---

## 7. Web UI Implementation

The user interface provides two synchronized control surfaces:

1. **Tactical Quickbar Overlay (`#tacticalHwQuickbar`):**
   - Positioned in the top-right of the 3D twin canvas.
   - Shows current mode badge (`MODE: SIM ONLY`, `BENCH TEST`, `AUTO CONTROL`).
   - Quick one-click toggle buttons for `L1 [ON/OFF]`, `L2 [ON/OFF]`, `L3 [ON/OFF]`.
   - `🚨 ALL-OFF` emergency button.
   - `🛠️ BENCH` button to open the full modal workbench.

2. **Full Hardware Control Bench (`#hardwareControlContainer`):**
   - Embedded inside Mode E: Hardware Lab modal.
   - Mode selector with 3 styled cards (`SIMULATION ONLY`, `HARDWARE TEST`, `AUTO HARDWARE CONTROL`).
   - 3 Layer Actuator Cards with glowing state rings, truth connection pills (`SIMULATED (NO USB)` vs `CONNECTED`), latency displays, and manual `[ACTIVATE]` / `[DEACTIVATE]` buttons.
   - Full-width Emergency All-Off button.
   - Live Command Telemetry Terminal displaying real-time ACK logs.

3. **3D Visual Ground Feedback:**
   - Layer 1 ground envelope opacity pulses from $0.08 \rightarrow 0.32$ (Cyan) when active.
   - Layer 2 ground envelope opacity pulses from $0.09 \rightarrow 0.35$ (Amber) when active.
   - Layer 3 ground envelope opacity pulses from $0.12 \rightarrow 0.42$ (Purple) when active.
   - 3D Wi-Fi router packet LEDs and Camera mast beacons illuminate synchronously.

---

## 8. Automated Verification Results

All 7 integration tests in `tests/test_hardware_control.py` pass cleanly in **0.15s**:

| Test Case | Scenario Tested | Result |
| :--- | :--- | :--- |
| `test_hardware_manager_initialization` | Default startup in `SIMULATION_ONLY` with all layers OFF | **PASSED** |
| `test_truthful_connection_status` | Accurate `DISCONNECTED` reporting when host has no hardware | **PASSED** |
| `test_operating_mode_transitions` | Mode switching between `SIM_ONLY`, `TEST`, and `AUTO` | **PASSED** |
| `test_manual_commands_and_simulated_acks` | Manual actuation, ACK latency, and history logging | **PASSED** |
| `test_emergency_all_off` | Instantaneous shutdown of all outputs & override reset | **PASSED** |
| `test_simulation_driven_invariant_event_sequence` | 6-step event sequence: L1 $\rightarrow$ L2 $\rightarrow$ L3 $\rightarrow$ Exit L3 $\rightarrow$ Exit L2 $\rightarrow$ Exit L1 | **PASSED** |
| `test_multi_animal_occupancy_debouncing` | Debounced zone occupancy across multiple animals | **PASSED** |

Browser verification via headless Chrome verified 0 console errors and generated photographic proof:
- `suite_04_three_layer_ground_envelopes.png`: Visual ground envelopes active with tactical quickbar.
- `suite_05_hardware_workbench_bench_test_mode.png`: Control bench modal in `HARDWARE TEST` mode.
- `suite_06_hardware_all_layers_active_telemetry.png`: All 3 layers active with glowing indicators and live telemetry log.
- `suite_07_emergency_all_off_executed.png`: Immediate shutdown upon emergency stop.


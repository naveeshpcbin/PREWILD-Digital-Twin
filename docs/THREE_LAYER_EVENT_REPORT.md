# PRW-Wild — Three-Layer Sensing Architecture & Event Sequence Report

## 1. Fixed Architecture Specification

The PRW-Wild early-warning and deterrence infrastructure operates strictly on a **fixed three-layer physical detection topology** arranged from the deep forest corridor towards human settlements and agricultural farmland:

```
[ DEEP FOREST ]
      │
      ▼  (Wildlife approaches boundary)
┌────────────────────────────────────────────────────────┐
│ LAYER 1 — OUTER PERIMETER: Wi-Fi CSI / ESP32 Nodes     │  (X: 45.0m to 70.0m)
│ • Subcarrier CSI amplitude/phase disturbance           │
│ • Long-range non-line-of-sight early warning           │
│ • RF pulses & perimeter mesh beacons                   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼  (Wildlife continues intrusion)
┌────────────────────────────────────────────────────────┐
│ LAYER 2 — MIDDLE PERIMETER: Physical Sensor Network    │  (X: 70.0m to 85.0m)
│ • Passive Infrared (PIR) dual-element pyroelectric     │
│ • Geophone seismic ground vibration probes             │
│ • Acoustic tripwire microphone arrays                  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼  (Wildlife breaches crop boundary)
┌────────────────────────────────────────────────────────┐
│ LAYER 3 — INNER PERIMETER: Physical Surveillance Camera│  (X: 85.0m to 100.0m)
│ • PTZ Optical Surveillance Camera CAM_01              │
│ • Real-time AI species verification (YOLO / ONNX)      │
│ • Boundary intercept vector & deterrence trigger       │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
[ AGRICULTURAL FARMLAND / HUMAN SETTLEMENT ]
```

---

## 2. Inviolable Event Sequence Verification

The physical movement of wildlife through the digital twin triggers detection events in strict chronological order:

```
  [1] ENTER L1  ──►  [2] ENTER L2  ──►  [3] ENTER L3
                                           │
  [6] EXIT L1   ◄──  [5] EXIT L2   ◄──  [4] EXIT L3
```

### Transition State Machine

| Sequence Step | Event Name | Detection Layer | Coordinate Trigger | System Action Triggered | Hardware State |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `ANIMAL_ENTER_LAYER_1` | Layer 1 (CSI / ESP32) | $X \ge 45.0\text{ m}$ | Early warning RF pulse; amber ground envelope activates; HUD L1 badge `ACTIVE`. | ESP32 CSI telemetry active |
| **02** | `ANIMAL_ENTER_LAYER_2` | Layer 2 (Sensor Net) | $X \ge 70.0\text{ m}$ | Seismic & acoustic tripwires tripped; magenta ground envelope activates; L2 badge `ACTIVE`. | Sensor network corroborating |
| **03** | `ANIMAL_ENTER_LAYER_3` | Layer 3 (Camera POV) | $X \ge 85.0\text{ m}$ | PTZ CAM_01 locks target; AI bounding box overlays target; deterrence ready. | Camera CAM_01 active tracking |
| **04** | `ANIMAL_EXIT_LAYER_3` | Layer 3 (Camera POV) | $X < 85.0\text{ m}$ | Camera returns to wide patrol sweep; L3 badge returns to `STANDBY`. | Camera CAM_01 standby |
| **05** | `ANIMAL_EXIT_LAYER_2` | Layer 2 (Sensor Net) | $X < 70.0\text{ m}$ | Sensor tripwires clear; L2 badge returns to `IDLE`. | Sensor network idle |
| **06** | `ANIMAL_EXIT_LAYER_1` | Layer 1 (CSI / ESP32) | $X < 45.0\text{ m}$ | Full corridor clear; L1 badge returns to `IDLE`; deterrence disarmed. | ESP32 CSI baseline monitoring |

---

## 3. Digital Twin 3D Visual Corroboration

In `src/prw_wild/web/static/app.js`, the three-layer topology is reflected across the entire user interface:
1. **Volumetric Ground Envelopes:**
   - **Layer 1 Envelope:** Shimmering cyan-amber mesh band covering corridor $X \in [45, 70\text{m}]$. Opacity elevates to $0.22$ on intrusion.
   - **Layer 2 Envelope:** Magenta sensor perimeter band covering $X \in [70, 85\text{m}]$. Opacity elevates to $0.26$ on intrusion.
   - **Layer 3 Envelope:** High-visibility hazard crimson band covering $X \in [85, 100\text{m}]$ along agricultural border. Opacity elevates to $0.32$ with targeting crosshairs.
2. **Tactical Quickbar Overlay (`#tacticalHwQuickbar`):**
   - Live toggles for `L1 CSI`, `L2 SENS`, and `L3 CAM`.
   - Real-time indicator LEDs displaying active status.
   - One-click `EMERGENCY HALT` and `BENCH` modal triggers.
3. **Multi-Animal Occupancy Aggregation:**
   - Occupancy counts across all 75 autonomous agents are evaluated continuously:
   $$N_{L1} = \sum [45 \le X_i < 70], \quad N_{L2} = \sum [70 \le X_i < 85], \quad N_{L3} = \sum [85 \le X_i < 100]$$

---

## 4. Hardware Actuation Coupling

In `AUTO_HARDWARE_CONTROL` mode, the simulation engine acts as the master event controller:
- Virtual animal entering Layer 1 issues commanded state `ON` to Layer 1.
- Virtual animal entering Layer 2 issues commanded state `ON` to Layer 2.
- Virtual animal entering Layer 3 issues commanded state `ON` to Layer 3.
- In `SIMULATION_ONLY` mode, hardware outputs remain safely disarmed (SIL virtualization).
- Manual override commands coexist without desynchronizing the automated event monitor.


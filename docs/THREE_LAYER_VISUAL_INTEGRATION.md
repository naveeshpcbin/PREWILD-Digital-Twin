# PRW-Wild Wildlife Digital Twin: Three-Layer Sensing & Detection Integration

**Project:** PRW-Wild — AAA-Quality Immersive Wildlife Digital Twin  
**Document Revision:** 2.0.0 (Production Master)  
**Standard:** Antigravity Fixed Multi-Tier Physical Architecture Specification  
**Architecture Classification:** Three-Tier Early Warning & Visual Confirmation System  

---

## 1. Strictly Fixed Architecture Specification

The PRW-Wild physical defense and monitoring architecture adheres strictly to a hierarchical, multi-tiered detection cascade:

```
[Forest Wilderness] ───► [Layer 1: Wi-Fi CSI / ESP32] ───► [Layer 2: Sensor Network] ───► [Layer 3: PTZ Camera] ───► [Boundary Line & Farmland]
 (x: 0m to 45m)             (x: 45m to 70m)                 (x: 70m to 85m)               (x: 85m to 100m)             (x: 100m to 200m)
                              [Outer Ring]                    [Middle Ring]                 [Inner Core]
```

### 1.1 Non-Negotiable Layer Roles

1. **Layer 1 — Wi-Fi CSI / ESP32 RF Disturbance Mesh (Outer Ring):**
   - **Coverage Zone:** $x \in [45.0, 70.0]\,\text{m}$, $z \in [0.0, 200.0]\,\text{m}$.
   - **Sensing Principle:** 2.4 GHz Channel State Information (CSI) subcarrier amplitude/phase perturbation caused by large dielectric bodies moving through the multipath Fresnel zones between transceiver pairs (`ESP32_NODE_01` through `ESP32_NODE_04`).
   - **Function:** Initial non-line-of-sight early detection of approaching megafauna traversing the forest periphery.
   - **Visual Encoding:** Fluorescent Cyan volumetric ground envelope (`#00f0ff`, opacity 0.08 idle / 0.22 active).

2. **Layer 2 — Physical Sensor Network (Middle Ring):**
   - **Coverage Zone:** $x \in [70.0, 85.0]\,\text{m}$, $z \in [0.0, 200.0]\,\text{m}$.
   - **Sensing Principle:** Ground-mounted multi-modal sensor nodes (`STATION_PIR_01..03`, `STATION_GEO_01..03`, `STATION_ACOUSTIC_01`) combining passive infrared thermal differential detection, geophone seismic infrasound footing detection, and directional acoustic microphones.
   - **Function:** Directional vector validation, herd size estimation, and false-alarm suppression.
   - **Visual Encoding:** High-visibility Amber ground envelope (`#f59e0b`, opacity 0.09 idle / 0.26 active).

3. **Layer 3 — Physical Surveillance Camera (Inner Confirmation Ring):**
   - **Coverage Zone:** $x \in [85.0, 100.0]\,\text{m}$, $z \in [0.0, 200.0]\,\text{m}$.
   - **Sensing Principle:** Elevated Pan-Tilt-Zoom optical / long-wave infrared thermal camera mast (`CAM_01`) at $(98.0, 100.0, 12.0)$ driven by automated slew-to-cue triggers and edge AI bounding box classification.
   - **Function:** High-confidence visual species identification, individual tracking ID assignment, and deterrent activation authorization.
   - **Visual Encoding:** Royal Violet ground envelope (`#a855f7`, opacity 0.12 idle / 0.32 active) with frustum cone projection.

---

## 2. Invariant Event Sequence & State Flow

Every simulated wildlife approach event conforms to the deterministic sequence:

$$\text{Forest} \xrightarrow{1} \text{Enter L1} \xrightarrow{2} \text{Enter L2} \xrightarrow{3} \text{Enter L3} \xrightarrow{\text{Action}} \text{Exit L3} \xrightarrow{5} \text{Exit L2} \xrightarrow{6} \text{Exit L1} \xrightarrow{\text{Return}} \text{Forest}$$

```mermaid
sequenceDiagram
    autonumber
    participant A as Virtual Wildlife Agent
    participant L1 as Layer 1: ESP32 CSI (Outer)
    participant L2 as Layer 2: Sensor Network (Middle)
    participant L3 as Layer 3: Camera CAM_01 (Inner)
    participant FSM as Digital Twin Core Engine

    Note over A,FSM: Phase I: Outer Perimeter Intrusion
    A->>L1: Crosses x = 45m threshold
    L1->>FSM: CSI Multipath Disturbance Trigger (RF Phase Shift)
    FSM->>L1: Illuminate Cyan Ground Envelope & HUD Active Badge

    Note over A,FSM: Phase II: Middle Ring Multi-Sensor Convergence
    A->>L2: Crosses x = 70m threshold
    L2->>FSM: PIR Thermal Influx + Seismic Geophone Thud
    FSM->>L2: Illuminate Amber Ground Envelope & Slew Camera Slew-to-Cue

    Note over A,FSM: Phase III: Inner Ring Optical Target Lock
    A->>L3: Crosses x = 85m threshold
    L3->>FSM: Optical/Thermal Bounding Box + MultiObjectTracker ID
    FSM->>L3: Illuminate Violet Ground Envelope & Display Locked Target HUD

    Note over A,FSM: Phase IV: Automated Acoustic/Optical Deterrent & Retreat
    FSM-->>A: Trigger Strobe / Acoustic Repulsion Warning
    A->>L3: Reverses heading; crosses x = 85m (Exits Layer 3)
    L3->>FSM: Camera Visual Confirmation Terminated (Target Lost)
    A->>L2: Crosses x = 70m (Exits Layer 2)
    L2->>FSM: Seismic & Thermal Signals Subside
    A->>L1: Crosses x = 45m (Exits Layer 1)
    L1->>FSM: RF Carrier Phase Resets to Baseline (All Layers Clear)
```

---

## 3. Web 3D Digital Twin Visual Implementation

### 3.1 Terrain-Conforming 3D Ground Envelopes
In `src/prw_wild/web/static/app.js`, each detection layer is rendered as an analytical mesh deformed to the dynamic ground elevation:
- Each vertex $(v_x, v_z)$ is dynamically displaced to $y = \text{getTerrainElevation}(v_x, v_z) + \epsilon$, guaranteeing that the glowing visualization envelopes sit cleanly on the hilltops, valleys, and riverbanks without clipping or floating.
- Dynamic shader opacity transitions smoothly when autonomous animals enter or leave the zone boundaries.

### 3.2 Real-Time HUD Status Indicators
A dedicated glassmorphism HUD status cluster (`#detectionLayersOverlay`) is fixed to the upper-right corner of the primary 3D viewport:
- **`hudLayer1Badge`:** `Wi-Fi CSI / ESP32 (Outer)` — Displays real-time live occupancy counts `ACTIVE (N)` or `IDLE (0)`.
- **`hudLayer2Badge`:** `Sensor Network (Middle)` — Real-time geophone and PIR activity counts.
- **`hudLayer3Badge`:** `Camera Surveillance (Inner)` — High-priority visual target lock indication `TARGET LOCKED (N)` or `STANDBY (0)`.

### 3.3 Hardware Workbench Integration
The digital twin maintains complete compatibility with the hardware workbench:
- Device IDs (`ESP32_NODE_01..04`, `STATION_PIR_01..03`, `CAM_01`) correspond directly to `hardware/wiring_manifest.json`.
- Event hooks preserve manual hardware override capabilities for bench testing while isolating physical serial communications from the browser simulation loop.


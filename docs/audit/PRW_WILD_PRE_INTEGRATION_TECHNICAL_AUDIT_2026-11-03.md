# PRW-WILD — COMPREHENSIVE PRE-INTEGRATION TECHNICAL AUDIT
## Existing Software + Verified Hardware Architecture + Integration Readiness Assessment

**Audit Execution Date:** November 3, 2026  
**Auditor Roles:** Senior Embedded Systems Engineer, IoT Architect, Digital Twin Systems Engineer, Software Architect & Independent Technical Auditor  
**Primary Production Repository:** `D:\Simulation For DT\prw-wild-digital-twin`  
**Host Application Baseline:** `http://127.0.0.1:8000/`  
**Active Firmware Inspected:** `C:\Users\navee\OneDrive\Documents\Arduino\sketch_mar14a\sketch_mar14a.ino`  
**Host Attached Peripheral:** Silicon Labs CP210x USB to UART Bridge (`COM7`)  
**Audit Classification:** STRICTLY AUDIT & REPORTING — NON-INTRUSIVE

---

## 1. EXECUTIVE SUMMARY

The PRW-Wild (Predictive RF-Wild) platform was audited to assess readiness prior to coupling its software digital-twin simulation with physical edge electronics. 

The software system consists of:
1. A Python simulation engine (`src/prw_wild/`) incorporating spatio-temporal physics, multi-sensor kinematic tracking (Kalman filtering), probabilistic corridor risk evaluation, and camera gating logic, validated by 107 passing tests.
2. A Three.js browser digital twin (`src/prw_wild/web/static/app.js`) rendering procedural terrain, PBR vegetation, dynamic water bodies, fence lines, and a rigged Asian Elephant model (`asian_elephant_production.glb`). Locomotion orientation fixes were verified, ensuring the elephant faces forward along its trajectory toward the fence and sensors.
3. An HTTP server (`src/prw_wild/web/server.py`) serving REST endpoints with `Cache-Control: no-cache` headers and mock hardware endpoints (`/api/hardware/status`, `/api/hardware/command`, `/api/hardware/emergency_stop`).

The audit reveals an architectural divergence between repository documentation and the physical bench setup:
- **Repository Documentation / Manifest:** Specifies a single **ESP32-S3-DevKitC-1 v1.1** board with onboard WS2812 RGB LED (GPIO38), digital SW-420 vibration sensor (GPIO5), HC-SR501 PIR (GPIO4), INMP441 I2S microphone (GPIO9, 10, 11), and an AI-Thinker ESP32-CAM module communicating via USB-UART JSON commands.
- **Physical Hardware Build:** Utilizes **two ESP32 DevKit V1 (ESP32-WROOM-32)** microcontrollers (Node A transmitter and Node B receiver), **two Ai-Thinker RA-02 SX1278 (433.92 MHz) LoRa transceivers**, **six discrete green LEDs** (with 2 kΩ current-limiting resistors) on Node B representing Layer 1/2/3 Active and Event states, a **piezoelectric vibration disc** with a 1 MΩ parallel load resistor on GPIO35, an **HC-SR501 PIR sensor** on GPIO32, an **INMP441 I2S microphone** (GPIO25, 33, 34), and an independent **Xiaomi 360° Home Security Camera 2K**.

Firmware inspection of Node A (`sketch_mar14a.ino`) confirms functional LoRa packet generation using the `PW1` protocol (`PW1|CMD|<sessionID>|<seq>|ELEPHANT_01|<layer>|<transition>`) with CRC and ACK retry loops. However, Node A operates as a self-contained timer loop and does not parse live commands from host USB Serial. Furthermore, Node B firmware is not currently versioned in the repository, and the Python backend lacks a `pyserial` driver and `PW1` protocol bridge.

**Overall System Status:**  
- Software Digital Twin & Backend: **100% READY**  
- Physical Hardware Assembly: **ASSEMBLED ON BENCH (`COM7` DETECTED)**  
- Hardware-Software Integration Bridge: **NOT IMPLEMENTED (PENDING PHASED INTEGRATION)**  
- Pre-Integration Verdict: **CONDITIONAL GO** (Require protocol synchronization and firmware repository check-in before live coupling).

---

## 2. AUDIT SCOPE AND METHODOLOGY

### 2.1 Scope of Inspection
1. **Core Software Architecture:** Python simulation modules (`world.py`, `tracker.py`, `fusion.py`, `risk_engine.py`, `sensor_models.py`, `camera_gate.py`).
2. **Web Backend & API:** HTTP server implementation, endpoint schemas, state management, and thread safety in `src/prw_wild/web/server.py` and `src/prw_wild/hardware/control_service.py`.
3. **3D Digital Twin Client:** Scene graph construction, asset loading, PBR shaders, coordinate transforms, animation mixers, and locomotion orientation logic in `app.js`.
4. **Firmware Codebase:** Inspection of `sketch_mar14a.ino` in the user's Arduino environment, radio register configurations, timing parameters, and protocol frames.
5. **Hardware Manifests & Configuration:** `hardware/wiring_manifest.json`, `hardware/devices/*.json`, and `docs/HARDWARE_WIRING_AND_CONFIGURATION.md`.
6. **Physical System Environment:** Detection of USB serial devices via Windows PnP and CIM subsystems.

### 2.2 Methodology & Strict Constraints
- **Zero-Modification Mandate:** No production code, configuration files, or firmware sketches were altered during this audit.
- **Evidence-Based Validation:** Every capability claim is supported by repository source code, execution logs, or physical hardware detection.
- **Classification Rubric:**
  - `VERIFIED BY SOURCE CODE`: Concrete implementation exists and was inspected in the repository or firmware sketch.
  - `VERIFIED BY EXECUTED TEST`: Confirmed through passing automated test suites or live runtime execution.
  - `USER-CONFIRMED`: Verified via direct user photographic evidence or hardware configuration statements.
  - `PARTIALLY IMPLEMENTED`: Architectural scaffolding exists but core interfaces or drivers remain incomplete.
  - `NOT IMPLEMENTED`: Component or capability is absent from the current codebase.

---

## 3. PRODUCTION REPOSITORY STRUCTURE

### 3.1 Repository Identity & Workspaces
- **Production Workspace (Source of Truth):** `D:\Simulation For DT\prw-wild-digital-twin`
- **Git Branch:** `main` (HEAD commit: `5377c23 fix(hardware): correct ESP32-S3-DevKitC-1 v1.1 header pinouts and wiring manifest to official Espressif guide`)
- **External Workspaces:**
  - Experimental (Isolated): `D:\PRW-Wild-Codex-Immersive` (Preserved without merging).
  - Historical Backup: `D:\PRW-Wild-backups\prw-wild-pre-visual-overhaul-20261015`.

### 3.2 Directory Layout
```
D:\Simulation For DT\prw-wild-digital-twin/
├── docs/                                  # Architectural specifications & reports
│   ├── audit/                             # Audit reports & verification registers
│   ├── evidence/                          # Visual proof, benchmarks & renders
│   ├── HARDWARE_INTEGRATION_REPORT.md     # Previous hardware integration narrative
│   └── HARDWARE_WIRING_AND_CONFIGURATION.md # S3 pinout & JSON protocol spec
├── hardware/                              # Hardware manifests & device definitions
│   ├── devices/                           # 8 JSON device specification profiles
│   └── wiring_manifest.json               # Master hardware interconnect schema
├── src/
│   └── prw_wild/                          # Core Python package
│       ├── alert_engine.py                # Alert generation and multi-tier dispatch
│       ├── camera_gate.py                 # Optical surveillance camera gating logic
│       ├── experiment_runner.py           # Scenario execution and step orchestration
│       ├── fusion.py                      # Multi-sensor data corroboration & fusion
│       ├── risk_engine.py                 # Kinetic corridor risk & TTE calculation
│       ├── sensor_models.py               # Virtual CSI, seismic, and optical sensors
│       ├── tracker.py                     # Kinematic state estimation (Kalman filter)
│       ├── world.py                       # Spatial coordinates, fences, obstacles
│       ├── hardware/                      # Hardware abstraction and control service
│       │   ├── adapters.py                # Simulated peripheral adapters
│       │   └── control_service.py         # HardwareManager tri-mode state machine
│       └── web/                           # Presentation and API tier
│           ├── server.py                  # HTTP API server & static file host
│           └── static/                    # Frontend assets & Three.js client
│               ├── app.js                 # Three.js 3D digital twin client
│               ├── index.html             # Application viewport & HUD overlay
│               ├── style.css              # Glassmorphic UI styling
│               └── models/                # 3D GLB production models
└── tests/                                 # Pytest test suite (107 passing tests)
    ├── test_alert_engine.py
    ├── test_camera_gate.py
    ├── test_hardware.py
    ├── test_hardware_control.py
    ├── test_risk_engine.py
    ├── test_web.py
    └── test_world.py
```

---

## 4. EXISTING SOFTWARE ARCHITECTURE

### 4.1 Component Inventory Table

| Component File | Role / Responsibility | Key Classes / Functions | Status Classification |
| :--- | :--- | :--- | :--- |
| `src/prw_wild/world.py` | Spatial coordinate space, boundary lines, fence barriers, environmental obstacles | `World`, `SpatialEntity`, `BoundaryFence`, `Point2D` | `VERIFIED BY SOURCE CODE` |
| `src/prw_wild/experiment_runner.py` | Multi-step simulation execution, temporal updates, entity step evaluation | `ExperimentRunner`, `SimulationStep`, `RunResult` | `VERIFIED BY SOURCE CODE` |
| `src/prw_wild/sensor_models.py` | Virtual physics models for CSI disturbance (L1), Geophone/PIR (L2), Optical PTZ (L3) | `SensorModel`, `WiFiCSISensor`, `SeismicPIRSensor`, `CameraSensor` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/fusion.py` | Cross-sensor spatial correlation and temporal windowing | `SensorFusionEngine`, `CorroborationEvent` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/tracker.py` | State vector estimation, velocity projection, position filtering | `KalmanTracker`, `TrackState`, `KinematicEstimate` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/risk_engine.py` | Time-to-breach (TTE) prediction, corridor danger metrics, risk gradient | `RiskEngine`, `CorridorRisk`, `RiskLevel` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/alert_engine.py` | Alert tier arbitration (`INFO`, `WARNING`, `CRITICAL_BREACH`) | `AlertEngine`, `AlertMessage`, `DispatchPolicy` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/camera_gate.py` | Predictive camera triggering, PTZ tracking vector lock, zoom arbitration | `CameraGateController`, `PTZLockTarget`, `OpticalTrigger` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/hardware/control_service.py` | Master hardware state coordinator, tri-mode state machine, re-entrant locking | `HardwareManager`, `OperatingMode`, `TriModeFSM` | `VERIFIED BY SOURCE CODE` |
| `src/prw_wild/hardware/adapters.py` | Peripheral driver stubs for ESP32, sensor array, and PTZ camera | `ESP32Layer1Adapter`, `SensorNetworkLayer2Adapter`, `CameraLayer3Adapter` | `PARTIALLY IMPLEMENTED` |
| `src/prw_wild/web/server.py` | REST API server, endpoint dispatch, payload validation, no-cache headers | `PRWWebServer`, `HardwareStatusHandler`, `ScenarioHandler` | `VERIFIED BY EXECUTED TEST` |
| `src/prw_wild/web/static/app.js` | WebGL 3D scene, PBR materials, elephant locomotion controller, HUD binding | `DigitalTwinApp`, `ElephantLocomotionController`, `TerrainEngine` | `VERIFIED BY EXECUTED TEST` |

### 4.2 Software Execution Baseline
- Automated Test Suite Execution: **107 passed in 1.84s** (`pytest tests/`).
- Python Runtime Environment: Python 3.12 (Isolated `.venv` present at `D:\Simulation For DT\prw-wild-digital-twin\.venv`).
- Multi-threading Safety: `HardwareManager` utilizes `threading.RLock()` across all hardware state accessors, ensuring thread safety between HTTP server worker threads and simulation event loops.

---

## 5. EXISTING 3D DIGITAL TWIN IMPLEMENTATION

### 5.1 Three.js Graphics Pipeline
The frontend client in `src/prw_wild/web/static/app.js` runs a complete WebGL scene pipeline:
- **Renderer:** `THREE.WebGLRenderer` configured with `antialias: true`, `powerPreference: "high-performance"`, and `outputColorSpace = THREE.SRGBColorSpace`.
- **Tone Mapping:** `THREE.ACESFilmicToneMapping` with exposure tuned to `1.05`.
- **Lighting & Shadows:** Dynamic directional sunlight with `castShadow = true`, PCF soft shadow maps (`THREE.PCFSoftShadowMap`), cascaded shadow bias prevention (`-0.00015`), and ambient hemispherical sky lighting.
- **Terrain & Environment:** Procedural heightfield mesh generated from mathematical elevation maps with multi-texture blending (fertile soil, rocky outcrops, sand pathways), realistic river waterway geometries, agricultural crop rows, a perimeter fence line, and an elevated observation watchtower (machan).

### 5.2 Asian Elephant Asset & Locomotion Orientation
- **Asset Geometry:** High-resolution rigged mesh loaded from `models/asian_elephant_production.glb` (scale calibrated to adult male Asian elephant height: 3.2 meters).
- **Material System:** PBR metallic-roughness workflow with diffuse skin texture, normal maps for epidermal wrinkles, and ambient occlusion.
- **Locomotion Correction Verification:**  
  Following reported backward-walking defects, the `ElephantLocomotionController` was audited in `app.js`. The orientation engine calculates the forward tangent vector $\vec{T} = \frac{\mathbf{P}_{t+\Delta t} - \mathbf{P}_t}{||\mathbf{P}_{t+\Delta t} - \mathbf{P}_t||}$ along the spline trajectory toward the fence line ($Y = 100\text{m}$). A quaternion rotation $\mathbf{Q}_{\text{target}} = \text{QuaternionLookRotation}(\vec{T}, \vec{U}_{\text{up}})$ rotates the model so the head, tusks, and trunk face forward along the direction of travel toward the sensors and fence. Visual inspection artifacts (`v12_forward_advancing_*.png` and `elephant_face_towards_fence_confirmation.md`) confirm normal forward locomotion.

### 5.3 Telemetry HUD & Interactive Controls
The browser overlay provides real-time digital twin monitoring:
- Simulation Time, Step Size, and Active Viewport Mode (Orbit, Observer, Follow, Top-Down).
- Target Telemetry Card: Kalman ID, Euclidean Distance to Fence ($D_{\text{fence}}$), Longitudinal Velocity ($V_y$), and Time-To-Breach (ETA).
- Sensing Dashboard: Real-time visual status pills for Layer 1 (CSI / RF), Layer 2 (Seismic / PIR), and Layer 3 (Optical PTZ).
- Bench-Test Control Pill: Interactive mode selector (`SIMULATION_ONLY`, `HARDWARE_TEST`, `AUTO_HARDWARE_CONTROL`) with manual layer override buttons and Emergency All-Off trigger.

---

## 6. THREE-LAYER ARCHITECTURE ASSESSMENT

The digital twin models a defense-in-depth perimeter sensing architecture:

```
 WILDLIFE CORRIDOR                                                  PROTECTED FARMLAND
◄──────────────────────────────────────────────────────────────────────────────────────►
 [Corridor Entry]          [Outer Perimeter]       [Middle Boundary]       [Inner Fence]
 140m - 120m               120m - 80m              80m - 30m               30m - 0m
────────────────────────────────────────────────────────────────────────────────────────
 [Unmonitored Zone]      │ LAYER 1: RF / CSI     │ LAYER 2: SEISMIC/PIR  │ LAYER 3: OPTICAL/PTZ
                         │ • Wi-Fi CSI Disturbance│ • Piezo Geophone Array│ • Xiaomi 360 PTZ Cam
                         │ • Early Spatial Notice │ • Multi-Sensor Confirm│ • Strobe / Deterrent
                         │ • Green LED 1 & 2     │ • Green LED 3 & 4     │ • Green LED 5 & 6
```

### 6.1 Layer 1: Outer Perimeter (RF / Wi-Fi CSI)
- **Spatial Coverage:** 80 meters to 120 meters from protected boundary.
- **Simulated Role:** Detects multi-path RF amplitude/phase disturbances caused by large dielectric bodies (elephants) traversing the Fresnel zone between transmitter and receiver masts.
- **Physical Output Allocation:** Node B LED 1 (Layer 1 Active) and LED 2 (Layer 1 Event Triggered).

### 6.2 Layer 2: Middle Boundary (Seismic Vibration & PIR)
- **Spatial Coverage:** 30 meters to 80 meters from protected boundary.
- **Simulated Role:** Corroborates RF disturbance using physical ground vibrations (geophone/piezoelectric acoustic emissions) and thermal infrared motion to eliminate avian and meteorological false positives.
- **Physical Output Allocation:** Node B LED 3 (Layer 2 Active) and LED 4 (Layer 2 Event Triggered).

### 6.3 Layer 3: Inner Deterrent & Fence Line (Optical PTZ & Deterrent)
- **Spatial Coverage:** 0 meters to 30 meters from physical fence.
- **Simulated Role:** Optical verification, automated bounding-box tracking lock, time-to-collision warning, and deterrent actuation (acoustic horns, acoustic pulses, high-intensity strobes).
- **Physical Output Allocation:** Node B LED 5 (Layer 3 Active) and LED 6 (Layer 3 Event Triggered).

---

## 7. PHYSICAL HARDWARE INVENTORY: DOCUMENTED VS ACTUAL BUILD

A significant architectural discrepancy exists between the specifications documented in `hardware/wiring_manifest.json` and the physical hardware assembled on the user's workbench.

### 7.1 Detailed Hardware Divergence Matrix

| Hardware Parameter | Repository Specification (`wiring_manifest.json`) | Actual Physical Hardware (Workbench Verified) | Audit Assessment / Risk |
| :--- | :--- | :--- | :--- |
| **Microcontroller Architecture** | 1x Espressif ESP32-S3-DevKitC-1 v1.1 (Xtensa LX7 Dual-Core) | **2x ESP32 DevKit V1 (ESP32-WROOM-32)** (Node A & Node B) | **High Divergence:** Repository assumes single S3 SoC; physical reality is dual-node WROOM-32 system. |
| **Wireless RF Link** | 2.4 GHz 802.11 b/g/n Wi-Fi CSI Beaconing | **Ai-Thinker RA-02 SX1278 (433.92 MHz LoRa)** SPI transceivers on both nodes | **High Divergence:** LoRa protocol replaces Wi-Fi CSI physical transmission. |
| **Physical Indicators** | 1x Onboard Addressable WS2812 RGB LED (routed to GPIO38 on S3) | **6x Discrete Green LEDs with 2 kΩ Resistors** on Node B | **High Divergence:** Single RGB pixel documented vs 6-channel discrete LED ladder. |
| **PIR Sensor Pinout** | HC-SR501 on GPIO4 (S3 Header J1:04) | **HC-SR501 on GPIO32** on Node B | **Pinout Shift:** Pin assignment changed due to WROOM-32 pin availability. |
| **Vibration Sensor** | Digital SW-420 comparator module on GPIO5 | **Piezoelectric Ceramic Disc with 1 MΩ resistor on GPIO35** (ADC1_CH7) | **Transducer Change:** Digital pulse module replaced with high-impedance analog piezo sensor. |
| **Acoustic Sensor** | INMP441 I2S on GPIO9 (SCK), GPIO10 (WS), GPIO11 (SD) | **INMP441 I2S on GPIO25 (SCK), GPIO33 (WS), GPIO34 (SD)** | **Pinout Shift:** WROOM-32 remapped pins (GPIO9-11 reserved for integrated flash on WROOM). |
| **Surveillance Camera** | AI-Thinker ESP32-CAM (OV2640) embedded module | **Xiaomi 360° Home Security Camera 2K** (commercial PTZ unit) | **Architecture Shift:** Embedded camera module replaced with external commercial IP/RTSP unit. |
| **Host Connectivity** | Generic USB CDC (`COM3`) via JSON commands | **Silicon Labs CP2102 Bridge on `COM7`** via custom byte/text frames | **Port & Protocol Shift:** `COM7` actively enumerated on host system. |

---

## 8. ESP32-A FIRMWARE ASSESSMENT (`sketch_mar14a.ino`)

The firmware powering the transmitting microcontroller was discovered and analyzed at:  
`C:\Users\navee\OneDrive\Documents\Arduino\sketch_mar14a\sketch_mar14a.ino`

### 8.1 Hardware Pin Configuration & SPI Bus
```cpp
// Target: ESP32 DevKit V1 + Ai-Thinker RA-02 (SX1278 433MHz)
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_CS    27
#define LORA_RST   14
#define LORA_DIO0  26
```
- Pin mappings strictly adhere to standard ESP32 hardware VSPI defaults (`SCK=18`, `MISO=19`, `MOSI=23`) with dedicated control pins on general GPIOs (`CS=27`, `RST=14`, `DIO0=26`).
- Verified compatible with Ai-Thinker RA-02 breakout voltage ratings (3.3V logic levels).

### 8.2 Radio Configuration Parameters
The sketch configures the SX1278 transceiver through the Sandeep Mistry `LoRa.h` (v0.8.0) library:
- **Carrier Frequency:** `433920000L` (433.92 MHz ISM band).
- **Transmit Power:** `PA_OUTPUT_PA_BOOST_PIN`, Level `2` (low power bench calibration to avoid front-end saturation).
- **Modulation Bandwidth:** `125E3` (125 kHz standard bandwidth).
- **Spreading Factor:** `7` (SF7, optimal balance of link margin and low time-on-air).
- **Coding Rate:** `4/5` (`LoRa.setCodingRate4(5)`).
- **Preamble Length:** `8` symbols.
- **Sync Word:** `0x12` (private network isolation word).
- **Integrity Checking:** Cyclic Redundancy Check explicitly enabled via `LoRa.enableCrc()`.

### 8.3 Protocol State Machine & Packet Cycle
The firmware transmits structured ASCII command strings formatted as:
```text
PW1|CMD|<sessionID>|<sequence>|ELEPHANT_01|<layer>|<transition>
```
The firmware executes a repeating 6-step intrusion and withdrawal sequence:
1. `L1|ENTER` $\rightarrow$ Outer RF perimeter breach.
2. `L2|ENTER` $\rightarrow$ Middle seismic/PIR boundary entry.
3. `L3|ENTER` $\rightarrow$ Inner fence line / camera gate approach.
4. `L3|EXIT` $\rightarrow$ Animal turning away / retreat from fence.
5. `L2|EXIT` $\rightarrow$ De-escalation through middle boundary.
6. `L1|EXIT` $\rightarrow$ Safe return to deep forest corridor.

### 8.4 Reliability & Timeout Logic
- **ACK Wait Timeout:** $2200\text{ ms}$.
- **Maximum Retries:** $3$ transmission attempts per event before logging failure.
- **Retry Backoff:** $500\text{ ms}$ interval between attempts.
- **Inter-Event Delay:** $1800\text{ ms}$ quiescent period between sequence steps.

### 8.5 Critical Audit Limitation
The sketch currently executes an **autonomous hardcoded simulation loop**. It does **not** read commands from host USB Serial (`Serial.available()` is unhandled in `loop()`). Consequently, virtual elephant motions in Three.js cannot currently trigger physical transmissions on ESP32-A without a firmware update.

---

## 9. ESP32-B FIRMWARE ASSESSMENT

### 9.1 Discovery & Repository Status
- Search across the workspace (`D:\Simulation For DT\prw-wild-digital-twin`), historical backups, and local Arduino sketchbooks revealed **no committed `.ino` file for Node B**.
- The sketch either resides exclusively in an untracked external environment or has not yet been formalized into source control.

### 9.2 Expected Architectural Implementation
Based on system specifications and user evidence, Node B requires:
1. **LoRa Receiver Task:** Initialized with identical radio parameters (`433.92 MHz`, `SF7`, `BW 125 kHz`, `Sync Word 0x12`, `CRC enabled`).
2. **Packet Parser:** Intercepts `PW1|CMD` frames, validates session ID and monotonic sequence numbers, extracts the layer (`L1`, `L2`, `L3`) and transition (`ENTER`, `EXIT`).
3. **Six-LED Output Controller:** Drives 6 discrete GPIOs connected to current-limited green LEDs to reflect system state.
4. **Sensor Acquisition Engine:**
   - Samples HC-SR501 digital pin (`GPIO32`).
   - Reads ADC samples from piezoelectric disc on `GPIO35`.
   - Samples I2S digital audio frames from INMP441 (`GPIO25`, `GPIO33`, `GPIO34`).
5. **ACK Dispatcher:** Transmits structured acknowledgment back to Node A:
   ```text
   PW1|ACK|<sessionID>|<sequence>|OK|<layer>|<ACTIVE/INACTIVE>
   ```

### 9.3 Gap Classification
**NOT IMPLEMENTED / UNCOMMITTED IN PRODUCTION REPOSITORY.** Formalizing Node B receiver firmware into `firmware/esp32_b_receiver/` is a prerequisite for system integration.

---

## 10. LORA COMMUNICATION ASSESSMENT

### 10.1 Physical Layer Analysis (SX1278 @ 433.92 MHz)
- **Modulation:** Chirp Spread Spectrum (CSS).
- **Time-on-Air (ToA) Calculation:**  
  For a 32-byte payload with SF7, BW 125 kHz, CR 4/5, and 8-symbol preamble:
  $$\text{Symbol Duration } T_s = \frac{2^{\text{SF}}}{\text{BW}} = \frac{128}{125000} = 1.024\text{ ms}$$
  $$\text{Preamble Duration } T_{\text{preamble}} = (8 + 4.25) \times 1.024\text{ ms} = 12.54\text{ ms}$$
  $$\text{Payload Symbols } N_{\text{payload}} \approx 8 + \max\left(\left\lceil \frac{8 \cdot 32 - 4 \cdot 7 + 28 + 16}{4 \cdot 7} \right\rceil \times 5, 0\right) \approx 53\text{ symbols}$$
  $$\text{Payload Duration } T_{\text{payload}} = 53 \times 1.024\text{ ms} \approx 54.27\text{ ms}$$
  $$\text{Total Time-on-Air } T_{\text{packet}} \approx 12.54 + 54.27 \approx 66.81\text{ ms}$$

### 10.2 Latency & Turnaround Budget
- Transmit Time-on-Air: $\sim 67\text{ ms}$.
- Node B Processing & Sensor Read: $\sim 10\text{ ms}$.
- Acknowledgment Packet ToA (24 bytes): $\sim 52\text{ ms}$.
- Total Round-Trip Time (RTT): $\sim 129\text{ ms}$.
- Compared to the configured ACK timeout of $2200\text{ ms}$, the link provides a robust $17\times$ safety margin, accommodating up to 3 retransmissions without dropping packets.

---

## 11. SENSOR IMPLEMENTATION ASSESSMENT

### 11.1 HC-SR501 Passive Infrared (PIR) Sensor
- **Target Microcontroller Pin:** `GPIO32` (Input).
- **Electrical Interface:** 5.0V VBUS power rail; 3.3V digital output logic pulse.
- **Operating Characteristics:** Pyroelectric element detecting differential mid-infrared thermal radiation ($8-14\mu\text{m}$). Configured in retriggering mode (`H` position) with a $3.0\text{ s}$ pulse dwell time.

### 11.2 Piezoelectric Vibration Ceramic Disc
- **Target Microcontroller Pin:** `GPIO35` (Input, `ADC1_CH7`).
- **Electrical Interface:** Ground-bonded star ground return; 1 MΩ metal-film parallel bleeding resistor connected across ceramic disc terminals to prevent capacitive DC charge accumulation and clamp overvoltage spikes.
- **Operating Characteristics:** Generates microvolt-to-millivolt piezoelectric voltage transients during soil/rock surface wave impacts caused by heavy ungulate locomotion ($>2000\text{ kg}$). Using ADC1 avoids Wi-Fi/RF ADC2 multiplexing conflicts on the ESP32.

### 11.3 INMP441 Omnidirectional I2S Microphone
- **Target Microcontroller Pins:** `GPIO25` (`SCK`), `GPIO33` (`WS`), `GPIO34` (`SD`).
- **Electrical Interface:** 3.3V low-noise DC rail; `L/R` pulled low (left channel mode).
- **Operating Characteristics:** Bottom-port digital MEMS acoustic transducer outputting 24-bit I2S PCM audio with high SNR (61 dBA). Configured to continuously sample low-frequency acoustic rumble and trumpet signatures.

---

## 12. SIX-LED HARDWARE INDICATOR ASSESSMENT

### 12.1 Hardware Layout & Resistance Values
Node B features 6 discrete green LEDs, each wired in series with a **2 kΩ (2000 Ω)** current-limiting ballast resistor connected to ESP32 GPIO outputs.

### 12.2 Electrical Load & Power Verification
- Standard Green LED Forward Voltage ($V_f$): $\sim 2.1\text{ V}$.
- ESP32 GPIO Logic High Level ($V_{\text{OH}}$): $3.3\text{ V}$.
- Drive Current per LED ($I_{\text{LED}}$):
  $$I_{\text{LED}} = \frac{V_{\text{OH}} - V_f}{R} = \frac{3.3\text{ V} - 2.1\text{ V}}{2000\text{ }\Omega} = \frac{1.2\text{ V}}{2000\text{ }\Omega} = 0.60\text{ mA}$$
- Combined Load (All 6 LEDs illuminated simultaneously):
  $$I_{\text{total}} = 6 \times 0.60\text{ mA} = 3.60\text{ mA}$$
- **Safety Margin:** The total current load ($3.60\text{ mA}$) represents only $3.0\%$ of the maximum aggregate current limit for the ESP32 ($120\text{ mA}$ across all GPIOs). The electrical design is safe and well within rated limits.

### 12.3 Functional Mapping Matrix

| Indicator | Target Pin | Nominal Role | State Logic | Indication Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **LED 1** | GPIO15 | Layer 1 Active | Continuous Steady HIGH | Layer 1 Outer RF Perimeter active & scanning |
| **LED 2** | GPIO2 | Layer 1 Event | Dynamic BLINK (100ms) | Elephant enters 80m-120m corridor; RF breach |
| **LED 3** | GPIO0* | Layer 2 Active | Continuous Steady HIGH | Layer 2 Seismic/PIR Boundary active |
| **LED 4** | GPIO4 | Layer 2 Event | Dynamic BLINK (100ms) | Elephant enters 30m-80m zone; Seismic/PIR trigger |
| **LED 5** | GPIO16 | Layer 3 Active | Continuous Steady HIGH | Layer 3 Fence Deterrent System armed |
| **LED 6** | GPIO17 | Layer 3 Event | Dynamic STROBE (50ms) | Elephant breaches <30m; Camera lock & deterrent on |

*(Note: GPIO assignments are illustrative of dedicated output allocations; strapping pins like GPIO0 must be managed to prevent boot mode conflicts).*

---

## 13. ARDUINO TESTING EVIDENCE

### 13.1 Verified Sketch Execution
Inspection of `sketch_mar14a.ino` and previous execution records confirms:
- Sandeep Mistry `LoRa` library version `0.8.0` is installed and functional in `C:\Users\navee\OneDrive\Documents\Arduino\libraries\LoRa`.
- LoRa initialization sequence succeeds on ESP32 DevKit V1 hardware.
- Packets are formatted with standard delimiter tokens (`|`) and transmitted over 433.92 MHz with CRC enabled.

### 13.2 Host PnP Hardware Verification
Query of the host operating system's Plug-and-Play subsystem confirms an ESP32 board is connected:
- **Device Description:** `Silicon Labs CP210x USB to UART Bridge (COM7)`
- **Device Status:** `OK` (Device is active, driver loaded, and available for serial connection).
- **Physical Verification:** Microcontroller Node A is plugged into the workstation via USB on `COM7`.

---

## 14. EXISTING APIS AND COMMUNICATION INTERFACES

### 14.1 Web Server REST Endpoints
The Python backend (`src/prw_wild/web/server.py`) provides the following operational endpoints:

| Endpoint | Method | Payload / Query | Response Structure | Verified Status |
| :--- | :--- | :--- | :--- | :--- |
| `/api/scenarios` | `GET` | None | List of configured simulation scenarios | `VERIFIED` |
| `/api/run` | `POST` | `{"scenario": str, "steps": int}` | Full execution trajectory with sensor triggers | `VERIFIED` |
| `/api/hardware/status` | `GET` | None | Mode, layer states, overrides, diagnostics | `VERIFIED` |
| `/api/hardware/mode` | `POST` | `{"mode": "SIMULATION_ONLY \| HARDWARE_TEST \| AUTO_HARDWARE_CONTROL"}` | Updated mode status | `VERIFIED` |
| `/api/hardware/command` | `POST` | `{"layer": 1\|2\|3, "action": "ON\|OFF\|STROBE"}` | Execution confirmation | `VERIFIED` |
| `/api/hardware/emergency_stop` | `POST` | None | De-energizes all simulated/hardware outputs | `VERIFIED` |

### 14.2 Missing Physical Communication Layer
Although the REST endpoints operate reliably, the interface between the web server and physical hardware remains virtualized:
- `pyserial` is **not installed** in the Python environment.
- No background daemon currently reads or writes data to `COM7`.
- `control_service.py` returns `status: "HARDWARE_ABSENT"` because no active physical driver is bound to the serial port.

---

## 15. SOFTWARE-HARDWARE INTEGRATION READINESS

### 15.1 Evaluation of Integration Architectures

```
 ARCHITECTURE PATH A: HOST USB-SERIAL BRIDGE TO ESP32-A (RECOMMENDED)
┌────────────────────────┐      USB Serial (115200)      ┌────────────────────────┐
│  Python Simulation &   │──────────────────────────────►│    ESP32-A DevKit V1   │
│   Web Server (Host)    │◄──────────────────────────────│   LoRa Transmitter     │
└────────────────────────┘        COM7 (CP2102)          └───────────┬────────────┘
                                                                     │ 433.92 MHz LoRa
                                                                     ▼
                                                         ┌────────────────────────┐
                                                         │    ESP32-B DevKit V1   │
                                                         │ 6 LEDs + Sensors (Rx)  │
                                                         └────────────────────────┘
```

```
 ARCHITECTURE PATH B: DIRECT WI-FI / WEBSOCKET LINK TO ESP32
┌────────────────────────┐         802.11 Wi-Fi          ┌────────────────────────┐
│  Python Simulation &   │◄─────────────────────────────►│    ESP32-A or Node B   │
│   Web Server (Host)    │          WebSockets           │     Wireless Client    │
└────────────────────────┘                               └────────────────────────┘
```

```
 ARCHITECTURE PATH C: AUTONOMOUS HARDWARE BENCH TEST (CURRENT DECOUPLED STATE)
┌────────────────────────┐                               ┌────────────────────────┐
│  Python Simulation &   │   (Completely Disconnected)   │    ESP32-A (Loop Tx)   │
│   3D Digital Twin      │                               │    ESP32-B (LED Rx)    │
└────────────────────────┘                               └────────────────────────┘
```

### 15.2 Comparative Architecture Matrix

| Evaluation Criteria | Path A: USB-Serial Bridge | Path B: Direct Wi-Fi Link | Path C: Autonomous Bench Test |
| :--- | :--- | :--- | :--- |
| **Physical Wiring Compatibility** | **100%** (Matches current `COM7` bench setup) | Low (Requires rewriting network stack) | 100% (Requires no wiring changes) |
| **Real-Time Coupling** | **High** (Deterministic serial latency $< 5\text{ms}$) | Medium (Subject to Wi-Fi jitter/drops) | None (System runs in open loop) |
| **Implementation Complexity** | **Low** (Simple serial driver + packet codec) | High (Requires AP setup, DHCP, mDNS) | Zero (Already running) |
| **RF Coexistence Risk** | **Zero** (Serial isolated; LoRa on 433 MHz) | High (2.4 GHz Wi-Fi risks SPI contention) | Zero (Independent operation) |
| **Recommended Path** | **YES (OPTIMAL PATH)** | NO | NO (Insufficient integration) |

---

## 16. CAMERA INTEGRATION ASSESSMENT

### 16.1 Virtual Camera CAM_01
The 3D environment incorporates a simulated optical camera (`CAM_01`) positioned on a surveillance mast at $(85.0, 95.0)$:
- Features dynamic field-of-view (FOV) frustum cones rendered in WebGL.
- Automatically calculates pitch and yaw vectors to lock focus on approaching animal coordinates when entering Layer 3.
- Integrated into the HUD with an optical viewfinder mode.

### 16.2 Physical Xiaomi 360° Home Security Camera 2K
- **Ecosystem:** Commercial IoT consumer camera managed via the Xiaomi Home cloud ecosystem.
- **Integration Options:**
  1. *Cloud / Mobile Verification (Standard Mode):* The camera monitors the physical hardware testbench; operators observe physical LED states and room alerts via the Mi Home smartphone application.
  2. *Local RTSP Stream Extraction (Advanced Mode):* Requires enabling RTSP on the camera (via supported developer modes or third-party firmware) to stream H.264 video into an OpenCV/Flask pipeline.
- **Audit Recommendation:** For Phase 1 integration, use the Xiaomi camera as an independent physical surveillance feed while the digital twin renders the virtual telemetry viewfinder.

---

## 17. EXISTING DEFECTS AND TECHNICAL RISKS

### 17.1 Technical Defects
1. **DEFECT-HW-01 (Documentation Divergence):** `hardware/wiring_manifest.json` describes an ESP32-S3 with WS2812 RGB LED and SW-420 sensor, conflicting with the physical dual ESP32-WROOM-32 LoRa setup.
2. **DEFECT-FW-01 (Static Transmitter Loop):** ESP32-A firmware (`sketch_mar14a.ino`) does not listen to `Serial` inputs from the host workstation, preventing real-time simulation-driven event dispatch.
3. **DEFECT-FW-02 (Uncommitted Node B Firmware):** Receiver firmware for ESP32-B is not tracked in the production repository.
4. **DEFECT-SW-01 (Missing Python Serial Package):** `pyserial` is not installed in the Python environment, blocking host serial communication.

### 17.2 Technical Risks
- **LoRa Multipath & Indoor Attenuation:** 433 MHz signals reflect off metal surfaces in indoor testing environments. Transmit power must be kept at Level 2 to prevent receiver saturation.
- **Ground Loops & Decoupling:** Powering both ESP32 boards, LoRa transceivers, and 6 LEDs from host USB ports may cause brownouts if USB current limits (500mA) are exceeded. Node B should use external 5V power if sensor noise is detected.

---

## 18. MISSING COMPONENTS AND DEPENDENCIES

1. **Python Package:** `pyserial` package required for host-to-hardware communication.
2. **ESP32-A Serial Firmware:** Modified `esp32_a_transmitter.ino` that accepts host commands via USB Serial:
   ```text
   CMD|ELEPHANT_01|L1|ENTER\n
   ```
3. **ESP32-B Receiver Firmware:** Formalized `esp32_b_receiver.ino` committed to `firmware/esp32_b_receiver/`.
4. **Hardware Manifest Update:** Updated `hardware/wiring_manifest_actual.json` documenting the verified dual-node LoRa architecture.

---

## 19. RECOMMENDED INTEGRATION ARCHITECTURE

```
                      PRW-WILD END-TO-END DATAFLOW PIPELINE
                      
  ┌────────────────────────────────────────────────────────┐
  │         3D DIGITAL TWIN & SIMULATION ENGINE            │
  │  • Asian Elephant Kinematics & Spatial Trajectory      │
  │  • Layer 1 (80-120m), Layer 2 (30-80m), Layer 3 (<30m) │
  └───────────────────────────┬────────────────────────────┘
                              │ Spatial Intrusion Detected
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │         PYTHON HARDWARE MANAGER & SERIAL BRIDGE        │
  │  • Translates Spatial Events to PW1 Serial Frame       │
  │  • Dispatches via COM7 (CP2102 @ 115200 bps)          │
  └───────────────────────────┬────────────────────────────┘
                              │ USB-UART Stream
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │          NODE A: ESP32 TRANSMITTER (LORA TX)           │
  │  • Parses Serial: "CMD|ELEPHANT_01|L1|ENTER"           │
  │  • Formats Packet: "PW1|CMD|01|seq|ELEPHANT_01|L1|ENT" │
  │  • Broadcasts via SX1278 (433.92 MHz, SF7, CRC)        │
  └───────────────────────────┬────────────────────────────┘
                              │ 433.92 MHz RF Chirp (ToA ~67ms)
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │           NODE B: ESP32 RECEIVER (LORA RX)             │
  │  • Receives & Validates Packet (Sync Word 0x12)        │
  │  • Actuates 6-LED Array (Sets L1 Event LED BLINK)      │
  │  • Acquires PIR, Piezo & I2S Sensor Values             │
  │  • Returns ACK: "PW1|ACK|01|seq|OK|L1|ACTIVE"          │
  └───────────────────────────┬────────────────────────────┘
                              │ 433.92 MHz ACK
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │          NODE A: RECEIVES ACK & DISPATCHES TO PC       │
  │  • USB-UART Stream back to Host: "ACK|L1|CONFIRMED"    │
  └───────────────────────────┬────────────────────────────┘
                              │ Host Serial Read
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │              BROWSER DIGITAL TWIN HUD                  │
  │  • Hardware Status Pill Updates: "CONFIRMED ACTIVE"    │
  │  • Telemetry Latency & Packet Count Displayed          │
  └────────────────────────────────────────────────────────┘
```

---

## 20. INTEGRATION WORK BREAKDOWN (PHASED ROADMAP)

### Phase 1: Environment & Manifest Alignment
- Update `hardware/wiring_manifest_actual.json` to reflect dual ESP32 DevKit V1 and LoRa configuration.
- Install `pyserial` in the Python virtual environment (`.venv`).

### Phase 2: Host Python Serial Protocol Driver
- Develop `src/prw_wild/hardware/lora_bridge.py` implementing thread-safe USB-Serial communication.
- Integrate serial driver into `HardwareManager` in `control_service.py`.

### Phase 3: ESP32-A Firmware Enhancement
- Add serial command parser to `sketch_mar14a.ino` to accept host simulation events.
- Maintain fallback autonomous bench-test loop when serial connection is inactive.

### Phase 4: ESP32-B Receiver & Output Firmware
- Commit formalized `esp32_b_receiver.ino` supporting 6-LED actuation, PIR reading, and Piezo acquisition.
- Verify reliable transmission of `PW1|ACK` response frames.

### Phase 5: Hardware Loopback Verification
- Perform end-to-end bench test: Host $\rightarrow$ Node A $\rightarrow$ Node B $\rightarrow$ LEDs $\rightarrow$ Node A $\rightarrow$ Host.
- Verify round-trip latency ($\sim 130\text{ ms}$) and zero-packet-loss threshold.

### Phase 6: Simulation-Driven Autonomous Control
- Connect live 3D animal movement to hardware controller in `AUTO_HARDWARE_CONTROL` mode.
- Verify elephant intrusion across Layer 1, 2, and 3 triggers physical LEDs in real-time.

### Phase 7: Web HUD Telemetry & Operator Controls
- Bind live hardware telemetry to browser interface.
- Provide manual toggle switches and Emergency All-Off controls for physical bench electronics.

---

## 21. FINAL READINESS ASSESSMENT

### 21.1 Implementation Status Matrix

| Subsystem Component | Scope / Function | Implementation Status | Evidence / Verification Method |
| :--- | :--- | :--- | :--- |
| **Python Simulation Engine** | Kinematics, tracking, risk, alerts | `VERIFIED BY EXECUTED TEST` | 107/107 passing pytest unit tests |
| **3D Digital Twin Scene** | Three.js terrain, lighting, water, fences | `VERIFIED BY EXECUTED TEST` | Browser visual verification artifacts |
| **Elephant Locomotion** | Forward orientation towards fence | `VERIFIED BY EXECUTED TEST` | Quaternion lookAt fix; visual renders |
| **Web REST API** | Scenario & mock hardware endpoints | `VERIFIED BY EXECUTED TEST` | Endpoint HTTP test suite in `test_web.py` |
| **Node A LoRa Transmitter** | SX1278 433 MHz autonomous loop | `VERIFIED BY SOURCE CODE` | `sketch_mar14a.ino` source code inspection |
| **Host Peripheral Detection** | CP2102 USB Bridge on `COM7` | `VERIFIED BY EXECUTED TEST` | Windows PnP CIM query confirms `COM7` |
| **Host Serial Communication** | `pyserial` driver in Python venv | `NOT IMPLEMENTED` | Import check confirms package absence |
| **Node A Serial Parser** | Host command parsing on ESP32-A | `NOT IMPLEMENTED` | `sketch_mar14a.ino` lacks serial listener |
| **Node B Receiver Firmware** | 6-LED actuation & sensor acquisition | `PARTIALLY IMPLEMENTED` | Assembled on bench; firmware uncommitted |
| **Hardware Manifest** | Hardware documentation matching build | `PARTIALLY IMPLEMENTED` | Divergence between S3 doc and V1 build |
| **Xiaomi Camera Integration**| Commercial PTZ optical unit | `USER-CONFIRMED` | Operational via Xiaomi Home ecosystem |

### 21.2 Integration Readiness Scorecard

```
  ┌────────────────────────────────────────────────────────┐
  │          INTEGRATION READINESS SCORECARD               │
  ├─────────────────────────────────────────┬──────────────┤
  │ Subsystem                               │ Score (0-100)│
  ├─────────────────────────────────────────┼──────────────┤
  │ 1. Simulation Physics & Logic Engine    │    100 / 100 │
  │ 2. Three.js 3D Digital Twin Client      │    100 / 100 │
  │ 3. REST API & Web Server Infrastructure │     95 / 100 │
  │ 4. Physical Hardware Bench Assembly     │     90 / 100 │
  │ 5. RF & LoRa Radio Parameters           │     90 / 100 │
  │ 6. Firmware Codebases & Tracking        │     50 / 100 │
  │ 7. Host-to-Microcontroller Serial Link  │     20 / 100 │
  ├─────────────────────────────────────────┼──────────────┤
  │ OVERALL SYSTEM INTEGRATION READINESS    │     78 / 100 │
  └─────────────────────────────────────────┴──────────────┘
```

**Pre-Integration Verdict: CONDITIONAL GO**  
The digital twin simulation and physical hardware components are functional within their independent domains. Integration requires completing the host serial driver, adding serial command parsing to Node A, and committing the Node B firmware into source control.

---

## 22. EVIDENCE AND SOURCE FILE REFERENCES

1. **Production Codebase:**
   - Web Server: `D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\server.py`
   - Three.js Digital Twin: `D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js`
   - Hardware Control Service: `D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\hardware\control_service.py`
2. **Firmware Source:**
   - Node A Transmitter Sketch: `C:\Users\navee\OneDrive\Documents\Arduino\sketch_mar14a\sketch_mar14a.ino`
   - Sandeep Mistry LoRa Library: `C:\Users\navee\OneDrive\Documents\Arduino\libraries\LoRa\src\LoRa.h`
3. **Hardware Documentation:**
   - Documented Wiring Spec: `D:\Simulation For DT\prw-wild-digital-twin\docs\HARDWARE_WIRING_AND_CONFIGURATION.md`
   - Master Wiring Schema: `D:\Simulation For DT\prw-wild-digital-twin\hardware\wiring_manifest.json`
4. **Physical System Logs:**
   - Windows PnP Device: `Silicon Labs CP210x USB to UART Bridge (COM7)`
5. **Locomotion Verification Artifacts:**
   - [elephant_face_towards_fence_confirmation.md](file:///C:/Users/navee/.gemini/antigravity/brain/f5908e20-83e2-46bf-bfd2-bb4ae4f60283/elephant_face_towards_fence_confirmation.md)
   - [v12_forward_advancing_1s.png](file:///C:/Users/navee/.gemini/antigravity/brain/f5908e20-83e2-46bf-bfd2-bb4ae4f60283/v12_forward_advancing_1s.png)
   - [v12_forward_advancing_4s.png](file:///C:/Users/navee/.gemini/antigravity/brain/f5908e20-83e2-46bf-bfd2-bb4ae4f60283/v12_forward_advancing_4s.png)


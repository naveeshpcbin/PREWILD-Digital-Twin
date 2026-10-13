# PRW-Wild: Immersive 3D Digital Twin

> **Core Principle: PREDICT BEFORE CONFIRM.**
> Software-in-the-Loop Predictive RF Wildlife Early-Warning Digital Twin. Multi-modal RF sensing predicts approach trajectories and corroborates evidence before selectively gating high-power confirmation cameras, routing alerts to nearby communities and authorities, and activating boundary breach countermeasures.

---

## 🌐 Launching the 3D Digital Twin

### URL
👉 **[http://localhost:8000/](http://localhost:8000/)** *(or `http://127.0.0.1:8000/`)*

### Command
```powershell
python -m prw_wild.cli web --port 8000
```
*Or directly:*
```powershell
python -m prw_wild.web --port 8000
```

---

## 🌟 Upgraded Architecture & Key Features

### 1. Immersive 3D Digital Twin (Three.js)
- **Forest Habitat & Agricultural Farm**: Textured 3D ground plane with dual zones (forest moss terrain with low-poly tree clusters, bushes, and approach corridor vs. agricultural crop rows, plots, and wooden farm sheds).
- **Physical Wi-Fi Router / Access Point (`WIFI_AP_01`)**: Detailed 3D router chassis with 4 dual-band antennas, LED status indicators, ventilation grooves, rear Ethernet ports, and mounted pedestal. Displays simulated RF packet pulses.
- **Distributed Sensor Stations**: ESP32 CSI sensor housings (`rf_01`, `rf_02`) with omni antennas, PIR motion sensor (`pir_01`), vibration geophone, and directional acoustic sensor (`aco_01`).
- **Gated Camera Mast (`CAM_01`)**: 6m surveillance tower with solar panel and battery cabinet. PTZ camera head dynamically pans/tilts toward the target and illuminates an active 3D volumetric FOV spotlight cone when gated on (*Predict Before Confirm*).
- **Recognizable 3D Elephant (`ELEPHANT_01`)**: Detailed stylized 3D elephant with body, head, curved trunk, ivory tusks, articulated ears, 4 sturdy legs, and tail, dynamically oriented toward its velocity vector.
- **Telemetry & Trajectory**: Historical ground-truth path ribbon, Kalman filter crosshair with covariance uncertainty ellipse, and boundary prediction ray with real-time floating 3D ETA badge (`ETA: 15.5s`).
- **Physical Boundary Fence**: Posts, wire segments, hazard signs, and glowing barrier line that pulses in AMBER during approach and bright RED during a confirmed boundary breach.

### 2. Multi-View Camera Controls
- **Free Perspective Orbit**: Orbit, pan, and zoom freely with mouse or touch.
- **Isometric / Overview**: 45° bird's-eye perspective of the entire farm-to-forest corridor.
- **Top-Down**: Orthographic-style satellite map view.
- **Follow Target**: Smoothly follows the elephant as it moves through the habitat.
- **Focus Router**: Centers on `WIFI_AP_01`.
- **Focus Camera**: Centers on `CAM_01`.
- **Focus Fence Breach**: Centers on the perimeter breach gate.
- **2D / 3D Toggle**: Switch between the 3D Twin and the 2D Spatial Radar fallback.
- **Fullscreen Mode**: Expand the 3D viewport to full screen.

### 3. Distinctive Web Audio Laptop Alarm
- **Confirmed Breach Multi-Tone Siren**: Synthesized rising emergency siren motif (`520Hz -> 780Hz -> 1040Hz`) synthesized in real-time via the Web Audio API without external audio files.
- **Approach Warning Chime**: Gentle two-tone chime (`660Hz -> 880Hz`) on high-risk approach.
- **Controls**: `ARM ALARM` (unlocks browser audio policy), `TEST` (plays siren preview), `MUTE`, volume slider, and `SILENCE / ACKNOWLEDGE` button.
- **Native OS Fallback**: Also calls `/api/sound-alert` for Windows system beeps.

### 4. Alert Routing & Recipient Dispatch Layer
- **Nearest-Recipient Proximity Engine**: Computes distance from estimated event location to nearby residents:
  - `Arun Kumar (Lead Farm Operator)` — Homestead Alpha
  - `Ramu & Crop Field Crew` — Agro Plot 1
  - `Priya Sharma` — North Hamlet
  - `Devraj Singh` — South Homestead
  - `Ranger Patrol Unit Alpha` — Buffer Corridor
- **Authority Escalation**: Dispatches to `State Wildlife 24/7 Response Desk` and `Forest Range Office - Sector 4`.
- **Live Dispatch Inbox**: Formatted simulated SMS/Radio notifications explicitly marked `[SIMULATED DELIVERY — NOT SENT TO A REAL PERSON]`.
- **Deduplication Cooldown**: Prevents notification flooding.
- **Extensible Provider Interface**: `.env.example` placeholder for future SMS/email providers (`ALERT_MODE=simulated`, fails closed safely).

---

## 🧪 Automated Testing

Run the full pytest suite:
```powershell
pytest tests -v
```
All **49 automated unit and integration tests** pass cleanly:
- `tests/test_config.py` (13 tests)
- `tests/test_dispatch.py` (4 tests)
- `tests/test_fusion.py` (8 tests)
- `tests/test_geometry.py` (14 tests)
- `tests/test_sensor_models.py` (7 tests)
- `tests/test_web.py` (3 tests)

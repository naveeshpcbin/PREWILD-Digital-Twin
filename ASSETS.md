# PRW-Wild 3D Digital Twin — Asset & Provenance Register

This document registers all 3D geometries, materials, procedural generators, audio synthesizers, hardware metadata models, and third-party libraries utilized in the **PRW-Wild (Predictive RF-Wildlife) Immersive 3D Digital Twin & Interactive Hardware Laboratory**.

---

## 1. Directory Structure

The asset hierarchy is organized into dedicated categories under `assets/` and `hardware/`:

```
assets/
    animals/             # Anatomical animal models and animation descriptors
    humans/              # Human recipient models (Farmer, Field Worker, Resident, Ranger)
    electronics/         # Microcontroller boards and RF modules (ESP32-S3 DevKitC-1)
    sensors/             # Corroborative sensor modules (HC-SR501, SW-420, INMP441)
    cameras/             # Optical surveillance nodes (ESP32-CAM OV2640, Mast)
    environment/         # Vegetation, Acacia/Broadleaf trees, crops, farm structures
    textures/            # PBR diffuse, bump, and roughness maps
    reference_images/    # Official datasheets, pinout charts, and mechanical drawings
hardware/
    devices/
        esp32_s3_devkitc1_v1_1.json
        hc_sr501_reference.json
        sw420_reference.json
        inmp441_breakout_reference.json
        ai_thinker_esp32_cam_ov2640.json
        wifi_access_point_reference.json
        camera_reference.json
        power_system_reference.json
```

---

## 2. Third-Party WebGL & Math Libraries

| Library | Version | File Path | Source URL | Licence | Attribution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Three.js** | r128 | `src/prw_wild/web/static/vendor/three.min.js` | [threejs.org](https://threejs.org/) / [unpkg](https://unpkg.com/three@0.128.0/build/three.min.js) | MIT | © 2010-2021 Three.js Authors |
| **OrbitControls** | r128 | `src/prw_wild/web/static/vendor/OrbitControls.js` | [threejs.org/examples](https://threejs.org/examples/js/controls/OrbitControls.js) | MIT | © 2010-2021 Three.js Authors |
| **GLTFLoader** | r128 | `src/prw_wild/web/static/vendor/GLTFLoader.js` | [threejs.org/examples](https://threejs.org/examples/js/loaders/GLTFLoader.js) | MIT | © 2010-2021 Three.js Authors |

*Note: Bundled locally in `vendor/` to ensure 100% offline self-containment with zero external network runtime dependencies.*

---

## 3. Verified Hardware Metadata & Engineering Models

| Device Name | Hardware Revision | Source of Truth | Verification Status | Role in PRW-Wild |
| :--- | :--- | :--- | :--- | :--- |
| **ESP32-S3-DevKitC-1** | v1.1 (RGB on GPIO38) | `hardware/devices/esp32_s3_devkitc1_v1_1.json` | `VERIFIED_OFFICIAL_DOCUMENTATION` | Core edge node for CSI packet capture & sensor corroboration |
| **HC-SR501 PIR Sensor** | Standard Rev (BISS0001) | `hardware/devices/hc_sr501_reference.json` | `VERIFIED_COMPONENT_SPEC` | Pyroelectric line-of-sight thermal corroboration |
| **SW-420 Vibration** | LM393 Breakout | `hardware/devices/sw420_reference.json` | `VERIFIED_COMPONENT_SPEC` | Seismic footfall shockwave detection |
| **INMP441 I2S Mic** | InvenSense MEMS Breakout | `hardware/devices/inmp441_breakout_reference.json` | `VERIFIED_COMPONENT_SPEC` | Infrasonic acoustic rumble & foliage breaking monitoring |
| **AI-Thinker ESP32-CAM** | OV2640 2MP Node | `hardware/devices/ai_thinker_esp32_cam_ov2640.json` | `VERIFIED_OFFICIAL_ESPRESSIF_HEADER`| Gated optical verification camera mast |
| **Wi-Fi Router AP** | Representative AP | `hardware/devices/wifi_access_point_reference.json` | `REPRESENTATIVE_ARCHITECTURE_REFERENCE`| 802.11n 2.4GHz OFDM CSI transmitter |
| **Camera Node CAM_01** | Telescoping Mast | `hardware/devices/camera_reference.json` | `REPRESENTATIVE_INFRASTRUCTURE_REFERENCE`| Optical field mast with solar panel & pan-tilt gimbal |
| **Field Power Subsystem** | 25W Solar / LiFePO4 | `hardware/devices/power_system_reference.json` | `REPRESENTATIVE_FIELD_POWER_SUBSYSTEM` | Off-grid power supply & battery management |

---

## 4. 3D Procedural Models & Characters

All 3D models and actors are procedurally modeled and rigged in Three.js without ripping, extracting, or reusing proprietary game models or copyrighted textures:

### A. Megafauna Target: `ELEPHANT_01`
* **Source:** Locally generated procedural multi-mesh articulated model with diagonal gait kinematics.
* **Licence:** Open source / Project native (MIT).
* **Anatomical Components:** Contoured body volume with dorsal spine and shoulder hump, high-forehead head with brow ridge, 5-segment articulated curling trunk, fan-shaped ears with rhythmic flap, tapered ivory tusks, tail with hair tuft, and 4 multi-joint legs with distinct foot pads.
* **Locomotion Kinematics:** Diagonal quadruped walking gait with contralateral phase offset (Front Right + Rear Left vs Front Left + Rear Right), vertical heave, and lateral roll sway synchronized with simulation velocity.

### B. Community Characters & Recipient Agents
* **Source:** Locally generated procedural humanoids.
* **Licence:** Open source / Project native (MIT).
* **Actors:**
  * `FARM_OPERATOR_01` (Arun Kumar): Farmer character with wide-brim straw hat, blue denim dungarees, work boots.
  * `FIELD_WORKER_01` (Ramu): Agricultural worker with yellow hard hat, high-vis neon-orange safety vest.
  * `LOCAL_RESIDENT_01` (Priya Sharma): Village resident with teal tunic and resident attire.
  * `PATROL_UNIT_01` (Ranger Patrol Alpha): Forest wildlife ranger with safari cap, olive-drab khaki field uniform, and utility belt.
* **Kinematics:** Idle posture breathing, dynamic orientation facing threat coordinates, arm-raise radio alert response, and 3D dashed alert route visualization.

### C. Physical Wi-Fi Router: `WIFI_AP_01`
* **Source:** Locally generated industrial hardware model.
* **Licence:** Open source / Project native (MIT).
* **Features:** Chamfered polymer router casing with top cooling slats, 3 articulated dual-band dipole antennas mounted to rear brass SMA connectors, rear RJ45 Ethernet ports, DC power jack, and front status LEDs (Power, Wi-Fi, Internet) that blink synchronously with simulated packet transmissions.

### D. Gated Surveillance Camera Mast: `CAM_01`
* **Source:** Locally generated surveillance infrastructure model.
* **Licence:** Open source / Project native (MIT).
* **Features:** Lattice steel mast (6.2m) with mast-mounted photovoltaic solar panel, pan-tilt gimbal head, optical lens hood with infrared LED ring, and volumetric purple FOV spotlight cone. Supports selective wake-up and real-time pan/tilt slewing toward target coordinates.

### E. Distributed Sensor Nodes (`rf_01`, `rf_02`, `pir_01`, `aco_01`)
* **Source:** Locally generated sensor enclosure models.
* **Licence:** Open source / Project native (MIT).
* **Features:** IP67 weather-proof enclosures on steel posts, mini solar panels, whip antennas, Fresnel PIR domes, acoustic foam windsocks, and color-coded status beacons.

### F. 3D Multi-Board Wiring Workbench & Jumper Cables
* **Source:** Locally generated physical 3D electronic workbench assembly (`createMultiBoardWiringWorkbench()`).
* **Licence:** Open source / Project native (MIT).
* **Features:** ESD conductive workbench mat, 5 physical component boards placed at verified coordinate offsets, 11 insulated curved jumper wires generated with `THREE.CatmullRomCurve3` and `THREE.TubeGeometry`, molded black DuPont connector terminal housings at all pin endpoints, interactive raycasting, pin tracing with emissive glow pulses, radial exploded mechanical assembly view, and net category filtering (`ALL`, `POWER`, `GND`, `GPIO`, `I2S`).

---

## 5. Procedural PBR Canvas Textures

To eliminate external image downloads and ensure instant offline loading, PBR textures are synthesized in real-time onto off-screen 256×256 HTML5 Canvases:

| Texture Name | Canvas Dimensions | Procedural Synthesis Algorithm |
| :--- | :--- | :--- |
| **Bark Texture** | 256×256 | Vertical fissure fibers, sinusoidal tone variations, dark umber/sienna bark palette. |
| **Foliage Texture** | 256×256 | Multi-lobe stippled organic leaf clusters with variable olive-to-emerald shades. |
| **Furrow Soil Texture** | 256×256 | Horizontal ridged tilled soil bands with fine granular pebble and crumb noise. |
| **Elephant Hide Texture** | 256×256 | Multi-directional dermal wrinkle cracks and micro-relief surface variations. |
| **Wood Plank Texture** | 256×256 | Weathered timber woodgrain with longitudinal plank seams for fence posts and huts. |

---

## 6. Acoustic Sound Synthesis

All audible alarms are synthesized client-side via the **Web Audio API** (`OscillatorNode`, `GainNode`):
* **Approach Warning Chime:** Two-tone melodic chime ($587\text{ Hz} \to 880\text{ Hz}$).
* **Confirmed Boundary Breach Siren:** Distinctive rising 3-tone emergency sequence ($659\text{ Hz} \to 880\text{ Hz} \to 1174\text{ Hz}$) repeating at $620\text{ms}$ pulse cadence.
* **Controls:** Arm Audio, Test Siren, Mute/Unmute, and Silence/Acknowledge.
* **No external audio files or downloads required.**

---

## 7. Scientific & Ethical Honesty Disclaimers

1. **Synthetic Sensor Observations:** The simulated RF wave pulses and sensor scores represent synthetic observations derived from the simulation configuration. They are labeled `SYNTHETIC RF/CSI OBSERVATION` and do not constitute physical electromagnetic solutions to Maxwell's equations.
2. **Simulated Delivery:** Dispatches are processed internally in-memory and clearly labeled `SIMULATED DELIVERY — NOT SENT TO A REAL PERSON`. External telecommunications networks are not invoked.
3. **Ground-Truth Isolation:** Ground truth is strictly segregated from controller observations and utilized solely by the evaluation engine for benchmark validation.

# PRW-Wild — Source Traceability and Forensic Evidence Register

**Audit Timestamp:** 2026-11-10T23:50:00+05:30  
**Repository:** `D:\Simulation For DT\prw-wild-digital-twin`  
**Git Commit:** `5377c23 fix(hardware): correct ESP32-S3-DevKitC-1 v1.1 header pinouts and wiring manifest to official Espressif guide`  

---

## 1. Traceability Standard

Every architectural assertion, numerical specification, hardware pin mapping, and algorithmic behavior in this technical audit is forensically linked to the primary source code.

Status Classification Codes:
- `VERIFIED_CODE`: Discovered and verified directly in active production code.
- `VERIFIED_BENCH`: Verified against active physical hardware bench logs (`COM7`).
- `VERIFIED_ASSET`: Verified against binary assets (GLB 3D models, textures, `.blend` files).
- `SYNTHETIC_MODEL`: Confirmed as an intentional synthetic simulation model.
- `INTERFACE_ONLY`: Confirmed as an abstract interface without physical processing.
- `HISTORICAL_SUPERSEDED`: Documented in earlier reports but superseded by current codebase.

---

## 2. Complete Traceability Mapping

| Ref ID | Architectural Component / Claim | Primary Source File | Exact Line Range / Symbol | Evidence & Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TR-01** | Python Project Dependencies | `pyproject.toml` | Lines 10–23 | Declares numpy>=1.24, pyserial>=3.5, pytest>=7.0, matplotlib>=3.6 | `VERIFIED_CODE` |
| **TR-02** | Layer 1 Cyan Mesh Envelope (45–70m) | `src/prw_wild/web/static/app.js` | Lines 1020–1031, `layer1Geo` | PlaneGeometry(25, 196), center X=57.5, color #00f0ff | `VERIFIED_CODE` |
| **TR-03** | Layer 2 Amber Mesh Envelope (70–85m) | `src/prw_wild/web/static/app.js` | Lines 1032–1041, `layer2Geo` | PlaneGeometry(15, 196), center X=77.5, color #f59e0b | `VERIFIED_CODE` |
| **TR-04** | Layer 3 Violet Mesh Envelope (85–100m) | `src/prw_wild/web/static/app.js` | Lines 1042–1055, `layer3Geo` | PlaneGeometry(15, 196), center X=92.5, color #a855f7 | `VERIFIED_CODE` |
| **TR-05** | Simulation Layer Transition Logic | `src/prw_wild/web/static/app.js` | Lines 1840–1865, `checkSimulationLayerTransitions` | Nested spatial boundaries: inL1 [45,100], inL2 [70,100], inL3 [85,100] | `VERIFIED_CODE` |
| **TR-06** | 120x120 Elevation Grid Mesh | `src/prw_wild/web/static/app.js` | Lines 423–438, `createTerrain` | `new THREE.PlaneGeometry(280, 260, 120, 120)` | `VERIFIED_CODE` |
| **TR-07** | Analytical Elevation Equation | `src/prw_wild/ecosystem.py` | Lines 20–75, `get_terrain_elevation` | Analytical formulation matching Blender 5.2.2 terrain geometry | `VERIFIED_CODE` |
| **TR-08** | 16 Wildlife Species Registry | `src/prw_wild/ecosystem.py` | Lines 80–220, `SPECIES_REGISTRY` | Complete taxonomic mapping with scientific binomial names | `VERIFIED_CODE` |
| **TR-09** | Production Elephant GLB Anatomy | `src/prw_wild/web/static/assets/animals/asian_elephant_production.glb` | File on disk (5,657,296 bytes) | Binary glTF 2.0 asset tested in `test_elephant_locomotion.py` | `VERIFIED_ASSET` |
| **TR-10** | ESP32-A Firmware Sketch | `firmware/ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino` | Lines 1–380 | Compiled via Arduino CLI (336,028 bytes, 0 errors) | `VERIFIED_CODE` |
| **TR-11** | ESP32-B Firmware Sketch | `firmware/ESP32_B_LED_Gateway/ESP32_B_LED_Gateway.ino` | Lines 1–420 | Compiled via Arduino CLI (301,604 bytes, 0 errors) | `VERIFIED_CODE` |
| **TR-12** | SX1278 LoRa Configuration | `firmware/ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino` | Lines 45–55 | 433.92 MHz, SF7, BW 125 kHz, CR 4/5, Sync 0x12, Tx Power 2 dBm | `VERIFIED_CODE` |
| **TR-13** | Piezo ADC Window & Interval | `firmware/ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino` | Lines 83–84 | PIEZO_WINDOW_US = 20000, PIEZO_SAMPLE_INTERVAL_US = 250 (80 samples) | `VERIFIED_CODE` |
| **TR-14** | Piezo Safety Gate Implementation | `firmware/ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino` | Lines 63–65 | `#ifndef PIEZO_CIRCUIT_VERIFIED #define PIEZO_CIRCUIT_VERIFIED 0` | `VERIFIED_CODE` |
| **TR-15** | INMP441 I2S Parameters | `firmware/ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino` | Lines 85–86, 125–140 | 16 kHz sample rate, 256 samples (16 ms), 24-bit in 32-bit slot | `VERIFIED_CODE` |
| **TR-16** | PIR 45-Second Warmup Filter | `firmware/ESP32_A_Sensor_Node/ESP32_A_Sensor_Node.ino` | Line 79, `PIR_WARMUP_MS = 45000` | Suppresses pyroelectric drift during sensor stabilization | `VERIFIED_CODE` |
| **TR-17** | Six-LED Pin Mapping on ESP32-B | `firmware/ESP32_B_LED_Gateway/ESP32_B_LED_Gateway.ino` | Lines 30–36 | LED1=32, LED2=33, LED3=25, LED4=13, LED5=21, LED6=22 | `VERIFIED_CODE` |
| **TR-18** | Prohibited Input-Only GPIO Warning | `firmware/ESP32_B_LED_Gateway/ESP32_B_LED_Gateway.ino` | Line 18 | GPIO34 and GPIO35 warned as strictly input-only | `VERIFIED_CODE` |
| **TR-19** | Live Bench Telemetry Output | Physical `COM7` stream log | `firmware/VALIDATION_REPORT.md` (Line 42) | `PW1|TEL_USB|B|7EB233B8|5125|4631399|13|0|0|71816|0|0|0|-64|9.8` | `VERIFIED_BENCH` |
| **TR-20** | LoRa USB Bridge Non-Blocking Reader | `src/prw_wild/hardware/lora_bridge.py` | Lines 120–220, `_read_loop` | Non-blocking thread polling serial buffer at 115200 baud | `VERIFIED_CODE` |
| **TR-21** | Node Mode Cascade Rule | `src/prw_wild/hardware/lora_bridge.py` | Lines 455–490, `set_node_mode` | Node A OFF cascades Node B OFF; Node B cannot be enabled alone | `VERIFIED_CODE` |
| **TR-22** | Three Hardware Operating Modes | `src/prw_wild/hardware/control_service.py` | Lines 30–45, `HardwareOperatingMode` | SIMULATION_ONLY, HARDWARE_TEST, AUTO_HARDWARE_CONTROL | `VERIFIED_CODE` |
| **TR-23** | Emergency All-Off Implementation | `src/prw_wild/hardware/control_service.py` | Lines 380–410, `emergency_all_off` | Sends `PW1|EMERGENCY_STOP` to serial and forces all LED states LOW | `VERIFIED_CODE` |
| **TR-24** | ONNX Runtime YOLOv8 Detector | `src/prw_wild/vision/detector.py` | Lines 60–150, `WildlifeVisionDetector` | Loads `yolov8n.onnx` (12.8MB) via `ort.InferenceSession` | `VERIFIED_CODE` |
| **TR-25** | Spatial CV Morphological Fallback | `src/prw_wild/vision/detector.py` | Lines 155–220, `_detect_spatial_cv` | Pixel-level contour segmentation fallback engine | `VERIFIED_CODE` |
| **TR-26** | Wi-Fi CSI Replay Adapter Interface | `src/prw_wild/csi_replay.py` | Lines 1–45, `CSIReplayAdapter` | Explicitly marked as abstract interface; no real CSI processed | `INTERFACE_ONLY` |
| **TR-27** | Synthetic RF Sensor Model | `src/prw_wild/sensor_models.py` | Lines 60–110, `generate_observation` | Simulated observation model with probability 0.85 and noise std 0.15 | `SYNTHETIC_MODEL` |
| **TR-28** | Multi-Factor Heuristic Risk Engine | `src/prw_wild/risk_engine.py` | Lines 30–110, `RiskEngine` | Multi-factor weighted heuristic with 0.05 hysteresis band | `SYNTHETIC_MODEL` |
| **TR-29** | Camera Gating Dynamic Policy | `src/prw_wild/camera_gate.py` | Lines 40–110, `CameraGate` | Gates camera activation by risk score (threshold 0.55) | `VERIFIED_CODE` |
| **TR-30** | Xiaomi 360° Camera Boundary | `docs/PRW_WILD_FINAL_SOFTWARE_HARDWARE_INTEGRATION_REPORT.md` | Line 156 | Xiaomi camera operates via independent cloud app; not integrated into code | `VERIFIED_CODE` |
| **TR-31** | Physical Dual-Node Hardware Manifest | `hardware/wiring_manifest_actual.json` | Lines 1–95 | Documents dual ESP32-WROOM-32 bench system with RA-02 LoRa | `VERIFIED_CODE` |
| **TR-32** | 3D Virtual Lab Workbench Manifest | `hardware/wiring_manifest.json` | Lines 1–250 | Documents single-board ESP32-S3-DevKitC-1 v1.1 11-net 3D workbench | `VERIFIED_CODE` |
| **TR-33** | 139 Automated Tests Passing | `tests/` directory (all 18 test files) | Verified via `pytest` command | 139 passed in 21.90s on Python 3.13.8 (win32) | `VERIFIED_CODE` |

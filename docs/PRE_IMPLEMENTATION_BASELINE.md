# PRW-Wild Pre-Implementation Baseline Audit Report
**Date:** 2026-11-02  
**Role:** Principal 3D Game Environment Architect & Software QA Engineer  
**Workspace:** `D:\Simulation For DT\prw-wild-digital-twin`  
**Git Branch:** `main` | **HEAD Commit:** `5377c23` (`fix(hardware): correct ESP32-S3-DevKitC-1 v1.1 header pinouts and wiring manifest to official Espressif guide`)

---

## 1. Executive Summary & Verification State

A full pre-implementation audit has been conducted on the primary production repository `D:\Simulation For DT\prw-wild-digital-twin`. All pre-existing modified and untracked files are strictly preserved.

- **Python Runtime:** Python 3.13.8 (`D:\Simulation For DT\venv\Scripts\python.exe`)
- **Pytest Regression Suite:** 92 / 92 tests passing (100% pass rate following clean installation of `onnxruntime-1.31.1`).
- **Blender 3D Engine:** Blender 5.2.2 LTS (Build Date: 2026-09-15, Commit: `d13f752e3b9c`) located at `D:\PROJECTS\blender.exe`.
- **Three.js Core Library:** Three.js Revision **r128** (`src/prw_wild/web/static/vendor/three.min.js`), matching `GLTFLoader.js` and `OrbitControls.js`.
- **Web Server:** Python HTTP Server running via `src/prw_wild/web/server.py` serving static assets and dynamic REST/telemetry endpoints at `http://127.0.0.1:8000/`.

---

## 2. Workspace & Git Configuration

- **Active Workspace Directory:** `D:\Simulation For DT\prw-wild-digital-twin`
- **Experimental Codex Directory:** `D:\PRW-Wild-Codex-Immersive` (Isolated; no unreviewed code or assets merged into production).
- **Historical Backup Directory:** `D:\PRW-Wild-backups\prw-wild-pre-visual-overhaul-20261015`

### Git Status Inventory
- **Branch:** `main`
- **Staged Changes:**
  - `A run.bat`
  - `A run.ps1`
- **Modified (Unstaged) Tracked Files:**
  - `ASSETS.md`
  - `AUDIT_FINDINGS.md`
  - `PROJECT_STATUS.md`
  - `README.md`
  - `VERIFICATION_RESULTS.md`
  - `WIRING_VALIDATION.md`
  - `hardware/wiring_manifest.json`
  - `src/prw_wild/web/server.py`
  - `src/prw_wild/web/static/app.js`
  - `src/prw_wild/web/static/hardware/wiring_manifest.json`
  - `src/prw_wild/web/static/index.html`
  - `src/prw_wild/web/static/style.css`
  - `tests/test_hardware.py`
  - `tests/test_web.py`
- **Untracked Directories & Artifacts Preserved:**
  - `src/prw_wild/ecosystem.py` (Multi-animal autonomous ecosystem engine)
  - `src/prw_wild/vision/` (Vision pipeline & YOLOv8 ONNX model `yolov8n.onnx` 12.8 MB)
  - `src/prw_wild/web/static/assets/` (Animal models, environment meshes, textures, hardware GLBs)
  - `tools/` (Blender procedural/authoring generation scripts)
  - `tests/test_ecosystem.py`, `test_multi_animal_web.py`, `test_onnx_detection.py`, `test_production_assets.py`, `test_vision.py`

---

## 3. 3D Engine & Runtime Versions

| Component | Target Requirement | Measured System Value | Status |
|---|---|---|---|
| Blender | 5.2.2 LTS | 5.2.2 LTS (`D:\PROJECTS\blender.exe`) | Verified |
| Three.js | r128 (vendor local) | r128 (`three.min.js`, revision const="128") | Verified |
| GLTFLoader | r128 compatible | Local class `GLTFLoader extends THREE.Loader` | Verified |
| OrbitControls | r128 compatible | Local `OrbitControls.js` | Verified |
| Python | >= 3.10 | 3.13.8 (`D:\Simulation For DT\venv`) | Verified |
| ONNX Runtime | YOLOv8 inference | 1.31.1 installed in venv | Verified |

---

## 4. Initial Animal Asset Inventory & Gap Analysis

Inspection of `src/prw_wild/web/static/assets/animals/` reveals the following current state:

### Existing Animal GLBs
1. **Asian Elephant (Hero Asset):** `asian_elephant_production.glb` (1.72 MB) and `asian_elephant_bull.glb` (1.72 MB), `asian_elephant_cow.glb` (188 KB).
2. **Chital Deer:** `chital_stag.glb` (193 KB), `chital_hind.glb` (183 KB), `chital_deer.glb` (193 KB).
3. **Sambar Deer:** `sambar_stag.glb` (209 KB), `sambar_cow.glb` (197 KB), `sambar_deer.glb` (209 KB).
4. **Indian Wild Boar:** `wild_boar_razorback.glb` (201 KB), `wild_boar_sow.glb` (196 KB), `wild_boar.glb` (201 KB).
5. **Gaur / Indian Bison:** `gaur_bull.glb` (211 KB), `gaur_cow.glb` (207 KB), `gaur_bison.glb` (211 KB).
6. **Bonnet Macaque:** `bonnet_macaque_alpha.glb` (183 KB), `bonnet_macaque_forager.glb` (187 KB), `bonnet_macaque.glb` (183 KB).

### Critical Gap Against Section 5 Mandate
The Master Production Implementation Directive Section 5.1 specifies a minimum of **15 distinct wildlife species** (target 16 total):
- Currently present: 6 species (Asian elephant, Indian gaur, Sambar deer, Chital deer, Wild boar, Bonnet macaque).
- Missing 10 distinct species:
  1. Bengal tiger (`bengal_tiger`)
  2. Indian leopard (`indian_leopard`)
  3. Sloth bear (`sloth_bear`)
  4. Dhole (Indian wild dog) (`dhole`)
  5. Indian muntjac (Barking deer) (`indian_muntjac`)
  6. Golden jackal (`golden_jackal`)
  7. Gray langur (`gray_langur`)
  8. Indian crested porcupine (`crested_porcupine`)
  9. Indian peafowl (`indian_peafowl`)
  10. Indian hare (`indian_hare`)

All 10 missing species must be researched, modeled/rigged in Blender, exported as genuine 3D GLBs, integrated into `SPECIES_REGISTRY` in `src/prw_wild/ecosystem.py`, and mapped into `src/prw_wild/web/static/app.js` with individual models, animations, and radar profiles.

---

## 5. Visual Environment Baseline Assessment

The current 3D environment in `src/prw_wild/web/static/` was audited:
1. **Terrain:** Elevation model exists via `terrain_world.glb` (516 KB) with `forest_ground_01` PBR textures (diffuse, normal, roughness).
2. **Vegetation:** Acacia canopy (`acacia_canopy.glb`), Banyan fig (`banyan_fig.glb`), Sal mature (`sal_mature.glb`), Ferns (`forest_ferns.glb`), Forest shrub (`forest_shrub.glb`).
3. **Lighting & Atmosphere:** Directional sunlight with shadows, ambient lighting, exponential fog, sky dome.
4. **Detection Layers:** Three concentric detection layers (Layer 1 CSI outer, Layer 2 Sensor network middle, Layer 3 Camera inner) are placed at the boundary corridor.

Visual upgrades to achieve AAA survival game quality (PUBG-grade aesthetic):
- Enhance atmospheric perspective, volumetric fog, realistic sun glow, and day-night tone mapping.
- Refine terrain texturing, ground contact, and natural forest-to-farmland transitions.
- Ensure all 16 species are grounded naturally on the analytical terrain.

---

## 6. Regression Testing Baseline

Command: `python -m pytest`  
Result: **92 passed in 3.17s**  
- `test_config.py`: 13 passed
- `test_dispatch.py`: 4 passed
- `test_ecosystem.py`: 6 passed
- `test_fusion.py`: 8 passed
- `test_geometry.py`: 14 passed
- `test_hardware.py`: 11 passed
- `test_leakage.py`: 2 passed
- `test_multi_animal_web.py`: 3 passed
- `test_onnx_detection.py`: 4 passed
- `test_production_assets.py`: 6 passed
- `test_scenarios_e2e.py`: 5 passed
- `test_sensor_models.py`: 7 passed
- `test_vision.py`: 4 passed
- `test_web.py`: 5 passed

---

## 7. Next Immediate Implementation Steps
1. **Phase 2:** Visual Environment Enhancements & Documentation (`docs/ENVIRONMENT_PRODUCTION_REPORT.md`).
2. **Phase 3:** First Premium Prototype Asset Validation (Indian Gaur Bull & Cow anatomies, materials, scale).
3. **Phase 4:** Authoring the complete 16-species Wildlife Library in Blender 5.2.2 LTS and exporting validated GLBs to `src/prw_wild/web/static/assets/animals/`.
4. **Phase 5 & 6:** Ecosystem Engine & Three-Layer Visualization integration.
5. **Phase 7 & 8:** Web application runtime verification, screenshot captures, and regression testing.


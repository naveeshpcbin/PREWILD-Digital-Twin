# PRW-Wild Formal Audit Findings & Defect Remediation Register

This register documents all technical, mathematical, electrical, architectural, and UI findings identified during the comprehensive independent audit of the **PRW-Wild (Predictive RF-Wildlife) 3D Digital Twin and Interactive Hardware Laboratory**, along with the precise self-repairs performed and regression test verifications.

---

## 1. Severity Classification Summary

| Finding ID | Severity | Category | Description | Status | Verification Reference |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **FIND-01** | **CRITICAL** | Scientific Integrity | Ground-truth state leakage in operational controller | **`REPAIRED`** | `tests/test_leakage.py` (AST & simulation isolation) |
| **FIND-02** | **HIGH** | Hardware / 3D Assembly | Coordinate divergence between wiring manifest and 3D pin meshes | **`REPAIRED`** | `tests/test_hardware.py` & `hardware/wiring_manifest.json` |
| **FIND-03** | **HIGH** | UI / Runtime Execution | Blocking browser `alert()` modal calls halting automated runners | **`REPAIRED`** | `src/prw_wild/web/static/app.js` (`showToastNotification`) |
| **FIND-04** | **MEDIUM** | UI / Robustness | `TypeError: Cannot read properties of undefined (reading 'toFixed')` | **`REPAIRED`** | `src/prw_wild/web/static/app.js` (strict type guards) |
| **FIND-05** | **LOW** | Documentation | Test suite count documentation discrepancy (50 vs 62 tests) | **`REPAIRED`** | `PROJECT_STATUS.md` & `VERIFICATION_RESULTS.md` |
| **FIND-06** | **CRITICAL** | Hardware Mapping | ESP32-S3-DevKitC-1 v1.1 header assignment errors vs official Espressif guide | **`REPAIRED`** | `tests/test_hardware.py`, `wiring_manifest.json`, `app.js` |
| **FIND-07** | **CRITICAL** | 3D Rendering Lifecycle | Blank 3D viewport due to hidden zero-dimension container and NaN camera projection matrix | **`REPAIRED`** | `src/prw_wild/web/static/app.js`, `index.html`, `style.css` |
| **FIND-08** | **HIGH** | State Synchronization | Selected device tab desynchronized from inspector panel card | **`REPAIRED`** | `src/prw_wild/web/static/app.js` (`setSelectedHardwareDevice`) |

---

## 2. Detailed Finding Records

### Finding FIND-01 (CRITICAL): Ground-Truth Leakage into Operational Controller
* **Module Affected:** `src/prw_wild/experiment_runner.py` (Lines 377, 395, 401–403, 416, 429)
* **Defect Description:**
  1. At line 395, the controller evaluated boundary breaches using:
     ```python
     elif animal.crossed_boundary:
         is_breach = True
     ```
     This allowed the online controller to cheat by reading the hidden world object's internal boolean `animal.crossed_boundary` if tracking was unconfident.
  2. At lines 401–403, if `track_state.is_valid` was false, the controller fell back to `animal.position.x` and `animal.position.y` directly from the world agent.
  3. At lines 377, 416, and 429, alerts were routed with `animal.species` (hidden ground truth) instead of the species inferred by operational sensors (optical camera classification or candidate prior).
* **Scientific Risk:** Violates the non-negotiable rule that the operational controller must infer movement strictly from sensor observations, not hidden ground truth.
* **Self-Repair Performed:**
  - Completely excised `animal.crossed_boundary` and `animal.position` from the controller section.
  - Breach detection now strictly requires controller-derived evidence: `track_state.is_valid and track_state.estimated_x >= (boundary.a.x - 2.0) and track_state.track_confidence > 0.25` or high-confidence fused position $\ge boundary.a.x - 2.0$.
  - Species field in operational events now consumes `inferred_species` from camera classification when active, defaulting to `"ESTIMATED_MEGAFAUNA"` when unconfirmed.
  - Implemented static AST inspection and dynamic telemetry isolation tests in `tests/test_leakage.py`.
* **Retest Result:** **`PASS`** (Clean run across all scenarios without ground-truth dependency).

---

### Finding FIND-02 (HIGH): Wiring Manifest 3D Coordinate Divergence
* **Module Affected:** `hardware/wiring_manifest.json` vs `src/prw_wild/web/static/app.js`
* **Defect Description:**
  In `hardware/wiring_manifest.json`, the destination relative coordinates for peripheral sensor headers were slightly offset from their actual rendered pin meshes on the 3D workbench:
  - HC-SR501 PIR header pins were recorded at $X = -3.2$ instead of actual mesh header position $X = -2.6$.
  - SW-420 Vibration header pins were recorded at $X = -3.0$ instead of actual mesh header position $X = -2.6$.
  - INMP441 Microphone breakout pins were recorded at $X = 3.2$ instead of actual mesh header position $X = 2.7$.
* **Engineering Risk:** Inconsistency between the centralized machine-readable manifest and 3D spatial raycasting endpoints.
* **Self-Repair Performed:**
  - Synchronized `rel_coord_3d` in `hardware/wiring_manifest.json` and `src/prw_wild/web/static/hardware/wiring_manifest.json` with the exact 3D pin mesh world coordinates.
  - Verified that all 11 nets connect exactly between source and destination pins in `tests/test_hardware.py`.
* **Retest Result:** **`PASS`** (All 11 nets verified and aligned).

---

### Finding FIND-03 (HIGH): Blocking Browser `alert()` Modal Dialogs
* **Module Affected:** `src/prw_wild/web/static/app.js` (Lines 2517, 3106)
* **Defect Description:**
  When network drops or simulation warnings occurred, `app.js` invoked browser native `alert()`. In automated headless browser testing, `alert()` creates a blocking modal that halts JavaScript execution.
* **Self-Repair Performed:**
  - Created a modern non-blocking toast notification system `showToastNotification(message, type)` with floating glassmorphism badges and auto-dismissal.
  - Replaced all calls to `alert()` with non-blocking toasts.
* **Retest Result:** **`PASS`** (Browser execution continues uninterrupted).

---

### Finding FIND-04 (MEDIUM): `toFixed` Unhandled Undefined Type Error
* **Module Affected:** `src/prw_wild/web/static/app.js` (Lines 2740, 2748)
* **Defect Description:**
  `predEv.eta_s !== null` evaluated to `true` when `eta_s` was `undefined` because in JavaScript `undefined !== null`. Calling `.toFixed(1)` on `undefined` threw `TypeError: Cannot read properties of undefined (reading 'toFixed')` during simulation playback when the target had diverged or ETA was unavailable.
* **Self-Repair Performed:**
  - Added strict numeric guards: `typeof predEv.eta_s === 'number' && !isNaN(predEv.eta_s)`.
  - Added array length and element type validation for `trackEv.estimated_position_xy`.
* **Retest Result:** **`PASS`** (HUD updates smoothly across all simulation timestamps).

---

### Finding FIND-05 (LOW): Test Suite Count Documentation Desynchronization
* **Module Affected:** `PROJECT_STATUS.md`
* **Defect Description:**
  `PROJECT_STATUS.md` referenced 50 passing tests from an earlier milestone, whereas the test suite has grown to 65 passing automated tests.
* **Self-Repair Performed:**
  - Updated `PROJECT_STATUS.md` and created `VERIFICATION_RESULTS.md` with complete logs of all 65 tests.
* **Retest Result:** **`PASS`**.

---

### Finding FIND-06 (CRITICAL): ESP32-S3-DevKitC-1 v1.1 Header Assignment Errors
* **Module Affected:** `hardware/wiring_manifest.json`, `hardware/devices/esp32_s3_devkitc1_v1_1.json`, `src/prw_wild/web/static/app.js`, `HARDWARE_REFERENCES.md`, `WIRING_VALIDATION.md`
* **Defect Description:**
  Cross-verification against the official Espressif Systems DevKitC-1 v1.1 User Guide (`https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html`) identified four critical pin assignment defects in earlier manifests:
  1. **HC-SR501 VCC was assigned to Header J3 Pin 21:** On official DevKitC-1 v1.1, Header J3 Pin 21 is **GND**, not 5V. Supplying 0V to PIR VCC renders the sensor unpowered. The verified 5V supply is on **Header J1 Pin 21**.
  2. **INMP441 L/R was connected to Header J3 Pin 20:** On official DevKitC-1 v1.1, Header J3 Pin 20 is **GPIO19 (USB_D-)**, not Ground. Tying channel select to USB D- disrupts native USB communication and floats the channel select logic. The verified Ground pin is **Header J3 Pin 21 (GND)**.
  3. **GPIO48 / GPIO47 Inversion:** Earlier tables listed J3 Pin 16 as GPIO47 and J3 Pin 17 as GPIO48. The official schematic specifies **J3 Pin 16 = GPIO48** and **J3 Pin 17 = GPIO47**.
  4. **INMP441 SCK (GPIO9) Pin Position:** Earlier manifests mapped GPIO9 to Header J1 Pin 17. On official DevKitC-1 v1.1, Header J1 Pin 17 is **GPIO11**, while **Header J1 Pin 15 is GPIO9**.
* **Self-Repair Performed:**
  - Updated centralized `hardware/wiring_manifest.json` and static mirror:
    - `NET_5V_PIR_PWR`: Source Header J1 Pin 21 (5V), 3D coords `[-1.14, 0.35, 2.42]`.
    - `NET_GND_INMP441`: Source Header J3 Pin 21 (GND), 3D coords `[1.14, 0.35, 2.42]`.
    - `NET_I2S_MIC_SCK`: Source Header J1 Pin 15 (GPIO9), 3D coords `[-1.14, 0.35, 0.90]`.
  - Replaced complete 22-pin arrays for Header J1 and Header J3 in `hardware/devices/esp32_s3_devkitc1_v1_1.json`, its web static mirror, and `src/prw_wild/web/static/app.js`.
  - Updated all hardware documentation files (`HARDWARE_REFERENCES.md`, `WIRING_VALIDATION.md`).
  - Added strict automated regression tests in `tests/test_hardware.py` asserting every official pin signal, type, and coordinate.
* **Retest Result:** **`PASS`** (All 65 tests passing).

---

### Finding FIND-07 (CRITICAL): Hardware Lab 3D Viewport Blank on Modal Initialization
* **Module Affected:** `src/prw_wild/web/static/app.js` (Lines 3617–3725), `src/prw_wild/web/static/index.html`, `src/prw_wild/web/static/style.css`
* **Defect Description:**
  When `hardwareLabModal` was initialized while hidden (`display: none` / `opacity: 0`), `#hardwareLab3DContainer` reported `clientWidth = 0` and `clientHeight = 0`.
  1. The `THREE.PerspectiveCamera` aspect ratio calculation `width / height` evaluated to `0 / 0 = NaN`.
  2. This corrupted the Three.js projection matrix with `NaN` values, causing all subsequent WebGL draw calls to evaluate to zero-area clip space.
  3. The WebGL renderer initialized with a $0 \times 0$ canvas. When the modal was subsequently revealed, no reflow or resize was dispatched, leaving the viewport completely blank.
  4. When procedural model generation completed, there was no bounding-box camera auto-framing, leaving models outside or improperly clipped by the camera view.
* **Self-Repair Performed:**
  - Added robust dimension fallbacks: `const width = container.clientWidth || 700; const height = container.clientHeight || 540;`.
  - Added strict aspect guard preventing `NaN` matrices: `let aspect = width / height; if (!isFinite(aspect) || aspect <= 0) aspect = 700 / 540;`.
  - Attached a dynamic `ResizeObserver` to `#hardwareLab3DContainer` that continuously updates camera aspect, projection matrices, renderer size, and device pixel ratio whenever the modal opens or resizes.
  - Implemented `fitHardwareCameraToObject(object, fovMultiplier)` which computes exact `THREE.Box3` and `THREE.Sphere` bounding geometry and smoothly frames the camera around any selected board or multi-board assembly.
  - Added an in-viewport diagnostics HUD (`#hwDiagnosticsOverlay`) displaying live device, mode, viewport dimensions, mesh count, and cable count, plus an automatic error banner (`#hw3DErrorBanner`) if zero meshes are detected.
* **Retest Result:** **`PASS`** (Verified via browser automation: viewport cleanly renders 182 meshes and 11/11 wires on workbench; single-board models frame automatically with 105 meshes on ESP32-S3 and 6 meshes on ESP32-CAM).

---

### Finding FIND-08 (HIGH): Selected Device and Inspector Card State Desynchronization
* **Module Affected:** `src/prw_wild/web/static/app.js` (Lines 4680–4840)
* **Defect Description:**
  In the initial screenshot, the `ESP32-S3-DevKitC-1 v1.1` tab was selected, but the right-hand inspector panel displayed `ESP32-CAM Standard V1.0`.
  1. There was no single authoritative state variable controlling hardware device selection.
  2. Tab clicks, submode buttons, and dashboard "Explore in Hardware Lab" clicks modified independent variables (`hwCurrentDevice`, `hwCurrentSubMode`) across separate event handlers without unified synchronization.
  3. When switching from Workbench mode to single-component tabs, `hwCurrentHeaderTab` remained stuck on `'WIRING'`, causing the pinout register to show 11 workbench wire nets instead of the board's header pins. Clicking wires overwrote the inspector card title with wire net names.
* **Self-Repair Performed:**
  - Established a single authoritative state variable `selectedDeviceId` and controller `setSelectedHardwareDevice(deviceId, options)`.
  - Every UI trigger (device tabs, workbench mode button, 3D submode button, inspector card buttons) now routes through `setSelectedHardwareDevice`.
  - Synchronously updates:
    - Tab styling (`.hw-tab.active` strictly on `selectedDeviceId`).
    - Submode buttons (`#btnHwModeWorkbench`, `#btnHwMode3D`, `#btnHwModeWiring`).
    - 3D scene model lifecycle (clean disposal of old models, procedural build and camera fitting for selected model).
    - Inspector quick info card (`#hwCompName`, `#hwCompBadge`, `#hwMetaRole`, `#hwRevisionAlert`).
    - Pinout register table (`populatePinoutTable`), resetting active header tab to `Header J1` / primary pinout for single devices and `All Sensor Nets (11)` for workbench.
    - Viewport diagnostics overlay.
  - Added targeted regression tests in `tests/test_hardware.py` validating that every hardware device is mapped to its dedicated builder and pinout table.
* **Retest Result:** **`PASS`** (Verified in live browser: ESP32-S3 tab strictly displays ESP32-S3 model, J1 pinout, and v1.1 inspector card; ESP32-CAM tab strictly displays ESP32-CAM model, DVP bus pinout, and OV2640 inspector card).


---

## 2. Detailed Finding Records

### Finding FIND-01 (CRITICAL): Ground-Truth Leakage into Operational Controller
* **Module Affected:** `src/prw_wild/experiment_runner.py` (Lines 377, 395, 401–403, 416, 429)
* **Defect Description:**
  1. At line 395, the controller evaluated boundary breaches using:
     ```python
     elif animal.crossed_boundary:
         is_breach = True
     ```
     This allowed the online controller to cheat by reading the hidden world object's internal boolean `animal.crossed_boundary` if tracking was unconfident.
  2. At lines 401–403, if `track_state.is_valid` was false, the controller fell back to `animal.position.x` and `animal.position.y` directly from the world agent.
  3. At lines 377, 416, and 429, alerts were routed with `animal.species` (hidden ground truth) instead of the species inferred by operational sensors (optical camera classification or candidate prior).
* **Scientific Risk:** Violates the non-negotiable rule that the operational controller must infer movement strictly from sensor observations, not hidden ground truth.
* **Self-Repair Performed:**
  - Completely excised `animal.crossed_boundary` and `animal.position` from the controller section.
  - Breach detection now strictly requires controller-derived evidence: `track_state.is_valid and track_state.estimated_x >= (boundary.a.x - 2.0) and track_state.track_confidence > 0.25` or high-confidence fused position $\ge boundary.a.x - 2.0$.
  - Species field in operational events now consumes `inferred_species` from camera classification when active, defaulting to `"ESTIMATED_MEGAFAUNA"` when unconfirmed.
  - Implemented static AST inspection and dynamic telemetry isolation tests in `tests/test_leakage.py`.
* **Retest Result:** **`PASS`** (Clean run across all scenarios without ground-truth dependency).

---

### Finding FIND-02 (HIGH): Wiring Manifest 3D Coordinate Divergence
* **Module Affected:** `hardware/wiring_manifest.json` vs `src/prw_wild/web/static/app.js`
* **Defect Description:**
  In `hardware/wiring_manifest.json`, the destination relative coordinates for peripheral sensor headers were slightly offset from their actual rendered pin meshes on the 3D workbench:
  - HC-SR501 PIR header pins were recorded at $X = -3.2$ instead of actual mesh header position $X = -2.6$.
  - SW-420 Vibration header pins were recorded at $X = -3.0$ instead of actual mesh header position $X = -2.6$.
  - INMP441 Microphone breakout pins were recorded at $X = 3.2$ instead of actual mesh header position $X = 2.7$.
* **Engineering Risk:** Inconsistency between the centralized machine-readable manifest and 3D spatial raycasting endpoints.
* **Self-Repair Performed:**
  - Synchronized `rel_coord_3d` in `hardware/wiring_manifest.json` and `src/prw_wild/web/static/hardware/wiring_manifest.json` with the exact 3D pin mesh world coordinates.
  - Verified that all 11 nets connect exactly between source and destination pins in `tests/test_hardware.py`.
* **Retest Result:** **`PASS`** (All 11 nets verified and aligned).

---

### Finding FIND-03 (HIGH): Blocking Browser `alert()` Modal Dialogs
* **Module Affected:** `src/prw_wild/web/static/app.js` (Lines 2517, 3106)
* **Defect Description:**
  When network drops or simulation warnings occurred, `app.js` invoked browser native `alert()`. In automated headless browser testing, `alert()` creates a blocking modal that halts JavaScript execution.
* **Self-Repair Performed:**
  - Created a modern non-blocking toast notification system `showToastNotification(message, type)` with floating glassmorphism badges and auto-dismissal.
  - Replaced all calls to `alert()` with non-blocking toasts.
* **Retest Result:** **`PASS`** (Browser execution continues uninterrupted).

---

### Finding FIND-04 (MEDIUM): `toFixed` Unhandled Undefined Type Error
* **Module Affected:** `src/prw_wild/web/static/app.js` (Lines 2740, 2748)
* **Defect Description:**
  `predEv.eta_s !== null` evaluated to `true` when `eta_s` was `undefined` because in JavaScript `undefined !== null`. Calling `.toFixed(1)` on `undefined` threw `TypeError: Cannot read properties of undefined (reading 'toFixed')` during simulation playback when the target had diverged or ETA was unavailable.
* **Self-Repair Performed:**
  - Added strict numeric guards: `typeof predEv.eta_s === 'number' && !isNaN(predEv.eta_s)`.
  - Added array length and element type validation for `trackEv.estimated_position_xy`.
* **Retest Result:** **`PASS`** (HUD updates smoothly across all simulation timestamps).

---

### Finding FIND-05 (LOW): Test Suite Count Documentation Desynchronization
* **Module Affected:** `PROJECT_STATUS.md`
* **Defect Description:**
  `PROJECT_STATUS.md` referenced 50 passing tests from an earlier milestone, whereas the test suite has grown to 62 passing automated tests.
* **Self-Repair Performed:**
  - Updated `PROJECT_STATUS.md` and created `VERIFICATION_RESULTS.md` with complete logs of all 62 tests.
* **Retest Result:** **`PASS`**.

---

### Finding FIND-06 (CRITICAL): ESP32-S3-DevKitC-1 v1.1 Header Assignment Errors
* **Module Affected:** `hardware/wiring_manifest.json`, `hardware/devices/esp32_s3_devkitc1_v1_1.json`, `src/prw_wild/web/static/app.js`, `HARDWARE_REFERENCES.md`, `WIRING_VALIDATION.md`
* **Defect Description:**
  Cross-verification against the official Espressif Systems DevKitC-1 v1.1 User Guide (`https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html`) identified four critical pin assignment defects in earlier manifests:
  1. **HC-SR501 VCC was assigned to Header J3 Pin 21:** On official DevKitC-1 v1.1, Header J3 Pin 21 is **GND**, not 5V. Supplying 0V to PIR VCC renders the sensor unpowered. The verified 5V supply is on **Header J1 Pin 21**.
  2. **INMP441 L/R was connected to Header J3 Pin 20:** On official DevKitC-1 v1.1, Header J3 Pin 20 is **GPIO19 (USB_D-)**, not Ground. Tying channel select to USB D- disrupts native USB communication and floats the channel select logic. The verified Ground pin is **Header J3 Pin 21 (GND)**.
  3. **GPIO48 / GPIO47 Inversion:** Earlier tables listed J3 Pin 16 as GPIO47 and J3 Pin 17 as GPIO48. The official schematic specifies **J3 Pin 16 = GPIO48** and **J3 Pin 17 = GPIO47**.
  4. **INMP441 SCK (GPIO9) Pin Position:** Earlier manifests mapped GPIO9 to Header J1 Pin 17. On official DevKitC-1 v1.1, Header J1 Pin 17 is **GPIO11**, while **Header J1 Pin 15 is GPIO9**.
* **Self-Repair Performed:**
  - Updated centralized `hardware/wiring_manifest.json` and static mirror:
    - `NET_5V_PIR_PWR`: Source Header J1 Pin 21 (5V), 3D coords `[-1.14, 0.35, 2.42]`.
    - `NET_GND_INMP441`: Source Header J3 Pin 21 (GND), 3D coords `[1.14, 0.35, 2.42]`.
    - `NET_I2S_MIC_SCK`: Source Header J1 Pin 15 (GPIO9), 3D coords `[-1.14, 0.35, 0.90]`.
  - Replaced complete 22-pin arrays for Header J1 and Header J3 in `hardware/devices/esp32_s3_devkitc1_v1_1.json`, its web static mirror, and `src/prw_wild/web/static/app.js`.
  - Updated all hardware documentation files (`HARDWARE_REFERENCES.md`, `WIRING_VALIDATION.md`).
  - Added strict automated regression tests in `tests/test_hardware.py` asserting every official pin signal, type, and coordinate.
* **Retest Result:** **`PASS`** (All 62 tests passing).

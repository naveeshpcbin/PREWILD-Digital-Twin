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

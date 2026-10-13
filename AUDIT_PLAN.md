# PRW-Wild Comprehensive Audit & Verification Plan

## 1. Objectives & Scope
This document defines the formal audit, verification, and self-repair methodology for the **PRW-Wild (Predictive RF-Wildlife) 3D Digital Twin and Interactive Hardware Laboratory**.

As an independent auditor, no prior claim of completeness or correctness is accepted as ground truth. Every algorithm, hardware pinout, wiring path, 3D asset, event sequence, risk transition, alert dispatch, and audio trigger must be verified through direct code inspection, mathematical derivation, automated test execution, and browser interaction.

---

## 2. Audit Execution Cycles

### Cycle 1: Inventory & Static Review
* **Inventory Verification:** Audit all files across frontend (`src/prw_wild/web/static/`), backend (`src/prw_wild/`), configurations (`configs/`), hardware descriptors (`hardware/`), test suite (`tests/`), and documentation.
* **Security & Dependency Audit:** Check for exposed secrets, unsafe environment variable usage, unverified external network calls, untrusted script injections, and dependency vulnerabilities.
* **Hardware & Pinout Audit:** Cross-reference ESP32-S3-DevKitC-1 v1.1 official Espressif schematics, J1/J3 pinout mappings, Octal SPI memory reservations (`GPIO35`, `GPIO36`, `GPIO37`), strapping pins (`GPIO0`, `GPIO45`, `GPIO46`), RGB LED assignment (`GPIO38`), and sensor voltage domains.

### Cycle 2: Logic, Algorithmic Correctness & Ground-Truth Isolation
* **Ground-Truth Leakage Audit:** Verify that the operational controller (EKF tracker, fusion, ETA estimator, risk engine, camera gate, alert router) does NOT read true animal coordinates or future crossing times from the world simulation.
* **Geometry & Intersection Audit:** Verify boundary ray-segment intersection mathematics across edge cases: parallel motion, zero velocity, movement away from perimeter, collinear points, and boundary segment endpoints.
* **Tracking & Estimation Audit:** Verify the state vector, transition matrix, measurement update, and covariance behavior in `tracker.py`. Ensure it is accurately documented and mathematically consistent.
* **ETA & Risk Formula Audit:** Verify ETA calculation, units (seconds), and that invalid or diverging trajectories yield `None` instead of fabricated ETAs. Verify risk evaluation against configured thresholds.
* **Sensor Fusion & Decay:** Audit exponential decay weighting, multi-modal evidence accumulation, and noise rejection in `fusion.py`.

### Cycle 3: End-to-End Scenario Testing
Execute and verify the 5 mandatory end-to-end operational scenarios:
1. **Scenario A (`approach_crossing`):** Animal approaches and breaches perimeter; verify approach warning $\to$ camera gate $\to$ optical confirmation $\to$ breach event $\to$ laptop alarm $\to$ nearest recipient dispatch.
2. **Scenario B (`turns_away`):** Animal approaches but diverts away; verify elevated risk decays, no spurious breach alarm is triggered, camera duty cycle turns off gracefully.
3. **Scenario C (`nuisance_triggers`):** Spurious isolated PIR/vibration noise pulses without sustained RF precursor; verify fusion rejects nuisance events without false positive dispatches.
4. **Scenario D (`degraded_network`):** High packet loss / sensor dropouts; verify graceful degradation, uncertainty handling, and lack of system crashes.
5. **Scenario E (`camera_gating`):** Predictive camera gating policy comparison against reactive baselines; verify calculated metrics (lead time, recall, activations, energy).

### Cycle 4: 3D Hardware Assembly & UI/UX Audit
* **3D Wiring Assembly:** Verify that the physical workbench is a genuine 3D assembly in Three.js (`TubeGeometry` + DuPont connector housings), that wire endpoints match exact physical pin coordinates in `hardware/wiring_manifest.json`, and that pinout tables, component inspectors, and exploded view remain synchronized.
* **Visual Realism & Anatomy:** Verify quadruped diagonal gait, ear flapping, trunk curling on `ELEPHANT_01`. Verify multi-segment human figures with distinct clothing and footwear.
* **UI Interactions:** Test 9 camera viewpoints, 3D/2D toggle, Layer Explorer, Causal Replay timeline scrubber, and Counterfactual Twin.
* **Web Audio Alarm:** Verify audio synthesizer, arming state, mute, volume, and silencing/acknowledgment controls.

### Cycle 5: Self-Repair, Regression Testing & Final Acceptance
* Remediate all Critical and High-severity defects immediately.
* Remediate Medium and Low issues without destabilizing core features.
* Rerun full pytest test suite and browser validation after every edit.
* Produce updated traceability matrix, findings report, and verification results.

---

## 3. Defect Classification Severity Scale

| Severity | Criteria | Resolution SLA |
| :--- | :--- | :--- |
| **CRITICAL** | Core simulation crash; ground truth leak into controller; dangerous/invalid hardware wiring; broken breach alert/alarm loop; security vulnerability. | Immediate fix required. |
| **HIGH** | Algorithmic error in ETA/risk/metrics; camera gate desynchronization; incorrect pinout or board revision; fake UI disconnected from backend; wire endpoints mismatch manifest. | Immediate fix required. |
| **MEDIUM** | Inspector displaying stale state; missing visual animation or clipping; camera POV misalignment; minor UI regression. | Remediate before final delivery. |
| **LOW** | Minor styling inconsistency; non-critical label flaw; cosmetic performance tweak. | Remediate as time permits. |

---

## 4. Evidence Requirements
Every audit check must cite:
- File path with line numbers (`file:///...`)
- Terminal command executed and exit code
- Exact console/log output
- Verification status: `PASS`, `FAIL`, `PARTIAL`, `BLOCKED`, `NOT TESTED`

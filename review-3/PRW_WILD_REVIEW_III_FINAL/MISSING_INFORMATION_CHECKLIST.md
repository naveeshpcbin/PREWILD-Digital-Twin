# PRW-Wild — Missing Information and Pre-Submission Customization Checklist
**Thiagarajar College of Engineering, Madurai**  
**Course:** Design Thinking (22ES390) | **Review III Assessment**  
**Deliverable Folder:** `Review -3/PRW_WILD_REVIEW_III_FINAL/`

---

## 1. Purpose of this Checklist

In accordance with academic integrity guidelines, **no student names, register numbers, or faculty supervisor identities were fabricated**. Where verified personal records were absent from the project workspace, structured and clearly identifiable placeholders (e.g. `[Student Name 1 | Reg. No. XXXXXXX]`) were placed on the slides and in project documentation.

This checklist identifies every placeholder that requires student input prior to final faculty submission, as well as the technical boundaries that should be acknowledged during presentation delivery.

---

## 2. Student & Institutional Information Checklist

| Item ID | Location in Presentation | Current Placeholder Text | Required Action / Information to Insert | Urgency |
| :---: | :--- | :--- | :--- | :---: |
| **STU-01** | **Slide 01 (Cover)** | `[Student Name 1 | Reg. No. XXXXXXX]` | Insert official name and university register number of Lead Embedded/IoT Engineer | **HIGH** |
| **STU-02** | **Slide 01 (Cover)** | `[Student Name 2 | Reg. No. XXXXXXX]` | Insert official name and university register number of Backend & AI Engineer | **HIGH** |
| **STU-03** | **Slide 01 (Cover)** | `[Student Name 3 | Reg. No. XXXXXXX]` | Insert official name and university register number of Digital Twin Architect | **HIGH** |
| **STU-04** | **Slide 01 (Cover)** | `[Student Name 4 | Reg. No. XXXXXXX]` | Insert official name and university register number of Hardware/QA Engineer | **HIGH** |
| **STU-05** | **Slide 01 (Cover)** | `Team Name: ByteForce / PRW-Wild Team` | Update to the official team name assigned by the course coordinator | MEDIUM |
| **STU-06** | **Slide 01 (Cover)** | `Team ID: [Team ID Placeholder — e.g., TC2_ECE_XX]` | Insert assigned TCE Design Thinking Team ID (e.g. `TC2_ECE_12`) | **HIGH** |
| **STU-07** | **Slide 01 (Cover)** | `[Faculty Supervisor Name / ECE Dept]` | Insert name, academic designation, and department of the supervising faculty guide | **HIGH** |
| **STU-08** | **Slide 02 (Team Roles)** | `[Student Name 1]` to `[Student Name 4]` | Replace table names and register numbers to match Slide 01 | **HIGH** |
| **STU-09** | **Slide 02 (Team Roles)** | Department Column | Verify if all members belong to ECE or if the team is interdisciplinary (ECE / CSE / IT) | MEDIUM |

---

## 3. How to Update Placeholders in the PowerPoint File

The generated PowerPoint presentation is fully editable:
1. Open `PRW_WILD_REVIEW_III_PRESENTATION.pptx` in Microsoft PowerPoint.
2. Navigate to **Slide 01 (Cover Slide)**:
   - Click inside the **"PROJECT TEAM DETAILS"** card on the bottom-left.
   - Replace the student name and register number placeholders with the official team member details.
   - Click inside the **"ACADEMIC & EVALUATION DETAILS"** card on the bottom-right and update the Faculty Guide name.
3. Navigate to **Slide 02 (Team Roles & Responsibilities)**:
   - In the first column of the table, update the four student name blocks to match Slide 01.
4. Save the file.
5. Export to PDF by selecting **File -> Save As -> PDF** to produce the updated `PRW_WILD_REVIEW_III_PRESENTATION.pdf`.
*(Alternatively, update the strings in `d:\Simulation For DT\generate_review3_deck.py` and run the script to recompile both PPTX and PDF automatically.)*

---

## 4. Technical Disclosure Checklist for Faculty Defense

During the Review III oral examination, the team should confidently present the working prototype while maintaining complete transparency regarding technical boundaries:

### What to Proudly Demonstrate as Physically Verified:
- [x] **Dual ESP32-WROOM-32 Hardware:** Nodes communicate over active 433.92 MHz LoRa link with 0% packet loss, -64 dBm RSSI, and +10.1 dB SNR.
- [x] **Physical Sensor Conditioning:** HC-SR501 PIR sensor operating with 45s stabilization filter; INMP441 digital MEMS microphone streaming 16 kHz audio over I2S; piezoelectric disc sampled via 12-bit ADC.
- [x] **Physical 6-LED Annunciator Panel:** All 6 LEDs illuminate with 2 kΩ ballast resistors, proving multi-sensor threshold triggers on ESP32-B.
- [x] **Full 3D WebGL Digital Twin:** Running smoothly in browser at 60 FPS with 120x120 heightmap mesh, 16 wildlife species, 75 agents, and 5 tactical viewpoints.
- [x] **Automated Software Regression Suite:** 139 tests passing across 18 test files (`pytest`) in 21.90s.

### What to Disclose Transparently as Roadmap / Planned (Phase 4):
- [x] **Wi-Fi CSI Physical Capture:** Explain that Layer 1 is modeled mathematically and visually in the 3D twin, but physical OFDM subcarrier CSI capture will be implemented in Phase 4 via ESP-IDF CSI tools.
- [x] **Physical Camera Stream Integration:** Clarify that while the Xiaomi 360° camera was bench tested, it operates via its vendor cloud app; the in-code YOLOv8n vision pipeline operates over the 3D virtual viewfinder.
- [x] **In-Ground Soil Seismic Calibration:** Note that the piezoelectric disc was bench calibrated via mechanical taps, and field geophone cross-calibration will occur in Phase 4.
- [x] **Solar Energy Harvesting:** Clarify that current bench nodes run on 5V/3.3V USB power, and 10W solar panels with LiFePO4 packs are planned for field deployment.

---

## 5. Deliverables Verification Summary

All required deliverables have been compiled and verified in:
- `D:\Simulation For DT\Review -3\PRW_WILD_REVIEW_III_FINAL\`
- `D:\Simulation For DT\prw-wild-digital-twin\review-3\PRW_WILD_REVIEW_III_FINAL\`

Files present:
1. `PRW_WILD_REVIEW_III_PRESENTATION.pptx` (Editable PowerPoint presentation, 28 slides)
2. `PRW_WILD_REVIEW_III_PRESENTATION.pdf` (Rendered PDF presentation, 28 pages)
3. `REVIEW_III_RUBRIC_MAPPING.md` (Detailed rubric mapping table and narrative justification)
4. `TECHNICAL_CLAIM_VERIFICATION.md` (Forensic verification register linking claims to source code)
5. `MISSING_INFORMATION_CHECKLIST.md` (This document)

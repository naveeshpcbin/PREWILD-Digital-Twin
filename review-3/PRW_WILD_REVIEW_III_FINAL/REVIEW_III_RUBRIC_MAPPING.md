# PRW-Wild — Design Thinking Review III Rubric Mapping
**Thiagarajar College of Engineering, Madurai – 625 015**  
**Department of Electronics and Communication Engineering**  
**Course:** Design Thinking (22ES390) | **Regulation:** 2019–20  
**Authority:** Official Assessment Rubrics — Review III (`Rubrics_Review-3_2019-20.pdf`)

---

## 1. Executive Rubric Audit Summary

The official Thiagarajar College of Engineering Review III Assessment Rubric evaluates student mini projects across **five fundamental descriptors** on a 4-point scale:
- **Exemplary (4 Points):** Full identification, rigorous systematic procedures, working prototype, complete role execution with ethical adherence, and high-impact communication.
- **Proficient (3 Points):** Substantial identification with adequate evidence and presentation.
- **Partially Proficient (2 Points):** Incomplete functions, unverified claims, or inadequate timelines.
- **Incomplete (1 Point):** Missing significant components, poor execution, or unclear responsibilities.
- *Failing to meet minimum requirements in any descriptor yields zero points for that descriptor.*

The PRW-Wild Review III presentation (`PRW_WILD_REVIEW_III_PRESENTATION.pptx` / `.pdf`) is structured to target and demonstrate **Exemplary (Level 4)** achievement across all five assessment criteria.

---

## 2. Complete Rubric-to-Slide Forensic Mapping

| Rubric Descriptor | Target Score | Primary Slides | Secondary Slides | Specific Rubric Requirement Addressed | Concrete Technical Evidence Presented |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **1. Functional Decomposition** | **Exemplary (4)** | **Slide 11, 12, 13, 14** | Slide 03, 15, 20, 21 | Identified all functions of proposed product; represented visually via tree diagram, system block diagram, and spatial concept maps. | • Complete 5-pillar functional decomposition tree (F1 Sensing, F2 LoRa, F3 Ingestion, F4 Digital Twin, F5 Command)<br>• End-to-end signal flow block diagram (`fig1_system_architecture.png`)<br>• Three-tier spatial defense corridors (`fig2_three_layer_spatial.png`)<br>• Strict Physical vs Virtual domain demarcation |
| **2. Alternate Solutions and Their Evaluation** | **Exemplary (4)** | **Slide 06, 07, 08, 09, 10** | Slide 04, 05, 26 | Identified potential alternate solutions; adopted systematic weighted evaluation procedure to select optimal architecture. | • Comparative state-of-the-art literature survey (Kumar 2021, Zeppelzauer 2015, Sharma 2023, Chen 2020)<br>• Detection modality trade-off analysis (Cameras vs Seismic vs Tri-Corridor)<br>• RF propagation & foliage loss evaluation (Wi-Fi vs BLE vs Cellular vs 433 MHz LoRa)<br>• Operator visualization trade-offs (Serial CLI vs 2D GIS vs 3D Digital Twin)<br>• Multi-attribute weighted decision matrix ($w_i S_i = 8.90 / 10.0$) |
| **3. Prototype** | **Exemplary (4)** | **Slide 15, 16, 17, 18, 19, 20, 21, 22** | Slide 12, 13, 14 | Demonstrated a working prototype and all its core functions with authentic physical and software evidence. | • Dual ESP32-WROOM-32 hardware architecture (ESP32-A and ESP32-B)<br>• HC-SR501 PIR (45s filter), Piezoelectric ADC window (20ms / 80 samples at 250µs), INMP441 I2S digital audio bus (16kHz RMS)<br>• Sub-GHz LoRa telemetry (433.92 MHz, SF7, 0% packet loss, +10.1 dB SNR)<br>• 6-LED physical annunciator panel with 2kΩ ballast protection<br>• 5 authentic bench prototype photographs<br>• 3D WebGL Digital Twin (120x120 heightmap, 16 species, 75 agents, 5 camera views)<br>• Dynamic Camera Gating saving 88% power; YOLOv8n ONNX AI vision<br>• 139 passing automated regression tests (`pytest`) |
| **4. Adherence to Project Plan** | **Exemplary (4)** | **Slide 02, 23, 24** | Slide 01, 26 | Completely executed individual roles and responsibilities in accordance with professional code of conduct; clearly defined project timelines. | • Individual roles & subsystem ownership table (Firmware, Backend, 3D Twin, QA)<br>• Phase 1–4 project timeline (Reviews I, II, III, IV milestones)<br>• 100% on-schedule completion of Review III deliverables<br>• Engineering code of conduct: 2kΩ silicon protection, ADC attenuation, piezo safety gate, strict scientific truth disclosure, non-lethal wildlife ethics |
| **5. Communication Skill** | **Exemplary (4)** | **All 28 Slides** | Slide 01, 26, 27, 28 | Slides support presentation, easy to read, effective keywords, structured sentences, proper sequence, professional visual identity, comprehensive notes. | • 10.0" x 7.5" standard 4:3 TCE format with official textured cream background (`layout_bg.jpg`) and crest<br>• One clear central message per slide; bold Times New Roman headings (20pt); legible Calibri body (10–14pt)<br>• Muted gold, sage green, and semantic layer accents (Cyan L1, Amber L2, Violet L3)<br>• High-contrast tables and cards with 0.08" colored accent strips<br>• Comprehensive speaker notes embedded on every slide |

---

## 3. Detailed Rubric Criteria Justifications

### Descriptor 1: Functional Decomposition (Score: 4 / 4 — Exemplary)
- **Visual Representation:** Slide 11 provides a multi-level hierarchical tree diagram decomposing the core wildlife monitoring mission into 5 primary pillars and 18 discrete sub-functions.
- **System Block Diagram:** Slide 12 presents the complete audited system architecture diagram (`fig1_system_architecture.png`), tracing physical transducers, SPI LoRa transceivers, USB serial bridging, backend risk calculations, and WebGL rendering.
- **Spatial Decomposition:** Slide 13 visually maps the three defense envelopes (`fig2_three_layer_spatial.png`): Layer 1 (X = 45–70m, Cyan), Layer 2 (X = 70–85m, Amber), and Layer 3 (X = 85–100m, Violet) up to the agricultural fence line (X = 100m).
- **Domain Separation:** Slide 14 enforces the critical architectural demarcation between the physical hardware domain (ESP32-A/B, real ADC counts, measured RSSI/SNR) and the virtual simulation domain (autonomous agents, 3D mesh).

### Descriptor 2: Alternate Solutions and Their Evaluation (Score: 4 / 4 — Exemplary)
- **Broad Exploration:** Alternative solutions are investigated across three separate technical dimensions: detection modalities (Slide 07), wireless communication links (Slide 08), and operator visualization interfaces (Slide 09).
- **Systematic Procedure:** Slide 10 establishes a formal Multi-Attribute Utility Analysis (MAUA) matrix. Seven weighted engineering criteria are evaluated across four architectural alternatives.
- **Defensible Scores:** Criteria weights ($\sum w_i = 1.00$) reflect stakeholder priorities. PRW-Wild achieves an evidence-backed composite score of **8.90 / 10.0**, providing quantitative justification for the chosen design.

### Descriptor 3: Prototype (Score: 4 / 4 — Exemplary)
- **Authentic Working Hardware:** Slide 15 and 19 demonstrate our dual ESP32-WROOM-32 hardware bench prototype. Five authentic photographs display the field sensor enclosure, RA-02 LoRa transceiver, PIR dome, piezo disc, gateway enclosure, ballast resistors, and active 6-LED indicators.
- **Sensor Signal Conditioning:** Slide 16 documents verified firmware parameters: HC-SR501 45s warmup lockout, Piezoelectric 20ms window (80 samples at 250µs) with compile-time safety gate (`#define PIEZO_CIRCUIT_VERIFIED 0`), and INMP441 16kHz I2S digital audio RMS processing.
- **Wireless Telemetry:** Slide 17 proves sub-GHz communication with real bench telemetry captures over `COM7` at 115,200 baud showing sequence continuity, RSSI = -64 dBm, SNR = +10.1 dB, and 0% packet loss.
- **Interactive 3D Digital Twin:** Slide 20 and 21 showcase our WebGL Three.js Digital Twin with 120x120 elevation mesh, 16 wildlife species, 75 active agents, 5 camera viewpoints, and dynamic camera gating saving 88% power.
- **Verification Evidence:** Slide 22 documents our 139 passing automated software regression tests (100% pass rate in 21.90s) and clean Arduino CLI compilation logs.

### Descriptor 4: Adherence to Project Plan (Score: 4 / 4 — Exemplary)
- **Individual Roles & Responsibilities:** Slide 02 details clear subsystem ownership: Embedded Firmware Lead (ESP32-A/B, LoRa SPI), Backend Engineer (FastAPI, PySerial, YOLOv8n ONNX), Digital Twin Architect (Three.js WebGL, 120x120 mesh), and Hardware/QA Specialist (enclosures, 6-LED gateway, 139 pytest suite).
- **Milestone Timelines:** Slide 23 provides a comprehensive project chronological timeline tracking Phase 1 (Review I), Phase 2 (Review II), Phase 3 (Review III - Current), and Phase 4 (Review IV). Review III deliverables are verified 100% complete on schedule.
- **Professional Code of Conduct:** Slide 24 establishes our engineering ethics: 2 kΩ ballast resistors and 11 dB attenuation protecting silicon rails; software safety gates on piezoelectric inputs; transparent disclosure of physical vs simulated models; and 100% non-lethal, non-invasive animal welfare ethics.

### Descriptor 5: Communication Skill (Score: 4 / 4 — Exemplary)
- **Visual Design Authority:** Strictly adopts the visual language of `Smart_Rake_TCE_Template_Final (1).pptx`: 10.0" x 7.5" dimensions, official TCE textured ivory background (`layout_bg.jpg`), dark charcoal headings, muted gold dividers, white card containers, and sage green accent pills.
- **Readability & Structure:** One central takeaway per slide, high-contrast text, clean vector cards, properly aligned tables, verified engineering units (m, MHz, kHz, ms, V, ADC counts).
- **Comprehensive Speaker Notes:** Detailed, articulate speaker notes are embedded on every single slide, equipping team members to deliver a confident, delightful presentation that finishes strictly on time.

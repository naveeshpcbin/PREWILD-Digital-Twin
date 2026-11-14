# PREWILD-Digital-Twin — PRW-Wild: Immersive 3D Digital Twin

> **Core Principle: PREDICT BEFORE CONFIRM.**  
> Software-in-the-Loop Predictive RF Wildlife Early-Warning Digital Twin. Multi-modal RF and ground sensing predicts approach trajectories and corroborates evidence before selectively gating high-power confirmation cameras, routing alerts to nearby communities and authorities, and activating boundary breach countermeasures.

---

## 🌐 Launching the 3D Digital Twin

### Local Web Application URL
👉 **[http://localhost:8000/](http://localhost:8000/)** *(or `http://127.0.0.1:8000/`)*

### Quick Launch Command (Opens Browser Automatically)
In PowerShell / Terminal:
```powershell
$env:PYTHONPATH="src"; python -m prw_wild.web --port 8000 --open
```

*Or run the one-click startup scripts:*
- **Windows File Explorer:** Double-click [`run.bat`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/run.bat) or [`opentwin.bat`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/opentwin.bat)
- **PowerShell:** `.\run.ps1` or `.\opentwin.ps1`

---

## 🌟 Upgraded Architecture & Key Features

### 1. Tri-Corridor Spatial Defense Architecture
- **Layer 1 — Outer RF Corridor ($X = 45\text{ m}$ to $70\text{ m}$)**: Glowing Cyan envelope (#00f0ff); non-line-of-sight foliage RF disturbance monitoring; preliminary early warning cue.
- **Layer 2 — Middle Physical Sensor Corridor ($X = 70\text{ m}$ to $85\text{ m}$)**: Glowing Amber envelope (#f59e0b); physical multi-modal ground verification via dual ESP32-WROOM-32 nodes, HC-SR501 PIR motion sensor, 27mm piezoelectric ground vibration disc, and INMP441 digital MEMS acoustic sensor over I2S.
- **Layer 3 — Inner Camera Surveillance Corridor ($X = 85\text{ m}$ to $100\text{ m}$)**: Glowing Violet envelope (#a855f7); optical species confirmation; dynamic camera gating to eliminate continuous video power drain; automated YOLOv8n AI bounding-box tracking.
- **Perimeter Boundary Fence ($X = 100\text{ m}$)**: Formal boundary dividing reserve forest ($X < 100\text{ m}$) from agricultural farmland ($X > 100\text{ m}$).

### 2. Distributed Dual-Node IoT Hardware Subsystem
- **ESP32-A Sensor Acquisition Node**:
  - Microcontroller: ESP32-WROOM-32 (Xtensa Dual-Core 32-bit LX6 @ 240 MHz).
  - HC-SR501 PIR motion sensor on GPIO34 with 45,000 ms software stabilization filter.
  - Piezoelectric vibration disc on GPIO35 (ADC1_CH7, 12-bit, 11 dB attenuation, 20 ms / 80-sample peak-to-peak sampling).
  - INMP441 Omnidirectional MEMS microphone on I2S (BCLK 14, WS 15, SD 32, 16 kHz sampling, 24-bit PCM).
  - Semtech SX1278 / RA-02 LoRa transceiver on SPI (SCK 18, MISO 19, MOSI 23, NSS 5, RST 4, DIO0 2).
- **ESP32-B Gateway & Annunciator Node**:
  - Semtech SX1278 LoRa receiver on matching SPI bus.
  - Dedicated 6-LED physical annunciator panel with 2 kΩ current-limiting protection (LED1=32, LED2=33, LED3=25, LED4=13, LED5=21, LED6=22).
  - CP2102 USB UART bridge (115,200 baud) feeding live serial telemetry into Python backend.
  - Bench Link Margin: RSSI = -64 dBm, SNR = +10.1 dB, 0% packet loss.

### 3. Immersive 3D Digital Twin (Three.js / WebGL)
- **Geospatial Elevation Mesh**: 120 × 120 heightmapped terrain mesh (280 m × 260 m) with analytical terrain equations matching Blender topology.
- **16 Wildlife Species & 75 Active Agents**: Complete taxonomic registry with autonomous Reynolds flocking behaviors (cohesion, alignment, separation, grazing, drinking).
- **Hero Species — Asian Elephant (*Elephas maximus*)**: Realistic 4000 kg mass, 1.2 m/s walk speed, 6.5 m/s sprint speed, articulated glTF skeletal animation.
- **Five Tactical Viewpoints**: Master Orbit, Ground-Level Observer, Elephant Hero Follow, Farmland Machan, and Top-Down Radar.

### 4. Threat Ingestion, Risk Engine & Dynamic Camera Gating
- **Multi-Factor Risk Engine**: Continuous threat scoring ($R = w_s S_{species} + w_v V_{approach} + w_p P_{proximity} + w_d D_{density}$) with 0.05 hysteresis band.
- **Dynamic Camera Gating**: High-power optical camera sleeps until $R \ge 0.55$, achieving an **88% reduction in continuous video power draw**.
- **ONNX Runtime YOLOv8n Vision**: Automated species bounding-box tracking (`yolov8n.onnx`, 12.8 MB) with spatial morphological contour fallback.

---

## 🧪 Automated Testing & Verification

The project includes a comprehensive automated test suite with **139 passing tests** across 18 test files:
```powershell
pytest tests -v
```
**Results:** `139 passed in 21.90s` on Python 3.13.8 (win32) — **100% Pass Rate**.

---

## 🎓 Design Thinking Review III Presentation & Academic Deliverables

Complete official deliverables prepared for **Design Thinking Review III (22ES390)** at **Thiagarajar College of Engineering, Madurai**:
- **Presentation Deck (PPTX):** [`review-3/PRW_WILD_REVIEW_III_FINAL/PRW_WILD_REVIEW_III_PRESENTATION.pptx`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/review-3/PRW_WILD_REVIEW_III_FINAL/PRW_WILD_REVIEW_III_PRESENTATION.pptx) (28 slides)
- **Presentation Document (PDF):** [`review-3/PRW_WILD_REVIEW_III_FINAL/PRW_WILD_REVIEW_III_PRESENTATION.pdf`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/review-3/PRW_WILD_REVIEW_III_FINAL/PRW_WILD_REVIEW_III_PRESENTATION.pdf) (28 pages)
- **Official Rubric Mapping:** [`review-3/PRW_WILD_REVIEW_III_FINAL/REVIEW_III_RUBRIC_MAPPING.md`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/review-3/PRW_WILD_REVIEW_III_FINAL/REVIEW_III_RUBRIC_MAPPING.md)
- **Technical Specification Register:** [`review-3/PRW_WILD_REVIEW_III_FINAL/TECHNICAL_CLAIM_VERIFICATION.md`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/review-3/PRW_WILD_REVIEW_III_FINAL/TECHNICAL_CLAIM_VERIFICATION.md)
- **Pre-Submission Checklist:** [`review-3/PRW_WILD_REVIEW_III_FINAL/MISSING_INFORMATION_CHECKLIST.md`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/review-3/PRW_WILD_REVIEW_III_FINAL/MISSING_INFORMATION_CHECKLIST.md)
- **Complete System Audit Report:** [`reports/PRW_WILD_COMPLETE_TECHNICAL_AUDIT/PRW_WILD_COMPLETE_SYSTEM_ARCHITECTURE_AND_IMPLEMENTATION_AUDIT.pdf`](file:///d:/Simulation%20For%20DT/prw-wild-digital-twin/reports/PRW_WILD_COMPLETE_TECHNICAL_AUDIT/PRW_WILD_COMPLETE_SYSTEM_ARCHITECTURE_AND_IMPLEMENTATION_AUDIT.pdf)

---

## 📜 License & Academic Integrity
Developed as part of the academic curriculum for Design Thinking at Thiagarajar College of Engineering, Madurai.
All code, models, and firmware are published under an open educational license for wildlife conservation and human-wildlife conflict research.

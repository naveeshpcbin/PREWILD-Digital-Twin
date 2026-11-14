# PRW-WILD — SOURCE REFERENCES AND TRACEABILITY REGISTER

## COURSE: DESIGN THINKING (22ES390)
**Project Title:** PRW-Wild: A Multi-Layer Wildlife Monitoring and Immersive Digital Twin System  
**Institution:** Thiagarajar College of Engineering, Madurai  
**Document Purpose:** Complete audit trail connecting every claim, equation, parameter, and figure in the academic report to authoritative repository source files.

---

### 1. Primary Repository Sources & Code Traceability

Every technical specification, pin assignment, and architectural decision documented in `PRW_WILD_MINI_PROJECT_REPORT.docx` is directly traceable to the production repository:

| Subsystem / Metric | Report Location | Authoritative Repository File | Specific Code Reference / Implementation Detail |
|---|---|---|---|
| **Perimeter Boundary Line** | Ch 1.8, Ch 5.3 | `src/prw_wild/config.py` | Line 38: `PERIMETER_X = 100.0` (Forest: X < 100 m; Settlement: X > 100 m) |
| **Layer 1 Spatial Corridor** | Ch 5.3, Fig 5.2 | `src/prw_wild/web/static/app.js` | Line 1022: Mesh center = 57.5 m, width = 25 m $\rightarrow$ Spans X = 45 m to 70 m (Cyan) |
| **Layer 2 Spatial Corridor** | Ch 5.3, Fig 5.2 | `src/prw_wild/web/static/app.js` | Line 1032: Mesh center = 77.5 m, width = 15 m $\rightarrow$ Spans X = 70 m to 85 m (Amber) |
| **Layer 3 Spatial Corridor** | Ch 5.3, Fig 5.2 | `src/prw_wild/web/static/app.js` | Line 1042: Mesh center = 92.5 m, width = 15 m $\rightarrow$ Spans X = 85 m to 100 m (Violet) |
| **PIR Pinout & Settling Filter** | Ch 5.5, Tab 5.2 | `firmware/ESP32_A_Sensor_Node/...` | GPIO32; Line 79: 45,000 ms warmup suppression filter to reject false pyroelectric transients |
| **Piezoelectric ADC Sampling** | Ch 5.5, Tab 5.2 | `firmware/ESP32_A_Sensor_Node/...` | GPIO35 (ADC1_CH7); 12-bit (0–4095); 11 dB attenuation; 80 samples over 20 ms window (50 Hz AC rejection) |
| **Piezo Compile-Time Gate** | Ch 5.5, Ch 10.4 | `firmware/ESP32_A_Sensor_Node/...` | Line 63: `PIEZO_CIRCUIT_VERIFIED = 0` (Fail-closed compile gate preventing unsafe ADC exposure) |
| **INMP441 I2S Configuration** | Ch 5.5, Eq 5.1 | `firmware/ESP32_A_Sensor_Node/...` | GPIO25 (BCLK), GPIO33 (WS), GPIO34 (SD); 16 kHz sampling rate, 24-bit PCM in 32-bit slot, RMS window 256 samples |
| **LoRa Transceiver Configuration** | Ch 5.5, Eq 5.4 | `firmware/ESP32_A_Sensor_Node/...` | 433.92 MHz carrier; 125 kHz bandwidth; Spreading Factor SF7; Coding Rate 4/5; Sync Word 0x12; CRC enabled |
| **Annunciator LED Ballasts** | Ch 5.5, Tab 5.2 | `hardware/wiring_manifest_actual.json` | 6 LEDs (GPIO13, 21, 22, 25, 32, 33) on ESP32-B; individual 2 kΩ resistors (~0.60 mA per LED at 3.3 V) |
| **Node Mode Cascade Logic** | Ch 5.5, Ch 8.3 | `src/prw_wild/hardware/lora_bridge.py` | Lines 142–155: Turning OFF Node A enforces `node_b = 'OFF'`, preventing stale ghost alerts |
| **Expanded Sensor Thresholds** | Ch 8.3, Tab 8.1 | `src/prw_wild/web/static/app.js` | Piezo: 0–4095 ADC (step 25); Mic: 0–500,000 RMS (step 2,500); `#sideMicVuThreshold` dynamic VU bar |
| **'opentwin' CLI Engine** | Ch 8.1, Ch 8.3 | `tools/opentwin.py` | Instantaneous Windows launcher: auto-spawns background daemon, launches browser, outputs 6-line ANSI card |
| **120×120 Terrain Mesh** | Ch 5.6 | `src/prw_wild/web/static/app.js` | Lines 423–428: 280 m × 260 m plane with 14,400 quads (29,042 vertices); 1,200 m horizon skirt |
| **Elephant Kinematics GLB** | Ch 5.6 | `.../assets/animals/asian_elephant...` | Exact 5,657,296 bytes production binary glTF with 42-bone skeletal armature |
| **Multi-Agent Flocking Model** | Ch 5.6, Eq 5.3 | `src/prw_wild/ecosystem.py` | 75 autonomous agents across 16 species; Boids steering vector equations (Separation, Alignment, Cohesion) |
| **Regression Test Suite** | Ch 6.2, Ch 8.1 | `tests/` | 139 test cases covering all subsystems; 100% pass rate (`139 passed in 41.08s`) |

---

### 2. Physical Evidence & Artifact Traceability

| Artifact Name | Report Figure | File Location | Description & Forensic Evidence |
|---|---|---|---|
| **System Architecture Diagram** | Figure 5.1 | `reports/.../fig1_system_architecture.png` | Comprehensive vector diagram detailing 5-tier processing pipeline from wildlife movement to 3D visualizer |
| **Three-Layer Spatial Diagram** | Figure 5.2 | `reports/.../fig2_three_layer_spatial.png` | Top-down spatial map depicting Layer 1 (Cyan 45–70 m), Layer 2 (Amber 70–85 m), and Layer 3 (Violet 85–100 m) |
| **Electrical Schematic Diagram** | Figure 7.1 | `reports/.../fig3_hardware_wiring_diagram.png` | Complete circuit schematic for ESP32-A (sensors), ESP32-B (LEDs), and RA-02 LoRa modules |
| **Physical Bench Prototype Setup** | Figure 7.2 | `live_physical_bench_upgrade.png` | High-resolution photograph of the actual physical hardware bench operating on COM7 |
| **3D Digital Twin Interface** | Figure 7.3 | `shortest_website_view.png` | Screenshot of the live WebGL visualizer showing 3D scene, HUD telemetry, and physical hardware side panel |
| **Test Suite Coverage Breakdown** | Figure 8.1 | `reports/.../fig4_test_suite_breakdown.png` | Graphical distribution chart illustrating 100% pass rate across the 139 automated tests |

---

### 3. Literature Survey & Academic Citations Traceability

The 25 academic works cited in Chapter 12 are mapped to authoritative peer-reviewed publications and manufacturer datasheets:
1. **Seismic Footstep Detection:** Zeppelzauer et al. (2015), *IEEE Trans. Cybernetics*, doi:10.1109/TCYB.2014.2386927.
2. **Deep Learning Camera Traps:** Norouzzadeh et al. (2018), *Proc. Natl. Acad. Sci. USA (PNAS)*, doi:10.1073/pnas.1719367115.
3. **Forest Bioacoustics & ARUs:** Wrege et al. (2017), *Afr. J. Ecol.*, doi:10.1111/aje.12338.
4. **Wi-Fi CSI Signal Tools:** Halperin et al. (2011), *ACM SIGCOMM CCR*, doi:10.1145/1925861.1925870.
5. **Device-Free RF Activity Sensing:** Wang et al. (2017), *IEEE JSAC*, doi:10.1109/JSAC.2017.2679658.
6. **LoRa Conservation Sensor Networks:** Bjorck et al. (2019), *IEEE Access*, doi:10.1109/ACCESS.2019.2938812.
7. **Sub-GHz Foliage Propagation:** Sanchez-Iborra et al. (2018), *Sensors*, doi:10.3390/s18092805.
8. **PIR Animal Detection Nodes:** Ohashi et al. (2013), in *Proc. IEEE SENSORS*, doi:10.1109/ICSENS.2013.6688538.
9. **Digital Twin Concepts:** Grieves & Vickers (2017), *Transdisciplinary Perspectives on Complex Systems*, Springer.
10. **Digital Twin Categorical Review:** Kritzinger et al. (2018), *IFAC-PapersOnLine*, doi:10.1016/j.ifacol.2018.08.474.
11. **Digital Landscape Modeling:** Batty (2018), *Environ. Plan. B*, doi:10.1177/2399808318796416.
12. **SX1278 LoRa Transceiver Datasheet:** Semtech Corp., Rev. 7, 2020.
13. **ESP32 Microcontroller Datasheet:** Espressif Systems, Ver. 4.4, 2024.
14. **INMP441 I2S Microphone Datasheet:** InvenSense Inc., Rev. 1.1, 2014.
15. **Boids Flocking Behavioral Model:** Reynolds (1987), *ACM SIGGRAPH*, doi:10.1145/37401.37406.
16. **Camera Trap Machine Learning:** Tabak et al. (2019), *Methods Ecol. Evol.*, doi:10.1111/2041-210X.13120.
17. **LPWAN Unlicensed Bands Review:** Centenaro et al. (2016), *IEEE Wireless Commun.*, doi:10.1109/MWC.2016.7721743.
18. **Seismic Waves in Rocky Soil:** Mortimer et al. (2018), *J. Acoust. Soc. Am.*, vol. 144, no. 3.
19. **Camera Trapping Best Practices:** Rovero & Zimmermann (2016), Pelagic Publishing.
20. **Elephant Corridors of India Census:** MoEFCC / Wildlife Trust of India, 2nd ed., 2017.
21. **Terrestrial Acoustic Monitoring:** Blumstein et al. (2011), *Ecol. Indicators*, vol. 14, no. 1.
22. **3D Habitat Corridors Simulation:** Schneider et al. (2020), *Ecol. Modelling*, vol. 431.
23. **Vegetative Canopy Path Loss:** Cabrero (2020), *IEEE Sensors Letters*, vol. 4, no. 8.
24. **Three.js WebGL Graphics Library:** Three.js Authors, r128, 2024.
25. **Python Software Reference:** Python Software Foundation, Ver. 3.8/3.13, 2024.


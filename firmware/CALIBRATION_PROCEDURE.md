# PRW-Wild — Sensor Calibration and Threshold Management Procedure

This guide documents the procedures for tuning detection thresholds, establishing quiet baselines, and synchronizing sensitivity settings across the cyber-physical architecture.

---

## 1. Principles of Measurement

1. **HC-SR501 PIR Motion Sensor:**
   - Digital active-high signal with a $45\text{-second}$ stabilization warmup gate.
   - Requires no analog calibration; sensitivity potentiometer on module should be adjusted to 5-meter range.

2. **Piezoelectric Seismic Sensor (ADC1_CH7 on GPIO 35):**
   - Metric: Peak-to-Peak ADC Amplitude ($\Delta = \text{ADC}_{\max} - \text{ADC}_{\min}$) over a $20\text{ ms}$ sampling window ($80\text{ samples}$ @ $250\ \mu\text{s}$).
   - **Quiet Bench Baseline:** $10 - 50\text{ ADC counts}$.
   - **Footstep / Heavy Vibration:** $120 - 400\text{ ADC counts}$.
   - **Default Threshold:** $150\text{ ADC counts}$ with $35\text{ ADC}$ hysteresis and $600\text{ ms}$ debounce hold.

3. **INMP441 Digital MEMS Microphone (I²S on GPIO 25, 33, 34):**
   - Metric: Root-Mean-Square Amplitude ($\text{RMS} = \sqrt{\frac{1}{N}\sum x_i^2}$) calculated over $256\text{ samples}$ ($16\text{ ms}$ @ $16\text{ kHz}$).
   - Samples are 24-bit left-justified in 32-bit words, sign-extended via `sample >> 8`.
   - **Quiet Room Baseline:** $5,000 - 25,000\text{ RMS}$.
   - **Speech / Animal Call / Clapping:** $> 35,000\text{ RMS}$.
   - **Default Threshold:** $35,000\text{ RMS}$ with $6,000\text{ RMS}$ hysteresis and $600\text{ ms}$ debounce hold.
   - Note: Uncalibrated digital RMS values represent relative acoustic energy, NOT absolute dB SPL.

---

## 2. Calibration Workflows

### Method 1: Web Interface Sliders (Real-Time Interactive)
1. Open the PRW-Wild visualizer at `http://127.0.0.1:8000/`.
2. Inspect the **⚡ PHYSICAL HARDWARE** panel on the right sidebar.
3. Observe live readings for **PIEZO SEISMIC** and **INMP441 MIC**.
4. Adjust the sliders:
   - **Piezo Sensitivity Slider:** Range $30 - 1000\text{ ADC}$. Set lower for soft ground or further distance; higher to suppress heavy table vibrations.
   - **Microphone Sensitivity Slider:** Range $5,000 - 100,000\text{ RMS}$.
5. Click **CIRCUIT: ENABLED** to enable/disable the piezoelectric ADC protection gate.

### Method 2: HTTP REST API
Send a JSON payload to `/api/hardware/calibration`:
```bash
curl -X POST http://127.0.0.1:8000/api/hardware/calibration \
  -H "Content-Type: application/json" \
  -d '{"piezo_threshold": 160, "mic_threshold": 35000, "piezo_enabled": true}'
```

### Method 3: Direct USB Serial Command (COM7 @ 115200 baud)
Send over serial:
```text
PW1|SET_CALIB|160|35000|1\n
```
ESP32-B immediately confirms:
```text
PW1|CALIB_ACK|160|35000|1
```
And relays to ESP32-A on the next LoRa acknowledgement frame:
```text
PW1|ACK|B|<bootId>|<seq>|OK|160|35000|1
```
ESP32-A applies the new thresholds and logs:
```text
CALIBRATION_APPLIED: piezoThresh=160 micThresh=35000 piezoVerified=1
```


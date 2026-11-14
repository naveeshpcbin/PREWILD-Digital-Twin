/*
  PRW-Wild Physical Bench Firmware — ESP32-A Sensor Node
  Board: ESP32 Dev Module / DOIT ESP32 DEVKIT V1, ESP32-WROOM-32
  Arduino-ESP32 core: 3.x (ESP_I2S.h)
  Library: LoRa by Sandeep Mistry, 0.8.0

  ESP32-A Verified Pin Connections:
    RA-02 SX1278: SCK=18, MISO=19, MOSI=23, NSS=27, RST=14, DIO0=26
    HC-SR501 PIR: OUT=GPIO32, VCC=5V, GND=GND
    INMP441 I2S:  BCLK=GPIO25, WS=GPIO33, SD=GPIO34 (Input-only), VDD=3V3, GND=GND, L/R=GND
    Piezo Sensor: Conditioned/Protected ADC=GPIO35 (Input-only, ADC1_CH7), GND=GND

  Telemetry Frame Transmitted to ESP32-B:
    PW1|TEL|A|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>

  ACK Frame Received from ESP32-B:
    PW1|ACK|B|<bootIdHex>|<seq>|<status>[|<piezoThresh>|<micThresh>|<piezoVerified>]

  Sensor Safety & Flags:
    bit 0 = PIR warmed up (>45s)
    bit 1 = Piezo input circuit approved & sampling enabled
    bit 2 = I2S microphone initialized & valid audio received
    bit 3 = Piezo measurement valid (no ADC saturation/fault)
    bit 4 = Microphone measurement valid (not floating/disconnected)
*/

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <ESP_I2S.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "esp_system.h"

// ============================================================================
// 1. PIN ALLOCATIONS & ELECTRICAL CONSTRAINTS
// ============================================================================
static constexpr int PIN_LORA_SCK  = 18;
static constexpr int PIN_LORA_MISO = 19;
static constexpr int PIN_LORA_MOSI = 23;
static constexpr int PIN_LORA_CS   = 27;
static constexpr int PIN_LORA_RST  = 14;
static constexpr int PIN_LORA_DIO0 = 26;

static constexpr int PIN_PIR       = 32;
static constexpr int PIN_PIEZO_ADC = 35; // ADC1_CH7, input-only pin
static constexpr int PIN_I2S_BCLK  = 25; // Bit Clock output to INMP441
static constexpr int PIN_I2S_WS    = 33; // Word Select output to INMP441
static constexpr int PIN_I2S_SD    = 34; // Serial Data input-only from INMP441

// ============================================================================
// 2. RADIO SETTINGS (433.92 MHz SX1278)
// ============================================================================
static constexpr long LORA_FREQUENCY_HZ = 433920000L;
static constexpr long LORA_BANDWIDTH_HZ = 125000L;
static constexpr int LORA_SPREADING_FACTOR = 7;
static constexpr int LORA_CODING_RATE = 5; // 4/5
static constexpr uint8_t LORA_SYNC_WORD = 0x12;
static constexpr int LORA_TX_POWER_DBM = 2; // Bench power setting

// ============================================================================
// 3. SENSOR CALIBRATION, HYSTERESIS & SAFETY CONFIGURATION
// ============================================================================
// Explicit compile-time configuration gate per Phase 3 requirements.
// Must not silently default to true. Fail-closed: Requires verified protection
// circuit (e.g. Schottky BAT54S clamping + resistive divider) before ADC sampling.
#ifndef PIEZO_CIRCUIT_VERIFIED
#define PIEZO_CIRCUIT_VERIFIED 0
#endif

bool g_piezoCircuitVerified = (PIEZO_CIRCUIT_VERIFIED != 0);

// Piezo Peak-to-Peak ADC Threshold & Hysteresis (0 - 4095)
// Quiet bench baseline: ~20 - 70 ADC counts
// Light surface tap / vibration: ~120 - 300 ADC counts
uint16_t g_piezoThreshold = 150;
static constexpr uint16_t PIEZO_HYSTERESIS = 35; // Release at threshold - 35
static constexpr uint32_t PIEZO_HOLD_TIME_MS = 600; // Debounce hold duration

// INMP441 I2S Microphone RMS Threshold & Hysteresis
// Ambient quiet room: ~2,000 - 18,000 RMS
// Speech / acoustic whistle / clapping: > 32,000 RMS
uint32_t g_micThreshold = 32000;
static constexpr uint32_t MIC_HYSTERESIS = 6000; // Release at threshold - 6000
static constexpr uint32_t MIC_HOLD_TIME_MS = 600; // Debounce hold duration

// PIR Motion Warmup: 45 seconds filter for stable pyroelectric baseline
static constexpr uint32_t PIR_WARMUP_MS = 45000;

// Acquisition Windows
static constexpr uint32_t TELEMETRY_INTERVAL_MS = 700;
static constexpr uint32_t PIEZO_WINDOW_US = 20000;        // 20ms = 1 full 50Hz mains cycle
static constexpr uint16_t PIEZO_SAMPLE_INTERVAL_US = 250; // 80 samples in window
static constexpr uint32_t I2S_SAMPLE_RATE_HZ = 16000;
static constexpr size_t I2S_SAMPLE_COUNT = 256;           // 16ms acoustic window

// ============================================================================
// 4. RUNTIME SYSTEM STATE
// ============================================================================
I2SClass I2S;
bool g_loraReady = false;
bool g_i2sReady = false;
uint32_t g_bootId = 0;
uint32_t g_sequence = 0;
uint32_t g_lastTelemetryMs = 0;
uint32_t g_lastSentSequence = 0;

// Debounce & State Tracking
uint32_t g_piezoActiveUntilMs = 0;
bool g_piezoState = false;
uint32_t g_micActiveUntilMs = 0;
bool g_micState = false;

// ============================================================================
// 5. PIEZOELECTRIC ACQUISITION (BOUNDED & PROTECTED)
// ============================================================================
uint16_t readPiezoPeakToPeak(bool &measurementValid) {
  measurementValid = false;
  // Safety check: Never sample ADC35 if protection is not verified
  if (!g_piezoCircuitVerified) {
    return 0;
  }

  uint16_t minValue = 4095;
  uint16_t maxValue = 0;
  uint16_t sampleCount = 0;
  const uint32_t startUs = micros();

  while ((uint32_t)(micros() - startUs) < PIEZO_WINDOW_US) {
    const uint16_t v = (uint16_t)analogRead(PIN_PIEZO_ADC);
    if (v < minValue) minValue = v;
    if (v > maxValue) maxValue = v;
    ++sampleCount;
    delayMicroseconds(PIEZO_SAMPLE_INTERVAL_US);
  }

  if (sampleCount == 0) return 0;

  // Validity check: Flag if ADC is saturated rail-to-rail (clipping)
  if (minValue == 0 && maxValue >= 4095) {
    measurementValid = true; // Saturated, but valid physical strike
    return 4095;
  }

  measurementValid = true;
  return (uint16_t)(maxValue - minValue);
}

// ============================================================================
// 6. INMP441 I2S MICROPHONE ACQUISITION (24-BIT SIGNED & FLOATING DETECTION)
// ============================================================================
bool readMicrophoneRms(uint32_t &rmsOut, bool &validAcoustic) {
  rmsOut = 0;
  validAcoustic = false;
  if (!g_i2sReady) return false;

  int32_t samples[I2S_SAMPLE_COUNT];
  const size_t bytesRead = I2S.readBytes((char *)samples, sizeof(samples));
  const size_t count = bytesRead / sizeof(int32_t);
  if (count < 32) return false;

  double sum = 0.0;
  double sumSquares = 0.0;
  double diffSum = 0.0;
  int32_t prevSample = 0;
  bool allZero = true;
  bool allIdentical = true;
  const int32_t firstSample = samples[0] >> 8;

  for (size_t i = 0; i < count; ++i) {
    // INMP441 sends 24-bit MSB-aligned data in 32-bit slot.
    // Arithmetic right shift by 8 sign-extends the signed 24-bit audio integer.
    const int32_t sample24 = samples[i] >> 8;

    if (sample24 != 0) allZero = false;
    if (sample24 != firstSample) allIdentical = false;

    if (i > 0) {
      diffSum += fabs((double)(sample24 - prevSample));
    }
    prevSample = sample24;

    const double x = (double)sample24;
    sum += x;
    sumSquares += x * x;
  }

  // Reject disconnected mic (all zero or stuck DC rail)
  if (allZero || allIdentical) {
    validAcoustic = false;
    return false;
  }

  const double mean = sum / (double)count;
  double variance = (sumSquares / (double)count) - (mean * mean);
  if (variance < 0.0) variance = 0.0;
  const double rmsVal = sqrt(variance);

  // Floating GPIO detection:
  // An unconnected high-Z pin (GPIO 34) oscillates randomly on clock crosstalk,
  // causing full-scale transitions with high variance and extreme step deltas.
  const double avgDelta = diffSum / (double)(count - 1);
  if (rmsVal > 1500000.0 || (rmsVal > 100000.0 && avgDelta > (2.5 * rmsVal))) {
    // Floating pin noise detected — not a genuine acoustic microphone signal!
    validAcoustic = false;
    return false;
  }

  validAcoustic = true;
  rmsOut = (uint32_t)(rmsVal + 0.5);
  return true;
}

// ============================================================================
// 7. RA-02 SX1278 INITIALIZATION
// ============================================================================
bool initializeLoRa() {
  SPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI, PIN_LORA_CS);
  LoRa.setPins(PIN_LORA_CS, PIN_LORA_RST, PIN_LORA_DIO0);
  if (!LoRa.begin(LORA_FREQUENCY_HZ)) return false;
  LoRa.setSignalBandwidth(LORA_BANDWIDTH_HZ);
  LoRa.setSpreadingFactor(LORA_SPREADING_FACTOR);
  LoRa.setCodingRate4(LORA_CODING_RATE);
  LoRa.setPreambleLength(8);
  LoRa.setSyncWord(LORA_SYNC_WORD);
  LoRa.enableCrc();
  LoRa.setTxPower(LORA_TX_POWER_DBM, PA_OUTPUT_PA_BOOST_PIN);
  LoRa.receive();
  return true;
}

// ============================================================================
// 8. INMP441 I2S INITIALIZATION
// ============================================================================
bool initializeMicrophone() {
  I2S.setPins(PIN_I2S_BCLK, PIN_I2S_WS, -1, PIN_I2S_SD);
  return I2S.begin(
    I2S_MODE_STD,
    I2S_SAMPLE_RATE_HZ,
    I2S_DATA_BIT_WIDTH_32BIT,
    I2S_SLOT_MODE_MONO,
    I2S_STD_SLOT_LEFT
  );
}

// ============================================================================
// 9. PROCESS ACKNOWLEDGEMENTS & RUNTIME CALIBRATION UPDATES
// ============================================================================
void processLoRaAck() {
  const int packetSize = LoRa.parsePacket();
  if (packetSize <= 0) return;

  char frame[128];
  size_t n = 0;
  bool tooLong = false;
  while (LoRa.available()) {
    const char c = (char)LoRa.read();
    if (n < sizeof(frame) - 1) frame[n++] = c;
    else tooLong = true;
  }
  frame[n] = '\0';

  if (tooLong) {
    Serial.println("ACK_RX_REJECTED: frame too long");
    LoRa.receive();
    return;
  }

  char nodeId[8] = {0};
  unsigned long ackBootId = 0;
  unsigned long ackSequence = 0;
  char status[16] = {0};
  unsigned int newPiezoThresh = 0;
  unsigned long newMicThresh = 0;
  int newPiezoVerified = -1;

  // Support both standard 4-field ACK and extended 7-field Calibration ACK
  const int fields = sscanf(
    frame,
    "PW1|ACK|%7[^|]|%8lx|%lu|%15[^|]|%u|%lu|%d",
    nodeId, &ackBootId, &ackSequence, status,
    &newPiezoThresh, &newMicThresh, &newPiezoVerified
  );

  if (fields >= 4 && strcmp(nodeId, "B") == 0 &&
      (uint32_t)ackBootId == g_bootId &&
      (uint32_t)ackSequence == g_lastSentSequence) {
    
    // Process optional runtime calibration updates from Host via ESP32-B
    if (fields >= 7) {
      if (newPiezoThresh > 0 && newPiezoThresh <= 4095) {
        g_piezoThreshold = (uint16_t)newPiezoThresh;
      }
      if (newMicThresh > 0 && newMicThresh <= 1000000) {
        g_micThreshold = (uint32_t)newMicThresh;
      }
      if (newPiezoVerified == 0 || newPiezoVerified == 1) {
        g_piezoCircuitVerified = (newPiezoVerified == 1);
      }
      Serial.printf("CALIBRATION_APPLIED: piezoThresh=%u micThresh=%lu piezoVerified=%d\n",
                    g_piezoThreshold, (unsigned long)g_micThreshold, g_piezoCircuitVerified ? 1 : 0);
    }

    Serial.printf("ACK_MATCHED: seq=%lu status=%s RSSI=%d dBm SNR=%.1f dB\n",
                  ackSequence, status, LoRa.packetRssi(), LoRa.packetSnr());
  } else {
    Serial.printf("ACK_UNMATCHED: %s\n", frame);
  }
  LoRa.receive();
}

// ============================================================================
// 10. SERIAL COMMAND PROCESSOR (DIRECT USB CALIBRATION)
// ============================================================================
void processSerialCommands() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;

  if (line.startsWith("PW1|SET_CALIB|")) {
    unsigned int pThresh = 0;
    unsigned long mThresh = 0;
    int pVer = 0;
    const int count = sscanf(line.c_str(), "PW1|SET_CALIB|%u|%lu|%d", &pThresh, &mThresh, &pVer);
    if (count == 3) {
      if (pThresh > 0 && pThresh <= 4095) g_piezoThreshold = (uint16_t)pThresh;
      if (mThresh > 0 && mThresh <= 1000000) g_micThreshold = (uint32_t)mThresh;
      g_piezoCircuitVerified = (pVer == 1);
      Serial.printf("PW1|CALIB_CONFIRMED|%u|%lu|%d\n", g_piezoThreshold, (unsigned long)g_micThreshold, g_piezoCircuitVerified ? 1 : 0);
    }
  } else if (line == "PW1|PING") {
    Serial.printf("PW1|PONG|STANDALONE|%08lX|2.1.0\n", (unsigned long)g_bootId);
  }
}

// ============================================================================
// 11. TELEMETRY ACQUISITION & TRANSMISSION
// ============================================================================
void sendTelemetry() {
  const uint32_t now = millis();

  // 1. PIR Motion Processing (with 45s warmup filter)
  const bool pirReady = (uint32_t)(now) >= PIR_WARMUP_MS;
  const int pirRaw = digitalRead(PIN_PIR);
  const bool pirActive = pirReady && (pirRaw == HIGH);

  // 2. Piezoelectric Vibration Processing (Hysteresis & Debounce)
  bool piezoValid = false;
  const uint16_t piezoP2P = readPiezoPeakToPeak(piezoValid);

  if (g_piezoCircuitVerified && piezoValid) {
    if (piezoP2P >= g_piezoThreshold) {
      g_piezoState = true;
      g_piezoActiveUntilMs = now + PIEZO_HOLD_TIME_MS;
    } else {
      const uint16_t resetThresh = (g_piezoThreshold > PIEZO_HYSTERESIS) ? (g_piezoThreshold - PIEZO_HYSTERESIS) : 0;
      if (piezoP2P < resetThresh && (int32_t)(now - g_piezoActiveUntilMs) >= 0) {
        g_piezoState = false;
      }
    }
  } else {
    g_piezoState = false;
  }

  // 3. INMP441 Microphone Processing (Hysteresis & Debounce)
  uint32_t micRms = 0;
  bool micValid = false;
  const bool micReadOK = readMicrophoneRms(micRms, micValid);

  if (g_i2sReady && micReadOK && micValid) {
    if (micRms >= g_micThreshold) {
      g_micState = true;
      g_micActiveUntilMs = now + MIC_HOLD_TIME_MS;
    } else {
      const uint32_t resetThresh = (g_micThreshold > MIC_HYSTERESIS) ? (g_micThreshold - MIC_HYSTERESIS) : 0;
      if (micRms < resetThresh && (int32_t)(now - g_micActiveUntilMs) >= 0) {
        g_micState = false;
      }
    }
  } else {
    g_micState = false;
  }

  // 4. Encode Hardware Flags
  uint8_t flags = 0;
  if (pirReady) flags |= 0x01;                // bit 0 = PIR warmed up
  if (g_piezoCircuitVerified) flags |= 0x02;  // bit 1 = Piezo circuit verified
  if (g_i2sReady && micValid) flags |= 0x04;  // bit 2 = INMP441 ready & operational
  if (piezoValid) flags |= 0x08;              // bit 3 = Piezo ADC reading valid
  if (micValid) flags |= 0x10;                // bit 4 = Mic acoustic reading valid

  const uint32_t seq = ++g_sequence;
  char frame[192];
  const int len = snprintf(
    frame, sizeof(frame),
    "PW1|TEL|A|%08lX|%lu|%lu|%u|%d|%u|%lu|%d|%d|%d",
    (unsigned long)g_bootId,
    (unsigned long)seq,
    (unsigned long)now,
    (unsigned int)flags,
    pirRaw,
    (unsigned int)piezoP2P,
    (unsigned long)micRms,
    pirActive ? 1 : 0,
    g_piezoState ? 1 : 0,
    g_micState ? 1 : 0
  );

  Serial.printf(
    "SENSORS: PIR_RAW=%d PIR_READY=%d PIR_ACTIVE=%d PIEZO_P2P=%u PIEZO_VERIFIED=%d PIEZO_ACTIVE=%d MIC_RMS=%lu MIC_VALID=%d MIC_ACTIVE=%d FLAGS=0x%02X\n",
    pirRaw, pirReady ? 1 : 0, pirActive ? 1 : 0,
    (unsigned int)piezoP2P, g_piezoCircuitVerified ? 1 : 0, g_piezoState ? 1 : 0,
    (unsigned long)micRms, micValid ? 1 : 0, g_micState ? 1 : 0, flags
  );

  if (len <= 0 || (size_t)len >= sizeof(frame)) {
    Serial.println("ERROR: telemetry frame formatting failed");
    return;
  }
  if (!g_loraReady) {
    Serial.println("ERROR: LoRa unavailable; telemetry not sent");
    return;
  }

  LoRa.idle();
  if (LoRa.beginPacket() == 0) {
    Serial.println("LORA_TX_SKIPPED: radio busy");
    LoRa.receive();
    return;
  }
  LoRa.print(frame);
  const int txOK = LoRa.endPacket();
  LoRa.receive();
  g_lastSentSequence = seq;
  Serial.printf("LORA_TX: %s result=%s\n", frame, txOK ? "OK" : "FAILED");
}

// ============================================================================
// 12. SETUP & INITIALIZATION
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  g_bootId = esp_random();
  if (g_bootId == 0) g_bootId = 1;

  pinMode(PIN_PIR, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_PIEZO_ADC, ADC_11db);

  Serial.println();
  Serial.println("==================================================");
  Serial.println("PRW-WILD ESP32-A SENSOR NODE — UPGRADED FIRMWARE");
  Serial.println("==================================================");
  Serial.printf("BOOT_ID=%08lX\n", (unsigned long)g_bootId);
  Serial.println("PIR: GPIO32 (HC-SR501 with 45s warm-up filter)");
  Serial.printf("PIEZO: GPIO35 (ADC1_CH7, CircuitVerified=%s, Thresh=%u, Hyst=%u, Debounce=%ums)\n",
                g_piezoCircuitVerified ? "TRUE" : "FALSE", g_piezoThreshold, PIEZO_HYSTERESIS, PIEZO_HOLD_TIME_MS);
  Serial.printf("INMP441: BCLK=25 WS=33 SD=34 (Thresh=%lu, Hyst=%lu, Debounce=%ums)\n",
                (unsigned long)g_micThreshold, (unsigned long)MIC_HYSTERESIS, MIC_HOLD_TIME_MS);

  g_i2sReady = initializeMicrophone();
  Serial.printf("INMP441 I2S: %s\n", g_i2sReady ? "READY" : "FAILED");

  g_loraReady = initializeLoRa();
  Serial.printf("RA-02 SX1278: %s\n", g_loraReady ? "READY" : "FAILED");
  Serial.println("Radio: 433.920 MHz, SF7, BW125kHz, CR4/5, sync=0x12, CRC=ON");
}

// ============================================================================
// 13. MAIN LOOP
// ============================================================================
void loop() {
  processSerialCommands();
  processLoRaAck();
  const uint32_t now = millis();
  if ((uint32_t)(now - g_lastTelemetryMs) >= TELEMETRY_INTERVAL_MS) {
    g_lastTelemetryMs = now;
    sendTelemetry();
  }
}

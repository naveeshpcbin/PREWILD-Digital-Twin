/*
  PRW-Wild physical bench firmware — ESP32-B LoRa receiver + 6 LEDs + USB gateway
  Board: ESP32 Dev Module / DOIT ESP32 DEVKIT V1, ESP32-WROOM-32
  Library: LoRa by Sandeep Mistry, 0.8.0

  ESP32-B LoRa: SCK=18, MISO=19, MOSI=23, NSS=27, RST=14, DIO0=26

  FINAL ESP32-B LED MAP:
    LED1 PIR indicator         GPIO32
    LED2 Piezo indicator       GPIO33
    LED3 Microphone indicator  GPIO25
    LED4 Node-A heartbeat      GPIO13
    LED5 LoRa packet pulse     GPIO21
    LED6 Overall sensor alert  GPIO22

  IMPORTANT: GPIO34 and GPIO35 are input-only on classic ESP32-WROOM-32.
  Do not use them as LED outputs. All LEDs are driven with individual 2 kΩ ballast resistors.

  Receives from Node A:
    PW1|TEL|A|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>
  Sends to Node A:
    PW1|ACK|B|<bootIdHex>|<seq>|<status>[|<piezoThresh>|<micThresh>|<piezoVerified>]
  USB telemetry to Python Host:
    PW1|TEL_USB|B|<bootIdHex>|<seq>|<uptimeMs>|<flags>|<pirRaw>|<piezoP2P>|<micRms>|<pirActive>|<piezoActive>|<micActive>|<rssi>|<snr>

  Operating Modes:
    MODE 1: AUTO_SENSOR (Default) — Physical sensors drive physical LEDs.
    MODE 2: MANUAL — Operator independently controls all 6 LEDs.
    MODE 3: SIMULATION — Digital twin simulation mode; physical LEDs disarmed by default.
*/

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <stdio.h>
#include <string.h>

// ---------- ESP32-B pin map ----------
static constexpr int PIN_LORA_SCK  = 18;
static constexpr int PIN_LORA_MISO = 19;
static constexpr int PIN_LORA_MOSI = 23;
static constexpr int PIN_LORA_CS   = 27;
static constexpr int PIN_LORA_RST  = 14;
static constexpr int PIN_LORA_DIO0 = 26;

static constexpr uint8_t LED_PIR       = 32;
static constexpr uint8_t LED_PIEZO     = 33;
static constexpr uint8_t LED_MIC       = 25;
static constexpr uint8_t LED_HEARTBEAT = 13;
static constexpr uint8_t LED_LORA      = 21;
static constexpr uint8_t LED_ALERT     = 22;

// ---------- Must match Node A ----------
static constexpr long LORA_FREQUENCY_HZ = 433920000L;
static constexpr long LORA_BANDWIDTH_HZ = 125000L;
static constexpr int LORA_SPREADING_FACTOR = 7;
static constexpr int LORA_CODING_RATE = 5;
static constexpr uint8_t LORA_SYNC_WORD = 0x12;
static constexpr int LORA_TX_POWER_DBM = 2;

static constexpr uint32_t NODE_A_TIMEOUT_MS = 2200;
static constexpr uint32_t LORA_LED_PULSE_MS = 120;

// Operating Modes
enum OperatingMode {
  MODE_AUTO_SENSOR = 0,
  MODE_MANUAL = 1,
  MODE_SIMULATION = 2
};

OperatingMode g_operatingMode = MODE_AUTO_SENSOR;
bool g_manualLeds[7] = {false, false, false, false, false, false, false}; // index 1..6

bool g_loraReady = false;
uint32_t g_lastNodeAMessageMs = 0;
uint32_t g_loraLedOffAtMs = 0;
uint32_t g_currentBootId = 0;
uint32_t g_lastSequence = 0;
bool g_haveBootId = false;
bool g_haveSequence = false;

// Pending calibration to forward to Node A via LoRa ACK
uint16_t g_calibPiezoThreshold = 150;
uint32_t g_calibMicThreshold = 32000;
int g_calibPiezoVerified = 1;
bool g_calibPendingSync = false;

void setLedPin(uint8_t pin, bool state) {
  digitalWrite(pin, state ? HIGH : LOW);
}

void applyManualLeds() {
  setLedPin(LED_PIR, g_manualLeds[1]);
  setLedPin(LED_PIEZO, g_manualLeds[2]);
  setLedPin(LED_MIC, g_manualLeds[3]);
  setLedPin(LED_HEARTBEAT, g_manualLeds[4]);
  setLedPin(LED_LORA, g_manualLeds[5]);
  setLedPin(LED_ALERT, g_manualLeds[6]);
}

void applySensorLeds(bool pir, bool piezo, bool mic) {
  if (g_operatingMode != MODE_AUTO_SENSOR) return;
  digitalWrite(LED_PIR, pir ? HIGH : LOW);
  digitalWrite(LED_PIEZO, piezo ? HIGH : LOW);
  digitalWrite(LED_MIC, mic ? HIGH : LOW);
  digitalWrite(LED_ALERT, (pir || piezo || mic) ? HIGH : LOW);
}

void sendAck(uint32_t bootId, uint32_t sequence, const char *status) {
  char ack[128];
  if (g_calibPendingSync) {
    snprintf(ack, sizeof(ack), "PW1|ACK|B|%08lX|%lu|%s|%u|%lu|%d",
             (unsigned long)bootId, (unsigned long)sequence, status,
             g_calibPiezoThreshold, (unsigned long)g_calibMicThreshold, g_calibPiezoVerified);
  } else {
    snprintf(ack, sizeof(ack), "PW1|ACK|B|%08lX|%lu|%s",
             (unsigned long)bootId, (unsigned long)sequence, status);
  }
  LoRa.idle();
  if (LoRa.beginPacket() == 0) {
    Serial.println("ACK_TX_FAILED: radio busy");
    LoRa.receive();
    return;
  }
  LoRa.print(ack);
  const int ok = LoRa.endPacket();
  Serial.printf("ACK_TX: %s result=%s\n", ack, ok ? "OK" : "FAILED");
  LoRa.receive();
}

void processSerialCommands() {
  while (Serial.available()) {
    char cmdBuf[128];
    size_t n = Serial.readBytesUntil('\n', cmdBuf, sizeof(cmdBuf) - 1);
    cmdBuf[n] = '\0';
    if (n == 0) continue;
    if (n > 0 && cmdBuf[n - 1] == '\r') {
      cmdBuf[n - 1] = '\0';
    }

    // 1. SET_CALIB: PW1|SET_CALIB|<pThresh>|<mThresh>|<pVer>
    unsigned int pThresh = 0;
    unsigned long mThresh = 0;
    int pVer = 0;
    if (sscanf(cmdBuf, "PW1|SET_CALIB|%u|%lu|%d", &pThresh, &mThresh, &pVer) == 3) {
      if (pThresh > 0 && pThresh <= 4095) g_calibPiezoThreshold = (uint16_t)pThresh;
      if (mThresh > 0 && mThresh <= 1000000) g_calibMicThreshold = (uint32_t)mThresh;
      if (pVer == 0 || pVer == 1) g_calibPiezoVerified = pVer;
      g_calibPendingSync = true;
      Serial.printf("PW1|CALIB_ACK|%u|%lu|%d\n", g_calibPiezoThreshold, (unsigned long)g_calibMicThreshold, g_calibPiezoVerified);
      continue;
    }

    // 2. MODE: PW1|MODE|<AUTO_SENSOR|MANUAL|SIMULATION>
    char modeStr[32] = {0};
    if (sscanf(cmdBuf, "PW1|MODE|%31s", modeStr) == 1) {
      if (strcasecmp(modeStr, "AUTO_SENSOR") == 0 || strcasecmp(modeStr, "AUTO") == 0) {
        g_operatingMode = MODE_AUTO_SENSOR;
        Serial.println("PW1|MODE_ACK|AUTO_SENSOR");
      } else if (strcasecmp(modeStr, "MANUAL") == 0 || strcasecmp(modeStr, "HARDWARE_TEST") == 0) {
        g_operatingMode = MODE_MANUAL;
        applyManualLeds();
        Serial.println("PW1|MODE_ACK|MANUAL");
      } else if (strcasecmp(modeStr, "SIMULATION") == 0 || strcasecmp(modeStr, "SIMULATION_ONLY") == 0) {
        g_operatingMode = MODE_SIMULATION;
        digitalWrite(LED_PIR, LOW);
        digitalWrite(LED_PIEZO, LOW);
        digitalWrite(LED_MIC, LOW);
        digitalWrite(LED_ALERT, LOW);
        Serial.println("PW1|MODE_ACK|SIMULATION");
      } else {
        Serial.printf("PW1|ERR_INVALID_MODE|%s\n", modeStr);
      }
      continue;
    }

    // 3. MANUAL LED CONTROL: PW1|LED|<1..6>|<0|1>
    int ledNum = 0;
    int ledState = 0;
    if (sscanf(cmdBuf, "PW1|LED|%d|%d", &ledNum, &ledState) == 2) {
      if (ledNum >= 1 && ledNum <= 6) {
        g_manualLeds[ledNum] = (ledState != 0);
        if (g_operatingMode == MODE_MANUAL) {
          uint8_t targetPin = 0;
          switch (ledNum) {
            case 1: targetPin = LED_PIR; break;
            case 2: targetPin = LED_PIEZO; break;
            case 3: targetPin = LED_MIC; break;
            case 4: targetPin = LED_HEARTBEAT; break;
            case 5: targetPin = LED_LORA; break;
            case 6: targetPin = LED_ALERT; break;
          }
          if (targetPin != 0) setLedPin(targetPin, g_manualLeds[ledNum]);
        }
        Serial.printf("PW1|LED_ACK|%d|%d\n", ledNum, ledState ? 1 : 0);
      } else {
        Serial.printf("PW1|ERR_INVALID_LED|%d\n", ledNum);
      }
      continue;
    }

    // 4. MANUAL LED ALL: PW1|LED_ALL|<0|1>
    if (sscanf(cmdBuf, "PW1|LED_ALL|%d", &ledState) == 1) {
      for (int i = 1; i <= 6; ++i) g_manualLeds[i] = (ledState != 0);
      if (g_operatingMode == MODE_MANUAL) {
        applyManualLeds();
      }
      Serial.printf("PW1|LED_ALL_ACK|%d\n", ledState ? 1 : 0);
      continue;
    }

    // 5. PING: PW1|PING
    if (strcmp(cmdBuf, "PW1|PING") == 0) {
      const char* modeName = (g_operatingMode == MODE_AUTO_SENSOR) ? "AUTO_SENSOR" :
                             (g_operatingMode == MODE_MANUAL) ? "MANUAL" : "SIMULATION";
      Serial.printf("PW1|PONG|B|%s|2.0.0\n", modeName);
      continue;
    }

    // 6. EMERGENCY ALL-OFF: PW1|EMERGENCY_STOP or PW1|CMD|...|ALL|OFF
    if (strcmp(cmdBuf, "PW1|EMERGENCY_STOP") == 0 || strstr(cmdBuf, "|ALL|OFF") != NULL) {
      for (int i = 1; i <= 6; ++i) g_manualLeds[i] = false;
      digitalWrite(LED_PIR, LOW);
      digitalWrite(LED_PIEZO, LOW);
      digitalWrite(LED_MIC, LOW);
      digitalWrite(LED_HEARTBEAT, LOW);
      digitalWrite(LED_LORA, LOW);
      digitalWrite(LED_ALERT, LOW);
      Serial.println("PW1|ACK|ALL|ALL_OFF");
      continue;
    }

    // 7. SIMULATION / LAYER COMMAND: PW1|CMD|<session>|<seq>|<animal>|<layer>|<trans>
    char session[16] = {0};
    unsigned long cmdSeq = 0;
    char animal[32] = {0};
    char layer[16] = {0};
    char trans[16] = {0};
    if (sscanf(cmdBuf, "PW1|CMD|%15[^|]|%lu|%31[^|]|%15[^|]|%15s", session, &cmdSeq, animal, layer, trans) == 5) {
      bool activeState = (strcasecmp(trans, "ENTER") == 0 || strcasecmp(trans, "ON") == 0);
      if (g_operatingMode == MODE_SIMULATION) {
        if (strcasecmp(layer, "L1") == 0) digitalWrite(LED_PIR, activeState ? HIGH : LOW);
        else if (strcasecmp(layer, "L2") == 0) digitalWrite(LED_PIEZO, activeState ? HIGH : LOW);
        else if (strcasecmp(layer, "L3") == 0) digitalWrite(LED_MIC, activeState ? HIGH : LOW);
      }
      Serial.printf("PW1|ACK|%s|%lu|OK|%s|%s\n", session, cmdSeq, layer, activeState ? "ACTIVE" : "INACTIVE");
      continue;
    }
  }
}

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

void rejectPacket(const char *reason, const char *frame) {
  Serial.printf("RX_REJECTED: %s | %s\n", reason, frame);
  LoRa.receive();
}

void handleTelemetryPacket() {
  char frame[192];
  size_t n = 0;
  bool tooLong = false;
  while (LoRa.available()) {
    const char c = (char)LoRa.read();
    if (n < sizeof(frame) - 1) frame[n++] = c;
    else tooLong = true;
  }
  frame[n] = '\0';
  if (tooLong) {
    rejectPacket("frame too long", frame);
    return;
  }

  char nodeId[8] = {0};
  unsigned long bootIdUL = 0;
  unsigned long sequenceUL = 0;
  unsigned long uptimeUL = 0;
  unsigned int flags = 0;
  int pirRaw = 0;
  unsigned int piezoP2P = 0;
  unsigned long micRms = 0;
  int pirActiveInt = 0;
  int piezoActiveInt = 0;
  int micActiveInt = 0;

  const int fields = sscanf(
    frame,
    "PW1|TEL|%7[^|]|%8lx|%lu|%lu|%u|%d|%u|%lu|%d|%d|%d",
    nodeId, &bootIdUL, &sequenceUL, &uptimeUL, &flags, &pirRaw,
    &piezoP2P, &micRms, &pirActiveInt, &piezoActiveInt, &micActiveInt
  );

  if (fields != 11 || strcmp(nodeId, "A") != 0 ||
      (pirRaw != LOW && pirRaw != HIGH) ||
      (pirActiveInt != 0 && pirActiveInt != 1) ||
      (piezoActiveInt != 0 && piezoActiveInt != 1) ||
      (micActiveInt != 0 && micActiveInt != 1)) {
    rejectPacket("invalid telemetry fields", frame);
    return;
  }

  const uint32_t bootId = (uint32_t)bootIdUL;
  const uint32_t sequence = (uint32_t)sequenceUL;
  const int rssi = LoRa.packetRssi();
  const float snr = LoRa.packetSnr();

  // A new ESP32-A boot ID starts a new sequence session.
  if (!g_haveBootId || bootId != g_currentBootId) {
    g_currentBootId = bootId;
    g_haveBootId = true;
    g_haveSequence = false;
    Serial.printf("NODE_A_SESSION: boot_id=%08lX\n", (unsigned long)bootId);
  }

  if (g_haveSequence) {
    const int32_t delta = (int32_t)(sequence - g_lastSequence);
    if (delta == 0) {
      g_lastNodeAMessageMs = millis();
      if (g_operatingMode != MODE_MANUAL) {
        digitalWrite(LED_LORA, HIGH);
        g_loraLedOffAtMs = millis() + LORA_LED_PULSE_MS;
      }
      Serial.printf("DUPLICATE: boot=%08lX seq=%lu; outputs unchanged\n",
                    (unsigned long)bootId, (unsigned long)sequence);
      sendAck(bootId, sequence, "DUPLICATE");
      return;
    }
    if (delta < 0) {
      Serial.printf("STALE_PACKET: boot=%08lX seq=%lu last=%lu\n",
                    (unsigned long)bootId, (unsigned long)sequence,
                    (unsigned long)g_lastSequence);
      sendAck(bootId, sequence, "ERR_STALE");
      return;
    }
  }

  g_lastSequence = sequence;
  g_haveSequence = true;
  g_lastNodeAMessageMs = millis();

  const bool pirReady = (flags & 0x01U) != 0;
  const bool piezoReady = (flags & 0x02U) != 0;
  const bool micReady = (flags & 0x04U) != 0;

  // Never activate an indicator for a sensor the transmitter reports as unavailable.
  const bool pirActive = pirReady && (pirActiveInt == 1);
  const bool piezoActive = piezoReady && (piezoActiveInt == 1);
  const bool micActive = micReady && (micActiveInt == 1);

  if (g_operatingMode == MODE_AUTO_SENSOR) {
    applySensorLeds(pirActive, piezoActive, micActive);
    digitalWrite(LED_LORA, HIGH);
    g_loraLedOffAtMs = millis() + LORA_LED_PULSE_MS;
  } else if (g_operatingMode == MODE_SIMULATION) {
    digitalWrite(LED_LORA, HIGH);
    g_loraLedOffAtMs = millis() + LORA_LED_PULSE_MS;
  }

  // Machine-readable USB line streamed to Python serial parser.
  Serial.printf(
    "PW1|TEL_USB|B|%08lX|%lu|%lu|%u|%d|%u|%lu|%d|%d|%d|%d|%.1f\n",
    (unsigned long)bootId, (unsigned long)sequence, uptimeUL, flags,
    pirRaw, piezoP2P, micRms,
    pirActive ? 1 : 0, piezoActive ? 1 : 0, micActive ? 1 : 0,
    rssi, snr
  );

  Serial.printf(
    "SENSOR_STATE: PIR=%s PIEZO=%s MIC=%s OVERALL=%s RSSI=%d SNR=%.1f\n",
    pirActive ? "ACTIVE" : (pirReady ? "NORMAL" : "WARMING"),
    piezoActive ? "ACTIVE" : (piezoReady ? "NORMAL" : "DISABLED"),
    micActive ? "ACTIVE" : (micReady ? "NORMAL" : "NOT_READY"),
    (pirActive || piezoActive || micActive) ? "ALERT" : "NORMAL",
    rssi, snr
  );

  sendAck(bootId, sequence, "OK");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  const uint8_t ledPins[] = {
    LED_PIR, LED_PIEZO, LED_MIC, LED_HEARTBEAT, LED_LORA, LED_ALERT
  };
  for (size_t i = 0; i < sizeof(ledPins) / sizeof(ledPins[0]); ++i) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  Serial.println();
  Serial.println("===============================================");
  Serial.println("PRW-WILD ESP32-B RECEIVER + SIX-LED USB GATEWAY");
  Serial.println("===============================================");
  Serial.println("LED map: PIR=32 PIEZO=33 MIC=25 HEARTBEAT=13 LORA=21 ALERT=22");
  Serial.println("Do not connect LEDs to GPIO34 or GPIO35 (input-only pins).");
  Serial.println("Operating Mode: AUTO_SENSOR (Default)");

  g_loraReady = initializeLoRa();
  Serial.printf("RA-02 SX1278: %s\n", g_loraReady ? "READY" : "FAILED");
  Serial.println("Waiting for ESP32-A sensor telemetry...");
  if (!g_loraReady) {
    Serial.println("Check RA-02 3.3V supply, antenna, SPI wiring and matching radio settings.");
  }
}

void loop() {
  processSerialCommands();

  if (g_loraReady) {
    const int packetSize = LoRa.parsePacket();
    if (packetSize > 0) handleTelemetryPacket();
  }

  const uint32_t now = millis();
  if (g_loraLedOffAtMs != 0 && (int32_t)(now - g_loraLedOffAtMs) >= 0) {
    if (g_operatingMode != MODE_MANUAL) {
      digitalWrite(LED_LORA, LOW);
    }
    g_loraLedOffAtMs = 0;
  }

  const bool nodeAAlive = g_lastNodeAMessageMs != 0 &&
    (uint32_t)(now - g_lastNodeAMessageMs) <= NODE_A_TIMEOUT_MS;

  if (g_operatingMode == MODE_AUTO_SENSOR) {
    digitalWrite(LED_HEARTBEAT, nodeAAlive ? HIGH : LOW);
    if (!nodeAAlive) {
      // Telemetry is stale: report unknown physical state by clearing activity LEDs.
      applySensorLeds(false, false, false);
    }
  }
}

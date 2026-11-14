#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <esp_system.h>

// ============================================================================
// PRW-WILD | ESP32-A | PRODUCTION SOFTWARE-HARDWARE TRANSMITTER
// Modes: HOST_CONTROL (Default / Master Digital Twin Link) & STANDALONE_BENCH_TEST
// ============================================================================

#define FW_VERSION "2.0.0-PROD"

// Verified RA-02 SPI Connections for ESP32 DevKit V1
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_CS    27
#define LORA_RST   14
#define LORA_DIO0  26

#define LORA_FREQUENCY 433920000L

// Communication Timings
const unsigned long ACK_TIMEOUT = 2200;
const unsigned long RETRY_DELAY = 500;
const unsigned long STANDALONE_EVENT_PAUSE = 1800;
const unsigned long STANDALONE_RETRY_CYCLE_PAUSE = 2500;

const uint8_t MAX_ATTEMPTS = 3;

// Operational Modes
enum OperatingMode {
  MODE_HOST_CONTROL,       // Master mode: Python simulation commands over USB Serial
  MODE_STANDALONE_DEMO     // Autonomous 6-step loop demonstration
};

OperatingMode currentMode = MODE_HOST_CONTROL;

// ============================================================================
// SESSION AND EVENT TRACKING
// ============================================================================

char sessionID[9];
uint32_t sequenceNumber = 0;
uint32_t currentSequence = 0;

// Host Command Buffer & Outstanding Transaction
struct ActiveTransaction {
  bool active;
  String rawPacket;
  String session;
  uint32_t sequence;
  String animalID;
  String layer;
  String transition;
  uint8_t attempts;
  unsigned long lastTxTime;
  unsigned long nextTxTime;
  bool waitingForACK;
};

ActiveTransaction currentTx = {false, "", "", 0, "", "", 0, 0, 0, false};

// Standalone Demonstration Sequence
struct WildlifeEvent {
  const char* layer;
  const char* transition;
};

const WildlifeEvent standaloneEvents[6] = {
  {"L1", "ENTER"},
  {"L2", "ENTER"},
  {"L3", "ENTER"},
  {"L3", "EXIT"},
  {"L2", "EXIT"},
  {"L1", "EXIT"}
};

int standaloneEventIndex = 0;
int completedCycles = 0;
unsigned long standaloneNextActionTime = 0;

// Serial Line Input Buffer
String serialLineBuffer = "";

// ============================================================================
// PROTOCOL HELPER: PACKET FIELD EXTRACTION
// ============================================================================

String getField(const String& packet, int index) {
  int start = 0;
  for (int i = 0; i < index; i++) {
    int separator = packet.indexOf('|', start);
    if (separator < 0) return "";
    start = separator + 1;
  }
  int end = packet.indexOf('|', start);
  if (end < 0) end = packet.length();
  return packet.substring(start, end);
}

// ============================================================================
// INITIALIZE RA-02 (SX1278)
// ============================================================================

bool initializeLoRa() {
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_FREQUENCY)) {
    return false;
  }

  LoRa.setTxPower(2, PA_OUTPUT_PA_BOOST_PIN);
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setPreambleLength(8);
  LoRa.setSyncWord(0x12);
  LoRa.enableCrc();
  LoRa.receive();

  return true;
}

// ============================================================================
// TRANSMISSION ENGINE
// ============================================================================

bool dispatchLoRaPacket(const String& packet) {
  if (LoRa.beginPacket() != 1) {
    LoRa.receive();
    return false;
  }
  LoRa.print(packet);
  int result = LoRa.endPacket();
  LoRa.receive();
  return (result == 1);
}

void transmitActiveTransaction() {
  if (!currentTx.active) return;

  currentTx.attempts++;
  bool ok = dispatchLoRaPacket(currentTx.rawPacket);

  if (ok) {
    currentTx.waitingForACK = true;
    currentTx.lastTxTime = millis();
    // In Host Control mode, report transmission dispatch to serial
    if (currentMode == MODE_HOST_CONTROL) {
      Serial.print("PW1|TX_SENT|");
      Serial.print(currentTx.session);
      Serial.print("|");
      Serial.print(currentTx.sequence);
      Serial.print("|ATTEMPT_");
      Serial.println(currentTx.attempts);
    }
  } else {
    currentTx.waitingForACK = false;
    currentTx.nextTxTime = millis() + RETRY_DELAY;
    if (currentMode == MODE_HOST_CONTROL) {
      Serial.println("PW1|RADIO_BUSY_RETRYING");
    }
  }
}

// ============================================================================
// ACKNOWLEDGEMENT PROCESSING
// ============================================================================

void processIncomingLoRaPackets() {
  int packetSize = LoRa.parsePacket();
  if (packetSize <= 0) return;

  String message = "";
  while (LoRa.available()) {
    message += (char)LoRa.read();
  }
  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();
  LoRa.receive();

  // Validate PW1 ACK header
  if (getField(message, 0) != "PW1" || getField(message, 1) != "ACK") {
    return;
  }

  String ackSession = getField(message, 2);
  uint32_t ackSeq = (uint32_t)getField(message, 3).toInt();
  String ackResult = getField(message, 4);
  String ackLayer = getField(message, 5);
  String ackState = getField(message, 6);

  // Check if matching current active transaction
  if (currentTx.active && currentTx.waitingForACK) {
    if (ackSession == currentTx.session && ackSeq == currentTx.sequence) {
      // SUCCESSFUL ACK MATCH
      currentTx.waitingForACK = false;
      currentTx.active = false;

      // Forward to Host Computer via USB Serial with RF diagnostics
      Serial.println(message);
      Serial.print("PW1|RF_DIAG|");
      Serial.print(ackSession);
      Serial.print("|");
      Serial.print(ackSeq);
      Serial.print("|RSSI_");
      Serial.print(rssi);
      Serial.print("|SNR_");
      Serial.println(snr);

      // If in standalone mode, schedule next event
      if (currentMode == MODE_STANDALONE_DEMO) {
        standaloneEventIndex++;
        if (standaloneEventIndex >= 6) {
          standaloneEventIndex = 0;
          completedCycles++;
        }
        standaloneNextActionTime = millis() + STANDALONE_EVENT_PAUSE;
      }
      return;
    }
  }

  // If outside active transaction or unhandled ACK
  Serial.print("PW1|UNMATCHED_ACK|");
  Serial.println(message);
}

// ============================================================================
// TIMEOUT AND RETRY MANAGEMENT
// ============================================================================

void checkTransactionTimeout() {
  if (!currentTx.active || !currentTx.waitingForACK) return;

  if (millis() - currentTx.lastTxTime >= ACK_TIMEOUT) {
    currentTx.waitingForACK = false;

    if (currentTx.attempts < MAX_ATTEMPTS) {
      // Schedule immediate retry
      currentTx.nextTxTime = millis() + RETRY_DELAY;
      if (currentMode == MODE_HOST_CONTROL) {
        Serial.print("PW1|RETRY|");
        Serial.print(currentTx.session);
        Serial.print("|");
        Serial.print(currentTx.sequence);
        Serial.print("|ATTEMPT_");
        Serial.println(currentTx.attempts + 1);
      }
    } else {
      // Maximum retries exhausted - report definitive failure to host
      currentTx.active = false;
      Serial.print("PW1|ACK|");
      Serial.print(currentTx.session);
      Serial.print("|");
      Serial.print(currentTx.sequence);
      Serial.print("|ERR_TIMEOUT|");
      Serial.print(currentTx.layer);
      Serial.println("|TIMEOUT");

      if (currentMode == MODE_STANDALONE_DEMO) {
        standaloneNextActionTime = millis() + STANDALONE_RETRY_CYCLE_PAUSE;
      }
    }
  }
}

// ============================================================================
// HOST COMMAND PARSER (USB SERIAL)
// ============================================================================

void processHostSerialCommand(const String& cmd) {
  if (cmd.length() == 0) return;

  // 1. Diagnostic / Ping Query
  if (cmd == "PW1|PING") {
    Serial.print("PW1|PONG|");
    Serial.print(currentMode == MODE_HOST_CONTROL ? "HOST_CONTROL" : "STANDALONE_DEMO");
    Serial.print("|");
    Serial.print(sessionID);
    Serial.print("|");
    Serial.println(FW_VERSION);
    return;
  }

  // 2. Mode Configuration
  if (cmd == "PW1|SET_MODE|HOST_CONTROL") {
    currentMode = MODE_HOST_CONTROL;
    currentTx.active = false;
    currentTx.waitingForACK = false;
    Serial.println("PW1|MODE_CONFIRMED|HOST_CONTROL");
    return;
  }

  if (cmd == "PW1|SET_MODE|STANDALONE") {
    currentMode = MODE_STANDALONE_DEMO;
    currentTx.active = false;
    currentTx.waitingForACK = false;
    standaloneNextActionTime = millis() + 1000;
    Serial.println("PW1|MODE_CONFIRMED|STANDALONE_DEMO");
    return;
  }

  // 3. Wildlife / Output Command Execution: PW1|CMD|<session>|<seq>|<animalID>|<layer>|<transition>
  if (cmd.startsWith("PW1|CMD|")) {
    // Automatically switch to HOST_CONTROL upon receiving simulation events
    if (currentMode != MODE_HOST_CONTROL) {
      currentMode = MODE_HOST_CONTROL;
      Serial.println("PW1|MODE_SWITCHED|HOST_CONTROL");
    }

    // Check if another transaction is currently blocking
    if (currentTx.active && currentTx.waitingForACK) {
      Serial.print("PW1|ERR_BUSY|");
      Serial.print(currentTx.session);
      Serial.print("|");
      Serial.println(currentTx.sequence);
      return;
    }

    String reqSession = getField(cmd, 2);
    String reqSeqStr = getField(cmd, 3);
    String reqAnimal = getField(cmd, 4);
    String reqLayer = getField(cmd, 5);
    String reqTrans = getField(cmd, 6);

    if (reqSession.length() == 0 || reqSeqStr.length() == 0 || reqLayer.length() == 0 || reqTrans.length() == 0) {
      Serial.println("PW1|ERR_BAD_SYNTAX");
      return;
    }

    // Load active transaction
    currentTx.active = true;
    currentTx.rawPacket = cmd;
    currentTx.session = reqSession;
    currentTx.sequence = (uint32_t)reqSeqStr.toInt();
    currentTx.animalID = reqAnimal;
    currentTx.layer = reqLayer;
    currentTx.transition = reqTrans;
    currentTx.attempts = 0;
    currentTx.waitingForACK = false;
    currentTx.nextTxTime = millis(); // Transmit immediately

    transmitActiveTransaction();
    return;
  }

  Serial.println("PW1|ERR_UNKNOWN_COMMAND");
}

void readHostSerial() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      serialLineBuffer.trim();
      if (serialLineBuffer.length() > 0) {
        processHostSerialCommand(serialLineBuffer);
      }
      serialLineBuffer = "";
    } else {
      if (serialLineBuffer.length() < 128) {
        serialLineBuffer += c;
      }
    }
  }
}

// ============================================================================
// STANDALONE DEMO GENERATOR
// ============================================================================

void runStandaloneDemoStep() {
  if (currentMode != MODE_STANDALONE_DEMO) return;
  if (currentTx.active) return;
  if ((int32_t)(millis() - standaloneNextActionTime) < 0) return;

  sequenceNumber++;
  currentSequence = sequenceNumber;

  String packet = "PW1|CMD|" +
                  String(sessionID) + "|" +
                  String(currentSequence) + "|ELEPHANT_01|" +
                  String(standaloneEvents[standaloneEventIndex].layer) + "|" +
                  String(standaloneEvents[standaloneEventIndex].transition);

  currentTx.active = true;
  currentTx.rawPacket = packet;
  currentTx.session = String(sessionID);
  currentTx.sequence = currentSequence;
  currentTx.animalID = "ELEPHANT_01";
  currentTx.layer = String(standaloneEvents[standaloneEventIndex].layer);
  currentTx.transition = String(standaloneEvents[standaloneEventIndex].transition);
  currentTx.attempts = 0;
  currentTx.waitingForACK = false;
  currentTx.nextTxTime = millis();

  transmitActiveTransaction();
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  snprintf(sessionID, sizeof(sessionID), "%08lX", (unsigned long)esp_random());

  Serial.println();
  Serial.println("==================================================");
  Serial.println("PRW-WILD DIGITAL TWIN — ESP32-A TRANSMITTER");
  Serial.print("FIRMWARE VERSION: ");
  Serial.println(FW_VERSION);
  Serial.print("INITIAL SESSION ID: ");
  Serial.println(sessionID);
  Serial.println("INITIALIZING RA-02 SX1278 (433.92 MHz)...");

  if (!initializeLoRa()) {
    Serial.println("ERROR: RA-02 INITIALIZATION FAILED — CHECK SPI WIRING");
    while (true) {
      delay(1000);
    }
  }

  Serial.println("RA-02 INITIALIZED SUCCESSFULLY (433.92 MHz, SF7, BW 125kHz, CRC)");
  Serial.println("DEFAULT MODE: HOST_CONTROL (USB SERIAL MASTER ACTIVE)");
  Serial.println("SYSTEM READY FOR DIGITAL TWIN SIMULATION EVENTS");
  Serial.println("==================================================");
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // 1. Process host USB commands
  readHostSerial();

  // 2. Check for incoming LoRa acknowledgements
  processIncomingLoRaPackets();

  // 3. Monitor timeouts and retry active transactions if pending
  checkTransactionTimeout();

  if (currentTx.active && !currentTx.waitingForACK && (int32_t)(millis() - currentTx.nextTxTime) >= 0) {
    transmitActiveTransaction();
  }

  // 4. If in standalone mode, trigger sequence steps
  runStandaloneDemoStep();
}


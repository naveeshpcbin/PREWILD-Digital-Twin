#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <esp_system.h>

// ==========================================
// PRW-WILD | ESP32-A | EVENT TRANSMITTER
// Compatible with your existing ESP32-B code
// ==========================================

// RA-02 pin connections
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_CS    27
#define LORA_RST   14
#define LORA_DIO0  26

#define LORA_FREQUENCY 433920000L

// Communication timings
const unsigned long ACK_TIMEOUT = 2200;
const unsigned long RETRY_DELAY = 500;
const unsigned long EVENT_PAUSE = 1800;
const unsigned long RETRY_CYCLE_PAUSE = 2500;

const uint8_t MAX_ATTEMPTS = 3;

// Animal identification
const char* ANIMAL_ID = "ELEPHANT_01";

// ==========================================
// SIX-STAGE DETECTION SEQUENCE
// ==========================================

struct WildlifeEvent {
  const char* layer;
  const char* transition;
};

WildlifeEvent events[6] = {
  {"L1", "ENTER"},
  {"L2", "ENTER"},
  {"L3", "ENTER"},
  {"L3", "EXIT"},
  {"L2", "EXIT"},
  {"L1", "EXIT"}
};

// ==========================================
// SESSION AND EVENT TRACKING
// ==========================================

char sessionID[9];

uint32_t sequenceNumber = 0;
uint32_t currentSequence = 0;

int eventIndex = 0;
int completedCycles = 0;

uint8_t attemptCount = 0;

bool eventStarted = false;
bool waitingForACK = false;

unsigned long lastTransmitTime = 0;
unsigned long nextActionTime = 0;

// ==========================================
// PACKET FIELD EXTRACTION
// ==========================================

String getField(const String& packet, int index) {

  int start = 0;

  for (int i = 0; i < index; i++) {

    int separator = packet.indexOf('|', start);

    if (separator < 0) {
      return "";
    }

    start = separator + 1;
  }

  int end = packet.indexOf('|', start);

  if (end < 0) {
    end = packet.length();
  }

  return packet.substring(start, end);
}

// ==========================================
// INITIALIZE RA-02
// ==========================================

bool initializeLoRa() {

  SPI.begin(
    LORA_SCK,
    LORA_MISO,
    LORA_MOSI,
    LORA_CS
  );

  LoRa.setPins(
    LORA_CS,
    LORA_RST,
    LORA_DIO0
  );

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

// ==========================================
// BUILD EVENT PACKET
// ==========================================

String buildEventPacket() {

  return
    "PW1|CMD|" +
    String(sessionID) + "|" +
    String(currentSequence) + "|" +
    String(ANIMAL_ID) + "|" +
    String(events[eventIndex].layer) + "|" +
    String(events[eventIndex].transition);
}

// ==========================================
// TRANSMIT EVENT
// ==========================================

void transmitEvent() {

  String packet = buildEventPacket();

  Serial.println();
  Serial.println("====================================");
  Serial.println("PRW-WILD ANIMAL MOVEMENT EVENT");

  Serial.print("ANIMAL ID: ");
  Serial.println(ANIMAL_ID);

  Serial.print("LAYER: ");
  Serial.println(events[eventIndex].layer);

  Serial.print("TRANSITION: ");
  Serial.println(events[eventIndex].transition);

  Serial.print("SEQUENCE: ");
  Serial.println(currentSequence);

  Serial.print("TRANSMISSION ATTEMPT: ");
  Serial.println(attemptCount + 1);

  Serial.print("PACKET: ");
  Serial.println(packet);

  // Check radio availability

  if (LoRa.beginPacket() != 1) {

    Serial.println("RADIO BUSY");

    LoRa.receive();

    nextActionTime = millis() + RETRY_DELAY;

    Serial.println("====================================");

    return;
  }

  LoRa.print(packet);

  int result = LoRa.endPacket();

  LoRa.receive();

  if (result == 1) {

    waitingForACK = true;
    lastTransmitTime = millis();

    attemptCount++;

    Serial.println("EVENT TRANSMITTED SUCCESSFULLY");
    Serial.println("WAITING FOR ESP32-B ACKNOWLEDGEMENT");

  } else {

    waitingForACK = false;

    attemptCount++;

    Serial.println("TRANSMISSION ERROR");

    nextActionTime = millis() + RETRY_DELAY;
  }

  Serial.println("====================================");
}

// ==========================================
// CHECK ESP32-B ACKNOWLEDGEMENT
// ==========================================

void receiveAcknowledgement() {

  int packetSize = LoRa.parsePacket();

  if (packetSize <= 0) {
    return;
  }

  String message = "";

  while (LoRa.available()) {
    message += (char)LoRa.read();
  }

  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();

  LoRa.receive();

  // Validate ACK packet header

  if (
    getField(message, 0) != "PW1" ||
    getField(message, 1) != "ACK"
  ) {
    return;
  }

  String receivedSession = getField(message, 2);
  String receivedSequenceText = getField(message, 3);
  String result = getField(message, 4);
  String receivedLayer = getField(message, 5);
  String receivedState = getField(message, 6);

  if (
    receivedSession != String(sessionID) ||
    receivedSequenceText.toInt() != currentSequence ||
    result != "OK"
  ) {
    Serial.println("UNMATCHED ACKNOWLEDGEMENT");
    return;
  }

  if (!waitingForACK) {
    Serial.println("ACK RECEIVED OUTSIDE WAIT STATE");
    return;
  }

  String expectedState =
    String(events[eventIndex].transition) == "ENTER"
      ? "ACTIVE"
      : "INACTIVE";

  if (
    receivedLayer != String(events[eventIndex].layer) ||
    receivedState != expectedState
  ) {
    Serial.println("ACK STATE DOES NOT MATCH EVENT");
    return;
  }

  // Valid acknowledgement received

  waitingForACK = false;
  eventStarted = false;

  Serial.println();
  Serial.println("************************************");
  Serial.println("EVENT ACKNOWLEDGED SUCCESSFULLY");

  Serial.print("ACKNOWLEDGEMENT: ");
  Serial.println(message);

  Serial.print("ACK RSSI: ");
  Serial.print(rssi);
  Serial.println(" dBm");

  Serial.print("ACK SNR: ");
  Serial.print(snr);
  Serial.println(" dB");

  Serial.println("************************************");

  // Advance to next event

  eventIndex++;

  if (eventIndex >= 6) {

    eventIndex = 0;

    completedCycles++;

    Serial.println();
    Serial.println("====================================");
    Serial.println("COMPLETE DETECTION CYCLE FINISHED");

    Serial.print("COMPLETED CYCLES: ");
    Serial.println(completedCycles);

    Serial.println("PREPARING NEXT ANIMAL CYCLE");
    Serial.println("====================================");
  }

  attemptCount = 0;

  nextActionTime = millis() + EVENT_PAUSE;
}

// ==========================================
// HANDLE ACKNOWLEDGEMENT TIMEOUT
// ==========================================

void handleTimeout() {

  if (
    !waitingForACK ||
    millis() - lastTransmitTime < ACK_TIMEOUT
  ) {
    return;
  }

  waitingForACK = false;

  Serial.println();
  Serial.println("ACKNOWLEDGEMENT TIMEOUT");

  if (attemptCount < MAX_ATTEMPTS) {

    Serial.println("RETRANSMITTING SAME EVENT");

    nextActionTime = millis() + RETRY_DELAY;

  } else {

    Serial.println("RETRY LIMIT REACHED");
    Serial.println("KEEPING CURRENT EVENT");
    Serial.println("RETRYING AFTER A SHORT PAUSE");

    attemptCount = 0;

    nextActionTime = millis() + RETRY_CYCLE_PAUSE;
  }
}

// ==========================================
// SETUP
// ==========================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("====================================");
  Serial.println("       PRW-WILD DIGITAL TWIN");
  Serial.println("       ESP32-A EVENT TRANSMITTER");
  Serial.println("====================================");

  // Generate session ID for this boot

  snprintf(
    sessionID,
    sizeof(sessionID),
    "%08lX",
    (unsigned long)esp_random()
  );

  Serial.print("SESSION ID: ");
  Serial.println(sessionID);

  Serial.println("INITIALIZING RA-02...");

  if (!initializeLoRa()) {

    Serial.println("RA-02 INITIALIZATION FAILED");

    while (true) {
      delay(1000);
    }
  }

  Serial.println("RA-02 INITIALIZED SUCCESSFULLY");
  Serial.println("FREQUENCY: 433.92 MHz");

  Serial.println("EVENT TRANSMISSION READY");
  Serial.println("ACKNOWLEDGEMENT SYSTEM READY");

  Serial.println("STARTING WILDLIFE DEMONSTRATION");

  nextActionTime = millis() + 2000;
}

// ==========================================
// MAIN LOOP — CONTINUOUS OPERATION
// ==========================================

void loop() {

  receiveAcknowledgement();

  handleTimeout();

  if (
    !eventStarted &&
    !waitingForACK &&
    (int32_t)(millis() - nextActionTime) >= 0
  ) {

    sequenceNumber++;
    currentSequence = sequenceNumber;

    eventStarted = true;
    attemptCount = 0;
  }

  if (
    eventStarted &&
    !waitingForACK &&
    (int32_t)(millis() - nextActionTime) >= 0
  ) {

    transmitEvent();
  }
}
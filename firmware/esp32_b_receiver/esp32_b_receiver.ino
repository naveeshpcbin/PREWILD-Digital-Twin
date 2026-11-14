#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>

// ============================================================================
// PRW-WILD | ESP32-B | SIX-LED HARDWARE RECEIVER & PERIPHERAL CONTROLLER
// Target: ESP32 DevKit V1 (ESP32-WROOM-32) + Ai-Thinker RA-02 (SX1278 433MHz)
// ============================================================================

#define FW_VERSION "2.0.0-PROD"

// Verified RA-02 SPI Connections
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_CS    27
#define LORA_RST   14
#define LORA_DIO0  26

#define LORA_FREQUENCY 433920000L

// Six Discrete Green LED Outputs (with 2k ohm ballast resistors)
// Layer 1: Wi-Fi CSI / RF Outer Perimeter (80m - 120m)
#define LED_L1_ACTIVE  15
#define LED_L1_EVENT    2

// Layer 2: Seismic Geophone & PIR Middle Boundary (30m - 80m)
#define LED_L2_ACTIVE   4
#define LED_L2_EVENT   16

// Layer 3: Optical PTZ Camera & Deterrent Inner Fence Line (< 30m)
#define LED_L3_ACTIVE  17
#define LED_L3_EVENT   13

// Sensors
#define PIN_PIR        32
#define PIN_PIEZO      35
#define PIN_I2S_BCLK   25
#define PIN_I2S_WS     33
#define PIN_I2S_SD     34

// Non-blocking Event LED Pulse Duration (ms)
const unsigned long EVENT_PULSE_DURATION = 350;

// LED State Tracking
bool l1Active = false;
bool l2Active = false;
bool l3Active = false;

unsigned long l1EventTimer = 0;
unsigned long l2EventTimer = 0;
unsigned long l3EventTimer = 0;

// Idempotency: Track last processed transaction to prevent duplicate actuation
String lastProcessedSession = "";
uint32_t lastProcessedSequence = 0;

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
// INITIALIZE RA-02
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
// INITIALIZE GPIO OUTPUTS & SENSORS
// ============================================================================

void initializeGPIO() {
  pinMode(LED_L1_ACTIVE, OUTPUT);
  pinMode(LED_L1_EVENT, OUTPUT);
  pinMode(LED_L2_ACTIVE, OUTPUT);
  pinMode(LED_L2_EVENT, OUTPUT);
  pinMode(LED_L3_ACTIVE, OUTPUT);
  pinMode(LED_L3_EVENT, OUTPUT);

  // Initial Safe State: All LEDs de-energized
  digitalWrite(LED_L1_ACTIVE, LOW);
  digitalWrite(LED_L1_EVENT, LOW);
  digitalWrite(LED_L2_ACTIVE, LOW);
  digitalWrite(LED_L2_EVENT, LOW);
  digitalWrite(LED_L3_ACTIVE, LOW);
  digitalWrite(LED_L3_EVENT, LOW);

  // Configure Sensors
  pinMode(PIN_PIR, INPUT);
  pinMode(PIN_PIEZO, INPUT);
  pinMode(PIN_I2S_SD, INPUT);
}

// ============================================================================
// APPLY HARDWARE OUTPUT STATE
// ============================================================================

void applyLayerOutputs() {
  digitalWrite(LED_L1_ACTIVE, l1Active ? HIGH : LOW);
  digitalWrite(LED_L2_ACTIVE, l2Active ? HIGH : LOW);
  digitalWrite(LED_L3_ACTIVE, l3Active ? HIGH : LOW);

  unsigned long now = millis();

  // Non-blocking pulse expiration for Event LEDs
  if (l1EventTimer > 0 && now >= l1EventTimer) {
    digitalWrite(LED_L1_EVENT, LOW);
    l1EventTimer = 0;
  }

  if (l2EventTimer > 0 && now >= l2EventTimer) {
    digitalWrite(LED_L2_EVENT, LOW);
    l2EventTimer = 0;
  }

  if (l3EventTimer > 0 && now >= l3EventTimer) {
    digitalWrite(LED_L3_EVENT, LOW);
    l3EventTimer = 0;
  }
}

void triggerEventPulse(int pin, unsigned long& timer) {
  digitalWrite(pin, HIGH);
  timer = millis() + EVENT_PULSE_DURATION;
}

void emergencyAllOff() {
  l1Active = false;
  l2Active = false;
  l3Active = false;
  l1EventTimer = 0;
  l2EventTimer = 0;
  l3EventTimer = 0;
  digitalWrite(LED_L1_ACTIVE, LOW);
  digitalWrite(LED_L1_EVENT, LOW);
  digitalWrite(LED_L2_ACTIVE, LOW);
  digitalWrite(LED_L2_EVENT, LOW);
  digitalWrite(LED_L3_ACTIVE, LOW);
  digitalWrite(LED_L3_EVENT, LOW);
}

// ============================================================================
// DISPATCH ACKNOWLEDGEMENT OVER LORA
// ============================================================================

void sendAcknowledgement(const String& session, uint32_t seq, const String& status, const String& layer, const String& state) {
  String ackPacket = "PW1|ACK|" + session + "|" + String(seq) + "|" + status + "|" + layer + "|" + state;

  LoRa.beginPacket();
  LoRa.print(ackPacket);
  LoRa.endPacket();
  LoRa.receive();

  Serial.print("TRANSMITTED ACK: ");
  Serial.println(ackPacket);
}

// ============================================================================
// PROCESS RECEIVED PACKETS
// ============================================================================

void processLoRaPacket() {
  int packetSize = LoRa.parsePacket();
  if (packetSize <= 0) return;

  String packet = "";
  while (LoRa.available()) {
    packet += (char)LoRa.read();
  }
  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();
  LoRa.receive();

  Serial.println();
  Serial.println("==================================================");
  Serial.print("RECEIVED LORA PACKET: ");
  Serial.println(packet);
  Serial.print("RSSI: "); Serial.print(rssi); Serial.print(" dBm | SNR: "); Serial.print(snr); Serial.println(" dB");

  // Validate PW1 CMD header
  if (getField(packet, 0) != "PW1" || getField(packet, 1) != "CMD") {
    Serial.println("IGNORED NON-PW1/NON-CMD PACKET");
    return;
  }

  String session = getField(packet, 2);
  uint32_t seq = (uint32_t)getField(packet, 3).toInt();
  String animalID = getField(packet, 4);
  String layer = getField(packet, 5);
  String transition = getField(packet, 6);

  // 1. Idempotency Check: Duplicate command detection
  bool isDuplicate = (session == lastProcessedSession && seq == lastProcessedSequence);
  if (isDuplicate) {
    Serial.println("NOTICE: DUPLICATE PACKET RECEIVED — RESENDING ACK WITHOUT RETRIGGERING EVENT LED");
    String state = "INACTIVE";
    if (layer == "L1" && l1Active) state = "ACTIVE";
    else if (layer == "L2" && l2Active) state = "ACTIVE";
    else if (layer == "L3" && l3Active) state = "ACTIVE";
    else if (layer == "ALL") state = "ALL_OFF";
    sendAcknowledgement(session, seq, "OK", layer, state);
    return;
  }

  // Record transaction key
  lastProcessedSession = session;
  lastProcessedSequence = seq;

  // 2. Emergency All-Off / System Commands
  if (layer == "ALL" && transition == "OFF") {
    Serial.println("ACTION: EMERGENCY ALL-OFF EXECUTED");
    emergencyAllOff();
    sendAcknowledgement(session, seq, "OK", "ALL", "ALL_OFF");
    return;
  }

  // 3. Layer Transitions
  String ackState = "INACTIVE";

  if (layer == "L1") {
    if (transition == "ENTER" || transition == "ON") {
      l1Active = true;
      triggerEventPulse(LED_L1_EVENT, l1EventTimer);
      ackState = "ACTIVE";
      Serial.println("STATE CHANGE: LAYER 1 ARMED (ACTIVE=ON, EVENT_PULSE)");
    } else if (transition == "EXIT" || transition == "OFF") {
      l1Active = false;
      triggerEventPulse(LED_L1_EVENT, l1EventTimer);
      ackState = "INACTIVE";
      Serial.println("STATE CHANGE: LAYER 1 CLEARED (ACTIVE=OFF, DEPARTURE_PULSE)");
    }
  } else if (layer == "L2") {
    if (transition == "ENTER" || transition == "ON") {
      l2Active = true;
      triggerEventPulse(LED_L2_EVENT, l2EventTimer);
      ackState = "ACTIVE";
      Serial.println("STATE CHANGE: LAYER 2 ARMED (ACTIVE=ON, EVENT_PULSE)");
    } else if (transition == "EXIT" || transition == "OFF") {
      l2Active = false;
      triggerEventPulse(LED_L2_EVENT, l2EventTimer);
      ackState = "INACTIVE";
      Serial.println("STATE CHANGE: LAYER 2 CLEARED (ACTIVE=OFF, DEPARTURE_PULSE)");
    }
  } else if (layer == "L3") {
    if (transition == "ENTER" || transition == "ON" || transition == "STROBE") {
      l3Active = true;
      triggerEventPulse(LED_L3_EVENT, l3EventTimer);
      ackState = "ACTIVE";
      Serial.println("STATE CHANGE: LAYER 3 ARMED (ACTIVE=ON, EVENT_PULSE)");
    } else if (transition == "EXIT" || transition == "OFF") {
      l3Active = false;
      triggerEventPulse(LED_L3_EVENT, l3EventTimer);
      ackState = "INACTIVE";
      Serial.println("STATE CHANGE: LAYER 3 CLEARED (ACTIVE=OFF, DEPARTURE_PULSE)");
    }
  } else {
    Serial.println("ERROR: UNRECOGNIZED LAYER IDENTIFIER");
    sendAcknowledgement(session, seq, "ERR_INVALID_LAYER", layer, "UNKNOWN");
    return;
  }

  // Update physical outputs immediately
  applyLayerOutputs();

  // Return confirmed hardware acknowledgement
  sendAcknowledgement(session, seq, "OK", layer, ackState);
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  initializeGPIO();

  Serial.println();
  Serial.println("==================================================");
  Serial.println("PRW-WILD DIGITAL TWIN");
  Serial.println("ESP32-B HARDWARE RECEIVER");
  Serial.print("FIRMWARE VERSION: ");
  Serial.println(FW_VERSION);
  Serial.println("==================================================");
  Serial.println("INITIALIZING RA-02...");

  if (!initializeLoRa()) {
    Serial.println("ERROR: RA-02 INITIALIZATION FAILED");
    while (true) {
      delay(1000);
    }
  }

  Serial.println("RA-02 INITIALIZED SUCCESSFULLY");
  Serial.println("FREQUENCY: 433.92 MHz");
  Serial.println("SIX LED CONTROLLERS READY");
  Serial.println("ACKNOWLEDGEMENT SYSTEM READY");
  Serial.println("WAITING FOR WILDLIFE EVENTS FROM ESP32-A");
  Serial.println("==================================================");
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // 1. Check for incoming LoRa commands from ESP32-A
  processLoRaPacket();

  // 2. Maintain non-blocking LED state updates and timer expirations
  applyLayerOutputs();
}


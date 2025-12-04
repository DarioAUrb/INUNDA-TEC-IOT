#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "iPhone de Darío";      
const char* password = "123456789";      

// Server Configuration
const char* serverURL = "http://172.20.10.6:8000/sensors";

// DHT11 Sensor
#define DHT_PIN 4
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// AJ-SR04M Ultrasonic Sensor
#define ULTRASONIC_TRIG_PIN 23
#define ULTRASONIC_ECHO_PIN 22

#define BOX_HEIGHT 40.0

unsigned long lastSendTime = 0;
const long sendInterval = 10000;

void setup() {
  Serial.begin(115200);
  delay(2000);

  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

  dht.begin();
  delay(1000);

  Serial.println("\n\nInitializing ESP32...");
  connectToWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    connectToWiFi();
  }

  if (millis() - lastSendTime >= sendInterval) {
    lastSendTime = millis();
    readSensorsAndSend();
  }

  delay(100);
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nError connecting to WiFi");
  }
}

// Read distance with AJ-SR04M (LOW pulse)
float readDistance() {
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(5);

  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

long pulseDuration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000);

  if (pulseDuration == 0) return -1;

  float distance = pulseDuration * 0.0343 / 2;
  return distance;
}

void readSensorsAndSend() {
  Serial.println("\n### READING SENSORS ####");

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error reading DHT11");
    return;
  }

  Serial.print("Temperature: ");
  Serial.println(temperature);

  Serial.print("Humidity: ");
  Serial.println(humidity);

  float distance = readDistance();
  Serial.print("Distance raw: ");
  Serial.println(distance);

  if (distance < 0) {
    Serial.println("Error: Unable to read distance");
    return;
  }
  float waterHeight = BOX_HEIGHT - distance;
  waterHeight = constrain(waterHeight, 0, BOX_HEIGHT);

  Serial.print("Water level (cm): ");
  Serial.println(waterHeight);

  Serial.println("#########################");

  sendData(waterHeight, temperature, humidity);
}

void sendData(float waterLevel, float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, cannot send data");
    return;
  }

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["water_level_cm"] = waterLevel;
  doc["temperature_c"] = temperature;
  doc["humidity_percentage"] = humidity;

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.print("Sending JSON: ");
  Serial.println(jsonString);

  int httpResponseCode = http.POST(jsonString);

  Serial.print("HTTP Response Code: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.print("Server Response: ");
    Serial.println(response);
  }

  http.end();
}

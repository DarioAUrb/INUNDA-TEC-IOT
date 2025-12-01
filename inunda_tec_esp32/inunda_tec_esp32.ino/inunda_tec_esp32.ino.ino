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
#define DHT_PIN 4        // Connected to GPIO4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

// AJ-SR04M Ultrasonic Sensor
#define ULTRASONIC_TRIG_PIN 23     // Connected to GPIO23 for TRIG
#define ULTRASONIC_ECHO_PIN 22     // Connected to GPIO22 for ECHO

// Box Configuration
#define BOX_HEIGHT 12.0  // Total box height in cm


unsigned long lastSendTime = 0;
const long sendInterval = 10000;  // Send every 10 seconds

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
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    connectToWiFi();
  }

  // Send data every sendInterval
  if (millis() - lastSendTime >= sendInterval) {
    lastSendTime = millis();
    readSensorsAndSend();
  }

  delay(100);
}

// WiFi Connection Function
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


// Read Ultrasonic Distance
float readDistance() {
  float distanceReadings[5];
  int validReadings = 0;
  
  for (int i = 0; i < 5; i++) {
    digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
    delayMicroseconds(5);
    digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

    long pulseDuration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000);
    
    if (pulseDuration > 0 && pulseDuration < 23200) {
      float distance = pulseDuration * 0.0343 / 2;
      
      // Validate that it's between 0 and 12 cm (box height)
      if (distance >= 0 && distance <= BOX_HEIGHT) {
        distanceReadings[validReadings] = distance;
        validReadings++;
      }
    }
    
    delay(100); 
  }
  
  if (validReadings == 0) {
    return -1;  // Return -1 to indicate error
  } else {
    float averageDistance = 0;
    for (int i = 0; i < validReadings; i++) {
      averageDistance += distanceReadings[i];
    }
    return averageDistance / validReadings;
  }
}


// Read Sensors and Send Data
void readSensorsAndSend() {
  Serial.println("\n### READING SENSORS ####");

  // DHT11 Reading
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error reading DHT11");
    return;
  }

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  // Ultrasonic Sensor Reading (distance to the bottom of the box)
  float distance = readDistance();

  // Calculate water height
  float waterHeight = 0;
  if (distance > 0) {
    waterHeight = BOX_HEIGHT - distance;
    waterHeight = constrain(waterHeight, 0, BOX_HEIGHT);
  } else {
    Serial.println("Error: Unable to read distance from sensor");
    return;
  }

  Serial.print("Distance to bottom (cm): ");
  Serial.print(distance);
  Serial.println(" cm");

  Serial.print("Water height: ");
  Serial.print(waterHeight);
  Serial.println(" cm");

  Serial.println("#########################");

  // Send to server (now with water height, not distance)
  sendData(waterHeight, temperature, humidity);
}


// Send Data to Server
void sendData(float waterLevel, float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, cannot send data");
    return;
  }

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  // Create JSON with data
  StaticJsonDocument<200> doc;
  doc["water_level_cm"] = waterLevel;
  doc["temperature_c"] = temperature;
  doc["humidity_percentage"] = humidity;

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.print("Sending JSON: ");
  Serial.println(jsonString);

  // Send POST
  int httpResponseCode = http.POST(jsonString);

  Serial.print("HTTP Response Code: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.print("Server Response: ");
    Serial.println(response);
  } else {
    Serial.print("HTTP Error. Code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}
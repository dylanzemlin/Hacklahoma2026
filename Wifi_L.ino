#include <WiFi.h>
#include <WiFiClient.h>

const char* ssid = "ESP32_Chat_Slave";
const char* password = "12345678";

const char* serverIP = "192.168.4.1";
const uint16_t serverPort = 8080;

WiFiClient client;

String incomingMessage = "";

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 MASTER (Client) ===");
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Slave");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to Slave AP!");
  Serial.print("Master IP: ");
  Serial.println(WiFi.localIP());
  
  Serial.println("Connecting to server...");
  if (client.connect(serverIP, serverPort)) {
    Serial.println("Connected to server!");
    Serial.println("\nType a message and press Enter to send to Slave");
  } else {
    Serial.println("Connection to server failed!");
  }
}

void loop() {
  if (client.connected()) {
    
    // Check for incoming data from Slave
    while (client.available()) {
      char c = client.read();
      if (c == '\n') {
        if (incomingMessage.length() > 0) {
          Serial.print("Slave: ");
          Serial.println(incomingMessage);
          incomingMessage = "";
        }
      } else if (c != '\r') {
        incomingMessage += c;
      }
    }
    
    // Check for outgoing data from Serial
    if (Serial.available()) {
      String message = Serial.readStringUntil('\n');
      message.trim();
      
      if (message.length() > 0) {
        client.println(message);
        Serial.print("You: ");
        Serial.println(message);
      }
    }
    
  } else {
    Serial.println("Disconnected from server. Reconnecting...");
    if (client.connect(serverIP, serverPort)) {
      Serial.println("Reconnected!");
    } else {
      delay(1000);
    }
  }
  
  delay(10);
}
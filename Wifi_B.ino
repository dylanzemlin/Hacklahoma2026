#include <WiFi.h>
#include <WiFiClient.h>

const char* ssid = "ESP32_Chat_Slave";
const char* password = "12345678";

WiFiServer server(8080);
WiFiClient client;

String incomingMessage = "";

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 SLAVE (Server) ===");
  
  WiFi.softAP(ssid, password);
  
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
  
  server.begin();
  Serial.println("Server started on port 8080");
  Serial.println("Waiting for Master to connect...");
  Serial.println("\nType a message and press Enter to send to Master");
}

void loop() {
  if (!client || !client.connected()) {
    client = server.available();
    if (client) {
      Serial.println("\n>>> Master connected!");
    }
  }
  
  if (client && client.connected()) {
    
    // Check for incoming data from Master
    while (client.available()) {
      char c = client.read();
      if (c == '\n') {
        if (incomingMessage.length() > 0) {
          Serial.print("Master: ");
          Serial.println(incomingMessage);
          incomingMessage = "";
        }
      } else if (c != '\r') {
        incomingMessage += c;
NEW SKETCH

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
  }
  
  delay(10);
}
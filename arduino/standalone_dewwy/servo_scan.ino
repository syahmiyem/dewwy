/*
 * Servo Scanning Module for Dewwy Robot
 * This file contains functions for controlling the servo-mounted ultrasonic sensor
 * to create a radar-like scanning system for improved navigation.
 */

#include <Servo.h>

// Servo control
Servo scanServo;
#define SERVO_PIN 9

// Scanning parameters
#define SCAN_MIN_ANGLE 0
#define SCAN_MAX_ANGLE 180
#define SCAN_STEP 15
#define SCAN_DELAY 50

// Array to store scan results
#define SCAN_ARRAY_SIZE ((SCAN_MAX_ANGLE - SCAN_MIN_ANGLE) / SCAN_STEP + 1)
int scanDistances[SCAN_ARRAY_SIZE];
int scanAngles[SCAN_ARRAY_SIZE];
int currentScanIndex = 0;
boolean isScanning = false;
boolean autoScanEnabled = true;
unsigned long lastScanTime = 0;
const unsigned long AUTO_SCAN_INTERVAL = 5000; // Auto scan every 5 seconds

// Initialize the servo and scanning system
void setupServo() {
  scanServo.attach(SERVO_PIN);
  scanServo.write(90); // Center position
  delay(300); // Give servo time to reach position
  
  // Initialize scan arrays
  for (int i = 0; i < SCAN_ARRAY_SIZE; i++) {
    scanAngles[i] = SCAN_MIN_ANGLE + (i * SCAN_STEP);
    scanDistances[i] = 0;
  }
}

// Perform a full area scan
void performScan() {
  Serial.println("Starting area scan...");
  isScanning = true;
  
  // First move to starting position
  scanServo.write(SCAN_MIN_ANGLE);
  delay(300); // Give servo time to reach position
  
  // Scan from left to right
  for (int i = 0; i < SCAN_ARRAY_SIZE; i++) {
    // Move servo to each angle
    scanServo.write(scanAngles[i]);
    delay(SCAN_DELAY); // Wait for servo to reach position
    
    // Measure distance at this angle
    scanDistances[i] = measureDistance();
    
    // Print scan data
    Serial.print("Angle: ");
    Serial.print(scanAngles[i]);
    Serial.print("°, Distance: ");
    Serial.print(scanDistances[i]);
    Serial.println(" cm");
  }
  
  // Return to center position
  scanServo.write(90);
  
  // Find the clearest direction
  int bestAngle = findClearestPath();
  Serial.print("Clearest path at angle: ");
  Serial.print(bestAngle);
  Serial.println("°");
  
  isScanning = false;
  lastScanTime = millis();
}

// Find the clearest path based on scan results
int findClearestPath() {
  int bestAngle = 90; // Default to straight ahead
  int maxDistance = 0;
  
  // Simple algorithm: find the angle with maximum distance
  for (int i = 0; i < SCAN_ARRAY_SIZE; i++) {
    if (scanDistances[i] > maxDistance) {
      maxDistance = scanDistances[i];
      bestAngle = scanAngles[i];
    }
  }
  
  // Apply weighted preference for forward direction
  for (int i = 0; i < SCAN_ARRAY_SIZE; i++) {
    // If this reading is at least 80% of the max and closer to center
    if (scanDistances[i] > maxDistance * 0.8) {
      // The closer to 90 degrees, the more we prefer this angle
      int centerDistance = abs(scanAngles[i] - 90);
      int bestDistance = abs(bestAngle - 90);
      
      // If this angle is significantly closer to center, choose it
      if (centerDistance < bestDistance * 0.7) {
        bestAngle = scanAngles[i];
        maxDistance = scanDistances[i];
      }
    }
  }
  
  return bestAngle;
}

// Point the sensor in a specific direction and get reading
int getDistanceAt(int angle) {
  scanServo.write(angle);
  delay(SCAN_DELAY);
  return measureDistance();
}

// Update scan data and control auto-scanning
void updateScanner() {
  // Don't do anything if we're currently in a full scan
  if (isScanning) return;
  
  // Check if it's time for an auto-scan
  if (autoScanEnabled && millis() - lastScanTime > AUTO_SCAN_INTERVAL) {
    // Only scan if we're in ROAMING or AVOIDING state
    if (currentState == ROAMING || currentState == AVOIDING) {
      performScan();
    }
  }
}

// Turn toward the clearest path
void turnTowardClearestPath() {
  int bestAngle = findClearestPath();
  
  // Only perform the turn if we have valid scan data
  if (bestAngle < 0) return;
  
  // Convert the angle to a relative direction
  // (90° is straight ahead in servo coordinates)
  int relativeAngle = bestAngle - 90;
  
  // If the clearest path is significantly to the left
  if (relativeAngle < -20) {
    turnLeft(180);
    delay(abs(relativeAngle) * 5); // Rough approximation of turn time
    stopMotors();
  }
  // If the clearest path is significantly to the right
  else if (relativeAngle > 20) {
    turnRight(180);
    delay(abs(relativeAngle) * 5); // Rough approximation of turn time
    stopMotors();
  }
  
  // Return sensor to forward position
  scanServo.write(90);
}

// Process additional serial commands for the scanner
void processServoScanCommands(String command) {
  if (command == "SCAN") {
    performScan();
  } 
  else if (command == "SCAN_ON") {
    autoScanEnabled = true;
    Serial.println("Auto-scanning enabled");
  } 
  else if (command == "SCAN_OFF") {
    autoScanEnabled = false;
    Serial.println("Auto-scanning disabled");
  }
}

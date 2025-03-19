/**
 * Main Arduino sketch for Dewwy Pet Robot
 * This handles hardware communication between Raspberry Pi and physical components
 */

#include <Wire.h>
#include <Servo.h>

// Pin Definitions - Using Sensor Shield V5 mapping
// Motor control pins
#define LEFT_MOTOR_PWM 5
#define LEFT_MOTOR_DIR1 4
#define LEFT_MOTOR_DIR2 3
#define RIGHT_MOTOR_PWM 6
#define RIGHT_MOTOR_DIR1 7
#define RIGHT_MOTOR_DIR2 8

// Sensor pins
#define TRIG_PIN 12  // Ultrasonic trigger pin
#define ECHO_PIN 11  // Ultrasonic echo pin
#define SERVO_PIN 9  // Servo control pin

// Optional pins
#define BATTERY_PIN A3  // Battery monitoring

// Serial communication
#define BAUD_RATE 115200
#define TX_INTERVAL 50  // Minimum time between transmissions (ms)

// Constants
#define MAX_COMMAND_LENGTH 32
#define SCAN_MIN_ANGLE 0
#define SCAN_MAX_ANGLE 180
#define SCAN_STEP 15
#define SCAN_DELAY 50

// Global variables
unsigned long lastTxTime = 0;
unsigned long lastDistance = 0;
char command[MAX_COMMAND_LENGTH];
int commandIndex = 0;
int distance = 0;
int currentServoAngle = 90;  // Default to center position
boolean isScanning = false;

// Objects
Servo scanServo;

// Setup function
void setup() {
  // Initialize Serial
  Serial.begin(BAUD_RATE);
  
  // Initialize motor pins
  pinMode(LEFT_MOTOR_PWM, OUTPUT);
  pinMode(LEFT_MOTOR_DIR1, OUTPUT);
  pinMode(LEFT_MOTOR_DIR2, OUTPUT);
  pinMode(RIGHT_MOTOR_PWM, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR1, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR2, OUTPUT);
  
  // Initialize ultrasonic sensor pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Initialize servo
  scanServo.attach(SERVO_PIN);
  scanServo.write(currentServoAngle); // Center position
  
  // Stop motors on startup (safety)
  stopMotors();
  
  // Send startup message after a brief delay
  delay(1000);
  Serial.println("ARDUINO:READY");
}

// Main loop
void loop() {
  // Process any incoming commands
  processSerial();
  
  // Read distance sensor
  if (millis() - lastDistance > 100) {  // Every 100ms
    distance = readDistance();
    lastDistance = millis();
    
    // Only send if it's been at least TX_INTERVAL ms since last transmission
    if (millis() - lastTxTime > TX_INTERVAL) {
      sendDistanceReading(distance);
      lastTxTime = millis();
    }
  }
}

// Read serial for commands
void processSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    // Check for end of command
    if (c == '\n' || c == '\r') {
      if (commandIndex > 0) {
        command[commandIndex] = '\0';  // Null terminate
        executeCommand(command);
        commandIndex = 0;  // Reset for next command
      }
    } 
    else if (commandIndex < MAX_COMMAND_LENGTH - 1) {
      command[commandIndex++] = c;
    }
  }
}

// Execute a command from the Raspberry Pi
void executeCommand(char* cmd) {
  // Motor commands
  if (strcmp(cmd, "FWD") == 0) {
    moveForward(255);
    Serial.println("ACK:FWD");
  } 
  else if (strncmp(cmd, "FWD:", 4) == 0) {
    int speed = atoi(cmd + 4);
    moveForward(speed);
    Serial.println("ACK:FWD");
  }
  else if (strcmp(cmd, "BCK") == 0) {
    moveBackward(255);
    Serial.println("ACK:BCK");
  }
  else if (strncmp(cmd, "BCK:", 4) == 0) {
    int speed = atoi(cmd + 4);
    moveBackward(speed);
    Serial.println("ACK:BCK");
  }
  else if (strcmp(cmd, "LFT") == 0) {
    turnLeft(255);
    Serial.println("ACK:LFT");
  }
  else if (strncmp(cmd, "LFT:", 4) == 0) {
    int speed = atoi(cmd + 4);
    turnLeft(speed);
    Serial.println("ACK:LFT");
  }
  else if (strcmp(cmd, "RGT") == 0) {
    turnRight(255);
    Serial.println("ACK:RGT");
  }
  else if (strncmp(cmd, "RGT:", 4) == 0) {
    int speed = atoi(cmd + 4);
    turnRight(speed);
    Serial.println("ACK:RGT");
  }
  else if (strcmp(cmd, "STP") == 0) {
    stopMotors();
    Serial.println("ACK:STP");
  }
  
  // Servo control commands
  else if (strncmp(cmd, "SRV:", 4) == 0) {
    int angle = atoi(cmd + 4);
    setServoAngle(angle);
    Serial.println("ACK:SRV");
  }
  else if (strcmp(cmd, "SCAN") == 0) {
    performScan();
    Serial.println("ACK:SCAN");
  }
  
  // System commands
  else if (strcmp(cmd, "PING") == 0) {
    Serial.println("PONG");
  }
  else if (strcmp(cmd, "BAT") == 0) {
    sendBatteryLevel();
  }
  else {
    Serial.print("ERR:UNKNOWN_CMD:");
    Serial.println(cmd);
  }
}

// Motor control functions
void moveForward(int speed) {
  speed = constrain(speed, 0, 255);
  
  digitalWrite(LEFT_MOTOR_DIR1, HIGH);
  digitalWrite(LEFT_MOTOR_DIR2, LOW);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  digitalWrite(RIGHT_MOTOR_DIR1, HIGH);
  digitalWrite(RIGHT_MOTOR_DIR2, LOW);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void moveBackward(int speed) {
  speed = constrain(speed, 0, 255);
  
  digitalWrite(LEFT_MOTOR_DIR1, LOW);
  digitalWrite(LEFT_MOTOR_DIR2, HIGH);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  digitalWrite(RIGHT_MOTOR_DIR1, LOW);
  digitalWrite(RIGHT_MOTOR_DIR2, HIGH);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void turnLeft(int speed) {
  speed = constrain(speed, 0, 255);
  
  digitalWrite(LEFT_MOTOR_DIR1, LOW);
  digitalWrite(LEFT_MOTOR_DIR2, HIGH);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  digitalWrite(RIGHT_MOTOR_DIR1, HIGH);
  digitalWrite(RIGHT_MOTOR_DIR2, LOW);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void turnRight(int speed) {
  speed = constrain(speed, 0, 255);
  
  digitalWrite(LEFT_MOTOR_DIR1, HIGH);
  digitalWrite(LEFT_MOTOR_DIR2, LOW);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  digitalWrite(RIGHT_MOTOR_DIR1, LOW);
  digitalWrite(RIGHT_MOTOR_DIR2, HIGH);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void stopMotors() {
  digitalWrite(LEFT_MOTOR_DIR1, LOW);
  digitalWrite(LEFT_MOTOR_DIR2, LOW);
  analogWrite(LEFT_MOTOR_PWM, 0);
  
  digitalWrite(RIGHT_MOTOR_DIR1, LOW);
  digitalWrite(RIGHT_MOTOR_DIR2, LOW);
  analogWrite(RIGHT_MOTOR_PWM, 0);
}

// Distance sensor functions
int readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH);
  int dist = duration * 0.034 / 2;  // Convert to cm
  
  return constrain(dist, 0, 400);  // HC-SR04 has max range of ~400cm
}

// Servo control functions
void setServoAngle(int angle) {
  angle = constrain(angle, SCAN_MIN_ANGLE, SCAN_MAX_ANGLE);
  scanServo.write(angle);
  currentServoAngle = angle;
}

// Perform a full area scan with the servo and ultrasonic sensor
void performScan() {
  isScanning = true;
  
  // First move to starting position
  setServoAngle(SCAN_MIN_ANGLE);
  delay(SCAN_DELAY * 2);  // Extra delay for initial positioning
  
  // Scan from left to right
  for (int angle = SCAN_MIN_ANGLE; angle <= SCAN_MAX_ANGLE; angle += SCAN_STEP) {
    setServoAngle(angle);
    delay(SCAN_DELAY);
    
    // Measure distance at this angle
    int dist = readDistance();
    
    // Send scan data to Pi
    Serial.print("SCAN:");
    Serial.print(angle);
    Serial.print(":");
    Serial.println(dist);
  }
  
  // Return to center position
  setServoAngle(90);
  
  // Send end of scan marker
  Serial.println("SCAN:END");
  isScanning = false;
}

// Send distance reading to the Raspberry Pi
void sendDistanceReading(int dist) {
  Serial.print("DIST:");
  Serial.println(dist);
}

// Send battery level to the Raspberry Pi
void sendBatteryLevel() {
  int batteryValue = analogRead(BATTERY_PIN);
  // Map to a percentage (adjust these values based on your battery)
  int batteryPercent = map(batteryValue, 614, 768, 0, 100);
  batteryPercent = constrain(batteryPercent, 0, 100);
  
  Serial.print("BAT:");
  Serial.println(batteryPercent);
}

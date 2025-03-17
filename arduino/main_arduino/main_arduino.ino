// Include the other Arduino files
#include "../sensor_module/ultrasonic_sensor.ino"
#include "../motor_control/motor_control.ino"

// Define constants
#define MOTOR_SPEED 150      // Speed from 0-255
#define OBSTACLE_DISTANCE 20 // Distance in cm
#define SERIAL_BAUD 9600     // Serial baud rate

// Serial communication
String inputString = "";
boolean stringComplete = false;

// Operating mode
enum OperatingMode {
  AUTO_MODE,     // Autonomous operation
  COMMAND_MODE   // Remote controlled
};

OperatingMode currentMode = COMMAND_MODE; // Default to command mode

// Timing variables
unsigned long lastDistanceUpdate = 0;
const unsigned long distanceUpdateInterval = 200; // 200ms between distance updates

void setup() {
  Serial.begin(SERIAL_BAUD);
  setup_ultrasonic();
  setup_motors();
  
  // Wait for serial port to connect
  delay(500);
  
  // Reserve memory for input string
  inputString.reserve(200);
  
  // Send initial status message
  Serial.println("ROBOT:READY");
}

void loop() {
  // Update current time
  unsigned long currentMillis = millis();
  
  // Regularly measure and send distance
  if (currentMillis - lastDistanceUpdate > distanceUpdateInterval) {
    int distance = measure_distance();
    Serial.print("DIST:");
    Serial.println(distance);
    lastDistanceUpdate = currentMillis;
    
    // In auto mode, handle obstacle avoidance
    if (currentMode == AUTO_MODE) {
      handleAutonomousBehavior(distance);
    }
  }
  
  // Process any incoming commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Process any bytes from serial port
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
      break;
    }
  }
}

void processCommand(String command) {
  command.trim();  // Remove newline and any whitespace
  
  // Motor commands
  if (command == "FWD") {
    move_forward(MOTOR_SPEED);
    Serial.println("ACK:FWD");
  } 
  else if (command == "BCK") {
    move_backward(MOTOR_SPEED);
    Serial.println("ACK:BCK");
  }
  else if (command == "LFT") {
    turn_left(MOTOR_SPEED);
    Serial.println("ACK:LFT");
  }
  else if (command == "RGT") {
    turn_right(MOTOR_SPEED);
    Serial.println("ACK:RGT");
  }
  else if (command == "STP") {
    stop_motors();
    Serial.println("ACK:STP");
  }
  // Mode commands
  else if (command == "AUTO") {
    currentMode = AUTO_MODE;
    Serial.println("MODE:AUTO");
  }
  else if (command == "CMD") {
    currentMode = COMMAND_MODE;
    Serial.println("MODE:CMD");
  }
  // Info commands
  else if (command == "PING") {
    Serial.println("PONG");
  }
  else if (command == "STATUS") {
    sendStatusInfo();
  }
  else {
    Serial.println("ERR:UNKNOWN_COMMAND");
  }
}

void sendStatusInfo() {
  Serial.println("STATUS:BEGIN");
  
  // Send current mode
  Serial.print("MODE:");
  Serial.println(currentMode == AUTO_MODE ? "AUTO" : "CMD");
  
  // Send distance
  Serial.print("DIST:");
  Serial.println(measure_distance());
  
  // Send voltage if we had a sensor
  Serial.println("VOLT:5.0");
  
  Serial.println("STATUS:END");
}

void handleAutonomousBehavior(int distance) {
  // Simple obstacle avoidance
  if (distance < OBSTACLE_DISTANCE) {
    // Too close, stop and turn
    stop_motors();
    delay(300);
    
    // Decide to turn left or right based on some factor
    // For simplicity, we'll use time to decide
    if ((millis() % 2000) < 1000) {
      turn_left(MOTOR_SPEED);
    } else {
      turn_right(MOTOR_SPEED);
    }
    delay(700); // Turn for a moment
  } else {
    // Clear path ahead, move forward
    move_forward(MOTOR_SPEED);
  }
}

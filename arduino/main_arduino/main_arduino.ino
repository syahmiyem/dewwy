// Include the other Arduino files
#include "../sensor_module/ultrasonic_sensor.ino"
#include "../motor_control/motor_control.ino"

// Define constants
#define MOTOR_SPEED 150      // Speed from 0-255
#define OBSTACLE_DISTANCE 20 // Distance in cm
#define SERIAL_BAUD 9600     // Serial baud rate
#define AVOIDANCE_BACKUP_TIME 300    // ms to back up from obstacle
#define AVOIDANCE_TURN_TIME 700     // ms to turn away from obstacle
#define AVOIDANCE_FORWARD_TIME 500  // ms to move forward after turning

// Serial communication
String inputString = "";
boolean stringComplete = false;

// Operating mode
enum OperatingMode {
  AUTO_MODE,     // Autonomous operation
  COMMAND_MODE   // Remote controlled
};

// Robot movement state for avoidance maneuver
enum AvoidanceState {
  NONE,          // No avoidance in progress
  BACKING_UP,    // Step 1: Moving backward
  TURNING,       // Step 2: Turning away from obstacle
  MOVING_FORWARD // Step 3: Moving forward in new direction
};

OperatingMode currentMode = COMMAND_MODE; // Default to command mode
AvoidanceState avoidanceState = NONE;     // Current avoidance maneuver state

// Timing variables
unsigned long lastDistanceUpdate = 0;
const unsigned long distanceUpdateInterval = 200; // 200ms between distance updates
unsigned long avoidanceStartTime = 0;         // When current avoidance step started
unsigned long lastStuckCheckTime = 0;         // For stuck detection
unsigned long lastPositionChangeTime = 0;     // For stuck detection

// Avoidance parameters
boolean turningDirection = true;    // true = left, false = right
int stuckCount = 0;                 // How many times robot has been stuck
int previousDistance = 100;         // Previously measured distance
int sameDistanceCount = 0;          // Count of repeated similar distance readings

void setup() {
  Serial.begin(SERIAL_BAUD);
  setup_ultrasonic();
  setup_motors();
  
  // Wait for serial port to connect
  delay(500);
  
  // Reserve memory for input string
  inputString.reserve(200);
  
  // Initialize timing variables
  lastStuckCheckTime = millis();
  lastPositionChangeTime = millis();
  
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
      checkForStuckCondition(distance);
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
  // If currently executing an avoidance maneuver
  if (avoidanceState != NONE) {
    executeAvoidanceManeuver(distance);
    return;
  }
  
  // Start a new avoidance maneuver if obstacle detected
  if (distance < OBSTACLE_DISTANCE) {
    startAvoidanceManeuver();
  } else {
    // No obstacles, move forward
    move_forward(MOTOR_SPEED);
  }
}

void startAvoidanceManeuver() {
  // Begin the multi-step avoidance maneuver
  avoidanceState = BACKING_UP;
  avoidanceStartTime = millis();
  
  // Choose turn direction, alternating for better coverage
  // But when stuck, maintain same direction for more extensive turn
  if (stuckCount <= 0) {
    turningDirection = !turningDirection; // Alternate direction
  }
  
  // Send status
  Serial.println("Starting avoidance maneuver");
}

void executeAvoidanceManeuver(int distance) {
  unsigned long currentTime = millis();
  unsigned long elapsedTime = currentTime - avoidanceStartTime;
  
  switch (avoidanceState) {
    case BACKING_UP:
      // Step 1: Back up to get away from the obstacle
      move_backward(MOTOR_SPEED);
      
      // After backing up time, move to turning phase
      if (elapsedTime > AVOIDANCE_BACKUP_TIME) {
        avoidanceState = TURNING;
        avoidanceStartTime = currentTime;
      }
      break;
      
    case TURNING:
      // Step 2: Turn in the chosen direction
      
      // Calculate turn time based on stuck count (turns longer if stuck)
      int turnTime = AVOIDANCE_TURN_TIME;
      if (stuckCount > 0) {
        // Increase turn amount by 30% for each stuck count up to triple
        turnTime = min(AVOIDANCE_TURN_TIME * (1 + stuckCount * 0.3), AVOIDANCE_TURN_TIME * 3);
      }
      
      // Execute turn based on selected direction
      if (turningDirection) {
        turn_left(MOTOR_SPEED);
      } else {
        turn_right(MOTOR_SPEED);
      }
      
      // After turning time, move to forward phase
      if (elapsedTime > turnTime) {
        avoidanceState = MOVING_FORWARD;
        avoidanceStartTime = currentTime;
      }
      break;
      
    case MOVING_FORWARD:
      // Step 3: Move forward in new direction
      move_forward(MOTOR_SPEED);
      
      // If we encounter another obstacle immediately, restart avoidance
      if (distance < OBSTACLE_DISTANCE) {
        startAvoidanceManeuver();
        return;
      }
      
      // After forward time, end the maneuver
      if (elapsedTime > AVOIDANCE_FORWARD_TIME) {
        avoidanceState = NONE;
        Serial.println("Avoidance maneuver complete");
      }
      break;
      
    default:
      // Should never get here, but just in case
      avoidanceState = NONE;
  }
}

void checkForStuckCondition(int distance) {
  // Only check periodically (every 1 second)
  unsigned long currentTime = millis();
  if (currentTime - lastStuckCheckTime < 1000) {
    return;
  }
  
  lastStuckCheckTime = currentTime;
  
  // Check if distance is very similar to previous reading (±10%)
  if (abs(distance - previousDistance) < (previousDistance * 0.1)) {
    sameDistanceCount++;
  } else {
    sameDistanceCount = 0;
    lastPositionChangeTime = currentTime;
  }
  
  // If we've had similar readings for a while, consider robot stuck
  if (sameDistanceCount >= 5) {
    stuckCount++;
    sameDistanceCount = 0;
    
    // If stuck, start a new avoidance maneuver
    if (avoidanceState == NONE) {
      Serial.println("Robot appears stuck, starting avoidance");
      startAvoidanceManeuver();
    }
  } 
  else if (currentTime - lastPositionChangeTime > 5000) {
    // If position hasn't changed in 5 seconds, consider stuck
    stuckCount++;
    lastPositionChangeTime = currentTime;
    
    // If stuck, start a new avoidance maneuver
    if (avoidanceState == NONE) {
      Serial.println("Robot position unchanged, starting avoidance");
      startAvoidanceManeuver();
    }
  }
  else if (stuckCount > 0 && currentTime - lastPositionChangeTime > 10000) {
    // If position has changed for a while, decrement stuck count
    stuckCount = max(0, stuckCount - 1);
  }
  
  // Store current distance for next comparison
  previousDistance = distance;
}

// Include the other Arduino files
#include "../sensor_module/ultrasonic_sensor.ino"
#include "../motor_control/motor_control.ino"

// Define constants
#define MOTOR_SPEED 150  // Speed from 0-255
#define OBSTACLE_DISTANCE 20  // Distance in cm

// Serial communication
String inputString = "";
boolean stringComplete = false;

void setup() {
  Serial.begin(9600);
  setup_ultrasonic();
  setup_motors();
  
  // Wait for serial port to connect
  while (!Serial) {
    ; // wait for serial port to connect
  }
  
  // Reserve memory for input string
  inputString.reserve(200);
}

void loop() {
  // Measure distance
  int distance = measure_distance();
  
  // Send distance to Raspberry Pi
  Serial.print("DIST:");
  Serial.println(distance);
  
  // Process any incoming commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Auto obstacle avoidance if enabled
  // This will be controlled by commands from RPi
  
  delay(100);  // Small delay between readings
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void processCommand(String command) {
  command.trim();  // Remove newline and any whitespace
  
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
  else {
    Serial.println("ERR:UNKNOWN_COMMAND");
  }
}

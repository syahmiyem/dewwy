#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     -1 // Reset pin
#define SCREEN_ADDRESS 0x3C // Typically 0x3C for 128x64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Motor control pins
#define LEFT_MOTOR_PWM 5
#define LEFT_MOTOR_DIR1 4
#define LEFT_MOTOR_DIR2 3
#define RIGHT_MOTOR_PWM 6
#define RIGHT_MOTOR_DIR1 7
#define RIGHT_MOTOR_DIR2 8

// Optional encoder pins (if connected)
#define LEFT_ENCODER_A 2
#define LEFT_ENCODER_B A0
#define RIGHT_ENCODER_A A1
#define RIGHT_ENCODER_B A2

// Battery monitoring
#define BATTERY_PIN A3

// Add HC-SR04 pins
#define TRIG_PIN 12  // Trigger pin
#define ECHO_PIN 11  // Echo pin

// States and emotions
enum RobotState {
  IDLE,
  ROAMING,
  AVOIDING,
  SLEEPING
};

enum Emotion {
  NEUTRAL,
  HAPPY,
  SAD,
  EXCITED,
  SLEEPY,
  CURIOUS,
  SCARED
};

// Current state
RobotState currentState = IDLE;
Emotion currentEmotion = NEUTRAL;
unsigned long stateStartTime = 0;
unsigned long lastBlinkTime = 0;
bool isBlinking = false;
int animationFrame = 0;
unsigned long lastFrameTime = 0;
const int frameInterval = 200;  // Animation frame duration in ms

// For random behaviors
unsigned long seed;

// Add autopilot control variables
bool autopilotEnabled = true;  // Start with autopilot ON by default

// Add global variables for the sensor
long duration;
int distance;
unsigned long last_sensor_reading = 0;
const int sensor_read_interval = 100;  // Read sensor every 100ms

void setup() {
  // Initialize serial for debugging
  Serial.begin(9600);
  Serial.println("Dewwy Standalone Starting...");
  
  // Initialize display
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  
  // Clear display
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Dewwy - Standalone");
  display.display();
  delay(1000);
  
  // Initialize motor control pins
  pinMode(LEFT_MOTOR_PWM, OUTPUT);
  pinMode(LEFT_MOTOR_DIR1, OUTPUT);
  pinMode(LEFT_MOTOR_DIR2, OUTPUT);
  pinMode(RIGHT_MOTOR_PWM, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR1, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR2, OUTPUT);
  
  // Stop motors initially
  stopMotors();
  
  // Set up random seed from an unconnected analog pin
  seed = analogRead(A5);
  randomSeed(seed);
  
  // Initial state and timing
  setState(IDLE);
  setEmotion(NEUTRAL);
  stateStartTime = millis();
  
  // Initialize ultrasonic sensor pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Initialize servo for scanning
  setupServo();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Measure distance with ultrasonic sensor
  if (currentTime - last_sensor_reading > sensor_read_interval) {
    distance = measureDistance();
    last_sensor_reading = currentTime;
    
    // Obstacle avoidance when autopilot is enabled
    if (autopilotEnabled && distance < 20 && currentState != AVOIDING) {
      setState(AVOIDING);
      setEmotion(SCARED);
    }
  }
  
  // Update animation at regular intervals
  if (currentTime - lastFrameTime > frameInterval) {
    animationFrame++;
    lastFrameTime = currentTime;
  }
  
  // Update blink state
  updateBlinking(currentTime);
  
  // Process serial commands (if any)
  processSerialCommands();
  
  // Core state machine
  switch (currentState) {
    case IDLE:
      executeIdleState(currentTime);
      break;
    case ROAMING:
      executeRoamingState(currentTime);
      break;
    case AVOIDING:
      executeAvoidingState(currentTime);
      break;
    case SLEEPING:
      executeSleepingState(currentTime);
      break;
  }
  
  // Always update the display
  updateDisplay();
  
  // Update scanner
  updateScanner();
  
  // Small delay to prevent too frequent updates
  delay(20);
}

void updateBlinking(unsigned long currentTime) {
  // Handle blinking
  int blinkInterval = 3000;  // Default 3 seconds between blinks
  int blinkDuration = 200;   // Default blink lasts 200ms
  
  // Adjust intervals based on emotion
  switch (currentEmotion) {
    case SLEEPY:
      blinkInterval = 1000;  // More frequent blinking when sleepy
      blinkDuration = 500;   // Longer blinks
      break;
    case EXCITED:
      blinkInterval = 1500;  // Faster blinking when excited
      blinkDuration = 150;   // Quick blinks
      break;
    case SCARED:
      blinkInterval = 4000;  // Rare blinking when scared
      blinkDuration = 100;   // Very quick blinks
      break;
    default:
      // Use defaults
      break;
  }
  
  if (isBlinking && currentTime - lastBlinkTime > blinkDuration) {
    isBlinking = false;
  } 
  else if (!isBlinking && currentTime - lastBlinkTime > blinkInterval) {
    isBlinking = true;
    lastBlinkTime = currentTime;
  }
}

void setState(RobotState newState) {
  if (newState != currentState) {
    currentState = newState;
    stateStartTime = millis();
    
    // Log state change
    Serial.print("State: ");
    switch (currentState) {
      case IDLE: Serial.println("IDLE"); break;
      case ROAMING: Serial.println("ROAMING"); break;
      case AVOIDING: Serial.println("AVOIDING"); break;
      case SLEEPING: Serial.println("SLEEPING"); break;
    }
    
    // Reset animation
    animationFrame = 0;
    
    // Stop motors on state change (safety)
    if (newState == IDLE || newState == SLEEPING) {
      stopMotors();
    }
  }
}

void setEmotion(Emotion newEmotion) {
  if (newEmotion != currentEmotion) {
    currentEmotion = newEmotion;
    
    // Log emotion change
    Serial.print("Emotion: ");
    switch (currentEmotion) {
      case NEUTRAL: Serial.println("NEUTRAL"); break;
      case HAPPY: Serial.println("HAPPY"); break;
      case SAD: Serial.println("SAD"); break;
      case EXCITED: Serial.println("EXCITED"); break;
      case SLEEPY: Serial.println("SLEEPY"); break;
      case CURIOUS: Serial.println("CURIOUS"); break;
      case SCARED: Serial.println("SCARED"); break;
    }
    
    // Reset animation
    animationFrame = 0;
  }
}

void processSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "FWD") {
      moveForward(180);
    } else if (command == "BCK") {
      moveBackward(180);
    } else if (command == "LFT") {
      turnLeft(200);
    } else if (command == "RGT") {
      turnRight(200);
    } else if (command == "STP") {
      stopMotors();
    } else if (command == "ROAM") {
      setState(ROAMING);
    } else if (command == "IDLE") {
      setState(IDLE);
    } else if (command == "SLEEP") {
      setState(SLEEPING);
      setEmotion(SLEEPY);
    } else if (command == "HAPPY") {
      setEmotion(HAPPY);
    } else if (command == "SAD") {
      setEmotion(SAD);
    } else if (command == "NEUTRAL") {
      setEmotion(NEUTRAL);
    } else if (command == "EXCITED") {
      setEmotion(EXCITED);
    } else if (command == "CURIOUS") {
      setEmotion(CURIOUS);
    } else if (command == "SCARED") {
      setEmotion(SCARED);
    } else if (command == "AUTO_ON") {
      autopilotEnabled = true;
      Serial.println("Autopilot enabled");
    } 
    else if (command == "AUTO_OFF") {
      autopilotEnabled = false;
      Serial.println("Autopilot disabled");
      stopMotors();  // Stop motors when disabling autopilot
    }
    
    // Process servo scan commands
    processServoScanCommands(command);
  }
}

// State execution functions

void executeIdleState(unsigned long currentTime) {
  // In idle state, just stay still but randomly change emotion
  if (currentTime - stateStartTime > 10000) {  // Every 10 seconds
    // 10% chance of changing to a random emotion
    if (random(10) == 0) {
      Emotion randomEmotion = (Emotion)random(7);  // 0-6 for emotions
      setEmotion(randomEmotion);
    }
    
    // Only transition to other states if autopilot is enabled
    if (autopilotEnabled) {
      // 5% chance of transitioning to ROAMING
      if (random(20) == 0) {
        setState(ROAMING);
        setEmotion(CURIOUS);
      }
      
      // 5% chance of transitioning to SLEEPING
      if (random(20) == 0) {
        setState(SLEEPING);
        setEmotion(SLEEPY);
      }
    }
    
    stateStartTime = currentTime;
  }
}

void executeRoamingState(unsigned long currentTime) {
  // If autopilot is disabled, transition back to IDLE
  if (!autopilotEnabled) {
    setState(IDLE);
    return;
  }

  unsigned long stateElapsed = currentTime - stateStartTime;
  
  // For simplicity, just move in patterns
  // Change direction every 3 seconds
  if (stateElapsed % 3000 < 1500) {
    moveForward(150);
  } else {
    // Turn randomly
    if ((stateElapsed / 3000) % 2 == 0) {
      turnLeft(180);
    } else {
      turnRight(180);
    }
  }
  
  // Occasionally transition back to IDLE
  if (stateElapsed > 30000 && random(100) < 5) {  // 5% chance after 30 seconds
    setState(IDLE);
  }
}

void executeAvoidingState(unsigned long currentTime) {
  // If autopilot is disabled, transition back to IDLE
  if (!autopilotEnabled) {
    setState(IDLE);
    return;
  }

  unsigned long stateElapsed = currentTime - stateStartTime;
  
  // Modified obstacle avoidance sequence with scanning
  if (stateElapsed < 1000) {
    // Back up first
    moveBackward(180);
  } else if (stateElapsed < 2000) {
    // Stop and scan the area
    stopMotors();
    
    // Only perform the scan once when we enter this phase
    if (stateElapsed < 1100) {
      performScan();
    }
  } else if (stateElapsed < 4000) {
    // Turn toward the clearest path
    turnTowardClearestPath();
  } else {
    // Check if path is clear before moving forward
    if (distance > 30) {
      // Path is clear, return to roaming
      setState(ROAMING);
      setEmotion(CURIOUS);
    } else {
      // Path still blocked, continue turning
      // Extend the turning time
      stateStartTime = currentTime - 2000;
    }
  }
}

void executeSleepingState(unsigned long currentTime) {
  // If autopilot is disabled, transition back to IDLE
  if (!autopilotEnabled) {
    setState(IDLE);
    return;
  }

  // Do nothing but occasionally wake up
  if (currentTime - stateStartTime > 20000) {  // Sleep for 20 seconds
    // 10% chance of waking up
    if (random(10) == 0) {
      setState(IDLE);
      setEmotion(NEUTRAL);
    }
  }
}

// Motor control functions

void moveForward(int speed) {
  // Left motor forward
  digitalWrite(LEFT_MOTOR_DIR1, HIGH);
  digitalWrite(LEFT_MOTOR_DIR2, LOW);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  // Right motor forward
  digitalWrite(RIGHT_MOTOR_DIR1, HIGH);
  digitalWrite(RIGHT_MOTOR_DIR2, LOW);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void moveBackward(int speed) {
  // Left motor backward
  digitalWrite(LEFT_MOTOR_DIR1, LOW);
  digitalWrite(LEFT_MOTOR_DIR2, HIGH);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  // Right motor backward
  digitalWrite(RIGHT_MOTOR_DIR1, LOW);
  digitalWrite(RIGHT_MOTOR_DIR2, HIGH);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void turnLeft(int speed) {
  // Left motor backward
  digitalWrite(LEFT_MOTOR_DIR1, LOW);
  digitalWrite(LEFT_MOTOR_DIR2, HIGH);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  // Right motor forward
  digitalWrite(RIGHT_MOTOR_DIR1, HIGH);
  digitalWrite(RIGHT_MOTOR_DIR2, LOW);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void turnRight(int speed) {
  // Left motor forward
  digitalWrite(LEFT_MOTOR_DIR1, HIGH);
  digitalWrite(LEFT_MOTOR_DIR2, LOW);
  analogWrite(LEFT_MOTOR_PWM, speed);
  
  // Right motor backward
  digitalWrite(RIGHT_MOTOR_DIR1, LOW);
  digitalWrite(RIGHT_MOTOR_DIR2, HIGH);
  analogWrite(RIGHT_MOTOR_PWM, speed);
}

void stopMotors() {
  // Stop both motors
  digitalWrite(LEFT_MOTOR_DIR1, LOW);
  digitalWrite(LEFT_MOTOR_DIR2, LOW);
  analogWrite(LEFT_MOTOR_PWM, 0);
  
  digitalWrite(RIGHT_MOTOR_DIR1, LOW);
  digitalWrite(RIGHT_MOTOR_DIR2, LOW);
  analogWrite(RIGHT_MOTOR_PWM, 0);
}

// Add distance measurement function
int measureDistance() {
  // Clear the TRIG_PIN
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Set the TRIG_PIN HIGH for 10 microseconds
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read the ECHO_PIN, return the sound wave travel time in microseconds
  duration = pulseIn(ECHO_PIN, HIGH);
  
  // Calculate and return the distance
  int dist = duration * 0.034 / 2;  // Speed of sound is 0.034 cm/us, divide by 2 (go and back)
  
  // Print to serial for debugging
  Serial.print("Distance: ");
  Serial.print(dist);
  Serial.println(" cm");
  
  // Constrain to valid range (HC-SR04 is reliable between 2-400 cm)
  dist = constrain(dist, 0, 400);
  
  return dist;
}

// Display functions

void updateDisplay() {
  display.clearDisplay();
  
  // Draw the appropriate face based on emotion
  switch (currentEmotion) {
    case NEUTRAL:
      drawNeutralFace();
      break;
    case HAPPY:
      drawHappyFace();
      break;
    case SAD:
      drawSadFace();
      break;
    case EXCITED:
      drawExcitedFace();
      break;
    case SLEEPY:
      drawSleepyFace();
      break;
    case CURIOUS:
      drawCuriousFace();
      break;
    case SCARED:
      drawScaredFace();
      break;
  }
  
  // Draw state at the bottom
  display.setCursor(0, 57);
  display.print(getStateText());
  
  // Display auto/manual mode and battery level
  display.setCursor(60, 57);
  display.print(autopilotEnabled ? "AUTO" : "MANUAL");
  
  // Display battery level
  drawBattery();
  
  // Display distance at top left
  display.setCursor(2, 0);
  display.print(distance);
  display.print("cm");
  
  display.display();
}

String getStateText() {
  switch (currentState) {
    case IDLE: return "IDLE";
    case ROAMING: return "ROAMING";
    case AVOIDING: return "AVOIDING";
    case SLEEPING: return "SLEEPING";
    default: return "UNKNOWN";
  }
}

void drawBattery() {
  // Read battery level
  int batteryValue = analogRead(BATTERY_PIN);
  // Convert to percentage (assuming 3.7V full, 3.0V empty)
  int batteryPercent = map(batteryValue, 614, 768, 0, 100);  // These values may need calibration
  batteryPercent = constrain(batteryPercent, 0, 100);
  
  // Draw battery icon at top right
  display.setCursor(95, 0);
  display.print(batteryPercent);
  display.print("%");
}

// Face drawing functions - enhanced to maximize screen usage
void drawNeutralFace() {
  // Center coordinates - use more of the screen vertically
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5; // Shifted up slightly to make room for status line
  int eyeSize = 6; // Larger eyes
  
  // Eyes
  int eyeY = y - 8;
  int eyeDistance = 20; // More distance between eyes
  
  if (!isBlinking) {
    display.fillCircle(x - eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    display.fillCircle(x + eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
  } else {
    display.drawFastHLine(x - eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
    display.drawFastHLine(x + eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
  }
  
  // Mouth - straight line (wider)
  display.drawFastHLine(x - 20, y + 15, 40, SSD1306_WHITE);
  display.drawFastHLine(x - 20, y + 16, 40, SSD1306_WHITE); // Thicker mouth
}

void drawHappyFace() {
  // Center coordinates - better screen usage
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5;
  int eyeSize = 6;
  
  // Add subtle bouncy movement based on frame
  int bounce = animationFrame % 4;
  
  // Eyes
  int eyeY = y - 8 - bounce;
  int eyeDistance = 20;
  
  if (!isBlinking) {
    display.fillCircle(x - eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    display.fillCircle(x + eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
  } else {
    display.drawFastHLine(x - eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
    display.drawFastHLine(x + eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
  }
  
  // Smile - wider and more pronounced curve
  for (int i = -25; i <= 25; i++) {
    // Enhanced smile curve
    int mouthY = y + 12 + (i * i) / 25;
    display.drawPixel(x + i, mouthY, SSD1306_WHITE);
    display.drawPixel(x + i, mouthY + 1, SSD1306_WHITE); // Thicker line
  }
}

void drawSadFace() {
  // Center coordinates
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5;
  int eyeSize = 6;
  int eyeDistance = 20;
  
  // Eyes - droopy
  int eyeY = y - 8;
  if (!isBlinking) {
    // Sad eyes - angled slightly
    display.fillCircle(x - eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    display.fillCircle(x + eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    
    // Sad eyebrows
    display.drawLine(x - eyeDistance - 6, eyeY - 6, x - eyeDistance + 4, eyeY - 8, SSD1306_WHITE);
    display.drawLine(x + eyeDistance - 4, eyeY - 8, x + eyeDistance + 6, eyeY - 6, SSD1306_WHITE);
  } else {
    display.drawFastHLine(x - eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
    display.drawFastHLine(x + eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
  }
  
  // Frown curve - wider and more pronounced
  for (int i = -25; i <= 25; i++) {
    // Inverted curve for sad - deeper frown
    int mouthY = y + 25 - (i * i) / 25;
    display.drawPixel(x + i, mouthY, SSD1306_WHITE);
    display.drawPixel(x + i, mouthY + 1, SSD1306_WHITE); // Thicker line
  }
}

void drawExcitedFace() {
  // Center coordinates
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5;
  
  // Bouncy animation
  int bounce = (animationFrame % 6) - 3;
  y += bounce;
  
  // Larger eyes with pupils
  int eyeY = y - 10;
  int eyeDistance = 22;
  int eyeSize = 9;
  int pupilSize = 4;
  
  if (!isBlinking) {
    // Excited eyes - wide with pupils
    display.fillCircle(x - eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    display.fillCircle(x + eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    display.fillCircle(x - eyeDistance, eyeY, pupilSize, SSD1306_BLACK);
    display.fillCircle(x + eyeDistance, eyeY, pupilSize, SSD1306_BLACK);
  } else {
    display.drawFastHLine(x - eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
    display.drawFastHLine(x + eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
  }
  
  // Wide excited smile - double thickness
  for (int i = -30; i <= 30; i++) {
    // Wider, more curved smile
    int mouthY = y + 15 + (i * i) / 30;
    display.drawPixel(x + i, mouthY, SSD1306_WHITE);
    display.drawPixel(x + i, mouthY + 1, SSD1306_WHITE);
    display.drawPixel(x + i, mouthY + 2, SSD1306_WHITE);
  }
}

void drawSleepyFace() {
  // Center coordinates
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5;
  int eyeDistance = 20;
  int eyeSize = 6;
  
  // Eyes are always closed or nearly closed
  display.drawFastHLine(x - eyeDistance - eyeSize, y - 8, eyeSize * 2, SSD1306_WHITE);
  display.drawFastHLine(x + eyeDistance - eyeSize, y - 8, eyeSize * 2, SSD1306_WHITE);
  
  // Z's floating up - properly positioned inside the screen bounds
  // Choose Z positions that will remain within screen
  if (animationFrame % 4 >= 2) {
    // First Z - smaller and closer to face
    display.setCursor(x + 15, y - 10);
    display.setTextSize(1); // Small text
    display.print("z");
  }
  
  if (animationFrame % 6 >= 3) {
    // Second Z - slightly larger, higher up
    display.setCursor(x + 10, y - 20);
    display.setTextSize(2); // Medium text
    display.print("z");
  }
  
  // Slightly open mouth (yawning occasionally)
  if (animationFrame % 8 >= 6) {
    // Yawning
    display.fillCircle(x, y + 15, 10, SSD1306_WHITE);
    display.fillCircle(x, y + 15, 8, SSD1306_BLACK);
  } else {
    // Closed mouth - slightly curved
    display.drawFastHLine(x - 15, y + 15, 30, SSD1306_WHITE);
    display.drawFastHLine(x - 10, y + 16, 20, SSD1306_WHITE);
  }
}

void drawCuriousFace() {
  // Center coordinates
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5;
  int eyeDistance = 20;
  int eyeSize = 7;
  
  // Head tilt effect - shift everything slightly
  int tilt = (animationFrame % 2) * 2;
  
  // Eyes - one larger than the other for curious look
  int eyeY = y - 8;
  if (!isBlinking) {
    // Different sized eyes for curiosity
    display.fillCircle(x - eyeDistance + tilt, eyeY, eyeSize - 1, SSD1306_WHITE);
    display.fillCircle(x + eyeDistance + tilt, eyeY, eyeSize + 1, SSD1306_WHITE);
  } else {
    display.drawFastHLine(x - eyeDistance - eyeSize + tilt, eyeY, eyeSize * 2, SSD1306_WHITE);
    display.drawFastHLine(x + eyeDistance - eyeSize + tilt, eyeY, eyeSize * 2, SSD1306_WHITE);
  }
  
  // Raised eyebrow
  display.drawLine(x - eyeDistance - 8 + tilt, eyeY - 6, x - eyeDistance + 4 + tilt, eyeY - 10, SSD1306_WHITE);
  display.drawLine(x - eyeDistance - 8 + tilt, eyeY - 5, x - eyeDistance + 4 + tilt, eyeY - 9, SSD1306_WHITE);
  
  // Small 'o' mouth
  display.drawCircle(x + tilt, y + 15, 8, SSD1306_WHITE);
  display.drawCircle(x + tilt, y + 15, 7, SSD1306_WHITE);
}

void drawScaredFace() {
  // Center coordinates
  int x = SCREEN_WIDTH / 2;
  int y = SCREEN_HEIGHT / 2 - 5;
  int eyeDistance = 22;
  
  // Trembling effect
  int tremble = (animationFrame % 2) * 2 - 1;
  x += tremble;
  
  // Wide eyes - very large
  int eyeY = y - 10;
  int eyeSize = 10;
  int pupilSize = 5;
  
  if (!isBlinking) {
    // Scared eyes - wide with pupils
    display.fillCircle(x - eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    display.fillCircle(x + eyeDistance, eyeY, eyeSize, SSD1306_WHITE);
    // Pupils looking to the sides (fleeing)
    display.fillCircle(x - eyeDistance - 3, eyeY, pupilSize, SSD1306_BLACK);
    display.fillCircle(x + eyeDistance + 3, eyeY, pupilSize, SSD1306_BLACK);
  } else {
    display.drawFastHLine(x - eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
    display.drawFastHLine(x + eyeDistance - eyeSize, eyeY, eyeSize * 2, SSD1306_WHITE);
  }
  
  // Scared eyebrows
  display.drawLine(x - eyeDistance - 8, eyeY - 10, x - eyeDistance + 8, eyeY - 14, SSD1306_WHITE);
  display.drawLine(x + eyeDistance - 8, eyeY - 14, x + eyeDistance + 8, eyeY - 10, SSD1306_WHITE);
  
  // Open mouth (oval shape) - larger
  display.fillCircle(x, y + 15, 12, SSD1306_WHITE);
  display.fillCircle(x, y + 15, 10, SSD1306_BLACK);
}

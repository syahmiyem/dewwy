# Standalone Dewwy

## Introduction

Standalone Dewwy is a simplified version of the full Dewwy pet robot that runs entirely on an Arduino UNO. This version maintains core functionality including emotional expressions, autonomous movement, and obstacle detection while eliminating the need for a Raspberry Pi. 

Standalone Dewwy features:
- Animated facial expressions on a 128x64 OLED display
- Autonomous movement with randomized behaviors
- Basic obstacle detection and avoidance using an HC-SR04 ultrasonic sensor
- Four states: idle, roaming, avoiding, sleeping
- Seven emotions: neutral, happy, sad, excited, sleepy, curious, scared
- Autopilot and manual control modes
- Complete offline operation with no internet dependency

This standalone version is perfect for testing the robot's basic mechanics before implementing the full Raspberry Pi version, or as a simpler alternative for educational purposes.

## Hardware Requirements

- Arduino UNO board
- Sensor Shield V5 for Arduino UNO
- 128x64 OLED display (I2C)
- HC-SR04 ultrasonic distance sensor
- Dual DC motors (and wheels)
- Motor driver board (TB6612FNG or L298N)
- SG90 servo motor (for radar scanning)
- Battery pack (for motors)
- Optional: Voltage regulator and power bank for Arduino
- Optional: Small breadboard (for prototyping or additional components)

### Why Use the Sensor Shield?

The Sensor Shield V5 simplifies the wiring process by providing organized connections for all components. This reduces errors, creates a cleaner build, and makes the project more beginner-friendly. While not strictly necessary, it's highly recommended for a more reliable and professional result.

## Hardware Setup

### Step 1: OLED Display Connection

Connect the OLED display to Arduino using breadboard and jumper wires:

| OLED Pin | Arduino Pin |
|----------|-------------|
| VCC      | 5V          |
| GND      | GND         |
| SCL      | A5 (SCL)    |
| SDA      | A4 (SDA)    |

### Step 2: HC-SR04 Ultrasonic Sensor Connection

Connect the ultrasonic sensor:

| HC-SR04 Pin | Arduino Pin |
|-------------|-------------|
| VCC         | 5V          |
| Trig        | Pin 12      |
| Echo        | Pin 11      |
| GND         | GND         |

### Step 3: Servo and Ultrasonic Sensor Setup

Mount the HC-SR04 ultrasonic sensor on the SG90 servo to create a radar-like scanning system:

1. Attach the HC-SR04 sensor to the servo horn using hot glue or a small bracket
2. Connect the servo to Arduino:

| SG90 Pin | Sensor Shield/Arduino |
|----------|----------------------|
| Red (power)| 5V                 |
| Brown (GND)| GND                |
| Orange (signal)| Digital Pin 9  |

Connect the ultrasonic sensor:

| HC-SR04 Pin | Sensor Shield/Arduino |
|-------------|----------------------|
| VCC         | 5V                   |
| Trig        | Digital Pin 12       |
| Echo        | Digital Pin 11       |
| GND         | GND                  |

### Step 4: Motor Driver Connection

For TB6612FNG motor driver:

| TB6612FNG Pin | Arduino Pin | Other Connection |
|---------------|-------------|------------------|
| VM            | -           | Motor Power (4-6V) |
| VCC           | 5V          | -                |
| GND           | GND         | GND of motor power|
| PWMA          | Pin 5       | -                |
| AIN1          | Pin 4       | -                |
| AIN2          | Pin 3       | -                |
| PWMB          | Pin 6       | -                |
| BIN1          | Pin 7       | -                |
| BIN2          | Pin 8       | -                |
| A01           | -           | Left Motor +     |
| A02           | -           | Left Motor -     |
| B01           | -           | Right Motor +    |
| B02           | -           | Right Motor -    |
| STBY          | 5V          | Enable the driver|

### Step 5: Battery Connections

1. **Motor Power**: Connect a battery pack (4-6V recommended) to the VM and GND pins of the motor driver.
2. **Arduino Power**: Either power the Arduino via USB during testing, or use a separate power bank/battery pack.

### Step 6: Full Assembly

1. Mount the OLED display in front of the robot (visible part)
2. Mount the servo at the front of the robot, with the ultrasonic sensor attached
3. Attach motors to the wheels and chassis
4. Secure the Arduino, Sensor Shield, and batteries to the chassis

## Software Installation

### Step 1: Required Libraries

Install the following Arduino libraries using the Library Manager (Tools > Manage Libraries):
- Adafruit GFX Library
- Adafruit SSD1306
- Wire (built-in)

### Step 2: Upload the Code

1. Open the `standalone_dewwy.ino` file in Arduino IDE
2. Select your Arduino board and port
3. Click Upload

## Operating Dewwy

### Automatic Mode

By default, Dewwy starts in autopilot mode and will:
1. Begin in IDLE state with neutral emotion
2. Randomly transition between states
3. Detect and avoid obstacles automatically
4. Display appropriate emotions based on its state

### Manual Control via Serial Monitor

You can control Dewwy manually using the Serial Monitor (Tools > Serial Monitor). Set the baud rate to 9600 and send these commands:

#### Movement Commands
- `FWD` - Move forward
- `BCK` - Move backward
- `LFT` - Turn left
- `RGT` - Turn right
- `STP` - Stop movement

#### State Commands
- `IDLE` - Enter idle state
- `ROAM` - Start roaming
- `SLEEP` - Go to sleep mode

#### Emotion Commands
- `NEUTRAL` - Neutral expression
- `HAPPY` - Happy expression
- `SAD` - Sad expression
- `EXCITED` - Excited expression
- `SLEEPY` - Sleepy expression
- `CURIOUS` - Curious expression 
- `SCARED` - Scared expression

#### Autopilot Control
- `AUTO_ON` - Enable autopilot mode
- `AUTO_OFF` - Disable autopilot (manual control)

## Features

### Area Scanning

Dewwy uses its servo-mounted ultrasonic sensor to scan the area in front of it:

1. The servo rotates from 0° to 180° to create a radar-like scan
2. Distance readings are taken at multiple angles
3. The robot analyzes these readings to find the clearest path
4. This significantly improves navigation compared to a fixed sensor

### Basic Navigation Algorithm

The scanning feature enables smarter navigation:
- When an obstacle is detected, the robot scans the full range
- It identifies the direction with the most open space
- The robot then turns toward that direction and proceeds
- This allows for more natural and efficient movement around obstacles

### Enhanced Serial Commands

Additional commands for the scanning feature:
- `SCAN` - Perform a single full scan
- `SCAN_ON` - Enable automatic periodic scanning
- `SCAN_OFF` - Disable automatic scanning

## Troubleshooting

### Motor Issues
- Check motor connections and polarity
- Ensure motor driver is receiving power
- Verify pin connections match the code configuration

### Display Issues
- Check I2C connections (SCL/SDA)
- Verify display address (default is 0x3C, some use 0x3D)
- Ensure display is receiving 5V power

### Sensor Issues
- Check pin connections
- Ensure sensor is facing forward
- Clean sensor surface if detection is unreliable

### Power Issues
- Motors require separate power from Arduino
- If motors stall when moving, battery may be low
- Avoid powering Arduino through Vin with motor batteries

## Extending Dewwy

### Adding Sensors
The code can be modified to incorporate additional sensors:
- Light sensors for detecting brightness levels
- Line sensors for line-following behavior
- Touch sensors for interaction

### Customizing Behaviors
Edit these functions to customize behavior:
- `executeIdleState()` - Modify idle behavior
- `executeRoamingState()` - Change movement patterns
- `executeAvoidingState()` - Adjust obstacle avoidance strategy
- `executeSleepingState()` - Modify sleep behavior

### Creating New Emotions
To add a new emotion:
1. Add a new entry to the `Emotion` enum
2. Create a new drawing function (e.g., `drawAngryFace()`)
3. Add the new emotion to the display switch statement
4. Update `setEmotion()` function to handle the new emotion

### Using the Servo for Other Functions

The servo motor can be used for additional features:
- Nodding or shaking head for more expressive interactions
- Looking around when curious
- Tracking movement when following objects
- Pointing in the direction it plans to travel

To implement these behaviors, modify the `executeIdleState()` and other state functions to include servo movements that match the current emotion.

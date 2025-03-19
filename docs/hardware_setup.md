# Dewwy Hardware Setup Guide

This guide explains how to assemble the hardware components for your Dewwy pet robot.

## Components Needed

### Core Components
- Raspberry Pi (3B+ or 4)
- Arduino UNO
- Sensor Shield V5 for Arduino
- 128x64 OLED I2C Display
- HC-SR04 Ultrasonic Distance Sensor
- SG90 Servo Motor
- L298N or TB6612FNG Motor Driver
- 2 DC Motors with wheels
- Robot chassis
- USB cable (Type A to Type B) for Arduino
- Battery pack for motors (4-6V)
- Power bank for Raspberry Pi

### Tools
- Screwdrivers (Phillips and flat head)
- Wire cutters and strippers
- Soldering iron and solder (optional)
- Hot glue gun or strong adhesive
- Zip ties

## Assembly Steps

### Step 1: Chassis Assembly

1. Assemble the robot chassis according to its instructions
2. Mount the motors and wheels
3. Place the battery holder on the chassis

### Step 2: Arduino and Sensor Shield

1. Mount the Arduino UNO securely on the chassis
2. Attach the Sensor Shield V5 to the Arduino UNO
3. Ensure pins are aligned properly

### Step 3: Servo and Ultrasonic Sensor

1. Mount the SG90 servo to the front of the chassis
2. Attach the HC-SR04 ultrasonic sensor to the servo horn
3. Connect the servo to the Sensor Shield:
   - Red (power) → 5V
   - Brown (ground) → GND
   - Orange (signal) → Digital Pin 9

4. Connect the HC-SR04 to the Sensor Shield:
   - VCC → 5V
   - Trig → Digital Pin 12
   - Echo → Digital Pin 11
   - GND → GND

### Step 4: Motor Driver

For TB6612FNG motor driver:

1. Connect to the Sensor Shield:
   - VM → External power (4-6V)
   - VCC → 5V
   - GND → GND
   - PWMA → Pin 5
   - AIN1 → Pin 4
   - AIN2 → Pin 3
   - PWMB → Pin 6
   - BIN1 → Pin 7
   - BIN2 → Pin 8
   - STBY → 5V
   
2. Connect motors:
   - A01 → Left motor +
   - A02 → Left motor -
   - B01 → Right motor +
   - B02 → Right motor -

### Step 5: OLED Display

1. Mount the OLED display at the front top of your robot (for visibility)
2. Connect to the Sensor Shield:
   - VCC → 5V
   - GND → GND
   - SCL → SCL (A5)
   - SDA → SDA (A4)

### Step 6: Raspberry Pi Setup

1. Mount the Raspberry Pi on the chassis
2. Connect the Raspberry Pi to the Arduino using USB cable
3. Connect the power bank to the Raspberry Pi

### Step 7: Final Wiring and Securing

1. Double-check all connections
2. Secure loose wires with zip ties
3. Use hot glue to reinforce any loose components

## Testing the Setup

1. Power up the motor battery pack
2. Power up the Raspberry Pi
3. Run the basic test script:
   ```
   cd /path/to/dewwy
   python tools/hardware_test.py
   ```

## Troubleshooting

### Motor Issues
- Check motor connections and polarity
- Ensure motor driver is receiving power
- Verify pin connections match the code configuration

### Display Issues
- Check I2C connections
- Verify display address (default is 0x3C, some use 0x3D)

### Sensor Issues
- Check pin connections
- Ensure sensor is facing forward
- Clean sensor surface if detection is unreliable

### Servo Issues
- Make sure servo is not binding or stalling
- Check power supply - servos can draw significant current

## Wiring Diagram


# Dewwy - Offline Pet Robot

An offline pet robot built using a hybrid Raspberry Pi + Arduino setup. This project simulates the robot's behavior before deploying to hardware.

## Project Overview

Dewwy is designed to:
- Navigate autonomously with obstacle avoidance
- Display emotions on an OLED screen
- Respond to voice commands (offline)
- Learn from interactions

## Components

### Hardware (Simulated)
- Raspberry Pi: Handles AI, voice recognition, display, and Arduino communication
- Arduino: Controls motors and sensors
- HC-SR04 Ultrasonic sensors
- TB6612FNG motor driver
- OLED display

### Software Architecture
- **Arduino Side**: Sensor polling and motor control
- **Raspberry Pi Side**: Robot intelligence, personality, display control
- **Simulation**: Arcade-based visualization and virtual hardware

## Getting Started

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/dewwy.git
cd dewwy
```

2. Install dependencies:
```
pip install -r requirements.txt
```

### Running the Simulation

To run the robot simulation with GUI:
```
python raspberry_pi/main.py
```

For console-only simulation (no GUI):
```
python raspberry_pi/main.py --no-gui
```

To connect to real hardware:
```
python raspberry_pi/main.py --no-simulation
```

### Testing Serial Communication

To test serial communication between Raspberry Pi and Arduino:
```
python tools/serial_tester.py
```

For real hardware:
```
python tools/serial_tester.py --real --port /dev/ttyUSB0
```

## Serial Communication Protocol

Communication between Raspberry Pi and Arduino uses simple text-based commands:

### Commands (Raspberry Pi → Arduino)
- `FWD` - Move forward
- `BCK` - Move backward
- `LFT` - Turn left
- `RGT` - Turn right
- `STP` - Stop movement
- `AUTO` - Switch to autonomous mode
- `CMD` - Switch to command mode
- `PING` - Check connection
- `STATUS` - Request status information

### Responses (Arduino → Raspberry Pi)
- `DIST:123` - Distance reading (123 cm)
- `ACK:XXX` - Acknowledge command XXX
- `MODE:XXX` - Current mode (AUTO or CMD)
- `PONG` - Response to PING
- `ERR:XXX` - Error message

## Tests

Run the tests to verify functionality:
```
python -m pytest tests/
```

## Project Structure

```
dewwy/
├── arduino/                  # Arduino firmware files
│   ├── main_arduino/         # Main Arduino program
│   ├── motor_control/        # Motor control functions
│   ├── sensor_module/        # Sensor interface code
│   ├── diagram.json          # Wokwi circuit diagram
│   └── wokwi.toml            # Wokwi configuration
├── raspberry_pi/             # Raspberry Pi software
│   ├── behavior/             # Robot personality and state machine
│   ├── communication/        # Serial communication with Arduino
│   ├── display/              # OLED display interface
│   └── main.py               # Main entry point
├── simulation/               # Simulation components
│   ├── arcade_simulator.py   # Graphics simulator (Arcade)
│   ├── serial_visualizer.py  # Serial communication visualizer
│   ├── virtual_motors.py     # Motor simulation
│   └── virtual_sensors.py    # Sensor simulation
├── tools/                    # Utility scripts
│   └── serial_tester.py      # Serial communication testing tool
└── tests/                    # Test files
```

## License

[MIT License](LICENSE)

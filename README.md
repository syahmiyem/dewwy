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
- **Simulation**: Tkinter-based visualization and virtual hardware

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

### Tests

Run the tests to verify functionality:
```
python -m pytest tests/
```

## Project Structure

```
dewwy/
├── arduino/                  # Arduino firmware files
│   ├── main_arduino/         
│   ├── motor_control/
│   └── sensor_module/
├── raspberry_pi/             # Raspberry Pi software
│   ├── behavior/             # Robot personality and state machine
│   ├── communication/        # Serial communication with Arduino
│   ├── display/              # OLED display interface
│   └── main.py
├── simulation/               # Simulation components
│   ├── gui_display.py
│   ├── robot_simulator.py
│   ├── virtual_motors.py
│   └── virtual_sensors.py
└── tests/                    # Test files
```

## License

[MIT License](LICENSE)

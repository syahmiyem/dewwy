# Dewwy: Offline Pet Robot

![Dewwy Robot](/docs/images/dewwy_logo.png)

## Overview

Dewwy is an autonomous pet robot built with a hybrid Raspberry Pi and Arduino architecture. It's designed to behave like a real pet with unique personality traits, emotions, and autonomous movement. Unlike cloud-based robots, Dewwy operates completely offline, ensuring privacy and consistent operation without internet dependency.

## Features

### Core Capabilities

- **Autonomous Movement**: Navigate environments with pet-like behaviors
- **Emotional Expression**: Display emotions through an OLED screen
- **Obstacle Avoidance**: Smart detection and avoidance of obstacles
- **Interactive Voice Recognition**: Wake-word activation and command processing
- **Adaptive Personality**: Unique traits that evolve based on interactions

### Emotional Intelligence

Dewwy features a sophisticated emotional system with nine distinct emotional states:
- 😊 **Happy**: When praised or during play
- 😢 **Sad**: When ignored or after negative interactions
- 😐 **Neutral**: Default calm state
- 😃 **Excited**: During energetic activities
- 😴 **Sleepy**: When battery is low or after extended activity
- 🤔 **Curious**: When exploring new environments or objects
- 😨 **Scared**: When encountering obstacles suddenly
- 😋 **Playful**: During interactive sessions
- 😠 **Grumpy**: When repeatedly interrupted or during "bad moods"

Each emotion affects Dewwy's movement patterns, blinking rates, and facial expressions, creating a more lifelike experience.

### Behavior Modes

Dewwy operates in several behavior states:
- **Idle**: Stationary but emotionally responsive
- **Roaming**: Autonomous exploration
- **Avoiding**: Smart obstacle avoidance
- **Sleeping**: Power conservation mode
- **Playing**: Interactive and energetic behavior
- **Searching**: Looking for interaction
- **Startled**: Quick response to sudden stimuli

## Hardware Components

- Raspberry Pi 4 (main controller)
- Arduino (real-time sensor and motor control)
- HC-SR04 Ultrasonic Distance Sensor
- TB6612FNG Dual Motor Driver
- 1.3" OLED Display (128x64 pixels)
- SPH0645 I2S MEMS Microphone (for voice recognition)
- Dual DC Motors with Encoder
- LiPo Battery Pack

## Software Architecture

### Key Components

- **State Machine**: Manages robot behavior states
- **Personality Engine**: Controls emotional responses and preferences
- **Embedded OLED Display Interface**: Renders facial expressions
- **Voice Recognition System**: Processes voice commands offline
- **Obstacle Avoidance Algorithm**: Roomba-inspired detection and navigation
- **Motion Control System**: Manages movement patterns based on state

### Simulation Environment

A comprehensive simulation environment allows you to test and interact with Dewwy:

- **Arcade-based Simulator**: Graphical environment for testing
- **Real-time Animation**: Simulates emotional expressions and movement
- **System Monitoring**: Displays status and performance metrics
- **Input Controls**: Keyboard commands for direct interaction
- **Voice Command Testing**: Simulate voice recognition

## Getting Started

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dewwy.git
   cd dewwy
   ```

2. Install dependencies:
   ```
   # For Raspberry Pi
   pip install -r requirements.txt
   
   # For macOS
   pip install -r requirements_macos.txt
   ```

### Running the Simulator

Launch the simulator to test Dewwy without hardware:

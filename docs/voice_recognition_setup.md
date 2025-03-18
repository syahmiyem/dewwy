# Voice Recognition Setup Guide

This guide explains how to set up and use the voice recognition feature in your Dewwy pet robot.

## Prerequisites

1. Raspberry Pi with fresh Raspbian OS
2. SPH0645 I2S MEMS Microphone
3. Basic wiring components and soldering equipment

## Hardware Setup

### Step 1: Connect the SPH0645 Microphone

Connect the microphone to the Raspberry Pi GPIO pins:

| SPH0645 Pin | Raspberry Pi GPIO |
|-------------|------------------|
| VDD         | 3.3V (Pin 1)     |
| GND         | Ground (Pin 6)   |
| SEL         | Ground (Pin 9)   |
| CLK         | GPIO 18 (Pin 12) |
| DATA        | GPIO 20 (Pin 38) |
| WS/FS       | GPIO 19 (Pin 35) |

### Step 2: Enable I2S on Raspberry Pi

1. Open the config file:
   ```
   sudo nano /boot/config.txt
   ```

2. Add the following line at the end:
   ```
   dtoverlay=rpi-i2s-mems
   ```

3. Save and reboot:
   ```
   sudo reboot
   ```

### Step 3: Test the Microphone

1. Install ALSA utils if not already installed:
   ```
   sudo apt-get update
   sudo apt-get install alsa-utils
   ```

2. Check if the device is recognized:
   ```
   arecord -l
   ```

3. Create a test recording:
   ```
   arecord -D hw:0,0 -c1 -r16000 -f S16_LE -t wav -d 5 test.wav
   ```

4. Play back the recording:
   ```
   aplay test.wav
   ```

## Software Setup

### Step 1: Install Required Packages

Install the dependencies for voice recognition:

```bash
# General audio packages
sudo apt-get install -y libportaudio2 python3-pyaudio

# For PocketSphinx (offline voice recognition)
sudo apt-get install -y swig libpulse-dev

# Install Python packages
pip3 install pyaudio sounddevice webrtcvad pyttsx3 SpeechRecognition pocketsphinx
```

### Step 2: Configure the Robot Software

No additional configuration is needed. The robot software will automatically use the real microphone when run with the `--no-simulation` flag.

## Usage

### Wake Word

The robot responds to the wake word "Dewwy". Say the wake word clearly, then wait for acknowledgment (the robot will look at you).

### Supported Commands

After the wake word is recognized, you can use the following commands:

| Command       | Action                         |
|---------------|--------------------------------|
| "come here"   | Robot moves toward you         |
| "follow me"   | Robot follows your movements   |
| "stop"        | Robot stops moving             |
| "go to sleep" | Robot enters sleep mode        |
| "wake up"     | Robot wakes from sleep mode    |
| "play"        | Robot enters play mode         |
| "sit"         | Robot stops and sits           |
| "turn around" | Robot turns in place           |
| "go forward"  | Robot moves forward            |
| "go backward" | Robot moves backward           |
| "dance"       | Robot performs a dance routine |
| "good boy/girl" | Robot gets happy             |

## Troubleshooting

### No Sound Detected

1. Check the microphone connections
2. Verify I2S is enabled with `lsmod | grep snd_soc_i2s_mems`
3. Check permissions with `ls -l /dev/snd*`
4. Run `alsamixer` and make sure capture is not muted

### Recognition Problems

1. Speak clearly and directly toward the microphone
2. Reduce background noise
3. Try adjusting the recognition sensitivity:
   ```python
   # In raspberry_pi/audio/voice_recognition.py
   self.recognizer.energy_threshold = 300  # Try 400 for less sensitive, 200 for more
   ```

### Audio Library Errors

If you get "ALSA lib pcm.c:8526:(snd_pcm_recover) underrun occurred" warnings, they can be safely ignored.

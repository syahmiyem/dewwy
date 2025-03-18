#!/usr/bin/env python3
"""
Installation helper for Dewwy Pet Robot
This script detects your platform and installs the appropriate dependencies.
"""

import os
import sys
import platform
import subprocess
import time

def print_step(message):
    """Print a step message with formatting"""
    print(f"\n\033[1;34m=== {message} ===\033[0m")
    time.sleep(0.5)

def run_command(command, error_message=None):
    """Run a shell command and handle errors"""
    try:
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        if error_message:
            print(f"\033[1;31mError: {error_message}\033[0m")
        print(f"Command failed with exit code {e.returncode}")
        return False

def detect_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    
    if system == "darwin":
        # Check if we're on Apple Silicon
        machine = platform.machine().lower()
        if machine in ["arm64", "aarch64"]:
            return "macos_arm"
        else:
            return "macos_intel"
    elif system == "linux":
        # Check for Raspberry Pi
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            if 'BCM' in cpuinfo:  # Broadcom chip indicates Raspberry Pi
                return "raspberry_pi"
            else:
                return "linux"
        except:
            return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

def install_macos_dependencies():
    """Install dependencies for macOS"""
    print_step("Installing macOS dependencies")
    
    # Check if Homebrew is installed
    if not run_command(["which", "brew"], "Homebrew not found"):
        print("Installing Homebrew...")
        brew_install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        run_command(brew_install_cmd.split(), "Failed to install Homebrew")
    
    # Install dependencies using Homebrew
    run_command(["brew", "install", "portaudio", "swig", "libsndfile"], 
                "Failed to install system dependencies")
    
    # Try installing requirements with regular pip first
    if run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        print("\033[1;32mSuccessfully installed dependencies!\033[0m")
    else:
        # If that fails, try the macOS specific requirements
        print("Trying macOS specific requirements...")
        run_command([sys.executable, "-m", "pip", "install", "-r", "requirements_macos.txt"], 
                   "Failed to install Python dependencies")
        
        # Try installing pyaudio with --no-portaudio flag
        print("Trying alternate PyAudio installation...")
        run_command([sys.executable, "-m", "pip", "install", "--global-option=--no-portaudio", "pyaudio"],
                   "Failed to install PyAudio, but that's okay, using fallback")

def install_raspberry_pi_dependencies():
    """Install dependencies for Raspberry Pi"""
    print_step("Installing Raspberry Pi dependencies")
    
    # Update package lists
    run_command(["sudo", "apt", "update"], "Failed to update package lists")
    
    # Install system dependencies
    run_command(["sudo", "apt", "install", "-y", 
                "portaudio19-dev", "libsndfile1", "swig", "libpulse-dev", 
                "python3-pyaudio", "python3-numpy"], 
                "Failed to install system dependencies")
    
    # Install Python dependencies
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
               "Failed to install Python dependencies")
    
    # Enable I2S for the microphone
    print("Enabling I2S for MEMS microphone...")
    with open("/boot/config.txt", "r") as f:
        config = f.read()
        
    if "dtparam=i2s=on" not in config and "dtoverlay=rpi-i2s-mems" not in config:
        try:
            with open("/boot/config.txt", "a") as f:
                f.write("\n# Enable I2S for MEMS microphone\n")
                f.write("dtparam=i2s=on\n")
                f.write("dtoverlay=rpi-i2s-mems\n")
            print("Added I2S configuration. Please reboot for changes to take effect.")
        except:
            print("Could not modify /boot/config.txt. Please add these lines manually:")
            print("dtparam=i2s=on")
            print("dtoverlay=rpi-i2s-mems")

def main():
    """Main installation function"""
    print("Dewwy Pet Robot Installation Helper")
    print("----------------------------------")
    
    platform_type = detect_platform()
    print(f"Detected platform: {platform_type}")
    
    if platform_type.startswith("macos"):
        install_macos_dependencies()
    elif platform_type == "raspberry_pi":
        install_raspberry_pi_dependencies()
    elif platform_type == "linux":
        print("Regular Linux detected. Using Raspberry Pi installation method...")
        install_raspberry_pi_dependencies()
    elif platform_type == "windows":
        print("Windows is not fully supported for the full robot functionality.")
        print("However, the simulation should work.")
        print("Please install the dependencies manually from requirements.txt")
    else:
        print("Unknown platform. Please install dependencies manually.")
    
    print("\nTo run the robot simulator:")
    print("python raspberry_pi/main.py")
    
    print("\nTo run the robot with hardware:")
    print("python raspberry_pi/main.py --no-simulation")

if __name__ == "__main__":
    main()

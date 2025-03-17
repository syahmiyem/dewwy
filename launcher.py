#!/usr/bin/env python3
"""
Main launcher for the robot application.
This script uses subprocess to fully isolate the GUI process.
"""

import argparse
import subprocess
import sys
import os

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pet Robot Control System")
    parser.add_argument("--no-simulation", action="store_true", 
                        help="Connect to real hardware instead of simulation")
    parser.add_argument("--no-gui", action="store_true",
                        help="Run without GUI (console mode)")
    args = parser.parse_args()
    
    # Build command with arguments
    cmd = [sys.executable, "raspberry_pi/main.py"]
    if args.no_simulation:
        cmd.append("--no-simulation")
    if args.no_gui:
        cmd.append("--no-gui")
    
    # Run command
    print(f"Launching: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()

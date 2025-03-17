#!/usr/bin/env python3
"""
Serial Communication Tester

This tool helps test the serial communication between the Raspberry Pi
and Arduino components, either with real hardware or in simulation.
"""

import sys
import os
import time
import threading
import argparse

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.virtual_serial import VirtualArduino
from raspberry_pi.communication.serial_handler import SerialHandler

class SerialTester:
    def __init__(self, simulation=True, port=None):
        self.simulation = simulation
        self.port = port
        self.running = True
        
        if simulation:
            print(f"Starting in simulation mode")
            self.arduino = VirtualArduino()
            self.arduino.start()
            self.pi_serial = SerialHandler(simulation=True)
        else:
            if not port:
                print("Error: Real hardware mode requires a serial port")
                sys.exit(1)
            print(f"Connecting to real hardware on port {port}")
            self.arduino = None  # Arduino should be connected for real hardware
            self.pi_serial = SerialHandler(port=port, simulation=False)
        
        # Start receive thread
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
    
    def _receive_loop(self):
        """Loop to receive and display messages"""
        while self.running:
            message = self.pi_serial.get_next_message(block=False)
            if message:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] ARDUINO → PI: {message}")
            
            time.sleep(0.1)
    
    def send_command(self, command):
        """Send a command to the Arduino"""
        if command.upper() in ["FWD", "BCK", "LFT", "RGT", "STP"]:
            print(f"Sending command: {command}")
            self.pi_serial.send_command(command)
        else:
            print(f"Unknown command: {command}")
            print("Valid commands: FWD, BCK, LFT, RGT, STP")
    
    def run_interactive(self):
        """Run in interactive mode, accepting user commands"""
        print("===== Serial Communication Tester =====")
        print("Type commands to send to Arduino, or 'exit' to quit")
        print("Valid commands: FWD, BCK, LFT, RGT, STP")
        print("======================================")
        
        try:
            while self.running:
                command = input("> ").strip()
                if command.lower() == 'exit':
                    break
                elif command:
                    self.send_command(command)
        
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        self.running = False
        if self.simulation and self.arduino:
            self.arduino.stop()

def main():
    parser = argparse.ArgumentParser(description="Test serial communication with Arduino")
    parser.add_argument("--real", action="store_true", help="Use real hardware instead of simulation")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port for real hardware mode")
    args = parser.parse_args()
    
    tester = SerialTester(simulation=not args.real, port=args.port)
    tester.run_interactive()

if __name__ == "__main__":
    main()

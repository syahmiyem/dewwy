#!/usr/bin/env python3
"""
Voice Recognition Test Tool

This script tests the voice recognition system in isolation.
It listens for commands and prints them to the console.
"""

import sys
import os
import time
import signal

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from raspberry_pi.audio.microphone_interface import MicrophoneInterface
from raspberry_pi.audio.voice_recognition import VoiceRecognizer

class VoiceRecognitionTester:
    def __init__(self, simulation=True):
        self.simulation = simulation
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Initializing voice recognition test...")
        
        # Initialize audio components
        self.microphone = MicrophoneInterface(simulation=simulation)
        self.voice_recognizer = VoiceRecognizer(
            microphone=self.microphone, 
            simulation=simulation
        )
    
    def start(self):
        """Start the voice recognition system and enter main loop"""
        print("Starting microphone...")
        self.microphone.start_listening()
        
        print("Starting voice recognition...")
        self.voice_recognizer.start()
        
        print("\n=== Voice Recognition Test ===")
        print("Say the wake word 'Dewwy' followed by a command.")
        if self.simulation:
            print("SIMULATION MODE: Commands are randomly generated.")
        print("Press Ctrl+C to exit.")
        print("==============================\n")
        
        # Main loop - check for commands
        try:
            while self.running:
                command = self.voice_recognizer.get_next_command(block=False)
                if command:
                    print(f"Command detected: '{command}'")
                    self._process_command(command)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.shutdown()
    
    def _process_command(self, command):
        """Process a recognized command"""
        # This would connect to robot actions
        # For now, just print confirmation
        print(f"Processing command: {command}...")
        time.sleep(1)
        print("Command executed!")
    
    def signal_handler(self, sig, frame):
        """Handle system signals for clean shutdown"""
        print("\nShutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of all components"""
        if hasattr(self, 'voice_recognizer'):
            print("Stopping voice recognition...")
            self.voice_recognizer.stop()
        
        if hasattr(self, 'microphone'):
            print("Stopping microphone...")
            self.microphone.shutdown()
        
        self.running = False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test voice recognition system")
    parser.add_argument("--real-hardware", action="store_true", 
                        help="Use real hardware instead of simulation")
    args = parser.parse_args()
    
    tester = VoiceRecognitionTester(simulation=not args.real_hardware)
    tester.start()

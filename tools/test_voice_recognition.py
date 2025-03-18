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

# Try to import the microphone interface first
try:
    from raspberry_pi.audio.microphone_interface import MicrophoneInterface
except ImportError:
    # Fall back to simple implementation
    try:
        from raspberry_pi.audio.fallback_recognition import SimpleMicrophoneInterface as MicrophoneInterface
    except ImportError:
        print("Error: Could not import microphone interface modules")
        sys.exit(1)

# Then import the voice recognizer
try:
    from raspberry_pi.audio.voice_recognition import VoiceRecognizer
except ImportError:
    print("Error: Could not import voice recognition module")
    sys.exit(1)

class VoiceRecognitionTester:
    def __init__(self, simulation=True, force_simple_mode=False):
        self.simulation = simulation
        self.force_simple_mode = force_simple_mode
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("Initializing voice recognition test...")
        
        # Initialize audio components
        self.microphone = MicrophoneInterface(simulation=simulation)
        self.voice_recognizer = VoiceRecognizer(
            microphone=self.microphone, 
            simulation=simulation,
            force_simple_mode=force_simple_mode
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
        if self.force_simple_mode:
            print("SIMPLE MODE: Using simplified voice recognition (no advanced features).")
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
    parser.add_argument("--simple", action="store_true",
                        help="Force simple mode even if advanced modules are available")
    args = parser.parse_args()
    
    if args.simple:
        print("Forcing simple mode")
    
    tester = VoiceRecognitionTester(
        simulation=not args.real_hardware,
        force_simple_mode=args.simple
    )
    tester.start()

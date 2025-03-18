"""
Fallback voice recognition without requiring PyAudio or PocketSphinx.
This uses a simulated recognizer that doesn't depend on hardware or
difficult-to-install libraries.
"""

import time
import threading
import queue
import random
import numpy as np

class SimpleMicrophoneInterface:
    """Simple fallback microphone implementation that doesn't require PyAudio"""
    
    def __init__(self, simulation=True):
        self.simulation = True  # Always simulation mode
        self.running = False
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        self.channels = 1
        
    def start_listening(self):
        """Start the audio capture thread"""
        if self.running:
            return
            
        self.running = True
        self.listen_thread = threading.Thread(target=self._simulate_audio)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("Simple microphone simulation started")
        
    def _simulate_audio(self):
        """Generate fake audio data"""
        while self.running:
            # Generate random noise once in a while
            if random.random() < 0.05:
                data = np.random.normal(0, 0.1, (1600, self.channels))
            else:
                data = np.zeros((1600, self.channels))
                
            self.audio_queue.put(data)
            time.sleep(0.1)
    
    def get_audio_chunk(self, timeout=0.1):
        """Get a chunk of audio data"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_listening(self):
        """Stop the audio capture thread"""
        self.running = False
        
    def shutdown(self):
        """Clean shutdown"""
        self.stop_listening()


class SimpleVoiceRecognizer:
    """Simple fallback voice recognizer that doesn't require PocketSphinx"""
    
    def __init__(self, microphone=None, simulation=True):
        self.microphone = microphone
        self.simulation = True  # Always simulation mode
        self.running = False
        self.command_queue = queue.Queue()
        self.wake_word = "dewwy"
        
        # Define known commands
        self.command_keywords = {
            "come here": "come",
            "follow me": "follow",
            "stop": "stop",
            "go to sleep": "sleep",
            "wake up": "wake",
            "play": "play",
            "good boy": "praise",
            "good girl": "praise",
            "sit": "sit",
            "turn around": "turn",
            "go forward": "forward",
            "go backward": "backward",
            "dance": "dance"
        }
    
    def start(self):
        """Start the voice recognition system"""
        if not self.microphone:
            print("Error: No microphone interface provided")
            return False
            
        # Start the microphone
        if not hasattr(self.microphone, 'running') or not self.microphone.running:
            self.microphone.start_listening()
            
        # Start the recognition thread
        self.running = True
        self.recognition_thread = threading.Thread(target=self._simulate_recognition)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        print("Simple voice recognition simulation started")
        return True
    
    def _simulate_recognition(self):
        """Simulate voice recognition by randomly generating commands"""
        while self.running:
            if random.random() < 0.10:  # 10% chance of generating a command
                # Randomly select a command
                command = random.choice(list(self.command_keywords.values()))
                print(f"[SIMULATED] Command recognized: '{command}'")
                self.command_queue.put(command)
            time.sleep(3)  # Check every 3 seconds
    
    def get_next_command(self, block=False, timeout=None):
        """Get the next recognized command"""
        try:
            return self.command_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop the voice recognition system"""
        self.running = False

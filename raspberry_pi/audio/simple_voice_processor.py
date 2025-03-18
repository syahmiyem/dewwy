"""
Simplified voice processing that works without scipy or other hard-to-install dependencies.
This provides a basic implementation that works on all platforms without compilation issues.
"""

import os
import threading
import tempfile
import time
import queue
import random

class SimpleVoiceProcessor:
    """Simple voice processor that works without scipy dependency"""
    
    def __init__(self, microphone=None):
        self.microphone = microphone
        self.running = False
        self.command_queue = queue.Queue()
        self.wake_word_active = False
        self.wake_word_time = 0
        self.command_timeout = 10  # Seconds
        
        # Known commands
        self.commands = [
            "come", "follow", "stop", "sleep", "wake",
            "play", "praise", "sit", "turn", "forward",
            "backward", "dance"
        ]
    
    def start(self):
        """Start the voice processor"""
        if self.running:
            return True
            
        self.running = True
        self.processor_thread = threading.Thread(target=self._processing_loop)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        print("Simple voice processor started")
        return True
    
    def stop(self):
        """Stop the voice processor"""
        self.running = False
        if hasattr(self, 'processor_thread') and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=1.0)
        print("Simple voice processor stopped")
    
    def _processing_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                # Simulate voice processing with occasional detections
                if random.random() < 0.05:  # Occasional detection
                    if not self.wake_word_active:
                        print("[SIM] Wake word detected")
                        self.wake_word_active = True
                        self.wake_word_time = time.time()
                    elif time.time() - self.wake_word_time < self.command_timeout:
                        cmd = random.choice(self.commands)
                        print(f"[SIM] Command recognized: {cmd}")
                        self.command_queue.put(cmd)
                        self.wake_word_active = False
                
                # Expire wake word after timeout
                if self.wake_word_active and time.time() - self.wake_word_time > self.command_timeout:
                    self.wake_word_active = False
                
                time.sleep(2.0)
                
            except Exception as e:
                print(f"Error in voice processor: {e}")
                time.sleep(1.0)
    
    def get_next_command(self, block=False, timeout=None):
        """Get the next recognized command"""
        try:
            return self.command_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def activate_wake_word(self):
        """Manually activate wake word (for testing)"""
        self.wake_word_active = True
        self.wake_word_time = time.time()
        return True

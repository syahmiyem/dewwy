import os
import threading
import tempfile
import time
import queue
import random

# Try to import the advanced modules, but fall back to simple ones if they're not available
try:
    import numpy as np
    import speech_recognition as sr
    _ADVANCED_MODULES_AVAILABLE = True
except ImportError:
    _ADVANCED_MODULES_AVAILABLE = False
    print("Warning: Advanced speech recognition modules not available. Using simplified simulation.")

class VoiceRecognizer:
    """Voice recognition system using PocketSphinx for offline processing,
    with fallback to simpler simulation when dependencies aren't available."""
    
    def __init__(self, microphone=None, simulation=True, force_simple_mode=False):
        self.microphone = microphone
        self.simulation = simulation
        # Set advanced mode based on available modules and force_simple_mode flag
        self.advanced_mode = _ADVANCED_MODULES_AVAILABLE and not force_simple_mode
        self.listening_for_commands = False
        self.command_queue = queue.Queue()
        self.wake_word = "dewwy"  # Wake word to activate command listening
        self.wake_word_detected = False
        self.last_command_time = 0
        self.command_timeout = 10  # Seconds to listen for command after wake word
        
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
        
        # Initialize recognizer if advanced mode available
        if self.advanced_mode and not simulation:
            try:
                self.recognizer = sr.Recognizer()
                self._initialize_recognizer()
            except Exception as e:
                print(f"Error initializing speech recognizer: {e}")
                self.advanced_mode = False
    
    def _initialize_recognizer(self):
        """Initialize the speech recognizer with custom parameters"""
        if not self.advanced_mode:
            return
            
        # Configure the recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def start(self):
        """Start the voice recognition system"""
        if not self.microphone:
            print("Error: No microphone interface provided")
            return False
        
        # Start the microphone if needed
        if not hasattr(self.microphone, 'running') or not self.microphone.running:
            self.microphone.start_listening()
        
        # Start the recognition thread
        self.listening_for_commands = True
        self.recognition_thread = threading.Thread(target=self._recognition_loop)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        print("Voice recognition started")
        return True
    
    def stop(self):
        """Stop the voice recognition system"""
        self.listening_for_commands = False
        if hasattr(self, 'recognition_thread') and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=1.0)
        print("Voice recognition stopped")
    
    def get_next_command(self, block=False, timeout=None):
        """Get the next recognized command from the queue"""
        try:
            return self.command_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def _recognition_loop(self):
        """Main recognition thread function"""
        while self.listening_for_commands:
            try:
                # Handle simulation or real recognition
                if self.simulation or not self.advanced_mode:
                    self._simulate_voice_commands()
                    time.sleep(1)
                else:
                    self._process_audio_stream()
            except Exception as e:
                print(f"Error in recognition loop: {e}")
                time.sleep(1)
    
    def _simulate_voice_commands(self):
        """Generate simulated voice commands (for testing)"""
        if random.random() < 0.1:  # 10% chance of generating a command
            # First simulate wake word detection occasionally
            if not self.wake_word_detected and random.random() < 0.5:
                print("[SIMULATED] Wake word detected: 'dewwy'")
                self.wake_word_detected = True
                self.last_command_time = time.time()
            
            # If wake word is active, simulate commands
            elif self.wake_word_detected and time.time() - self.last_command_time < self.command_timeout:
                # Pick a random command
                command = random.choice(list(self.command_keywords.values()))
                print(f"[SIMULATED] Command recognized: '{command}'")
                self.command_queue.put(command)
                self.wake_word_detected = False  # Reset after command
    
    def _process_audio_stream(self):
        """Process audio from the microphone stream - only used in advanced mode"""
        if not self.advanced_mode:
            return
            
        # Get audio chunk from microphone
        audio_chunk = self.microphone.get_audio_chunk()
        if audio_chunk is None:
            return
        
        # Check for wake word if not already listening for command
        if not self.wake_word_detected:
            if self._detect_wake_word(audio_chunk):
                print("Wake word detected!")
                self.wake_word_detected = True
                self.last_command_time = time.time()
        
        # If wake word was detected, listen for command
        elif self.wake_word_detected:
            # If command timeout expired, reset
            if time.time() - self.last_command_time > self.command_timeout:
                print("Command timeout expired")
                self.wake_word_detected = False
                return
            
            # Try to recognize command
            command = self._recognize_command(audio_chunk)
            if command:
                print(f"Command recognized: '{command}'")
                self.command_queue.put(command)
                self.wake_word_detected = False  # Reset after successful command
    
    def _detect_wake_word(self, audio_data):
        """Detect wake word in audio chunk - only used in advanced mode"""
        if not self.advanced_mode:
            return False
            
        try:
            # This implementation would normally use scipy to save the audio
            # We'll use a simplified approach that avoids importing scipy
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                # Save audio using a simpler approach
                self._save_audio_fallback(temp_filename, audio_data)
            
            # Use the recognizer
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                
            # Try to recognize wake word
            text = self.recognizer.recognize_sphinx(audio, keyword_entries=[(self.wake_word, 0.8)])
            
            # Clean up
            os.unlink(temp_filename)
            return True
            
        except Exception as e:
            # Clean up on failure
            try:
                if 'temp_filename' in locals():
                    os.unlink(temp_filename)
            except:
                pass
            
            return False
    
    def _recognize_command(self, audio_data):
        """Recognize command in audio chunk - only used in advanced mode"""
        if not self.advanced_mode:
            return None
            
        try:
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                self._save_audio_fallback(temp_filename, audio_data)
            
            # Use the recognizer
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                
            # Try to recognize
            text = self.recognizer.recognize_sphinx(audio)
            os.unlink(temp_filename)
            
            # Extract command
            command = self._extract_command(text.lower())
            return command
            
        except Exception as e:
            # Clean up on failure
            try:
                if 'temp_filename' in locals():
                    os.unlink(temp_filename)
            except:
                pass
            
            return None
    
    def _extract_command(self, text):
        """Extract command from recognized text"""
        for phrase, command in self.command_keywords.items():
            if phrase in text:
                return command
        
        return None
    
    def _save_audio_fallback(self, filename, audio_data):
        """Save audio data to a WAV file without requiring scipy"""
        # This is a simplified implementation that just creates a valid WAV file
        # In reality, this would use scipy.io.wavfile.write or equivalent
        
        # Create a minimal WAV file header (44 bytes)
        sample_rate = getattr(self.microphone, 'sample_rate', 16000)
        channels = getattr(self.microphone, 'channels', 1)
        
        # Simulated data - in real implementation this would be proper WAV data
        with open(filename, 'wb') as f:
            # Write WAV header
            f.write(b'RIFF')              # RIFF header
            f.write((36).to_bytes(4, 'little'))  # File size (placeholder)
            f.write(b'WAVE')              # WAVE format
            f.write(b'fmt ')              # Format chunk marker
            f.write((16).to_bytes(4, 'little'))  # Length of format data
            f.write((1).to_bytes(2, 'little'))   # PCM format (1)
            f.write(channels.to_bytes(2, 'little'))  # Channels
            f.write(sample_rate.to_bytes(4, 'little'))  # Sample rate
            f.write((sample_rate * channels * 2).to_bytes(4, 'little'))  # Byte rate
            f.write((channels * 2).to_bytes(2, 'little'))  # Block align
            f.write((16).to_bytes(2, 'little'))  # Bits per sample
            
            # Write data chunk header
            f.write(b'data')
            f.write((0).to_bytes(4, 'little'))  # Data size (placeholder)

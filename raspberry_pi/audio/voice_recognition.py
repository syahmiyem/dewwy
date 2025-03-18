import os
import threading
import tempfile
import time
import numpy as np
from pathlib import Path
import queue
import speech_recognition as sr

class VoiceRecognizer:
    """Voice recognition system using PocketSphinx for offline processing"""
    
    def __init__(self, microphone=None, simulation=True):
        self.microphone = microphone
        self.simulation = simulation
        self.recognizer = sr.Recognizer()
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
        
        # Initialize and adapt the recognizer for our specific use case
        # (For real hardware, we would adapt the acoustic model here)
        if not simulation:
            self._initialize_recognizer()
    
    def _initialize_recognizer(self):
        """Initialize the speech recognizer with custom parameters"""
        # The recognizer uses PocketSphinx by default for offline recognition
        # We can adjust its parameters for our specific use case
        self.recognizer.energy_threshold = 300  # Increase if not detecting speech
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Shorter pause is End of phrase
        
        # A real implementation would include acoustic model adaptation
        # But this is beyond the scope of this implementation
    
    def start(self):
        """Start the voice recognition system"""
        if not self.microphone:
            print("Error: No microphone interface provided")
            return False
        
        # Start the microphone
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
                if self.simulation:
                    # In simulation mode, occasionally inject fake commands
                    self._simulate_voice_commands()
                    time.sleep(2)  # Only check periodically in simulation
                else:
                    # Real recognition with microphone
                    self._process_audio_stream()
            except Exception as e:
                print(f"Error in recognition loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)  # Wait before retrying
    
    def _simulate_voice_commands(self):
        """Generate simulated voice commands (for testing)"""
        import random
        
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
        """Process audio from the microphone stream"""
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
                # Play a sound or visual indication that wake word was recognized
        
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
        """Detect wake word in audio chunk"""
        # For a real implementation, this would use a specialized wake word detector
        # For this example, we'll use the general speech recognition and check for wake word
        try:
            # Convert numpy array to audio data format
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                import scipy.io.wavfile as wavfile
                wavfile.write(temp_filename, self.microphone.sample_rate, audio_data)
            
            # Use the recognizer on the temporary file
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                
            # Try to recognize with specified wake word as keywords
            text = self.recognizer.recognize_sphinx(audio, keyword_entries=[(self.wake_word, 0.8)])
            
            # Clean up the temporary file
            os.unlink(temp_filename)
            
            # If we got here, the wake word was detected
            return True
            
        except sr.UnknownValueError:
            # Wake word not found
            pass
        except sr.RequestError as e:
            print(f"Recognition error: {e}")
        except Exception as e:
            print(f"Error detecting wake word: {e}")
        
        # Clean up on failure
        try:
            if 'temp_filename' in locals():
                os.unlink(temp_filename)
        except:
            pass
        
        return False
    
    def _recognize_command(self, audio_data):
        """Recognize command in audio chunk using PocketSphinx"""
        try:
            # Convert numpy array to audio data format
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
                import scipy.io.wavfile as wavfile
                wavfile.write(temp_filename, self.microphone.sample_rate, audio_data)
            
            # Use the recognizer on the temporary file
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                
            # Try to recognize with general speech recognition
            text = self.recognizer.recognize_sphinx(audio)
            os.unlink(temp_filename)
            
            # Check if the recognized text contains any of our commands
            command = self._extract_command(text.lower())
            return command
            
        except sr.UnknownValueError:
            # No speech recognized
            pass
        except sr.RequestError as e:
            print(f"Recognition error: {e}")
        except Exception as e:
            print(f"Error recognizing command: {e}")
        
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

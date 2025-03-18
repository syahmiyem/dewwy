import time
import threading
import queue
import random
import numpy as np
import sounddevice as sd
import webrtcvad  # Voice Activity Detection

class MicrophoneInterface:
    """Interface for SPH0645 I2S MEMS Microphone
    
    Hardware connections:
    - WS (Word Select) -> GPIO 19
    - SCK (Serial Clock) -> GPIO 18
    - SD (Serial Data) -> GPIO 20
    - L/R (Left/Right Channel) -> GND (use left channel)
    - GND -> GND
    - VDD -> 3.3V
    
    Requires you add to /boot/config.txt:
    dtoverlay=rpi-i2s-mems
    """
    
    def __init__(self, simulation=True, sample_rate=16000, channels=1):
        self.simulation = simulation
        self.sample_rate = sample_rate
        self.channels = channels
        self.running = False
        self.audio_queue = queue.Queue()
        self.recording = False
        self.vad = webrtcvad.Vad(3)  # Aggressiveness level (0-3)
        
        # Initial configuration
        if not simulation:
            # Configure the I2S interface
            try:
                # Check if I2S module is loaded
                import subprocess
                result = subprocess.run(['lsmod'], stdout=subprocess.PIPE)
                if 'snd_soc_i2s_mems' not in result.stdout.decode('utf-8'):
                    print("Warning: I2S MEMS module not detected. Make sure dtoverlay=rpi-i2s-mems is in /boot/config.txt")
            except Exception as e:
                print(f"Error checking I2S module: {e}")
        else:
            print("Initializing microphone in simulation mode")
    
    def start_listening(self):
        """Start the audio capture thread"""
        if self.running:
            return
        
        self.running = True
        self.listen_thread = threading.Thread(target=self._audio_capture_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("Microphone listening started")
    
    def stop_listening(self):
        """Stop the audio capture thread"""
        self.running = False
        if hasattr(self, 'listen_thread') and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        print("Microphone listening stopped")
    
    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.recorded_frames = []
    
    def stop_recording(self):
        """Stop recording and return the recorded audio"""
        self.recording = False
        if self.recorded_frames:
            # Combine all frames
            audio_data = np.concatenate(self.recorded_frames)
            self.recorded_frames = []
            return audio_data
        return np.array([])
    
    def get_audio_chunk(self, timeout=0.1):
        """Get the next chunk of audio from the queue"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _audio_capture_loop(self):
        """Main audio capture thread function"""
        # Frame size must be one of: 10, 20, or 30 ms for VAD
        frame_duration = 30  # ms
        frame_size = int(self.sample_rate * frame_duration / 1000)
        
        def audio_callback(indata, frames, time_info, status):
            """Callback for sounddevice"""
            if status:
                print(f"Audio status: {status}")
            
            # Convert to the right format for VAD
            audio_data = indata.copy()
            
            # Put the audio data in the queue
            self.audio_queue.put(audio_data)
            
            # If recording, save the frame
            if self.recording:
                self.recorded_frames.append(audio_data)
                
            # Check if speech is detected (for real hardware)
            if not self.simulation and len(audio_data) >= frame_size:
                audio_frame = audio_data[:frame_size].tobytes()
                try:
                    is_speech = self.vad.is_speech(audio_frame, self.sample_rate)
                    if is_speech:
                        # Speech detected, could trigger an event
                        pass
                except Exception as e:
                    # VAD can be picky about frame sizes
                    pass
        
        try:
            if self.simulation:
                # In simulation mode, generate silent audio with occasional noise
                while self.running:
                    # Create simulated audio data (mostly silence with occasional noise)
                    if random.random() < 0.05:  # Occasional noise
                        audio_data = np.random.normal(0, 0.1, (frame_size, self.channels))
                    else:
                        audio_data = np.zeros((frame_size, self.channels))
                    
                    # Process the simulated audio
                    audio_callback(audio_data, frame_size, None, None)
                    time.sleep(frame_duration / 1000)  # Sleep for the frame duration
            else:
                # Real hardware mode - use sounddevice to capture audio
                with sd.InputStream(samplerate=self.sample_rate,
                                    channels=self.channels,
                                    callback=audio_callback,
                                    blocksize=frame_size):
                    print(f"Listening on audio device with {self.sample_rate}Hz, {self.channels} channels")
                    
                    # Keep the stream open until stopped
                    while self.running:
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"Error in audio capture: {e}")
            import traceback
            traceback.print_exc()
            self.running = False

    def shutdown(self):
        """Clean shutdown of the microphone interface"""
        self.stop_listening()

import time
import threading

# Simulated imports (would be real on hardware)
# from luma.core.interface.serial import i2c
# from luma.core.render import canvas
# from luma.oled.device import ssd1306
# from PIL import Image, ImageDraw, ImageFont

class OLEDDisplay:
    def __init__(self, width=128, height=64, simulation=True):
        self.width = width
        self.height = height
        self.simulation = simulation
        self.current_emotion = "neutral"
        self.status_message = "Online"
        self.running = True
        
        # Animation properties
        self.animation_frame = 0  # Current frame in animation sequence
        self.animation_speed = 5  # Frames per second
        self.last_frame_time = time.time()
        self.animation_frames = {}  # Will store frames for each emotion
        
        # Initialize animation frames for different emotions
        self._init_animation_frames()
        
        if not simulation:
            # Setup for real hardware
            # self.serial = i2c(port=1, address=0x3C)
            # self.device = ssd1306(self.serial, width=width, height=height)
            # self.font = ImageFont.load_default()
            pass
        else:
            # For simulation, we'll just print to console
            print("OLED Display Initialized (Simulation Mode)")
        
        # Start the display update thread
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _init_animation_frames(self):
        """Initialize animation sequences for each emotion"""
        # Format: self.animation_frames[emotion] = [frame1, frame2, ...]
        # Each frame is a description of what to draw in that frame
        # This would be more complex on real hardware with actual image data
        
        # Neutral - occasional blinks
        self.animation_frames["neutral"] = [
            {"eyes": "open", "mouth": "flat"},        # Regular face
            {"eyes": "open", "mouth": "flat"},        # Regular face
            {"eyes": "open", "mouth": "flat"},        # Regular face
            {"eyes": "half_closed", "mouth": "flat"}, # Starting to blink
            {"eyes": "closed", "mouth": "flat"},      # Blink
            {"eyes": "half_closed", "mouth": "flat"}, # Ending blink
            {"eyes": "open", "mouth": "flat"},        # Back to regular
            {"eyes": "open", "mouth": "flat"}         # Regular face
        ]
        
        # Happy - blinking and smiling
        self.animation_frames["happy"] = [
            {"eyes": "open", "mouth": "smile_1"},
            {"eyes": "open", "mouth": "smile_2"},
            {"eyes": "open", "mouth": "smile_1"},
            {"eyes": "half_closed", "mouth": "smile_1"},
            {"eyes": "closed", "mouth": "smile_1"},
            {"eyes": "half_closed", "mouth": "smile_1"},
            {"eyes": "open", "mouth": "smile_2"}
        ]
        
        # Sad - occasional blinks, downturned mouth
        self.animation_frames["sad"] = [
            {"eyes": "droopy", "mouth": "frown_1"},
            {"eyes": "droopy", "mouth": "frown_1"},
            {"eyes": "half_closed", "mouth": "frown_1"},
            {"eyes": "closed", "mouth": "frown_1"},
            {"eyes": "droopy", "mouth": "frown_1"},
            {"eyes": "droopy", "mouth": "frown_2"}
        ]
        
        # Sleepy - heavy blinking, yawning
        self.animation_frames["sleepy"] = [
            {"eyes": "half_closed", "mouth": "flat", "zzz": False},
            {"eyes": "mostly_closed", "mouth": "flat", "zzz": False},
            {"eyes": "closed", "mouth": "flat", "zzz": False},
            {"eyes": "mostly_closed", "mouth": "small_o", "zzz": True},
            {"eyes": "closed", "mouth": "yawn", "zzz": True},
            {"eyes": "closed", "mouth": "yawn", "zzz": True},
            {"eyes": "mostly_closed", "mouth": "small_o", "zzz": True}
        ]
        
        # Excited - wide eyes, big smile, bouncy
        self.animation_frames["excited"] = [
            {"eyes": "wide", "mouth": "big_smile", "bounce": 0},
            {"eyes": "wide", "mouth": "big_smile", "bounce": 2},
            {"eyes": "wide", "mouth": "big_smile", "bounce": 0},
            {"eyes": "wide", "mouth": "big_smile", "bounce": -2},
            {"eyes": "blink", "mouth": "big_smile", "bounce": 0},
            {"eyes": "wide", "mouth": "big_smile", "bounce": 2}
        ]
        
        # Add more emotion animations...
        self.animation_frames["curious"] = [
            {"eyes": "open", "eyebrow": "raised", "mouth": "small_o"},
            {"eyes": "open", "eyebrow": "raised", "mouth": "small_o", "head_tilt": 5},
            {"eyes": "open", "eyebrow": "raised", "mouth": "small_o", "head_tilt": -5},
            {"eyes": "squint", "eyebrow": "raised", "mouth": "small_o"},
            {"eyes": "open", "eyebrow": "raised", "mouth": "small_o"}
        ]
        
        self.animation_frames["scared"] = [
            {"eyes": "wide", "mouth": "small_o", "trembling": 0},
            {"eyes": "wide", "mouth": "small_o", "trembling": 1},
            {"eyes": "wide", "mouth": "small_o", "trembling": -1},
            {"eyes": "wide", "mouth": "small_o", "trembling": 2},
            {"eyes": "wide", "mouth": "small_o", "trembling": -2}
        ]
        
        self.animation_frames["playful"] = [
            {"eyes": "wink", "mouth": "smile_1"},
            {"eyes": "wink", "mouth": "tongue_out_1"},
            {"eyes": "wink", "mouth": "tongue_out_2"},
            {"eyes": "wink", "mouth": "tongue_out_1"},
            {"eyes": "normal", "mouth": "smile_2"},
            {"eyes": "wink", "mouth": "smile_1"}
        ]
        
        self.animation_frames["grumpy"] = [
            {"eyes": "squint", "eyebrows": "furrowed", "mouth": "frown_1"},
            {"eyes": "squint", "eyebrows": "furrowed", "mouth": "frown_1"},
            {"eyes": "squint", "eyebrows": "more_furrowed", "mouth": "frown_2"},
            {"eyes": "blink", "eyebrows": "furrowed", "mouth": "frown_1"}
        ]
        
        # Default animation if emotion is not defined
        self.animation_frames["default"] = [
            {"eyes": "open", "mouth": "flat"}
        ]
    
    def _update_loop(self):
        while self.running:
            self.update_display()
            self._update_animation_frame()
            time.sleep(1.0 / self.animation_speed)  # Update at animation speed rate
    
    def _update_animation_frame(self):
        """Update the current animation frame based on timer"""
        current_time = time.time()
        if current_time - self.last_frame_time >= (1.0 / self.animation_speed):
            # Get frames for current emotion
            frames = self.animation_frames.get(
                self.current_emotion,
                self.animation_frames["default"]
            )
            
            # Advance frame and wrap around
            self.animation_frame = (self.animation_frame + 1) % len(frames)
            self.last_frame_time = current_time
    
    def update_display(self):
        if self.simulation:
            # Skip detailed console output for animation frames
            if self.animation_frame == 0:  # Only print on first frame to reduce noise
                print(f"[OLED] Emotion: {self.current_emotion} | Status: {self.status_message}")
        else:
            # Real hardware code would use current animation frame
            # with canvas(self.device) as draw:
            #     current_frame = self._get_current_animation_frame()
            #     self._draw_emotion_frame(draw, current_frame)
            #     # Draw status text
            #     draw.text((10, 50), self.status_message, font=self.font, fill="white")
            pass
    
    def _get_current_animation_frame(self):
        """Get the current frame data for the current emotion"""
        frames = self.animation_frames.get(
            self.current_emotion, 
            self.animation_frames["default"]
        )
        return frames[self.animation_frame]
    
    def _draw_emotion_frame(self, draw, frame_data):
        """Draw the specific frame based on frame data
        This would be implemented on real hardware
        """
        pass
    
    def set_emotion(self, emotion):
        """Set the robot's emotional state for display
        
        Args:
            emotion (str): One of 'happy', 'sad', 'neutral', 'excited', 'sleepy'
        """
        if emotion != self.current_emotion:
            self.current_emotion = emotion
            self.animation_frame = 0  # Reset animation when emotion changes
    
    def set_status(self, status):
        """Update the status message shown on the display"""
        self.status_message = status
    
    def set_animation_speed(self, fps):
        """Set animation speed in frames per second"""
        self.animation_speed = max(1, min(30, fps))  # Clamp between 1-30 fps
    
    def shutdown(self):
        """Clean shutdown of display"""
        self.running = False
        if not self.simulation:
            # Hardware cleanup would go here
            pass

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

class OLEDInterface:
    """Interface to the OLED display"""
    
    def __init__(self, simulation=False):
        self.simulation = simulation
        self.current_emotion = "neutral"
        self.current_status = "Online"
        self.display_active = True
        
        if not simulation:
            try:
                # Import hardware-specific libraries only when not in simulation mode
                import board # type: ignore
                import busio # type: ignore
                import adafruit_ssd1306 # type: ignore
                from PIL import Image, ImageDraw, ImageFont
                
                # Set up display
                i2c = busio.I2C(board.SCL, board.SDA)
                self.display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
                self.image = Image.new("1", (self.display.width, self.display.height))
                self.draw = ImageDraw.Draw(self.image)
                
                # Load font
                try:
                    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except OSError:
                    # Fallback to default font
                    self.font = ImageFont.load_default()
                
                # Clear the display.
                self.display.fill(0)
                self.display.show()
                
                print("OLED Display Initialized")
            except (ImportError, OSError) as e:
                print(f"OLED hardware error: {e}")
                print("OLED Display Initialized (Simulation Mode)")
                self.simulation = True
        else:
            print("OLED Display Initialized (Simulation Mode)")
    
    def clear(self):
        """Clear the display"""
        if not self.simulation and hasattr(self, 'display'):
            self.display.fill(0)
            self.display.show()
        # In simulation mode, just update status
    
    def show_text(self, text, x=0, y=0):
        """Display text on the OLED screen"""
        if not self.simulation and hasattr(self, 'display'):
            self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
            self.draw.text((x, y), text, font=self.font, fill=255)
            self.display.image(self.image)
            self.display.show()
        # In simulation mode, just update status
    
    def show_emotion(self, emotion):
        """Display an emotion on the OLED screen"""
        # Store the current emotion for both hardware and simulation
        self.current_emotion = emotion.lower() if emotion else "neutral"
        
        if not self.simulation and hasattr(self, 'display'):
            # Clear display
            self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
            
            # Draw emotion (simplified version for actual hardware)
            center_x = self.display.width // 2
            center_y = self.display.height // 2
            
            # Draw different faces based on emotion
            if emotion == "happy":
                # Draw happy face
                self._draw_happy_face()
            elif emotion == "sad":
                # Draw sad face
                self._draw_sad_face()
            # ... other emotions would be implemented here
            else:
                # Default to neutral
                self._draw_neutral_face()
                
            # Update the display
            self.display.image(self.image)
            self.display.show()
        
        # Log the emotion change
        print(f"[OLED] Emotion: {self.current_emotion} | Status: {self.current_status}")
    
    def update_status(self, status_text):
        """Update status text displayed on OLED"""
        self.current_status = status_text
        
        if not self.simulation and hasattr(self, 'display'):
            # Actual hardware implementation would redraw the screen here
            # Keep emotion face but update status text at the bottom
            self.show_emotion(self.current_emotion)  # This will redraw with the current emotion
            
            # Draw status text at the bottom
            self.draw.text((0, self.display.height - 12), status_text, font=self.font, fill=255)
            self.display.image(self.image)
            self.display.show()
        
        print(f"[OLED] Emotion: {self.current_emotion} | Status: {self.current_status}")
    
    def get_current_emotion(self):
        """Get the current emotion being displayed (for simulator)"""
        return self.current_emotion
    
    def get_current_status(self):
        """Get the current status text (for simulator)"""
        return self.current_status
    
    # Hardware-specific drawing methods would be implemented here
    def _draw_happy_face(self):
        """Draw a happy face on the OLED (hardware implementation)"""
        if not self.simulation and hasattr(self, 'draw'):
            # Draw eyes
            self.draw.ellipse((30, 15, 45, 30), outline=255)
            self.draw.ellipse((80, 15, 95, 30), outline=255)
            
            # Draw smile
            self.draw.arc((30, 20, 95, 60), 0, 180, fill=255, width=2)
    
    def _draw_sad_face(self):
        """Draw a sad face on the OLED (hardware implementation)"""
        if not self.simulation and hasattr(self, 'draw'):
            # Draw eyes
            self.draw.ellipse((30, 15, 45, 30), outline=255)
            self.draw.ellipse((80, 15, 95, 30), outline=255)
            
            # Draw frown
            self.draw.arc((30, 40, 95, 80), 180, 0, fill=255, width=2)
    
    def _draw_neutral_face(self):
        """Draw a neutral face on the OLED (hardware implementation)"""
        if not self.simulation and hasattr(self, 'draw'):
            # Draw eyes
            self.draw.ellipse((30, 15, 45, 30), outline=255)
            self.draw.ellipse((80, 15, 95, 30), outline=255)
            
            # Draw straight mouth
            self.draw.line((40, 50, 85, 50), fill=255, width=2)

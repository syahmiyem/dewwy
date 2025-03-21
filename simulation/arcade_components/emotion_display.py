import arcade
import math
import random
import time

class EmotionDisplay:
    """Component for drawing animated emotion faces on the robot's display"""
    
    def __init__(self):
        # OLED display properties (1.3" screen)
        self.display_width = 128  # pixels
        self.display_height = 64  # pixels
        self.display_scale = 0.6  # Scale factor for display inside robot
        self.display_offset_y = 10  # Offset from center for display
        
        # Animation properties
        self.animation_frame = 0
        self.animation_time = 0
        # Base frames per second
        self.base_frames_per_second = 5
        self.frames_per_second = self.base_frames_per_second
        self.last_frame_time = time.time()
        
        # Emotion-specific animation speeds
        self.emotion_speeds = {
            "happy": 1.2,       # 20% faster
            "sad": 0.8,         # 20% slower
            "neutral": 1.0,     # Normal speed
            "excited": 1.5,     # 50% faster
            "sleepy": 0.5,      # 50% slower
            "curious": 0.9,     # Slightly slower
            "scared": 1.3,      # Faster
            "playful": 1.4,     # Faster
            "grumpy": 0.7       # Slower
        }
        
        # Reference to OLED interface (set by simulator)
        self.oled_interface = None
        
        # Map emotions to animation rendering functions
        self.emotion_animations = {
            "happy": self._animate_happy_face,
            "sad": self._animate_sad_face,
            "neutral": self._animate_neutral_face,
            "excited": self._animate_excited_face,
            "sleepy": self._animate_sleepy_face,
            "curious": self._animate_curious_face,
            "scared": self._animate_scared_face,
            "playful": self._animate_playful_face,
            "grumpy": self._animate_grumpy_face
        }
        
        # Animation frame counts for each emotion
        self.animation_frame_counts = {
            "happy": 7,
            "sad": 6,
            "neutral": 8,
            "excited": 6,
            "sleepy": 7,
            "curious": 5,
            "scared": 5,
            "playful": 6,
            "grumpy": 4
        }
        
        # Last emotion to detect changes
        self.last_emotion = "neutral"
        
        # Blink timer - random blinking
        self.next_blink_time = time.time() + random.uniform(2, 6)
        self.is_blinking = False
        self.blink_duration = 0.2  # seconds
        self.blink_start_time = 0
        
        # Emotion-specific blinking behaviors
        self.blink_behaviors = {
            "happy": {"min_interval": 3.0, "max_interval": 6.0, "duration": 0.2},
            "sad": {"min_interval": 4.0, "max_interval": 7.0, "duration": 0.3},  # Slower, longer blinks
            "neutral": {"min_interval": 2.0, "max_interval": 5.0, "duration": 0.2},
            "excited": {"min_interval": 1.5, "max_interval": 4.0, "duration": 0.15},  # Quick, frequent blinks
            "sleepy": {"min_interval": 0.8, "max_interval": 3.0, "duration": 0.5},  # Very frequent, long blinks
            "curious": {"min_interval": 1.0, "max_interval": 3.0, "duration": 0.2},  # More frequent when curious
            "scared": {"min_interval": 5.0, "max_interval": 10.0, "duration": 0.1},  # Rare, quick blinks when scared
            "playful": {"min_interval": 1.0, "max_interval": 3.0, "duration": 0.2},  # Frequent, playful blinks
            "grumpy": {"min_interval": 3.0, "max_interval": 8.0, "duration": 0.3}    # Slow, deliberate blinks
        }
        
        # Transition animation properties
        self.transitioning = False
        self.transition_start_time = 0
        self.transition_duration = 0.5  # seconds
        self.transition_from_emotion = "neutral"
        self.transition_to_emotion = "neutral"
        self.transition_progress = 0  # 0 to 1
    
    def draw(self, x, y, emotion=None):
        """Draw the emotion display at the specified position
        
        Args:
            x: Center x coordinate of the robot
            y: Center y coordinate of the robot
            emotion: If provided, overrides the OLED interface emotion
        """
        # Use the OLED interface's emotion if available and no override provided
        if not emotion and self.oled_interface:
            emotion = self.oled_interface.get_current_emotion()
        
        # Default to neutral if no emotion available
        if not emotion:
            emotion = "neutral"
            
        # Handle emotion transitions
        if self.transitioning:
            # Calculate transition progress
            elapsed_time = time.time() - self.transition_start_time
            self.transition_progress = min(1, elapsed_time / self.transition_duration)
            
            # Apply easing function to make transitions more natural
            eased_progress = self.ease_in_out_cubic(self.transition_progress)
            
            # If transition is complete, stop transitioning
            if self.transition_progress >= 1:
                self.transitioning = False
                self.last_emotion = emotion
        
        # Update animation frame if needed
        self._update_animation_frame(emotion)
        
        # Calculate display position and size
        display_width = self.display_width * self.display_scale
        display_height = self.display_height * self.display_scale
        
        # Position display in the robot (slightly above center)
        display_x = x - display_width / 2
        display_y = y - display_height / 2 - self.display_offset_y
        
        # Draw display background (black like OLED)
        arcade.draw_rectangle_filled(
            x, y - self.display_offset_y,
            display_width, display_height,
            arcade.color.BLACK
        )
        
        # Draw display border
        arcade.draw_rectangle_outline(
            x, y - self.display_offset_y,
            display_width, display_height,
            arcade.color.GRAY,
            1
        )
        
        # Draw appropriate emotion animation frame
        emotion = emotion.lower()
        if self.transitioning:
            # Blend between two emotions
            self._draw_blended_emotion(
                display_x, display_y, display_width, display_height,
                self.transition_from_emotion, self.transition_to_emotion,
                self.transition_progress
            )
        elif emotion in self.emotion_animations:
            # Call the appropriate animation function
            self.emotion_animations[emotion](
                display_x, display_y, display_width, display_height, 
                self.animation_frame
            )
        else:
            # Default to neutral if emotion not found
            self._animate_neutral_face(
                display_x, display_y, display_width, display_height, 
                self.animation_frame
            )
            
        # If we have a status from the OLED interface, draw it at the bottom
        if self.oled_interface:
            status = self.oled_interface.get_current_status()
            if status:
                arcade.draw_text(
                    status,
                    x - display_width/2 + 5, y - self.display_offset_y - display_height/2 + 5,
                    arcade.color.WHITE,
                    8
                )
    
    def _update_animation_frame(self, emotion):
        """Update the current animation frame based on timer"""
        # Check for emotion change
        if emotion != self.last_emotion and not self.transitioning:
            # Start a transition
            self.transitioning = True
            self.transition_start_time = time.time()
            self.transition_from_emotion = self.last_emotion
            self.transition_to_emotion = emotion
            self.transition_progress = 0
            
            # Set emotion-specific speed
            self.frames_per_second = self.base_frames_per_second * self.emotion_speeds.get(emotion.lower(), 1.0)
        
        # Update frame based on timer
        current_time = time.time()
        if current_time - self.last_frame_time >= (1.0 / self.frames_per_second):
            # Get frame count for current emotion
            frame_count = self.animation_frame_counts.get(emotion.lower(), 1)
            
            # Advance frame and wrap around
            self.animation_frame = (self.animation_frame + 1) % frame_count
            
            # Update animation time (for smooth animations)
            self.animation_time += 1.0 / self.frames_per_second
            
            self.last_frame_time = current_time
            
        # Handle random blinking
        self._update_blink_state(current_time)
    
    def _update_blink_state(self, current_time):
        """Update blinking state for natural eye movements that adapt to emotional state"""
        # Get current emotion (or default to neutral)
        current_emotion = self.last_emotion if hasattr(self, 'last_emotion') else "neutral"
        
        # Get blink behavior for current emotion
        blink_behavior = self.blink_behaviors.get(current_emotion, self.blink_behaviors["neutral"])
        
        if not self.is_blinking and current_time >= self.next_blink_time:
            # Start a blink
            self.is_blinking = True
            self.blink_start_time = current_time
            # Use emotion-specific blink duration
            self.blink_duration = blink_behavior["duration"]
        elif self.is_blinking and current_time - self.blink_start_time > self.blink_duration:
            # End the blink
            self.is_blinking = False
            # Schedule next blink using emotion-specific interval
            min_interval = blink_behavior["min_interval"]
            max_interval = blink_behavior["max_interval"]
            self.next_blink_time = current_time + random.uniform(min_interval, max_interval)
    
    def _draw_blended_emotion(self, x, y, width, height, emotion1, emotion2, progress):
        """Blend two emotions together during transition"""
        # Ensure emotions are valid
        if emotion1 not in self.emotion_animations or emotion2 not in self.emotion_animations:
            return
        
        # Apply easing to progress for smoother transitions
        eased_progress = self.ease_in_out_cubic(progress)
        
        # Draw first emotion (fading out)
        alpha1 = int(255 * (1 - eased_progress))
        self.emotion_animations[emotion1](
            x, y, width, height, 
            self.animation_frame,
            alpha=alpha1
        )
        
        # Draw second emotion (fading in)
        alpha2 = int(255 * eased_progress)
        self.emotion_animations[emotion2](
            x, y, width, height, 
            self.animation_frame,
            alpha=alpha2
        )
    
    def ease_in_out_cubic(self, x):
        """Easing function for smooth animation"""
        if x < 0.5:
            return 4 * x * x * x
        else:
            return 1 - pow(-2 * x + 2, 3) / 2
    
    # Helper drawing methods for eye states
    def _draw_open_eyes(self, left_x, right_x, y, face_size, alpha=255):
        """Draw regular open eyes"""
        eye_size = face_size * 0.1
        white_with_alpha = (255, 255, 255, alpha)
        arcade.draw_circle_filled(left_x, y, eye_size, white_with_alpha)
        arcade.draw_circle_filled(right_x, y, eye_size, white_with_alpha)
    
    def _draw_half_closed_eyes(self, left_x, right_x, y, face_size, alpha=255):
        """Draw half-closed eyes"""
        eye_width = face_size * 0.15
        eye_height = face_size * 0.05
        white_with_alpha = (255, 255, 255, alpha)
        
        arcade.draw_ellipse_filled(left_x, y, eye_width, eye_height, white_with_alpha)
        arcade.draw_ellipse_filled(right_x, y, eye_width, eye_height, white_with_alpha)
    
    def _draw_closed_eyes(self, left_x, right_x, y, face_size, alpha=255):
        """Draw closed eyes (horizontal lines)"""
        eye_width = face_size * 0.15
        white_with_alpha = (255, 255, 255, alpha)
        
        arcade.draw_line(
            left_x - eye_width/2, y,
            left_x + eye_width/2, y,
            white_with_alpha, 2
        )
        arcade.draw_line(
            right_x - eye_width/2, y,
            right_x + eye_width/2, y,
            white_with_alpha, 2
        )
    
    # Animation functions for each emotion
    
    def _animate_neutral_face(self, x, y, width, height, frame, alpha=255):
        """Draw the neutral face with animation"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        
        # Handle blinking in the animation
        if self.is_blinking:
            self._draw_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        elif frame == 3:  # Half-closed eyes
            self._draw_half_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        elif frame == 4:  # Fully closed eyes
            self._draw_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        elif frame == 5:  # Half-closed eyes again
            self._draw_half_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        else:  # Normal open eyes
            self._draw_open_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        
        # Draw straight mouth
        mouth_y = center_y - face_size * 0.15
        mouth_width = face_size * 0.4
        
        arcade.draw_line(
            center_x - mouth_width/2, mouth_y,
            center_x + mouth_width/2, mouth_y,
            white_with_alpha,
            3
        )
    
    def _animate_happy_face(self, x, y, width, height, frame, alpha=255):
        """Draw an improved happy face with organic animation"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Add subtle bouncy movement
        bounce = math.sin(self.animation_time * 3) * 2
        center_y += bounce
        
        # Draw eyes - with blinking and more life
        eye_y = center_y + face_size * 0.12
        left_eye_x = center_x - face_size * 0.22
        right_eye_x = center_x + face_size * 0.22
        
        # Blinking in animation
        if self.is_blinking:
            self._draw_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        elif frame in [3, 4, 5]:
            if frame == 3:
                self._draw_half_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
            elif frame == 4:
                self._draw_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
            elif frame == 5:
                self._draw_half_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        else:
            self._draw_open_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        
        # Draw smile - FIXED positioning for proper smile shape
        smile_y = center_y - face_size * 0.15  # Position slightly lower
        smile_width = face_size * (0.48 + math.sin(self.animation_time * 2) * 0.03)
        smile_height = face_size * (0.32 + bounce/20)
        
        # FIXED: Use correct angles for smile curve (upward arc)
        start_angle = 200  # Start angle (degrees)
        end_angle = 340    # End angle (degrees)
        
        arcade.draw_arc_outline(
            center_x, smile_y,
            smile_width, smile_height,
            white_with_alpha,
            start_angle, end_angle,
            3
        )
        
        # Inner smile curve to show mouth depth
        inner_width = smile_width * 0.8
        inner_height = smile_height * 0.5
        
        arcade.draw_arc_outline(
            center_x, smile_y - smile_height * 0.1,
            inner_width, inner_height,
            white_with_alpha,
            start_angle, end_angle,
            2
        )
    
    def _animate_sad_face(self, x, y, width, height, frame, alpha=255):
        """Draw the sad face with animation"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw eyes (droopy or blinking)
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        
        if frame in [2, 3]:
            # Blinking sequence
            if frame == 2:
                self._draw_half_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
            else:
                self._draw_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        else:
            # Droopy eyes
            eye_size = face_size * 0.1
            
            arcade.draw_circle_filled(left_eye_x, eye_y - eye_size/2, eye_size, white_with_alpha)
            arcade.draw_circle_filled(right_eye_x, eye_y - eye_size/2, eye_size, white_with_alpha)
        
        # Draw frown - sad downward curve with slight animation
        frown_y = center_y - face_size * 0.2
        frown_width = face_size * 0.5
        frown_height = face_size * (0.3 + (0.05 if frame == 5 else 0))
        
        # FIXED: Use correct angles for frown (this is already correct at 180-360 degrees)
        arcade.draw_arc_outline(
            center_x, frown_y + frown_height,
            frown_width, frown_height,
            white_with_alpha,
            180, 360,
            3
        )
    
    def _animate_sleepy_face(self, x, y, width, height, frame, alpha=255):
        """Draw the sleepy face with animation"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw eyes (mostly closed for sleepy look)
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_width = face_size * 0.15
        
        # Draw mostly closed eyes
        arcade.draw_line(
            left_eye_x - eye_width/2, eye_y,
            left_eye_x + eye_width/2, eye_y,
            white_with_alpha,
            2
        )
        arcade.draw_line(
            right_eye_x - eye_width/2, eye_y,
            right_eye_x + eye_width/2, eye_y,
            white_with_alpha,
            2
        )
        
        # Draw Z's that float up and fade based on frame
        if frame >= 3:  # Only show Z's in some frames
            z_x = center_x + face_size * 0.25
            z_y = center_y + face_size * (0.4 + frame * 0.05)  # Z's float up
            z_size = face_size * 0.1
            
            # First Z
            arcade.draw_text(
                "z", z_x, z_y,
                white_with_alpha,
                z_size
            )
            
            # Second, smaller Z (appears in later frames)
            if frame >= 4:
                arcade.draw_text(
                    "z", z_x - z_size, z_y + z_size * 1.2,
                    white_with_alpha,
                    z_size * 0.8
                )
        
        # Draw mouth - sometimes yawning
        mouth_y = center_y - face_size * 0.15
        mouth_width = face_size * 0.3
        
        if frame >= 4 and frame <= 6:
            # Yawning (bigger oval)
            mouth_height = mouth_width * (0.6 + (frame - 4) * 0.1)
            arcade.draw_ellipse_outline(
                center_x, mouth_y,
                mouth_width, mouth_height,
                white_with_alpha,
                2
            )
        else:
            # Slight oval mouth
            arcade.draw_ellipse_outline(
                center_x, mouth_y,
                mouth_width, mouth_width * 0.4,
                white_with_alpha,
                2
            )
    
    def _animate_excited_face(self, x, y, width, height, frame, alpha=255):
        """Draw an improved excited face with bouncy animation"""
        # Apply a bounce effect to the whole face
        bounce_offset = math.sin(self.animation_time * 5) * 3
        
        center_x = x + width/2
        center_y = y + height/2 + bounce_offset
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw wide eyes with pupils
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.13  # Bigger eyes for excitement
        
        # Brief blink at frame 4
        if frame == 4:
            self._draw_closed_eyes(left_eye_x, right_eye_x, eye_y, face_size, alpha)
        else:
            # Draw wide eyes with pupils
            arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, white_with_alpha)
            arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, white_with_alpha)
            
            # Pupils
            pupil_size = eye_size * 0.5
            arcade.draw_circle_filled(left_eye_x, eye_y, pupil_size, arcade.color.BLACK)
            arcade.draw_circle_filled(right_eye_x, eye_y, pupil_size, arcade.color.BLACK)
        
        # Draw big open smile - FIXED positioning
        smile_y = center_y - face_size * 0.15  # Lower position for smile
        smile_width = face_size * (0.56 + math.sin(self.animation_time * 4) * 0.04)
        smile_height = face_size * 0.35
        
        # FIXED: Use correct angles for smile curve (upward arc)
        start_angle = 200  # Start angle (degrees)
        end_angle = 340    # End angle (degrees)
        
        arcade.draw_arc_outline(
            center_x, smile_y,
            smile_width, smile_height,
            white_with_alpha,
            start_angle, end_angle,
            3
        )
        
        # Inner smile line to create open mouth effect
        inner_width = smile_width * 0.8
        inner_height = smile_height * 0.6
        
        arcade.draw_arc_outline(
            center_x, smile_y - smile_height * 0.1,  # Slightly lower for depth
            inner_width, inner_height,
            white_with_alpha,
            start_angle, end_angle,
            2
        )
    
    def _animate_curious_face(self, x, y, width, height, frame, alpha=255):
        """Draw a curious face with animation"""
        # Apply a slight head tilt based on frame
        tilt = 0
        if frame == 1:
            tilt = 5
        elif frame == 2:
            tilt = -5
            
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw eyes (one eyebrow raised)
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.1
        
        # Frame 3 has slightly squinted eyes
        if frame == 3:
            # Squinted eyes
            eye_width = face_size * 0.15
            
            arcade.draw_ellipse_filled(
                left_eye_x, eye_y,
                eye_width, eye_size * 0.7,
                white_with_alpha
            )
            arcade.draw_ellipse_filled(
                right_eye_x, eye_y,
                eye_width, eye_size * 0.7,
                white_with_alpha
            )
        else:
            # Normal eyes
            arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, white_with_alpha)
            arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, white_with_alpha)
        
        # Draw raised eyebrow (tilts slightly based on frame)
        brow_width = face_size * 0.18
        left_brow_y = eye_y + face_size * 0.15
        brow_tilt = face_size * 0.06 + (face_size * 0.02 if frame == 4 else 0)
        
        arcade.draw_line(
            left_eye_x - brow_width/2, left_brow_y - face_size * 0.02 - tilt/50,
            left_eye_x + brow_width/2, left_brow_y + brow_tilt + tilt/50,
            white_with_alpha,
            2
        )
        
        # Draw slightly open mouth (changes shape slightly)
        mouth_y = center_y - face_size * 0.15
        mouth_size = face_size * (0.12 + (0.02 if frame % 2 == 0 else 0))
        
        arcade.draw_circle_outline(
            center_x, mouth_y,
            mouth_size,
            white_with_alpha,
            2
        )
    
    def _animate_scared_face(self, x, y, width, height, frame, alpha=255):
        """Draw a scared face with trembling animation"""
        # Apply a trembling effect
        tremble = 0
        if frame == 1:
            tremble = 1
        elif frame == 2:
            tremble = -1
        elif frame == 3:
            tremble = 2
        elif frame == 4:
            tremble = -2
            
        center_x = x + width/2 + tremble
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw wide, scared eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.15  # Bigger eyes for fear
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, white_with_alpha)
        arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, white_with_alpha)
        
        # Draw pupils (bigger for scared look)
        pupil_size = eye_size * 0.6
        pupil_offset = 0
        if frame in [1, 3]:
            pupil_offset = 1  # Pupils dart around
            
        arcade.draw_circle_filled(left_eye_x + pupil_offset, eye_y, pupil_size, arcade.color.BLACK)
        arcade.draw_circle_filled(right_eye_x + pupil_offset, eye_y, pupil_size, arcade.color.BLACK)
        
        # Draw mouth in an oval 'scared' shape that changes size
        mouth_y = center_y - face_size * 0.2
        mouth_width = face_size * 0.2
        mouth_height = face_size * (0.25 + (0.05 if frame % 2 == 0 else 0))
        
        arcade.draw_ellipse_outline(
            center_x, mouth_y,
            mouth_width, mouth_height,
            white_with_alpha,
            3
        )
    
    def _animate_playful_face(self, x, y, width, height, frame, alpha=255):
        """Draw a playful face with winking animation"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Draw left eye (always open)
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.12
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, white_with_alpha)
        
        # Right eye alternates between wink and open
        if frame in [0, 1, 2, 3, 5]:
            # Winking
            arcade.draw_line(
                right_eye_x - eye_size, eye_y,
                right_eye_x + eye_size, eye_y,
                white_with_alpha,
                2
            )
        else:
            # Open eye briefly in the animation
            arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, white_with_alpha)
        
        # Draw smile or tongue out depending on frame
        smile_y = center_y - face_size * 0.1
        smile_width = face_size * 0.6
        smile_height = face_size * 0.35
        
        # FIXED: Use correct angles for smile curve (upward arc)
        start_angle = 200  # Start angle (degrees)
        end_angle = 340    # End angle (degrees)
        
        # Draw different mouth shapes based on frame
        if frame in [1, 2, 3]:
            # Tongue out
            arcade.draw_arc_outline(
                center_x, smile_y,
                smile_width, smile_height,
                white_with_alpha,
                start_angle, end_angle,
                3
            )
            
            # Draw tongue - size varies with frame
            tongue_width = smile_width * 0.2
            tongue_height = smile_height * (0.4 + (0.2 if frame == 2 else 0))
            arcade.draw_ellipse_filled(
                center_x, smile_y - smile_height * 0.2,
                tongue_width, tongue_height,
                white_with_alpha
            )
        else:
            # Regular smile
            arcade.draw_arc_outline(
                center_x, smile_y,
                smile_width, smile_height,
                white_with_alpha,
                start_angle, end_angle,
                3
            )
    
    def _animate_grumpy_face(self, x, y, width, height, frame, alpha=255):
        """Draw a grumpy face with furrowed brow animation"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        white_with_alpha = (255, 255, 255, alpha)
        
        # Eyes position
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_width = face_size * 0.15
        
        # Frame 3 shows blinking eyes
        if frame == 3:
            # Blink
            arcade.draw_line(
                left_eye_x - eye_width/2, eye_y,
                left_eye_x + eye_width/2, eye_y,
                white_with_alpha,
                2
            )
            arcade.draw_line(
                right_eye_x - eye_width/2, eye_y,
                right_eye_x + eye_width/2, eye_y,
                white_with_alpha,
                2
            )
        else:
            # Squinted eyes
            eye_height = face_size * 0.05
            arcade.draw_ellipse_filled(
                left_eye_x, eye_y,
                eye_width, eye_height,
                white_with_alpha
            )
            arcade.draw_ellipse_filled(
                right_eye_x, eye_y,
                eye_width, eye_height,
                white_with_alpha
            )
        
        # Draw eyebrows - furrow level increases with frame 2
        brow_furrow = 0.06 if frame != 2 else 0.08
        
        # Left eyebrow
        arcade.draw_line(
            left_eye_x - eye_width/2, eye_y + face_size * brow_furrow,
            left_eye_x + eye_width/2, eye_y + face_size * 0.02,
            white_with_alpha,
            2
        )
        
        # Right eyebrow
        arcade.draw_line(
            right_eye_x - eye_width/2, eye_y + face_size * 0.02,
            right_eye_x + eye_width/2, eye_y + face_size * brow_furrow,
            white_with_alpha,
            2
        )
        
        # Draw frown - more pronounced in frame 2
        mouth_y = center_y - face_size * 0.15
        mouth_width = face_size * 0.4
        frown_depth = face_size * (0.05 + (0.02 if frame == 2 else 0))
        
        arcade.draw_line(
            center_x - mouth_width/2, mouth_y,
            center_x + mouth_width/2, mouth_y - frown_depth,
            white_with_alpha,
            3
        )
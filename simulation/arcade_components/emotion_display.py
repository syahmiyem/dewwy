import arcade

class EmotionDisplay:
    """Component for drawing emotion faces on the robot's display"""
    
    def __init__(self):
        # OLED display properties (1.3" screen)
        self.display_width = 128  # pixels
        self.display_height = 64  # pixels
        self.display_scale = 0.6  # Scale factor for display inside robot
        self.display_offset_y = 10  # Offset from center for display
        
        # Map emotion names to drawing functions
        self.emotion_faces = {
            "happy": self._create_happy_face,
            "sad": self._create_sad_face,
            "neutral": self._create_neutral_face,
            "excited": self._create_excited_face,
            "sleepy": self._create_sleepy_face,
            "curious": self._create_curious_face,
            "scared": self._create_scared_face,
            "playful": self._create_playful_face,
            "grumpy": self._create_grumpy_face
        }
    
    def draw(self, x, y, emotion):
        """Draw the emotion display at the specified position
        
        Args:
            x: Center x coordinate of the robot
            y: Center y coordinate of the robot
            emotion: Current emotion to display
        """
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
        
        # Draw appropriate emotion face
        emotion = emotion.lower()
        if emotion in self.emotion_faces:
            # Call the appropriate face drawing function
            self.emotion_faces[emotion](display_x, display_y, display_width, display_height)
        else:
            # Default to neutral if emotion not found
            self._create_neutral_face(display_x, display_y, display_width, display_height)
    
    def _create_happy_face(self, x, y, width, height):
        """Draw a happy face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.1
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, arcade.color.WHITE)
        
        # Draw smile - happy upward curve
        smile_y = center_y - face_size * 0.1
        smile_width = face_size * 0.5
        smile_height = face_size * 0.3
        
        # Draw the smile as an arc (happy faces have upward curves)
        arcade.draw_arc_outline(
            center_x, smile_y,
            smile_width, smile_height,
            arcade.color.WHITE,
            0, 180,
            3
        )
    
    def _create_sad_face(self, x, y, width, height):
        """Draw a sad face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw eyes (slightly droopy)
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.1
        
        arcade.draw_circle_filled(left_eye_x, eye_y - eye_size/2, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(right_eye_x, eye_y - eye_size/2, eye_size, arcade.color.WHITE)
        
        # Draw frown - sad downward curve
        frown_y = center_y - face_size * 0.2
        frown_width = face_size * 0.5
        frown_height = face_size * 0.3
        
        arcade.draw_arc_outline(
            center_x, frown_y + frown_height,
            frown_width, frown_height,
            arcade.color.WHITE,
            180, 360,
            3
        )
    
    def _create_neutral_face(self, x, y, width, height):
        """Draw a neutral face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.1
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, arcade.color.WHITE)
        
        # Draw straight mouth
        mouth_y = center_y - face_size * 0.15
        mouth_width = face_size * 0.4
        
        arcade.draw_line(
            center_x - mouth_width/2, mouth_y,
            center_x + mouth_width/2, mouth_y,
            arcade.color.WHITE,
            3
        )
    
    def _create_excited_face(self, x, y, width, height):
        """Draw an excited face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw wide eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.13  # Bigger eyes for excitement
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, arcade.color.WHITE)
        
        # Pupils
        pupil_size = eye_size * 0.5
        arcade.draw_circle_filled(left_eye_x, eye_y, pupil_size, arcade.color.BLACK)
        arcade.draw_circle_filled(right_eye_x, eye_y, pupil_size, arcade.color.BLACK)
        
        # Draw open smile
        smile_y = center_y - face_size * 0.1
        smile_width = face_size * 0.5
        smile_height = face_size * 0.3
        
        # Outer smile arc
        arcade.draw_arc_outline(
            center_x, smile_y,
            smile_width, smile_height,
            arcade.color.WHITE,
            0, 180,
            3
        )
        
        # Inner smile line to create open mouth effect
        arcade.draw_arc_outline(
            center_x, smile_y - smile_height * 0.2,
            smile_width * 0.7, smile_height * 0.5,
            arcade.color.WHITE,
            0, 180,
            2
        )
    
    def _create_sleepy_face(self, x, y, width, height):
        """Draw a sleepy face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw half-closed eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_width = face_size * 0.15
        eye_height = face_size * 0.05
        
        # Draw eye lines
        arcade.draw_line(
            left_eye_x - eye_width/2, eye_y,
            left_eye_x + eye_width/2, eye_y,
            arcade.color.WHITE,
            2
        )
        arcade.draw_line(
            right_eye_x - eye_width/2, eye_y,
            right_eye_x + eye_width/2, eye_y,
            arcade.color.WHITE,
            2
        )
        
        # Draw small 'z's above head to indicate sleeping
        z_x = center_x + face_size * 0.25
        z_y = center_y + face_size * 0.4
        z_size = face_size * 0.1
        
        arcade.draw_text(
            "z", z_x, z_y,
            arcade.color.WHITE,
            z_size
        )
        
        arcade.draw_text(
            "z", z_x - z_size, z_y + z_size * 1.2,
            arcade.color.WHITE,
            z_size * 0.8
        )
        
        # Draw slightly open mouth
        mouth_y = center_y - face_size * 0.15
        mouth_width = face_size * 0.3
        
        arcade.draw_ellipse_outline(
            center_x, mouth_y,
            mouth_width, mouth_width * 0.4,
            arcade.color.WHITE,
            2
        )
    
    def _create_curious_face(self, x, y, width, height):
        """Draw a curious face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw eyes with one eyebrow raised
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.1
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, arcade.color.WHITE)
        
        # Draw raised eyebrow
        brow_width = face_size * 0.18
        left_brow_y = eye_y + face_size * 0.15
        
        arcade.draw_line(
            left_eye_x - brow_width/2, left_brow_y - face_size * 0.02,
            left_eye_x + brow_width/2, left_brow_y + face_size * 0.06,
            arcade.color.WHITE,
            2
        )
        
        # Draw slightly open mouth in "o" shape
        mouth_y = center_y - face_size * 0.15
        mouth_size = face_size * 0.12
        
        arcade.draw_circle_outline(
            center_x, mouth_y,
            mouth_size,
            arcade.color.WHITE,
            2
        )
    
    def _create_scared_face(self, x, y, width, height):
        """Draw a scared face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw wide eyes
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.15  # Big eyes for fear
        
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(right_eye_x, eye_y, eye_size, arcade.color.WHITE)
        
        # Pupils
        pupil_size = eye_size * 0.6
        arcade.draw_circle_filled(left_eye_x, eye_y, pupil_size, arcade.color.BLACK)
        arcade.draw_circle_filled(right_eye_x, eye_y, pupil_size, arcade.color.BLACK)
        
        # Draw mouth in a small 'o' shape for fear
        mouth_y = center_y - face_size * 0.2
        mouth_width = face_size * 0.2
        mouth_height = face_size * 0.25
        
        arcade.draw_ellipse_outline(
            center_x, mouth_y,
            mouth_width, mouth_height,
            arcade.color.WHITE,
            3
        )
    
    def _create_playful_face(self, x, y, width, height):
        """Draw a playful face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw winking eye (one open, one closed)
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_size = face_size * 0.12
        
        # Open eye
        arcade.draw_circle_filled(left_eye_x, eye_y, eye_size, arcade.color.WHITE)
        
        # Wink (horizontal line)
        arcade.draw_line(
            right_eye_x - eye_size, eye_y,
            right_eye_x + eye_size, eye_y,
            arcade.color.WHITE,
            2
        )
        
        # Big smile
        smile_y = center_y - face_size * 0.1
        smile_width = face_size * 0.6
        smile_height = face_size * 0.35
        
        # Draw the smile as an arc
        arcade.draw_arc_outline(
            center_x, smile_y,
            smile_width, smile_height,
            arcade.color.WHITE,
            0, 180,
            3
        )
        
        # Tongue sticking out
        tongue_width = smile_width * 0.2
        tongue_height = smile_height * 0.5
        arcade.draw_ellipse_filled(
            center_x, smile_y - smile_height * 0.2,
            tongue_width, tongue_height,
            arcade.color.WHITE
        )
    
    def _create_grumpy_face(self, x, y, width, height):
        """Draw a grumpy face on the display"""
        center_x = x + width/2
        center_y = y + height/2
        face_size = min(width, height) * 0.8
        
        # Draw squinted eyes with furrowed brows
        eye_y = center_y + face_size * 0.1
        left_eye_x = center_x - face_size * 0.2
        right_eye_x = center_x + face_size * 0.2
        eye_width = face_size * 0.15
        
        # Left eye and eyebrow
        arcade.draw_line(
            left_eye_x - eye_width/2, eye_y,
            left_eye_x + eye_width/2, eye_y,
            arcade.color.WHITE,
            2
        )
        arcade.draw_line(
            left_eye_x - eye_width/2, eye_y + face_size * 0.06,
            left_eye_x + eye_width/2, eye_y + face_size * 0.02,
            arcade.color.WHITE,
            2
        )
        
        # Right eye and eyebrow
        arcade.draw_line(
            right_eye_x - eye_width/2, eye_y,
            right_eye_x + eye_width/2, eye_y,
            arcade.color.WHITE,
            2
        )
        arcade.draw_line(
            right_eye_x - eye_width/2, eye_y + face_size * 0.02,
            right_eye_x + eye_width/2, eye_y + face_size * 0.06,
            arcade.color.WHITE,
            2
        )
        
        # Draw frown
        mouth_y = center_y - face_size * 0.15
        mouth_width = face_size * 0.4
        
        arcade.draw_line(
            center_x - mouth_width/2, mouth_y,
            center_x + mouth_width/2, mouth_y - face_size * 0.05,
            arcade.color.WHITE,
            3
        )

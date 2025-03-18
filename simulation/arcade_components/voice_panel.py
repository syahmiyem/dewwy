import arcade
import time
import math

class VoiceRecognitionPanel:
    """Component for visualizing and testing voice recognition"""
    
    def __init__(self):
        self.wake_word = "dewwy"
        self.wake_word_active = False
        self.wake_word_time = 0
        self.wake_word_timeout = 10  # Seconds until wake word detection expires
        
        self.last_commands = []
        self.max_commands = 5
        
        self.test_commands = [
            "come here",
            "follow me", 
            "stop", 
            "go to sleep",
            "wake up",
            "play",
            "good boy",
            "sit",
            "turn around",
            "dance"
        ]
        self.selected_command = 0
        
        # Visual state
        self.listening_animation = 0
        self.voice_active = False
        self.command_feedback = ""
        self.feedback_time = 0
    
    def add_command(self, command):
        """Add a recognized command to history"""
        self.last_commands.insert(0, {
            "time": time.strftime("%H:%M:%S"),
            "command": command
        })
        while len(self.last_commands) > self.max_commands:
            self.last_commands.pop()
    
    def activate_wake_word(self):
        """Simulate wake word detection"""
        self.wake_word_active = True
        self.wake_word_time = time.time()
        self.voice_active = True
        return True
    
    def select_next_command(self):
        """Select the next command in the test list"""
        self.selected_command = (self.selected_command + 1) % len(self.test_commands)
    
    def select_prev_command(self):
        """Select the previous command in the test list"""
        self.selected_command = (self.selected_command - 1) % len(self.test_commands)
    
    def get_selected_command(self):
        """Get the currently selected test command"""
        return self.test_commands[self.selected_command]
    
    def show_command_feedback(self, command):
        """Show feedback that a command was processed"""
        self.command_feedback = command
        self.feedback_time = time.time()
    
    def update(self):
        """Update the panel state"""
        current_time = time.time()
        
        # Check for wake word timeout
        if self.wake_word_active and current_time - self.wake_word_time > self.wake_word_timeout:
            self.wake_word_active = False
        
        # Increment listening animation counter
        if self.voice_active:
            self.listening_animation = (self.listening_animation + 0.1) % (2 * 3.14159)
        
        # Clear feedback after a delay
        if self.command_feedback and current_time - self.feedback_time > 2.0:
            self.command_feedback = ""
    
    def draw(self, x, y, width=300, height=250):
        """Draw the voice recognition panel"""
        # Background panel with rounded corners
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (40, 44, 52, 220)  # Semi-transparent dark gray
        )
        
        # Panel border
        arcade.draw_rectangle_outline(
            x, y, width, height,
            (80, 90, 100),
            2
        )
        
        # Title
        arcade.draw_text(
            "VOICE RECOGNITION",
            x - width/2 + 10, y + height/2 - 25,
            arcade.color.WHITE,
            16,
            bold=True
        )
        
        # Horizontal separator
        arcade.draw_line(
            x - width/2 + 10, y + height/2 - 35,
            x + width/2 - 10, y + height/2 - 35,
            arcade.color.GRAY,
            1
        )
        
        # Status indicator
        status_text = "Ready"
        status_color = arcade.color.YELLOW
        
        if self.wake_word_active:
            status_text = "Listening for command..."
            status_color = arcade.color.GREEN
            
            # Calculate remaining time
            remaining = self.wake_word_timeout - (time.time() - self.wake_word_time)
            if remaining > 0:
                status_text += f" ({remaining:.0f}s)"
        
        arcade.draw_text(
            status_text,
            x - width/2 + 10, y + height/2 - 60,
            status_color,
            14
        )
        
        # Draw listening animation - more dynamic visualizer
        if self.voice_active:
            center_x = x - width/2 + 40
            center_y = y + height/2 - 90
            
            # Draw visualizer background
            arcade.draw_rectangle_filled(
                x, center_y,
                width - 20, 40,
                arcade.color.DARK_BLUE_GRAY
            )
            
            # Calculate animation values
            bar_count = 8
            for i in range(bar_count):
                # Calculate height based on sine wave with offset per bar
                phase_offset = i * 0.7
                amplitude = 5 + 10 * abs(math.sin(self.listening_animation + phase_offset))
                bar_width = (width - 40) / bar_count - 3
                
                arcade.draw_rectangle_filled(
                    center_x + i * ((width - 40) / bar_count), 
                    center_y,
                    bar_width, 
                    amplitude,
                    arcade.color.ELECTRIC_GREEN
                )
        
        # Wake word button - more attractive design
        wake_button_y = y + height/2 - 120
        
        # Button background
        arcade.draw_rectangle_filled(
            x, wake_button_y,
            width - 40, 30,
            arcade.color.DARK_BLUE
        )
        
        # Button highlight/glow when active
        if self.wake_word_active:
            arcade.draw_rectangle_outline(
                x, wake_button_y,
                width - 40, 30,
                arcade.color.ELECTRIC_GREEN,
                2
            )
        
        arcade.draw_text(
            f'Say "{self.wake_word}" (W key)',
            x - 80, wake_button_y - 7,
            arcade.color.WHITE,
            12
        )
        
        # Command selector - improved design
        command_y = y + height/2 - 160
        
        # Selector background
        arcade.draw_rectangle_filled(
            x, command_y,
            width - 40, 30,
            arcade.color.DARK_SLATE_GRAY
        )
        
        arcade.draw_text(
            f"Test: {self.get_selected_command()}",
            x - 80, command_y - 7,
            arcade.color.WHITE,
            12
        )
        
        # Left/right indicators for selection
        arcade.draw_text(
            "◀",
            x - width/2 + 20, command_y - 7,
            arcade.color.LIGHT_GRAY,
            12
        )
        
        arcade.draw_text(
            "▶",
            x + width/2 - 20, command_y - 7,
            arcade.color.LIGHT_GRAY,
            12
        )
        
        # Command history with background
        history_y = y - height/2 + 90
        arcade.draw_text(
            "Command History:",
            x - width/2 + 10, history_y + 10,
            arcade.color.LIGHT_BLUE,
            12
        )
        
        # History background
        arcade.draw_rectangle_filled(
            x, history_y - 40,
            width - 20, 80,
            arcade.color.DARK_BLUE_GRAY
        )
        
        for i, cmd in enumerate(self.last_commands):
            arcade.draw_text(
                f"{cmd['time']}: {cmd['command']}",
                x - width/2 + 15, history_y - 10 - (i * 20),
                arcade.color.WHITE,
                10
            )
        
        # Feedback for executed command - improved visibility
        if self.command_feedback:
            # Green feedback box
            arcade.draw_rectangle_filled(
                x, y - height/2 + 30,
                width - 20, 30,
                arcade.color.DARK_GREEN
            )
            
            # Add subtle glow/pulse effect
            pulse_scale = 1.0 + 0.05 * math.sin(time.time() * 10)
            arcade.draw_rectangle_outline(
                x, y - height/2 + 30,
                (width - 20) * pulse_scale, 30 * pulse_scale,
                arcade.color.GREEN,
                2
            )
            
            arcade.draw_text(
                f"Executed: {self.command_feedback}",
                x - width/2 + 20, y - height/2 + 23,
                arcade.color.WHITE,
                12,
                bold=True
            )

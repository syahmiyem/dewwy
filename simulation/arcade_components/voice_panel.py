import arcade
import time

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
    
    def draw(self, x, y, width=300, height=200):
        """Draw the voice recognition panel"""
        # Background panel
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (0, 0, 0, 150)  # Semi-transparent black
        )
        
        # Title
        arcade.draw_text(
            "Voice Recognition",
            x - width/2 + 10, y + height/2 - 20,
            arcade.color.WHITE,
            16
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
            x - width/2 + 10, y + height/2 - 50,
            status_color,
            14
        )
        
        # Draw listening animation
        if self.voice_active:
            center_x = x - width/2 + 30
            center_y = y + height/2 - 80
            
            # Calculate animation values
            import math
            bar_count = 5
            for i in range(bar_count):
                # Calculate height based on sine wave with offset per bar
                bar_height = 6.0 + 5.0 * math.sin(self.listening_animation + i * 0.8)
                
                arcade.draw_rectangle_filled(
                    center_x + i * 10, 
                    center_y,
                    4, 
                    bar_height,
                    arcade.color.ELECTRIC_GREEN
                )
        
        # Wake word button
        wake_button_y = y + height/2 - 110
        arcade.draw_rectangle_filled(
            x - width/2 + 70, wake_button_y,
            120, 30,
            arcade.color.DARK_BLUE
        )
        
        arcade.draw_text(
            f"Say \"{self.wake_word}\"",
            x - width/2 + 20, wake_button_y - 7,
            arcade.color.WHITE,
            12
        )
        
        # Command selector
        command_y = y + height/2 - 150
        arcade.draw_rectangle_filled(
            x, command_y,
            width - 20, 30,
            arcade.color.DARK_SLATE_GRAY
        )
        
        arcade.draw_text(
            f"Test: {self.get_selected_command()}",
            x - width/2 + 20, command_y - 7,
            arcade.color.WHITE,
            12
        )
        
        # Left/right indicators for selection
        arcade.draw_text(
            "◀",
            x - width/2 + 10, command_y - 7,
            arcade.color.LIGHT_GRAY,
            12
        )
        
        arcade.draw_text(
            "▶",
            x + width/2 - 20, command_y - 7,
            arcade.color.LIGHT_GRAY,
            12
        )
        
        # Command history
        history_y = y - height/2 + 80
        arcade.draw_text(
            "Command History:",
            x - width/2 + 10, history_y,
            arcade.color.LIGHT_BLUE,
            12
        )
        
        for i, cmd in enumerate(self.last_commands):
            arcade.draw_text(
                f"{cmd['time']}: {cmd['command']}",
                x - width/2 + 10, history_y - 20 - (i * 20),
                arcade.color.WHITE,
                10
            )
        
        # Feedback for executed command
        if self.command_feedback:
            arcade.draw_rectangle_filled(
                x, y - height/2 + 30,
                width - 20, 30,
                arcade.color.DARK_GREEN
            )
            
            arcade.draw_text(
                f"Executed: {self.command_feedback}",
                x - width/2 + 20, y - height/2 + 23,
                arcade.color.WHITE,
                12
            )

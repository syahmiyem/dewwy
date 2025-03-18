import threading
import time
import random

class CommandProcessor:
    """Process voice commands and convert them to robot behaviors"""
    
    # Move command_keywords to class level for accessibility
    command_keywords = {
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
    
    def __init__(self, voice_recognizer=None, state_machine=None, personality=None):
        self.voice_recognizer = voice_recognizer
        self.state_machine = state_machine
        self.personality = personality
        self.running = False
        self.command_handlers = {
            "come": self._handle_come_command,
            "follow": self._handle_follow_command,
            "stop": self._handle_stop_command,
            "sleep": self._handle_sleep_command,
            "wake": self._handle_wake_command,
            "play": self._handle_play_command,
            "praise": self._handle_praise_command,
            "sit": self._handle_sit_command,
            "turn": self._handle_turn_command,
            "forward": self._handle_forward_command,
            "backward": self._handle_backward_command,
            "dance": self._handle_dance_command
        }
    
    def start(self):
        """Start the command processor"""
        if not self.voice_recognizer:
            print("Error: No voice recognizer provided")
            return False
        
        self.running = True
        self.processor_thread = threading.Thread(target=self._processing_loop)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        print("Command processor started")
        return True
    
    def stop(self):
        """Stop the command processor"""
        self.running = False
        if hasattr(self, 'processor_thread') and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=1.0)
        print("Command processor stopped")
    
    def _processing_loop(self):
        """Main processing loop for voice commands"""
        while self.running:
            # Get next command with timeout
            command = self.voice_recognizer.get_next_command(block=True, timeout=0.5)
            if command:
                print(f"Processing command: {command}")
                self._process_command(command)
    
    def _process_command(self, command):
        """Process a recognized command"""
        # Check if we have a handler for this command
        if command in self.command_handlers:
            try:
                # Call the appropriate handler
                self.command_handlers[command]()
                
                # Respond to the command 
                self._respond_to_command(command, success=True)
            except Exception as e:
                print(f"Error processing command '{command}': {e}")
                self._respond_to_command(command, success=False)
        else:
            print(f"Unknown command: {command}")
    
    def _respond_to_command(self, command, success=True):
        """Respond to a command with appropriate behavior"""
        if not self.personality:
            return
            
        # Based on command and success, set an appropriate emotion
        if success:
            from raspberry_pi.behavior.robot_personality import Emotion
            
            if command in ["praise"]:
                # Happy response to praise
                self.personality.set_emotion(Emotion.HAPPY)
            elif command in ["play", "dance"]:
                # Excited for fun commands
                self.personality.set_emotion(Emotion.EXCITED)
            elif command in ["sleep"]:
                # Sleepy for sleep command
                self.personality.set_emotion(Emotion.SLEEPY)
            else:
                # General positive response
                self.personality.set_emotion(random.choice([Emotion.HAPPY, Emotion.NEUTRAL]))
        else:
            # If command failed, show confusion
            from raspberry_pi.behavior.robot_personality import Emotion
            self.personality.set_emotion(Emotion.CURIOUS)
    
    # Command handlers
    
    def _handle_come_command(self):
        """Handle 'come' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.ROAMING)
    
    def _handle_follow_command(self):
        """Handle 'follow' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            # This would be a new state we'd need to implement
            # For now transition to ROAMING as a close approximation
            self.state_machine.transition_to(RobotState.ROAMING)
    
    def _handle_stop_command(self):
        """Handle 'stop' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.IDLE)
    
    def _handle_sleep_command(self):
        """Handle 'sleep' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.SLEEPING)
    
    def _handle_wake_command(self):
        """Handle 'wake' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.IDLE)
    
    def _handle_play_command(self):
        """Handle 'play' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.PLAYING)
    
    def _handle_praise_command(self):
        """Handle praise command"""
        if self.personality:
            from raspberry_pi.behavior.robot_personality import Emotion
            self.personality.set_emotion(Emotion.HAPPY)
    
    def _handle_sit_command(self):
        """Handle 'sit' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.IDLE)
    
    def _handle_turn_command(self):
        """Handle 'turn' command"""
        if hasattr(self, 'motors') and self.motors:
            # Make the robot turn around
            self.motors.turn_left(0.5)
            time.sleep(0.5)
            self.motors.stop()
    
    def _handle_forward_command(self):
        """Handle 'forward' command"""
        if hasattr(self, 'motors') and self.motors:
            # Make the robot move forward
            self.motors.move_forward(0.5)
            time.sleep(0.5)
            self.motors.stop()
    
    def _handle_backward_command(self):
        """Handle 'backward' command"""
        if hasattr(self, 'motors') and self.motors:
            # Make the robot move backward
            self.motors.move_backward(0.5)
            time.sleep(0.5)
            self.motors.stop()
    
    def _handle_dance_command(self):
        """Handle 'dance' command"""
        if self.state_machine:
            from raspberry_pi.behavior.state_machine import RobotState
            self.state_machine.transition_to(RobotState.PLAYING)

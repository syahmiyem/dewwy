import arcade
import math
import sys
import os
import random
import time
import threading
import queue

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from simulation.arcade_components import (
    EmotionDisplay, 
    Dashboard, 
    SerialMonitor, 
    UltrasonicSensor, 
    MotorController,
    VoiceRecognitionPanel,
    ControlsPanel
)

# Import layout helper and component classes
from simulation.arcade_components.layout_helper import LayoutHelper
from simulation.arcade_components.robot_component import RobotComponent
from simulation.arcade_components.environment_component import EnvironmentComponent
from simulation.arcade_components.input_handler import InputHandler

# Try to import voice recognition components
try:
    from raspberry_pi.audio.microphone_interface import MicrophoneInterface
    from raspberry_pi.audio.voice_recognition import VoiceRecognizer
    from raspberry_pi.audio.command_processor import CommandProcessor
    voice_recognition_available = True
except ImportError:
    try:
        from raspberry_pi.audio.fallback_recognition import SimpleMicrophoneInterface as MicrophoneInterface
        from raspberry_pi.audio.fallback_recognition import SimpleVoiceRecognizer as VoiceRecognizer
        voice_recognition_available = True
    except ImportError:
        print("Voice recognition components not available")
        voice_recognition_available = False

class ArcadeSimulator(arcade.Window):
    """Robot simulator using the Arcade library"""
    
    def __init__(self, width=800, height=600, title="Dewwy - Pet Robot Simulator"):
        super().__init__(width, height, title)
        
        arcade.set_background_color(arcade.color.WHITE)
        
        # Store width and height for reference
        self.width = width
        self.height = height
        
        # Create layout helper for consistent positioning
        self.layout = LayoutHelper(width, height)
        
        # Initialize components
        self.robot = RobotComponent(self, width // 2, height // 2, 50)
        self.environment = EnvironmentComponent(width, height)
        self.input_handler = InputHandler(self)
        
        # Legacy attributes for backward compatibility
        self.robot_x = self.robot.x
        self.robot_y = self.robot.y
        self.robot_radius = self.robot.radius
        self.robot_direction = self.robot.direction
        self.current_state = self.robot.current_state
        self.current_emotion = self.robot.current_emotion
        
        # Keep obstacle data for compatibility
        self.border_obstacles = self.environment.border_obstacles
        self.interior_obstacles = self.environment.interior_obstacles
        self.obstacles = self.environment.obstacles
        
        # Sensor properties
        self.sensor_range = self.robot.sensor_range
        self.last_distance = self.robot.last_distance
        
        # Interface controls
        self.autopilot = True
        self.keys_pressed = self.input_handler.keys_pressed
        
        # Initialize UI components
        self.emotion_display = EmotionDisplay()
        self.dashboard = Dashboard()
        self.serial_monitor = SerialMonitor()
        self.voice_panel = VoiceRecognitionPanel()
        self.controls_panel = ControlsPanel()
        
        # Connect the emotion display to the robot
        self.robot.emotion_display = self.emotion_display
        
        # Create sensor and motors using the component versions
        self.sensor = UltrasonicSensor(self)
        self.motors = MotorController(self)
        
        # Serial communication state
        self.serial_active = False
        self.last_serial_activity = time.time()
        
        # Component status
        self.component_status = {
            "battery": 100,  # Battery level percentage
            "cpu_usage": 0,  # CPU usage percentage
            "temperature": 25.0,  # Temperature in Celsius
            "memory_used": 0,  # Memory usage percentage
        }
        
        # UI controls
        self.show_dashboard = True
        self.show_serial_monitor = False
        self.show_voice_panel = True
        self.show_controls_help = False
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        
        # Worker thread for time-consuming operations
        self.worker_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.worker_thread.start()
        
        # Initialize voice recognition if available
        self.voice_recognizer = None
        self.microphone = None
        self.command_processor = None
        
        if voice_recognition_available:
            self._init_voice_recognition()
            
        print("Arcade simulator initialized successfully")
    
    def _init_voice_recognition(self):
        """Initialize the voice recognition system"""
        try:
            # Create the microphone and voice recognizer
            self.microphone = MicrophoneInterface(simulation=True)
            self.voice_recognizer = VoiceRecognizer(microphone=self.microphone, simulation=True)
            
            # Start the microphone in the background
            self.microphone.start_listening()
            self.voice_recognizer.start()
            
            # Create a thread to check for voice commands
            self.voice_thread = threading.Thread(target=self._voice_command_loop)
            self.voice_thread.daemon = True
            self.voice_thread.start()
            
            print("Voice recognition initialized successfully")
        except Exception as e:
            print(f"Error initializing voice recognition: {e}")
            import traceback
            traceback.print_exc()
    
    def _voice_command_loop(self):
        """Background thread to check for voice commands"""
        while True:
            if self.voice_recognizer:
                try:
                    # Check for commands
                    command = self.voice_recognizer.get_next_command(block=False)
                    
                    if command:
                        print(f"Voice command detected: {command}")
                        # Add the command to the panel
                        self.voice_panel.add_command(command)
                        self.voice_panel.show_command_feedback(command)
                        
                        # Handle the command (similar to command processor)
                        self._handle_voice_command(command)
                        
                except Exception as e:
                    print(f"Error checking voice commands: {e}")
            
            time.sleep(0.2)  # Check every 200ms
    
    def _handle_voice_command(self, command):
        """Handle a recognized voice command"""
        from raspberry_pi.behavior.state_machine import RobotState
        from raspberry_pi.behavior.robot_personality import Emotion
        
        # Map commands to actions
        if command == "stop":
            self.motors.stop()
            self.current_state = "Idle"
        elif command == "come" or command == "follow":
            self.motors.move_forward(0.5)
            self.current_state = "Roaming" 
        elif command == "sleep":
            self.current_state = "Sleeping"
            self.current_emotion = "sleepy"
        elif command == "wake":
            self.current_state = "Idle"
            self.current_emotion = "neutral"
        elif command == "play" or command == "dance":
            self.current_state = "Playing"
            self.current_emotion = "excited"
        elif command == "praise":
            self.current_emotion = "happy"
        elif command == "turn":
            self.motors.turn_right(0.5)
            time.sleep(0.5)
            self.motors.stop()
        elif command == "forward":
            self.motors.move_forward(0.5)
        elif command == "backward":
            self.motors.move_backward(0.5)
        elif command == "sit":
            self.motors.stop()
            self.current_state = "Idle"
    
    def calculate_distance(self):
        """Calculate distance to nearest obstacle - delegate to environment component"""
        return self.environment.calculate_distance(
            self.robot.x, self.robot.y, 
            self.robot.direction, 
            self.robot.sensor_range
        )
    
    def _worker_thread(self):
        """Background thread for non-critical operations"""
        while True:
            try:
                # Get task from queue with timeout
                task, args = self.worker_queue.get(timeout=0.5)
                task(*args)
                self.worker_queue.task_done()
            except queue.Empty:
                # No tasks, update system metrics
                self._update_system_metrics()
            except Exception as e:
                print(f"Error in worker thread: {e}")
            time.sleep(0.01)
    
    def _update_system_metrics(self):
        """Update simulated system metrics"""
        # Battery decreases
        self.component_status["battery"] -= random.uniform(0, 0.05)
        if self.component_status["battery"] < 0:
            self.component_status["battery"] = 100
            
        # CPU usage based on state
        target_cpu = 30
        if self.current_state == "Avoiding":
            target_cpu = 70
        
        # Smooth CPU changes
        current = self.component_status["cpu_usage"]
        self.component_status["cpu_usage"] = current * 0.9 + target_cpu * 0.1
        
        # Temperature correlates with CPU
        current_temp = self.component_status["temperature"]
        target_temp = 25 + (self.component_status["cpu_usage"] / 100) * 15
        self.component_status["temperature"] = current_temp * 0.98 + target_temp * 0.02
        
        # Memory usage
        self.component_status["memory_used"] = min(100, max(0, 
            self.component_status["memory_used"] + random.uniform(-0.5, 0.5)))
        
        # Update dashboard with latest metrics
        self.dashboard.update_status(self.component_status)
        self.dashboard.set_serial_active(self.serial_active)
    
    def add_serial_message(self, message, direction="rx"):
        """Add a message to either RX or TX history"""
        # Add to the serial monitor component instead of internal lists
        self.serial_monitor.add_message(message, direction)
        
        # Update serial activity status
        self.serial_active = True
        self.last_serial_activity = time.time()
    
    def on_draw(self):
        """Render the screen - This runs on the main thread"""
        # Track performance
        self.frame_count += 1
        now = time.time()
        if now - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = now
        
        # Clear screen and start drawing
        self.clear()
        
        # Set a light background for the entire window
        arcade.draw_rectangle_filled(
            self.width / 2, self.height / 2,
            self.width, self.height,
            arcade.color.LIGHT_GRAY
        )
        
        # Draw the environment (obstacles, etc.)
        self.environment.draw(self.layout)
        
        # Draw the robot
        self.robot.draw()
        
        # ==============================================
        # STATUS CONTAINER - TOP BAR
        # ==============================================
        # Get top bar region from layout helper
        top_bar = self.layout.top_bar_region
        
        # Draw the status bar
        arcade.draw_rectangle_filled(
            top_bar["x"], top_bar["y"],
            top_bar["width"], top_bar["height"],
            (40, 44, 52, 230)  # Dark semi-transparent background
        )
        
        # Draw status information in the status bar
        status_y = self.height - 30
        
        # Distance reading
        arcade.draw_text(
            f"Distance: {self.robot.last_distance:.1f}px",
            20, status_y,
            arcade.color.WHITE,
            16
        )
        
        # Robot state - Use an estimated width instead of measure_text
        state_text = f"State: {self.robot.current_state}"
        # Estimate width based on character count (rough approximation)
        estimated_width = len(state_text) * 9  # ~9 pixels per character at font size 16
        arcade.draw_text(
            state_text,
            (self.width - estimated_width) / 2, status_y,
            arcade.color.WHITE,
            16
        )
        
        # FPS counter
        arcade.draw_text(
            f"FPS: {self.fps}",
            self.width - 100, status_y,
            arcade.color.WHITE,
            16
        )
        
        # Mode indicator (autopilot)
        mode_text = "Autopilot: ON" if self.autopilot else "Manual Control"
        arcade.draw_text(
            mode_text,
            self.width - 250, status_y,
            arcade.color.GREEN if self.autopilot else arcade.color.YELLOW,
            14
        )
        
        # Add help hint (H key) in the status bar
        arcade.draw_text(
            "Press H for Controls",
            20, status_y - 20,
            arcade.color.LIGHT_GRAY,
            12
        )
        
        # ==============================================
        # RIGHT SIDE PANELS
        # ==============================================
        # Heading for right side panel area
        right_area_x = self.layout.left_width + (self.layout.right_width // 2)
        arcade.draw_text(
            "CONTROLS & MONITORING",
            right_area_x - 120, self.height - 80,
            arcade.color.DARK_BLUE,
            16,
            bold=True
        )
        
        # Voice panel (top-right)
        if self.show_voice_panel:
            voice_region = self.layout.voice_panel_region
            self.voice_panel.draw(
                voice_region["x"],
                voice_region["y"],
                voice_region["width"],
                voice_region["height"]
            )
        
        # Dashboard (middle-right)
        if self.show_dashboard:
            dashboard_region = self.layout.dashboard_region
            self.dashboard.draw(
                dashboard_region["x"],
                dashboard_region["y"],
                dashboard_region["width"],
                dashboard_region["height"]
            )
        
        # Serial monitor (can be toggled with dashboard)
        if self.show_serial_monitor:
            serial_region = self.layout.serial_monitor_region
            self.serial_monitor.draw(
                serial_region["x"],
                serial_region["y"],
                serial_region["width"],
                serial_region["height"]
            )
        
        # Controls/help panel (bottom-right)
        help_region = self.layout.help_region
        self.controls_panel.draw(
            help_region["x"], 
            help_region["y"],
            help_region["width"],
            help_region["height"]
        )
    
    def on_update(self, delta_time):
        """Update simulation state - keep this light and fast"""
        # Check if serial connection is still active
        if time.time() - self.last_serial_activity > 1.0:
            self.serial_active = False
        
        # Check if robot is in sleep state - if so, stop all movement
        if self.robot.current_emotion == "sleepy":
            self.robot.stop()
            self.robot.current_state = "Sleeping"
            return
            
        # Sample current position periodically for stuck detection
        current_time = time.time()
        if current_time - self.robot.stuck_detection["position_sample_time"] > 1.0:
            self.robot.stuck_detection["position_sample_time"] = current_time
            self.robot.check_if_stuck()
        
        # Process keyboard input
        self.input_handler.process_update()
        
        # Distance reading - do this every frame
        distance = self.sensor.measure_distance()
        self.robot.last_distance = distance
        self.last_distance = distance
        
        # Periodically add distance reading to serial monitor
        if random.random() < 0.05:  # 5% chance per frame
            self.add_serial_message(f"DIST:{int(distance)}", "rx")
        
        # Autopilot control (only if enabled)
        if self.autopilot:
            self.handle_autopilot(distance)
        
        # Keep robot within screen bounds
        self.robot.constrain_to_bounds(self.width, self.height)
        
        # Update the voice panel
        self.voice_panel.update()

        # Update legacy attributes for backward compatibility
        self.robot_x = self.robot.x
        self.robot_y = self.robot.y
        self.robot_direction = self.robot.direction
        self.current_state = self.robot.current_state
        self.current_emotion = self.robot.current_emotion

    def handle_autopilot(self, distance):
        """Handle autopilot navigation with improved obstacle avoidance"""
        # Let the robot component handle obstacle avoidance
        if self.robot.handle_obstacle_avoidance(distance):
            # Robot is handling obstacle avoidance
            return
            
        # Normal roaming behavior
        if random.random() < 0.01:  # Occasional random turn
            if random.choice([True, False]):
                self.robot.turn_left(0.2)
            else:
                self.robot.turn_right(0.2)
        else:
            # Move forward by default
            self.robot.move_forward(0.3)
        
        self.robot.current_state = "Roaming"

    def on_key_press(self, key, modifiers):
        """Handle key presses - delegate to input handler"""
        self.input_handler.process_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        """Handle key releases - delegate to input handler"""
        self.input_handler.process_key_release(key, modifiers)

    def set_state_and_emotion(self, state, emotion):
        """Update the state and emotion display"""
        self.robot.set_state_and_emotion(state, emotion)
        # Update legacy attributes
        self.current_state = state
        self.current_emotion = emotion.lower() if emotion else "neutral"

    def close(self):
        """Clean shutdown"""
        print("Closing simulator window")
        
        # Shutdown voice recognition if active
        if hasattr(self, 'voice_recognizer') and self.voice_recognizer:
            self.voice_recognizer.stop()
        
        if hasattr(self, 'microphone') and self.microphone:
            self.microphone.shutdown()

def run_simulator():
    simulator = ArcadeSimulator()
    arcade.run()

if __name__ == "__main__":
    run_simulator()

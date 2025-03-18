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

# Import layout helper
from simulation.arcade_components.layout_helper import LayoutHelper

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
        
        # Create layout helper for consistent positioning
        self.layout = LayoutHelper(width, height)
        
        # Robot state
        self.robot_x = width // 2
        self.robot_y = height // 2
        self.robot_radius = 50
        self.robot_direction = 0  # 0 radians = facing right
        
        # Create border obstacles with some thickness
        wall_thickness = 20
        self.border_obstacles = [
            # Left wall
            [0, 0, wall_thickness, height],
            # Right wall
            [width - wall_thickness, 0, wall_thickness, height],
            # Top wall
            [0, height - wall_thickness, width, wall_thickness],
            # Bottom wall
            [0, 0, width, wall_thickness]
        ]
        
        # Interior obstacles - format: [x, y, width, height]
        self.interior_obstacles = [
            [100, 100, 100, 100],
            [600, 400, 100, 100],
            [300, 500, 200, 50],
            [700, 100, 80, 150]
        ]
        
        # All obstacles (combine border and interior obstacles)
        self.obstacles = self.border_obstacles + self.interior_obstacles
        
        # Sensor properties
        self.sensor_range = 200
        self.last_distance = 100
        
        # Status information
        self.current_state = "Initializing"
        self.current_emotion = "neutral"
        
        # Interface controls
        self.autopilot = True
        self.keys_pressed = set()
        
        # Initialize components
        self.emotion_display = EmotionDisplay()
        self.dashboard = Dashboard()
        self.serial_monitor = SerialMonitor()
        self.voice_panel = VoiceRecognitionPanel()
        self.controls_panel = ControlsPanel()  # Add controls panel
        
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
        self.show_controls_help = False  # Add control for help panel visibility
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        
        # Worker thread for time-consuming operations
        self.worker_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.worker_thread.start()
        
        # Add variables to track obstacle avoidance behavior
        self.avoiding_obstacle = False
        self.avoidance_start_time = 0
        self.avoidance_turn_direction = None  # Will be set to "left" or "right"
        self.avoidance_step = 0  # 0=backup, 1=turn, 2=move forward
        self.stuck_detection = {
            "last_positions": [],  # Store recent positions
            "position_sample_time": 0,  # When we last sampled position
            "stuck_count": 0  # Counter for being stuck in same area
        }
        
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
        """Calculate distance to nearest obstacle"""
        # Simple optimized distance calculation
        min_distance = self.sensor_range
        
        # Direction vector
        dx = math.cos(self.robot_direction)
        dy = math.sin(self.robot_direction)
        
        for obs in self.obstacles:
            rect_x, rect_y, rect_w, rect_h = obs
            
            # Simplified ray-box intersection
            # Only check if the ray is pointing toward the obstacle
            # This reduces unnecessary calculations
            box_center_x = rect_x + rect_w/2
            box_center_y = rect_y + rect_h/2
            
            # Vector from robot to box center
            to_box_x = box_center_x - self.robot_x
            to_box_y = box_center_y - self.robot_y
            
            # If ray is pointing somewhat toward the box
            dot_product = dx * to_box_x + dy * to_box_y
            if dot_product > 0:
                # Now do the actual intersection check
                distance = self._ray_box_intersection(
                    self.robot_x, self.robot_y, dx, dy,
                    rect_x, rect_y, rect_x + rect_w, rect_y + rect_h
                )
                if distance and distance < min_distance:
                    min_distance = distance
        
        # Add minor noise
        noise = random.uniform(-min_distance * 0.03, min_distance * 0.03)
        result = max(5, min(min_distance + noise, self.sensor_range))
        
        self.last_distance = result
        return result
    
    def _ray_box_intersection(self, ray_x, ray_y, ray_dx, ray_dy, min_x, min_y, max_x, max_y):
        """Optimized ray-box intersection algorithm"""
        t_min = float('-inf')
        t_max = float('inf')
        
        # X planes
        if abs(ray_dx) < 1e-8:
            if ray_x < min_x or ray_x > max_x:
                return None
        else:
            t1 = (min_x - ray_x) / ray_dx
            t2 = (max_x - ray_x) / ray_dx
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            if t_min > t_max or t_max < 0:
                return None
        
        # Y planes
        if abs(ray_dy) < 1e-8:
            if ray_y < min_y or ray_y > max_y:
                return None
        else:
            t1 = (min_y - ray_y) / ray_dy
            t2 = (max_y - ray_y) / ray_dy
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            if t_min > t_max or t_max < 0:
                return None
        
        # Return distance to closest intersection
        if t_min > 0:
            return t_min * math.sqrt(ray_dx*ray_dx + ray_dy*ray_dy)
        return t_max * math.sqrt(ray_dx*ray_dx + ray_dy*ray_dy)
    
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
        
        # ==============================================
        # ROBOT VISUALIZATION CONTAINER (LEFT SIDE)
        # ==============================================
        # Get environment region from layout helper
        env = self.layout.environment_region
        
        # Draw environment container background
        arcade.draw_rectangle_filled(
            env["x"], env["y"],
            env["width"], env["height"],
            (200, 210, 230)  # Custom light blue-gray RGB color
        )
        
        # Draw environment border
        arcade.draw_rectangle_outline(
            env["x"], env["y"],
            env["width"], env["height"],
            arcade.color.DARK_BLUE,
            2
        )
        
        # Draw border obstacles within environment
        for obs in self.border_obstacles:
            arcade.draw_rectangle_filled(
                obs[0] + obs[2]/2, obs[1] + obs[3]/2,
                obs[2], obs[3],
                arcade.color.DARK_BLUE
            )
        
        # Draw interior obstacles within environment
        for obs in self.interior_obstacles:
            arcade.draw_rectangle_filled(
                obs[0] + obs[2]/2, obs[1] + obs[3]/2,
                obs[2], obs[3],
                arcade.color.RED
            )
        
        # Draw robot
        arcade.draw_circle_filled(
            self.robot_x, self.robot_y, 
            self.robot_radius, 
            arcade.color.LIGHT_BLUE
        )
        
        arcade.draw_circle_outline(
            self.robot_x, self.robot_y,
            self.robot_radius,
            arcade.color.BLUE,
            3
        )
        
        # Draw emotion display using the component
        self.emotion_display.draw(self.robot_x, self.robot_y, self.current_emotion)
        
        # Draw direction indicator
        end_x = self.robot_x + math.cos(self.robot_direction) * self.robot_radius
        end_y = self.robot_y + math.sin(self.robot_direction) * self.robot_radius
        arcade.draw_line(
            self.robot_x, self.robot_y,
            end_x, end_y,
            arcade.color.GREEN,
            4
        )
        
        # Draw sensor beam
        beam_length = min(self.last_distance, self.sensor_range)
        beam_end_x = self.robot_x + math.cos(self.robot_direction) * beam_length
        beam_end_y = self.robot_y + math.sin(self.robot_direction) * beam_length
        
        arcade.draw_line(
            self.robot_x, self.robot_y,
            beam_end_x, beam_end_y,
            arcade.color.ORANGE,
            2
        )
        
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
            f"Distance: {self.last_distance:.1f}px",
            20, status_y,
            arcade.color.WHITE,
            16
        )
        
        # Robot state - Use an estimated width instead of measure_text
        state_text = f"State: {self.current_state}"
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
        if self.current_emotion == "sleepy":
            self.motors.stop()
            self.current_state = "Sleeping"
            return
            
        # Sample current position periodically for stuck detection
        current_time = time.time()
        if current_time - self.stuck_detection["position_sample_time"] > 1.0:
            self.stuck_detection["position_sample_time"] = current_time
            self.check_if_stuck()
        
        # Process keyboard input
        if arcade.key.UP in self.keys_pressed:
            self.motors.move_forward(0.5)
            self.add_serial_message("FWD command", "tx")
        elif arcade.key.DOWN in self.keys_pressed:
            self.motors.move_backward(0.5)
            self.add_serial_message("BCK command", "tx")
        elif arcade.key.LEFT in self.keys_pressed:
            self.motors.turn_left(0.5)
            self.add_serial_message("LFT command", "tx")
        elif arcade.key.RIGHT in self.keys_pressed:
            self.motors.turn_right(0.5)
            self.add_serial_message("RGT command", "tx")
        
        # Distance reading - do this every frame
        distance = self.sensor.measure_distance()
        
        # Periodically add distance reading to serial monitor
        if random.random() < 0.05:  # 5% chance per frame
            self.add_serial_message(f"DIST:{int(distance)}", "rx")
        
        # Autopilot control (only if enabled)
        if self.autopilot:
            self.handle_autopilot(distance)
        
        # Keep robot within screen bounds
        self._constrain_to_bounds()
        
        # Update the voice panel
        self.voice_panel.update()

    def handle_autopilot(self, distance):
        """Handle autopilot navigation with improved obstacle avoidance"""
        # If we're currently in an obstacle avoidance maneuver
        if self.avoiding_obstacle:
            self.execute_avoidance_maneuver()
            return
            
        # Start obstacle avoidance if distance is too close
        if distance < 80:  # Increased detection distance for earlier response
            # Begin a new avoidance maneuver
            self.start_avoidance_maneuver()
            self.current_state = "Avoiding"
        else:
            # Normal roaming behavior
            if random.random() < 0.01:  # 1% chance per update
                if random.choice([True, False]):
                    self.motors.turn_left(0.1)
                else:
                    self.motors.turn_right(0.1)
            else:
                self.motors.move_forward(0.2)
            self.current_state = "Roaming"

    def start_avoidance_maneuver(self):
        """Start a new obstacle avoidance maneuver"""
        self.avoiding_obstacle = True
        self.avoidance_start_time = time.time()
        self.avoidance_step = 0  # Start with backing up
        
        # Choose a turn direction, with bias away from edges
        center_x = self.width / 2
        if self.robot_x < center_x:
            # If on left side, bias toward turning right
            self.avoidance_turn_direction = "right" if random.random() < 0.7 else "left"
        else:
            # If on right side, bias toward turning left
            self.avoidance_turn_direction = "left" if random.random() < 0.7 else "right"
            
        # If we've been getting stuck, make more dramatic turns
        turn_multiplier = min(1.0 + (self.stuck_detection["stuck_count"] * 0.3), 2.5)
        self.avoidance_turn_angle = random.uniform(0.8, 1.5) * turn_multiplier

    def execute_avoidance_maneuver(self):
        """Execute the ongoing obstacle avoidance maneuver"""
        current_time = time.time()
        elapsed = current_time - self.avoidance_start_time
        
        if self.avoidance_step == 0:
            # Step 0: Back up briefly to get away from the obstacle
            self.motors.move_backward(0.5)
            self.add_serial_message("BCK (Auto)", "tx")
            
            # Move to next step after backing up for a short time
            if elapsed > 0.3:
                self.avoidance_step = 1
                self.avoidance_start_time = current_time
                
        elif self.avoidance_step == 1:
            # Step 1: Turn in the chosen direction
            turn_duration = self.avoidance_turn_angle  # Time to turn is based on desired angle
            
            if self.avoidance_turn_direction == "left":
                self.motors.turn_left(1.0)  # Turn at full speed
                self.add_serial_message("LFT (Auto)", "tx")
            else:
                self.motors.turn_right(1.0)  # Turn at full speed
                self.add_serial_message("RGT (Auto)", "tx")
                
            # Move to next step after turning for the calculated duration
            if elapsed > turn_duration:
                self.avoidance_step = 2
                self.avoidance_start_time = current_time
                
        elif self.avoidance_step == 2:
            # Step 2: Move forward to find a clear path
            self.motors.move_forward(0.4)
            
            # Take a new distance reading
            new_distance = self.sensor.measure_distance()
            
            # If we encounter another obstacle immediately, restart avoidance
            if new_distance < 60:
                self.start_avoidance_maneuver()
                return
                
            # Otherwise, finish the maneuver after moving forward for a bit
            if elapsed > 0.5:
                self.avoiding_obstacle = False
                self.current_state = "Roaming"

    def check_if_stuck(self):
        """Check if the robot is stuck in the same area"""
        # Add current position to history
        current_pos = (int(self.robot_x), int(self.robot_y))
        self.stuck_detection["last_positions"].append(current_pos)
        
        # Keep only the last 5 positions
        if len(self.stuck_detection["last_positions"]) > 5:
            self.stuck_detection["last_positions"].pop(0)
            
        # If we have enough samples, check if they're all close together
        if len(self.stuck_detection["last_positions"]) >= 5:
            # Calculate maximum distance between any two points
            max_distance = 0
            for pos1 in self.stuck_detection["last_positions"]:
                for pos2 in self.stuck_detection["last_positions"]:
                    dist = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
                    max_distance = max(max_distance, dist)
            
            # If all positions are within a small range, we're stuck
            if max_distance < 20:
                self.stuck_detection["stuck_count"] += 1
                
                # If we've been stuck multiple times, do a more drastic maneuver
                if self.stuck_detection["stuck_count"] > 2:
                    # Clear our current path and do something random
                    self.start_avoidance_maneuver()
            else:
                # Reset stuck counter if we're moving normally
                self.stuck_detection["stuck_count"] = max(0, self.stuck_detection["stuck_count"] - 1)

    def _constrain_to_bounds(self):
        """Keep the robot within the screen bounds"""
        margin = self.robot_radius
        
        if self.robot_x < margin:
            self.robot_x = margin
        elif self.robot_x > self.width - margin:
            self.robot_x = self.width - margin
            
        if self.robot_y < margin:
            self.robot_y = margin
        elif self.robot_y > self.height - margin:
            self.robot_y = self.height - margin
    
    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        self.keys_pressed.add(key)
        
        if key == arcade.key.SPACE:
            self.motors.stop()
            self.add_serial_message("STP command", "tx")
        elif key == arcade.key.A:
            # Toggle autopilot
            self.autopilot = not self.autopilot
            self.add_serial_message(f"Autopilot {'ON' if self.autopilot else 'OFF'}", "tx")
        elif key == arcade.key.R:
            # Reset robot position
            self.robot_x = self.width // 2
            self.robot_y = self.height // 2
            self.robot_direction = 0
        elif key == arcade.key.S:
            # Toggle serial monitor
            self.show_serial_monitor = not self.show_serial_monitor
        elif key == arcade.key.D:
            # Toggle dashboard
            self.show_dashboard = not self.show_dashboard
        elif key == arcade.key.V:
            # Toggle voice panel
            self.show_voice_panel = not self.show_voice_panel
        elif key == arcade.key.H:
            # Toggle help/controls panel
            self.controls_panel.toggle()
        elif key == arcade.key.W:
            # Simulate wake word
            if self.show_voice_panel:
                self.voice_panel.activate_wake_word()
        elif key == arcade.key.C:
            # Execute the selected test command
            if self.show_voice_panel:
                command = self.voice_panel.get_selected_command()
                self._handle_voice_command(command)
                self.voice_panel.show_command_feedback(command)
        elif key == arcade.key.LEFT:
            if self.show_voice_panel and modifiers & arcade.key.MOD_SHIFT:
                # Previous test command
                self.voice_panel.select_prev_command()
            else:
                # Turn robot left
                self.motors.turn_left(0.5)
                self.add_serial_message("LFT command", "tx")
        elif key == arcade.key.RIGHT:
            if self.show_voice_panel and modifiers & arcade.key.MOD_SHIFT:
                # Next test command
                self.voice_panel.select_next_command()
            else:
                # Turn robot right
                self.motors.turn_right(0.5)
                self.add_serial_message("RGT command", "tx")
        elif key == arcade.key.Q or key == arcade.key.ESCAPE:
            print("Exit key pressed - closing window")
            self.close()
            arcade.exit()
    
    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def set_state_and_emotion(self, state, emotion):
        """Update the state and emotion display"""
        self.current_state = state
        self.current_emotion = emotion.lower() if emotion else "neutral"
    
    def close(self):
        """Clean shutdown"""
        print("Closing simulator window")
        
        # Shutdown voice recognition if active
        if self.voice_recognizer:
            self.voice_recognizer.stop()
        if self.microphone:
            self.microphone.shutdown()

def run_simulator():
    simulator = ArcadeSimulator()
    arcade.run()

if __name__ == "__main__":
    run_simulator()

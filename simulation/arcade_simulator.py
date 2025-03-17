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
    MotorController
)

class ArcadeSimulator(arcade.Window):
    """Robot simulator using the Arcade library"""
    
    def __init__(self, width=800, height=600, title="Dewwy - Pet Robot Simulator"):
        super().__init__(width, height, title)
        
        arcade.set_background_color(arcade.color.WHITE)
        
        # Robot state
        self.robot_x = width // 2
        self.robot_y = height // 2
        self.robot_radius = 50
        self.robot_direction = 0  # 0 radians = facing right
        
        # Obstacles - format: [x, y, width, height]
        self.obstacles = [
            [100, 100, 100, 100],
            [600, 400, 100, 100],
            [300, 500, 200, 50],
            [700, 100, 80, 150]
        ]
        
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
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        
        # Worker thread for time-consuming operations
        self.worker_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.worker_thread.start()
        
        print("Arcade simulator initialized successfully")
    
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
        
        # Draw obstacles
        for obs in self.obstacles:
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
        
        # Draw basic status info (minimal version always visible)
        arcade.draw_text(
            f"Distance: {self.last_distance:.1f}px",
            20, self.height - 30,
            arcade.color.BLACK,
            16
        )
        
        arcade.draw_text(
            f"State: {self.current_state}",
            20, self.height - 60,
            arcade.color.BLACK,
            16
        )
        
        arcade.draw_text(
            f"FPS: {self.fps}",
            self.width - 100, self.height - 30,
            arcade.color.BLACK,
            16
        )
        
        # Draw dashboard if enabled using the component
        if self.show_dashboard:
            self.dashboard.draw(120, 120)
        
        # Draw serial monitor if enabled using the component
        if self.show_serial_monitor:
            self.serial_monitor.draw(self.width - 150, 250)
    
    def on_update(self, delta_time):
        """Update simulation state - keep this light and fast"""
        # Check if serial connection is still active
        if time.time() - self.last_serial_activity > 1.0:
            self.serial_active = False
        
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
            if distance < 50:
                # Obstacle detected - immediately turn in random direction (Roomba style)
                turning_direction = random.choice([True, False])  # True = left, False = right
                if turning_direction:
                    self.motors.turn_left(0.5)  # Increased turn speed for faster response
                    self.add_serial_message("LFT (Auto)", "tx")
                else:
                    self.motors.turn_right(0.5)  # Increased turn speed for faster response
                    self.add_serial_message("RGT (Auto)", "tx")
                self.current_state = "Avoiding"
            else:
                # Occasionally change direction during roaming
                if random.random() < 0.01:  # 1% chance per update
                    if random.choice([True, False]):
                        self.motors.turn_left(0.1)
                    else:
                        self.motors.turn_right(0.1)
                else:
                    self.motors.move_forward(0.2)
                self.current_state = "Roaming"
        
        # Keep robot within screen bounds
        self._constrain_to_bounds()
    
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


def run_simulator():
    simulator = ArcadeSimulator()
    arcade.run()

if __name__ == "__main__":
    run_simulator()

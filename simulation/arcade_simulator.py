import arcade
import math
import sys
import os
import random

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        self.current_emotion = "Neutral"
        
        # Interface controls
        self.autopilot = True
        self.keys_pressed = set()
        
        # Create sensor and motors
        self.sensor = self.create_sensor()
        self.motors = self.create_motors()
        
        print("Arcade simulator initialized")
    
    def create_sensor(self):
        """Create an ultrasonic sensor object compatible with the virtual_sensors interface"""
        class ArcadeUltrasonicSensor:
            def __init__(self, simulator):
                self.simulator = simulator
                
            def measure_distance(self):
                # Calculate distance to nearest obstacle in the direction
                return self.simulator.calculate_distance()
        
        return ArcadeUltrasonicSensor(self)
    
    def create_motors(self):
        """Create a motor controller object compatible with the virtual_motors interface"""
        class ArcadeMotorController:
            def __init__(self, simulator):
                self.simulator = simulator
                self.speed = 0.0
                self.direction = 0.0
            
            def move_forward(self, speed=1.0):
                # Convert speed (0-1) to pixels per frame
                speed_px = speed * 5
                # Update position based on direction
                self.simulator.robot_x += math.cos(self.simulator.robot_direction) * speed_px
                self.simulator.robot_y += math.sin(self.simulator.robot_direction) * speed_px
                
            def move_backward(self, speed=1.0):
                # Convert speed (0-1) to pixels per frame
                speed_px = speed * 5
                # Update position based on opposite direction
                self.simulator.robot_x -= math.cos(self.simulator.robot_direction) * speed_px
                self.simulator.robot_y -= math.sin(self.simulator.robot_direction) * speed_px
            
            def turn_left(self, speed=1.0):
                # Update direction counter-clockwise
                turn_amount = speed * 0.1
                self.simulator.robot_direction -= turn_amount
                
            def turn_right(self, speed=1.0):
                # Update direction clockwise
                turn_amount = speed * 0.1
                self.simulator.robot_direction += turn_amount
            
            def stop(self):
                pass  # No need to do anything in the simulation
        
        return ArcadeMotorController(self)
    
    def calculate_distance(self):
        """Calculate distance to the nearest obstacle in the direction of travel"""
        # Simple ray casting approach
        min_distance = self.sensor_range
        
        # Direction vector
        dx = math.cos(self.robot_direction)
        dy = math.sin(self.robot_direction)
        
        # Check each obstacle
        for obs in self.obstacles:
            rect_x, rect_y, rect_w, rect_h = obs
            
            # Check all 4 sides of the obstacle
            # Top side
            distance = self._ray_line_intersection(
                self.robot_x, self.robot_y, dx, dy,
                rect_x, rect_y, rect_x + rect_w, rect_y
            )
            if distance and distance < min_distance:
                min_distance = distance
                
            # Bottom side
            distance = self._ray_line_intersection(
                self.robot_x, self.robot_y, dx, dy,
                rect_x, rect_y + rect_h, rect_x + rect_w, rect_y + rect_h
            )
            if distance and distance < min_distance:
                min_distance = distance
                
            # Left side
            distance = self._ray_line_intersection(
                self.robot_x, self.robot_y, dx, dy,
                rect_x, rect_y, rect_x, rect_y + rect_h
            )
            if distance and distance < min_distance:
                min_distance = distance
                
            # Right side
            distance = self._ray_line_intersection(
                self.robot_x, self.robot_y, dx, dy,
                rect_x + rect_w, rect_y, rect_x + rect_w, rect_y + rect_h
            )
            if distance and distance < min_distance:
                min_distance = distance
        
        # Add some noise
        noise = random.uniform(-min_distance * 0.05, min_distance * 0.05)
        result = min_distance + noise
        
        # Ensure it's within valid range
        result = max(5, min(result, self.sensor_range))
        
        # Store result for display
        self.last_distance = result
        return result
    
    def _ray_line_intersection(self, ray_x, ray_y, ray_dx, ray_dy, line_x1, line_y1, line_x2, line_y2):
        """Calculate intersection of a ray with a line segment"""
        # Convert line segment to a vector
        line_dx = line_x2 - line_x1
        line_dy = line_y2 - line_y1
        
        # Solve for t and s
        denom = ray_dy * line_dx - ray_dx * line_dy
        
        # If denominator is 0, lines are parallel
        if abs(denom) < 1e-6:
            return None
        
        s = (ray_dx * (line_y1 - ray_y) - ray_dy * (line_x1 - ray_x)) / denom
        
        # If s is outside [0, 1], intersection is not on the line segment
        if s < 0 or s > 1:
            return None
            
        t = (line_dx * (line_y1 - ray_y) - line_dy * (line_x1 - ray_x)) / -denom
        
        # If t is negative, the intersection is behind the ray origin
        if t < 0:
            return None
            
        # Return the distance to intersection
        return t * math.sqrt(ray_dx*ray_dx + ray_dy*ray_dy)
    
    def on_draw(self):
        """Render the screen"""
        self.clear()
        
        # Draw obstacles
        for obs in self.obstacles:
            arcade.draw_rectangle_filled(
                obs[0] + obs[2]/2, # x center
                obs[1] + obs[3]/2, # y center
                obs[2], # width
                obs[3], # height
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
        
        # Draw status text
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
            f"Emotion: {self.current_emotion}",
            20, self.height - 90,
            arcade.color.BLACK,
            16
        )
        
        autopilot_status = "ON" if self.autopilot else "OFF"
        arcade.draw_text(
            f"Autopilot: {autopilot_status}",
            20, self.height - 120,
            arcade.color.BLACK,
            16
        )
        
        # Draw instructions
        instructions = [
            "Controls:",
            "Arrow Keys: Manual Movement",
            "Space: Stop",
            "A: Toggle Autopilot",
            "R: Reset Position",
            "Q: Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            arcade.draw_text(
                instruction,
                600, 150 - (i * 25),
                arcade.color.BLACK,
                12
            )
    
    def on_update(self, delta_time):
        """Update the simulation"""
        # Get distance reading
        distance = self.sensor.measure_distance()
        
        # Process keyboard input
        if arcade.key.UP in self.keys_pressed:
            self.motors.move_forward(0.5)
        if arcade.key.DOWN in self.keys_pressed:
            self.motors.move_backward(0.5)
        if arcade.key.LEFT in self.keys_pressed:
            self.motors.turn_left(0.5)
        if arcade.key.RIGHT in self.keys_pressed:
            self.motors.turn_right(0.5)
        
        # Autopilot control
        if self.autopilot:
            if distance < 50:
                # Obstacle detected - turn away
                if random.choice([True, False]):
                    self.motors.turn_left(0.2)
                else:
                    self.motors.turn_right(0.2)
                self.current_state = "Avoiding"
            else:
                # Occasionally change direction during roaming
                if random.random() < 0.02:  # 2% chance per update
                    if random.choice([True, False]):
                        self.motors.turn_left(0.1)
                    else:
                        self.motors.turn_right(0.1)
                else:
                    self.motors.move_forward(0.2)  # Move forward
                self.current_state = "Roaming"
        
        # Keep robot within screen bounds
        self._constrain_to_bounds()
    
    def _constrain_to_bounds(self):
        """Keep the robot within the screen bounds"""
        margin = self.robot_radius + 10
        
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
        elif key == arcade.key.A:
            # Toggle autopilot
            self.autopilot = not self.autopilot
        elif key == arcade.key.R:
            # Reset robot position
            self.robot_x = self.width // 2
            self.robot_y = self.height // 2
            self.robot_direction = 0
        elif key == arcade.key.Q:
            # Quit
            arcade.close_window()
    
    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def set_state_and_emotion(self, state, emotion):
        """Update the state and emotion display"""
        self.current_state = state
        self.current_emotion = emotion
    
    def close(self):
        """Close the simulator"""
        arcade.close_window()


# When run directly, start the simulator
def main():
    simulator = ArcadeSimulator()
    arcade.run()

if __name__ == "__main__":
    main()

import arcade
import math
import random
import time

class RobotComponent:
    """Component that manages robot state and rendering"""
    
    def __init__(self, simulator, x=400, y=300, radius=50):
        self.simulator = simulator
        self.x = x
        self.y = y
        self.radius = radius
        self.direction = 0  # 0 radians = facing right
        self.current_state = "Initializing"
        self.current_emotion = "neutral"
        self.emotion_display = None  # Set by simulator
        
        # Sensor properties
        self.sensor_range = 200
        self.last_distance = 100
        
        # Obstacle avoidance
        self.avoiding_obstacle = False
        self.avoidance_start_time = 0
        self.avoidance_turn_direction = None
        self.avoidance_step = 0
        self.avoidance_turn_angle = 0
        
        # Stuck detection
        self.stuck_detection = {
            "last_positions": [],
            "position_sample_time": 0,
            "stuck_count": 0
        }
    
    def draw(self):
        """Draw the robot"""
        # Draw robot body
        arcade.draw_circle_filled(
            self.x, self.y, 
            self.radius, 
            arcade.color.LIGHT_BLUE
        )
        
        arcade.draw_circle_outline(
            self.x, self.y,
            self.radius,
            arcade.color.BLUE,
            3
        )
        
        # Draw emotion display if available
        if self.emotion_display:
            self.emotion_display.draw(self.x, self.y, self.current_emotion)
        
        # Draw direction indicator
        end_x = self.x + math.cos(self.direction) * self.radius
        end_y = self.y + math.sin(self.direction) * self.radius
        arcade.draw_line(
            self.x, self.y,
            end_x, end_y,
            arcade.color.GREEN,
            4
        )
        
        # Draw sensor beam
        beam_length = min(self.last_distance, self.sensor_range)
        beam_end_x = self.x + math.cos(self.direction) * beam_length
        beam_end_y = self.y + math.sin(self.direction) * beam_length
        
        arcade.draw_line(
            self.x, self.y,
            beam_end_x, beam_end_y,
            arcade.color.ORANGE,
            2
        )
    
    def move_forward(self, speed=1.0):
        """Move robot forward"""
        speed_px = min(speed * 5, 5)  # Limit speed
        self.x += math.cos(self.direction) * speed_px
        self.y += math.sin(self.direction) * speed_px
    
    def move_backward(self, speed=1.0):
        """Move robot backward"""
        speed_px = min(speed * 5, 5)  # Limit speed
        self.x -= math.cos(self.direction) * speed_px
        self.y -= math.sin(self.direction) * speed_px
    
    def turn_left(self, speed=1.0):
        """Turn robot left"""
        turn_amount = min(speed * 0.1, 0.1)  # Limit turn rate
        self.direction -= turn_amount
    
    def turn_right(self, speed=1.0):
        """Turn robot right"""
        turn_amount = min(speed * 0.1, 0.1)  # Limit turn rate
        self.direction += turn_amount
    
    def stop(self):
        """Stop robot movement"""
        pass  # In this simple physics model, stopping is immediate
    
    def set_state_and_emotion(self, state, emotion):
        """Update the robot's state and emotion"""
        self.current_state = state
        self.current_emotion = emotion.lower() if emotion else "neutral"
    
    def handle_obstacle_avoidance(self, distance):
        """Handle obstacle avoidance behavior"""
        # If we're currently in an obstacle avoidance maneuver
        if self.avoiding_obstacle:
            self.execute_avoidance_maneuver()
            return True
            
        # Start obstacle avoidance if distance is too close
        if distance < 80:  # Increased detection distance for earlier response
            # Begin a new avoidance maneuver
            self.start_avoidance_maneuver()
            self.current_state = "Avoiding"
            return True
        
        # No obstacle avoidance needed
        return False
    
    def start_avoidance_maneuver(self):
        """Start a new obstacle avoidance maneuver"""
        self.avoiding_obstacle = True
        self.avoidance_start_time = time.time()
        self.avoidance_step = 0  # Start with backing up
        
        # Choose a turn direction, with bias away from edges
        center_x = self.simulator.width / 2
        if self.x < center_x:
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
            self.move_backward(0.5)
            self.simulator.add_serial_message("BCK (Auto)", "tx")
            
            # Move to next step after backing up for a short time
            if elapsed > 0.3:
                self.avoidance_step = 1
                self.avoidance_start_time = current_time
                
        elif self.avoidance_step == 1:
            # Step 1: Turn in the chosen direction
            turn_duration = self.avoidance_turn_angle  # Time to turn is based on desired angle
            
            if self.avoidance_turn_direction == "left":
                self.turn_left(0.5)
                self.simulator.add_serial_message("LFT (Auto)", "tx")
            else:
                self.turn_right(0.5)
                self.simulator.add_serial_message("RGT (Auto)", "tx")
                
            # Move to next step after turning for the calculated duration
            if elapsed > turn_duration:
                self.avoidance_step = 2
                self.avoidance_start_time = current_time
                
        elif self.avoidance_step == 2:
            # Step 2: Move forward to find a clear path
            self.move_forward(0.4)
            
            # Take a new distance reading
            new_distance = self.simulator.sensor.measure_distance()
            
            # If we encounter another obstacle immediately, restart avoidance
            if new_distance < 60:
                self.start_avoidance_maneuver()
                
            # Otherwise, finish the maneuver after moving forward for a bit
            if elapsed > 0.5:
                self.avoiding_obstacle = False
    
    def check_if_stuck(self):
        """Check if the robot is stuck in the same area"""
        current_pos = (int(self.x), int(self.y))
        self.stuck_detection["last_positions"].append(current_pos)
        
        # Keep only the last 5 positions
        if len(self.stuck_detection["last_positions"]) > 5:
            self.stuck_detection["last_positions"].pop(0)
            
        # If we have enough samples, check if they're all close together
        if len(self.stuck_detection["last_positions"]) >= 5:
            # Calculate average distance between positions
            positions = self.stuck_detection["last_positions"]
            
            # Simple check: are all positions within a small radius?
            all_close = True
            center_x = sum(x for x, y in positions) / len(positions)
            center_y = sum(y for x, y in positions) / len(positions)
            
            for x, y in positions:
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if dist > 20:  # Consider positions further than 20px apart as "not stuck"
                    all_close = False
                    break
            
            # If all positions are close, increment stuck counter
            if all_close:
                self.stuck_detection["stuck_count"] += 1
                if self.stuck_detection["stuck_count"] > 3:
                    # We're definitely stuck, try a more dramatic avoidance
                    self.start_avoidance_maneuver()
            else:
                # Reset stuck counter if we've moved
                self.stuck_detection["stuck_count"] = 0
    
    def constrain_to_bounds(self, width, height):
        """Keep the robot within screen bounds"""
        margin = self.radius
        
        if self.x < margin:
            self.x = margin
        elif self.x > width - margin:
            self.x = width - margin
            
        if self.y < margin:
            self.y = margin
        elif self.y > height - margin:
            self.y = height - margin

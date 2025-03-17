import time
import math

class MotorController:
    def __init__(self, robot_obj=None, direction_obj=None, canvas=None):
        self.speed = 0.0  # Current speed (0.0-1.0)
        self.direction = 0.0  # Current heading in radians
        self.last_update = time.time()
        
        # For GUI simulation
        self.robot = robot_obj  # Reference to robot object in canvas
        self.direction_indicator = direction_obj  # Reference to direction indicator
        self.canvas = canvas  # Reference to tkinter canvas
        
        # Motor properties
        self.max_speed = 10  # pixels per update in GUI mode
        self.turn_speed = 0.1  # radians per update
    
    def move_forward(self, speed=1.0):
        """Move robot forward at specified speed (0.0-1.0)"""
        self.speed = max(0.0, min(1.0, speed))  # Clamp speed between 0 and 1
        
        # If we have a GUI reference, update robot position
        if self.canvas and self.robot:
            self._update_position()
    
    def move_backward(self, speed=1.0):
        """Move robot backward at specified speed"""
        # Negative speed means backward movement
        self.speed = -max(0.0, min(1.0, speed))
        
        if self.canvas and self.robot:
            self._update_position()
    
    def turn_left(self, speed=1.0):
        """Turn robot left at specified speed"""
        speed_factor = max(0.1, min(1.0, speed))
        self.direction -= self.turn_speed * speed_factor
        
        # Keep direction within 0-2π range
        while self.direction < 0:
            self.direction += 2 * math.pi
            
        if self.canvas and self.robot:
            self._update_direction()
            
    def turn_right(self, speed=1.0):
        """Turn robot right at specified speed"""
        speed_factor = max(0.1, min(1.0, speed))
        self.direction += self.turn_speed * speed_factor
        
        # Keep direction within 0-2π range
        while self.direction >= 2 * math.pi:
            self.direction -= 2 * math.pi
            
        if self.canvas and self.robot:
            self._update_direction()
    
    def stop(self):
        """Stop the robot"""
        self.speed = 0.0
    
    def _update_position(self):
        """Update robot position in GUI simulation"""
        if not self.robot or not self.canvas:
            return
            
        # Calculate movement based on current direction and speed
        dx = math.cos(self.direction) * (self.speed * self.max_speed)
        dy = math.sin(self.direction) * (self.speed * self.max_speed)
        
        # Move the robot in canvas
        self.canvas.move(self.robot, dx, dy)
        
        # Update direction indicator position
        if self.direction_indicator:
            self.canvas.move(self.direction_indicator, dx, dy)
            self._update_direction()
            
        # Redraw canvas
        self.canvas.update()
    
    def _update_direction(self):
        """Update direction indicator in GUI simulation"""
        if not self.direction_indicator or not self.canvas:
            return
            
        # Get robot center
        robot_coords = self.canvas.coords(self.robot)
        center_x = (robot_coords[0] + robot_coords[2]) / 2
        center_y = (robot_coords[1] + robot_coords[3]) / 2
        
        # Calculate new endpoint for direction line
        length = 25  # Length of direction indicator
        end_x = center_x + math.cos(self.direction) * length
        end_y = center_y + math.sin(self.direction) * length
        
        # Update direction line
        self.canvas.coords(self.direction_indicator, center_x, center_y, end_x, end_y)
        self.canvas.update()

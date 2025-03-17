import random
import time
import math

class UltrasonicSensor:
    def __init__(self, canvas=None, robot=None, obstacles=None):
        self.max_range = 200  # Maximum sensor range in cm/pixels
        self.canvas = canvas  # Reference to tkinter canvas for GUI mode
        self.robot = robot    # Reference to robot object in GUI
        self.obstacles = obstacles  # List of obstacles in GUI
        self.noise_factor = 0.05  # 5% noise
        self.last_distance = 100  # Start with default distance
        self.last_measure_time = time.time()
        
    def measure_distance(self):
        """Measure distance to nearest obstacle"""
        # If we're in GUI mode with canvas references
        if self.canvas and self.robot and self.obstacles:
            return self._measure_gui_distance()
        else:
            # Simple simulation mode - return semi-random values
            return self._measure_simulated_distance()
    
    def _measure_simulated_distance(self):
        """Generate a simulated distance reading with some coherence"""
        current_time = time.time()
        time_diff = current_time - self.last_measure_time
        
        # Add some noise and drift to the reading
        if random.random() < 0.1:  # 10% chance of significant change
            new_distance = random.randint(10, self.max_range)
        else:
            # Smaller variation from previous reading
            drift = random.uniform(-20, 20) * time_diff  # More time = more drift
            noise = random.uniform(-self.last_distance * self.noise_factor, 
                                  self.last_distance * self.noise_factor)
            new_distance = max(5, min(self.max_range, self.last_distance + drift + noise))
        
        self.last_distance = new_distance
        self.last_measure_time = current_time
        return new_distance
    
    def _measure_gui_distance(self):
        """Calculate actual distance to obstacles in GUI simulation"""
        # Get robot position
        robot_coords = self.canvas.coords(self.robot)
        robot_x = (robot_coords[0] + robot_coords[2]) / 2
        robot_y = (robot_coords[1] + robot_coords[3]) / 2
        
        # Get robot heading (this is simplified - would need actual heading)
        # Assuming heading info is available somehow
        heading_rad = 0  # Default to 0 - would be set by robot controller
        
        # Check distance to each obstacle
        min_distance = self.max_range
        
        for obstacle in self.obstacles:
            obstacle_coords = self.canvas.coords(obstacle)
            # Simple distance to bounding box - not precise but works for simulation
            dist = self._distance_to_rectangle(
                robot_x, robot_y, heading_rad,
                obstacle_coords[0], obstacle_coords[1],
                obstacle_coords[2], obstacle_coords[3]
            )
            min_distance = min(min_distance, dist)
        
        # Add some noise
        noise = random.uniform(-min_distance * self.noise_factor, 
                              min_distance * self.noise_factor)
        
        return max(5, min_distance + noise)
    
    def _distance_to_rectangle(self, x, y, heading, x1, y1, x2, y2):
        """Simple distance calculation from point to rectangle"""
        # This is a simplified calculation - not accounting for heading yet
        dx = max(x1 - x, 0, x - x2)
        dy = max(y1 - y, 0, y - y2)
        return math.sqrt(dx*dx + dy*dy)

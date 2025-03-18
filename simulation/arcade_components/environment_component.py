import arcade
import math
import random

class EnvironmentComponent:
    """Component that manages the environment, obstacles, and collisions"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
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
    
    def draw(self, layout):
        """Draw the environment and obstacles"""
        # Get environment region from layout helper
        env = layout.environment_region
        
        # Draw environment container background
        arcade.draw_rectangle_filled(
            env["x"], env["y"],
            env["width"], env["height"],
            (200, 210, 230)  # Custom light blue-gray color
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
    
    def calculate_distance(self, robot_x, robot_y, robot_direction, sensor_range):
        """Calculate distance to nearest obstacle"""
        # Simple optimized distance calculation
        min_distance = sensor_range
        
        # Direction vector
        dx = math.cos(robot_direction)
        dy = math.sin(robot_direction)
        
        for obs in self.obstacles:
            rect_x, rect_y, rect_w, rect_h = obs
            
            # Simplified ray-box intersection
            dist = self._ray_box_intersection(
                robot_x, robot_y,
                dx, dy,
                rect_x, rect_y,
                rect_x + rect_w, rect_y + rect_h
            )
            
            if dist < min_distance:
                min_distance = dist
        
        # Add minor noise
        noise = random.uniform(-min_distance * 0.03, min_distance * 0.03)
        result = max(5, min(min_distance + noise, sensor_range))
        
        return result
    
    def _ray_box_intersection(self, ray_x, ray_y, ray_dx, ray_dy, min_x, min_y, max_x, max_y):
        """Optimized ray-box intersection algorithm"""
        t_min = float('-inf')
        t_max = float('inf')
        
        # X planes
        if abs(ray_dx) < 1e-8:
            # Ray is parallel to Y axis
            if ray_x < min_x or ray_x > max_x:
                return float('inf')
        else:
            t1 = (min_x - ray_x) / ray_dx
            t2 = (max_x - ray_x) / ray_dx
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            if t_min > t_max or t_max < 0:
                return float('inf')
        
        # Y planes
        if abs(ray_dy) < 1e-8:
            # Ray is parallel to X axis
            if ray_y < min_y or ray_y > max_y:
                return float('inf')
        else:
            t1 = (min_y - ray_y) / ray_dy
            t2 = (max_y - ray_y) / ray_dy
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            if t_min > t_max or t_max < 0:
                return float('inf')
        
        # Return distance to closest intersection
        if t_min > 0:
            return t_min * math.sqrt(ray_dx*ray_dx + ray_dy*ray_dy)
        return t_max * math.sqrt(ray_dx*ray_dx + ray_dy*ray_dy)
    
    def constrain_to_bounds(self, x, y, radius):
        """Keep an object within screen bounds"""
        margin = radius
        
        return (
            max(margin, min(x, self.width - margin)),
            max(margin, min(y, self.height - margin))
        )

class LayoutHelper:
    """Helper for organizing panel layout in the simulator"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # Define the main layout division - left 70% for simulation, right 30% for panels
        self.left_width = int(screen_width * 0.7)
        self.right_width = screen_width - self.left_width
        
        # Environment region (on the left side)
        self.environment_region = {
            "x": self.left_width // 2,  # Centered in left area
            "y": screen_height // 2,
            "width": self.left_width * 0.9,  # 90% of left area width
            "height": screen_height * 0.8
        }
        
        # Status bar at the top spans the full width
        self.top_bar_region = {
            "x": screen_width // 2,
            "y": screen_height - 30,
            "width": screen_width,
            "height": 60
        }
        
        # Voice panel (top-right)
        self.voice_panel_region = {
            "x": self.left_width + (self.right_width // 2),
            "y": screen_height * 0.7,
            "width": self.right_width * 0.9,
            "height": screen_height * 0.4
        }
        
        # Dashboard region (middle-right)
        self.dashboard_region = {
            "x": self.left_width + (self.right_width // 2),
            "y": screen_height * 0.3,
            "width": self.right_width * 0.9,
            "height": screen_height * 0.35
        }
        
        # Serial monitor region (can be toggled with dashboard)
        self.serial_monitor_region = {
            "x": self.left_width + (self.right_width // 2),
            "y": screen_height * 0.3,
            "width": self.right_width * 0.9,
            "height": screen_height * 0.35
        }
        
        # Help button/panel (bottom-right corner)
        self.help_region = {
            "x": self.left_width + (self.right_width // 2),
            "y": screen_height * 0.07,
            "width": self.right_width * 0.7,
            "height": screen_height * 0.1
        }
    
    def get_environment_bounds(self):
        """Get the bounds of the robot environment area"""
        r = self.environment_region
        return (
            r["x"] - r["width"]/2,  # left
            r["y"] - r["height"]/2,  # bottom
            r["x"] + r["width"]/2,  # right
            r["y"] + r["height"]/2   # top
        )
    
    def is_point_in_environment(self, x, y):
        """Check if a point is within the environment area"""
        left, bottom, right, top = self.get_environment_bounds()
        return left <= x <= right and bottom <= y <= top
    
    def constrain_to_environment(self, x, y):
        """Constrain a point to stay within the environment area"""
        left, bottom, right, top = self.get_environment_bounds()
        return (
            max(left, min(x, right)),
            max(bottom, min(y, top))
        )

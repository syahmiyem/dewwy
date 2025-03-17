import math

class UltrasonicSensor:
    """Ultrasonic sensor implementation for arcade simulation"""
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    def measure_distance(self):
        """Get distance reading from simulator"""
        return self.simulator.calculate_distance()

class MotorController:
    """Motor controller implementation for arcade simulation"""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.speed = 0.0
        self.direction = 0.0
    
    def move_forward(self, speed=1.0):
        """Move robot forward"""
        speed_px = min(speed * 5, 5)  # Limit speed
        self.simulator.robot_x += math.cos(self.simulator.robot_direction) * speed_px
        self.simulator.robot_y += math.sin(self.simulator.robot_direction) * speed_px
    
    def move_backward(self, speed=1.0):
        """Move robot backward"""
        speed_px = min(speed * 5, 5)  # Limit speed
        self.simulator.robot_x -= math.cos(self.simulator.robot_direction) * speed_px
        self.simulator.robot_y -= math.sin(self.simulator.robot_direction) * speed_px
    
    def turn_left(self, speed=1.0):
        """Turn robot left"""
        turn_amount = min(speed * 0.1, 0.1)  # Limit turn rate
        self.simulator.robot_direction -= turn_amount
    
    def turn_right(self, speed=1.0):
        """Turn robot right"""
        turn_amount = min(speed * 0.1, 0.1)  # Limit turn rate
        self.simulator.robot_direction += turn_amount
    
    def stop(self):
        """Stop the robot"""
        pass

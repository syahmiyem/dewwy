# tests/test_behavior.py
import unittest
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController
from raspberry_pi.behavior.state_machine import RobotStateMachine

class TestRobotBehavior(unittest.TestCase):
    def setUp(self):
        # Create mock sensor and motor objects
        self.sensor = MockUltrasonicSensor()
        self.motors = MockMotorController()
        
        # Create state machine with mocks
        self.state_machine = RobotStateMachine(self.sensor, self.motors)
    
    def test_obstacle_avoidance(self):
        # Test that robot stops and turns when obstacle detected
        self.sensor.set_distance(15)  # Set obstacle 15cm away
        
        # Run the state machine for one cycle
        self.state_machine.update()
        
        # Assert that motors received correct commands
        self.assertEqual(self.motors.last_command, "STOP")
        
        # Next update should trigger a turn
        self.state_machine.update()
        self.assertEqual(self.motors.last_command, "TURN_LEFT")
    
    def test_free_movement(self):
        # Test that robot moves forward when no obstacles
        self.sensor.set_distance(100)  # Clear path
        
        # Run state machine
        self.state_machine.update()
        
        # Should move forward
        self.assertEqual(self.motors.last_command, "FORWARD")

# Mock classes for testing
class MockUltrasonicSensor:
    def __init__(self):
        self.distance = 100
    
    def measure_distance(self):
        return self.distance
    
    def set_distance(self, new_distance):
        self.distance = new_distance

class MockMotorController:
    def __init__(self):
        self.last_command = None
    
    def move_forward(self, speed=1.0):
        self.last_command = "FORWARD"
    
    def turn_left(self, speed=1.0):
        self.last_command = "TURN_LEFT"
    
    def stop(self):
        self.last_command = "STOP"

if __name__ == "__main__":
    unittest.main()
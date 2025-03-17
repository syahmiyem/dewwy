import unittest
import sys
import os
import time
import random

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController
from raspberry_pi.behavior.state_machine import RobotStateMachine

class TestRoombaStyleAvoidance(unittest.TestCase):
    def setUp(self):
        # Create mock sensor and motor objects
        self.sensor = MockUltrasonicSensor()
        self.motors = MockMotorController()
        
        # Create state machine with mocks
        self.state_machine = RobotStateMachine(self.sensor, self.motors)
        
        # Seed random for test consistency
        random.seed(42)
    
    def test_immediate_turn_on_obstacle(self):
        # Test that robot immediately turns (without stopping first) when obstacle detected
        self.sensor.set_distance(15)  # Set obstacle 15cm away
        
        # Run the state machine for one cycle
        self.state_machine.update()
        
        # Assert that motors received turn command directly (not stop first)
        self.assertTrue(self.motors.last_command == "TURN_LEFT" or 
                       self.motors.last_command == "TURN_RIGHT")
        
        # Verify it didn't stop first
        self.assertNotEqual(self.motors.command_history[0], "STOP")
    
    def test_random_direction_selection(self):
        # Test that turn direction is randomly selected
        self.sensor.set_distance(15)  # Set obstacle 15cm away
        
        # Run multiple cycles and collect turning directions
        turns = {"TURN_LEFT": 0, "TURN_RIGHT": 0}
        
        # Run enough times to ensure we get both directions with high probability
        for _ in range(20):
            self.motors.reset()
            self.state_machine.update()
            if self.motors.last_command in turns:
                turns[self.motors.last_command] += 1
        
        # Both directions should be used at least once
        self.assertGreater(turns["TURN_LEFT"], 0)
        self.assertGreater(turns["TURN_RIGHT"], 0)

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
        self.command_history = []
    
    def move_forward(self, speed=1.0):
        self.last_command = "FORWARD"
        self.command_history.append("FORWARD")
    
    def move_backward(self, speed=1.0):
        self.last_command = "BACKWARD"
        self.command_history.append("BACKWARD")
    
    def turn_left(self, speed=1.0):
        self.last_command = "TURN_LEFT"
        self.command_history.append("TURN_LEFT")
    
    def turn_right(self, speed=1.0):
        self.last_command = "TURN_RIGHT"
        self.command_history.append("TURN_RIGHT")
    
    def stop(self):
        self.last_command = "STOP"
        self.command_history.append("STOP")
    
    def reset(self):
        self.last_command = None
        self.command_history = []

if __name__ == "__main__":
    unittest.main()

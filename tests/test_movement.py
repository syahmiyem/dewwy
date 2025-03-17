import unittest
import sys
import os
import time

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.virtual_motors import MotorController

class TestMovement(unittest.TestCase):
    def setUp(self):
        # Create a motor controller for testing
        self.motors = MotorController()
        
    def test_forward_movement(self):
        # Test that forward movement updates position correctly
        initial_direction = self.motors.direction
        self.motors.move_forward(0.5)
        
        # Ensure speed is set correctly
        self.assertEqual(self.motors.speed, 0.5)
        
        # Direction should be unchanged
        self.assertEqual(self.motors.direction, initial_direction)
        
    def test_backward_movement(self):
        # Test that backward movement sets negative speed
        self.motors.move_backward(0.8)
        self.assertEqual(self.motors.speed, -0.8)
        
    def test_turning(self):
        # Test that turning changes direction correctly
        initial_direction = self.motors.direction
        
        # Turn left
        self.motors.turn_left(1.0)
        # Direction should decrease (counterclockwise)
        self.assertLess(self.motors.direction, initial_direction)
        
        # Save the new direction
        after_left = self.motors.direction
        
        # Turn right
        self.motors.turn_right(1.0)
        # Direction should increase (clockwise)
        self.assertGreater(self.motors.direction, after_left)
        
    def test_stop(self):
        # Test that stop command zeroes speed
        self.motors.move_forward(1.0)
        self.motors.stop()
        self.assertEqual(self.motors.speed, 0.0)

class TestMovementSequence(unittest.TestCase):
    def setUp(self):
        # Create a motor controller for testing
        self.motors = MotorController()
        
    def test_movement_sequence(self):
        # Test a sequence of movements
        
        # Move forward
        self.motors.move_forward(1.0)
        time.sleep(0.1)  # Allow "movement" to register
        
        # Turn right
        self.motors.turn_right(0.5)
        time.sleep(0.1)  # Allow "turn" to register
        
        # Move backward
        self.motors.move_backward(0.3)
        time.sleep(0.1)  # Allow "movement" to register
        
        # Stop
        self.motors.stop()
        self.assertEqual(self.motors.speed, 0.0)

if __name__ == "__main__":
    unittest.main()

import unittest
import sys
import os
import time

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.virtual_sensors import UltrasonicSensor

class TestUltrasonicSensor(unittest.TestCase):
    def setUp(self):
        # Create a sensor for testing
        self.sensor = UltrasonicSensor()
        
    def test_initial_reading(self):
        # Test that we can get an initial reading
        reading = self.sensor.measure_distance()
        self.assertTrue(5 <= reading <= self.sensor.max_range)
        
    def test_reading_range(self):
        # Take multiple readings and ensure they're within valid range
        for _ in range(10):
            reading = self.sensor.measure_distance()
            self.assertTrue(5 <= reading <= self.sensor.max_range)
            time.sleep(0.05)  # Small delay between readings
            
    def test_reading_coherence(self):
        # Test that readings don't randomly jump too much
        readings = []
        for _ in range(5):
            readings.append(self.sensor.measure_distance())
            time.sleep(0.1)
            
        # Calculate maximum difference between consecutive readings
        max_diff = max(abs(readings[i] - readings[i-1]) for i in range(1, len(readings)))
        
        # With normal operation, readings shouldn't jump by more than 30% of the last value
        # This test might occasionally fail due to the random element in the simulation
        for i in range(1, len(readings)):
            diff = abs(readings[i] - readings[i-1])
            self.assertLessEqual(diff, readings[i-1] * 0.3 + 5)

class TestSensorWithObstacle(unittest.TestCase):
    def setUp(self):
        # Create a sensor with mock obstacle detection
        self.sensor = MockUltrasonicSensor()
        
    def test_obstacle_detection(self):
        # Set a near obstacle
        self.sensor.set_mock_distance(15)
        
        # Check reading
        reading = self.sensor.measure_distance()
        self.assertEqual(reading, 15)
        
        # Remove obstacle
        self.sensor.set_mock_distance(100)
        
        # Check reading
        reading = self.sensor.measure_distance()
        self.assertEqual(reading, 100)
            
# Mock sensor for testing specific distances
class MockUltrasonicSensor(UltrasonicSensor):
    def __init__(self):
        super().__init__()
        self.mock_distance = 100
        
    def measure_distance(self):
        return self.mock_distance
        
    def set_mock_distance(self, distance):
        self.mock_distance = distance

if __name__ == "__main__":
    unittest.main()

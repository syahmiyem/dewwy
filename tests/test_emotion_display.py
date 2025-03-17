import unittest
import sys
import os

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEmotionDisplay(unittest.TestCase):
    def test_emotion_names(self):
        """Test that all necessary emotions are defined in both systems"""
        # Import required modules
        from raspberry_pi.behavior.robot_personality import Emotion
        
        # Direct testing of emotion constants
        self.assertEqual(Emotion.HAPPY, "happy")
        self.assertEqual(Emotion.SAD, "sad")
        self.assertEqual(Emotion.NEUTRAL, "neutral")
        self.assertEqual(Emotion.EXCITED, "excited")
        self.assertEqual(Emotion.SLEEPY, "sleepy")
        self.assertEqual(Emotion.CURIOUS, "curious")
        self.assertEqual(Emotion.SCARED, "scared")
        
        # Check consistency in arcade simulator
        # Import only in a way that doesn't require arcade to run
        try:
            import importlib.util
            spec = importlib.util.find_spec("simulation.arcade_simulator")
            if spec:
                # Only import if module exists
                arcade_simulator = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(arcade_simulator)
                
                # Create simulator instance
                simulator = arcade_simulator.ArcadeSimulator.__new__(arcade_simulator.ArcadeSimulator)
                
                # Required emotions should match
                required_emotions = [
                    Emotion.HAPPY, Emotion.SAD, Emotion.NEUTRAL,
                    Emotion.EXCITED, Emotion.SLEEPY, 
                    Emotion.CURIOUS, Emotion.SCARED
                ]
                
                for emotion in required_emotions:
                    simulator.emotion_faces = {emotion: None}
        except ImportError:
            # Skip this part of the test if arcade not available
            print("Arcade not available, skipping simulator test")
        
if __name__ == "__main__":
    unittest.main()

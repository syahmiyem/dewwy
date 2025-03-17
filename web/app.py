import sys
import os
import time
import random
import json
import threading
from flask import Flask, render_template, jsonify, request

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import robot components - adapt for web version
from raspberry_pi.behavior.robot_personality import RobotPersonality, Emotion
from raspberry_pi.behavior.state_machine import RobotStateMachine, RobotState
from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController

app = Flask(__name__)

# Create a global robot instance
class WebRobot:
    def __init__(self):
        print("Initializing Web Robot")
        # Use virtual/simulated components
        self.sensor = UltrasonicSensor()
        self.motors = MotorController()
        self.personality = RobotPersonality(db_path="web_robot_memory.db")
        self.state_machine = RobotStateMachine(self.sensor, self.motors, self.personality)
        
        # Randomize personality traits
        self._randomize_personality()
        
        # Status tracking
        self.running = True
        self.last_update = time.time()
        self.obstacle_distance = 100
        self.messages = []
        
        # Start the update thread
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _randomize_personality(self):
        """Create a unique pet personality with randomized traits"""
        self.personality.traits["openness"] = random.randint(3, 10)
        self.personality.traits["friendliness"] = random.randint(5, 10)
        self.personality.traits["activeness"] = random.randint(3, 10)
        self.personality.traits["expressiveness"] = random.randint(4, 10)
        self.personality.traits["patience"] = random.randint(2, 10)
    
    def _update_loop(self):
        """Background loop to update robot state"""
        update_interval = 0.5  # Slower updates for web version
        
        while self.running:
            try:
                # Update the robot components
                self.personality.update()
                self.state_machine.update()
                
                # Simulate sensor readings
                if random.random() < 0.1:  # Occasionally change distance reading
                    self.obstacle_distance = random.uniform(20, 200)
                    self.sensor.mock_distance = self.obstacle_distance
                
                # Record status message
                if random.random() < 0.2:  # 20% chance
                    state = self.state_machine.current_state
                    emotion = self.personality.get_emotion()
                    msg = f"Robot is {state} and feeling {emotion}"
                    self.add_message(msg)
                
                # Sleep to maintain update rate
                time.sleep(update_interval)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                import traceback
                traceback.print_exc()
    
    def add_message(self, message):
        """Add a message to the history"""
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append({
            "time": timestamp,
            "text": message
        })
        # Keep only recent messages
        while len(self.messages) > 20:
            self.messages.pop(0)
    
    def get_status(self):
        """Get current robot status"""
        return {
            "state": self.state_machine.current_state,
            "emotion": self.personality.get_emotion(),
            "distance": self.obstacle_distance,
            "messages": self.messages[-5:],
            "personality": self.personality.traits
        }
    
    def trigger_state(self, state_name):
        """Trigger a specific state"""
        if hasattr(RobotState, state_name.upper()):
            state_value = getattr(RobotState, state_name.upper())
            self.state_machine.transition_to(state_value)
            return True
        return False
    
    def trigger_emotion(self, emotion_name):
        """Trigger a specific emotion"""
        emotion_name = emotion_name.lower()
        if hasattr(Emotion, emotion_name.upper()):
            emotion_value = getattr(Emotion, emotion_name.upper())
            self.personality.set_emotion(emotion_value)
            return True
        return False
    
    def simulate_obstacle(self, distance):
        """Simulate an obstacle at given distance"""
        self.obstacle_distance = distance
        self.sensor.mock_distance = distance
        return True

# Initialize the robot (once)
robot = WebRobot()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get robot status as JSON"""
    return jsonify(robot.get_status())

@app.route('/api/trigger/state/<state_name>', methods=['POST'])
def trigger_state(state_name):
    """Trigger a specific state"""
    success = robot.trigger_state(state_name)
    return jsonify({"success": success})

@app.route('/api/trigger/emotion/<emotion_name>', methods=['POST'])
def trigger_emotion(emotion_name):
    """Trigger a specific emotion"""
    success = robot.trigger_emotion(emotion_name)
    return jsonify({"success": success})

@app.route('/api/simulate/obstacle', methods=['POST'])
def simulate_obstacle():
    """Simulate an obstacle"""
    distance = request.json.get('distance', 20)
    success = robot.simulate_obstacle(float(distance))
    return jsonify({"success": success})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import time
import signal
import sys
import os
import threading
import argparse
import atexit
import random

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from raspberry_pi.display.oled_interface import OLEDDisplay
from raspberry_pi.communication.serial_handler import SerialHandler
from raspberry_pi.behavior.state_machine import RobotStateMachine, RobotState
from raspberry_pi.behavior.robot_personality import RobotPersonality, Emotion
from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController

# Try to import audio components, with fallback options
try:
    from raspberry_pi.audio.microphone_interface import MicrophoneInterface
    from raspberry_pi.audio.voice_recognition import VoiceRecognizer
    from raspberry_pi.audio.command_processor import CommandProcessor
    audio_modules_available = True
    print("Audio modules imported successfully")
except ImportError as e:
    print(f"Warning: Could not import audio modules: {e}")
    print("Falling back to simplified audio simulation")
    try:
        from raspberry_pi.audio.fallback_recognition import SimpleMicrophoneInterface as MicrophoneInterface
        from raspberry_pi.audio.voice_recognition import VoiceRecognizer
        from raspberry_pi.audio.command_processor import CommandProcessor
        audio_modules_available = True
    except ImportError:
        print("Could not import fallback audio modules either")
        audio_modules_available = False

# Import only the Arcade simulator
from simulation.arcade_simulator import ArcadeSimulator
import arcade

class PetRobot:
    def __init__(self, simulation_mode=True, gui_mode=True, simple_audio=False):
        print("Initializing Pet Robot...")
        self.simulation_mode = simulation_mode
        self.gui_mode = gui_mode
        self.running = True
        self.simulator_instance = None
        
        # Initialize components
        self.display = OLEDDisplay(simulation=simulation_mode)
        self.display.set_status("Starting up...")
        
        # Initialize GUI if requested
        if gui_mode and simulation_mode:
            print("Creating Arcade simulator interface...")
            # Create simulator - but don't run it yet
            self.simulator_instance = ArcadeSimulator()
            self.sensor = self.simulator_instance.sensor
            self.motors = self.simulator_instance.motors
        else:
            # No GUI - use simple simulated components
            self.sensor = UltrasonicSensor()
            self.motors = MotorController()
        
        # Initialize communication if not in pure simulation mode
        if not simulation_mode:
            self.serial = SerialHandler(simulation=False)
            # Wire up the hardware interfaces through serial
            self.sensor = self._create_sensor_interface(self.serial)
            self.motors = self._create_motor_interface(self.serial)
        
        # Initialize personality with unique traits
        self.personality = RobotPersonality(display=self.display)
        
        # Randomize personality traits to create a unique pet character
        self._randomize_personality_traits()
        
        # Initialize state machine with references to personality and components
        self.state_machine = RobotStateMachine(self.sensor, self.motors, self.personality)
        
        # Initialize audio and voice recognition components
        if audio_modules_available:
            self.microphone = MicrophoneInterface(simulation=simulation_mode)
            self.voice_recognizer = VoiceRecognizer(
                microphone=self.microphone, 
                simulation=simulation_mode,
                force_simple_mode=simple_audio
            )
            self.command_processor = CommandProcessor(
                voice_recognizer=self.voice_recognizer,
                state_machine=self.state_machine,
                personality=self.personality
            )
        else:
            print("Voice recognition disabled - required modules not available")
            self.microphone = None
            self.voice_recognizer = None
            self.command_processor = None
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.shutdown)  # Register shutdown on exit
        
        # Main thread control
        self.main_thread = None
        
        # Pet-specific variables
        self.last_random_behavior = time.time()
        self.random_behavior_interval = random.uniform(20, 60)  # Seconds between random behaviors
        
        # Show startup emotions
        self.personality.set_emotion(Emotion.EXCITED)
        print(f"Pet robot initialized with personality: {self._get_personality_description()}")
    
    def _create_sensor_interface(self, serial):
        """Create a sensor interface that works through serial connection"""
        class SerialUltrasonicSensor:
            def __init__(self, serial_handler):
                self.serial = serial_handler
                
            def measure_distance(self):
                return self.serial.get_distance()
                
        return SerialUltrasonicSensor(serial)
    
    def _create_motor_interface(self, serial):
        """Create a motor interface that works through serial connection"""
        class SerialMotorController:
            def __init__(self, serial_handler):
                self.serial = serial_handler
                
            def move_forward(self, speed=1.0):
                speed_val = int(min(255, max(0, speed * 255)))
                self.serial.send_command(f"FWD")
                
            def move_backward(self, speed=1.0):
                speed_val = int(min(255, max(0, speed * 255)))
                self.serial.send_command(f"BCK")
                
            def turn_left(self, speed=1.0):
                speed_val = int(min(255, max(0, speed * 255)))
                self.serial.send_command(f"LFT")
                
            def turn_right(self, speed=1.0):
                speed_val = int(min(255, max(0, speed * 255)))
                self.serial.send_command(f"RGT")
                
            def stop(self):
                self.serial.send_command("STP")
                
        return SerialMotorController(serial)
    
    def _randomize_personality_traits(self):
        """Create a unique pet personality with randomized traits"""
        # Create a unique personality for each run
        self.personality.traits["openness"] = random.randint(3, 10)
        self.personality.traits["friendliness"] = random.randint(5, 10)
        self.personality.traits["activeness"] = random.randint(3, 10)
        self.personality.traits["expressiveness"] = random.randint(4, 10)
        self.personality.traits["patience"] = random.randint(2, 10)
    
    def _get_personality_description(self):
        """Get a text description of the robot's personality"""
        traits = self.personality.traits
        description = []
        
        # Friendliness description
        if traits["friendliness"] > 8:
            description.append("very friendly")
        elif traits["friendliness"] > 5:
            description.append("generally friendly")
        else:
            description.append("somewhat reserved")
            
        # Activeness description
        if traits["activeness"] > 8:
            description.append("highly energetic")
        elif traits["activeness"] > 5:
            description.append("moderately active")
        else:
            description.append("relatively calm")
            
        # Expressiveness description
        if traits["expressiveness"] > 7:
            description.append("very expressive")
        else:
            description.append("subtly expressive")
        
        return ", ".join(description)
    
    def _check_for_random_behaviors(self):
        """Occasionally trigger random pet-like behaviors"""
        current_time = time.time()
        
        # Check if it's time for a random behavior
        if current_time - self.last_random_behavior > self.random_behavior_interval:
            self.last_random_behavior = current_time
            self.random_behavior_interval = random.uniform(15, 60)  # Vary time between behaviors
            
            # Choose a random behavior
            behavior = random.choice([
                "play_behavior",
                "curious_behavior",
                "sleep_behavior",
                "attention_seeking"
            ])
            
            # Execute the behavior
            if behavior == "play_behavior" and random.random() < self.personality.traits["activeness"] / 10:
                print("Pet robot feels playful!")
                self.state_machine.transition_to(RobotState.PLAYING)
            
            elif behavior == "curious_behavior" and random.random() < self.personality.traits["openness"] / 10:
                print("Pet robot is curious about something!")
                self.state_machine.transition_to(RobotState.CURIOUS)
            
            elif behavior == "sleep_behavior" and random.random() < (10 - self.personality.traits["activeness"]) / 10:
                print("Pet robot is feeling sleepy!")
                self.state_machine.transition_to(RobotState.SLEEPING)
            
            elif behavior == "attention_seeking" and random.random() < self.personality.traits["expressiveness"] / 10:
                print("Pet robot wants attention!")
                # Make a small noise or movement to get attention
                self.personality.set_emotion(random.choice([Emotion.EXCITED, Emotion.HAPPY]))
                # Move back and forth a bit
                if hasattr(self.state_machine, "current_state") and self.state_machine.current_state == RobotState.IDLE:
                    self.motors.move_forward(0.3)
                    time.sleep(0.2)
                    self.motors.stop()
    
    def start(self):
        """Start the robot's main loop"""
        print("Starting pet robot...")
        self.display.set_status("Running")
        self.display.set_emotion(Emotion.HAPPY)
        
        # Start audio and voice recognition
        if audio_modules_available and self.microphone and self.voice_recognizer and self.command_processor:
            self.microphone.start_listening()
            self.voice_recognizer.start()
            self.command_processor.start()
        
        # Start in a separate thread if using GUI
        if self.gui_mode and self.simulation_mode:
            print("Starting in GUI mode with Arcade simulation...")
            self.main_thread = threading.Thread(target=self._main_loop)
            self.main_thread.daemon = True
            self.main_thread.start()
            
            # Start the Arcade simulator main loop (this blocks until window is closed)
            print("Starting Arcade simulator...")
            # This will call on_close when window is closed
            arcade.run()
            
            # When simulator closes, shut down the system
            print("Arcade window closed, shutting down...")
            self.shutdown()
        else:
            # Run directly in this thread
            self._main_loop()
    
    def _main_loop(self):
        """Main control loop for the robot"""
        update_interval = 0.1  # seconds
        
        try:
            while self.running:
                start_time = time.time()
                
                # Update the personality (random emotion changes, etc.)
                if hasattr(self, 'personality'):
                    self.personality.update()
                
                # Update the state machine
                if hasattr(self, 'state_machine'):
                    self.state_machine.update()
                
                # Check for random pet-like behaviors
                self._check_for_random_behaviors()
                
                # Get current state
                if hasattr(self, 'state_machine') and hasattr(self, 'personality'):
                    state = self.state_machine.current_state
                    emotion = self.personality.get_emotion()
                    distance = self.sensor.measure_distance()
                    
                    # Log status every few updates
                    if random.random() < 0.05:  # ~5% chance each update
                        print(f"State: {state}, Emotion: {emotion}, Distance: {distance:.1f}cm")
                    
                    # Update the simulator if it exists
                    if self.simulator_instance:
                        self.simulator_instance.set_state_and_emotion(state, emotion)
                
                # Sleep to maintain update rate
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if not self.gui_mode:
                self.shutdown()
    
    def _signal_handler(self, sig, frame):
        """Handle system signals for clean shutdown"""
        print("Signal received, shutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of all components"""
        if not self.running:  # Prevent multiple shutdowns
            return
            
        print("Shutting down pet robot...")
        self.running = False
        
        # Set final emotion
        if hasattr(self, 'personality'):
            self.personality.set_emotion(Emotion.SAD)
        
        # Stop components - add safety checks
        if hasattr(self, 'display') and self.display:
            try:
                self.display.shutdown()
            except Exception as e:
                print(f"Error shutting down display: {e}")
        
        # Stop audio components
        if audio_modules_available and hasattr(self, 'command_processor') and self.command_processor:
            try:
                self.command_processor.stop()
            except Exception as e:
                print(f"Error stopping command processor: {e}")
                
        if audio_modules_available and hasattr(self, 'voice_recognizer') and self.voice_recognizer:
            try:
                self.voice_recognizer.stop()
            except Exception as e:
                print(f"Error stopping voice recognizer: {e}")
                
        if audio_modules_available and hasattr(self, 'microphone') and self.microphone:
            try:
                self.microphone.shutdown()
            except Exception as e:
                print(f"Error shutting down microphone: {e}")
                
        if hasattr(self, 'serial') and self.serial:
            try:
                self.serial.disconnect()
            except Exception as e:
                print(f"Error disconnecting serial: {e}")
        
        # Force exit the process
        print("Goodbye!")
        os._exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pet Robot Control System")
    parser.add_argument("--no-simulation", action="store_true", 
                        help="Connect to real hardware instead of simulation")
    parser.add_argument("--no-gui", action="store_true",
                        help="Run without GUI (console mode)")
    parser.add_argument("--simple-audio", action="store_true",
                        help="Use simplified audio processing (no advanced features)")
    args = parser.parse_args()
    
    # Create and start pet robot (globals so atexit can access)
    robot = PetRobot(
        simulation_mode=not args.no_simulation, 
        gui_mode=not args.no_gui,
        simple_audio=args.simple_audio
    )
    robot.start()

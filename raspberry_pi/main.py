import time
import signal
import sys
import os
import threading
import argparse
import atexit

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from raspberry_pi.display.oled_interface import OLEDDisplay
from raspberry_pi.communication.serial_handler import SerialHandler
from raspberry_pi.behavior.state_machine import RobotStateMachine, RobotState
from raspberry_pi.behavior.robot_personality import RobotPersonality, Emotion
from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController

# Import only the Arcade simulator
from simulation.arcade_simulator import ArcadeSimulator
import arcade

class PetRobot:
    def __init__(self, simulation_mode=True, gui_mode=True):
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
        
        # Initialize personality and state machine
        self.personality = RobotPersonality(display=self.display)
        self.state_machine = RobotStateMachine(self.sensor, self.motors, self.personality)
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.shutdown)  # Register shutdown on exit
        
        # Main thread control
        self.main_thread = None
    
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
    
    def start(self):
        """Start the robot's main loop"""
        print("Starting pet robot...")
        self.display.set_status("Running")
        self.display.set_emotion(Emotion.HAPPY)
        
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
                
                # Update the state machine
                if hasattr(self, 'state_machine'):
                    self.state_machine.update()
                
                # Get current state
                if hasattr(self, 'state_machine') and hasattr(self, 'personality'):
                    state = self.state_machine.current_state
                    emotion = self.personality.get_emotion()
                    distance = self.sensor.measure_distance()
                    
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
        
        # Stop components - add safety checks
        if hasattr(self, 'display') and self.display:
            try:
                self.display.shutdown()
            except Exception as e:
                print(f"Error shutting down display: {e}")
                
        if hasattr(self, 'serial') and self.serial:
            try:
                self.serial.disconnect()
            except Exception as e:
                print(f"Error disconnecting serial: {e}")
        
        # Force exit the process
        print("Exiting...")
        os._exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pet Robot Control System")
    parser.add_argument("--no-simulation", action="store_true", 
                        help="Connect to real hardware instead of simulation")
    parser.add_argument("--no-gui", action="store_true",
                        help="Run without GUI (console mode)")
    args = parser.parse_args()
    
    # Create and start pet robot (globals so atexit can access)
    robot = PetRobot(simulation_mode=not args.no_simulation, 
                     gui_mode=not args.no_gui)
    robot.start()

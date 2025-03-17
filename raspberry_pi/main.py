import time
import signal
import sys
import os
import threading
import argparse

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from raspberry_pi.display.oled_interface import OLEDDisplay
from raspberry_pi.communication.serial_handler import SerialHandler
from raspberry_pi.behavior.state_machine import RobotStateMachine, RobotState
from raspberry_pi.behavior.robot_personality import RobotPersonality, Emotion
from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController

# Import the Arcade simulator
from simulation.arcade_simulator import ArcadeSimulator, run_simulator

class PetRobot:
    def __init__(self, simulation_mode=True, gui_mode=True):
        print("Initializing Pet Robot...")
        self.simulation_mode = simulation_mode
        self.gui_mode = gui_mode
        self.running = True
        
        # Initialize components
        self.display = OLEDDisplay(simulation=simulation_mode)
        self.display.set_status("Starting up...")
        
        # Initialize either GUI simulator or headless components
        self.simulator = None
        if gui_mode and simulation_mode:
            print("Creating simulator interface...")
            # We'll initialize the simulator later when we start
            self.sensor = None  # Will be set when simulator starts
            self.motors = None  # Will be set when simulator starts
        else:
            # No GUI - use simple simulated components
            print("Using headless simulation...")
            self.sensor = UltrasonicSensor()
            self.motors = MotorController()
        
        # Initialize communication if not in pure simulation mode
        if not simulation_mode:
            self.serial = SerialHandler(simulation=False)
            # Wire up the hardware interfaces through serial
            self.sensor = self._create_sensor_interface(self.serial)
            self.motors = self._create_motor_interface(self.serial)
        
        # Initialize personality and state machine only for non-GUI mode
        # In GUI mode, we'll initialize these after the simulator starts
        if not (gui_mode and simulation_mode):
            self.personality = RobotPersonality(display=self.display)
            self.state_machine = RobotStateMachine(self.sensor, self.motors, self.personality)
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
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
        
        if self.gui_mode and self.simulation_mode:
            print("Starting simulator in GUI mode...")
            # Create and run the simulator
            self.simulator = ArcadeSimulator()
            
            # Set up references to simulator components
            self.sensor = self.simulator.sensor
            self.motors = self.simulator.motors
            
            # Now initialize personality and state machine
            self.personality = RobotPersonality(display=self.display)
            self.state_machine = RobotStateMachine(self.sensor, self.motors, self.personality)
            self.display.set_emotion(Emotion.HAPPY)
            
            # Start state machine in a separate thread
            self.main_thread = threading.Thread(target=self._main_loop)
            self.main_thread.daemon = True
            self.main_thread.start()
            
            # Start the simulator (this blocks until window is closed)
            run_simulator()
            
            # When simulator closes, shut down the system
            self.shutdown()
        else:
            # We're in headless mode, run directly
            self.display.set_emotion(Emotion.HAPPY)
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
                    if self.simulator:
                        self.simulator.set_state_and_emotion(state, emotion)
                
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
        print("Shutting down pet robot...")
        self.running = False
        
        # Stop components with safety checks
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
        
        # Exit normally if not in GUI mode
        if not self.gui_mode:
            sys.exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pet Robot Control System")
    parser.add_argument("--no-simulation", action="store_true", 
                        help="Connect to real hardware instead of simulation")
    parser.add_argument("--no-gui", action="store_true",
                        help="Run without GUI (console mode)")
    args = parser.parse_args()
    
    # Create and start pet robot
    robot = PetRobot(simulation_mode=not args.no_simulation, 
                     gui_mode=not args.no_gui)
    robot.start()

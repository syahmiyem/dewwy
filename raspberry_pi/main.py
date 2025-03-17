import time
import signal
import sys
import os
import threading
import tkinter as tk
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
from simulation.robot_simulator import RobotSimulator

class PetRobot:
    def __init__(self, simulation_mode=True, gui_mode=True):
        print("Initializing Pet Robot...")
        self.simulation_mode = simulation_mode
        self.gui_mode = gui_mode
        self.running = True
        
        # Initialize GUI if requested
        self.root = None
        self.simulator = None
        if gui_mode:
            self.root = tk.Tk()
            self.root.title("Dewwy - Pet Robot Simulation")
            self.root.geometry("850x700")  # Set window size
            self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
            
            print("Creating simulator interface...")
            # Create simulator with GUI
            self.simulator = RobotSimulator(self.root)
            self.sensor = self.simulator.sensor
            self.motors = self.simulator.motors
        else:
            # No GUI - use simple simulated components
            self.sensor = UltrasonicSensor()
            self.motors = MotorController()
        
        # Initialize components
        self.display = OLEDDisplay(simulation=simulation_mode)
        self.display.set_status("Starting up...")
        
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
        if self.gui_mode:
            print("Starting in GUI mode - launching window...")
            self.main_thread = threading.Thread(target=self._main_loop)
            self.main_thread.daemon = True
            self.main_thread.start()
            
            # Start the GUI main loop (this blocks until window is closed)
            print("Starting Tkinter mainloop...")
            self.root.mainloop()
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
                self.state_machine.update()
                
                # Print current state and emotion (for debugging/simulation)
                state = self.state_machine.current_state
                emotion = self.personality.get_emotion()
                distance = self.sensor.measure_distance()
                
                print(f"State: {state}, Emotion: {emotion}, Distance: {distance:.1f}cm")
                
                # Update the simulator UI if using GUI
                if self.gui_mode and self.simulator:
                    self.simulator.set_state_and_emotion(state, emotion)
                
                # Calculate sleep time to maintain consistent update rate
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean shutdown
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
        
        # Stop components - add safety checks
        if hasattr(self, 'display') and self.display:
            try:
                self.display.shutdown()
            except Exception as e:
                print(f"Error shutting down display: {e}")
                
        if hasattr(self, 'serial') and self.serial:
            self.serial.disconnect()
        
        # Stop GUI if active
        if self.gui_mode and self.root:
            try:
                self.root.quit()
            except Exception as e:
                print(f"Error closing GUI: {e}")
        
        # Don't call sys.exit directly - it can cause issues in Tkinter
        # Instead, schedule the exit to happen after Tkinter has cleaned up
        if self.gui_mode and self.root:
            self.root.after(100, lambda: os._exit(0))
        else:
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

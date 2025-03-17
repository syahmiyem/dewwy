# simulation/robot_simulator.py
import tkinter as tk
import math
import sys
import os

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController

class RobotSimulator:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a title label
        self.title_label = tk.Label(self.frame, text="Pet Robot Simulator", font=('Arial', 16, 'bold'))
        self.title_label.pack(pady=10)
        
        # Create canvas with border
        self.canvas = tk.Canvas(self.frame, width=800, height=500, bg='white', bd=2, relief=tk.SUNKEN)
        self.canvas.pack(padx=10, pady=10)
        
        # Status display area
        self.status_frame = tk.Frame(self.frame)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.distance_label = tk.Label(self.status_frame, text="Distance: --", font=('Arial', 12))
        self.distance_label.pack(side=tk.LEFT, padx=10)
        
        self.state_label = tk.Label(self.status_frame, text="State: --", font=('Arial', 12))
        self.state_label.pack(side=tk.LEFT, padx=10)
        
        self.emotion_label = tk.Label(self.status_frame, text="Emotion: --", font=('Arial', 12))
        self.emotion_label.pack(side=tk.LEFT, padx=10)
        
        # Create virtual robot components
        self.robot = self.canvas.create_oval(350, 250, 450, 350, fill='lightblue', outline='blue', width=2)
        self.direction = self.canvas.create_line(400, 300, 450, 300, fill='red', width=3)
        
        # Create some obstacles
        self.obstacles = [
            self.canvas.create_rectangle(100, 100, 200, 200, fill='gray', outline='black'),
            self.canvas.create_rectangle(600, 400, 700, 500, fill='gray', outline='black'),
            self.canvas.create_rectangle(300, 500, 500, 550, fill='gray', outline='black')
        ]
        
        # Add legend
        self.canvas.create_rectangle(650, 50, 670, 70, fill='lightblue', outline='blue')
        self.canvas.create_text(710, 60, text="Robot", anchor=tk.W)
        
        self.canvas.create_rectangle(650, 80, 670, 100, fill='gray', outline='black')
        self.canvas.create_text(710, 90, text="Obstacle", anchor=tk.W)
        
        self.canvas.create_line(650, 120, 670, 120, fill='red', width=3)
        self.canvas.create_text(710, 120, text="Direction", anchor=tk.W)
        
        # Initialize virtual components
        self.sensor = UltrasonicSensor(self.canvas, self.robot, self.obstacles)
        self.motors = MotorController(self.robot, self.direction, self.canvas)
        
        # Control buttons
        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Manual control buttons
        tk.Button(self.control_frame, text="Forward", command=lambda: self.motors.move_forward(0.5)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Left", command=lambda: self.motors.turn_left(0.5)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Stop", command=self.motors.stop).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Right", command=lambda: self.motors.turn_right(0.5)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Back", command=lambda: self.motors.move_backward(0.5)).pack(side=tk.LEFT, padx=5)
        
        # Add a little space
        tk.Label(self.control_frame, text=" | ").pack(side=tk.LEFT, padx=10)
        
        # Auto-pilot toggle
        self.autopilot_var = tk.BooleanVar(value=True)
        self.autopilot_check = tk.Checkbutton(self.control_frame, text="Auto-pilot", 
                                            variable=self.autopilot_var)
        self.autopilot_check.pack(side=tk.LEFT, padx=10)
        
        # Initialize UI update status
        self.last_distance = 0
        self.current_state = "Initializing"
        self.current_emotion = "Neutral"
        
        print("Robot simulator initialized successfully")
        
        # Start simulation loop
        self.update()
        
    def update(self):
        # Update sensor readings
        distance = self.sensor.measure_distance()
        self.last_distance = distance
        
        # Example control logic (only if autopilot is enabled)
        if self.autopilot_var.get():
            if distance < 50:  # If obstacle detected within 50px
                self.motors.turn_left(0.1)  # Turn to avoid
                self.current_state = "Avoiding"
            else:
                self.motors.move_forward(0.1)  # Move forward
                self.current_state = "Roaming"
        
        # Update UI labels    
        self.distance_label.config(text=f"Distance: {distance:.1f}px")
        self.state_label.config(text=f"State: {self.current_state}")
        self.emotion_label.config(text=f"Emotion: {self.current_emotion}")
        
        # Clear old sensor text (which was creating lots of text objects)
        self.canvas.delete("sensor_text")
        
        # Draw new sensor text
        self.canvas.create_text(100, 50, text=f"Distance: {distance:.1f}px", 
                              fill='black', font=('Arial', 12), tags="sensor_text")
        
        # Schedule next update
        self.root.after(100, self.update)
    
    def set_state_and_emotion(self, state, emotion):
        """Update the state and emotion display"""
        self.current_state = state
        self.current_emotion = emotion

# Run simulator when script is executed directly
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pet Robot Simulator")
    root.geometry("850x700")  # Set a reasonable window size
    app = RobotSimulator(root)
    root.mainloop()
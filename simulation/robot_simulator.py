import tkinter as tk
import math
import sys
import os
import random

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.virtual_sensors import UltrasonicSensor
from simulation.virtual_motors import MotorController

class RobotSimulator:
    def __init__(self, root):
        self.root = root
        
        # Create main frame to hold everything
        self.frame = tk.Frame(root, bg='white')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a title label with high contrast
        self.title_label = tk.Label(self.frame, text="Pet Robot Simulator", font=('Arial', 18, 'bold'), 
                                   bg='white', fg='blue')
        self.title_label.pack(pady=10)
        
        # Create canvas with clear border - making it very visible
        self.canvas = tk.Canvas(self.frame, width=800, height=500, bg='white', 
                              highlightthickness=2, highlightbackground="black")
        self.canvas.pack(padx=10, pady=10)
        
        print("Canvas created with dimensions 800x500")
        
        # Make 100% sure the canvas is visible - draw a test rectangle
        self.canvas.create_rectangle(0, 0, 800, 500, outline='black', width=1, tags="debug")
        print("Added debug rectangle covering entire canvas")
        
        # Status display area with high contrast
        self.status_frame = tk.Frame(self.frame, bg='#EEEEEE', bd=2, relief=tk.GROOVE)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.distance_label = tk.Label(self.status_frame, text="Distance: --", 
                                     font=('Arial', 12, 'bold'), bg='#EEEEEE')
        self.distance_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.state_label = tk.Label(self.status_frame, text="State: --", 
                                  font=('Arial', 12, 'bold'), bg='#EEEEEE')
        self.state_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.emotion_label = tk.Label(self.status_frame, text="Emotion: --", 
                                    font=('Arial', 12, 'bold'), bg='#EEEEEE')
        self.emotion_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Force an update to make sure the canvas is rendered
        self.root.update_idletasks()
        self.canvas.update()
        
        # Create obstacles - using very bright red for visibility
        self.obstacles = []
        self._create_obstacles()
        print(f"Created {len(self.obstacles)} obstacles")
        
        # Create the robot with high-contrast colors
        self.robot = self._create_robot()
        print("Robot created at center of canvas")
        
        # Create direction indicator
        center_x, center_y = 400, 300  # Center coordinates
        self.direction = self.canvas.create_line(
            center_x, center_y, center_x + 50, center_y, 
            fill='red', width=4, arrow=tk.LAST, tags="robot"
        )
        print("Direction indicator created")
        
        # Force another update to make sure objects are rendered
        self.root.update_idletasks()
        self.canvas.update()
        
        # Initialize virtual components
        self.sensor = UltrasonicSensor(self.canvas, self.robot, self.obstacles)
        self.motors = MotorController(self.robot, self.direction, self.canvas)
        
        # Control buttons using native macOS-compatible widgets
        self._create_control_panel()
        
        # Initialize UI update status
        self.last_distance = 100
        self.current_state = "Initializing"
        self.current_emotion = "Neutral"
        
        print("Robot simulator initialization complete")
        
        # Start simulation loop
        self.canvas.after(100, self.update)
    
    def _create_obstacles(self):
        """Create obstacles with high visibility"""
        # Very bright red for maximum visibility on macOS
        obstacle_color = '#FF0000'
        
        # Create obstacles - store them in the list
        self.obstacles.append(self.canvas.create_rectangle(
            100, 100, 200, 200, fill=obstacle_color, outline='black', width=3))
        
        self.obstacles.append(self.canvas.create_rectangle(
            600, 400, 700, 500, fill=obstacle_color, outline='black', width=3))
        
        self.obstacles.append(self.canvas.create_rectangle(
            300, 500, 500, 550, fill=obstacle_color, outline='black', width=3))
        
        self.obstacles.append(self.canvas.create_rectangle(
            700, 100, 780, 250, fill=obstacle_color, outline='black', width=3))
    
    def _create_robot(self):
        """Create the robot with high visibility"""
        # Very bright blue for maximum visibility
        robot_color = '#0000FF'
        robot_fill = '#00AAFF' 
        
        # Create a robot at the center of the canvas
        return self.canvas.create_oval(
            350, 250, 450, 350, 
            fill=robot_fill, outline=robot_color, width=5,
            tags="robot"
        )
    
    def _create_control_panel(self):
        """Create control panel with native macOS-compatible widgets"""
        # Control buttons frame
        self.control_frame = tk.Frame(self.frame, bd=2, relief=tk.GROOVE, bg='#EEEEEE')
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title for controls
        tk.Label(self.control_frame, text="Manual Controls", 
               font=('Arial', 14, 'bold'), bg='#EEEEEE').pack(pady=5)
        
        # Button frame for layout
        button_frame = tk.Frame(self.control_frame, bg='#EEEEEE')
        button_frame.pack(pady=10)
        
        # Create buttons with native look
        # Forward button in top middle
        tk.Button(button_frame, text="Forward", command=lambda: self.motors.move_forward(0.5),
                width=10, height=2, bg='#DDDDDD', relief=tk.RAISED).grid(row=0, column=1, padx=5, pady=5)
        
        # Left button on the left
        tk.Button(button_frame, text="Left", command=lambda: self.motors.turn_left(0.5),
                width=10, height=2, bg='#DDDDDD', relief=tk.RAISED).grid(row=1, column=0, padx=5, pady=5)
        
        # Stop button in the middle
        tk.Button(button_frame, text="Stop", command=self.motors.stop,
                width=10, height=2, bg='#FFCCCC', relief=tk.RAISED).grid(row=1, column=1, padx=5, pady=5)
        
        # Right button on the right
        tk.Button(button_frame, text="Right", command=lambda: self.motors.turn_right(0.5),
                width=10, height=2, bg='#DDDDDD', relief=tk.RAISED).grid(row=1, column=2, padx=5, pady=5)
        
        # Back button in bottom middle
        tk.Button(button_frame, text="Back", command=lambda: self.motors.move_backward(0.5),
                width=10, height=2, bg='#DDDDDD', relief=tk.RAISED).grid(row=2, column=1, padx=5, pady=5)
        
        # Add a separator
        tk.Frame(self.control_frame, height=2, bd=1, relief=tk.SUNKEN, bg='gray').pack(fill=tk.X, padx=10, pady=10)
        
        # Auto-pilot frame
        auto_frame = tk.Frame(self.control_frame, bg='#EEEEEE')
        auto_frame.pack(pady=10, fill=tk.X)
        
        # Auto-pilot toggle
        self.autopilot_var = tk.BooleanVar(value=True)
        self.autopilot_check = tk.Checkbutton(auto_frame, text="Auto-pilot Mode", 
                                            variable=self.autopilot_var,
                                            font=('Arial', 12), bg='#EEEEEE')
        self.autopilot_check.pack(side=tk.LEFT, padx=20)
        
        # Add a reset button
        tk.Button(auto_frame, text="Reset Position", bg='#CCDDFF',
                 command=self.reset_robot_position).pack(side=tk.RIGHT, padx=20)
    
    def reset_robot_position(self):
        """Reset the robot to the center of the canvas"""
        print("Resetting robot position...")
        
        # Get current robot position
        robot_coords = self.canvas.coords(self.robot)
        if not robot_coords:
            print("ERROR: Could not get robot coordinates")
            return
            
        curr_x = (robot_coords[0] + robot_coords[2]) / 2
        curr_y = (robot_coords[1] + robot_coords[3]) / 2
        
        # Calculate movement needed to center
        target_x, target_y = 400, 300  # Center of canvas
        dx = target_x - curr_x
        dy = target_y - curr_y
        
        # Move robot and direction indicator
        self.canvas.move(self.robot, dx, dy)
        self.canvas.move(self.direction, dx, dy)
        
        # Reset rotation (make robot face right)
        self.motors.direction = 0
        self.motors._update_direction()
        
        self.canvas.update()
        print("Robot position reset to center")
        
    def update(self):
        """Update the simulation"""
        # Print debug to confirm update is being called
        print("Simulator update...")
        
        # Update sensor readings
        distance = self.sensor.measure_distance()
        self.last_distance = distance
        
        # Control logic (only if autopilot is enabled)
        if self.autopilot_var.get():
            if distance < 50:  # If obstacle detected within 50px
                # Turn randomly left or right when obstacle detected
                if random.choice([True, False]):
                    self.motors.turn_left(0.1)
                else:
                    self.motors.turn_right(0.1)
                self.current_state = "Avoiding"
            else:
                # Occasionally change direction during roaming
                if random.random() < 0.02:  # 2% chance per update
                    if random.choice([True, False]):
                        self.motors.turn_left(0.05)
                    else:
                        self.motors.turn_right(0.05)
                else:
                    self.motors.move_forward(0.1)  # Move forward
                self.current_state = "Roaming"
        
        # Update UI labels    
        self.distance_label.config(text=f"Distance: {distance:.1f}px")
        self.state_label.config(text=f"State: {self.current_state}")
        self.emotion_label.config(text=f"Emotion: {self.current_emotion}")
        
        # Keep robot within bounds
        self._constrain_to_canvas()
        
        # Force canvas update
        self.canvas.update_idletasks()
        
        # Schedule next update
        self.root.after(100, self.update)
    
    def _constrain_to_canvas(self):
        """Keep the robot within the canvas bounds"""
        robot_coords = self.canvas.coords(self.robot)
        if not robot_coords:
            return
            
        # Check if robot is out of bounds and adjust
        margin = 10
        canvas_width = 800
        canvas_height = 500
        
        # Left boundary
        if robot_coords[0] < margin:
            dx = margin - robot_coords[0]
            self.canvas.move(self.robot, dx, 0)
            self.canvas.move(self.direction, dx, 0)
            
        # Right boundary
        if robot_coords[2] > canvas_width - margin:
            dx = canvas_width - margin - robot_coords[2]
            self.canvas.move(self.robot, dx, 0)
            self.canvas.move(self.direction, dx, 0)
            
        # Top boundary
        if robot_coords[1] < margin:
            dy = margin - robot_coords[1]
            self.canvas.move(self.robot, 0, dy)
            self.canvas.move(self.direction, 0, dy)
            
        # Bottom boundary
        if robot_coords[3] > canvas_height - margin:
            dy = canvas_height - margin - robot_coords[3]
            self.canvas.move(self.robot, 0, dy)
            self.canvas.move(self.direction, 0, dy)
    
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
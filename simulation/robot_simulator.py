# simulation/robot_simulator.py
import tkinter as tk
import math
from virtual_sensors import UltrasonicSensor
from virtual_motors import MotorController

class RobotSimulator:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()
        
        # Create virtual robot components
        self.robot = self.canvas.create_oval(350, 250, 450, 350, fill='lightblue')
        self.direction = self.canvas.create_line(400, 300, 425, 300, fill='red', width=2)
        
        # Create some obstacles
        self.obstacles = [
            self.canvas.create_rectangle(100, 100, 200, 200, fill='gray'),
            self.canvas.create_rectangle(600, 400, 700, 500, fill='gray'),
            self.canvas.create_rectangle(300, 500, 500, 550, fill='gray')
        ]
        
        # Initialize virtual components
        self.sensor = UltrasonicSensor(self.canvas, self.robot, self.obstacles)
        self.motors = MotorController(self.robot, self.direction, self.canvas)
        
        # Start simulation loop
        self.update()
        
    def update(self):
        # Update sensor readings
        distance = self.sensor.measure_distance()
        
        # Example control logic
        if distance < 50:  # If obstacle detected within 50px
            self.motors.turn_left(0.1)  # Turn to avoid
        else:
            self.motors.move_forward(5)  # Move forward
            
        # Update display
        sensor_text = f"Distance: {distance:.1f}px"
        self.canvas.create_text(100, 50, text=sensor_text, fill='black', font=('Arial', 12))
        
        # Schedule next update
        self.root.after(100, self.update)

# Run simulator when script is executed directly
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pet Robot Simulator")
    app = RobotSimulator(root)
    root.mainloop()
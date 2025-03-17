# simulation/gui_display.py
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import math

class RobotVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Robot Visualization")
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        
        # Robot state
        self.robot_x = 400
        self.robot_y = 300
        self.robot_heading = 0  # In radians
        
        # Robot image
        self.robot_image = self.create_robot_image()
        self.robot_on_canvas = self.canvas.create_image(
            self.robot_x, self.robot_y, image=self.robot_image
        )
        
        # Control panel
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)
        
        tk.Button(self.control_frame, text="Forward", command=self.move_forward).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Left", command=self.turn_left).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Right", command=self.turn_right).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Back", command=self.move_backward).pack(side=tk.LEFT, padx=5)
        
        # Sensor visualization
        self.update_sensor_display()
        
    def create_robot_image(self, size=60):
        # Create a round robot image with direction indicator
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw robot body
        draw.ellipse([0, 0, size, size], fill="lightblue", outline="blue")
        
        # Draw direction indicator
        center = size // 2
        draw.line([(center, center), (size-5, center)], fill="red", width=3)
        
        # Draw wheels
        draw.rectangle([size//4, 5, size//4+5, size-5], fill="black")
        draw.rectangle([size-size//4-5, 5, size-size//4, size-5], fill="black")
        
        # Convert to PhotoImage
        return ImageTk.PhotoImage(image)
        
    def update_robot_position(self):
        # Update robot on canvas
        self.canvas.coords(self.robot_on_canvas, self.robot_x, self.robot_y)
        
        # Rotate robot image based on heading
        # Note: In a real implementation, you'd regenerate the image with rotation
        # This example would need a more complex implementation to handle rotation
        self.update_sensor_display()
        
    def update_sensor_display(self):
        # Clear previous sensor visualization
        self.canvas.delete("sensor")
        
        # Draw ultrasonic cone
        sensor_length = 100  # Length of sensor visualization
        # Calculate positions based on heading
        end_x = self.robot_x + math.cos(self.robot_heading) * sensor_length
        end_y = self.robot_y + math.sin(self.robot_heading) * sensor_length
        
        # Draw sensor cone
        cone_width = math.pi/4  # 45 degrees wide
        left_x = self.robot_x + math.cos(self.robot_heading - cone_width/2) * sensor_length
        left_y = self.robot_y + math.sin(self.robot_heading - cone_width/2) * sensor_length
        right_x = self.robot_x + math.cos(self.robot_heading + cone_width/2) * sensor_length
        right_y = self.robot_y + math.sin(self.robot_heading + cone_width/2) * sensor_length
        
        self.canvas.create_polygon(
            self.robot_x, self.robot_y, left_x, left_y, right_x, right_y,
            fill="yellow", outline="orange", stipple="gray12", tags="sensor"
        )
        
    def move_forward(self):
        # Move robot in current heading direction
        move_distance = 10
        self.robot_x += math.cos(self.robot_heading) * move_distance
        self.robot_y += math.sin(self.robot_heading) * move_distance
        self.update_robot_position()
        
    def move_backward(self):
        # Move robot in opposite of heading direction
        move_distance = 10
        self.robot_x -= math.cos(self.robot_heading) * move_distance
        self.robot_y -= math.sin(self.robot_heading) * move_distance
        self.update_robot_position()
        
    def turn_left(self):
        # Rotate robot counter-clockwise
        self.robot_heading -= math.pi/6  # 30 degrees
        self.update_robot_position()
        
    def turn_right(self):
        # Rotate robot clockwise
        self.robot_heading += math.pi/6  # 30 degrees
        self.update_robot_position()

# Run as standalone
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotVisualizer(root)
    root.mainloop()
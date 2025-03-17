#!/usr/bin/env python3
import tkinter as tk
import sys
import platform

def check_tkinter():
    """Check if Tkinter is working correctly"""
    print("Python version:", sys.version)
    print("Tkinter version:", tk.TkVersion)
    print("OS:", platform.system(), platform.release())

    root = tk.Tk()
    root.title("Tkinter Test")
    root.geometry("600x500")

    # Create a frame
    frame = tk.Frame(root, bg='white')
    frame.pack(fill=tk.BOTH, expand=True)

    # Add a title
    title = tk.Label(frame, text="Tkinter Rendering Test", 
                   font=("Arial", 16, "bold"), bg='white')
    title.pack(pady=10)

    # Create a canvas
    canvas = tk.Canvas(frame, width=400, height=300, 
                     bg='white', highlightbackground="black", highlightthickness=2)
    canvas.pack(padx=10, pady=10)

    # Draw test shapes
    # Rectangle
    canvas.create_rectangle(50, 50, 150, 100, fill='red', outline='black', width=2, tags="test_shape")
    
    # Oval
    canvas.create_oval(200, 50, 300, 100, fill='blue', outline='black', width=2, tags="test_shape")
    
    # Line
    canvas.create_line(50, 150, 350, 150, fill='green', width=3, arrow=tk.LAST, tags="test_shape")
    
    # Text
    canvas.create_text(200, 200, text="Can you see this text?", 
                     fill='black', font=('Arial', 14), tags="test_shape")

    # Results panel
    results = tk.Frame(frame, bg='#EEEEEE', bd=2, relief=tk.GROOVE)
    results.pack(fill=tk.X, padx=10, pady=10)
    
    tk.Label(results, text="Do you see all the shapes on the canvas?", 
           bg='#EEEEEE', font=('Arial', 12)).pack(pady=5)
    
    def shapes_visible():
        print("User reports shapes are visible")
        label_result.config(text="Good! Your Tkinter is working correctly.", fg='green')
        
    def shapes_not_visible():
        print("User reports shapes are NOT visible")
        label_result.config(text="There may be an issue with your Tkinter rendering.", fg='red')
    
    button_frame = tk.Frame(results, bg='#EEEEEE')
    button_frame.pack(pady=5)
    
    tk.Button(button_frame, text="Yes, I see them", 
            command=shapes_visible, bg='#CCFFCC').pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="No, I don't see them", 
            command=shapes_not_visible, bg='#FFCCCC').pack(side=tk.LEFT, padx=10)
    
    label_result = tk.Label(results, text="", font=('Arial', 12, 'bold'), 
                          bg='#EEEEEE', wraplength=400)
    label_result.pack(pady=10)
    
    # Force update
    root.update_idletasks()
    
    root.mainloop()

if __name__ == "__main__":
    check_tkinter()

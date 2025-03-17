import tkinter as tk

# Create a simple test window
root = tk.Tk()
root.title("GUI Test")
root.geometry("400x200")  # Set window size

# Add a label with text
label = tk.Label(root, text="If you can see this, Tkinter is working!", 
                font=("Arial", 16))
label.pack(pady=50)

# Add a button that closes the window
button = tk.Button(root, text="Close", command=root.destroy)
button.pack()

print("Starting Tkinter test window...")
root.mainloop()
print("Window closed.")

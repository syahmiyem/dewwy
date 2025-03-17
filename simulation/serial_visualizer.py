import queue
import threading
import time
import random

class SerialVisualizer:
    """Visualizes serial communication between Arduino and Raspberry Pi"""
    
    def __init__(self):
        self.messages = []  # List of recent messages
        self.max_messages = 10  # Maximum number of messages to display
        self.active = False  # Is there active communication?
        self.last_activity = time.time()
        self.activity_timeout = 1.0  # How long before we consider communication inactive
        self.rx_bytes = 0  # Received bytes
        self.tx_bytes = 0  # Transmitted bytes
        
        # Message queues
        self.arduino_to_pi = queue.Queue()
        self.pi_to_arduino = queue.Queue()
    
    def add_message(self, message, direction="A→R"):
        """Add a message to the visualization
        
        Args:
            message: The message content
            direction: "A→R" for Arduino to Raspberry Pi, "R→A" for the reverse
        """
        timestamp = time.strftime("%H:%M:%S")
        
        if direction == "A→R":
            self.rx_bytes += len(message)
        else:
            self.tx_bytes += len(message)
        
        # Add message to the list
        self.messages.append({
            "timestamp": timestamp,
            "direction": direction,
            "message": message
        })
        
        # Truncate message list if too long
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # Mark activity
        self.active = True
        self.last_activity = time.time()
    
    def update(self):
        """Update the visualizer state"""
        # Check for timeout
        if time.time() - self.last_activity > self.activity_timeout:
            self.active = False
    
    def get_activity_indicator(self):
        """Get a visual indicator of activity level (0-1)"""
        if not self.active:
            return 0
            
        # More recent activity = higher value
        age = time.time() - self.last_activity
        return max(0, 1 - (age / self.activity_timeout))
    
    def get_recent_messages(self, max_count=5):
        """Get recent messages for display"""
        return self.messages[-max_count:] if self.messages else []
    
    def get_statistics(self):
        """Get communication statistics"""
        return {
            "rx_bytes": self.rx_bytes,
            "tx_bytes": self.tx_bytes,
            "message_count": len(self.messages),
            "active": self.active
        }

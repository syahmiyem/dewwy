import arcade

class Dashboard:
    """Component for drawing system dashboard"""
    
    def __init__(self):
        # Component status defaults
        self.component_status = {
            "battery": 100,
            "cpu_usage": 0,
            "temperature": 25.0,
            "memory_used": 0,
        }
        self.serial_active = False
    
    def update_status(self, status_dict):
        """Update the component status values"""
        for key, value in status_dict.items():
            if key in self.component_status:
                self.component_status[key] = value
    
    def set_serial_active(self, active):
        """Set whether serial communication is active"""
        self.serial_active = active
    
    def draw(self, x, y, width=220, height=220):
        """Draw the dashboard at the specified position"""
        # Background panel
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (0, 0, 0, 150)  # Semi-transparent black
        )
        
        # Battery level
        battery = self.component_status["battery"]
        battery_color = arcade.color.GREEN
        if battery < 30:
            battery_color = arcade.color.RED
        elif battery < 60:
            battery_color = arcade.color.YELLOW
            
        arcade.draw_text(
            f"Battery: {battery:.0f}%",
            x - width/2 + 10, y + height/2 - 20,
            battery_color,
            14
        )
        
        # CPU usage
        arcade.draw_text(
            f"CPU: {self.component_status['cpu_usage']:.0f}%",
            x - width/2 + 10, y + height/2 - 50,
            arcade.color.WHITE,
            14
        )
        
        # Temperature
        arcade.draw_text(
            f"Temp: {self.component_status['temperature']:.1f}°C",
            x - width/2 + 10, y + height/2 - 80,
            arcade.color.WHITE,
            14
        )
        
        # Serial status
        serial_status = "ACTIVE" if self.serial_active else "IDLE"
        arcade.draw_text(
            f"Serial: {serial_status}",
            x - width/2 + 10, y + height/2 - 110,
            arcade.color.GREEN if self.serial_active else arcade.color.GRAY,
            14
        )
        
        # Memory use
        arcade.draw_text(
            f"Mem: {self.component_status['memory_used']:.0f}%",
            x - width/2 + 10, y + height/2 - 140,
            arcade.color.WHITE,
            14
        )

class SerialMonitor:
    """Component for drawing serial communication monitor"""
    
    def __init__(self):
        self.rx_messages = []
        self.tx_messages = []
        self.max_messages = 10
        self.rx_bytes = 0
        self.tx_bytes = 0
    
    def add_message(self, message, direction="rx"):
        """Add a message to the history"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        
        if direction == "rx":
            self.rx_messages.append({
                "timestamp": timestamp,
                "content": message
            })
            self.rx_bytes += len(message)
            while len(self.rx_messages) > self.max_messages:
                self.rx_messages.pop(0)
        else:
            self.tx_messages.append({
                "timestamp": timestamp,
                "content": message
            })
            self.tx_bytes += len(message)
            while len(self.tx_messages) > self.max_messages:
                self.tx_messages.pop(0)
    
    def draw(self, x, y, width=280, height=300):
        """Draw the serial monitor at the specified position"""
        # Background panel
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (0, 0, 0, 150)  # Semi-transparent black
        )
        
        # Title
        arcade.draw_text(
            "SERIAL MONITOR",
            x - width/2 + 10, y + height/2 - 20,
            arcade.color.WHITE,
            16
        )
        
        # Recent RX messages
        y_pos = y + height/2 - 50
        arcade.draw_text(
            "RX Messages:",
            x - width/2 + 10, y_pos,
            arcade.color.GREEN,
            12
        )
        y_pos -= 20
        
        for i, msg in enumerate(reversed(self.rx_messages[:5])):
            arcade.draw_text(
                f"{msg['timestamp']}: {msg['content'][:20]}",
                x - width/2 + 10, y_pos - (i * 20),
                arcade.color.WHITE,
                10
            )
        
        # Recent TX messages
        y_pos = y + height/2 - 170
        arcade.draw_text(
            "TX Messages:",
            x - width/2 + 10, y_pos,
            arcade.color.ORANGE,
            12
        )
        y_pos -= 20
        
        for i, msg in enumerate(reversed(self.tx_messages[:5])):
            arcade.draw_text(
                f"{msg['timestamp']}: {msg['content'][:20]}",
                x - width/2 + 10, y_pos - (i * 20),
                arcade.color.WHITE,
                10
            )
        
        # Byte counts
        arcade.draw_text(
            f"RX: {self.rx_bytes} bytes  TX: {self.tx_bytes} bytes",
            x - width/2 + 10, y - height/2 + 30,
            arcade.color.WHITE,
            10
        )

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
        # Background panel with rounded corners
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (40, 44, 52, 220)  # Semi-transparent dark gray
        )
        
        # Panel border
        arcade.draw_rectangle_outline(
            x, y, width, height,
            (80, 90, 100),
            2
        )
        
        # Panel title
        arcade.draw_text(
            "SYSTEM DASHBOARD",
            x - width/2 + 10, y + height/2 - 25,
            arcade.color.WHITE,
            16,
            bold=True
        )
        
        # Horizontal separator
        arcade.draw_line(
            x - width/2 + 10, y + height/2 - 35,
            x + width/2 - 10, y + height/2 - 35,
            arcade.color.GRAY,
            1
        )
        
        # Battery level with colored gauge
        battery = self.component_status["battery"]
        battery_color = arcade.color.GREEN
        if battery < 20:
            battery_color = arcade.color.RED
        elif battery < 50:
            battery_color = arcade.color.YELLOW
        
        # Battery label    
        arcade.draw_text(
            f"Battery:",
            x - width/2 + 15, y + height/2 - 60,
            arcade.color.WHITE,
            14
        )
        
        # Battery gauge background
        gauge_width = 120
        gauge_height = 16
        arcade.draw_rectangle_filled(
            x + width/2 - 15 - gauge_width/2, y + height/2 - 60 + gauge_height/2,
            gauge_width, gauge_height,
            arcade.color.DARK_GRAY
        )
        
        # Battery gauge fill
        fill_width = gauge_width * (battery / 100)
        arcade.draw_rectangle_filled(
            x + width/2 - 15 - gauge_width/2 + fill_width/2 - gauge_width/2, 
            y + height/2 - 60 + gauge_height/2,
            fill_width, gauge_height - 4,
            battery_color
        )
        
        # Battery percentage
        arcade.draw_text(
            f"{battery:.0f}%",
            x + width/2 - 55, y + height/2 - 60,
            arcade.color.WHITE,
            14,
            bold=True
        )
        
        # CPU usage with gauge
        cpu_usage = self.component_status["cpu_usage"]
        cpu_color = arcade.color.GREEN
        if cpu_usage > 80:
            cpu_color = arcade.color.RED
        elif cpu_usage > 50:
            cpu_color = arcade.color.YELLOW
            
        # CPU label
        arcade.draw_text(
            f"CPU:",
            x - width/2 + 15, y + height/2 - 90,
            arcade.color.WHITE,
            14
        )
        
        # CPU gauge background
        arcade.draw_rectangle_filled(
            x + width/2 - 15 - gauge_width/2, y + height/2 - 90 + gauge_height/2,
            gauge_width, gauge_height,
            arcade.color.DARK_GRAY
        )
        
        # CPU gauge fill
        fill_width = gauge_width * (cpu_usage / 100)
        arcade.draw_rectangle_filled(
            x + width/2 - 15 - gauge_width/2 + fill_width/2 - gauge_width/2, 
            y + height/2 - 90 + gauge_height/2,
            fill_width, gauge_height - 4,
            cpu_color
        )
        
        # CPU percentage
        arcade.draw_text(
            f"{cpu_usage:.0f}%",
            x + width/2 - 55, y + height/2 - 90,
            arcade.color.WHITE,
            14
        )
        
        # Temperature display
        temp = self.component_status["temperature"]
        temp_color = arcade.color.GREEN
        if temp > 70:
            temp_color = arcade.color.RED
        elif temp > 50:
            temp_color = arcade.color.YELLOW
            
        arcade.draw_text(
            f"Temperature: {temp:.1f}°C",
            x - width/2 + 15, y + height/2 - 120,
            temp_color,
            14
        )
        
        # Serial connection status
        serial_status = "ACTIVE" if self.serial_active else "IDLE"
        serial_color = arcade.color.GREEN if self.serial_active else arcade.color.GRAY
        
        arcade.draw_text(
            f"Serial: {serial_status}",
            x - width/2 + 15, y + height/2 - 150,
            serial_color,
            14
        )
        
        # Memory usage
        mem = self.component_status["memory_used"]
        arcade.draw_text(
            f"Memory: {mem:.0f}%",
            x - width/2 + 15, y + height/2 - 180,
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
        # Background panel with rounded corners
        arcade.draw_rectangle_filled(
            x, y, width, height,
            (40, 44, 52, 220)  # Semi-transparent dark gray
        )
        
        # Panel border
        arcade.draw_rectangle_outline(
            x, y, width, height,
            (80, 90, 100),
            2
        )
        
        # Title
        arcade.draw_text(
            "SERIAL MONITOR",
            x - width/2 + 10, y + height/2 - 25,
            arcade.color.WHITE,
            16,
            bold=True
        )
        
        # Horizontal separator
        arcade.draw_line(
            x - width/2 + 10, y + height/2 - 35,
            x + width/2 - 10, y + height/2 - 35,
            arcade.color.GRAY,
            1
        )
        
        # Recent RX messages
        y_pos = y + height/2 - 50
        arcade.draw_text(
            "RX Messages:",
            x - width/2 + 10, y_pos,
            arcade.color.GREEN,
            12,
            bold=True
        )
        y_pos -= 20
        
        # RX message box background
        rx_box_height = 100
        arcade.draw_rectangle_filled(
            x, y_pos - rx_box_height/2 + 10,
            width - 20, rx_box_height,
            arcade.color.DARK_BLUE_GRAY
        )
        
        # Draw RX messages
        for i, msg in enumerate(reversed(self.rx_messages[:5])):
            arcade.draw_text(
                f"{msg['timestamp']}: {msg['content'][:28]}",
                x - width/2 + 15, y_pos - (i * 20),
                arcade.color.WHITE,
                10
            )
        
        # Recent TX messages
        y_pos = y + height/2 - 165
        arcade.draw_text(
            "TX Messages:",
            x - width/2 + 10, y_pos,
            arcade.color.ORANGE,
            12,
            bold=True
        )
        y_pos -= 20
        
        # TX message box background
        tx_box_height = 100
        arcade.draw_rectangle_filled(
            x, y_pos - tx_box_height/2 + 10, 
            width - 20, tx_box_height,
            arcade.color.DARK_BLUE_GRAY
        )
        
        # Draw TX messages
        for i, msg in enumerate(reversed(self.tx_messages[:5])):
            arcade.draw_text(
                f"{msg['timestamp']}: {msg['content'][:28]}",
                x - width/2 + 15, y_pos - (i * 20),
                arcade.color.WHITE,
                10
            )
        
        # Byte counts
        arcade.draw_text(
            f"RX: {self.rx_bytes} bytes  TX: {self.tx_bytes} bytes",
            x - width/2 + 10, y - height/2 + 20,
            arcade.color.WHITE,
            10
        )

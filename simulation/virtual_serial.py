# simulation/virtual_serial.py
import serial
import threading
import time
import queue
import random

class VirtualArduino(threading.Thread):
    def __init__(self, port="/dev/pts/2", simulator=None):
        threading.Thread.__init__(self)
        self.port = port
        self.simulator = simulator  # Reference to simulator for visualization
        self.running = True
        self.connected = False
        
        # Communication queues
        self.to_rpi_queue = queue.Queue()  # Messages going to RPi
        self.from_rpi_queue = queue.Queue()  # Commands from RPi
        
        # Sensor data
        self.distance = 100  # Default distance in cm
        self.last_command = "NONE"
        self.motor_speed = 0
        
        # Try to open serial port if not in pure simulation mode
        try:
            self.ser = serial.Serial(port, 9600)
            self.connected = True
            print(f"Serial connection opened on {port}")
        except:
            print(f"Could not open serial port {port}. Running in simulation mode.")
            self.ser = None
            
    def run(self):
        while self.running:
            # In simulation mode, update the distance with some random variation
            if self.simulator:
                if hasattr(self.simulator, 'sensor'):
                    self.distance = self.simulator.sensor.measure_distance()
                else:
                    # Add some random drift to distance
                    self.distance += random.uniform(-5, 5)
                    self.distance = max(5, min(200, self.distance))
            
            # Send simulated data to Raspberry Pi
            message = f"DIST:{int(self.distance)}\n"
            self.to_rpi_queue.put(message)
            
            if self.ser and self.connected:
                try:
                    # Send data over the physical serial connection
                    self.ser.write(message.encode())
                    
                    # Check for commands from Raspberry Pi on physical connection
                    if self.ser.in_waiting > 0:
                        command = self.ser.readline().decode().strip()
                        self._process_command(command)
                except Exception as e:
                    print(f"Serial error: {e}")
                    self.connected = False
            
            # Process any commands in the queue (from simulator)
            try:
                while not self.from_rpi_queue.empty():
                    command = self.from_rpi_queue.get_nowait()
                    self._process_command(command)
            except queue.Empty:
                pass
                
            time.sleep(0.1)
            
    def _process_command(self, command):
        """Process commands from Raspberry Pi"""
        print(f"Arduino received: {command}")
        self.last_command = command
        
        # Process motor commands
        if command == "FWD":
            self.motor_speed = 150  # Forward speed
        elif command == "BCK":
            self.motor_speed = -150  # Backward speed
        elif command == "LFT":
            self.motor_speed = 0  # Turn left (simplified)
        elif command == "RGT":
            self.motor_speed = 0  # Turn right (simplified)
        elif command == "STP":
            self.motor_speed = 0  # Stop
        
        # Send acknowledgment
        ack = f"ACK:{command}\n"
        self.to_rpi_queue.put(ack)
        
        if self.ser and self.connected:
            try:
                self.ser.write(ack.encode())
            except:
                pass
    
    def send_command(self, command):
        """Send a command to the Arduino (from RPi)"""
        self.from_rpi_queue.put(command)
    
    def get_next_message(self):
        """Get the next message from Arduino (to RPi)"""
        try:
            return self.to_rpi_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_distance(self):
        """Get the current distance reading"""
        return self.distance
    
    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

# Run when executed directly
if __name__ == "__main__":
    arduino = VirtualArduino()
    arduino.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        arduino.stop()
        print("Virtual Arduino stopped")
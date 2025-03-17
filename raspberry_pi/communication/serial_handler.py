import serial
import threading
import time
import queue

class SerialHandler:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600, simulation=True):
        self.port = port
        self.baud_rate = baud_rate
        self.simulation = simulation
        self.running = True
        self.connected = False
        self.ser = None
        
        # Queue to store received data
        self.receive_queue = queue.Queue()
        
        # Last sensor readings
        self.last_distance = 100  # Default value (cm)
        
        # Connect to serial
        self.connect()
        
    def connect(self):
        if self.simulation:
            print(f"[SERIAL] Simulating connection to {self.port}")
            self.connected = True
            
            # Start simulated reading thread
            self.read_thread = threading.Thread(target=self._simulated_read_loop)
            self.read_thread.daemon = True
            self.read_thread.start()
        else:
            try:
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
                self.connected = True
                print(f"[SERIAL] Connected to {self.port}")
                
                # Start real reading thread
                self.read_thread = threading.Thread(target=self._read_loop)
                self.read_thread.daemon = True
                self.read_thread.start()
            except Exception as e:
                print(f"[SERIAL] Failed to connect: {e}")
    
    def _read_loop(self):
        """Read incoming data from Arduino"""
        while self.running and self.connected and not self.simulation:
            try:
                if self.ser and self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    self._process_data(line)
            except Exception as e:
                print(f"[SERIAL] Read error: {e}")
                self.connected = False
                break
            time.sleep(0.01)
    
    def _simulated_read_loop(self):
        """Simulate incoming data from Arduino"""
        import random
        while self.running and self.connected and self.simulation:
            # Simulate distance readings
            dist = random.randint(10, 200)
            self._process_data(f"DIST:{dist}")
            time.sleep(0.5)  # Simulate sensor update frequency
    
    def _process_data(self, data):
        """Process incoming data"""
        if data.startswith("DIST:"):
            try:
                self.last_distance = int(data.split(':')[1])
            except ValueError:
                pass
        
        # Queue the data for any listeners
        self.receive_queue.put(data)
    
    def send_command(self, command):
        """Send command to Arduino"""
        if not self.connected:
            print("[SERIAL] Not connected")
            return False
        
        if self.simulation:
            print(f"[SERIAL] Simulating sending: {command}")
            # Simulate acknowledgment
            self.receive_queue.put(f"ACK:{command}")
            return True
        else:
            try:
                self.ser.write(f"{command}\n".encode('utf-8'))
                return True
            except Exception as e:
                print(f"[SERIAL] Send error: {e}")
                self.connected = False
                return False
    
    def get_distance(self):
        """Get last measured distance"""
        return self.last_distance
    
    def get_next_message(self, block=False, timeout=None):
        """Get next message from the queue"""
        try:
            return self.receive_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def disconnect(self):
        """Close the serial connection"""
        self.running = False
        if self.ser and not self.simulation:
            self.ser.close()
        self.connected = False

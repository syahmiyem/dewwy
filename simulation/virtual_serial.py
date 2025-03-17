# simulation/virtual_serial.py
import serial
import threading
import time

class VirtualArduino(threading.Thread):
    def __init__(self, port="/dev/pts/2"):
        threading.Thread.__init__(self)
        self.port = port
        self.ser = serial.Serial(port, 9600)
        self.running = True
        
    def run(self):
        while self.running:
            # Simulate ultrasonic sensor readings
            distance = 100  # Default distance in cm
            
            # Send simulated data to Raspberry Pi
            self.ser.write(f"DIST:{distance}\n".encode())
            
            # Check for commands from Raspberry Pi
            if self.ser.in_waiting > 0:
                command = self.ser.readline().decode().strip()
                print(f"Arduino received: {command}")
                
                # Acknowledge command
                self.ser.write(f"ACK:{command}\n".encode())
            
            time.sleep(0.1)
            
    def stop(self):
        self.running = False
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
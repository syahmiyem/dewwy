"""
Headless renderer for Arcade simulator that captures frames for web streaming
"""
import os
import sys
import threading
import time
import queue
from PIL import Image
import io
import base64

# Add project root to Python path for proper importing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import Arcade simulator with special handling
os.environ["ARCADE_HEADLESS"] = "1"  # Tell arcade to run in headless mode

try:
    import arcade
    from simulation.arcade_simulator import ArcadeSimulator
except ImportError:
    print("Error: Arcade or simulator components not available")
    sys.exit(1)

class HeadlessArcadeSimulator:
    """
    Runs the Arcade simulator in a headless mode and captures frames
    for web streaming.
    """
    
    def __init__(self, width=800, height=600):
        # Store dimensions
        self.width = width
        self.height = height
        
        # Frame handling
        self.current_frame = None
        self.frame_queue = queue.Queue(maxsize=2)  # Limit queue size
        self.frame_available = threading.Event()
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        
        # Control
        self.running = False
        self.keys_pressed = set()
        self.simulator_thread = None
        self.simulator = None
        
        # Use a mock window for arcade to work without a display
        self._setup_mock_window()

    def _setup_mock_window(self):
        """Setup a mock window for arcade to work headlessly"""
        # This is a simplified approach - for production, more elaborate mocking would be needed
        arcade.Window.create_sdl_context = lambda x: None
        arcade.Window.on_draw = lambda x: None
        arcade.Window.on_update = lambda x, dt: None
        arcade.Window.flip = lambda x: None
        
    def start(self):
        """Start the headless simulator"""
        if self.running:
            return
            
        self.running = True
        self.simulator_thread = threading.Thread(target=self._run_simulator)
        self.simulator_thread.daemon = True
        self.simulator_thread.start()
        print("Headless Arcade simulator started")

    def _run_simulator(self):
        """Main simulator thread"""
        try:
            # Initialize the simulator
            self.simulator = ArcadeSimulator(self.width, self.height)
            
            # Override methods that depend on a window
            self._monkey_patch_simulator()
            
            # Main loop
            while self.running:
                start_time = time.time()
                
                # Process queued key events
                self._process_keys()
                
                # Update simulator state
                self.simulator.on_update(1/30.0)  # Fixed time step
                
                # Capture frame
                self._capture_frame()
                
                # Maintain frame rate (cap at 30 FPS)
                elapsed = time.time() - start_time
                if elapsed < 1/30:
                    time.sleep(1/30 - elapsed)
                    
        except Exception as e:
            print(f"Error in simulator thread: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            
    def _monkey_patch_simulator(self):
        """Replace methods that require a window with headless versions"""
        # Store original draw method
        self.original_draw = self.simulator.on_draw
        
        # Override draw method to capture the frame
        def headless_draw():
            # Clear buffer and setup for drawing
            arcade.start_render()
            
            # Call original drawing code
            self.original_draw()
            
            # We'll capture the frame elsewhere
            arcade.finish_render()
        
        self.simulator.on_draw = headless_draw
        
    def _capture_frame(self):
        """Capture the current frame from the simulator"""
        # Draw the simulator content
        self.simulator.on_draw()
        
        # Calculate FPS
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
            
        # Use PIL to create a frame (in production, a more efficient approach would be needed)
        # This is a placeholder - actual frame capture would need to use OpenGL offscreen rendering
        image = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        
        # Convert to data URL for web streaming
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        img_data = buffer.getvalue()
        
        # Convert to base64 for embedding in data URL
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{img_base64}"
        
        # Update current frame
        self.current_frame = {
            "data_url": data_url,
            "timestamp": time.time(),
            "fps": self.fps
        }
        
        # Signal that a new frame is available
        try:
            # Update queue with newest frame, discard old if full
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put_nowait(self.current_frame)
            self.frame_available.set()
        except:
            pass
    
    def _process_keys(self):
        """Process queued keyboard events"""
        for key in self.keys_pressed:
            # Pass to the simulator
            if hasattr(self.simulator, 'on_key_press'):
                self.simulator.on_key_press(key, 0)  # 0 for no modifiers
    
    def press_key(self, key):
        """Press a key in the simulator"""
        self.keys_pressed.add(key)
    
    def release_key(self, key):
        """Release a key in the simulator"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            # Pass to the simulator
            if hasattr(self.simulator, 'on_key_release'):
                self.simulator.on_key_release(key, 0)
    
    def get_frame(self, block=False, timeout=None):
        """Get the latest frame"""
        if block:
            self.frame_available.wait(timeout)
            self.frame_available.clear()
            
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop the simulator"""
        self.running = False
        if self.simulator_thread:
            self.simulator_thread.join(timeout=1.0)

import sys
import os
import time
import json
from flask import Flask, render_template, jsonify, request, Response, session
from flask_socketio import SocketIO, emit

# Add project root to Python path for proper importing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the headless simulator
from web.arcade_headless import HeadlessArcadeSimulator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dewwy-secret-key'
socketio = SocketIO(app)

# Create a global simulator instance
simulator = HeadlessArcadeSimulator(width=800, height=600)

# Key mapping from web to arcade keycodes
KEY_MAPPING = {
    "ArrowUp": 0xFF52,    # arcade.key.UP
    "ArrowDown": 0xFF54,  # arcade.key.DOWN
    "ArrowLeft": 0xFF51,  # arcade.key.LEFT
    "ArrowRight": 0xFF53, # arcade.key.RIGHT
    "Space": 0x0020,      # arcade.key.SPACE
    "KeyA": 0x0061,       # arcade.key.A
    "KeyD": 0x0064,       # arcade.key.D
    "KeyR": 0x0072,       # arcade.key.R
    "KeyS": 0x0073,       # arcade.key.S
    "KeyV": 0x0076,       # arcade.key.V
    "KeyW": 0x0077,       # arcade.key.W
    "KeyC": 0x0063,       # arcade.key.C
    "Escape": 0xFF1B,     # arcade.key.ESCAPE
    "KeyQ": 0x0071,       # arcade.key.Q
}

@app.route('/')
def index():
    """Main page with simulator"""
    return render_template('simulator.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page showing robot status"""
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket"""
    print("Client connected")
    # Start simulator if it's not already running
    if not simulator.running:
        simulator.start()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected")
    # Don't stop simulator - other clients may be connected

@socketio.on('key_down')
def handle_key_down(data):
    """Handle key press event from client"""
    key = data.get('key')
    if key in KEY_MAPPING:
        arcade_key = KEY_MAPPING[key]
        simulator.press_key(arcade_key)
        emit('key_processed', {'key': key, 'action': 'down'})

@socketio.on('key_up')
def handle_key_up(data):
    """Handle key release event from client"""
    key = data.get('key')
    if key in KEY_MAPPING:
        arcade_key = KEY_MAPPING[key]
        simulator.release_key(arcade_key)
        emit('key_processed', {'key': key, 'action': 'up'})

@socketio.on('request_frame')
def handle_frame_request():
    """Send the latest frame when requested"""
    frame = simulator.get_frame(block=False)
    if frame:
        emit('frame_update', frame)

def stream_frames():
    """Background task to stream frames to clients"""
    while True:
        frame = simulator.get_frame(block=True, timeout=1.0)
        if frame:
            socketio.emit('frame_update', frame)
        socketio.sleep(0.033)  # ~30 fps

@app.route('/api/status')
def get_status():
    """Get robot status as JSON"""
    status = {
        "state": simulator.simulator.current_state if simulator.simulator else "Initializing",
        "emotion": simulator.simulator.current_emotion if simulator.simulator else "neutral",
        "time": time.time()
    }
    return jsonify(status)

if __name__ == '__main__':
    # Start the simulator
    simulator.start()
    
    # Start the background task for streaming frames
    socketio.start_background_task(stream_frames)
    
    # Run the web server
    socketio.run(app, debug=True, host='0.0.0.0')

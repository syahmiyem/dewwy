// Simulator client-side script

// Connect to the WebSocket server
const socket = io();

// Get references to DOM elements
const canvas = document.getElementById('simulator-canvas');
const ctx = canvas.getContext('2d');
const connectionStatus = document.getElementById('connection-status');
const fpsCounter = document.getElementById('fps-counter');
const robotState = document.getElementById('robot-state');
const robotEmotion = document.getElementById('robot-emotion');

// Track connection state
let isConnected = false;
let lastFrameTime = 0;
let frameCount = 0;
let fps = 0;

// Connect to WebSocket
socket.on('connect', () => {
    console.log('Connected to server');
    connectionStatus.textContent = 'Connected';
    connectionStatus.className = 'status connected';
    isConnected = true;
    
    // Start requesting frames
    requestAnimationFrame(requestFrame);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    connectionStatus.textContent = 'Disconnected';
    connectionStatus.className = 'status disconnected';
    isConnected = false;
});

// Handle incoming frames
socket.on('frame_update', (frame) => {
    // Render the frame on canvas
    renderFrame(frame);
    
    // Update FPS display
    fpsCounter.textContent = `${frame.fps} FPS`;
    
    // Request next frame
    requestAnimationFrame(requestFrame);
});

// Handle status updates
function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            robotState.textContent = data.state;
            robotEmotion.textContent = data.emotion;
        })
        .catch(error => console.error('Error fetching status:', error));
}

// Request a new frame from the server
function requestFrame() {
    if (isConnected) {
        socket.emit('request_frame');
    }
}

// Render a frame on the canvas
function renderFrame(frame) {
    // Create an image from the data URL
    const img = new Image();
    
    img.onload = () => {
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw the image
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        // Calculate FPS on client side
        const now = performance.now();
        frameCount++;
        
        if (now - lastFrameTime >= 1000) {
            fps = frameCount;
            frameCount = 0;
            lastFrameTime = now;
        }
    };
    
    // Set the image source to the data URL
    img.src = frame.data_url;
}

// Handle keyboard events
document.addEventListener('keydown', (event) => {
    if (isConnected && !event.repeat) {
        socket.emit('key_down', { key: event.code });
        event.preventDefault();
    }
});

document.addEventListener('keyup', (event) => {
    if (isConnected) {
        socket.emit('key_up', { key: event.code });
        event.preventDefault();
    }
});

// Update status periodically
setInterval(updateStatus, 1000);

// Initial status update
updateStatus();

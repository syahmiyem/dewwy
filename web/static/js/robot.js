// Robot status update
let lastUpdateTime = 0;
const updateInterval = 1000; // Update every second

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Start the update loop
    updateRobotStatus();
});

// Main update function
async function updateRobotStatus() {
    try {
        const now = Date.now();
        if (now - lastUpdateTime >= updateInterval) {
            lastUpdateTime = now;
            
            // Fetch robot status
            const response = await fetch('/api/status');
            const data = await response.json();
            
            // Update UI elements
            updateStatusDisplay(data);
            updateFace(data.emotion);
            updateMessages(data.messages);
            updatePersonalityTraits(data.personality);
        }
    } catch (error) {
        console.error('Error updating robot status:', error);
    }
    
    // Schedule next update
    requestAnimationFrame(updateRobotStatus);
}

// Update status display values
function updateStatusDisplay(data) {
    document.getElementById('robot-state').textContent = data.state;
    document.getElementById('robot-emotion').textContent = data.emotion;
    document.getElementById('robot-distance').textContent = Math.round(data.distance) + 'cm';
    
    // Also update dashboard elements if they exist
    if (document.getElementById('dash-state')) {
        document.getElementById('dash-state').textContent = data.state;
        document.getElementById('dash-emotion').textContent = data.emotion;
        document.getElementById('dash-distance').textContent = Math.round(data.distance) + 'cm';
    }
}

// Draw the robot face based on emotion
function updateFace(emotion) {
    const faceContainer = document.getElementById('robot-face');
    if (!faceContainer) return;
    
    // Generate SVG for the face
    let faceSvg = '';
    
    switch(emotion.toLowerCase()) {
        case 'happy':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="8" fill="white" />
                <circle cx="65" cy="40" r="8" fill="white" />
                <path d="M 30 65 Q 50 80 70 65" stroke="white" stroke-width="4" fill="none" />
            </svg>`;
            break;
            
        case 'sad':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="8" fill="white" />
                <circle cx="65" cy="40" r="8" fill="white" />
                <path d="M 30 75 Q 50 60 70 75" stroke="white" stroke-width="4" fill="none" />
            </svg>`;
            break;
            
        case 'excited':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="10" fill="white" />
                <circle cx="65" cy="40" r="10" fill="white" />
                <circle cx="35" cy="40" r="5" fill="black" />
                <circle cx="65" cy="40" r="5" fill="black" />
                <path d="M 30 65 Q 50 85 70 65" stroke="white" stroke-width="5" fill="none" />
            </svg>`;
            break;
            
        case 'sleepy':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <line x1="25" y1="40" x2="45" y2="40" stroke="white" stroke-width="4" />
                <line x1="55" y1="40" x2="75" y2="40" stroke="white" stroke-width="4" />
                <text x="70" y="30" fill="white" font-size="14">z</text>
                <text x="78" y="20" fill="white" font-size="10">z</text>
                <ellipse cx="50" cy="70" rx="15" ry="8" stroke="white" stroke-width="3" fill="none" />
            </svg>`;
            break;
            
        case 'curious':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="8" fill="white" />
                <circle cx="65" cy="40" r="8" fill="white" />
                <line x1="25" y1="30" x2="45" y2="35" stroke="white" stroke-width="3" />
                <circle cx="50" cy="70" r="10" stroke="white" stroke-width="3" fill="none" />
            </svg>`;
            break;
            
        case 'scared':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="35" r="12" fill="white" />
                <circle cx="65" cy="35" r="12" fill="white" />
                <circle cx="35" cy="35" r="8" fill="black" />
                <circle cx="65" cy="35" r="8" fill="black" />
                <ellipse cx="50" cy="70" rx="10" ry="15" stroke="white" stroke-width="3" fill="none" />
            </svg>`;
            break;
            
        case 'playful':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="8" fill="white" />
                <line x1="55" y1="40" x2="75" y2="40" stroke="white" stroke-width="3" />
                <path d="M 30 65 Q 50 80 70 65" stroke="white" stroke-width="4" fill="none" />
                <ellipse cx="50" cy="75" rx="5" ry="10" fill="white" />
            </svg>`;
            break;
            
        case 'grumpy':
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <line x1="25" y1="40" x2="45" y2="40" stroke="white" stroke-width="3" />
                <line x1="55" y1="40" x2="75" y2="40" stroke="white" stroke-width="3" />
                <line x1="25" y1="30" x2="45" y2="35" stroke="white" stroke-width="3" />
                <line x1="55" y1="35" x2="75" y2="30" stroke="white" stroke-width="3" />
                <line x1="30" y1="70" x2="70" y2="75" stroke="white" stroke-width="4" />
            </svg>`;
            break;
            
        default: // Neutral
            faceSvg = `<svg class="emotion-face" viewBox="0 0 100 100">
                <circle cx="35" cy="40" r="8" fill="white" />
                <circle cx="65" cy="40" r="8" fill="white" />
                <line x1="30" y1="70" x2="70" y2="70" stroke="white" stroke-width="4" />
            </svg>`;
    }
    
    faceContainer.innerHTML = faceSvg;
}

// Update message log
function updateMessages(messages) {
    const messagesContainer = document.getElementById('messages');
    if (!messagesContainer) return;
    
    let html = '';
    
    messages.forEach(msg => {
        html += `<div class="message-item">
            <span class="message-time">${msg.time}</span>
            <span class="message-content">${msg.text}</span>
        </div>`;
    });
    
    messagesContainer.innerHTML = html;
    
    // Also update dashboard messages if they exist
    const dashMessages = document.getElementById('dash-messages');
    if (dashMessages) {
        dashMessages.innerHTML = html;
    }
}

// Update personality traits display
function updatePersonalityTraits(traits) {
    const traitsContainer = document.getElementById('personality-traits');
    if (!traitsContainer) return;
    
    let html = '';
    
    for (const [trait, value] of Object.entries(traits)) {
        html += `<div class="trait">
            <span class="trait-label">${capitalizeFirstLetter(trait)}:</span>
            <div class="trait-bar-container">
                <div class="trait-bar" style="width: ${value * 10}%"></div>
            </div>
        </div>`;
    }
    
    traitsContainer.innerHTML = html;
    
    // Also update dashboard traits if they exist
    const dashTraits = document.getElementById('dash-traits');
    if (dashTraits) {
        dashTraits.innerHTML = html;
    }
}

// Helper to capitalize first letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// API functions for interaction
function triggerState(state) {
    fetch(`/api/trigger/state/${state}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => console.log('State triggered:', data));
}

function triggerEmotion(emotion) {
    fetch(`/api/trigger/emotion/${emotion}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => console.log('Emotion triggered:', data));
}

function simulateObstacle() {
    const distance = document.getElementById('obstacle-distance').value;
    fetch('/api/simulate/obstacle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ distance: parseInt(distance) })
    })
    .then(response => response.json())
    .then(data => console.log('Obstacle simulated:', data));
}

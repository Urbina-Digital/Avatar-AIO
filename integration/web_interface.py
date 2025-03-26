"""
Web Interface module for the AI Avatar Platform.

This module provides a Flask-based web interface for the AI Avatar Platform.
"""

import os
import logging
import json
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('web_interface')

class WebInterface:
    """
    Web interface for the AI Avatar Platform.
    
    This class provides a Flask-based web interface for interacting with the
    AI Avatar Platform, including:
    - Visual display of the avatar
    - Chatbox for text communication
    - Upload panels for appearance, voice, and communication data
    - Action buttons for triggering avatar actions
    """
    
    def __init__(self, base_dir=None, port=5000):
        """
        Initialize the WebInterface.
        
        Args:
            base_dir: Base directory for the platform
            port: Port for the web server
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.base_dir = Path(base_dir)
        self.port = port
        
        # Import components
        try:
            from integration.avatar_controller import AvatarController
            self.avatar_controller = AvatarController(base_dir=self.base_dir)
        except ImportError as e:
            logger.warning(f"Failed to import AvatarController: {e}")
            self.avatar_controller = None
        
        # Create Flask app
        self.app = Flask(__name__)
        
        # Set static and template folders
        self.static_folder = str(self.base_dir / 'integration' / 'static')
        self.template_folder = str(self.base_dir / 'integration' / 'templates')
        
        # Register routes
        self._register_routes()
        
        logger.info(f"WebInterface initialized with base directory: {self.base_dir}")
        logger.info(f"Web server will run on port {self.port}")
        logger.info(f"Static folder: {self.static_folder}")
        logger.info(f"Template folder: {self.template_folder}")
    
    def _register_routes(self):
        """Register Flask routes."""
        
        @self.app.route('/')
        def index():
            """Render the main page."""
            return render_template('index.html')
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """Serve static files."""
            return send_from_directory(self.static_folder, filename)
        
        @self.app.route('/api/session/start', methods=['POST'])
        def start_session():
            """Start a new avatar session."""
            data = request.json
            user_id = data.get('user_id', 'default_user')
            
            if self.avatar_controller:
                result = self.avatar_controller.start_session(user_id)
                return jsonify(result)
            else:
                return jsonify({
                    "success": False,
                    "message": "Avatar controller not available"
                })
        
        @self.app.route('/api/session/end', methods=['POST'])
        def end_session():
            """End an avatar session."""
            data = request.json
            user_id = data.get('user_id', 'default_user')
            
            if self.avatar_controller:
                result = self.avatar_controller.end_session(user_id)
                return jsonify(result)
            else:
                return jsonify({
                    "success": False,
                    "message": "Avatar controller not available"
                })
        
        @self.app.route('/api/input', methods=['POST'])
        def process_input():
            """Process user input."""
            data = request.json
            user_id = data.get('user_id', 'default_user')
            input_text = data.get('input', '')
            stealth_mode = data.get('stealth_mode', False)
            
            if self.avatar_controller:
                result = self.avatar_controller.process_user_input(
                    user_id, input_text, stealth_mode
                )
                return jsonify(result)
            else:
                return jsonify({
                    "success": False,
                    "message": "Avatar controller not available"
                })
        
        @self.app.route('/api/responses', methods=['GET'])
        def get_responses():
            """Get pending responses."""
            user_id = request.args.get('user_id', 'default_user')
            clear = request.args.get('clear', 'true').lower() == 'true'
            
            if self.avatar_controller:
                result = self.avatar_controller.get_pending_responses(user_id, clear)
                return jsonify(result)
            else:
                return jsonify({
                    "success": False,
                    "message": "Avatar controller not available"
                })
        
        @self.app.route('/api/action', methods=['POST'])
        def trigger_action():
            """Trigger an avatar action."""
            data = request.json
            user_id = data.get('user_id', 'default_user')
            action = data.get('action', '')
            
            if self.avatar_controller:
                result = self.avatar_controller.trigger_action(user_id, action)
                return jsonify(result)
            else:
                return jsonify({
                    "success": False,
                    "message": "Avatar controller not available"
                })
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get avatar status."""
            user_id = request.args.get('user_id', 'default_user')
            
            if self.avatar_controller:
                result = self.avatar_controller.get_avatar_status(user_id)
                return jsonify(result)
            else:
                return jsonify({
                    "success": False,
                    "message": "Avatar controller not available"
                })
        
        @self.app.route('/api/upload/<data_type>', methods=['POST'])
        def upload_data(data_type):
            """Upload data for training."""
            # This would be implemented in a production version
            # For the prototype, we'll just return a success message
            return jsonify({
                "success": True,
                "message": f"Data uploaded for {data_type}",
                "data_type": data_type
            })
    
    def create_template_files(self):
        """Create template files if they don't exist."""
        templates_dir = self.base_dir / 'integration' / 'templates'
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index.html if it doesn't exist
        index_html_path = templates_dir / 'index.html'
        if not index_html_path.exists():
            # Basic HTML template with no emoji characters
            index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Avatar Platform</title>
    <style>
/* AI Avatar Platform Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #121212;
    color: #e0e0e0;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #333;
}

h1 {
    color: #6200EE;
}

button {
    background-color: #6200EE;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #7E3FF2;
}

button:disabled {
    background-color: #666;
    cursor: not-allowed;
}

main {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}

@media (min-width: 768px) {
    main {
        grid-template-columns: 1fr 1fr;
    }
}

.avatar-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.visual-display {
    background-color: #1E1E1E;
    border-radius: 8px;
    overflow: hidden;
    position: relative;
    aspect-ratio: 4/3;
}

.avatar-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: #666;
}

.display-controls {
    position: absolute;
    bottom: 10px;
    right: 10px;
    display: flex;
    gap: 10px;
}

.zoom-controls {
    display: flex;
    gap: 5px;
}

.action-panel {
    background-color: #1E1E1E;
    border-radius: 8px;
    padding: 15px;
}

.action-buttons {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 10px;
}

.interaction-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.chatbox {
    background-color: #1E1E1E;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    height: 300px;
}

.chat-messages {
    flex-grow: 1;
    overflow-y: auto;
    margin-bottom: 10px;
    padding: 5px;
}

.message {
    margin-bottom: 10px;
    padding: 8px 12px;
    border-radius: 8px;
    max-width: 80%;
}

.message.user {
    background-color: #6200EE;
    align-self: flex-end;
    margin-left: auto;
}

.message.avatar {
    background-color: #333;
    align-self: flex-start;
}

.message.system {
    background-color: #444;
    align-self: center;
    text-align: center;
    max-width: 100%;
}

.chat-input {
    display: flex;
    gap: 10px;
}

.chat-input input {
    flex-grow: 1;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #333;
    background-color: #2A2A2A;
    color: #e0e0e0;
}

.chat-options {
    margin-top: 10px;
    display: flex;
    justify-content: flex-end;
}

.upload-panel {
    background-color: #1E1E1E;
    border-radius: 8px;
    padding: 15px;
}

.upload-tabs {
    display: flex;
    gap: 5px;
    margin-bottom: 10px;
}

.tab-btn {
    background-color: #333;
    color: #e0e0e0;
    border: none;
    padding: 8px 16px;
    border-radius: 4px 4px 0 0;
    cursor: pointer;
}

.tab-btn.active {
    background-color: #6200EE;
}

.tab-pane {
    display: none;
    padding: 10px;
    background-color: #2A2A2A;
    border-radius: 0 4px 4px 4px;
}

.tab-pane.active {
    display: block;
}

.tab-pane p {
    margin-bottom: 10px;
}

.tab-pane input[type="file"] {
    margin-bottom: 10px;
    width: 100%;
}

footer {
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid #333;
    display: flex;
    justify-content: space-between;
}

.status-indicator {
    display: flex;
    gap: 5px;
    align-items: center;
}

#status-text {
    color: #999;
}

#status-text.connected {
    color: #03DAC6;
}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI Avatar Platform</h1>
            <button id="start-session-btn">Start Session</button>
        </header>
        
        <main>
            <div class="avatar-container">
                <div class="visual-display">
                    <div class="avatar-placeholder">
                        <p>Avatar will appear here</p>
                    </div>
                    <div class="display-controls">
                        <button class="view-toggle-btn">2D/3D</button>
                        <div class="zoom-controls">
                            <button class="zoom-in-btn">+</button>
                            <button class="zoom-out-btn">-</button>
                        </div>
                    </div>
                </div>
                
                <div class="action-panel">
                    <h3>Actions</h3>
                    <div class="action-buttons">
                        <button class="action-btn" data-action="wave">Wave</button>
                        <button class="action-btn" data-action="dance">Dance</button>
                        <button class="action-btn" data-action="jump">Jump</button>
                        <button class="action-btn" data-action="smile">Smile</button>
                        <button class="action-btn" data-action="wink">Wink</button>
                        <button class="action-btn" data-action="blowkiss">Blow Kiss</button>
                    </div>
                </div>
            </div>
            
            <div class="interaction-container">
                <div class="chatbox">
                    <div class="chat-messages" id="chat-messages">
                        <div class="message system">
                            <p>Welcome to the AI Avatar Platform! Start a session to begin.</p>
                        </div>
                    </div>
                    <div class="chat-input">
                        <input type="text" id="message-input" placeholder="Type your message..." disabled>
                        <button id="voice-input-btn" disabled>Mic</button>
                        <button id="send-btn" disabled>Send</button>
                    </div>
                    <div class="chat-options">
                        <label>
                            <input type="checkbox" id="stealth-mode"> Stealth Mode (Text Only)
                        </label>
                    </div>
                </div>
                
                <div class="upload-panel">
                    <h3>Upload Data</h3>
                    <div class="upload-tabs">
                        <button class="tab-btn active" data-tab="appearance">Appearance</button>
                        <button class="tab-btn" data-tab="voice">Voice</button>
                        <button class="tab-btn" data-tab="communication">Communication</button>
                    </div>
                    <div class="tab-content">
                        <div class="tab-pane active" id="appearance-tab">
                            <p>Upload LoRA model or image dataset (min. 10 images)</p>
                            <input type="file" id="appearance-upload" multiple>
                            <button class="upload-btn" data-type="appearance">Upload</button>
                        </div>
                        <div class="tab-pane" id="voice-tab">
                            <p>Upload audio samples (10-20 samples, min. 1 minute total)</p>
                            <input type="file" id="voice-upload" multiple>
                            <button class="upload-btn" data-type="voice">Upload</button>
                        </div>
                        <div class="tab-pane" id="communication-tab">
                            <p>Upload text dialog samples (min. 10 samples)</p>
                            <input type="file" id="communication-upload">
                            <button class="upload-btn" data-type="communication">Upload</button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
        
        <footer>
            <p>AI Avatar Platform - Prototype Version</p>
            <div class="status-indicator">
                <span>Status:</span>
                <span id="status-text">Not Connected</span>
            </div>
        </footer>
    </div>
    
    <script>
// AI Avatar Platform Main JavaScript

// DOM Elements
const startSessionBtn = document.getElementById('start-session-btn');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const voiceInputBtn = document.getElementById('voice-input-btn');
const sendBtn = document.getElementById('send-btn');
const stealthModeCheckbox = document.getElementById('stealth-mode');
const statusText = document.getElementById('status-text');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');
const actionBtns = document.querySelectorAll('.action-btn');
const uploadBtns = document.querySelectorAll('.upload-btn');

// State
let sessionActive = false;
let userId = 'user_' + Math.floor(Math.random() * 10000);
let availableModules = {
    appearance: false,
    voice: false,
    communication: false
};

// Initialize
function init() {
    // Add event listeners
    startSessionBtn.addEventListener('click', toggleSession);
    messageInput.addEventListener('keypress', handleKeyPress);
    sendBtn.addEventListener('click', sendMessage);
    voiceInputBtn.addEventListener('click', toggleVoiceInput);
    
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all tabs
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab') + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Action buttons
    actionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.getAttribute('data-action');
            triggerAction(action);
        });
    });
    
    // Upload buttons
    uploadBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const dataType = btn.getAttribute('data-type');
            uploadData(dataType);
        });
    });
    
    // Start checking for responses
    setInterval(checkResponses, 1000);
}

// Toggle session
async function toggleSession() {
    if (sessionActive) {
        // End session
        try {
            const response = await fetch('/api/session/end', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                sessionActive = false;
                startSessionBtn.textContent = 'Start Session';
                statusText.textContent = 'Not Connected';
                statusText.classList.remove('connected');
                
                // Disable input
                messageInput.disabled = true;
                voiceInputBtn.disabled = true;
                sendBtn.disabled = true;
                
                // Add system message
                addMessage('Session ended.', 'system');
            } else {
                console.error('Failed to end session:', data.message);
            }
        } catch (error) {
            console.error('Error ending session:', error);
        }
    } else {
        // Start session
        try {
            const response = await fetch('/api/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                sessionActive = true;
                startSessionBtn.textContent = 'End Session';
                statusText.textContent = 'Connected';
                statusText.classList.add('connected');
                
                // Enable input
                messageInput.disabled = false;
                voiceInputBtn.disabled = false;
                sendBtn.disabled = false;
                
                // Store available modules
                availableModules = data.available_modules || {
                    appearance: false,
                    voice: false,
                    communication: false
                };
                
                // Add system message
                let welcomeMessage = 'Session started.';
                
                if (Object.values(availableModules).some(v => v)) {
                    welcomeMessage += ' Available modules:';
                    if (availableModules.appearance) welcomeMessage += ' Appearance';
                    if (availableModules.voice) welcomeMessage += ' Voice';
                    if (availableModules.communication) welcomeMessage += ' Communication';
                } else {
                    welcomeMessage += ' No modules available. Please upload data or models.';
                }
                
                addMessage(welcomeMessage, 'system');
            } else {
                console.error('Failed to start session:', data.message);
            }
        } catch (error) {
            console.error('Error starting session:', error);
        }
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (message && sessionActive) {
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Send to server
        try {
            const response = await fetch('/api/input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    input: message,
                    stealth_mode: stealthModeCheckbox.checked
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                console.error('Failed to process input:', data.message);
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }
}

// Handle key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Toggle voice input
function toggleVoiceInput() {
    // This would be implemented in a production version
    alert('Voice input is not implemented in this prototype.');
}

// Trigger action
async function triggerAction(action) {
    if (sessionActive) {
        try {
            const response = await fetch('/api/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    action: action
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                addMessage(`Action triggered: ${action}`, 'system');
            } else {
                console.error('Failed to trigger action:', data.message);
                
                if (!availableModules.appearance) {
                    addMessage('Cannot trigger actions: Appearance module not available.', 'system');
                }
            }
        } catch (error) {
            console.error('Error triggering action:', error);
        }
    } else {
        addMessage('Please start a session first.', 'system');
    }
}

// Upload data
async function uploadData(dataType) {
    // Get file input element
    const fileInput = document.getElementById(`${dataType}-upload`);
    
    if (fileInput.files.length === 0) {
        addMessage(`Please select files for ${dataType} data.`, 'system');
        return;
    }
    
    // This would be implemented in a production version
    // For the prototype, we'll just show a message
    addMessage(`Uploading ${dataType} data: ${fileInput.files.length} file(s)...`, 'system');
    
    // Simulate upload delay
    setTimeout(() => {
        addMessage(`${dataType} data uploaded successfully!`, 'system');
    }, 2000);
}

// Check for responses
async function checkResponses() {
    if (sessionActive) {
        try {
            const response = await fetch(`/api/responses?user_id=${userId}&clear=true`);
            const data = await response.json();
            
            if (data.success && data.responses && data.responses.length > 0) {
                data.responses.forEach(resp => {
                    if (resp.text) {
                        addMessage(resp.text, 'avatar');
                    }
                    
                    if (resp.action) {
                        // In a production version, this would trigger a visual action
                        console.log('Avatar action:', resp.action);
                    }
                    
                    if (resp.audio) {
                        // In a production version, this would play audio
                        console.log('Avatar audio:', resp.audio);
                    }
                });
            }
        } catch (error) {
            console.error('Error checking responses:', error);
        }
    }
}

// Add message to chat
function addMessage(text, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);
    
    const textElement = document.createElement('p');
    textElement.textContent = text;
    
    messageElement.appendChild(textElement);
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>"""
            
            # Write the file with UTF-8 encoding explicitly
            with open(index_html_path, 'w', encoding='utf-8') as f:
                f.write(index_html)
    
    def run(self):
        """Run the web server."""
        # Create template files
        self.create_template_files()
        
        # Run Flask app
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

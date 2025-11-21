from flask import Flask, request, jsonify
from flask_cors import CORS
from aria_core import AriaCore
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron

# Initialize Aria Core
aria = None
voice_mode_active = False
voice_thread = None

def init_aria():
    global aria
    aria = AriaCore(on_speak=None)  # We'll handle speech separately
    print("Aria backend initialized")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Aria backend is running'})

@app.route('/message', methods=['POST'])
def process_message():
    """Process text message from user"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process command through Aria
        # Capture the response by temporarily storing it
        responses = []
        
        def capture_response(text):
            responses.append(text)
        
        # Temporarily override the speak callback
        original_callback = aria.on_speak
        aria.on_speak = capture_response
        
        # Process the command
        aria.process_command(message)
        
        # Restore original callback
        aria.on_speak = original_callback
        
        # Get the response
        response_text = responses[0] if responses else "I'm processing your request."
        
        return jsonify({
            'status': 'success',
            'response': response_text
        })
    
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/voice/start', methods=['POST'])
def start_voice_mode():
    """Start voice listening mode"""
    global voice_mode_active, voice_thread
    
    try:
        voice_mode_active = True
        
        return jsonify({
            'status': 'success',
            'message': 'Voice mode started'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/voice/listen', methods=['GET'])
def listen_for_voice():
    """Listen for voice input"""
    try:
        if not voice_mode_active:
            return jsonify({
                'status': 'inactive',
                'text': None
            })
        
        # Listen for voice input
        text = aria.listen()
        
        if text and aria.wake_word in text.lower():
            return jsonify({
                'status': 'success',
                'text': text
            })
        
        return jsonify({
            'status': 'waiting',
            'text': None
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/voice/stop', methods=['POST'])
def stop_voice_mode():
    """Stop voice listening mode"""
    global voice_mode_active
    
    try:
        voice_mode_active = False
        
        return jsonify({
            'status': 'success',
            'message': 'Voice mode stopped'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def run_server():
    """Run the Flask server"""
    print("Starting Aria backend server on http://localhost:5000")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Initialize Aria
    init_aria()
    
    # Run server
    run_server()

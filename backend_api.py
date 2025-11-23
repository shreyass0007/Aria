from flask import Flask, request, jsonify
from flask_cors import CORS
from aria_core import AriaCore
from conversation_manager import ConversationManager
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron

# Initialize Aria Core
aria = None
voice_mode_active = False
voice_thread = None
conversation_mgr = None

def init_aria():
    global aria, conversation_mgr
    aria = AriaCore(on_speak=None)  # We'll handle speech separately
    conversation_mgr = ConversationManager()
    
    # Create initial conversation if MongoDB is connected
    if conversation_mgr.is_connected():
        conversation_mgr.create_conversation()
    
    print("Aria backend initialized")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Aria backend is running'})

@app.route('/greeting', methods=['GET'])
def greeting():
    if aria:
        greeting_text = aria.get_time_based_greeting()
        return jsonify({"greeting": greeting_text})
    return jsonify({"greeting": "Hello, I am Aria."})

@app.route('/message', methods=['POST'])
def process_message():
    """Process text message from user"""
    try:
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Use provided conversation_id or current one
        if conversation_id:
            conversation_mgr.set_current_conversation_id(conversation_id)
        else:
            # Create new conversation if none exists
            if not conversation_mgr.get_current_conversation_id():
                if conversation_mgr.is_connected():
                    conversation_mgr.create_conversation()
            conversation_id = conversation_mgr.get_current_conversation_id()
        
        # Save user message
        if conversation_mgr.is_connected() and conversation_id:
            conversation_mgr.add_message(conversation_id, 'user', message)
        
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
        # Join all responses with newlines to ensure the user sees everything
        response_text = "\n\n".join(responses) if responses else "I'm processing your request."
        
        # Save assistant message
        if conversation_mgr.is_connected() and conversation_id:
            conversation_mgr.add_message(conversation_id, 'assistant', response_text)
        
        return jsonify({
            'status': 'success',
            'response': response_text,
            'conversation_id': conversation_id
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



@app.route('/settings/tts', methods=['GET'])
def get_tts_status():
    """Get current TTS status"""
    try:
        return jsonify({
            'status': 'success',
            'enabled': aria.tts_enabled
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/settings/tts', methods=['POST'])
def set_tts_status():
    """Set TTS status"""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        aria.set_tts_enabled(enabled)
        return jsonify({
            'status': 'success',
            'enabled': aria.tts_enabled
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/conversations', methods=['GET'])
def get_conversations():
    """Get list of all conversations"""
    try:
        limit = int(request.args.get('limit', 20))
        conversations = conversation_mgr.list_conversations(limit=limit)
        return jsonify({
            'status': 'success',
            'conversations': conversations
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get specific conversation with all messages"""
    try:
        conversation = conversation_mgr.get_conversation(conversation_id)
        if conversation:
            return jsonify({
                'status': 'success',
                'conversation': conversation
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Conversation not found'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/conversation/new', methods=['POST'])
def create_new_conversation():
    """Create a new conversation"""
    try:
        conversation_id = conversation_mgr.create_conversation()
        if conversation_id:
            return jsonify({
                'status': 'success',
                'conversation_id': conversation_id
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to create conversation'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        success = conversation_mgr.delete_conversation(conversation_id)
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Conversation deleted'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to delete conversation'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/notion/summarize', methods=['POST'])
def summarize_notion_page():
    """Summarize a Notion page"""
    try:
        data = request.json
        page_id = data.get('page_id')
        page_url = data.get('page_url')
        page_title = data.get('page_title')
        command = data.get('command', '')
        
        # Extract page ID if not directly provided
        if not page_id:
            if page_url:
                # Extract ID from URL
                import re
                # Match various Notion URL formats
                match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', page_url)
                if match:
                    page_id = match.group(1).replace('-', '')
            elif page_title or command:
                # Search for page by title
                search_query = page_title or command
                try:
                    search_results = aria.notion.client.search(
                        query=search_query,
                        filter={"property": "object", "value": "page"},
                        page_size=1
                    ).get("results", [])
                    
                    if search_results:
                        page_id = search_results[0]["id"]
                    else:
                        return jsonify({
                            'status': 'error',
                            'error': f'No page found matching "{search_query}"'
                        }), 404
                except Exception as e:
                    return jsonify({
                        'status': 'error',
                        'error': f'Error searching Notion: {str(e)}'
                    }), 500
        
        if not page_id:
            return jsonify({
                'status': 'error',
                'error': 'Please provide a page_id, page_url, page_title, or command'
            }), 400
        
        # Fetch page content
        page_data = aria.notion.get_page_content(page_id)
        
        if page_data.get('status') == 'error':
            return jsonify({
                'status': 'error',
                'error': page_data.get('error', 'Failed to fetch page content')
            }), 500
        
        # Summarize the content
        content = page_data.get('content', '')
        summary = aria.brain.summarize_text(content, max_sentences=5)
        
        return jsonify({
            'status': 'success',
            'summary': summary,
            'page_title': page_data.get('title', 'Untitled'),
            'word_count': page_data.get('word_count', 0)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/conversation/<conversation_id>/rename', methods=['PUT'])
def rename_conversation(conversation_id):
    """Rename a conversation"""
    try:
        data = request.get_json()
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return jsonify({
                'status': 'error',
                'error': 'Title is required'
            }), 400
        
        success = conversation_mgr.rename_conversation(conversation_id, new_title)
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Conversation renamed'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to rename conversation'
            }), 500
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

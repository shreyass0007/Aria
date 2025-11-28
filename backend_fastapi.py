import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
import asyncio
import platform

# Fix for "ConnectionResetError: [WinError 10054]" on Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add project root to path if needed
# Add project root to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aria_core import AriaCore
from conversation_manager import ConversationManager

# Initialize Aria Core
aria = None
voice_mode_active = False
conversation_mgr = None

def init_aria():
    global aria, conversation_mgr
    aria = AriaCore(on_speak=None)  # We'll handle speech separately
    conversation_mgr = ConversationManager()
    
    # Create initial conversation if MongoDB is connected
    if conversation_mgr.is_connected():
        conversation_mgr.create_conversation()
    
    print("Aria backend initialized")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_aria()
    yield
    # Shutdown logic if needed

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Electron
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Aria backend is running"}

@app.get("/greeting")
def greeting():
    if aria:
        greeting_text = aria.get_time_based_greeting()
        return {"greeting": greeting_text}
    return {"greeting": "Hello, I am Aria."}

# Model management endpoints
current_model = "gpt-4o"  # Default model

@app.get("/models/available")
def get_available_models():
    """Get list of available AI models"""
    try:
        if aria and aria.brain:
            models = aria.brain.get_available_models()
            return {
                "status": "success",
                "models": models,
                "count": len(models)
            }
        return {"status": "error", "models": [], "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/current")
def get_current_model():
    """Get the currently selected model"""
    try:
        return {
            "status": "success",
            "model": current_model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ModelSetRequest(BaseModel):
    model: str

@app.post("/models/set")
def set_current_model(request: ModelSetRequest):
    """Set the current model for conversations"""
    global current_model
    try:
        # Validate that model is available
        if aria and aria.brain:
            available_models = aria.brain.get_available_models()
            model_ids = [m["id"] for m in available_models]
            
            if request.model not in model_ids:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Model {request.model} is not available. Available models: {', '.join(model_ids)}"
                )
            
            current_model = request.model
            return {
                "status": "success",
                "model": current_model,
                "message": f"Model set to {current_model}"
            }
        
        raise HTTPException(status_code=500, detail="Brain not initialized")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: Optional[str] = "gpt-4o"

@app.post("/message")
def process_message(request: MessageRequest):
    try:
        message = request.message
        conversation_id = request.conversation_id
        model = request.model
        
        if not message:
            raise HTTPException(status_code=400, detail="No message provided")
        
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
        responses = []
        
        def capture_response(text):
            responses.append(text)
        
        # Temporarily override the speak callback
        original_callback = aria.on_speak
        aria.on_speak = capture_response
        
        # Process the command
        aria.process_command(message, model_name=model)
        
        # Restore original callback
        aria.on_speak = original_callback
        
        # Get the response
        response_text = "\n\n".join(responses) if responses else "I'm processing your request."
        
        # Check for UI action
        ui_action = None
        if aria.last_ui_action:
            ui_action = aria.last_ui_action
            aria.last_ui_action = None # Clear it
        
        # Save assistant message
        if conversation_mgr.is_connected() and conversation_id:
            conversation_mgr.add_message(conversation_id, 'assistant', response_text)
        
        return {
            'status': 'success',
            'response': response_text,
            'conversation_id': conversation_id,
            'ui_action': ui_action
        }
    
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/start")
def start_voice_mode():
    global voice_mode_active
    try:
        voice_mode_active = True
        return {'status': 'success', 'message': 'Voice mode started'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/listen")
def listen_for_voice():
    try:
        if not voice_mode_active:
            return {'status': 'inactive', 'text': None}
        
        # Listen for voice input
        text = aria.listen()
        
        if text and aria.wake_word in text.lower():
            return {'status': 'success', 'text': text}
        
        return {'status': 'waiting', 'text': None}
    except Exception as e:
        return JSONResponse(status_code=500, content={'status': 'error', 'error': str(e)})

@app.post("/voice/stop")
def stop_voice_mode():
    global voice_mode_active
    try:
        voice_mode_active = False
        return {'status': 'success', 'message': 'Voice mode stopped'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings/tts")
def get_tts_status():
    try:
        return {'status': 'success', 'enabled': aria.tts_enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TTSRequest(BaseModel):
    enabled: bool = True

@app.post("/settings/tts")
def set_tts_status(request: TTSRequest):
    try:
        aria.set_tts_enabled(request.enabled)
        return {'status': 'success', 'enabled': aria.tts_enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Email Management Endpoints
class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/email/send")
def send_email(request: EmailSendRequest):
    """Send an email via Gmail"""
    try:
        # Check if email manager is available
        if not hasattr(aria, 'email') or aria.email is None:
            raise HTTPException(
                status_code=503, 
                detail="Email functionality not configured. Please set up Gmail credentials."
            )
        
        # Validate email fields
        if not request.to or not request.subject or not request.body:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Send email through aria's email manager
        result = aria.email.send_email(request.to, request.subject, request.body)
        
        if "successfully" in result.lower():
            return {
                'status': 'success',
                'message': result
            }
        else:
            return {
                'status': 'error',
                'error': result
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
def get_conversations(limit: int = 20):
    try:
        conversations = conversation_mgr.list_conversations(limit=limit)
        return {'status': 'success', 'conversations': conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    try:
        conversation = conversation_mgr.get_conversation(conversation_id)
        if conversation:
            return {'status': 'success', 'conversation': conversation}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        if "not found" in str(e).lower():
             raise HTTPException(status_code=404, detail="Conversation not found")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation/new")
def create_new_conversation():
    try:
        conversation_id = conversation_mgr.create_conversation()
        if conversation_id:
            return {'status': 'success', 'conversation_id': conversation_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversation/{conversation_id}")
def delete_conversation(conversation_id: str):
    try:
        success = conversation_mgr.delete_conversation(conversation_id)
        if success:
            return {'status': 'success', 'message': 'Conversation deleted'}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RenameRequest(BaseModel):
    title: str

@app.put("/conversation/{conversation_id}/rename")
def rename_conversation(conversation_id: str, request: RenameRequest):
    try:
        new_title = request.title.strip()
        if not new_title:
            raise HTTPException(status_code=400, detail="Title is required")
        
        success = conversation_mgr.rename_conversation(conversation_id, new_title)
        if success:
            return {'status': 'success', 'message': 'Conversation renamed'}
        else:
            raise HTTPException(status_code=500, detail="Failed to rename conversation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Feature Status Endpoints for Modular System
@app.get("/features/status")
def get_all_features_status():
    """Check availability of all optional features"""
    try:
        return {
            "status": "success",
            "features": {
                "email": check_email_available(),
                "calendar": check_calendar_available(),
                "notion": check_notion_available(),
                "weather": check_weather_available(),
                "systemMonitor": check_system_monitor_available(),
                "fileManager": True,  # Always available
                "clipboardManager": True  # Always available
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "features": {}}

@app.get("/features/{feature_name}/status")
def get_feature_status(feature_name: str):
    """Check if a specific feature is available"""
    try:
        feature_checks = {
            "email": check_email_available,
            "calendar": check_calendar_available,
            "notion": check_notion_available,
            "weather": check_weather_available,
            "systemMonitor": check_system_monitor_available,
            "fileManager": lambda: True,
            "clipboardManager": lambda: True
        }
        
        if feature_name not in feature_checks:
            raise HTTPException(status_code=404, detail=f"Unknown feature: {feature_name}")
        
        available = feature_checks[feature_name]()
        return {
            "status": "success",
            "feature": feature_name,
            "available": available
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "available": False, "error": str(e)}

def check_email_available():
    """Check if email functionality is configured"""
    try:
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            return False
        # Try importing email manager
        from email_manager import EmailManager
        return True
    except:
        return False

def check_calendar_available():
    """Check if calendar functionality is configured"""
    try:
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            return False
        # Try importing calendar manager
        from calendar_manager import CalendarManager
        return True
    except:
        return False

def check_notion_available():
    """Check if Notion functionality is configured"""
    try:
        # Check if Notion API key is set
        notion_key = os.getenv('NOTION_API_KEY')
        if not notion_key:
            return False
        # Try importing notion manager
        from notion_manager import NotionManager
        return True
    except:
        return False

def check_weather_available():
    """Check if weather functionality is configured"""
    try:
        # Check if weather API key is set
        weather_key = os.getenv('OPENWEATHER_API_KEY')
        if not weather_key:
            return False
        # Try importing weather manager
        from weather_manager import WeatherManager
        return True
    except:
        return False

def check_system_monitor_available():
    """Check if system monitoring is available"""
    try:
        from system_monitor import SystemMonitor
        return True
    except:
        return False

class SummarizeRequest(BaseModel):
    page_id: Optional[str] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    command: Optional[str] = None

@app.post("/notion/summarize")
def summarize_notion_page(request: SummarizeRequest):
    try:
        page_id = request.page_id
        page_url = request.page_url
        page_title = request.page_title
        command = request.command
        
        # Extract page ID if not directly provided
        if not page_id:
            if page_url:
                import re
                match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', page_url)
                if match:
                    page_id = match.group(1).replace('-', '')
            elif page_title or command:
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
                        raise HTTPException(status_code=404, detail=f'No page found matching "{search_query}"')
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f'Error searching Notion: {str(e)}')
        
        if not page_id:
            raise HTTPException(status_code=400, detail='Please provide a page_id, page_url, page_title, or command')
        
        # Fetch page content
        page_data = aria.notion.get_page_content(page_id)
        
        if page_data.get('status') == 'error':
            raise HTTPException(status_code=500, detail=page_data.get('error', 'Failed to fetch page content'))
        
        # Summarize the content
        content = page_data.get('content', '')
        summary = aria.brain.summarize_text(content, max_sentences=5)
        
        return {
            'status': 'success',
            'summary': summary,
            'page_title': page_data.get('title', 'Untitled'),
            'word_count': page_data.get('word_count', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_server():
    """Run the FastAPI server using Uvicorn"""
    print("Starting Aria backend server on http://localhost:5000")
    uvicorn.run(app, host="localhost", port=5000, log_level="info")

if __name__ == "__main__":
    run_server()

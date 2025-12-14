from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_aria_core, get_conversation_mgr, get_memory_mgr
from aria.aria_core import AriaCore
from aria.conversation_manager import ConversationManager
from aria.memory_manager import MemoryManager

router = APIRouter()

# Models
class MessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: Optional[str] = "gpt-4o-mini"
    extra_data: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    status: str = "success"
    response: str
    conversation_id: str
    audio_url: Optional[str] = None
    action_result: Optional[Any] = None
    ui_action: Optional[Dict[str, Any]] = None



@router.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    aria: AriaCore = Depends(get_aria_core),
    conversation_mgr: ConversationManager = Depends(get_conversation_mgr),
    memory_mgr: MemoryManager = Depends(get_memory_mgr)
):
    try:
        message = request.message
        conversation_id = request.conversation_id
        
        if not message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # 1. Manage Conversation ID
        if conversation_id:
            conversation_mgr.set_current_conversation_id(conversation_id)
        else:
            if not conversation_mgr.get_current_conversation_id():
                if conversation_mgr.is_connected():
                    conversation_mgr.create_conversation()
            conversation_id = conversation_mgr.get_current_conversation_id()
        
        # 2. Retrieve History
        conversation_history = []
        if conversation_mgr.is_connected() and conversation_id:
            conversation_data = conversation_mgr.get_conversation(conversation_id)
            if conversation_data and 'messages' in conversation_data:
                recent_messages = conversation_data['messages'][-25:]
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in recent_messages
                ]
        
        # 3. Retrieve Long-term Memory (RAG)
        long_term_context = []
        if memory_mgr and memory_mgr.is_available():
            long_term_context = memory_mgr.search_relevant_context(
                query=message,
                top_k=5,
                exclude_conversation=conversation_id
            )
        
        # 4. Save User Message
        if conversation_mgr.is_connected() and conversation_id:
            conversation_mgr.add_message(conversation_id, 'user', message)
            
        if memory_mgr and memory_mgr.is_available() and conversation_id:
            memory_mgr.add_message(conversation_id, message, 'user')
        
        # 5. Intent Classification & Processing
        # Check for pending email confirmation first
        if aria.command_processor.pending_email:
            intent_data = {"intent": "email_confirmation", "confidence": 1.0, "parameters": {}}
        elif message.lower().strip() == "aria":
            intent_data = {"intent": "wake_word", "confidence": 1.0, "parameters": {}}
        else:
            intent_data = aria.command_classifier.classify_intent(message, conversation_history)
            
        if isinstance(intent_data, list):
            intent = intent_data[0].get("intent") if intent_data else "none"
        else:
            intent = intent_data.get("intent")
            
        print(f"DEBUG: Router classified as: {intent}")
        
        # 6. Execute Command
        response_text = aria.command_processor.process_command(
            text=message, 
            model_name=request.model,
            intent_data=intent_data, 
            conversation_history=conversation_history,
            long_term_memory=long_term_context
        )
        
        if not response_text:
            response_text = "I'm sorry, I couldn't process that command."
        
        # 7. Save Assistant Response
        if conversation_mgr.is_connected() and conversation_id:
            conversation_mgr.add_message(conversation_id, 'assistant', response_text)
            
        if memory_mgr and memory_mgr.is_available() and conversation_id:
            memory_mgr.add_message(conversation_id, response_text, 'assistant')
            
        # 8. Get UI Action if any
        ui_action = aria.command_processor.last_ui_action
        if ui_action:
            aria.command_processor.last_ui_action = None # Clear it
            
        return MessageResponse(
            response=response_text,
            conversation_id=conversation_id or "default",
            action_result=intent_data,
            ui_action=ui_action
        )

    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/available")
def get_available_models(aria: AriaCore = Depends(get_aria_core)):
    """Returns a list of available LLM models."""
    try:
        models = aria.brain.get_available_models()
        return {
            "status": "success",
            "models": models
        }
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {
            "status": "error", 
            "models": []
        }

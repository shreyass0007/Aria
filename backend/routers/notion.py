from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dependencies import get_aria_core
from aria.aria_core import AriaCore

router = APIRouter()

class NotionSummaryRequest(BaseModel):
    page_id: str

@router.post("/notion/summarize")
def summarize_notion_page(request: NotionSummaryRequest, aria: AriaCore = Depends(get_aria_core)):
    try:
        # 1. Fetch Content
        page_data = aria.notion.get_page_content(request.page_id)
        
        if page_data["status"] == "error":
            raise HTTPException(status_code=404, detail=page_data["error"])
            
        content = page_data["content"]
        title = page_data["title"]
        
        # 2. Summarize using Brain
        summary = aria.brain.summarize_text(content)
        
        return {
            "title": title,
            "summary": summary,
            "original_length": page_data["word_count"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

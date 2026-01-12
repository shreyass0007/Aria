
import pytest
from unittest.mock import patch, MagicMock
from aria.brains.planner_brain import PlannerBrain

@pytest.mark.asyncio
async def test_planner_brain_generation():
    with patch('aria.brains.planner_brain.ollama.chat') as mock_chat:
        # Mock successful response
        mock_chat.return_value = {
            'message': {
                'content': '{"actions": [{"action": "open_app", "params": {"name": "notepad"}}]}'
            }
        }
        
        planner = PlannerBrain()
        plan = await planner.generate_plan("Open Notepad")
        
        assert "actions" in plan
        assert len(plan["actions"]) == 1
        assert plan["actions"][0]["action"] == "open_app"

@pytest.mark.asyncio
async def test_planner_brain_invalid_json():
    with patch('aria.brains.planner_brain.ollama.chat') as mock_chat:
        # Mock valid JSON but invalid schema or garbage
        mock_chat.return_value = {
            'message': {
                'content': 'NOT JSON'
            }
        }
        
        planner = PlannerBrain()
        plan = await planner.generate_plan("Open Notepad")
        
        assert "actions" in plan
        assert len(plan["actions"]) == 0
        assert "error" in plan

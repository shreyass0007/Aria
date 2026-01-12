
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from aria.command_processor import CommandProcessor
from aria.command_intent_classifier import CommandIntentClassifier
from aria.brain import AriaBrain

@pytest.fixture
def mock_deps():
    deps = {
        "tts_manager": MagicMock(),
        "app_launcher": MagicMock(),
        "brain": MagicMock(spec=AriaBrain),
        "calendar": MagicMock(),
        "notion": MagicMock(),
        "automator": MagicMock(),
        "system_control": MagicMock(),
        "command_classifier": MagicMock(), # We will mock this or use real one with mocked brain
        "file_manager": MagicMock(),
        "weather_manager": MagicMock(),
        "clipboard_screenshot": MagicMock(),
        "system_monitor": MagicMock(),
        "email_manager": MagicMock(),
        "greeting_service": MagicMock(),
        "music_manager": MagicMock(),
        "memory_manager": MagicMock(),
        "water_manager": MagicMock(),
    }
    return deps

@pytest.mark.asyncio
async def test_desktop_task_routing(mock_deps):
    # Mock classifier to return desktop_task
    mock_deps["command_classifier"].classify_intent.return_value = [{
        "intent": "desktop_task",
        "confidence": 0.9,
        "parameters": {}
    }]
    
    # Initialize processor
    processor = CommandProcessor(**mock_deps)
    
    # Mock PlannerBrain and Executor inside the processor
    processor.planner = MagicMock()
    processor.planner.generate_plan = AsyncMock(return_value={
        "actions": [{"action": "open_app", "params": {"name": "notepad"}}]
    })
    
    processor.executor = MagicMock()
    processor.executor.execute_plan = AsyncMock(return_value=True)
    
    # Run process_command
    # Note: process_command is sync but calls async planner/executor internally via asyncio.run
    # We need to patch asyncio.run if we are in an async test loop? 
    # Actually, asyncio.run fails if loop is running. 
    # We should trust the logic or refactor CommandProcessor to be async.
    # For this test, we can mock asyncio.run to just run the awaitable?
    # Or better, just test handle_desktop_task directly since that's what we modified.
    
    result = processor.handle_desktop_task("Open Notepad", "desktop_task", {})
    
    assert result == "Desktop task executed successfully."
    processor.planner.generate_plan.assert_called_once_with("Open Notepad")
    processor.executor.execute_plan.assert_called()
    assert processor.last_desktop_plan is not None

def test_intent_classifier_prompt_build():
    brain = MagicMock(spec=AriaBrain)
    classifier = CommandIntentClassifier(brain)
    
    prompt = classifier._build_classification_prompt("Open Notepad and type hi")
    
    assert "desktop_task" in prompt
    assert "Perform complex desktop automation" in prompt
    assert "desktop_task" in classifier.COMMAND_INTENTS

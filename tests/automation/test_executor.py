
import pytest
from unittest.mock import MagicMock, patch
from aria.executor.desktop_executor import DesktopExecutor

@pytest.mark.asyncio
async def test_executor_flow():
    with patch('aria.executor.desktop_executor.WindowsAdapter') as MockAdapter:
        # Setup mock
        mock_adapter_instance = MockAdapter.return_value
        mock_adapter_instance.open_app.return_value = True
        mock_adapter_instance.type_text.return_value = True
        
        executor = DesktopExecutor()
        # Force windows for test consistency if running on other OS (though user is on windows)
        executor.os_type = "Windows" 
        executor.adapter = mock_adapter_instance

        plan = {
            "actions": [
                {"action": "open_app", "params": {"name": "notepad"}},
                {"action": "type", "params": {"text": "test"}}
            ]
        }
        
        success = await executor.execute_plan(plan)
        
        assert success == True
        mock_adapter_instance.open_app.assert_called_with("notepad")
        mock_adapter_instance.type_text.assert_called_with("test")

@pytest.mark.asyncio
async def test_executor_failure():
    with patch('aria.executor.desktop_executor.WindowsAdapter') as MockAdapter:
        mock_adapter_instance = MockAdapter.return_value
        mock_adapter_instance.open_app.return_value = False # Simulate failure
        
        executor = DesktopExecutor()
        executor.adapter = mock_adapter_instance
        
        plan = {
            "actions": [
                {"action": "open_app", "params": {"name": "notepad"}}
            ]
        }
        
        success = await executor.execute_plan(plan)
        assert success == False

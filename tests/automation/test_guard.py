
import pytest
from aria.safety.action_guard import ActionGuard

def test_action_guard_valid_plan():
    guard = ActionGuard()
    plan = {
        "actions": [
            {"action": "open_app", "params": {"name": "notepad"}},
            {"action": "type", "params": {"text": "hello"}}
        ]
    }
    result = guard.validate_plan(plan)
    assert result["valid"] == True

def test_action_guard_blocked_action():
    guard = ActionGuard()
    plan = {
        "actions": [
            {"action": "delete_file", "params": {"path": "c:/windows"}}
        ]
    }
    result = guard.validate_plan(plan)
    assert result["valid"] == False
    assert "blocked" in result["reason"]

def test_action_guard_unknown_action():
    guard = ActionGuard()
    plan = {
        "actions": [
            {"action": "dance", "params": {}}
        ]
    }
    result = guard.validate_plan(plan)
    assert result["valid"] == False
    assert "whitelist" in result["reason"]

def test_action_guard_too_many_actions():
    guard = ActionGuard()
    actions = [{"action": "wait", "params": {"seconds": 1}}] * 11
    plan = {"actions": actions}
    result = guard.validate_plan(plan)
    assert result["valid"] == False
    assert "exceeds" in result["reason"]


class ActionGuard:
    """
    Safety gate to validate reliability and safety of automation plans.
    """
    ALLOWED_ACTIONS = {
        "open_app",
        "close_app",
        "type",
        "press",
        "wait",
        "click",
        "read_screen",
        "click_text",
        "wait_for_text",
        "get_active_window",
        "focus_window" 
    }

    BLOCKED_ACTIONS = {
        "delete_file",
        "run_shell",
        "download",
        "network_request",
        "registry_edit",
        "install_software",
        "modify_system_settings"
    }

    MAX_ACTIONS_PER_PLAN = 10

    def __init__(self):
        pass

    def validate_plan(self, plan: dict) -> dict:
        """
        Validates a plan against whitelist, blacklist, and safety rules.
        Returns a dict with {"valid": bool, "reason": str}.
        """
        if not isinstance(plan, dict) or "actions" not in plan:
            return {"valid": False, "reason": "Invalid plan format: missing 'actions' key"}

        actions = plan.get("actions", [])
        if not isinstance(actions, list):
            return {"valid": False, "reason": "Invalid plan format: 'actions' must be a list"}

        if len(actions) > self.MAX_ACTIONS_PER_PLAN:
            return {"valid": False, "reason": f"Plan exceeds maximum allowed actions ({self.MAX_ACTIONS_PER_PLAN})"}

        for i, action in enumerate(actions):
            action_name = action.get("action")
            if not action_name:
                return {"valid": False, "reason": f"Action at index {i} missing 'action' name"}

            if action_name in self.BLOCKED_ACTIONS:
                return {"valid": False, "reason": f"Action '{action_name}' is explicitly blocked"}

            if action_name not in self.ALLOWED_ACTIONS:
                return {"valid": False, "reason": f"Action '{action_name}' is not in the allowed whitelist"}

            # Basic parameter validation could go here
            if "params" not in action:
                return {"valid": False, "reason": f"Action '{action_name}' missing 'params'"}

        return {"valid": True, "reason": "Plan is safe"}

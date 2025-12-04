"""
Comprehensive Backend FastAPI Verification Test
Tests all endpoints and functionality in backend_fastapi.py
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

class BackendTester:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "skipped": []
        }
        self.test_conversation_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "PASS": "\033[92m",    # Green
            "FAIL": "\033[91m",    # Red
            "WARN": "\033[93m",    # Yellow
            "ENDC": "\033[0m"      # Reset
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{level}] {message}{colors['ENDC']}")
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     expected_status: int = 200, data: Dict = None,
                     check_fields: List[str] = None) -> bool:
        """Generic endpoint tester"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            if response.status_code != expected_status:
                self.log(f"✗ {name}: Expected status {expected_status}, got {response.status_code}", "FAIL")
                self.log(f"  Response: {response.text[:200]}", "FAIL")
                self.results["failed"].append(name)
                return False
            
            # Parse JSON
            try:
                response_data = response.json()
            except:
                if expected_status == 200:
                    self.log(f"✗ {name}: Could not parse JSON response", "FAIL")
                    self.results["failed"].append(name)
                    return False
                response_data = {}
            
            # Check required fields
            if check_fields:
                for field in check_fields:
                    if field not in response_data:
                        self.log(f"✗ {name}: Missing field '{field}' in response", "FAIL")
                        self.results["failed"].append(name)
                        return False
            
            self.log(f"✓ {name}", "PASS")
            self.results["passed"].append(name)
            return response_data
            
        except requests.exceptions.ConnectionError:
            self.log(f"✗ {name}: Could not connect to backend (is it running?)", "FAIL")
            self.results["failed"].append(name)
            return False
        except Exception as e:
            self.log(f"✗ {name}: {str(e)}", "FAIL")
            self.results["failed"].append(name)
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("=" * 60, "INFO")
        self.log("BACKEND FASTAPI COMPREHENSIVE TEST SUITE", "INFO")
        self.log("=" * 60, "INFO")
        
        # TEST 1: HEALTH CHECK
        self.log("\n1. Testing Health Check Endpoint", "INFO")
        self.test_endpoint(
            "Health Check",
            "GET",
            "/health",
            check_fields=["status", "message"]
        )
        
        # TEST 2: GREETING
        self.log("\n2. Testing Greeting Endpoint", "INFO")
        self.test_endpoint(
            "Greeting",
            "GET",
            "/greeting",
            check_fields=["greeting"]
        )
        
        # TEST 3: MODEL MANAGEMENT
        self.log("\n3. Testing Model Management", "INFO")
        
        # Get available models
        models_response = self.test_endpoint(
            "Get Available Models",
            "GET",
            "/models/available",
            check_fields=["status", "models"]
        )
        
        # Get current model
        self.test_endpoint(
            "Get Current Model",
            "GET",
            "/models/current",
            check_fields=["status", "model"]
        )
        
        # Set model (if models available)
        if models_response and "models" in models_response:
            if models_response["models"]:
                test_model = models_response["models"][0]["id"]
                self.test_endpoint(
                    "Set Model",
                    "POST",
                    "/models/set",
                    data={"model": test_model},
                    check_fields=["status", "model"]
                )
        
        # TEST 4: CONVERSATION MANAGEMENT
        self.log("\n4. Testing Conversation Management", "INFO")
        
        # Create new conversation
        new_conv = self.test_endpoint(
            "Create New Conversation",
            "POST",
            "/conversation/new",
            check_fields=["status", "conversation_id"]
        )
        
        if new_conv:
            self.test_conversation_id = new_conv.get("conversation_id")
            self.log(f"  Test Conversation ID: {self.test_conversation_id}", "INFO")
        
        # List conversations
        self.test_endpoint(
            "List Conversations",
            "GET",
            "/conversations",
            check_fields=["status", "conversations"]
        )
        
        # Get specific conversation (if we have an ID)
        if self.test_conversation_id:
            self.test_endpoint(
                "Get Specific Conversation",
                "GET",
                f"/conversation/{self.test_conversation_id}",
                check_fields=["status", "conversation"]
            )
            
            # Rename conversation
            self.test_endpoint(
                "Rename Conversation",
                "PUT",
                f"/conversation/{self.test_conversation_id}/rename",
                data={"title": "Test Conversation - Backend Verification"},
                check_fields=["status"]
            )
        
        # TEST 5: MESSAGE PROCESSING
        self.log("\n5. Testing Message Processing", "INFO")
        
        message_data = {
            "message": "Hello Aria, this is a test message",
            "conversation_id": self.test_conversation_id,
            "model": "gpt-4o"
        }
        
        msg_response = self.test_endpoint(
            "Process Message",
            "POST",
            "/message",
            data=message_data,
            check_fields=["status", "response", "conversation_id"]
        )
        
        if msg_response:
            self.log(f"  Response Preview: {msg_response.get('response', '')[:100]}...", "INFO")
        
        # TEST 6: TTS SETTINGS
        self.log("\n6. Testing TTS Settings", "INFO")
        
        self.test_endpoint(
            "Get TTS Status",
            "GET",
            "/settings/tts",
            check_fields=["status", "enabled"]
        )
        
        self.test_endpoint(
            "Set TTS Enabled",
            "POST",
            "/settings/tts",
            data={"enabled": True},
            check_fields=["status", "enabled"]
        )
        
        # TEST 7: VOICE MODE
        self.log("\n7. Testing Voice Mode", "INFO")
        
        self.test_endpoint(
            "Start Voice Mode",
            "POST",
            "/voice/start",
            check_fields=["status"]
        )
        
        self.test_endpoint(
            "Stop Voice Mode",
            "POST",
            "/voice/stop",
            check_fields=["status"]
        )
        
        # TEST 8: FEATURE STATUS
        self.log("\n8. Testing Feature Status", "INFO")
        
        features_response = self.test_endpoint(
            "Get All Features Status",
            "GET",
            "/features/status",
            check_fields=["status", "features"]
        )
        
        if features_response and "features" in features_response:
            self.log(f"  Available Features:", "INFO")
            for feature, available in features_response["features"].items():
                status = "✓" if available else "✗"
                self.log(f"    {status} {feature}: {available}", "INFO")
        
        # Test individual feature status
        self.test_endpoint(
            "Get Email Feature Status",
            "GET",
            "/features/email/status",
            check_fields=["status", "feature", "available"]
        )
        
        # TEST 9: BRIEFING
        self.log("\n9. Testing Briefing Endpoint", "INFO")
        
        self.test_endpoint(
            "Get Morning Briefing",
            "GET",
            "/briefing",
            check_fields=["status"]
        )
        
        # TEST 10: NOTIFICATIONS
        self.log("\n10. Testing Notifications", "INFO")
        
        self.test_endpoint(
            "Get Notifications",
            "GET",
            "/notifications",
            check_fields=["status", "notifications"]
        )
        
        # TEST 11: OPTIONAL FEATURES (if available)
        self.log("\n11. Testing Optional Features", "INFO")
        
        # Email (if configured)
        if features_response and features_response.get("features", {}).get("email"):
            self.log("  Email feature available, testing send endpoint...", "INFO")
            # Don't actually send email, but test validation
            self.test_endpoint(
                "Email Validation (Empty Fields)",
                "POST",
                "/email/send",
                data={"to": "", "subject": "", "body": ""},
                expected_status=400  # Should fail validation
            )
        else:
            self.log("  Email feature not configured, skipping...", "WARN")
            self.results["skipped"].append("Email Send")
        
        # Notion (if configured)
        if features_response and features_response.get("features", {}).get("notion"):
            self.log("  Notion feature available, testing summarize endpoint...", "INFO")
            # Test with invalid data to check endpoint exists
            self.test_endpoint(
                "Notion Summarize (Missing Data)",
                "POST",
                "/notion/summarize",
                data={},
                expected_status=400  # Should fail validation
            )
        else:
            self.log("  Notion feature not configured, skipping...", "WARN")
            self.results["skipped"].append("Notion Summarize")
        
        # TEST 12: CLEANUP
        self.log("\n12. Cleanup - Delete Test Conversation", "INFO")
        
        if self.test_conversation_id:
            self.test_endpoint(
                "Delete Test Conversation",
                "DELETE",
                f"/conversation/{self.test_conversation_id}",
                check_fields=["status"]
            )
        
        # FINAL RESULTS
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 60, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        total_tests = len(self.results["passed"]) + len(self.results["failed"]) + len(self.results["skipped"])
        
        self.log(f"\nTotal Tests: {total_tests}", "INFO")
        self.log(f"Passed: {len(self.results['passed'])}", "PASS")
        self.log(f"Failed: {len(self.results['failed'])}", "FAIL")
        self.log(f"Skipped: {len(self.results['skipped'])}", "WARN")
        
        if self.results["failed"]:
            self.log("\nFailed Tests:", "FAIL")
            for test in self.results["failed"]:
                self.log(f"  - {test}", "FAIL")
        
        if self.results["skipped"]:
            self.log("\nSkipped Tests:", "WARN")
            for test in self.results["skipped"]:
                self.log(f"  - {test}", "WARN")
        
        # Calculate success rate
        if total_tests > 0:
            success_rate = (len(self.results["passed"]) / (total_tests - len(self.results["skipped"]))) * 100
            self.log(f"\nSuccess Rate: {success_rate:.1f}%", "PASS" if success_rate > 80 else "FAIL")
        
        self.log("\n" + "=" * 60, "INFO")

if __name__ == "__main__":
    print("\n🚀 Starting Backend FastAPI Comprehensive Test...\n")
    print("⚠️  NOTE: Make sure the backend is running on http://localhost:5000")
    print("    Run: python backend_fastapi.py\n")
    
    time.sleep(2)
    
    tester = BackendTester()
    tester.run_all_tests()
    
    print("\n✨ Test Complete!\n")

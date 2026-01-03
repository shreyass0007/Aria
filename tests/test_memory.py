
import sys
import os
import time
from unittest.mock import MagicMock

# Ensure aria is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aria.command_processor import CommandProcessor
from aria.memory_manager import MemoryManager

def test_memory_systems():
    print("\n--- Testing Memory Systems ---")
    
    # Mock dependencies
    mock_brain = MagicMock()
    # Mocking stream_ask to behave like an iterable
    mock_brain.stream_ask.return_value = ["This ", "is ", "a ", "test ", "response."] 
    mock_brain.get_llm.return_value = MagicMock()
    mock_brain.is_available.return_value = True

    mock_tts = MagicMock()
    
    # Initialize Memory Manager (Real one if possible, or Mock if env missing)
    if os.getenv("OPEN_AI_API_KEY"):
        print("[INFO] Using REAL MemoryManager (requires OpenAI Key)")
        memory_manager = MemoryManager()
    else:
        print("[WARN] Using MOCK MemoryManager (No API Key)")
        memory_manager = MagicMock()
        memory_manager.search_relevant_context.return_value = []
        memory_manager.add_message.return_value = True

    # Initialize Processor
    processor = CommandProcessor(
        tts_manager=mock_tts,
        app_launcher=MagicMock(),
        brain=mock_brain,
        calendar=MagicMock(),
        notion=MagicMock(),
        automator=MagicMock(),
        system_control=MagicMock(),
        command_classifier=MagicMock(), # command_classifier
        file_manager=MagicMock(),
        weather_manager=MagicMock(),
        clipboard_screenshot=MagicMock(),
        system_monitor=MagicMock(),
        email_manager=MagicMock(),
        greeting_service=MagicMock(),
        music_manager=MagicMock(),
        memory_manager=memory_manager,
        water_manager=MagicMock()
    )
    
    # --- TEST 1: Short Term Memory (STM) ---
    print("\n[Test 1] Short Term Memory (STM)")
    
    # Turn 1
    user_input_1 = "My favorite color is blue."
    print(f"User: {user_input_1}")
    processor.process_command(user_input_1, model_name="gpt-4o-mini")
    
    # Check history
    history = processor.conversation_history
    if len(history) >= 2:
        print(f"  [PASS] STM has {len(history)} items.")
        print(f"  Last item: {history[-1]}")
    else:
        print(f"  [FAIL] STM is empty or missing items: {history}")

    # Turn 2
    user_input_2 = "What is it?" # Context dependent
    print(f"User: {user_input_2}")
    
    # We can't easily check the *internal* prompt sent to LLM without more mocking,
    # but we can check if history grew.
    processor.process_command(user_input_2, model_name="gpt-4o-mini")
    
    if len(processor.conversation_history) >= 4:
         print(f"  [PASS] STM grew correctly (Size: {len(processor.conversation_history)})")
    else:
         print(f"  [FAIL] STM did not grow as expected.")


    # --- TEST 2: Long Term Memory (LTM) ---
    print("\n[Test 2] Long Term Memory (LTM)")
    
    # We check if add_message was called
    if isinstance(memory_manager, MagicMock):
        if memory_manager.add_message.called:
             print("  [PASS] LTM.add_message was called.")
        else:
             print("  [FAIL] LTM.add_message was NOT called.")
    else:
        # Real Memory Check
        # 1. Add unique fact
        unique_fact = f"The secret code is {int(time.time())}"
        print(f"  Storing fact: '{unique_fact}'")
        processor.process_command(unique_fact, model_name="gpt-4o-mini")
        
        # 2. Wait a moment for async/indexing (if any)
        time.sleep(1)
        
        # 3. Search for it
        print("  Retrieving fact...")
        results = memory_manager.search_relevant_context("What is the secret code?")
        
        found = any(unique_fact in res['text'] for res in results)
        if found:
            print("  [PASS] Successfully retrieved fact from LTM.")
        else:
             print(f"  [FAIL] Could not find fact. Top results: {[r['text'] for r in results]}")

if __name__ == "__main__":
    test_memory_systems()

from brain import AriaBrain
import time

def test_streaming():
    print("Testing Streaming...")
    brain = AriaBrain()
    
    if not brain.is_available():
        print("Brain not available.")
        return

    print("Asking: 'Tell me a short story about a robot.'")
    print("--- Stream Start ---")
    
    start_time = time.time()
    first_chunk = True
    
    for chunk in brain.stream_ask("Tell me a short story about a robot."):
        if first_chunk:
            print(f"\n[First chunk received after {time.time() - start_time:.2f}s]")
            first_chunk = False
        print(chunk, end="", flush=True)
        
    print("\n--- Stream End ---")

if __name__ == "__main__":
    test_streaming()

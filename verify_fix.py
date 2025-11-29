
import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

try:
    import backend_fastapi
    print("Imported backend_fastapi successfully.")
    
    # Initialize
    backend_fastapi.init_aria()
    print("Initialized Aria.")
    
    # Check system_monitor
    if backend_fastapi.system_monitor is not None:
        print("SUCCESS: system_monitor is initialized and accessible.")
        # Try using it
        health = backend_fastapi.system_monitor.check_health()
        print(f"Health check result: {health}")
    else:
        print("FAILURE: system_monitor is None.")
        
except Exception as e:
    print(f"Error: {e}")

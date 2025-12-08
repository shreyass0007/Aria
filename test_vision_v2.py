"""
Test Vision Pipeline
"""
import sys
import os
import json
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from aria.vision.pipeline import VisionPipeline
    
    def test_pipeline():
        print("Initializing Vision Pipeline...")
        pipeline = VisionPipeline()
        
        print("Analyzing screen...")
        result = pipeline.analyze_screen(save_debug=True)
        
        # Remove numpy arrays for printing
        print(json.dumps(result, default=str, indent=2))
        
        if "error" in result:
            print("Test Failed!")
        else:
            print(f"Test Passed! Debug image saved to {pipeline.debug_dir}")

    if __name__ == "__main__":
        test_pipeline()

except Exception as e:
    print("CRITICAL ERROR:")
    traceback.print_exc()

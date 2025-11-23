import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from weather_manager import WeatherManager

def test_weather():
    print("Testing WeatherManager...")
    
    # Check API Key
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("WARNING: OPENWEATHER_API_KEY not found in environment variables.")
        print("Please set it in .env or the test will fail/return error message.")
    else:
        print(f"API Key found: {api_key[:4]}...{api_key[-4:]}")

    wm = WeatherManager()
    
    # Test 1: Valid City
    print("\nTest 1: Check weather for London")
    result = wm.get_weather("London")
    print(f"Result: {result}")
    
    # Test 2: Invalid City
    print("\nTest 2: Check weather for InvalidCityName123")
    result = wm.get_weather("InvalidCityName123")
    print(f"Result: {result}")

    # Test 3: Empty City
    print("\nTest 3: Check weather for empty city")
    result = wm.get_weather("")
    print(f"Result: {result}")

if __name__ == "__main__":
    test_weather()

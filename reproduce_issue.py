from brain import AriaBrain
import datetime

def test_parsing():
    brain = AriaBrain()
    
    # The query that failed
    query = "Schedule a call with Aman at 12:30 AM for tomorrow"
    
    print(f"Testing query: '{query}'")
    print(f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        result = brain.parse_calendar_intent(query)
        print("\nResult:")
        print(result)
        
        if result.get('start_time'):
            start_time = result['start_time']
            print(f"\nExtracted Start Time: {start_time}")
            
            # Check if it looks like UTC (19:00 previous day) or Local (00:30 next day)
            if "19:00:00" in start_time:
                print("❌ ERROR: Time appears to be in UTC (19:00 prev day)")
            elif "00:30:00" in start_time:
                print("✅ SUCCESS: Time appears to be in Local IST (00:30 next day)")
            else:
                print("⚠️ WARNING: Time is neither expected UTC nor Local. Please check manually.")
                
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_parsing()

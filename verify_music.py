from music_library import MusicManager
import time

def test_music():
    print("Initializing MusicManager...")
    music = MusicManager()
    
    print("\n--- Test 1: Play Music ---")
    query = "lofi hip hop radio"
    print(f"Playing: {query}")
    result = music.play_music(query)
    print(f"Result: {result}")
    
    print("Waiting 10 seconds to hear audio...")
    time.sleep(10)
    
    print("\n--- Test 2: Pause ---")
    print(music.pause())
    time.sleep(2)
    
    print("\n--- Test 3: Resume ---")
    print(music.resume())
    time.sleep(5)
    
    print("\n--- Test 4: Volume ---")
    print(music.set_volume(30))
    time.sleep(2)
    print(music.set_volume(80))
    time.sleep(2)
    
    print("\n--- Test 5: Stop ---")
    print(music.stop())

if __name__ == "__main__":
    test_music()

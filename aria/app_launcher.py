import os
import difflib

class AppLauncher:
    def __init__(self, tts_manager):
        self.tts_manager = tts_manager
        self.app_paths = {}
        import threading
        threading.Thread(target=self.index_apps, daemon=True).start()

    def index_apps(self):
        """Scans Start Menu for .lnk files to build an app index."""
        print("Indexing apps...")
        paths = [
            os.path.join(os.getenv('ProgramData'), r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs')
        ]
        
        for path in paths:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".lnk"):
                        # Clean name: "Google Chrome.lnk" -> "google chrome"
                        name = file.lower().replace(".lnk", "")
                        full_path = os.path.join(root, file)
                        self.app_paths[name] = full_path
        print(f"Indexed {len(self.app_paths)} apps.")

    def open_desktop_app(self, app_name: str):
        app_name = app_name.lower()
        
        # 1. Exact Match
        if app_name in self.app_paths:
            try:
                self.tts_manager.speak(f"Opening {app_name}")
                os.startfile(self.app_paths[app_name])
                return
            except Exception as e:
                print(f"Error opening {app_name}: {e}")

        # 2. Substring Match (e.g. "chrome" -> "google chrome")
        # Find all apps that contain the query
        substring_matches = [name for name in self.app_paths if app_name in name]
        if substring_matches:
            # Sort by length to find the most relevant (shortest) match
            # e.g. "chrome" prefers "google chrome" over "google chrome remote desktop"
            best_match = sorted(substring_matches, key=len)[0]
            try:
                self.tts_manager.speak(f"Opening {best_match}")
                os.startfile(self.app_paths[best_match])
                return
            except Exception as e:
                print(f"Error opening {best_match}: {e}")

        # 3. Fuzzy Match (Stricter)
        matches = difflib.get_close_matches(app_name, list(self.app_paths.keys()), n=1, cutoff=0.8)
        if matches:
            best_match = matches[0]
            try:
                self.tts_manager.speak(f"Opening {best_match}")
                os.startfile(self.app_paths[best_match])
                return
            except Exception as e:
                print(f"Error opening {best_match}: {e}")

        # 4. Fallback to System Command (e.g. notepad, calc)
        try:
            self.tts_manager.speak(f"Attempting to open {app_name}")
            os.startfile(app_name) # Works for things in PATH
        except Exception:
            self.tts_manager.speak(f"I couldn't find or open {app_name}.")

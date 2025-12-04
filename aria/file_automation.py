import os
import shutil
import time
import datetime
from pathlib import Path

class FileAutomator:
    def __init__(self):
        self.extensions = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
            "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
            "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
            "Executables": [".exe", ".msi", ".bat", ".sh", ".apk"],
            "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".sql"]
        }

    def get_downloads_folder(self):
        """Returns the path to the user's Downloads folder."""
        if os.name == 'nt':
            try:
                import winreg
                sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                    location = winreg.QueryValueEx(key, downloads_guid)[0]
                return Path(location)
            except Exception:
                pass
        
        return Path.home() / 'Downloads'

    def get_desktop_folder(self):
        """Returns the path to the user's Desktop folder."""
        return Path.home() / 'Desktop'

    def organize_folder(self, folder_path):
        """
        Organizes files in the specified folder into subfolders based on their extensions.
        """
        folder = Path(folder_path)
        if not folder.exists():
            return f"Error: The folder '{folder_path}' does not exist."


        moved_count = 0
        
        # Create category folders if they don't exist
        for category in self.extensions.keys():
            (folder / category).mkdir(exist_ok=True)
        
        # Create 'Others' folder
        (folder / "Others").mkdir(exist_ok=True)

        for file_path in folder.iterdir():
            if file_path.is_dir():
                continue
            
            # Skip hidden files
            if file_path.name.startswith('.'):
                continue

            # Find category
            file_ext = file_path.suffix.lower()
            destination_category = "Others"
            
            for category, exts in self.extensions.items():
                if file_ext in exts:
                    destination_category = category
                    break
            
            # Move file
            try:
                destination = folder / destination_category / file_path.name
                
                # Handle duplicates by renaming
                if destination.exists():
                    base = destination.stem
                    ext = destination.suffix
                    counter = 1
                    while destination.exists():
                        destination = folder / destination_category / f"{base}_{counter}{ext}"
                        counter += 1
                
                shutil.move(str(file_path), str(destination))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file_path.name}: {e}")

        # Cleanup empty folders (optional, maybe too aggressive for now)
        # for category in self.extensions.keys():
        #     cat_path = folder / category
        #     if cat_path.exists() and not any(cat_path.iterdir()):
        #         cat_path.rmdir()
        #     
        # others_path = folder / "Others"
        # if others_path.exists() and not any(others_path.iterdir()):
        #     others_path.rmdir()

        # ... (existing code) ...

        return f"Organized {moved_count} files in {folder_path}."

    def archive_old_files(self, folder_path, days=30):
        """
        Moves files older than 'days' to an 'Archive' subfolder, organized by Year/Month.
        """
        folder = Path(folder_path)
        if not folder.exists():
            return f"Error: The folder '{folder_path}' does not exist."


        archive_root = folder / "Archive"
        archive_root.mkdir(exist_ok=True)
        
        moved_count = 0
        cutoff_time = time.time() - (days * 86400) # 86400 seconds in a day

        for file_path in folder.iterdir():
            if file_path.is_dir():
                continue
            
            # Skip hidden files
            if file_path.name.startswith('.'):
                continue

            try:
                # Check modification time
                mtime = file_path.stat().st_mtime
                if mtime < cutoff_time:
                    # Get Year and Month
                    date_obj = datetime.datetime.fromtimestamp(mtime)
                    year_str = date_obj.strftime("%Y")
                    month_str = date_obj.strftime("%B") # e.g., "November"
                    
                    # Create target folder: Archive/2024/November
                    target_dir = archive_root / year_str / month_str
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    destination = target_dir / file_path.name
                    
                    # Handle duplicates
                    if destination.exists():
                        base = destination.stem
                        ext = destination.suffix
                        counter = 1
                        while destination.exists():
                            destination = target_dir / f"{base}_{counter}{ext}"
                            counter += 1
                    
                    shutil.move(str(file_path), str(destination))
                    moved_count += 1
            except Exception as e:
                print(f"Error archiving {file_path.name}: {e}")

        return f"Archived {moved_count} files older than {days} days."

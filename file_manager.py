"""
File Manager Module for Aria
Provides comprehensive CRUD operations on files with natural language support
"""

import os
import shutil
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FileManager:
    """
    Handles all file CRUD operations with chat-friendly output
    """
    
    def __init__(self):
        """Initialize the file manager."""
        self.safe_locations = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
        ]
        
        self.dangerous_extensions = ['.exe', '.dll', '.sys', '.bat', '.sh', '.ps1']
        
        self.location_shortcuts = {
            "desktop": os.path.expanduser("~/Desktop"),
            "downloads": os.path.expanduser("~/Downloads"),
            "documents": os.path.expanduser("~/Documents"),
            "pictures": os.path.expanduser("~/Pictures"),
            "music": os.path.expanduser("~/Music"),
            "videos": os.path.expanduser("~/Videos"),
        }
    
    def _resolve_path(self, path: str, location: Optional[str] = None) -> Path:
        """Resolve file path, defaulting to Desktop if no location specified."""
        if location and location.lower() in self.location_shortcuts:
            base_path = Path(self.location_shortcuts[location.lower()])
            return base_path / path
        
        if os.path.isabs(path):
            return Path(path)
        
        # Default to Desktop to avoid creating files in program directory
        desktop_path = Path(self.location_shortcuts["desktop"]) / path
        return desktop_path
    
    def _is_safe_operation(self, path: Path) -> bool:
        """Check if operation on this path is safe."""
        path_str = str(path.absolute()).lower()
        dangerous_paths = ['c:\\windows', 'c:\\program files', 'c:\\programdata', '/system', '/usr/bin', '/bin']
        return not any(dangerous in path_str for dangerous in dangerous_paths)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    # CREATE OPERATIONS
    def create_file(self, filename: str, content: str = "", location: Optional[str] = None) -> str:
        """Create a new file with optional content."""
        try:
            file_path = self._resolve_path(filename, location)
            if file_path.exists():
                return f"File '{filename}' already exists"
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            
            return f"Created file '{filename}' on Desktop" if not location else f"Created file '{filename}'"
        except Exception as e:
            return f"Error creating file: {str(e)}"
    
    # READ OPERATIONS
    def read_file(self, filename: str, location: Optional[str] = None, max_lines: int = 50) -> str:
        """Read and return file contents."""
        try:
            file_path = self._resolve_path(filename, location)
            if not file_path.exists():
                return f"I couldn't find '{filename}'"
            
            if not file_path.is_file():
                return f"'{filename}' is not a file"
            
            size = file_path.stat().st_size
            if size > 1_000_000:
                return f"File '{filename}' is too large to read ({self._format_file_size(size)})"
            
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            if len(lines) > max_lines:
                truncated = '\n'.join(lines[:max_lines])
                return f"Here's the first {max_lines} lines of {filename}:\n\n{truncated}\n\n...there's more below"
            else:
                return f"Here's {filename}:\n\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_file_info(self, filename: str, location: Optional[str] = None) -> str:
        """Get file information."""
        try:
            file_path = self._resolve_path(filename, location)
            if not file_path.exists():
                return f"I couldn't find '{filename}'"
            
            stats = file_path.stat()
            from datetime import datetime
            modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            return f"{filename}\nLocation: {file_path.parent}\nSize: {self._format_file_size(stats.st_size)}\nModified: {modified}"
        except Exception as e:
            return f"Error getting file info: {str(e)}"
    
    # UPDATE OPERATIONS  
    def append_to_file(self, filename: str, content: str, location: Optional[str] = None) -> str:
        """Append content to file."""
        try:
            file_path = self._resolve_path(filename, location)
            if not file_path.exists():
                return f"I couldn't find '{filename}'. Create it first"
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write('\n' + content)
            
            return f"Added content to '{filename}'"
        except Exception as e:
            return f"Error appending to file: {str(e)}"
    
    def replace_in_file(self, filename: str, old_text: str, new_text: str, location: Optional[str] = None) -> str:
        """Replace text in file."""
        try:
            file_path = self._resolve_path(filename, location)
            if not file_path.exists():
                return f"I couldn't find '{filename}'"
            
            content = file_path.read_text(encoding='utf-8')
            count = content.count(old_text)
            if count == 0:
                return f"Couldn't find '{old_text}' in '{filename}'"
            
            new_content = content.replace(old_text, new_text)
            file_path.write_text(new_content, encoding='utf-8')
            return f"Replaced {count} occurrence(s) in '{filename}'"
        except Exception as e:
            return f"Error replacing text: {str(e)}"
    
    # DELETE OPERATIONS
    def delete_file(self, filename: str, location: Optional[str] = None, force: bool = False) -> str:
        """Delete file or directory."""
        try:
            file_path = self._resolve_path(filename, location)
            if not file_path.exists():
                return f"I couldn't find '{filename}'"
            
            if not force and not self._is_safe_operation(file_path):
                return f"Can't delete '{filename}' - it's in a protected location"
            
            if not force and file_path.suffix.lower() in self.dangerous_extensions:
                return f"Can't delete '{filename}' - dangerous file type"
            
            if file_path.is_dir():
                shutil.rmtree(file_path)
                return f"Deleted directory '{filename}'"
            else:
                file_path.unlink()
                return f"Deleted '{filename}'"
        except Exception as e:
            return f"Error deleting: {str(e)}"
    
    # RENAME/MOVE OPERATIONS
    def rename_file(self, old_name: str, new_name: str, location: Optional[str] = None) -> str:
        """Rename file."""
        try:
            old_path = self._resolve_path(old_name, location)
            if not old_path.exists():
                return f"I couldn't find '{old_name}'"
            
            new_path = old_path.parent / new_name
            if new_path.exists():
                return f"'{new_name}' already exists"
            
            old_path.rename(new_path)
            return f"Renamed '{old_name}' to '{new_name}'"
        except Exception as e:
            return f"Error renaming: {str(e)}"
    
    def move_file(self, filename: str, destination: str, source_location: Optional[str] = None) -> str:
        """Move file to different location."""
        try:
            source_path = self._resolve_path(filename, source_location)
            if not source_path.exists():
                return f"I couldn't find '{filename}'"
            
            if destination.lower() in self.location_shortcuts:
                dest_path = Path(self.location_shortcuts[destination.lower()]) / filename
            else:
                dest_path = Path(destination)
                if dest_path.is_dir():
                    dest_path = dest_path / filename
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if dest_path.exists():
                return f"'{filename}' already exists at destination"
            
            shutil.move(str(source_path), str(dest_path))
            return f"Moved '{filename}' to {destination}"
        except Exception as e:
            return f"Error moving file: {str(e)}"
    
    # COPY OPERATIONS
    def copy_file(self, filename: str, destination: str, source_location: Optional[str] = None, new_name: Optional[str] = None) -> str:
        """Copy file to different location."""
        try:
            source_path = self._resolve_path(filename, source_location)
            if not source_path.exists():
                return f"I couldn't find '{filename}'"
            
            final_name = new_name if new_name else filename
            
            if destination.lower() in self.location_shortcuts:
                dest_path = Path(self.location_shortcuts[destination.lower()]) / final_name
            else:
                dest_path = Path(destination)
                if dest_path.is_dir():
                    dest_path = dest_path / final_name
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if dest_path.exists():
                return f"'{final_name}' already exists at destination"
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
                return f"Copied directory '{filename}' to {destination}"
            else:
                shutil.copy2(source_path, dest_path)
                return f"Copied '{filename}' to {destination}"
        except Exception as e:
            return f"Error copying file: {str(e)}"
    
    # SEARCH OPERATIONS
    def search_files(self, pattern: str, location: Optional[str] = None, search_subdirs: bool = True) -> str:
        """Search for files - CONVERSATIONAL OUTPUT (no technical symbols)."""
        try:
            if location and location.lower() in self.location_shortcuts:
                search_path = Path(self.location_shortcuts[location.lower()])
            else:
                search_path = Path(self.location_shortcuts["desktop"])
            
            if not search_path.exists():
                return f"I couldn't find the {location} folder"
            
            # Search
            matches = list(search_path.rglob(pattern)) if search_subdirs else list(search_path.glob(pattern))
            
            if not matches:
                return f"I couldn't find any files matching '{pattern}' in {search_path.name}"
            
            # Conversational output
            if len(matches) == 1:
                match = matches[0]
                size = self._format_file_size(match.stat().st_size) if match.is_file() else "folder"
                return f"I found 1 file: {match.name} ({size})"
            else:
                result = [f"I found {len(matches)} files in {search_path.name}:"]
                for i, match in enumerate(matches[:10], 1):
                    size = self._format_file_size(match.stat().st_size) if match.is_file() else "folder"
                    result.append(f"{i}. {match.name} ({size})")
                
                if len(matches) > 10:
                    result.append(f"...and {len(matches) - 10} more files")
                
                return '\n'.join(result)
        except Exception as e:
            return f"I had trouble searching: {str(e)}"

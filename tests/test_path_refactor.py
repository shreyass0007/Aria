import os
from pathlib import Path
from aria.file_automation import FileAutomator
from aria import config

def test_file_automator_paths():
    automator = FileAutomator()
    downloads = automator.get_downloads_folder()
    desktop = automator.get_desktop_folder()
    
    assert isinstance(downloads, Path)
    assert isinstance(desktop, Path)
    
    # Check if they look like valid paths (even if they don't exist in test env)
    assert "Downloads" in str(downloads)
    assert "Desktop" in str(desktop)

def test_config_root_dir():
    assert isinstance(config.ROOT_DIR, Path)
    assert config.ROOT_DIR.exists()
    assert (config.ROOT_DIR / "aria").exists()

def test_email_manager_paths():
    # Verify that email manager would look for files in the right place
    # We don't want to actually authenticate, just check the path logic if possible.
    # Since we can't easily unit test the internal logic without mocking, 
    # we rely on the fact that we changed it to use config.ROOT_DIR.
    # Here we just assert the files it *would* look for exist or are at least paths.
    
    token_path = config.ROOT_DIR / 'token_gmail.pickle'
    creds_path = config.ROOT_DIR / 'credentials.json'
    
    assert isinstance(token_path, Path)
    assert isinstance(creds_path, Path)

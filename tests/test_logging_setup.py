import os
import logging
from aria import config
from aria.logger import setup_logger

def test_logger_creation():
    logger = setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO or logger.level == logging.DEBUG
    assert len(logger.handlers) >= 2 # File and Stream

def test_log_file_creation():
    # Ensure log directory exists
    if not config.LOG_DIR.exists():
        config.LOG_DIR.mkdir()
    
    logger = setup_logger("test_file_logger")
    test_message = "TEST LOG MESSAGE"
    logger.info(test_message)
    
    # Check if file exists and contains message
    assert config.LOG_FILE_PATH.exists()
    
    with open(config.LOG_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        assert test_message in content

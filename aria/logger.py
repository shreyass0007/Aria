import logging
import sys
from logging.handlers import RotatingFileHandler
from . import config

def setup_logger(name):
    """
    Sets up a logger with the specified name.
    Configures both file and console handlers.
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, assume it's set up to avoid duplicate logs
    if logger.handlers:
        return logger
        
    logger.setLevel(config.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File Handler (Rotating)
    # Max size 5MB, keep 3 backup files
    file_handler = RotatingFileHandler(
        config.LOG_FILE_PATH, 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(config.LOG_LEVEL)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(config.LOG_LEVEL)

    # Add Handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

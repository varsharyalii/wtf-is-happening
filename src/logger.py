"""
Logging setup - because print statements are so 2010.

This sets up proper logging so we can:
- See what's happening without cluttering the console
- Save logs to files for debugging
- Filter by importance (DEBUG, INFO, WARNING, ERROR)

Usage:
    from src.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
    logger.error("Oh no, something broke")
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Set up logging for the entire application.
    
    Call this once at the start of your app (in main() or __init__).
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to save logs to
        format_string: Custom format for log messages
    """
    # Default format - includes timestamp, level, and message
    if format_string is None:
        format_string = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[]  # We'll add our own handlers
    )
    
    # Create formatters
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Console handler (prints to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Add console handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    
    # File handler (saves to file) - optional
    if log_file:
        # Make sure logs directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Usually __name__ (the module name)
        
    Returns:
        A logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Hello from my module!")
    """
    return logging.getLogger(name)


# Pre-configured logger for quick use
logger = logging.getLogger(__name__)


"""
Logging configuration for the AI Web Research Agent.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
):
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)
        log_dir: Directory to store log files (default: "logs")
        log_format: Log message format
        
    Returns:
        None
    """
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if requested
    if log_to_file:
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = os.path.join(log_dir, f"research_agent_{timestamp}.log")
        
        # Configure file handler with rotation (5 MB max size, max 5 backup files)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        logging.info(f"Logging to file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
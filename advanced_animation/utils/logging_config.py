"""
Logging Configuration for Advanced Animation System

This module provides centralized logging configuration that saves logs
to separate files for each run, making debugging and tracking easier.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional

class LoggingManager:
    """Manages logging configuration for the advanced animation system."""
    
"""
    Performs __init__ operation. Function has side effects. Takes self, output_dir and log_level as input. Returns a object value.
    :param self: The self object.
    :param output_dir: The output_dir string.
    :param log_level: The log_level integer.
    :return: Value of type object
"""
    def __init__(self, output_dir: str = "logs", log_level: int = logging.INFO):
        """
        Initialize the logging manager.
        
        Args:
            output_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.output_dir = Path(output_dir)
        self.log_level = log_level
        self.log_file = None
        self.setup_logging()
    
"""
    Sets the logging to the specified value. Function has side effects, performs arithmetic operations. Takes self as input. Returns a object value.
    :param self: The self object.
    :return: Value of type object
"""
    def setup_logging(self):
        """Setup logging configuration with file and console handlers."""
        # Create logs directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.output_dir / f"animation_run_{timestamp}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        
        # File handler (detailed logging)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler (simplified for terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log the start of this session
        logger = logging.getLogger(__name__)
        logger.info(f"Logging session started - Log file: {self.log_file}")
        logger.info(f"Log level: {logging.getLevelName(self.log_level)}")
    
"""
    Retrieves the log. Takes self as input. Returns a optional[path] value.
    :param self: The self object.
    :return: Value of type Optional[Path]
"""
    def get_log_file_path(self) -> Optional[Path]:
        """Get the current log file path."""
        return self.log_file
    
"""
    Performs log_system_info operation. Function has side effects, performs arithmetic operations. Takes self as input. Returns a object value.
    :param self: The self object.
    :return: Value of type object
"""
    def log_system_info(self):
        """Log system information for debugging."""
        logger = logging.getLogger(__name__)
        
        import sys
        import platform
        
        logger.info("=" * 60)
        logger.info("SYSTEM INFORMATION")
        logger.info("=" * 60)
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Architecture: {platform.architecture()}")
        logger.info(f"Processor: {platform.processor()}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info("=" * 60)
    
"""
    Performs log_environment_info operation. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes self as input. Returns a object value.
    :param self: The self object.
    :return: Value of type object
"""
    def log_environment_info(self):
        """Log environment information for debugging."""
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 60)
        logger.info("ENVIRONMENT INFORMATION")
        logger.info("=" * 60)
        
        # Check for important environment variables
        env_vars = [
            'OPENAI_API_KEY',
            'ELEVENLABS_API_KEY',
            'E2B_API_KEY',
            'PYTHONPATH'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'API_KEY' in var:
                    masked_value = value[:8] + '*' * (len(value) - 12) + value[-4:] if len(value) > 12 else '***'
                    logger.info(f"{var}: {masked_value}")
                else:
                    logger.info(f"{var}: {value}")
            else:
                logger.warning(f"{var}: Not set")
        
        logger.info("=" * 60)

"""
    Sets the logging to the specified value. Function has side effects. Takes output_dir and log_level as input. Returns a loggingmanager value.
    :param output_dir: The output_dir string.
    :param log_level: The log_level integer.
    :return: Value of type LoggingManager
"""
def setup_logging_for_run(output_dir: str = "logs", log_level: int = logging.INFO) -> LoggingManager:
    """
    Setup logging for a new run.
    
    Args:
        output_dir: Directory to store log files
        log_level: Logging level
        
    Returns:
        LoggingManager instance
    """
    manager = LoggingManager(output_dir, log_level)
    manager.log_system_info()
    manager.log_environment_info()
    return manager

"""
    Retrieves the logger. Function has side effects. Takes name as input. Returns a logging.logger value.
    :param name: The name string.
    :return: Value of type logging.Logger
"""
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) 
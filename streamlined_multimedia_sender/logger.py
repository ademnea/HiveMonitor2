"""
Logging module for the Arthur IoTRA project.
This module centralizes all logging functionality and provides consistent logging across the application.
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LoggingConfig:
    """Configuration class for logging settings."""
    level: str
    max_bytes: int
    backup_count: int
    format: str
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create LoggingConfig from environment variables with defaults."""
        return cls(
            level=_get_env("LOG_LEVEL", "INFO"),
            max_bytes=int(_get_env("LOG_MAX_BYTES", "1048576")),  # 1 MB
            backup_count=int(_get_env("LOG_BACKUP_COUNT", "3")),
            format=_get_env("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s"),
        )


def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Helper function to get environment variables with defaults."""
    value = os.environ.get(key, default)
    return value


def setup_logging(log_dir: str, config: LoggingConfig) -> logging.Logger:
    """Set up rotating file logging based on configuration.
    
    Args:
        log_dir: Directory where log files will be stored
        config: LoggingConfig object with logging settings
        
    Returns:
        Root logger configured according to settings
    """
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Set up root logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set logging level
    level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create rotating file handler
    log_file = log_path / "arthur_iotra.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file),
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    
    # Create console handler for INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(config.format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Return the root logger
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger.
    
    This is a convenience function to get a named logger from the root logger.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A named logger instance
    """
    return logging.getLogger(name)


def log_system_info() -> None:
    """Log system information that might be useful for debugging."""
    logger = get_logger(__name__)
    
    try:
        import platform
        import psutil
        
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Python version: {platform.python_version()}")
        
        # CPU info
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        logger.info(f"CPU cores: {cpu_count} physical, {cpu_count_logical} logical")
        
        # Memory info
        memory = psutil.virtual_memory()
        logger.info(f"Memory: {memory.total / (1024**3):.2f} GB total, {memory.available / (1024**3):.2f} GB available")
        
        # Disk info
        disk = psutil.disk_usage('/')
        logger.info(f"Disk: {disk.total / (1024**3):.2f} GB total, {disk.free / (1024**3):.2f} GB free")
        
    except ImportError:
        logger.debug("psutil not installed, skipping detailed system info")
        logger.info(f"Platform: {platform.platform() if 'platform' in locals() else 'Unknown'}")
        logger.info(f"Python version: {platform.python_version() if 'platform' in locals() else 'Unknown'}")
    except Exception as e:
        logger.warning(f"Failed to collect system info: {e}")
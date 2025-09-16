#!/usr/bin/env python3
"""
Test script to verify the logger functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    # Try absolute import first
    from streamlined_multimedia_sender.logger import setup_logging, get_logger, LoggingConfig, log_system_info
except ImportError:
    # Fallback to local imports
    try:
        from logger import setup_logging, get_logger, LoggingConfig, log_system_info
    except ImportError as e:
        print(f"Cannot import required modules: {e}")
        print("Please run from the repository root directory or install as a package")
        sys.exit(1)


def test_logging():
    """Test the logging functionality."""
    # Create a basic logging config
    logging_config = LoggingConfig(
        level="DEBUG",
        max_bytes=1048576,
        backup_count=3,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Setup logging
    log_dir = Path("./test_logs")
    setup_logging(str(log_dir), logging_config)
    
    # Get a logger
    logger = get_logger("test_logger")
    
    # Log some messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Log system info
    log_system_info()
    
    print(f"Log file created at: {log_dir / 'arthur_iotra.log'}")
    print("Please check the log file to verify logging works correctly")


if __name__ == "__main__":
    test_logging()
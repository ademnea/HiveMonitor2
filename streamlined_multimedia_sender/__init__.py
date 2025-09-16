"""
Arthur IoTra Streamlined Communication System

This package provides a linear-flow IoT communication system that adaptively
selects between WiFi, GSM, and LoRa interfaces based on connectivity metrics.
"""

__version__ = "1.0.0"
__author__ = "Arthur IoTra Project"

from .config import load_config, Config
from .comms import Comms

__all__ = ["load_config", "Config", "Comms"]

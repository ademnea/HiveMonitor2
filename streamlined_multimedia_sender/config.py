import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    # Try absolute import first
    from streamlined_multimedia_sender.logger import LoggingConfig
except ImportError:
    # Fallback to local import
    try:
        from logger import LoggingConfig
    except ImportError:
        # Define here as fallback
        @dataclass
        class LoggingConfig:
            level: str
            max_bytes: int
            backup_count: int
            format: str

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, environment variables should be set manually
    pass


def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(key, default)
    return value


@dataclass
class ServerConfig:
    host: str
    port: int
    username: str
    password: str
    dest_path: str


@dataclass
class PathsConfig:
    # Multiple source directories to match original sender
    image_dir: str
    video_dir: str
    audio_dir: str
    parameter_dir: str
    vibration_dir: str
    # Other directories
    archive_dir: str
    log_dir: str
    metrics_dir: str


@dataclass
class DeviceConfig:
    device_id: str
    wifi_iface: str
    ppp_profile: str


@dataclass
class GsmConfig:
    port: str
    baud: int


@dataclass
class LoraConfig:
    port: str
    baud: int


@dataclass
class SelectionConfig:
    threshold_wifi: float
    threshold_gsm: float
    hysteresis_delta: float
    ping_server: str


@dataclass
class LoggingConfig:
    level: str
    max_bytes: int
    backup_count: int
    format: str


@dataclass
class Config:
    server: ServerConfig
    paths: PathsConfig
    device: DeviceConfig
    gsm: GsmConfig
    lora: LoraConfig
    selection: SelectionConfig
    logging: LoggingConfig
    logging: LoggingConfig


def load_config() -> Config:
    """Load configuration from environment variables.

    Values default to those currently hardcoded in the repository so that
    existing behavior is preserved until a .env is provided.
    """

    server = ServerConfig(
        host=_get_env("SERVER_HOST", "REMOVED"),
        port=int(_get_env("SERVER_SSH_PORT", "22")),
        username=_get_env("SERVER_USER", "ephrince"),
        password=_get_env("SERVER_PASSWORD", "Ephrance@2026"),
        dest_path=_get_env("DEST_PATH", "/var/www/html/ademnea_website/public/arriving_hive_media"),
    )

    paths = PathsConfig(
        image_dir=_get_env("IMAGE_DIR", "/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/images/"),
        video_dir=_get_env("VIDEO_DIR", "/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/videos/"),
        audio_dir=_get_env("AUDIO_DIR", "/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/audios/"),
        parameter_dir=_get_env("PARAMETER_DIR", "/home/pi/Desktop/HiveMonitor2/parameter_capture/sensor_data"),
        vibration_dir=_get_env("VIBRATION_DIR", "/home/pi/Desktop/HiveMonitor2/parameter_capture/vibration_sensor/fft_log"),
        archive_dir=_get_env("ARCHIVE_DIR", "/home/pi/arthur/archives"),
        log_dir=_get_env("LOG_DIR", "/home/pi/arthur/logs"),
        metrics_dir=_get_env("METRICS_DIR", "/home/pi/arthur/metrics"),
    )

    device = DeviceConfig(
        device_id=_get_env("DEVICE_ID", "pi-zero-2w"),
        wifi_iface=_get_env("WIFI_IFACE", "wlan0"),
        ppp_profile=_get_env("PPP_PROFILE", "mobile"),
    )

    gsm = GsmConfig(
        port=_get_env("GSM_PORT", "/dev/serial0"),
        baud=int(_get_env("GSM_BAUD", "9600")),
    )

    lora = LoraConfig(
        port=_get_env("LORA_PORT", "/dev/ttyUSB0"),
        baud=int(_get_env("LORA_BAUD", "9600")),
    )

    selection = SelectionConfig(
        threshold_wifi=float(_get_env("THRESHOLD_WIFI", "0.60")),
        threshold_gsm=float(_get_env("THRESHOLD_GSM", "0.50")),
        hysteresis_delta=float(_get_env("HYSTERESIS_DELTA", "0.10")),
        ping_server=_get_env("PING_SERVER", "REMOVED"),
    )

    logging_config = LoggingConfig(
        level=_get_env("LOG_LEVEL", "INFO"),
        max_bytes=int(_get_env("LOG_MAX_BYTES", "1048576")),  # 1 MB
        backup_count=int(_get_env("LOG_BACKUP_COUNT", "3")),
        format=_get_env("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s"),
    )

    return Config(
        server=server,
        paths=paths,
        device=device,
        gsm=gsm,
        lora=lora,
        selection=selection,
        logging=logging_config,
    )


def setup_logging(config: Config):
    """Import and set up logging from the logger module.
    
    This function is maintained for backwards compatibility.
    It delegates to the logger module's setup_logging function.
    """
    try:
        from streamlined_multimedia_sender.logger import setup_logging as _setup_logging
    except ImportError:
        from logger import setup_logging as _setup_logging
    
    # Call the setup_logging function from logger.py
    return _setup_logging(config.paths.log_dir, config.logging)


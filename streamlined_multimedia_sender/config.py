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


def _get_env(key: str) -> str:
    """Get environment variable or raise error if not found."""
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
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
    query_read_delay: float
    query_timeout: float


@dataclass
class LoraConfig:
    port: str
    baud: int
    # Mock values for testing (should be replaced with actual sensor readings)
    mock_rssi: int
    mock_snr: int
    mock_temperature: float
    # Retry and timing configuration
    max_send_attempts: int
    retry_delay: float
    inter_chunk_delay: float


@dataclass
class SelectionConfig:
    threshold_wifi: float
    threshold_gsm: float
    hysteresis_delta: float
    ping_server: str
    # Scoring weights for WiFi interface
    wifi_rssi_weight: float
    wifi_latency_weight: float
    wifi_loss_weight: float
    wifi_tcp_weight: float
    # Scoring weights for GSM interface
    gsm_csq_weight: float
    gsm_creg_weight: float
    gsm_cops_weight: float
    gsm_tcp_weight: float


@dataclass
class NetworkConfig:
    # Timeout values in seconds
    ssh_connection_timeout: int
    ssh_auth_timeout: int
    wifi_command_timeout: int
    lora_serial_timeout: int
    lora_command_timeout: float
    # Retry configuration
    max_retries: int
    base_delay: float
    # WiFi activation delay
    wifi_activation_delay: float


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
    network: NetworkConfig
    logging: LoggingConfig


def load_config() -> Config:
    """Load configuration from environment variables.
    
    All values must be provided in the .env file or environment variables.
    """

    server = ServerConfig(
        host=_get_env("SERVER_HOST"),
        port=int(_get_env("SERVER_SSH_PORT")),
        username=_get_env("SERVER_USER"),
        password=_get_env("SERVER_PASSWORD"),
        dest_path=_get_env("DEST_PATH"),
    )

    paths = PathsConfig(
        image_dir=_get_env("IMAGE_DIR"),
        video_dir=_get_env("VIDEO_DIR"),
        audio_dir=_get_env("AUDIO_DIR"),
        parameter_dir=_get_env("PARAMETER_DIR"),
        vibration_dir=_get_env("VIBRATION_DIR"),
        archive_dir=_get_env("ARCHIVE_DIR"),
        log_dir=_get_env("LOG_DIR"),
        metrics_dir=_get_env("METRICS_DIR"),
    )

    device = DeviceConfig(
        device_id=_get_env("DEVICE_ID"),
        wifi_iface=_get_env("WIFI_IFACE"),
        ppp_profile=_get_env("PPP_PROFILE"),
    )

    gsm = GsmConfig(
        port=_get_env("GSM_PORT"),
        baud=int(_get_env("GSM_BAUD")),
        query_read_delay=float(_get_env("GSM_QUERY_READ_DELAY")),
        query_timeout=float(_get_env("GSM_QUERY_TIMEOUT")),
    )

    lora = LoraConfig(
        port=_get_env("LORA_PORT"),
        baud=int(_get_env("LORA_BAUD")),
        mock_rssi=int(_get_env("LORA_MOCK_RSSI")),
        mock_snr=int(_get_env("LORA_MOCK_SNR")),
        mock_temperature=float(_get_env("LORA_MOCK_TEMPERATURE")),
        max_send_attempts=int(_get_env("LORA_MAX_SEND_ATTEMPTS")),
        retry_delay=float(_get_env("LORA_RETRY_DELAY")),
        inter_chunk_delay=float(_get_env("LORA_INTER_CHUNK_DELAY")),
    )

    selection = SelectionConfig(
        threshold_wifi=float(_get_env("THRESHOLD_WIFI")),
        threshold_gsm=float(_get_env("THRESHOLD_GSM")),
        hysteresis_delta=float(_get_env("HYSTERESIS_DELTA")),
        ping_server=_get_env("PING_SERVER"),
        wifi_rssi_weight=float(_get_env("WIFI_RSSI_WEIGHT")),
        wifi_latency_weight=float(_get_env("WIFI_LATENCY_WEIGHT")),
        wifi_loss_weight=float(_get_env("WIFI_LOSS_WEIGHT")),
        wifi_tcp_weight=float(_get_env("WIFI_TCP_WEIGHT")),
        gsm_csq_weight=float(_get_env("GSM_CSQ_WEIGHT")),
        gsm_creg_weight=float(_get_env("GSM_CREG_WEIGHT")),
        gsm_cops_weight=float(_get_env("GSM_COPS_WEIGHT")),
        gsm_tcp_weight=float(_get_env("GSM_TCP_WEIGHT")),
    )

    network = NetworkConfig(
        ssh_connection_timeout=int(_get_env("SSH_CONNECTION_TIMEOUT")),
        ssh_auth_timeout=int(_get_env("SSH_AUTH_TIMEOUT")),
        wifi_command_timeout=int(_get_env("WIFI_COMMAND_TIMEOUT")),
        lora_serial_timeout=int(_get_env("LORA_SERIAL_TIMEOUT")),
        lora_command_timeout=float(_get_env("LORA_COMMAND_TIMEOUT")),
        max_retries=int(_get_env("MAX_RETRIES")),
        base_delay=float(_get_env("BASE_DELAY")),
        wifi_activation_delay=float(_get_env("WIFI_ACTIVATION_DELAY")),
    )

    logging_config = LoggingConfig(
        level=_get_env("LOG_LEVEL"),
        max_bytes=int(_get_env("LOG_MAX_BYTES")),
        backup_count=int(_get_env("LOG_BACKUP_COUNT")),
        format=_get_env("LOG_FORMAT"),
    )

    return Config(
        server=server,
        paths=paths,
        device=device,
        gsm=gsm,
        lora=lora,
        selection=selection,
        network=network,
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


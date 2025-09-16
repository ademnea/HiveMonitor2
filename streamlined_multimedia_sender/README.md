# Streamlined Multimedia Sender

A robust, multi-interface communication system for IoT devices that intelligently selects the best available network interface (WiFi, GSM, or LoRa) to transmit multimedia files and sensor data to remote servers.

## Overview

The Streamlined Multimedia Sender is an enhanced replacement for the original `multimedia_capture/send_files_to_server.py` script. It provides intelligent interface selection, comprehensive error handling, retry mechanisms, and detailed logging while maintaining full compatibility with the existing file structure and remote destinations.

## Key Features

- **Multi-Interface Support**: Automatically selects between WiFi, GSM (2G/3G/4G), and LoRa based on connectivity quality
- **Intelligent Interface Selection**: Uses scoring algorithms with hysteresis to prevent interface thrashing
- **Robust Error Handling**: Comprehensive retry mechanisms with exponential backoff
- **File Management**: Handles multiple media types (images, videos, audio, sensor data, vibration data)
- **Logging & Monitoring**: Detailed logging with configurable levels and automatic log rotation
- **Summary Reports**: Generates and uploads transmission summaries for monitoring
- **Configuration Management**: Environment variable-based configuration with sensible defaults

## Architecture

### Core Components

1. **`comms.py`**: Main orchestrator that manages interface selection and file transmission
2. **`sender.py`**: Unified sender that handles SFTP (WiFi/GSM) and LoRa transmission protocols
3. **`wifi.py`**: WiFi interface management and connectivity testing
4. **`gsm.py`**: GSM/cellular interface management via PPP
5. **`lora.py`**: LoRa communication handling
6. **`config.py`**: Configuration management and environment variable handling
7. **`logger.py`**: Centralized logging with rotation and formatting
8. **`utils.py`**: Utility functions for file operations and system tasks
9. **`summary.py`**: Transmission summary generation and reporting

### File Structure Compatibility

The streamlined sender maintains full compatibility with the original multimedia capture system:

**Local Source Directories** (scanned for files to upload):
- `/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/images/` - Camera images
- `/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/videos/` - Video recordings  
- `/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/audios/` - Audio recordings
- `/home/pi/Desktop/HiveMonitor2/parameter_capture/sensor_data/` - Sensor parameter data
- `/home/pi/Desktop/HiveMonitor2/parameter_capture/vibration_sensor/fft_log/` - Vibration analysis data

**Remote Destination**:
- All files uploaded to: `/var/www/html/ademnea_website/public/arriving_hive_media/`

## Installation & Setup

### Prerequisites

1. **Operating System**: 
   - Raspberry Pi Zero 2W: 32-bit legacy (Bullseye) Raspberry Pi OS
   - Raspberry Pi 4: 64-bit legacy (Bullseye) Raspberry Pi OS

2. **Hardware Requirements**:
   - WiFi capability (built-in or USB adapter)
   - GSM/cellular modem (optional, for cellular connectivity)
   - LoRa transceiver (optional, for LoRa communication)

### Installation Steps

1. **Install Python Dependencies**:
    ```bash
    cd streamlined_multimedia_sender
    pip3 install -r requirements.txt
    ```

2. **Install System Packages**:
    ```bash
    sudo apt update
    sudo apt install ppp usb-modeswitch
    ```

3. **Configure Environment**:
    ```bash
    cp .env.example .env
    nano .env
    ```
    Edit the `.env` file with your specific configuration values.

4. **Create Required Directories**:
    ```bash
    mkdir -p logs archives metrics
    ```

5. **Set Up PPP (for GSM)**:
    Configure PPP profile for your GSM modem in `/etc/ppp/peers/mobile`

6. **Test Installation**:
    ```bash
    python3 comms.py
    ```

## Configuration

### Environment Variables

All configuration is managed through environment variables defined in `.env`:

#### Server Configuration
```bash
SERVER_HOST=      # SFTP server hostname/IP
SERVER_SSH_PORT=22                 # SSH port
SERVER_USER=ephrince               # SSH username  
SERVER_PASSWORD=Ephrance@2026      # SSH password
DEST_PATH=/var/www/html/ademnea_website/public/arriving_hive_media  # Remote upload path
```

#### Local Paths
```bash
IMAGE_DIR=/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/images/
VIDEO_DIR=/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/videos/
AUDIO_DIR=/home/pi/Desktop/HiveMonitor2/multimedia_capture/multimedia/audios/
PARAMETER_DIR=/home/pi/Desktop/HiveMonitor2/parameter_capture/sensor_data
VIBRATION_DIR=/home/pi/Desktop/HiveMonitor2/parameter_capture/vibration_sensor/fft_log
```

#### Interface Selection Thresholds
```bash
THRESHOLD_WIFI=0.60               # WiFi selection threshold (0-1)
THRESHOLD_GSM=0.50                # GSM selection threshold (0-1)  
HYSTERESIS_DELTA=0.10             # Prevents interface thrashing
PING_SERVER=      # Server for connectivity testing
```

#### Device Configuration
```bash
DEVICE_ID=pi-zero-2w              # Unique device identifier
WIFI_IFACE=wlan0                  # WiFi interface name
PPP_PROFILE=mobile                # PPP profile name for GSM
```

#### Hardware Interfaces
```bash
GSM_PORT=/dev/serial0             # GSM modem serial port (Pi Zero 2W built-in UART)
GSM_BAUD=9600                     # GSM baud rate
LORA_PORT=/dev/ttyUSB0            # LoRa device serial port  
LORA_BAUD=9600                    # LoRa baud rate
```

**Important Note**: The GSM modem uses `/dev/serial0` (the Raspberry Pi's built-in UART), not `/dev/ttyUSB0`. This is the primary serial port on the Pi Zero 2W GPIO pins.

### Interface Selection Algorithm

The system uses a scoring algorithm to select the optimal interface:

1. **WiFi Scoring**: Based on ping response time and packet loss
2. **GSM Scoring**: Based on signal strength and connection stability  
3. **Hysteresis**: Prevents rapid switching between interfaces
4. **Fallback Logic**: LoRa used when WiFi/GSM scores are below thresholds

## Usage

### Manual Execution
```bash
cd streamlined_multimedia_sender
python3 comms.py
```

### Cron Job Setup
Replace the original file sender cron job:

```bash
crontab -e
```

Add entry (example - every 30 minutes):
```bash
*/30 * * * * cd /home/pi/Desktop/HiveMonitor2/streamlined_multimedia_sender && python3 comms.py >> logs/cron.log 2>&1
```

### Python Integration
```python
from streamlined_multimedia_sender.comms import Comms

# Initialize and run
comms = Comms()
comms.run()
```

## Interface Details

### WiFi Interface
- **Activation**: Uses `nmcli` to manage WiFi connections
- **Testing**: Ping-based connectivity and speed testing
- **Scoring**: Based on response time and packet loss percentage
- **File Transfer**: SFTP over WiFi connection

### GSM Interface  
- **Activation**: PPP dial-up connection via GSM modem on `/dev/serial0`
- **Testing**: AT commands for signal strength, ping tests
- **Scoring**: Signal strength (CSQ) and connection stability
- **File Transfer**: SFTP over PPP connection
- **Hardware**: Uses Raspberry Pi built-in UART (GPIO pins 14/15)
- **Supported Modems**: GSM/3G/4G modules connected to serial0

### LoRa Interface
- **Use Case**: Low-bandwidth text/CSV transmission when other interfaces fail
- **Protocol**: Custom protocol optimized for small data transmission
- **File Types**: Text files, CSV files, small sensor data
- **Hardware**: USB-connected LoRa transceiver on `/dev/ttyUSB0`
- **Limitations**: Not suitable for multimedia files due to bandwidth constraints

## Hardware Setup

### GSM Modem Connection
The GSM modem connects to the Raspberry Pi's built-in UART:
- **TX** → GPIO 14 (Pin 8)
- **RX** → GPIO 15 (Pin 10)  
- **GND** → Ground
- **VCC** → 3.3V or 5V (depending on modem)

Enable the serial interface:
```bash
sudo raspi-config
# Navigate to Interface Options > Serial Port
# Disable login shell over serial: No
# Enable serial port hardware: Yes
```

### LoRa Transceiver Connection
LoRa module connects via USB or USB-to-serial adapter on `/dev/ttyUSB0`.

## Logging & Monitoring

### Log Files
- **Location**: `logs/` directory
- **Rotation**: Automatic rotation at 1MB with 3 backup files
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Log Types
- **Main Log**: `streamlined_sender.log` - All system operations
- **Interface Logs**: Separate logs for WiFi, GSM, LoRa operations
- **Error Logs**: Detailed error traces and troubleshooting information

### Metrics & Summaries
- **Metrics**: Interface performance data in `metrics/` directory
- **Summaries**: Transmission reports uploaded to server
- **Monitoring**: Real-time status and historical performance data

## Troubleshooting

### Common Issues

1. **Permission Errors**:
    ```bash
    sudo chown -R pi:pi /home/pi/Desktop/HiveMonitor2/streamlined_multimedia_sender
    chmod +x comms.py
    ```

2. **GSM Connection Issues**:
    - Check PPP configuration in `/etc/ppp/peers/mobile`
    - Verify serial port access: `ls -l /dev/serial0`
    - Test AT commands: `screen /dev/serial0 9600`
    - Ensure serial is enabled in raspi-config

3. **WiFi Problems**:
    - Check interface status: `ip addr show wlan0`
    - Test connectivity: `ping -c 4
    - Verify NetworkManager: `systemctl status NetworkManager`

4. **LoRa Communication**:
    - Check device permissions: `ls -l /dev/ttyUSB0`
    - Add user to dialout group: `sudo usermod -a -G dialout pi`
    - Test serial communication with minicom

5. **File Transfer Failures**:
    - Verify SSH credentials and server accessibility
    - Check disk space on both local and remote systems
    - Review SFTP server logs

### Debug Mode
Enable detailed debugging:
```bash
LOG_LEVEL=DEBUG python3 comms.py
```

### Log Analysis
Check recent operations:
```bash
tail -f logs/streamlined_sender.log
grep ERROR logs/streamlined_sender.log
```

## Performance Optimization

### Interface Selection Tuning
- Adjust thresholds based on your environment
- Modify hysteresis delta to balance responsiveness vs stability
- Customize ping servers for your geographic location

### File Transfer Optimization
- Batch file transfers to reduce connection overhead
- Implement compression for large files (future enhancement)
- Adjust retry intervals based on network characteristics

### Resource Management
- Monitor disk usage in source directories
- Configure log rotation appropriately
- Optimize cron job frequency based on data generation rate

## Migration from Original Sender

### Compatibility
- **100% compatible** with existing file structure
- **Drop-in replacement** for `send_files_to_server.py`
- **Same remote destination** paths maintained
- **Existing cron jobs** easily adaptable

### Migration Steps
1. Install streamlined sender dependencies
2. Configure `.env` file with existing credentials
3. Test with manual execution
4. Update cron job to call `comms.py` instead of `send_files_to_server.py`
5. Monitor logs for successful operation

### Benefits of Migration
- **Improved Reliability**: Multiple interface options and retry mechanisms
- **Better Monitoring**: Comprehensive logging and reporting
- **Enhanced Error Handling**: Graceful failure recovery
- **Future-Proof**: Extensible architecture for new interfaces/protocols

## Security Considerations

### Credential Management
- Store sensitive credentials in `.env` file only
- Set appropriate file permissions: `chmod 600 .env`
- Consider using SSH keys instead of passwords
- Regularly rotate credentials

### Network Security
- Use VPN connections for enhanced security
- Implement certificate-based authentication where possible
- Monitor connection logs for unusual activity
- Keep system packages updated

## Development & Customization

### Adding New Interfaces
1. Create new interface module (e.g., `satellite.py`)
2. Implement required methods: `activate()`, `deactivate()`, `test_connectivity()`
3. Add scoring logic to `comms.py`
4. Update configuration options

### Custom File Handlers
- Extend `UnifiedSender` class for new protocols
- Add custom file filtering in `comms.py`
- Implement compression or encryption as needed

### Monitoring Extensions
- Add custom metrics collection
- Integrate with external monitoring systems
- Implement alerting mechanisms

## Support & Maintenance

### Regular Maintenance
- Monitor log files for errors and warnings
- Check disk space usage regularly
- Update system packages and dependencies
- Verify time synchronization (critical for timestamps)

### Performance Monitoring
- Track interface selection patterns
- Monitor file transfer success rates
- Analyze transmission times and failures
- Review summary reports for trends

### Version Updates
- Test updates in development environment first
- Backup configuration and logs before updates
- Follow semantic versioning for compatibility
- Document any breaking changes

## License & Credits

This streamlined multimedia sender is part of the Smart Bee Monitor project and maintains compatibility with the original multimedia capture system while providing enhanced reliability and monitoring capabilities.

For support or questions, refer to the main project documentation or contact the development team.
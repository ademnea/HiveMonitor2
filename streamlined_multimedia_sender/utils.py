import socket
import subprocess
import re
import logging
from contextlib import closing
import fcntl
import struct
import array

logger = logging.getLogger(__name__)


def tcp_reachable(host: str, port: int, timeout_sec: float = 2.0) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout_sec)
        try:
            sock.connect((host, port))
            logger.debug(f"TCP connection successful: {host}:{port}")
            return True
        except Exception as e:
            logger.debug(f"TCP connection failed: {host}:{port} - {e}")
            return False


def get_wifi_rssi_dbm(iface: str) -> float:
    """Return RSSI in dBm using `iw` if available, else try `iwconfig`.

    Returns a float (negative dBm) or 0.0 if unknown.
    """
    # Try: iw dev <iface> link
    try:
        logger.debug(f"Getting RSSI for interface {iface} using iw")
        out = subprocess.check_output(["iw", "dev", iface, "link"], stderr=subprocess.STDOUT, text=True, timeout=2)
        m = re.search(r"signal:\s*(-?\d+)\s*dBm", out)
        if m:
            rssi = float(m.group(1))
            logger.debug(f"RSSI from iw: {rssi} dBm")
            return rssi
    except Exception as e:
        logger.debug(f"iw command failed for {iface}: {e}")

    # Fallback: iwconfig <iface>
    try:
        logger.debug(f"Getting RSSI for interface {iface} using iwconfig")
        out = subprocess.check_output(["iwconfig", iface], stderr=subprocess.STDOUT, text=True, timeout=2)
        m = re.search(r"Signal level=\s*(-?\d+)\s*dBm", out)
        if m:
            rssi = float(m.group(1))
            logger.debug(f"RSSI from iwconfig: {rssi} dBm")
            return rssi
    except Exception as e:
        logger.debug(f"iwconfig command failed for {iface}: {e}")

    logger.warning(f"Could not determine RSSI for interface {iface}")
    return 0.0


def ping_host(host: str, count: int = 3, deadline_sec: int = 3) -> tuple[float, float]:
    """Ping host and return (avg_latency_ms, loss_fraction).

    If ping fails, returns (0.0, 1.0).
    """
    logger.debug(f"Pinging {host} with {count} packets")
    try:
        # Linux ping options: -c count, -w deadline
        out = subprocess.check_output(["ping", "-c", str(count), "-w", str(deadline_sec), host], stderr=subprocess.STDOUT, text=True, timeout=deadline_sec + 2)
    except Exception as e:
        logger.debug(f"Ping command failed for {host}: {e}")
        return 0.0, 1.0

    # Parse packet loss
    loss_fraction = 1.0
    m_loss = re.search(r"(\d+)% packet loss", out)
    if m_loss:
        try:
            loss_fraction = float(m_loss.group(1)) / 100.0
        except Exception:
            loss_fraction = 1.0

    # Parse avg latency from rtt line: rtt min/avg/max/mdev = 9.820/10.093/10.615/0.298 ms
    avg_latency_ms = 0.0
    m_rtt = re.search(r"rtt [^=]+=\s*([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms", out)
    if m_rtt:
        try:
            avg_latency_ms = float(m_rtt.group(2))
        except Exception:
            avg_latency_ms = 0.0

    return avg_latency_ms, loss_fraction


def normalize_rssi_dbm_to_unit(rssi_dbm: float, min_dbm: float = -90.0, max_dbm: float = -30.0) -> float:
    """Map RSSI from [min_dbm, max_dbm] to [0,1]. Clamp outside.
    Typical WiFi ranges from -90 (poor) to -30 (excellent).
    """
    if max_dbm <= min_dbm:
        return 0.0
    value = (rssi_dbm - min_dbm) / (max_dbm - min_dbm)
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def normalize_latency_ms_to_unit(avg_ms: float, good_ms: float = 20.0, bad_ms: float = 300.0) -> float:
    """Map latency where lower is better to [0,1]. 1.0 at good_ms or less, 0.0 at bad_ms or more."""
    if avg_ms <= good_ms:
        return 1.0
    if avg_ms >= bad_ms:
        return 0.0
    return 1.0 - (avg_ms - good_ms) / (bad_ms - good_ms)


def normalize_loss_to_unit(loss_fraction: float) -> float:
    """Map packet loss where lower is better to [0,1]."""
    if loss_fraction <= 0.0:
        return 1.0
    if loss_fraction >= 1.0:
        return 0.0
    return 1.0 - loss_fraction


# --- GSM helpers ---

def parse_csq(raw: str) -> int:
    """Parse +CSQ response and return RSSI index 0..31, or -1 if unknown.

    Accepts strings like: '+CSQ: 15,0' or '  +CSQ: 31,99\r\nOK\r\n'.
    """
    m = re.search(r"\+CSQ:\s*(\d+)", raw)
    if not m:
        return -1
    try:
        value = int(m.group(1))
        if 0 <= value <= 31:
            return value
        return -1
    except Exception:
        return -1


def normalize_csq_to_unit(csq_index: int) -> float:
    """Map CSQ index (0..31) to [0,1]; return 0.0 if invalid.

    Note: 0 is worst, 31 is best.
    """
    if csq_index < 0 or csq_index > 31:
        return 0.0
    return csq_index / 31.0


def parse_creg_registered(raw: str) -> bool:
    """Parse +CREG? response and return True if registered (home or roaming).

    Accepts: '+CREG: 0,1' (registered, home) or '+CREG: 0,5' (registered, roaming).
    """
    m = re.search(r"\+CREG:\s*\d+\s*,\s*(\d+)", raw)
    if not m:
        return False
    try:
        status = int(m.group(1))
        return status in (1, 5)
    except Exception:
        return False


def parse_cops_present(raw: str) -> bool:
    """Parse +COPS? response and return True if an operator string appears.

    Example: '+COPS: 0,0,"Safaricom",2'.
    """
    return bool(re.search(r"\+COPS:.*\".+\"", raw))


def iface_has_ipv4(iface: str) -> bool:
    """Return True if the given interface has an IPv4 address assigned.

    Uses SIOCGIFADDR; returns False on any failure. Linux-only.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ifreq = struct.pack('256s', iface[:15].encode('utf-8'))
            fcntl.ioctl(sock.fileno(), 0x8915, ifreq)  # SIOCGIFADDR
            return True
        finally:
            sock.close()
    except Exception:
        return False


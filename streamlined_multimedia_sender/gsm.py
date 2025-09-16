from typing import Dict, Any
import logging
import time
import subprocess

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    print("PySerial not installed. Please install with: pip install pyserial")
    serial = None
    SERIAL_AVAILABLE = False

try:
    from streamlined_multimedia_sender.utils import tcp_reachable, parse_csq, normalize_csq_to_unit, parse_creg_registered, parse_cops_present, iface_has_ipv4
except ImportError:
    from utils import tcp_reachable, parse_csq, normalize_csq_to_unit, parse_creg_registered, parse_cops_present, iface_has_ipv4

logger = logging.getLogger(__name__)


class GSM:
    def __init__(self, port: str, baud: int, ppp_profile: str, 
                 query_read_delay: float = 0.15, query_timeout: float = 2.0) -> None:
        self.port = port
        self.baud = baud
        self.ppp_profile = ppp_profile
        self.query_read_delay = query_read_delay
        self.query_timeout = query_timeout
        logger.debug(f"GSM adapter initialized: port={port}, baud={baud}, ppp_profile={ppp_profile}")

    def _query(self, at: str, read_delay_sec: float = None, timeout_sec: float = None) -> str:
        """Send an AT command and return raw response string; safe failures return empty string."""
        logger.debug(f"GSM AT command: {at.strip()}")
        
        if not SERIAL_AVAILABLE or serial is None:
            logger.warning("PySerial not available - GSM query failed")
            return ""
        
        # Use instance defaults if not provided
        if read_delay_sec is None:
            read_delay_sec = self.query_read_delay
        if timeout_sec is None:
            timeout_sec = self.query_timeout
            
        try:
            with serial.Serial(self.port, self.baud, timeout=timeout_sec) as ser:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                cmd = (at.strip() + "\r").encode("ascii", errors="ignore")
                ser.write(cmd)
                ser.flush()
                time.sleep(read_delay_sec)
                data = ser.read(ser.in_waiting or 128)
                response = data.decode("utf-8", errors="ignore")
                logger.debug(f"GSM AT response: {response.strip()}")
                return response
        except Exception as e:
            logger.warning(f"GSM AT command failed: {e}")
            return ""

    def measure(self, server_host: str, server_port: int) -> Dict[str, float]:
        # Probe modem basics; each step is best-effort.
        logger.debug("Starting GSM measurements")
        
        at_ok = "OK" in self._query("AT")
        logger.debug(f"GSM AT response OK: {at_ok}")
        
        raw_csq = self._query("AT+CSQ") if at_ok else ""
        raw_creg = self._query("AT+CREG?") if at_ok else ""
        raw_cops = self._query("AT+COPS?") if at_ok else ""

        logger.info(f"Raw CSQ: {raw_csq.strip()}")
        logger.info(f"Raw CREG: {raw_creg.strip()}")
        logger.info(f"Raw COPS: {raw_cops.strip()}")

        csq_index = parse_csq(raw_csq)
        csq_norm = normalize_csq_to_unit(csq_index)
        creg_norm = 1.0 if parse_creg_registered(raw_creg) else 0.0
        cops_norm = 1.0 if parse_cops_present(raw_cops) else 0.0
        
        logger.debug(f"GSM signal quality: CSQ={csq_index}, normalized={csq_norm}")
        logger.debug(f"GSM registration: {creg_norm}, operator: {cops_norm}")

        tcp_ok = tcp_reachable(server_host, server_port)
        logger.debug(f"TCP reachability to {server_host}:{server_port}: {tcp_ok}")
        
        measurements = {"csq_norm": csq_norm, "creg_norm": creg_norm, "cops_norm": cops_norm, "tcp_norm": 1.0 if tcp_ok else 0.0}
        logger.info(f"GSM measurements completed: CSQ={csq_index}, reg={creg_norm}, ops={cops_norm}, TCP={tcp_ok}")
        
        return measurements

    def activate(self) -> None:
        # Best-effort: attach GPRS and start PPP profile
        logger.info(f"Activating GSM with PPP profile: {self.ppp_profile}")
        
        try:
            # Try AT attach first (non-fatal if fails)
            logger.debug("Sending AT commands for GPRS attach")
            _ = self._query("AT")
            _ = self._query("AT+CGATT=1")
        except Exception as e:
            logger.warning(f"GSM AT attach failed: {e}")

        try:
            # Start PPP using configured peers profile (e.g., 'mobile')
            if self.ppp_profile:
                logger.debug(f"Starting PPP connection: sudo pon {self.ppp_profile}")
                subprocess.run(["sudo", "pon", self.ppp_profile], check=False, timeout=5)
            else:
                logger.warning("No PPP profile configured")
        except Exception as e:
            logger.warning(f"PPP connection failed: {e}")

        # Briefly wait for ppp0 to have IPv4
        logger.debug("Waiting for ppp0 to obtain IPv4 address")
        for i in range(5):
            if iface_has_ipv4("ppp0"):
                logger.debug(f"ppp0 has IPv4 after {i*0.5 + 0.5} seconds")
                break
            time.sleep(2)
        else:
            logger.warning("ppp0 did not obtain IPv4 address within timeout")
            
        logger.info("GSM activation completed")

    def deactivate(self) -> None:
        # Best-effort: stop PPP and detach GPRS
        logger.info("Deactivating GSM connection")
        
        try:
            if self.ppp_profile:
                logger.debug(f"Stopping PPP connection: sudo poff {self.ppp_profile}")
                subprocess.run(["sudo", "poff", self.ppp_profile], check=False, timeout=5)
        except Exception as e:
            logger.warning(f"PPP disconnect failed: {e}")

        try:
            logger.debug("Sending GPRS detach command")
            _ = self._query("AT")
            _ = self._query("AT+CGATT=0")
        except Exception as e:
            logger.warning(f"GSM GPRS detach failed: {e}")
            
        logger.info("GSM deactivation completed")



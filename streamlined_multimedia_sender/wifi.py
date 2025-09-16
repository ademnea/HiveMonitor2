from typing import Dict
import logging
import subprocess
import time

try:
    from streamlined_multimedia_sender.utils import tcp_reachable, get_wifi_rssi_dbm, ping_host, normalize_rssi_dbm_to_unit, normalize_latency_ms_to_unit, normalize_loss_to_unit
except ImportError:
    from utils import tcp_reachable, get_wifi_rssi_dbm, ping_host, normalize_rssi_dbm_to_unit, normalize_latency_ms_to_unit, normalize_loss_to_unit

logger = logging.getLogger(__name__)


class WiFi:
    def __init__(self, iface: str) -> None:
        self.iface = iface
        logger.debug(f"WiFi adapter initialized for interface: {iface}")

    def measure(self, server_host: str, server_port: int, ping_host_target: str | None = None) -> Dict[str, float]:
        logger.debug(f"Starting WiFi measurements for {self.iface}")
        
        tcp_ok = tcp_reachable(server_host, server_port)
        logger.debug(f"TCP reachability to {server_host}:{server_port}: {tcp_ok}")
        
        rssi_dbm = get_wifi_rssi_dbm(self.iface)
        logger.debug(f"RSSI for {self.iface}: {rssi_dbm} dBm")
        
        target = ping_host_target or server_host
        avg_ms, loss = ping_host(target)
        logger.debug(f"Ping to {target}: {avg_ms}ms avg, {loss}% loss")
        
        measurements = {
            "rssi_norm": normalize_rssi_dbm_to_unit(rssi_dbm),
            "latency_norm": normalize_latency_ms_to_unit(avg_ms),
            "loss_norm": normalize_loss_to_unit(loss),
            "tcp_norm": 1.0 if tcp_ok else 0.0,
        }
        
        logger.info(f"WiFi measurements completed: RSSI={rssi_dbm}dBm, latency={avg_ms}ms, loss={loss}%, TCP={tcp_ok}")
        return measurements

    def activate(self) -> None:
        # Best-effort: rfkill unblock wifi, reconfigure, and wait briefly
        logger.info(f"Activating WiFi interface {self.iface}")
        
        try:
            logger.debug("Unblocking WiFi via rfkill")
            subprocess.run(["rfkill", "unblock", "wifi"], check=False, timeout=3)
        except Exception as e:
            logger.warning(f"Failed to unblock WiFi: {e}")
            
        try:
            logger.debug(f"Reconfiguring WiFi interface {self.iface}")
            subprocess.run(["wpa_cli", "-i", self.iface, "reconfigure"], check=False, timeout=3)
        except Exception as e:
            logger.warning(f"Failed to reconfigure WiFi: {e}")
            
        # Give DHCP a moment
        logger.debug("Waiting 1 second for DHCP")
        time.sleep(1.0)
        logger.info("WiFi activation completed")

    def deactivate(self) -> None:
        logger.info("Deactivating WiFi interface")
        try:
            logger.debug("Blocking WiFi via rfkill")
            subprocess.run(["rfkill", "block", "wifi"], check=False, timeout=3)
            logger.info("WiFi deactivation completed")
        except Exception as e:
            logger.warning(f"Failed to block WiFi: {e}")



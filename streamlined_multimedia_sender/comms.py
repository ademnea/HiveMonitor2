import sys
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Add parent directory to path to allow imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    # Try absolute import first
    from streamlined_multimedia_sender.config import load_config, Config
    from streamlined_multimedia_sender.wifi import WiFi
    from streamlined_multimedia_sender.gsm import GSM
    from streamlined_multimedia_sender.lora import LoRa
    from streamlined_multimedia_sender.logger import get_logger, setup_logging
except ImportError:
    # Fallback to local imports
    try:
        from config import load_config, Config
        from wifi import WiFi
        from gsm import GSM
        from lora import LoRa
        from logger import get_logger, setup_logging
    except ImportError as e:
        print(f"Cannot import required modules: {e}")
        print("Please run from the repository root directory or install as a package")
        sys.exit(1)

# Get a logger for this module
logger = get_logger(__name__)

class Comms:
    """Handles link selection and file sending using a linear flow.

    Sequence: ensure_paths -> measure -> score -> decide -> activate -> send -> summarize
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.chosen_interface: Optional[str] = None  # "wifi" | "gsm" | "lora"
        self.measurements: Dict[str, Dict[str, float]] = {}
        self.scores: Dict[str, float] = {}
        self.run_started_at: datetime = datetime.utcnow()
        # Interface instances
        self.wifi = WiFi(
            self.config.device.wifi_iface,
            command_timeout=self.config.network.wifi_command_timeout,
            activation_delay=self.config.network.wifi_activation_delay
        )
        self.gsm = GSM(
            self.config.gsm.port, 
            self.config.gsm.baud, 
            self.config.device.ppp_profile,
            query_read_delay=self.config.gsm.query_read_delay,
            query_timeout=self.config.gsm.query_timeout
        )
        self.lora = LoRa(
            self.config.lora.port, 
            self.config.lora.baud,
            serial_timeout=self.config.network.lora_serial_timeout,
            command_timeout=self.config.network.lora_command_timeout,
            mock_rssi=self.config.lora.mock_rssi,
            mock_snr=self.config.lora.mock_snr,
            mock_temperature=self.config.lora.mock_temperature,
            max_send_attempts=self.config.lora.max_send_attempts,
            retry_delay=self.config.lora.retry_delay,
            inter_chunk_delay=self.config.lora.inter_chunk_delay
        )
        
        logger.info(f"Comms initialized for device {self.config.device.device_id}")
        logger.debug(f"Interface configuration: WiFi={self.config.device.wifi_iface}, GSM={self.config.gsm.port}, LoRa={self.config.lora.port}")

    def run(self) -> int:
        """Execute a single decision-and-send cycle in a straight-line."""
        logger.info("Starting communication run")
        
        self._ensure_paths()
        logger.debug("Directory paths ensured")
        
        self.measurements = self._measure_connectivity()
        logger.info(f"Connectivity measurements: {self.measurements}")
        
        self.scores = self._compute_scores(self.measurements)
        logger.info(f"Interface scores: {self.scores}")
        
        self.chosen_interface, self.choice_reason = self._decide_interface(self.scores)
        logger.info(f"Selected interface: {self.chosen_interface} - {self.choice_reason}")
        
        self._activate_interface(self.chosen_interface)
        logger.debug(f"Interface {self.chosen_interface} activated")
        
        self._send_files()
        logger.debug("File sending completed")
        
        self._write_summary()
        logger.info("Summary written and upload attempted")

        # If GSM was used, deactivate GSM and reactivate WiFi
        if self.chosen_interface == "gsm":
            try:
                self.gsm.deactivate()
                logger.info("GSM deactivated after summary upload")
            except Exception as e:
                logger.warning(f"Failed to deactivate GSM: {e}")
            try:
                self.wifi.activate()
                logger.info("WiFi reactivated after GSM deactivation")
            except Exception as e:
                logger.warning(f"Failed to reactivate WiFi: {e}")

        logger.info("Communication run completed successfully")
        return 0


    def _ensure_paths(self) -> None:
        Path(self.config.paths.archive_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.paths.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.paths.metrics_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directories: {self.config.paths.archive_dir}, {self.config.paths.log_dir}, {self.config.paths.metrics_dir}")

    def _measure_connectivity(self) -> Dict[str, Dict[str, float]]:
        """Collect measurements from WiFi, GSM, and LoRa adapters (placeholders for now)."""
        logger.debug("Starting connectivity measurements")
        
        measurements = {
            "wifi": self.wifi.measure(self.config.server.host, self.config.server.port, self.config.selection.ping_server),
            "gsm": self.gsm.measure(self.config.server.host, self.config.server.port),
            "lora": self.lora.measure(),
        }
        
        logger.debug(f"Raw measurements: {measurements}")
        return measurements

    def _compute_scores(self, measurements: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Compute interface scores using planned weights. Normalized inputs expected in [0,1]."""
        wifi_m = measurements.get("wifi", {})
        gsm_m = measurements.get("gsm", {})
        lora_m = measurements.get("lora", {})

        # Log component values at INFO level
        logger.info(f"WiFi components: RSSI={wifi_m.get('rssi_norm', 0.0):.3f}, Latency={wifi_m.get('latency_norm', 0.0):.3f}, "
                   f"Loss={wifi_m.get('loss_norm', 0.0):.3f}, TCP={wifi_m.get('tcp_norm', 0.0):.3f}")
        logger.info(f"GSM components: CSQ={gsm_m.get('csq_norm', 0.0):.3f}, CREG={gsm_m.get('creg_norm', 0.0):.3f}, "
                   f"COPS={gsm_m.get('cops_norm', 0.0):.3f}, TCP={gsm_m.get('tcp_norm', 0.0):.3f}")

        wifi_score = (
            self.config.selection.wifi_rssi_weight * wifi_m.get("rssi_norm", 0.0)
            + self.config.selection.wifi_latency_weight * wifi_m.get("latency_norm", 0.0)
            + self.config.selection.wifi_loss_weight * wifi_m.get("loss_norm", 0.0)
            + self.config.selection.wifi_tcp_weight * wifi_m.get("tcp_norm", 0.0)
        )

        gsm_score = (
            self.config.selection.gsm_csq_weight * gsm_m.get("csq_norm", 0.0)
            + self.config.selection.gsm_creg_weight * gsm_m.get("creg_norm", 0.0)
            + self.config.selection.gsm_cops_weight * gsm_m.get("cops_norm", 0.0)
            + self.config.selection.gsm_tcp_weight * gsm_m.get("tcp_norm", 0.0)
        )

        lora_score = 1.0  # Always set to 1.0 to bypass availability check

        scores = {"wifi": wifi_score, "gsm": gsm_score, "lora": lora_score}
        logger.info(f"Computed scores: WiFi={wifi_score:.3f}, GSM={gsm_score:.3f}, LoRa={lora_score:.3f}")
        
        return scores

    def _decide_interface(self, scores: Dict[str, float]) -> Tuple[str, str]:
        """Choose interface based on thresholds. Returns (choice, reason)."""
        wifi_th = self.config.selection.threshold_wifi
        gsm_th = self.config.selection.threshold_gsm

        wifi_score = scores.get("wifi", 0.0)
        gsm_score = scores.get("gsm", 0.0)
        lora_score = scores.get("lora", 0.0)

        # Store decision details for summary
        self._decision_details = {
            "thresholds": {"wifi": wifi_th, "gsm": gsm_th},
        }
        
        # Log the thresholds at INFO level
        logger.info(f"Decision thresholds: WiFi={wifi_th}, GSM={gsm_th}")

        # Make choice by thresholds
        if wifi_score >= wifi_th:
            choice, score = "wifi", wifi_score
            logger.info(f"WiFi score {wifi_score:.3f} >= threshold {wifi_th}, selecting WiFi")
        elif gsm_score >= gsm_th:
            choice, score = "gsm", gsm_score
            logger.info(f"GSM score {gsm_score:.3f} >= threshold {gsm_th}, selecting GSM")
        else:
            choice, score = "lora", lora_score
            logger.info(f"WiFi and GSM scores below thresholds, selecting LoRa as fallback")

        reason = f"choice={choice} score={score:.3f} (wifi={wifi_score:.3f}, gsm={gsm_score:.3f}, lora={lora_score:.3f})"
        logger.info(f"Interface decision: {reason}")
        return choice, reason

    def _activate_interface(self, choice: Optional[str]) -> None:
        """Activate chosen interface and deactivate others (placeholders)."""
        logger.info(f"Activating selected interface: {choice}")
        
        # Deactivate all first
        for iface_name, iface in [("wifi", self.wifi), ("gsm", self.gsm), ("lora", self.lora)]:
            try:
                iface.deactivate()
                logger.info(f"Deactivated {iface_name}")
            except Exception as e:
                logger.warning(f"Failed to deactivate {iface_name}: {e}")

        if choice == "wifi":
            try:
                self.wifi.activate()
                logger.info("WiFi activated successfully")
            except Exception as e:
                logger.error(f"Failed to activate WiFi: {e}")
        elif choice == "gsm":
            try:
                self.gsm.activate()
                logger.info("GSM activated successfully")
            except Exception as e:
                logger.error(f"Failed to activate GSM: {e}")
        elif choice == "lora":
            try:
                self.lora.activate()
                logger.info("LoRa activated successfully")
            except Exception as e:
                logger.error(f"Failed to activate LoRa: {e}")
        else:
            logger.warning(f"Unknown interface choice: {choice}")

    def _send_files(self) -> None:
        """Use unified sender for WiFi/GSM; LoRa path will be minimal later."""
        try:
            from streamlined_multimedia_sender.sender import UnifiedSender
        except ImportError:
            from sender import UnifiedSender
        
        # Gather files from all source directories
        source_dirs = [
            Path(self.config.paths.image_dir),
            Path(self.config.paths.video_dir),
            Path(self.config.paths.audio_dir),
            Path(self.config.paths.parameter_dir),
            Path(self.config.paths.vibration_dir)
        ]
        
        files = []
        for src_dir in source_dirs:
            if src_dir.exists():
                files.extend([p for p in src_dir.glob("*") if p.is_file()])
            else:
                logger.warning(f"Source directory does not exist: {src_dir}")
        
        files = sorted(files)
        logger.info(f"Found {len(files)} files to send: {[f.name for f in files]}")

        if self.chosen_interface == "lora":
            # Minimal LoRa path: send only .txt files via LoRa
            logger.info("Using LoRa sender for text/CSV files")
            lora = self.lora
            archive_root = Path(self.config.paths.archive_dir) / datetime.utcnow().strftime("%d_%m_%Y")
            
            # Send text files from all source directories
            all_results = []
            for src_dir in source_dirs:
                if src_dir.exists():
                    results = lora.send_text_files(str(src_dir), archive_dir=str(archive_root))
                    all_results.extend(results)
            
            logger.info(f"LoRa send results: {len(all_results)} files processed")
            
            # Map results to FileSummary-like dict, but keep in _last_send_results structure used below
            mapped = []
            for r in all_results:
                try:
                    from streamlined_multimedia_sender.sender import SendResult
                except ImportError:
                    from sender import SendResult
                    
                mapped.append(
                    SendResult(
                        src_path=Path(r.get("path", "")),
                        status=str(r.get("status", "failed")),
                        bytes_sent=int(r.get("bytes_sent", 0)),
                        attempts=int(r.get("attempts", 0)),
                        send_period=float(r.get("send_period", 0.0)),
                        throughput=float(r.get("throughput", 0.0)),
                        archived_path=Path(r.get("archived_path")) if r.get("archived_path") else None,
                        error=str(r.get("error")) if r.get("error") else None,
                    )
                )
            self._last_send_results = mapped  # type: ignore[attr-defined]
            return

        logger.info(f"Using unified SFTP sender via {self.chosen_interface}")
        sender = UnifiedSender(
            host=self.config.server.host,
            port=self.config.server.port,
            username=self.config.server.username,
            password=self.config.server.password,
            dest_path=self.config.server.dest_path,
            max_retries=self.config.network.max_retries,
            base_delay=self.config.network.base_delay,
            connection_timeout=self.config.network.ssh_connection_timeout,
            auth_timeout=self.config.network.ssh_auth_timeout,
        )
        archive_root = Path(self.config.paths.archive_dir) / datetime.utcnow().strftime("%d_%m_%Y")
        self._last_send_results = sender.send_files(files, archive_dir=archive_root)  # type: ignore[attr-defined]
        
        successful = sum(1 for r in self._last_send_results if r.status == "success")
        logger.info(f"SFTP send completed: {successful}/{len(files)} files successful")

    def _write_summary(self) -> None:
        """Write JSONL + TSV summary for this run and attempt to upload via active link."""
        try:
            from streamlined_multimedia_sender.summary import SummaryWriter, RunSummary, FileSummary
        except ImportError:
            from summary import SummaryWriter, RunSummary, FileSummary
            
        out_dir = Path(self.config.paths.metrics_dir) / "summary"
        files = []
        for r in getattr(self, "_last_send_results", []):  # type: ignore[attr-defined]
            files.append(
                FileSummary(
                    path=str(r.src_path),
                    status=r.status,
                    bytes_sent=r.bytes_sent,
                    attempts=r.attempts,
                    file_size=getattr(r, 'file_size', r.bytes_sent) if hasattr(r, 'file_size') or hasattr(r, 'bytes_sent') else 0,
                    send_period=getattr(r, 'send_period', 0.0),
                    throughput=getattr(r, 'throughput', 0.0),
                    archived_path=str(r.archived_path) if r.archived_path else "",
                )
            )
        summary = RunSummary(
            device_id=self.config.device.device_id,
            started_at=self.run_started_at.isoformat() + "Z",
            choice=self.chosen_interface or "",
            choice_reason=getattr(self, 'choice_reason', ''),
            scores=self.scores,
            thresholds=getattr(self, '_decision_details', {}).get('thresholds', {}),
            measurements=self.measurements,
            files=files,
        )
        
        # Write summary files locally
        summary_files = SummaryWriter(out_dir).write(summary)
        
        # Attempt to upload summary files via active link
        self._upload_summary_files(summary_files)

    def _upload_summary_files(self, summary_files: Dict[str, Path]) -> None:
        """Attempt to upload summary files via the active interface."""
        if not self.chosen_interface:
            # No interface chosen, keep files local
            logger.info(f"Summary files saved locally (interface={self.chosen_interface}): {list(summary_files.values())}")
            return
            
        if self.chosen_interface == "lora":
            # Use LoRa to send summary files, with status on fPort 2 and files on fPort 1
            logger.info(f"Sending summary files via LoRa: {list(summary_files.values())}")
            try:
                # Send status data on fPort 2 and then files on fPort 1
                results = self.lora.send_summary_data(summary_files)
                
                if results.get("status") == "success":
                    # Get file results from the returned dictionary
                    file_results = results.get("file_results", [])
                    successful = sum(1 for r in file_results if r.get("status") == "success")
                    logger.info(f"LoRa summary status sent on fPort 2, file upload completed: {successful}/{len(file_results)} files successful")
                else:
                    logger.warning(f"Failed to send summary status: {results.get('error', 'unknown error')}")
                    
                    # Fallback to just sending the files if status sending failed
                    logger.info("Falling back to sending summary files only on fPort 1")
                    summary_dir = next(iter(summary_files.values())).parent
                    archive_root = Path(self.config.paths.archive_dir) / "summary" / datetime.utcnow().strftime("%d_%m_%Y")
                    file_results = self.lora.send_text_files(str(summary_dir), archive_dir=str(archive_root))
                    
                    successful = sum(1 for r in file_results if r.get("status") == "success")
                    logger.info(f"LoRa summary file upload completed: {successful}/{len(file_results)} files successful")
                    
            except Exception as e:
                logger.error(f"Failed to send summary files via LoRa: {e}")
                logger.info(f"Summary files saved locally: {list(summary_files.values())}")
            return
            
        # For WiFi/GSM, use unified sender to upload summary files
        try:
            logger.debug(f"Attempting to upload summary files via {self.chosen_interface}")
            try:
                from streamlined_multimedia_sender.sender import UnifiedSender
            except ImportError:
                from sender import UnifiedSender
                
            sender = UnifiedSender(
                host=self.config.server.host,
                port=self.config.server.port,
                username=self.config.server.username,
                password=self.config.server.password,
                dest_path=f"{self.config.server.dest_path}/summary/{datetime.utcnow().strftime('%d_%m_%Y')}",
                max_retries=self.config.network.max_retries,
                base_delay=self.config.network.base_delay,
                connection_timeout=self.config.network.ssh_connection_timeout,
                auth_timeout=self.config.network.ssh_auth_timeout,
            )
            
            # Convert summary file paths to list
            files_to_upload = list(summary_files.values())
            
            # Upload without archiving (summary files are already timestamped)
            upload_results = sender.send_files(files_to_upload, archive_dir=None)
            
            # Log results
            successful_uploads = 0
            for result in upload_results:
                if result.status == "success":
                    successful_uploads += 1
                    logger.info(f"Summary uploaded: {result.src_path.name} ({result.bytes_sent} bytes)")
                else:
                    logger.warning(f"Summary upload failed: {result.src_path.name} - {result.error}")
            
            logger.info(f"Summary upload completed: {successful_uploads}/{len(upload_results)} files successful")
                    
        except Exception as e:
            logger.error(f"Failed to upload summary files via {self.chosen_interface}: {e}")
            logger.info(f"Summary files saved locally: {list(summary_files.values())}")


def main() -> int:
    config = load_config()
    
    # Set up logging
    setup_logging(config.paths.log_dir, config.logging)
    logger = get_logger(__name__)
    
    try:
        logger.info("=== Arthur IoTRA Communication System Starting ===")
        comms = Comms(config)
        result = comms.run()
        logger.info("=== Arthur IoTRA Communication System Completed ===")
        return result
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())



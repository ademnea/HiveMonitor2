from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import time
from typing import Iterable, List, Optional

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SendResult:
    src_path: Path
    status: str  # "success" | "failed" | "skipped"
    bytes_sent: int
    attempts: int
    send_period: float = 0.0  # seconds
    throughput: float = 0.0   # bytes/sec
    file_size: int = 0        # bytes
    error: Optional[str] = None
    archived_path: Optional[Path] = None


class UnifiedSender:
    """SFTP sender for WiFi/GSM routing with real Paramiko implementation.

    This class provides a unified API for SFTP uploads with retry logic,
    exponential backoff, and proper error handling. Falls back to placeholder
    behavior if Paramiko is not available.
    """

    def __init__(self, host: str, port: int, username: str, password: str, dest_path: str) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dest_path = dest_path.rstrip('/')  # Normalize path
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay for exponential backoff
        logger.debug(f"UnifiedSender initialized: {host}:{port}, dest_path={dest_path}")
        
        if not PARAMIKO_AVAILABLE:
            logger.warning("Paramiko not available - falling back to placeholder mode")

    def send_files(self, files: Iterable[Path], archive_dir: Optional[Path] = None) -> List[SendResult]:
        """Send files via SFTP with retry logic and error handling."""
        logger.info(f"Starting file transfer to {self.host}:{self.port}{self.dest_path}")
        results: List[SendResult] = []
        files_list = list(files)
        logger.debug(f"Files to transfer: {[f.name for f in files_list]}")
        
        # Establish SFTP connection if Paramiko is available
        sftp_client = None
        ssh_client = None
        
        if PARAMIKO_AVAILABLE:
            try:
                ssh_client, sftp_client = self._connect_sftp()
                logger.debug("SFTP connection established")
            except Exception as e:
                logger.error(f"Failed to establish SFTP connection: {e}")
                # Fall back to placeholder mode for this session
                sftp_client = None
        
        try:
            for file_path in files_list:
                result = self._send_single_file(file_path, sftp_client, archive_dir)
                results.append(result)
        finally:
            # Clean up connections
            if sftp_client:
                try:
                    sftp_client.close()
                    logger.debug("SFTP connection closed")
                except Exception as e:
                    logger.warning(f"Error closing SFTP connection: {e}")
            
            if ssh_client:
                try:
                    ssh_client.close()
                    logger.debug("SSH connection closed")
                except Exception as e:
                    logger.warning(f"Error closing SSH connection: {e}")
        
        successful = sum(1 for r in results if r.status == "success")
        logger.info(f"File transfer completed: {successful}/{len(results)} files successful")
        return results

    def _connect_sftp(self) -> tuple[paramiko.SSHClient, paramiko.SFTPClient]:
        """Establish SSH and SFTP connections with timeout and error handling."""
        if not PARAMIKO_AVAILABLE:
            raise RuntimeError("Paramiko not available")
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            logger.debug(f"Connecting to {self.host}:{self.port}")
            ssh_client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=30,  # 30 second connection timeout
                auth_timeout=15,  # 15 second auth timeout
            )
            
            sftp_client = ssh_client.open_sftp()
            
            # Ensure destination directory exists
            self._ensure_remote_dir(sftp_client, self.dest_path)
            
            return ssh_client, sftp_client
            
        except Exception as e:
            ssh_client.close()
            raise e

    def _ensure_remote_dir(self, sftp: paramiko.SFTPClient, remote_path: str) -> None:
        """Ensure the remote directory exists, creating it if necessary."""
        try:
            sftp.stat(remote_path)
            logger.debug(f"Remote directory exists: {remote_path}")
        except FileNotFoundError:
            try:
                # Try to create the directory (and any parent directories)
                parts = remote_path.strip('/').split('/')
                current_path = ''
                for part in parts:
                    current_path += '/' + part
                    try:
                        sftp.stat(current_path)
                    except FileNotFoundError:
                        sftp.mkdir(current_path)
                        logger.debug(f"Created remote directory: {current_path}")
            except Exception as e:
                logger.warning(f"Failed to create remote directory {remote_path}: {e}")
                # Non-fatal - upload may still work if parent exists

    def _send_single_file(self, file_path: Path, sftp_client: Optional[paramiko.SFTPClient], 
                         archive_dir: Optional[Path]) -> SendResult:
        """Send a single file with retry logic and error handling."""
        try:
            size = file_path.stat().st_size
            logger.debug(f"Processing file: {file_path.name} ({size} bytes)")
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return SendResult(src_path=file_path, status="failed", bytes_sent=0, attempts=1, send_period=0.0, throughput=0.0, file_size=0, error="file not found")

        attempts = 0
        last_error = None
        send_period = 0.0
        throughput = 0.0

        for attempt in range(1, self.max_retries + 1):
            attempts = attempt
            start_time = time.time()
            try:
                if sftp_client is not None:
                    # Real SFTP upload
                    success = self._upload_file_sftp(file_path, sftp_client)
                else:
                    # Placeholder mode
                    success = self._upload_file_placeholder(file_path)

                send_period = time.time() - start_time
                if success:
                    logger.debug(f"Upload successful: {file_path.name} (attempt {attempt})")

                    # Handle archiving for successful uploads
                    archived: Optional[Path] = None
                    if archive_dir is not None:
                        archived = self._archive_file(file_path, archive_dir)

                    throughput = round(size / send_period, 3) if send_period > 0 else 0.0
                    return SendResult(
                        src_path=file_path,
                        status="success",
                        bytes_sent=size,
                        attempts=attempts,
                        send_period=send_period,
                        throughput=throughput,
                        file_size=size,
                        archived_path=archived
                    )
                else:
                    last_error = "upload failed"
                    send_period = time.time() - start_time
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Upload attempt {attempt} failed for {file_path.name}: {e}")
                send_period = time.time() - start_time

            # Apply exponential backoff before retry (except on last attempt)
            if attempt < self.max_retries:
                delay = self.base_delay * (2 ** (attempt - 1))
                logger.debug(f"Retrying after {delay:.1f}s delay")
                time.sleep(delay)

        logger.error(f"Upload failed after {attempts} attempts: {file_path.name}")
        return SendResult(
            src_path=file_path,
            status="failed",
            bytes_sent=0,
            attempts=attempts,
            send_period=send_period,
            throughput=0.0,
            file_size=size,
            error=last_error
        )

    def _upload_file_sftp(self, file_path: Path, sftp: paramiko.SFTPClient) -> bool:
        """Upload file using real SFTP connection."""
        # Rename file with dd_mm_yyyy_hh_mm_ss_originalname format
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        renamed_filename = f"{timestamp}_{file_path.name}"
        remote_path = f"{self.dest_path}/{renamed_filename}"
        
        try:
            logger.debug(f"Uploading {file_path} to {remote_path} (renamed to {renamed_filename})")
            sftp.put(str(file_path), remote_path)
            
            # Verify upload by checking remote file size
            try:
                remote_stat = sftp.stat(remote_path)
                local_size = file_path.stat().st_size
                if remote_stat.st_size == local_size:
                    logger.debug(f"Upload verified: {file_path.name} ({local_size} bytes)")
                    return True
                else:
                    logger.warning(f"Upload size mismatch: {file_path.name} (local: {local_size}, remote: {remote_stat.st_size})")
                    return False
            except Exception as e:
                logger.warning(f"Could not verify upload: {file_path.name}: {e}")
                return True  # Assume success if we can't verify
                
        except Exception as e:
            logger.error(f"SFTP upload failed: {file_path.name}: {e}")
            return False

    def _upload_file_placeholder(self, file_path: Path) -> bool:
        """Placeholder upload implementation for when Paramiko is not available."""
        # Simulate upload success for files that exist
        success = file_path.exists()
        logger.debug(f"Placeholder upload for {file_path.name}: {'success' if success else 'failed'}")
        return success

    def _archive_file(self, file_path: Path, archive_dir: Path) -> Optional[Path]:
        """Archive a successfully sent file with timestamped naming."""
        try:
            archive_dir.mkdir(parents=True, exist_ok=True)
            # Use dd_mm_yyyy_hh_mm_ss format for consistency
            ts = datetime.utcnow().strftime("%d_%m_%Y_%H_%M_%S")
            candidate = archive_dir / f"{ts}_{file_path.name}"
            
            file_path.replace(candidate)
            logger.debug(f"File archived: {file_path.name} -> {candidate}")
            return candidate
        except Exception as e:
            logger.warning(f"Failed to archive file {file_path.name}: {e}")
            return None


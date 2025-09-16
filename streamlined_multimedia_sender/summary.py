from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List

logger = logging.getLogger(__name__)


@dataclass
class FileSummary:
    path: str
    status: str
    bytes_sent: int
    attempts: int
    file_size: int
    send_period: float  # seconds
    throughput: float   # bytes/sec
    archived_path: str = ""


@dataclass
class RunSummary:
    device_id: str
    started_at: str
    choice: str
    choice_reason: str
    scores: Dict[str, float]
    thresholds: Dict[str, float]
    measurements: Dict[str, Dict[str, float]]
    files: List[FileSummary]
    hysteresis_applied: bool = False
    previous_choice: str = ""


class SummaryWriter:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = out_dir
        logger.debug(f"SummaryWriter initialized: {out_dir}")

    def write(self, summary: RunSummary) -> Dict[str, Path]:
        logger.info(f"Writing summary for device {summary.device_id}, network used: {summary.choice}, reason: {summary.choice_reason}")

        self.out_dir.mkdir(parents=True, exist_ok=True)
        # Use dd_mm_yyyy_hh_mm_ss format for consistency
        ts = datetime.utcnow().strftime("%d_%m_%Y_%H_%M_%S")
        jsonl_path = self.out_dir / f"summary_{ts}.jsonl"
        tsv_path = self.out_dir / f"summary_{ts}.tsv"

        # JSONL (one object per line)
        import json

        # Custom JSON encoder to round floats to 3dp
        class RoundingEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, float):
                    return round(obj, 3)
                return super().default(obj)

        try:
            with jsonl_path.open("a", encoding="utf-8") as jf:
                jf.write(json.dumps(asdict(summary), ensure_ascii=False, cls=RoundingEncoder) + "\n")
            logger.debug(f"JSONL summary written: {jsonl_path}")
        except Exception as e:
            logger.error(f"Failed to write JSONL summary: {e}")

        # TSV (header + rows)
        header = [
            "device_id", "started_at", "network_used", "network_reason", "wifi_score", "gsm_score", "lora_score",
            "hysteresis_applied", "previous_choice", "path", "file_size", "send_period", "throughput", "status", "bytes_sent", "attempts", "archived_path"
        ]

        try:
            if not tsv_path.exists():
                with tsv_path.open("w", encoding="utf-8") as tf:
                    tf.write("\t".join(header) + "\n")
                logger.debug(f"TSV header written: {tsv_path}")

            with tsv_path.open("a", encoding="utf-8") as tf:
                # Write one row per file with run-level details repeated
                for f in summary.files:
                    row = [
                        summary.device_id,
                        summary.started_at,
                        summary.choice,
                        summary.choice_reason,
                        f"{summary.scores.get('wifi', 0.0):.3f}",
                        f"{summary.scores.get('gsm', 0.0):.3f}",
                        f"{summary.scores.get('lora', 0.0):.3f}",
                        str(summary.hysteresis_applied),
                        summary.previous_choice,
                        f.path,
                        str(f.file_size),
                        f"{f.send_period:.3f}",
                        f"{f.throughput:.3f}",
                        f.status,
                        str(f.bytes_sent),
                        str(f.attempts),
                        f.archived_path
                    ]
                    tf.write("\t".join(row) + "\n")
            logger.debug(f"TSV summary written: {tsv_path} ({len(summary.files)} rows)")
        except Exception as e:
            logger.error(f"Failed to write TSV summary: {e}")

        logger.info(f"Summary files created: {jsonl_path.name}, {tsv_path.name}")
        return {"jsonl": jsonl_path, "tsv": tsv_path}


from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class EventLogger:
    """A tiny JSONL timeline logger.

    The intent is to eventually power a Studio timeline UI ("time travel" debugging).
    """

    path: Path

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event_type: str, **fields: Any) -> None:
        rec = {"ts": time.time(), "type": event_type, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def make_default_eventlog_path(log_dir: Path, run_id: str) -> Path:
    return log_dir / f"run_{run_id}.jsonl"

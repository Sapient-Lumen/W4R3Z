from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class StateStore:
    root: Path
    events_path: Path = field(init=False)
    latest_dir: Path = field(init=False)
    run_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.events_path = self.root / "events.jsonl"
        self.latest_dir = self.root / "latest"
        self.run_dir = self.root.parent / "run"
        self.latest_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def append_event(self, event: dict[str, Any]) -> None:
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def write_latest(self, name: str, payload: dict[str, Any]) -> None:
        target = self.latest_dir / f"{name}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def read_latest(self, name: str) -> dict[str, Any] | None:
        target = self.latest_dir / f"{name}.json"
        if not target.exists():
            return None
        return json.loads(target.read_text(encoding="utf-8"))

    def status(self) -> dict[str, Any]:
        event_count = 0
        if self.events_path.exists():
            event_count = len(self.events_path.read_text(encoding="utf-8").splitlines())
        return {
            "state_root": str(self.root),
            "events_path": str(self.events_path),
            "event_count": event_count,
            "run_dir": str(self.run_dir),
        }

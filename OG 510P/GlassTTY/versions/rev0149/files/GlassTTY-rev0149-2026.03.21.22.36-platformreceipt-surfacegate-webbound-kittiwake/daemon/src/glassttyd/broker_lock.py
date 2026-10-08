from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - GlassTTY currently targets Linux/macOS for native-host work.
    fcntl = None  # type: ignore[assignment]

JsonDict = dict[str, Any]


class BrokerOwnershipLease:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.lock_path = run_dir / 'daemon-broker.lock'
        self.metadata_path = run_dir / 'daemon-broker-owner.json'
        self._handle = None
        self.acquired = False

    def try_acquire(self, metadata: JsonDict) -> bool:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        handle = self.lock_path.open('a+', encoding='utf-8')
        if fcntl is None:
            self._handle = handle
            self.acquired = True
            self.write_metadata(metadata)
            return True
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._handle = handle
            self.acquired = False
            return False
        self._handle = handle
        self.acquired = True
        self.write_metadata(metadata)
        return True

    def write_metadata(self, metadata: JsonDict) -> None:
        self.metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def read_metadata(self) -> JsonDict | None:
        if not self.metadata_path.exists():
            return None
        return json.loads(self.metadata_path.read_text(encoding='utf-8'))

    def release(self) -> None:
        if self.acquired:
            try:
                if self.metadata_path.exists():
                    self.metadata_path.unlink()
            except FileNotFoundError:
                pass
            if self._handle is not None and fcntl is not None:
                try:
                    fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
        if self._handle is not None:
            self._handle.close()
            self._handle = None
        self.acquired = False

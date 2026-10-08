#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_index import write_evidence_index


def main() -> None:
    summary = write_evidence_index(
        ROOT,
        json_path=ROOT / "data" / "rev0069_evidence_index.json",
        csv_path=ROOT / "data" / "rev0069_evidence_index.csv",
        min_bytes=1024 * 1024,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

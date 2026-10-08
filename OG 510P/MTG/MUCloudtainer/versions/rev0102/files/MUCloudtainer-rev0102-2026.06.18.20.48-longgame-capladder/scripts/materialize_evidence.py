#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import materialize_evidence_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize selected or all cold evidence from the immutable sidecar.")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--catalog", type=Path, help="Optional evidence-tier catalog path; defaults to the newest data/rev*_evidence_tiering_catalog.json")
    args = parser.parse_args()
    result = materialize_evidence_bundle(
        args.root,
        args.bundle,
        selected_paths=args.paths or None,
        catalog_path=args.catalog,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

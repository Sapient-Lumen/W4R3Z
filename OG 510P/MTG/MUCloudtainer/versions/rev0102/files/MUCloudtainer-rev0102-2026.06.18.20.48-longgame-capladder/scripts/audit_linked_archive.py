#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.archive_contract import audit_linked_archive, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit linked ZIP compression, integrity, identity, and size budget.")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-root")
    parser.add_argument("--max-mib", type=float, default=64.0)
    args = parser.parse_args()
    report = audit_linked_archive(
        args.archive,
        expected_root=args.expected_root,
        max_archive_bytes=int(args.max_mib * 1024 * 1024),
    )
    print(json.dumps({"archive": report.as_dict(), "sha256": sha256_file(args.archive)}, indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.package_contract import audit_package_contract


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit semantic and byte-level package integrity.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--skip-checksums", action="store_true")
    parser.add_argument("--allow-generated-artifacts", action="store_true")
    args = parser.parse_args()

    report = audit_package_contract(
        args.root,
        verify_checksums=not args.skip_checksums,
        check_forbidden=not args.allow_generated_artifacts,
    )
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

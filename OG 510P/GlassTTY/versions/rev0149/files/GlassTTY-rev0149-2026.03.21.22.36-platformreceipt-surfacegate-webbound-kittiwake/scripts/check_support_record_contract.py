#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from support_records import load_support_records, validate_support_records

ROOT = Path(__file__).resolve().parent.parent


def build_contract_report(*, root: Path = ROOT) -> dict:
    records = load_support_records(root=root)
    return {
        'project': 'GlassTTY',
        'root': str(root),
        **validate_support_records(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate GlassTTY support-record contract conformance.')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    payload = build_contract_report()
    print(json.dumps(payload, indent=2 if args.pretty else None))
    if not payload.get('all_valid'):
        sys.exit(1)


if __name__ == '__main__':
    main()

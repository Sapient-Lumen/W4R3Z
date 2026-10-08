#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from support_bundle_queue import build_support_bundle_queue, capture_support_bundle_queue

ROOT = Path(__file__).resolve().parent.parent
REPORT_COMMAND = 'python scripts/check-support-bundle-contract.py --pretty'
WRITE_ROOT_COMMAND = 'python scripts/check-support-bundle-contract.py write-root'


def build_contract_report(*, root: Path = ROOT) -> dict[str, Any]:
    queue = build_support_bundle_queue(root=root)
    bundles = queue.get('bundles') or []
    return {
        'project': 'GlassTTY',
        'generated_at': queue.get('generated_at'),
        'bundle_count': len(bundles),
        'valid_bundle_count': sum(1 for item in bundles if item.get('ok')),
        'invalid_bundle_count': sum(1 for item in bundles if not item.get('ok')),
        'all_valid': all(item.get('ok') for item in bundles) if bundles else True,
        'warnings': queue.get('warnings') or [],
        'bundle_summaries': [
            {
                'bundle_key': item.get('bundle_key'),
                'bundle_status': item.get('bundle_status'),
                'surface_key': item.get('surface_key'),
                'ok': item.get('ok'),
                'issues': item.get('issues') or [],
            }
            for item in bundles
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': 'python scripts/support-bundle-queue.py capture --output-dir validation/latest/support-bundle-queue',
            'write_root': WRITE_ROOT_COMMAND,
        },
    }


def write_root_conformance(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_contract_report(root=root)
    path = root / 'SUPPORT-BUNDLE-CONTRACT.json'
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate support bundle manifests and summarize queue contract health.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('write-root', help='Write SUPPORT-BUNDLE-CONTRACT.json in the repo root.')
    args = parser.parse_args()
    if args.command == 'write-root':
        payload = write_root_conformance(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_contract_report(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

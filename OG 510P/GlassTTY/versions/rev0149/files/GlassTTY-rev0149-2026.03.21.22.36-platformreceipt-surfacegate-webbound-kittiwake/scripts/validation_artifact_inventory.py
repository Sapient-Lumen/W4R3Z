#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VALIDATION_DIR = ROOT / 'validation' / 'latest'
DEFAULT_OUTPUT_DIR = DEFAULT_VALIDATION_DIR / 'validation-artifact-inventory'
REPORT_COMMAND = 'python scripts/validation-artifact-inventory.py --pretty'
CAPTURE_COMMAND = 'python scripts/validation-artifact-inventory.py capture --output-dir validation/latest/validation-artifact-inventory'

BUCKET_ORDER = {
    'capture_bundles': 0,
    'manual_and_forensics': 1,
    'checks_and_tests': 2,
    'fixture_samples_and_indexes': 3,
    'status_and_reports': 4,
    'other': 99,
}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _bucket_for(rel_path: str) -> str:
    parts = rel_path.split('/')
    first = parts[0]
    name = Path(rel_path).name
    if first in {
        'control-plane-report-capture',
        'install-receipt-capture',
        'opening-surface-capture',
        'operator-handoff',
        'readiness-report-capture',
        'support-surface-capture',
        'truth-surface-register',
        'truth-surface-warnings',
        'validation-artifact-inventory',
    }:
        return 'capture_bundles'
    if first == 'manual' or name.startswith('manual-') or 'forensic' in rel_path:
        return 'manual_and_forensics'
    if first == 'steps' or name.startswith(('test-', 'test_', 'typecheck', 'pytest', 'build-', 'py-compile', 'py_compile', 'extension_typecheck')):
        return 'checks_and_tests'
    if first in {'choice-sample', 'planner-sample-rev0040', 'planner-step-sample-rev0041', 'semantic-sample', 'state-sample-rev0039'}:
        return 'fixture_samples_and_indexes'
    if name.startswith(('compare-', 'index-', 'seed-', 'plan-sample-', 'current_step')):
        return 'fixture_samples_and_indexes'
    if first in {'choice-sample', 'semantic-sample'} or first.startswith(('planner-sample', 'planner-step-sample', 'state-sample')):
        return 'fixture_samples_and_indexes'
    if name.startswith(('SUMMARY', 'doctor', 'chrome-for-testing', 'playwright', 'e2e-fixturelab', 'report', 'rev')):
        return 'status_and_reports'
    return 'other'


def build_validation_artifact_inventory(*, validation_dir: Path = DEFAULT_VALIDATION_DIR) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(validation_dir.rglob('*')):
        if not path.is_file():
            continue
        rel_path = str(path.relative_to(validation_dir))
        if rel_path.startswith('validation-artifact-inventory/'):
            continue
        files.append({'path': rel_path, 'size_bytes': path.stat().st_size, 'bucket': _bucket_for(rel_path)})
    buckets: dict[str, dict[str, Any]] = {}
    for item in files:
        bucket = item['bucket']
        entry = buckets.setdefault(bucket, {'bucket': bucket, 'file_count': 0, 'total_bytes': 0, 'samples': []})
        entry['file_count'] += 1
        entry['total_bytes'] += item['size_bytes']
        if len(entry['samples']) < 5:
            entry['samples'].append(item['path'])
    bucket_list = sorted(buckets.values(), key=lambda item: (BUCKET_ORDER.get(item['bucket'], 999), item['bucket']))
    return {
        'project': 'GlassTTY',
        'validation_dir': str(validation_dir),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'total_file_count': len(files),
        'bucket_count': len(bucket_list),
        'buckets': bucket_list,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
        },
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# Validation artifact inventory',
        '',
        f"- generated_at: {payload.get('generated_at')}",
        f"- total_file_count: {payload.get('total_file_count')}",
        f"- bucket_count: {payload.get('bucket_count')}",
        '',
        '| bucket | files | bytes | sample |',
        '|---|---:|---:|---|',
    ]
    for bucket in payload.get('buckets') or []:
        sample = ', '.join(bucket.get('samples') or []) or '—'
        lines.append(f"| `{bucket.get('bucket')}` | {bucket.get('file_count')} | {bucket.get('total_bytes')} | {sample} |")
    return '\n'.join(lines) + '\n'


def capture_validation_artifact_inventory(*, output_dir: Path = DEFAULT_OUTPUT_DIR, validation_dir: Path = DEFAULT_VALIDATION_DIR) -> dict[str, Any]:
    payload = build_validation_artifact_inventory(validation_dir=validation_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'artifact-buckets.json', payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize GlassTTY validation/latest artifacts into stable bucket groups.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Write the current validation artifact inventory into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_validation_artifact_inventory(output_dir=Path(args.output_dir), validation_dir=DEFAULT_VALIDATION_DIR)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_validation_artifact_inventory(validation_dir=DEFAULT_VALIDATION_DIR)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

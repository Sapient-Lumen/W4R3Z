#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from support_records import flatten_workflow_rows, load_support_records, summarize_support, validate_support_records

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'support-surface-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'support-surface-captures.json'
REPORT_COMMAND = 'python scripts/support-surface-snapshot.py --pretty'
CAPTURE_COMMAND = 'python scripts/support-surface-snapshot.py capture --output-dir validation/latest/support-surface-capture'
HISTORY_COMMAND = 'python scripts/support-surface-snapshot.py history --pretty'
CHECK_COMMAND = 'python scripts/check-support-record-contract.py --pretty'


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    changed: list[str] = []
    for key in sorted(set(previous) | set(current)):
        if previous.get(key) != current.get(key):
            changed.append(key)
    return changed


def build_support_surface_snapshot(*, root: Path = ROOT) -> dict[str, Any]:
    records = load_support_records(root=root)
    summary = summarize_support(records)
    contract = validate_support_records(records)
    workflow_rows = flatten_workflow_rows(records)
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'support_surface': {
            **summary,
            'workflow_rows': workflow_rows,
        },
        'record_contract': contract,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'check_contract': CHECK_COMMAND,
        },
    }


def summarize_capture_history(history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    if not history_path.exists():
        return {'path': str(history_path), 'exists': False, 'capture_count': 0, 'latest_capture': None}
    payload = json.loads(history_path.read_text(encoding='utf-8'))
    captures = payload.get('captures') if isinstance(payload, dict) else None
    latest = captures[-1] if isinstance(captures, list) and captures else None
    return {
        'path': str(history_path),
        'exists': True,
        'capture_count': len(captures or []),
        'latest_capture': latest,
    }


def _summary_markdown(snapshot: dict[str, Any]) -> str:
    support = snapshot.get('support_surface') if isinstance(snapshot.get('support_surface'), dict) else {}
    contract = snapshot.get('record_contract') if isinstance(snapshot.get('record_contract'), dict) else {}
    review_queue = support.get('review_queue') if isinstance(support.get('review_queue'), list) else []
    lines = [
        '# Support surface snapshot',
        '',
        f"- generated_at: {snapshot.get('generated_at')}",
        f"- surface_count: {support.get('surface_count')}",
        f"- workflow_row_count: {len(support.get('workflow_rows') or [])}",
        f"- contract_errors: {contract.get('error_count')}",
        f"- contract_warnings: {contract.get('warning_count')}",
        '',
        '## Surface summary',
        '',
    ]
    for surface in support.get('surfaces') or []:
        lines.append(
            f"- `{surface.get('surface_key')}` — status={surface.get('record_status')}, strongest={surface.get('strongest_tier')}, weakest={surface.get('weakest_tier')}, last_reviewed={surface.get('last_reviewed')}"
        )
    lines.extend(['', '## Top review queue', ''])
    for item in review_queue[:8]:
        lines.append(
            f"- {item.get('priority')}. `{item.get('surface_key')} × {item.get('workflow')} × {item.get('lane')}` — {item.get('current_tier')}; next: {item.get('next_action') or item.get('promotion_requirement')}"
        )
    if contract.get('duplicate_surface_keys'):
        lines.extend(['', '## Contract warnings', ''])
        for key in contract.get('duplicate_surface_keys') or []:
            lines.append(f'- duplicate surface key: `{key}`')
    return '\n'.join(lines) + '\n'


def capture_support_surface_snapshot(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, root: Path = ROOT) -> dict[str, Any]:
    snapshot = build_support_surface_snapshot(root=root)
    previous_history = None
    if history_path.exists():
        previous_history = json.loads(history_path.read_text(encoding='utf-8'))
    previous_latest = None
    if isinstance(previous_history, dict):
        captures = previous_history.get('captures')
        if isinstance(captures, list) and captures:
            previous_latest = captures[-1].get('snapshot')
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'support-surface.json', snapshot)
    _write_json(output_dir / 'record-contract.json', snapshot.get('record_contract'))
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(snapshot), encoding='utf-8')
    history_payload = previous_history if isinstance(previous_history, dict) else {'captures': []}
    captures = history_payload.setdefault('captures', [])
    entry = {
        'captured_at': snapshot.get('generated_at'),
        'output_dir': str(output_dir),
        'surface_count': snapshot.get('support_surface', {}).get('surface_count'),
        'contract_error_count': snapshot.get('record_contract', {}).get('error_count'),
        'top_review_item': (snapshot.get('support_surface', {}).get('review_queue') or [None])[0],
        'snapshot': snapshot,
    }
    captures.append(entry)
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path))
    _write_json(output_dir / 'capture-diff.json', {'changed_fields': _changed_fields(previous_latest, snapshot)})
    return {
        'snapshot': snapshot,
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(captures),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a machine-readable GlassTTY support surface snapshot.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Freeze the current support surface snapshot into a bundle.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true')

    history_parser = subparsers.add_parser('history', help='Show support-surface capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')

    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_support_surface_snapshot(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_support_surface_snapshot()
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

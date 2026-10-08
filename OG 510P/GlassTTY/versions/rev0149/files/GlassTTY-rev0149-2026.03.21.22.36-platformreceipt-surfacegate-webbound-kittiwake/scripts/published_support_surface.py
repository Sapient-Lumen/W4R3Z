#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from support_bundle_queue import build_support_bundle_queue, STATUS_ORDER
    from support_records import load_support_records, summarize_support, ROLLOUT_PRIORITY_ORDER
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _BUNDLES_PATH = Path(__file__).resolve().parent / 'support_bundle_queue.py'
    _BUNDLES_SPEC = importlib.util.spec_from_file_location('support_bundle_queue', _BUNDLES_PATH)
    _BUNDLES_MODULE = importlib.util.module_from_spec(_BUNDLES_SPEC)
    assert _BUNDLES_SPEC.loader is not None
    _BUNDLES_SPEC.loader.exec_module(_BUNDLES_MODULE)
    build_support_bundle_queue = _BUNDLES_MODULE.build_support_bundle_queue
    STATUS_ORDER = _BUNDLES_MODULE.STATUS_ORDER

    _RECORDS_PATH = Path(__file__).resolve().parent / 'support_records.py'
    _RECORDS_SPEC = importlib.util.spec_from_file_location('support_records', _RECORDS_PATH)
    _RECORDS_MODULE = importlib.util.module_from_spec(_RECORDS_SPEC)
    assert _RECORDS_SPEC.loader is not None
    _RECORDS_SPEC.loader.exec_module(_RECORDS_MODULE)
    load_support_records = _RECORDS_MODULE.load_support_records
    summarize_support = _RECORDS_MODULE.summarize_support
    ROLLOUT_PRIORITY_ORDER = _RECORDS_MODULE.ROLLOUT_PRIORITY_ORDER

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'published-support-surface'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'published-support-surface-captures.json'
ROOT_OUTPUT_PATH = ROOT / 'SUPPORT-PUBLIC-SURFACE.json'
REPORT_COMMAND = 'python scripts/published-support-surface.py --pretty'
CAPTURE_COMMAND = 'python scripts/published-support-surface.py capture --output-dir validation/latest/published-support-surface'
HISTORY_COMMAND = 'python scripts/published-support-surface.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/published-support-surface.py write-root'
TRANSITION_COMMAND = 'python scripts/support-bundle-transition.py --bundle <bundle-key> --to-state <candidate|hold|published-ready|published>'


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


def _publication_posture(surface_bundles: list[dict[str, Any]]) -> str:
    statuses = {item.get('bundle_status') for item in surface_bundles}
    if 'published' in statuses:
        return 'published'
    if 'published-ready' in statuses:
        return 'published-ready'
    if 'hold' in statuses:
        return 'hold'
    if 'candidate' in statuses:
        return 'candidate'
    return 'none'


def _bundle_keys(surface_bundles: list[dict[str, Any]], status: str) -> list[str]:
    return [item.get('bundle_key') for item in surface_bundles if item.get('bundle_status') == status]


def build_published_support_surface(*, root: Path = ROOT) -> dict[str, Any]:
    records = load_support_records(root=root)
    support = summarize_support(records)
    queue = build_support_bundle_queue(root=root)
    bundles = queue.get('bundles') or []
    bundle_map: dict[str, list[dict[str, Any]]] = {}
    for bundle in bundles:
        surface_key = bundle.get('surface_key') or 'unknown'
        bucket = bundle_map.setdefault(surface_key, [])
        bucket.append(bundle)
    surfaces: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for surface in support.get('surfaces') or []:
        surface_key = surface.get('surface_key')
        surface_bundles = sorted(bundle_map.get(surface_key, []), key=lambda item: STATUS_ORDER.get(item.get('bundle_status', ''), 999))
        posture = _publication_posture(surface_bundles)
        strongest_tier = surface.get('strongest_tier')
        citable_bundle_keys = _bundle_keys(surface_bundles, 'published')
        ready_bundle_keys = _bundle_keys(surface_bundles, 'published-ready')
        hold_bundle_keys = _bundle_keys(surface_bundles, 'hold')
        candidate_bundle_keys = _bundle_keys(surface_bundles, 'candidate')
        surfaces.append({
            'surface_key': surface_key,
            'title': surface.get('title'),
            'rollout_priority': surface.get('rollout_priority'),
            'record_status': surface.get('record_status'),
            'strongest_tier': strongest_tier,
            'weakest_tier': surface.get('weakest_tier'),
            'publication_posture': posture,
            'citable_now': bool(citable_bundle_keys),
            'published_bundle_keys': citable_bundle_keys,
            'published_ready_bundle_keys': ready_bundle_keys,
            'hold_bundle_keys': hold_bundle_keys,
            'candidate_bundle_keys': candidate_bundle_keys,
            'next_action': surface.get('next_action'),
        })
        if strongest_tier in ('experimental', 'provisional', 'supported') and not citable_bundle_keys:
            warnings.append({
                'surface_key': surface_key,
                'severity': 'advisory',
                'message': f"{surface_key} reaches tier {strongest_tier!r} in support records but has no published support bundle yet",
                'suggested_command': REPORT_COMMAND,
            })
        if surface.get('rollout_priority') == 'reference adapter' and posture not in ('published', 'published-ready'):
            warnings.append({
                'surface_key': surface_key,
                'severity': 'advisory',
                'message': 'reference adapter surface lacks a published or published-ready support bundle',
                'suggested_command': REPORT_COMMAND,
            })
        if posture == 'published-ready' and not citable_bundle_keys:
            warnings.append({
                'surface_key': surface_key,
                'severity': 'actionable',
                'message': 'published-ready support bundle exists but has not been executed into published/citable state',
                'suggested_command': TRANSITION_COMMAND,
            })
    posture_counts = Counter(item.get('publication_posture') or 'none' for item in surfaces)
    published_only = [item for item in surfaces if item.get('citable_now')]
    warnings.sort(key=lambda item: (0 if item.get('severity') == 'actionable' else 1, ROLLOUT_PRIORITY_ORDER.get(next((s.get('rollout_priority') for s in surfaces if s.get('surface_key') == item.get('surface_key')), ''), 999), item.get('surface_key', '')))
    for index, item in enumerate(warnings, start=1):
        item['priority'] = index
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'counts': {
            'surface_count': len(surfaces),
            'citable_surface_count': len(published_only),
            'published_bundle_count': sum(1 for bundle in bundles if bundle.get('bundle_status') == 'published'),
            'published_ready_bundle_count': sum(1 for bundle in bundles if bundle.get('bundle_status') == 'published-ready'),
            'warning_count': len(warnings),
            'publication_posture_counts': dict(sorted(posture_counts.items(), key=lambda item: item[0])),
        },
        'surfaces': surfaces,
        'citable_surfaces': published_only,
        'warnings': warnings,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'transition_bundle': TRANSITION_COMMAND,
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
    counts = snapshot.get('counts') if isinstance(snapshot.get('counts'), dict) else {}
    lines = [
        '# Published support surface',
        '',
        f"- generated_at: {snapshot.get('generated_at')}",
        f"- citable_surface_count: {counts.get('citable_surface_count')}",
        f"- published_bundle_count: {counts.get('published_bundle_count')}",
        f"- published_ready_bundle_count: {counts.get('published_ready_bundle_count')}",
        f"- warning_count: {counts.get('warning_count')}",
        '',
        '## Surface posture',
        '',
    ]
    for surface in snapshot.get('surfaces') or []:
        lines.append(
            f"- `{surface.get('surface_key')}` — posture={surface.get('publication_posture')}, citable_now={surface.get('citable_now')}, strongest_tier={surface.get('strongest_tier')}"
        )
    lines.extend(['', '## Warnings', ''])
    for warning in snapshot.get('warnings') or []:
        lines.append(f"- {warning.get('priority')}. `{warning.get('surface_key')}` — {warning.get('severity')}: {warning.get('message')}")
    if not snapshot.get('warnings'):
        lines.append('- no published-support warnings')
    return '\n'.join(lines) + '\n'


def capture_published_support_surface(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, root: Path = ROOT) -> dict[str, Any]:
    snapshot = build_published_support_surface(root=root)
    previous_history = None
    if history_path.exists():
        previous_history = json.loads(history_path.read_text(encoding='utf-8'))
    previous_latest = None
    if isinstance(previous_history, dict):
        captures = previous_history.get('captures')
        if isinstance(captures, list) and captures:
            previous_latest = captures[-1].get('snapshot')
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'support-public-surface.json', snapshot)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(snapshot), encoding='utf-8')
    history_payload = previous_history if isinstance(previous_history, dict) else {'captures': []}
    captures = history_payload.setdefault('captures', [])
    entry = {
        'captured_at': snapshot.get('generated_at'),
        'output_dir': str(output_dir),
        'citable_surface_count': (snapshot.get('counts') or {}).get('citable_surface_count'),
        'published_bundle_count': (snapshot.get('counts') or {}).get('published_bundle_count'),
        'warning_count': (snapshot.get('counts') or {}).get('warning_count'),
        'snapshot': snapshot,
    }
    captures.append(entry)
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path))
    _write_json(output_dir / 'capture-diff.json', {'changed_fields': _changed_fields(previous_latest, snapshot)})
    return {
        'snapshot': snapshot,
        'history_update': {'history_path': str(history_path), 'capture_count_after_write': len(captures)},
    }


def write_root_published_support_surface(*, root: Path = ROOT) -> dict[str, Any]:
    snapshot = build_published_support_surface(root=root)
    _write_json(root / 'SUPPORT-PUBLIC-SURFACE.json', snapshot)
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description='Freeze the citable/published GlassTTY support surface separately from the broader support queue.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Freeze the current published support surface into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true')
    history_parser = subparsers.add_parser('history', help='Show published-support capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    subparsers.add_parser('write-root', help='Write SUPPORT-PUBLIC-SURFACE.json at the repo root.')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_published_support_surface(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_published_support_surface(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_published_support_surface(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

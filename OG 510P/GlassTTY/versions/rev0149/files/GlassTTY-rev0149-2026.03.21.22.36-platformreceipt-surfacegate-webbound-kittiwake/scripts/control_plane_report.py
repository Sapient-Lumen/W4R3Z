#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from readiness_report import build_readiness_report, load_doctor_report
    from truth_surface_warnings import build_truth_surface_warnings
    from support_bundle_queue import build_support_bundle_queue
    from published_support_surface import build_published_support_surface
    from support_publish_gate import build_support_publish_gate
    from support_source_baseline import build_support_source_baseline
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _READINESS_PATH = Path(__file__).resolve().parent / 'readiness_report.py'
    _READINESS_SPEC = importlib.util.spec_from_file_location('readiness_report', _READINESS_PATH)
    _READINESS_MODULE = importlib.util.module_from_spec(_READINESS_SPEC)
    assert _READINESS_SPEC.loader is not None
    _READINESS_SPEC.loader.exec_module(_READINESS_MODULE)
    build_readiness_report = _READINESS_MODULE.build_readiness_report
    load_doctor_report = _READINESS_MODULE.load_doctor_report

    _WARNINGS_PATH = Path(__file__).resolve().parent / 'truth_surface_warnings.py'
    _WARNINGS_SPEC = importlib.util.spec_from_file_location('truth_surface_warnings', _WARNINGS_PATH)
    _WARNINGS_MODULE = importlib.util.module_from_spec(_WARNINGS_SPEC)
    assert _WARNINGS_SPEC.loader is not None
    _WARNINGS_SPEC.loader.exec_module(_WARNINGS_MODULE)
    build_truth_surface_warnings = _WARNINGS_MODULE.build_truth_surface_warnings


    _BUNDLES_PATH = Path(__file__).resolve().parent / 'support_bundle_queue.py'
    _BUNDLES_SPEC = importlib.util.spec_from_file_location('support_bundle_queue', _BUNDLES_PATH)
    _BUNDLES_MODULE = importlib.util.module_from_spec(_BUNDLES_SPEC)
    assert _BUNDLES_SPEC.loader is not None
    _BUNDLES_SPEC.loader.exec_module(_BUNDLES_MODULE)
    build_support_bundle_queue = _BUNDLES_MODULE.build_support_bundle_queue

    _PUBLISHED_PATH = Path(__file__).resolve().parent / 'published_support_surface.py'
    _PUBLISHED_SPEC = importlib.util.spec_from_file_location('published_support_surface', _PUBLISHED_PATH)
    _PUBLISHED_MODULE = importlib.util.module_from_spec(_PUBLISHED_SPEC)
    assert _PUBLISHED_SPEC.loader is not None
    _PUBLISHED_SPEC.loader.exec_module(_PUBLISHED_MODULE)
    build_published_support_surface = _PUBLISHED_MODULE.build_published_support_surface

    _PUBLISH_GATE_PATH = Path(__file__).resolve().parent / 'support_publish_gate.py'
    _PUBLISH_GATE_SPEC = importlib.util.spec_from_file_location('support_publish_gate', _PUBLISH_GATE_PATH)
    _PUBLISH_GATE_MODULE = importlib.util.module_from_spec(_PUBLISH_GATE_SPEC)
    assert _PUBLISH_GATE_SPEC.loader is not None
    _PUBLISH_GATE_SPEC.loader.exec_module(_PUBLISH_GATE_MODULE)
    build_support_publish_gate = _PUBLISH_GATE_MODULE.build_support_publish_gate


    _SOURCE_BASELINE_PATH = Path(__file__).resolve().parent / 'support_source_baseline.py'
    _SOURCE_BASELINE_SPEC = importlib.util.spec_from_file_location('support_source_baseline', _SOURCE_BASELINE_PATH)
    _SOURCE_BASELINE_MODULE = importlib.util.module_from_spec(_SOURCE_BASELINE_SPEC)
    assert _SOURCE_BASELINE_SPEC.loader is not None
    _SOURCE_BASELINE_SPEC.loader.exec_module(_SOURCE_BASELINE_MODULE)
    build_support_source_baseline = _SOURCE_BASELINE_MODULE.build_support_source_baseline

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'control-plane-report-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'control-plane-report-captures.json'
REPORT_COMMAND = 'python scripts/control-plane-report.py --pretty'
CAPTURE_COMMAND = 'python scripts/control-plane-report.py capture --output-dir validation/latest/control-plane-report-capture'
HISTORY_COMMAND = 'python scripts/control-plane-report.py history --pretty'

ROLLOUT_PRIORITY_ORDER = {
    'reference adapter': 0,
    'recommended second adapter': 1,
    'phase-2': 2,
    'phase-3': 3,
}
TIER_ORDER = {
    'unsupported': 0,
    'investigated': 1,
    'experimental': 2,
    'provisional': 3,
    'supported': 4,
}
RECORD_STATUS_ORDER = {
    'seeded': 0,
    'backfilled-from-evidence': 1,
    'current': 2,
    'stale': 3,
}
WORKFLOW_ORDER = {
    'surface-detect': 0,
    'receiver-resolve': 1,
    'composer-read': 2,
    'composer-write': 3,
    'turn-submit': 4,
    'generation-read': 5,
    'latest-turn-read': 6,
    'support-capture': 7,
}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _markdown_table_rows(lines: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    table_lines = [line.rstrip('\n') for line in lines if line.strip()]
    if len(table_lines) < 3:
        return rows
    headers = [cell.strip() for cell in table_lines[0].strip().strip('|').split('|')]
    for line in table_lines[2:]:
        if '|' not in line:
            continue
        values = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(values) != len(headers):
            continue
        rows.append({headers[i]: values[i] for i in range(len(headers))})
    return rows


def parse_support_record(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    title_match = re.search(r'^# Support record — (.+)$', text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem
    metadata: dict[str, str] = {}
    for key, value in re.findall(r'^- \*\*(.+?):\*\* `(.*?)`$', text, flags=re.MULTILINE):
        metadata[key.strip().lower()] = value.strip()
    next_action = None
    next_action_match = re.search(r'^## Next action\n(.+?)(?:\n## |\Z)', text, flags=re.MULTILINE | re.DOTALL)
    if next_action_match:
        next_action = ' '.join(
            line.strip('- ').strip()
            for line in next_action_match.group(1).strip().splitlines()
            if line.strip()
        )
    known_blockers: list[str] = []
    blockers_match = re.search(r'^## Known blockers and risk notes\n(.+?)(?:\n## |\Z)', text, flags=re.MULTILINE | re.DOTALL)
    if blockers_match:
        known_blockers = [line.strip('- ').strip() for line in blockers_match.group(1).splitlines() if line.strip().startswith('-')]
    workflow_match = re.search(r'^## Workflow rows\n\n((?:\|.*\n)+)', text, flags=re.MULTILINE)
    workflows = _markdown_table_rows(workflow_match.group(1).splitlines()) if workflow_match else []
    normalized_rows = []
    for row in workflows:
        normalized_rows.append({
            'workflow': row.get('workflow', ''),
            'current_tier': row.get('current tier', ''),
            'lane': row.get('lane', ''),
            'evidence_posture': row.get('evidence refs / posture', ''),
            'caveats': row.get('caveats', ''),
            'promotion_requirement': row.get('promotion requirement', ''),
        })
    return {
        'path': str(path),
        'title': title,
        'surface_key': metadata.get('surface key', path.stem),
        'record_status': metadata.get('record status', 'unknown'),
        'default_browser_lane': metadata.get('default browser lane', 'unknown'),
        'last_reviewed': metadata.get('last reviewed'),
        'rollout_priority': metadata.get('rollout priority', 'unknown'),
        'workflow_rows': normalized_rows,
        'workflow_row_count': len(normalized_rows),
        'known_blockers': known_blockers,
        'next_action': next_action,
    }


def load_support_records(*, root: Path = ROOT) -> list[dict[str, Any]]:
    records_dir = root / 'docs' / 'support-records'
    records = []
    if not records_dir.exists():
        return records
    for path in sorted(records_dir.glob('*.md')):
        if path.name.lower() == 'readme.md':
            continue
        records.append(parse_support_record(path))
    return records


def _tier_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(row.get('current_tier') or 'unknown' for row in rows)
    return dict(sorted(counter.items(), key=lambda item: (TIER_ORDER.get(item[0], 999), item[0])))


def _surface_summary(record: dict[str, Any]) -> dict[str, Any]:
    rows = record.get('workflow_rows') or []
    tiers = [row.get('current_tier') for row in rows if row.get('current_tier')]
    strongest = max(tiers, key=lambda value: TIER_ORDER.get(value, -1)) if tiers else None
    weakest = min(tiers, key=lambda value: TIER_ORDER.get(value, 999)) if tiers else None
    return {
        'surface_key': record.get('surface_key'),
        'title': record.get('title'),
        'path': record.get('path'),
        'record_status': record.get('record_status'),
        'rollout_priority': record.get('rollout_priority'),
        'default_browser_lane': record.get('default_browser_lane'),
        'last_reviewed': record.get('last_reviewed'),
        'workflow_row_count': record.get('workflow_row_count', 0),
        'workflow_tier_counts': _tier_counts(rows),
        'strongest_tier': strongest,
        'weakest_tier': weakest,
        'known_blockers': record.get('known_blockers') or [],
        'next_action': record.get('next_action'),
    }


def _review_priority(record: dict[str, Any], row: dict[str, Any]) -> tuple[int, int, int, int, str, str]:
    rollout = ROLLOUT_PRIORITY_ORDER.get(record.get('rollout_priority', ''), 99)
    tier = TIER_ORDER.get(row.get('current_tier', ''), -1)
    tier_pressure = 10 - max(tier, 0)
    record_status = record.get('record_status', '')
    if record_status == 'seeded':
        status_pressure = 0
    elif record_status == 'stale':
        status_pressure = 1
    elif record_status == 'backfilled-from-evidence':
        status_pressure = 2
    else:
        status_pressure = 3
    workflow = WORKFLOW_ORDER.get(row.get('workflow', ''), 99)
    return (rollout, tier_pressure, status_pressure, workflow, record.get('surface_key', ''), row.get('workflow', ''))


def build_review_queue(records: list[dict[str, Any]], *, limit: int = 16) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for record in records:
        for row in record.get('workflow_rows') or []:
            rationale_bits = [
                f"{record.get('surface_key')} is a {record.get('rollout_priority')} surface",
                f"{row.get('workflow')} is only {row.get('current_tier')}",
            ]
            if record.get('record_status') == 'seeded':
                rationale_bits.append('record is still seeded, so support truth is not yet backfilled from named artifacts')
            elif record.get('record_status') == 'stale':
                rationale_bits.append('record is stale and should be refreshed before stronger claims')
            items.append({
                'surface_key': record.get('surface_key'),
                'workflow': row.get('workflow'),
                'lane': row.get('lane') or record.get('default_browser_lane'),
                'current_tier': row.get('current_tier'),
                'record_status': record.get('record_status'),
                'rollout_priority': record.get('rollout_priority'),
                'promotion_requirement': row.get('promotion_requirement'),
                'evidence_posture': row.get('evidence_posture'),
                'caveats': row.get('caveats'),
                'next_action': record.get('next_action'),
                'rationale': '; '.join(bit for bit in rationale_bits if bit),
            })
    items.sort(key=lambda item: _review_priority(item, item))
    for index, item in enumerate(items, start=1):
        item['priority'] = index
    return items[:limit]


def summarize_support(records: list[dict[str, Any]]) -> dict[str, Any]:
    all_rows = [row for record in records for row in (record.get('workflow_rows') or [])]
    record_status_counts = Counter(record.get('record_status') or 'unknown' for record in records)
    rollout_priority_counts = Counter(record.get('rollout_priority') or 'unknown' for record in records)
    workflow_counts = Counter(row.get('workflow') or 'unknown' for row in all_rows)
    return {
        'surface_count': len(records),
        'record_status_counts': dict(sorted(record_status_counts.items(), key=lambda item: (RECORD_STATUS_ORDER.get(item[0], 999), item[0]))),
        'rollout_priority_counts': dict(sorted(rollout_priority_counts.items(), key=lambda item: (ROLLOUT_PRIORITY_ORDER.get(item[0], 999), item[0]))),
        'workflow_tier_counts': _tier_counts(all_rows),
        'workflow_counts': dict(sorted(workflow_counts.items(), key=lambda item: (WORKFLOW_ORDER.get(item[0], 999), item[0]))),
        'surfaces': [_surface_summary(record) for record in records],
        'review_queue': build_review_queue(records),
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
        },
    }


def _health_summary(doctor_report: dict[str, Any], readiness: dict[str, Any], truth_surface_warnings: dict[str, Any], support_bundle_queue: dict[str, Any], published_support_surface: dict[str, Any], support_publish_gate: dict[str, Any]) -> dict[str, Any]:
    validation_summary = (((doctor_report.get('validation') or {}).get('latest_report') or {}).get('summary') or {})
    smoke_summary = (((doctor_report.get('fixture_lab') or {}).get('latest_smoke_report') or {}).get('summary') or {})
    triage = ((doctor_report.get('profiles') or {}).get('triage') or {})
    best_profile = triage.get('best_profile') if isinstance(triage, dict) else None
    socket_info = doctor_report.get('socket') if isinstance(doctor_report.get('socket'), dict) else {}
    native_runtime = ((doctor_report.get('native_host') or {}).get('runtime') or {})
    warning_counts = truth_surface_warnings.get('counts') if isinstance(truth_surface_warnings, dict) else {}
    bundle_counts = support_bundle_queue.get('counts') if isinstance(support_bundle_queue, dict) else {}
    published_counts = published_support_surface.get('counts') if isinstance(published_support_surface, dict) else {}
    publish_gate_counts = support_publish_gate.get('counts') if isinstance(support_publish_gate, dict) else {}
    return {
        'readiness_grade': readiness.get('readiness_grade'),
        'primary_next_kind': readiness.get('primary_next_kind'),
        'primary_next_command': readiness.get('primary_next_command'),
        'validation_complete': validation_summary.get('complete'),
        'latest_smoke_ok': smoke_summary.get('ok'),
        'latest_smoke_error': smoke_summary.get('error'),
        'best_profile': {
            'name': (best_profile or {}).get('name'),
            'tier': (best_profile or {}).get('tier'),
            'score': (best_profile or {}).get('score'),
            'attach_ready': (best_profile or {}).get('attach_ready'),
        },
        'socket_exists': socket_info.get('exists'),
        'native_runtime': native_runtime,
        'truth_surface_warning_count': warning_counts.get('warning_count'),
        'truth_surface_blocking_warning_count': warning_counts.get('blocking_warning_count'),
        'support_bundle_count': bundle_counts.get('bundle_count'),
        'support_bundle_warning_count': bundle_counts.get('warning_count'),
        'published_support_citable_surface_count': published_counts.get('citable_surface_count'),
        'published_support_warning_count': published_counts.get('warning_count'),
        'support_publish_gate_ready_count': publish_gate_counts.get('published_ready_pass_count'),
        'support_publish_gate_publish_count': publish_gate_counts.get('published_pass_count'),
        'support_publish_gate_warning_count': publish_gate_counts.get('warning_count'),
    }


def build_control_plane_report(*, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    doctor_payload = doctor_report or load_doctor_report(root=root)
    readiness = build_readiness_report(doctor_report=doctor_payload)['readiness']
    records = load_support_records(root=root)
    truth_surface_warnings = build_truth_surface_warnings(root=root)
    support_bundle_queue = build_support_bundle_queue(root=root)
    published_support_surface = build_published_support_surface(root=root)
    support_publish_gate = build_support_publish_gate(root=root)
    return {
        'project': doctor_payload.get('project', 'GlassTTY'),
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'health': _health_summary(doctor_payload, readiness, truth_surface_warnings, support_bundle_queue, published_support_surface, support_publish_gate),
        'readiness': readiness,
        'support': summarize_support(records),
        'support_bundles': support_bundle_queue,
        'published_support': published_support_surface,
        'support_publish_gate': support_publish_gate,
        'truth_surfaces': truth_surface_warnings,
        'commands': {
            'doctor': 'python scripts/doctor.py --pretty',
            'readiness_report': 'python scripts/readiness-report.py --pretty',
            'control_plane_report': REPORT_COMMAND,
            'truth_surface_warnings': 'python scripts/truth-surface-warnings.py --pretty',
            'support_bundle_queue': 'python scripts/support-bundle-queue.py --pretty',
            'published_support_surface': 'python scripts/published-support-surface.py --pretty',
            'support_publish_gate': 'python scripts/support-publish-gate.py --pretty',
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
        },
    }


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    changed: list[str] = []
    for key in sorted(set(previous) | set(current)):
        if previous.get(key) != current.get(key):
            changed.append(key)
    return changed


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


def capture_control_plane_report(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    doctor_payload = doctor_report or load_doctor_report(root=root)
    report = build_control_plane_report(doctor_report=doctor_payload, root=root)
    previous_history = None
    if history_path.exists():
        previous_history = json.loads(history_path.read_text(encoding='utf-8'))
    previous_latest = None
    if isinstance(previous_history, dict):
        captures = previous_history.get('captures')
        if isinstance(captures, list) and captures:
            previous_latest = captures[-1].get('report')
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'control-plane-report.json', report)
    _write_json(output_dir / 'doctor.json', doctor_payload)
    review_lines = ['# Control-plane review queue', '']
    for item in report['support']['review_queue']:
        review_lines.append(
            f"- {item['priority']}. `{item['surface_key']} × {item['workflow']} × {item['lane']}` — {item['current_tier']}; next: {item.get('next_action') or item.get('promotion_requirement')}"
        )
    (output_dir / 'review-queue.md').write_text('\n'.join(review_lines) + '\n', encoding='utf-8')
    support_bundle_lines = ['# Control-plane support bundle queue', '']
    for item in report['support_bundles']['review_queue']:
        support_bundle_lines.append(
            f"- {item['priority']}. `{item['bundle_key']}` — {item['bundle_status']} for `{item['surface_key']} × {item['browser_lane']}`; next: {item.get('next_action') or 'inspect bundle manifest'}"
        )
    if not report['support_bundles']['review_queue']:
        support_bundle_lines.append('- no support bundles yet')
    (output_dir / 'support-bundle-queue.md').write_text('\n'.join(support_bundle_lines) + '\n', encoding='utf-8')
    published_lines = ['# Control-plane published support surface', '']
    for item in report['published_support']['surfaces']:
        published_lines.append(
            f"- `{item['surface_key']}` — posture={item['publication_posture']}, citable_now={item['citable_now']}, strongest_tier={item['strongest_tier']}"
        )
    if not report['published_support']['surfaces']:
        published_lines.append('- no published-support surfaces yet')
    (output_dir / 'published-support-surface.md').write_text('\n'.join(published_lines) + '\n', encoding='utf-8')
    publish_gate_lines = ['# Control-plane support publish gate', '']
    for item in report['support_publish_gate']['bundles']:
        ready_gate = item.get('published_ready_gate') or {}
        published_gate = item.get('published_gate') or {}
        publish_gate_lines.append(
            f"- `{item['bundle_key']}` — state={item['current_state']}, published-ready={ready_gate.get('ok')}, published={published_gate.get('ok')}"
        )
    if not report['support_publish_gate']['bundles']:
        publish_gate_lines.append('- no support publish-gate bundles yet')
    (output_dir / 'support-publish-gate.md').write_text('\n'.join(publish_gate_lines) + '\n', encoding='utf-8')
    warning_lines = ['# Control-plane truth-surface warnings', '']
    for item in report['truth_surfaces']['warnings']:
        warning_lines.append(
            f"- {item['priority']}. `{item['family_key']}` — {item['severity']}: {item['message']}; next: {item.get('suggested_command') or 'inspect truth-surface register'}"
        )
    if not report['truth_surfaces']['warnings']:
        warning_lines.append('- no truth-surface warnings')
    (output_dir / 'truth-surface-warnings.md').write_text('\n'.join(warning_lines) + '\n', encoding='utf-8')
    history_payload = previous_history if isinstance(previous_history, dict) else {'captures': []}
    captures = history_payload.setdefault('captures', [])
    summary = {
        'captured_at': report['generated_at'],
        'output_dir': str(output_dir),
        'readiness_grade': report['health']['readiness_grade'],
        'primary_next_kind': report['health']['primary_next_kind'],
        'top_review_item': report['support']['review_queue'][0] if report['support']['review_queue'] else None,
        'top_support_bundle_item': report['support_bundles']['review_queue'][0] if report['support_bundles']['review_queue'] else None,
        'top_published_support_warning': report['published_support']['warnings'][0] if report['published_support']['warnings'] else None,
        'top_support_publish_gate_warning': report['support_publish_gate']['warnings'][0] if report['support_publish_gate']['warnings'] else None,
        'top_truth_surface_warning': report['truth_surfaces']['warnings'][0] if report['truth_surfaces']['warnings'] else None,
        'report': report,
    }
    captures.append(summary)
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path))
    diff = {'changed_fields': _changed_fields(previous_latest, report)}
    _write_json(output_dir / 'capture-diff.json', diff)
    return {
        'report': report,
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(captures),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a fused GlassTTY control-plane report.')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output.')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Freeze the current control-plane report into a bundle.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true')

    history_parser = subparsers.add_parser('history', help='Show control-plane capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')

    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_control_plane_report(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_control_plane_report()
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import operator_handoff as handoff_module
import readiness_report as readiness_module

ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'operator-attempt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'operator-attempts.json'

OPERATOR_ATTEMPT_REPORT_COMMAND = 'python scripts/operator-attempt.py --pretty'
OPERATOR_ATTEMPT_START_COMMAND = 'python scripts/operator-attempt.py start --output-dir validation/latest/operator-attempt'
OPERATOR_ATTEMPT_FINISH_COMMAND = 'python scripts/operator-attempt.py finish --output-dir validation/latest/operator-attempt --outcome success'
OPERATOR_ATTEMPT_HISTORY_COMMAND = 'python scripts/operator-attempt.py history --pretty'

TRACKED_FIELDS = (
    'status',
    'planned_command',
    'outcome',
    'readiness_grade_before',
    'readiness_grade_after',
    'primary_next_kind_before',
    'primary_next_kind_after',
    'primary_next_command_before',
    'primary_next_command_after',
    'best_profile_name_before',
    'best_profile_name_after',
    'validation_complete_before',
    'validation_complete_after',
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def operator_attempt_commands() -> dict[str, str]:
    return {
        'report': OPERATOR_ATTEMPT_REPORT_COMMAND,
        'start_latest': OPERATOR_ATTEMPT_START_COMMAND,
        'finish_latest': OPERATOR_ATTEMPT_FINISH_COMMAND,
        'history': OPERATOR_ATTEMPT_HISTORY_COMMAND,
    }


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _history_entries(history_path)
    payload = _read_json(history_path) if history_path.exists() else None
    latest = entries[-1] if entries else None
    return {
        'path': str(history_path),
        'exists': history_path.exists(),
        'capture_count': len(entries),
        'latest_capture': latest,
        'history': payload,
    }


def summarize_current_attempt(output_dir: Path | None = None) -> dict[str, Any]:
    target_dir = output_dir or DEFAULT_OUTPUT_DIR
    attempt_path = target_dir / 'attempt.json'
    if not attempt_path.exists():
        return {
            'path': str(attempt_path),
            'exists': False,
            'status': None,
        }
    payload = _read_json(attempt_path)
    before = payload.get('before') if isinstance(payload.get('before'), dict) else {}
    after = payload.get('after') if isinstance(payload.get('after'), dict) else {}
    diff = payload.get('attempt_diff') if isinstance(payload.get('attempt_diff'), dict) else {}
    return {
        'path': str(attempt_path),
        'exists': True,
        'status': payload.get('status'),
        'label': payload.get('label'),
        'planned_command': payload.get('planned_command'),
        'started_at': payload.get('started_at'),
        'finished_at': payload.get('finished_at'),
        'outcome': payload.get('outcome'),
        'before': before,
        'after': after,
        'attempt_diff': diff,
        'summary_markdown_path': str(target_dir / 'SUMMARY.md'),
    }


def load_doctor_report(*, root: Path = ROOT) -> dict[str, Any]:
    script = root / 'scripts' / 'doctor.py'
    result = subprocess.run([sys.executable, str(script)], check=True, capture_output=True, text=True, env=dict(os.environ))
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError('doctor.py did not return a JSON object')
    return payload


def _validation_summary(doctor_report: dict[str, Any]) -> dict[str, Any]:
    validation = doctor_report.get('validation') if isinstance(doctor_report.get('validation'), dict) else {}
    latest = validation.get('latest_report') if isinstance(validation.get('latest_report'), dict) else {}
    summary = latest.get('summary') if isinstance(latest.get('summary'), dict) else {}
    return summary


def _best_profile(readiness_report: dict[str, Any]) -> dict[str, Any] | None:
    readiness = readiness_report.get('readiness') if isinstance(readiness_report.get('readiness'), dict) else {}
    profiles = readiness.get('profiles') if isinstance(readiness.get('profiles'), dict) else {}
    best = profiles.get('best_profile') if isinstance(profiles.get('best_profile'), dict) else None
    return best if isinstance(best, dict) else None


def _snapshot_summary(*, doctor_report: dict[str, Any], readiness_report: dict[str, Any], operator_handoff: dict[str, Any]) -> dict[str, Any]:
    readiness = readiness_report.get('readiness') if isinstance(readiness_report.get('readiness'), dict) else {}
    validation_summary = _validation_summary(doctor_report)
    best_profile = _best_profile(readiness_report)
    artifact_inventory = operator_handoff.get('artifact_inventory') if isinstance(operator_handoff.get('artifact_inventory'), list) else []
    smoke_summary = (((doctor_report.get('fixture_lab') or {}).get('latest_smoke_report') or {}).get('summary') if isinstance((doctor_report.get('fixture_lab') or {}).get('latest_smoke_report'), dict) else {})
    return {
        'captured_at': utc_now_iso(),
        'readiness_grade': readiness.get('readiness_grade'),
        'primary_next_kind': readiness.get('primary_next_kind'),
        'primary_next_command': readiness.get('primary_next_command'),
        'best_profile_name': best_profile.get('name') if isinstance(best_profile, dict) else None,
        'best_profile_tier': best_profile.get('tier') if isinstance(best_profile, dict) else None,
        'validation_complete': validation_summary.get('complete'),
        'validation_running_step_name': validation_summary.get('running_step_name'),
        'smoke_report_timestamp': smoke_summary.get('report_timestamp') if isinstance(smoke_summary, dict) else None,
        'hint_count': len(doctor_report.get('hints') or []) if isinstance(doctor_report.get('hints'), list) else None,
        'artifact_count': len(artifact_inventory),
        'missing_required_artifact_count': sum(1 for item in artifact_inventory if isinstance(item, dict) and item.get('required') and not item.get('exists')),
    }


def _build_snapshot(*, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    report = doctor_report or load_doctor_report(root=root)
    readiness_report = readiness_module.build_readiness_report(doctor_report=report, root=root)
    operator_handoff = handoff_module.build_operator_handoff(doctor_report=report, root=root)
    artifact_inventory = operator_handoff.get('artifact_inventory') if isinstance(operator_handoff.get('artifact_inventory'), list) else []
    return {
        'doctor': report,
        'readiness_report': readiness_report,
        'operator_handoff': {
            'generated_at': operator_handoff.get('generated_at'),
            'commands': handoff_module.operator_handoff_commands(),
            'artifact_inventory': artifact_inventory,
            'readiness': operator_handoff.get('readiness'),
        },
        'summary': _snapshot_summary(doctor_report=report, readiness_report=readiness_report, operator_handoff=operator_handoff),
    }


def _write_snapshot_files(output_dir: Path, phase: str, snapshot: dict[str, Any]) -> None:
    _write_json(output_dir / f'doctor-{phase}.json', snapshot.get('doctor'))
    _write_json(output_dir / f'readiness-{phase}.json', snapshot.get('readiness_report'))
    _write_json(output_dir / f'operator-handoff-{phase}.json', snapshot.get('operator_handoff'))
    _write_json(output_dir / f'artifact-index-{phase}.json', ((snapshot.get('operator_handoff') or {}).get('artifact_inventory') if isinstance(snapshot.get('operator_handoff'), dict) else []))


def _attempt_diff(before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        'has_before': isinstance(before, dict),
        'has_after': isinstance(after, dict),
        'changed_fields': [],
    }
    if not isinstance(before, dict) or not isinstance(after, dict):
        comparison['summary'] = 'attempt is missing either the before or after snapshot'
        return comparison
    tracked = (
        'readiness_grade',
        'primary_next_kind',
        'primary_next_command',
        'best_profile_name',
        'validation_complete',
        'validation_running_step_name',
        'smoke_report_timestamp',
        'hint_count',
        'artifact_count',
        'missing_required_artifact_count',
    )
    for key in tracked:
        before_value = before.get(key)
        after_value = after.get(key)
        if before_value != after_value:
            comparison['changed_fields'].append(key)
            comparison[f'{key}_before'] = before_value
            comparison[f'{key}_after'] = after_value
    comparison['summary'] = 'operator attempt changed the next-action surface' if comparison['changed_fields'] else 'operator attempt left the tracked next-action surface unchanged'
    return comparison


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': utc_now_iso(),
        'capture_count': len(entries),
        'entries': entries,
    }


def _history_entry(payload: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    before = payload.get('before') if isinstance(payload.get('before'), dict) else {}
    after = payload.get('after') if isinstance(payload.get('after'), dict) else {}
    return {
        'captured_at': payload.get('finished_at') or payload.get('started_at'),
        'output_dir': str(output_dir),
        'attempt_path': str(output_dir / 'attempt.json'),
        'label': payload.get('label'),
        'status': payload.get('status'),
        'planned_command': payload.get('planned_command'),
        'outcome': payload.get('outcome'),
        'readiness_grade_before': before.get('readiness_grade'),
        'readiness_grade_after': after.get('readiness_grade'),
        'primary_next_kind_before': before.get('primary_next_kind'),
        'primary_next_kind_after': after.get('primary_next_kind'),
        'primary_next_command_before': before.get('primary_next_command'),
        'primary_next_command_after': after.get('primary_next_command'),
        'best_profile_name_before': before.get('best_profile_name'),
        'best_profile_name_after': after.get('best_profile_name'),
        'validation_complete_before': before.get('validation_complete'),
        'validation_complete_after': after.get('validation_complete'),
    }


def _comparison_to_previous(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        'has_previous_capture': isinstance(previous, dict),
        'previous_captured_at': previous.get('captured_at') if isinstance(previous, dict) else None,
        'current_captured_at': current.get('captured_at'),
        'changed_fields': [],
    }
    if not isinstance(previous, dict):
        comparison['summary'] = 'no previous operator attempt exists yet'
        return comparison
    for key in TRACKED_FIELDS:
        if previous.get(key) != current.get(key):
            comparison['changed_fields'].append(key)
            comparison[f'{key}_before'] = previous.get(key)
            comparison[f'{key}_after'] = current.get(key)
    comparison['summary'] = 'operator attempt history drift detected' if comparison['changed_fields'] else 'operator attempt matches the previous finished attempt on tracked fields'
    return comparison


def _update_history(current: dict[str, Any], *, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _history_entries(path)
    previous = entries[-1] if entries else None
    entries.append(current)
    payload = _history_payload(entries)
    _write_json(path, payload)
    return {
        'path': str(path),
        'capture_count_after_write': len(entries),
        'latest_capture': current,
        'previous_capture': previous,
        'history': payload,
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    before = payload.get('before') if isinstance(payload.get('before'), dict) else {}
    after = payload.get('after') if isinstance(payload.get('after'), dict) else {}
    attempt_diff = payload.get('attempt_diff') if isinstance(payload.get('attempt_diff'), dict) else {}
    history_update = payload.get('history_update') if isinstance(payload.get('history_update'), dict) else {}
    history_diff = payload.get('history_diff') if isinstance(payload.get('history_diff'), dict) else {}
    lines = [
        '# GlassTTY operator attempt',
        '',
        f"- label: {payload.get('label')}",
        f"- status: {payload.get('status')}",
        f"- started_at: {payload.get('started_at')}",
        f"- finished_at: {payload.get('finished_at')}",
        f"- outcome: {payload.get('outcome')}",
        f"- planned_command: `{payload.get('planned_command')}`",
        '',
        '## Before',
        '',
        f"- readiness_grade: `{before.get('readiness_grade')}`",
        f"- primary_next_kind: `{before.get('primary_next_kind')}`",
        f"- primary_next_command: `{before.get('primary_next_command')}`",
        f"- best_profile_name: `{before.get('best_profile_name')}`",
        f"- validation_complete: `{before.get('validation_complete')}`",
        f"- validation_running_step_name: `{before.get('validation_running_step_name')}`",
        '',
        '## After',
        '',
        f"- readiness_grade: `{after.get('readiness_grade')}`",
        f"- primary_next_kind: `{after.get('primary_next_kind')}`",
        f"- primary_next_command: `{after.get('primary_next_command')}`",
        f"- best_profile_name: `{after.get('best_profile_name')}`",
        f"- validation_complete: `{after.get('validation_complete')}`",
        f"- validation_running_step_name: `{after.get('validation_running_step_name')}`",
        '',
        '## Attempt diff',
        '',
        f"- summary: {attempt_diff.get('summary')}",
        f"- changed_fields: {', '.join(attempt_diff.get('changed_fields') or []) if isinstance(attempt_diff.get('changed_fields'), list) else ''}",
        '',
        '## Commands',
        '',
        f"- report: `{OPERATOR_ATTEMPT_REPORT_COMMAND}`",
        f"- start_latest: `{OPERATOR_ATTEMPT_START_COMMAND}`",
        f"- finish_latest: `{OPERATOR_ATTEMPT_FINISH_COMMAND}`",
        f"- history: `{OPERATOR_ATTEMPT_HISTORY_COMMAND}`",
    ]
    if payload.get('status') == 'in-progress':
        lines.append(f"- recommended_finish: `python scripts/operator-attempt.py finish --output-dir {payload.get('relative_output_dir') or 'validation/latest/operator-attempt'} --outcome success`")
    if isinstance(history_update, dict):
        lines.extend([
            '',
            '## History',
            '',
            f"- history_count: {history_update.get('capture_count_after_write')}",
            f"- history_summary: {history_diff.get('summary')}",
        ])
    return '\n'.join(lines).rstrip() + '\n'


def start_attempt(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, doctor_report: dict[str, Any] | None = None, label: str | None = None, planned_command: str | None = None, notes: str | None = None, root: Path = ROOT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    attempt_path = output_dir / 'attempt.json'
    if attempt_path.exists():
        current = _read_json(attempt_path)
        if isinstance(current, dict) and current.get('status') == 'in-progress':
            raise RuntimeError(f'operator attempt already in progress at {attempt_path}')
    snapshot = _build_snapshot(doctor_report=doctor_report, root=root)
    before = snapshot.get('summary') if isinstance(snapshot.get('summary'), dict) else {}
    relative_output_dir = str(output_dir.relative_to(root)) if output_dir.is_relative_to(root) else str(output_dir)
    payload = {
        'schema_version': 1,
        'label': label,
        'status': 'in-progress',
        'started_at': utc_now_iso(),
        'finished_at': None,
        'outcome': None,
        'planned_command': planned_command or before.get('primary_next_command'),
        'notes': notes,
        'history_path': str(history_path),
        'relative_output_dir': relative_output_dir,
        'commands': operator_attempt_commands(),
        'before': before,
        'after': None,
        'attempt_diff': None,
        'history_update': None,
        'history_diff': None,
    }
    _write_snapshot_files(output_dir, 'before', snapshot)
    _write_json(attempt_path, payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    return payload


def finish_attempt(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, doctor_report: dict[str, Any] | None = None, outcome: str, notes: str | None = None, root: Path = ROOT) -> dict[str, Any]:
    attempt_path = output_dir / 'attempt.json'
    if not attempt_path.exists():
        raise FileNotFoundError(f'operator attempt does not exist: {attempt_path}')
    payload = _read_json(attempt_path)
    if not isinstance(payload, dict):
        raise RuntimeError(f'invalid operator attempt payload: {attempt_path}')
    if payload.get('status') != 'in-progress':
        raise RuntimeError(f'operator attempt is not in progress: {attempt_path}')
    snapshot = _build_snapshot(doctor_report=doctor_report, root=root)
    after = snapshot.get('summary') if isinstance(snapshot.get('summary'), dict) else {}
    _write_snapshot_files(output_dir, 'after', snapshot)
    payload['status'] = 'finished'
    payload['finished_at'] = utc_now_iso()
    payload['outcome'] = outcome
    if notes is not None:
        payload['finish_notes'] = notes
    payload['after'] = after
    payload['attempt_diff'] = _attempt_diff(payload.get('before') if isinstance(payload.get('before'), dict) else None, after)
    entry = _history_entry(payload, output_dir)
    history_update = _update_history(entry, path=history_path)
    history_diff = _comparison_to_previous(history_update.get('previous_capture'), entry)
    payload['history_update'] = history_update
    payload['history_diff'] = history_diff
    _write_json(output_dir / 'attempt-diff.json', payload['attempt_diff'])
    _write_json(output_dir / 'history-update.json', history_update.get('history'))
    _write_json(output_dir / 'history-diff.json', history_diff)
    _write_json(attempt_path, payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    return payload


def cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Freeze a before/after operator attempt bundle around one GlassTTY live or profile run.')
    sub = parser.add_subparsers(dest='command')

    start = sub.add_parser('start', help='capture the before-state for an operator attempt')
    start.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    start.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    start.add_argument('--label', default=None)
    start.add_argument('--planned-command', default=None)
    start.add_argument('--notes', default=None)
    start.add_argument('--pretty', action='store_true')

    finish = sub.add_parser('finish', help='capture the after-state for an operator attempt and update the finished-attempt ledger')
    finish.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    finish.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    finish.add_argument('--outcome', required=True, choices=['success', 'failed', 'blocked', 'interrupted'])
    finish.add_argument('--notes', default=None)
    finish.add_argument('--pretty', action='store_true')

    history = sub.add_parser('history', help='inspect the finished operator-attempt ledger')
    history.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    history.add_argument('--pretty', action='store_true')

    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)

    if args.command == 'start':
        payload = start_attempt(output_dir=args.output_dir, history_path=args.history_path, label=args.label, planned_command=args.planned_command, notes=args.notes)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'finish':
        payload = finish_attempt(output_dir=args.output_dir, history_path=args.history_path, outcome=args.outcome, notes=args.notes)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(args.history_path)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = summarize_current_attempt(args.output_dir)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    cli()

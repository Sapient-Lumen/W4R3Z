#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'readiness-report-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'readiness-report-captures.json'
DOCTOR_COMMAND = 'python scripts/doctor.py --pretty'
READINESS_COMMAND = 'python scripts/readiness-report.py --pretty'
READINESS_CAPTURE_COMMAND = 'python scripts/readiness-report.py capture --output-dir validation/latest/readiness-report-capture'
READINESS_HISTORY_COMMAND = 'python scripts/readiness-report.py history --pretty'


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def load_doctor_report(*, root: Path = ROOT) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(root / 'scripts' / 'doctor.py')],
        check=True,
        capture_output=True,
        text=True,
        env=dict(os.environ),
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError('doctor.py did not return a JSON object')
    return payload


def _validation_already_captured(summary: dict[str, Any] | None, latest_capture: dict[str, Any] | None) -> bool:
    if not isinstance(summary, dict) or not isinstance(latest_capture, dict):
        return False
    return (
        latest_capture.get('report_path') == summary.get('path')
        and latest_capture.get('running_step_name') == summary.get('running_step_name')
        and latest_capture.get('latest_completed_step') == summary.get('latest_completed_step')
    )


def _smoke_already_captured(summary: dict[str, Any] | None, latest_capture: dict[str, Any] | None) -> bool:
    if not isinstance(summary, dict) or not isinstance(latest_capture, dict):
        return False
    return latest_capture.get('report_timestamp') == summary.get('report_timestamp')


def _action(priority: int, kind: str, command: str | None, rationale: str, *, section: str | None = None, state: str | None = None) -> dict[str, Any]:
    return {
        'priority': priority,
        'kind': kind,
        'command': command,
        'section': section,
        'state': state,
        'rationale': rationale,
    }


def derive_actions(doctor_report: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    validation = doctor_report.get('validation') if isinstance(doctor_report.get('validation'), dict) else {}
    validation_summary = (validation.get('latest_report') or {}).get('summary') if isinstance(validation.get('latest_report'), dict) else None
    validation_history = validation.get('capture_history') if isinstance(validation.get('capture_history'), dict) else None
    validation_commands = validation.get('commands') if isinstance(validation.get('commands'), dict) else {}
    if isinstance(validation_summary, dict) and validation_summary.get('complete') is False:
        problem = validation_summary.get('running_step_name') or validation_summary.get('required_failed_step') or 'the current required step'
        actions.append(_action(10, 'resume_validate_release', validation_commands.get('resume_latest'), f'The latest validate-release run is incomplete around {problem!r}; resume before starting a fresh umbrella pass.', section='validation', state='incomplete'))
    if isinstance(validation_summary, dict) and validation.get('latest_report', {}).get('exists') and not _validation_already_captured(validation_summary, (validation_history or {}).get('latest_capture')):
        actions.append(_action(20, 'capture_validate_release', validation_commands.get('capture_latest'), 'The current validate-release state is not yet frozen into the validation capture ledger.', section='validation', state='uncaptured'))

    fixture_lab = doctor_report.get('fixture_lab') if isinstance(doctor_report.get('fixture_lab'), dict) else {}
    fixture_summary = (fixture_lab.get('latest_smoke_report') or {}).get('summary') if isinstance(fixture_lab.get('latest_smoke_report'), dict) else None
    fixture_history = fixture_lab.get('smoke_capture_history') if isinstance(fixture_lab.get('smoke_capture_history'), dict) else None
    fixture_commands = fixture_lab.get('commands') if isinstance(fixture_lab.get('commands'), dict) else {}
    if isinstance(fixture_summary, dict) and fixture_lab.get('latest_smoke_report', {}).get('exists') and not _smoke_already_captured(fixture_summary, (fixture_history or {}).get('latest_capture')):
        actions.append(_action(30, 'capture_fixture_smoke', fixture_commands.get('capture_latest'), 'A latest fixture-lab smoke report exists but has not been frozen into the smoke ledger yet.', section='smoke', state='uncaptured'))

    profiles = doctor_report.get('profiles') if isinstance(doctor_report.get('profiles'), dict) else {}
    triage = profiles.get('triage') if isinstance(profiles.get('triage'), dict) else {}
    best_profile = triage.get('best_profile') if isinstance(triage.get('best_profile'), dict) else None
    triage_commands = triage.get('commands') if isinstance(triage.get('commands'), dict) else {}
    if isinstance(best_profile, dict):
        command = best_profile.get('next_command')
        rationale = f"Managed profile triage currently prefers {best_profile.get('name')!r} ({best_profile.get('tier')}, score={best_profile.get('score')})."
        actions.append(_action(40, 'follow_best_profile_lane', command, rationale, section='profiles', state=best_profile.get('tier')))
        commands = best_profile.get('commands') if isinstance(best_profile.get('commands'), dict) else {}
        if best_profile.get('attach_ready') and commands.get('resume_proof'):
            actions.append(_action(35, 'capture_mv3_resume_proof', commands.get('resume_proof'), f"Profile {best_profile.get('name')!r} is attach-ready for MV3 resume proof.", section='profiles', state='attach-ready'))
    fleet_history = profiles.get('fleet_capture_history') if isinstance(profiles.get('fleet_capture_history'), dict) else None
    if isinstance(fleet_history, dict) and not fleet_history.get('capture_count') and triage_commands.get('fleet_capture'):
        actions.append(_action(45, 'capture_profile_fleet', triage_commands.get('fleet_capture'), 'No fleet-level managed-profile snapshot has been frozen yet.', section='profiles', state='missing-fleet-capture'))

    playwright = doctor_report.get('playwright') if isinstance(doctor_report.get('playwright'), dict) else {}
    launch_plan = playwright.get('extension_launch_plan') if isinstance(playwright.get('extension_launch_plan'), dict) else None
    if isinstance(launch_plan, dict) and launch_plan.get('skip_reason') == 'missing-bundled-chromium':
        actions.append(_action(60, 'repair_playwright_browser_inventory', launch_plan.get('recommended_sync_command') or launch_plan.get('recommended_download_command') or launch_plan.get('recommended_import_command'), 'The persistent-context extension lane is blocked because no Playwright-managed browser package is currently available.', section='playwright', state='missing-browser'))

    actions.sort(key=lambda item: (item.get('priority', 999), item.get('kind', '')))
    return actions


def summarize_readiness(doctor_report: dict[str, Any]) -> dict[str, Any]:
    actions = derive_actions(doctor_report)
    validation = doctor_report.get('validation') if isinstance(doctor_report.get('validation'), dict) else {}
    validation_summary = (validation.get('latest_report') or {}).get('summary') if isinstance(validation.get('latest_report'), dict) else None
    fixture_lab = doctor_report.get('fixture_lab') if isinstance(doctor_report.get('fixture_lab'), dict) else {}
    fixture_summary = (fixture_lab.get('latest_smoke_report') or {}).get('summary') if isinstance(fixture_lab.get('latest_smoke_report'), dict) else None
    profiles = doctor_report.get('profiles') if isinstance(doctor_report.get('profiles'), dict) else {}
    triage = profiles.get('triage') if isinstance(profiles.get('triage'), dict) else {}
    best_profile = triage.get('best_profile') if isinstance(triage.get('best_profile'), dict) else None

    if isinstance(validation_summary, dict) and validation_summary.get('complete') is False:
        readiness_grade = 'blocked-by-validation'
    elif isinstance(best_profile, dict) and best_profile.get('attach_ready'):
        readiness_grade = 'live-lane-ready'
    elif isinstance(best_profile, dict):
        readiness_grade = 'profile-lane-ready'
    elif isinstance(fixture_summary, dict) and fixture_summary.get('ok'):
        readiness_grade = 'evidence-ready'
    else:
        readiness_grade = 'diagnostic-only'

    primary_action = actions[0] if actions else None
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'readiness_grade': readiness_grade,
        'primary_next_kind': primary_action.get('kind') if isinstance(primary_action, dict) else None,
        'primary_next_command': primary_action.get('command') if isinstance(primary_action, dict) else None,
        'primary_next_rationale': primary_action.get('rationale') if isinstance(primary_action, dict) else None,
        'action_count': len(actions),
        'actions': actions,
        'validation': {
            'latest': validation_summary,
            'capture_history': validation.get('capture_history'),
        },
        'smoke': {
            'latest': fixture_summary,
            'capture_history': fixture_lab.get('smoke_capture_history'),
        },
        'profiles': {
            'triage': triage,
            'best_profile': best_profile,
            'fleet_capture_history': profiles.get('fleet_capture_history'),
        },
        'commands': {
            'doctor': DOCTOR_COMMAND,
            'capture_latest': READINESS_CAPTURE_COMMAND,
            'capture_history': READINESS_HISTORY_COMMAND,
            'report': READINESS_COMMAND,
        },
    }


def build_readiness_report(*, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    doctor_payload = doctor_report if isinstance(doctor_report, dict) else load_doctor_report(root=root)
    readiness = summarize_readiness(doctor_payload)
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'doctor_report_path': str(root / 'scripts' / 'doctor.py'),
        'doctor': doctor_payload,
        'readiness': readiness,
    }


def _history_entry(report: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    readiness = report.get('readiness') if isinstance(report.get('readiness'), dict) else {}
    best_profile = ((readiness.get('profiles') or {}).get('best_profile') if isinstance(readiness.get('profiles'), dict) else None)
    validation_latest = ((readiness.get('validation') or {}).get('latest') if isinstance(readiness.get('validation'), dict) else None)
    smoke_latest = ((readiness.get('smoke') or {}).get('latest') if isinstance(readiness.get('smoke'), dict) else None)
    return {
        'captured_at': readiness.get('generated_at'),
        'output_dir': str(output_dir),
        'readiness_grade': readiness.get('readiness_grade'),
        'primary_next_kind': readiness.get('primary_next_kind'),
        'primary_next_command': readiness.get('primary_next_command'),
        'best_profile_name': best_profile.get('name') if isinstance(best_profile, dict) else None,
        'validation_complete': validation_latest.get('complete') if isinstance(validation_latest, dict) else None,
        'validation_running_step': validation_latest.get('running_step_name') if isinstance(validation_latest, dict) else None,
        'smoke_report_timestamp': smoke_latest.get('report_timestamp') if isinstance(smoke_latest, dict) else None,
    }


def _capture_diff(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    changed_fields: list[str] = []
    diff: dict[str, Any] = {'changed_fields': changed_fields}
    if not isinstance(previous, dict):
        diff['previous_exists'] = False
        return diff
    diff['previous_exists'] = True
    tracked = [
        'readiness_grade',
        'primary_next_kind',
        'primary_next_command',
        'best_profile_name',
        'validation_complete',
        'validation_running_step',
        'smoke_report_timestamp',
    ]
    for key in tracked:
        if previous.get(key) != current.get(key):
            changed_fields.append(key)
    return diff


def _summary_markdown(report: dict[str, Any]) -> str:
    readiness = report.get('readiness') if isinstance(report.get('readiness'), dict) else {}
    actions = readiness.get('actions') if isinstance(readiness.get('actions'), list) else []
    lines = [
        '# GlassTTY readiness board',
        '',
        f"- grade: `{readiness.get('readiness_grade')}`",
        f"- primary next kind: `{readiness.get('primary_next_kind')}`",
        f"- primary next command: `{readiness.get('primary_next_command')}`",
        '',
        '## Top actions',
        '',
    ]
    if not actions:
        lines.append('- no recommended actions')
    else:
        for action in actions[:8]:
            lines.append(f"- [{action.get('priority')}] `{action.get('kind')}` → `{action.get('command')}` — {action.get('rationale')}")
    lines.extend([
        '',
        '## Commands',
        '',
        f"- report: `{READINESS_COMMAND}`",
        f"- capture: `{READINESS_CAPTURE_COMMAND}`",
        f"- history: `{READINESS_HISTORY_COMMAND}`",
        '',
    ])
    return '\n'.join(lines).rstrip() + '\n'


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    target = path or DEFAULT_HISTORY_PATH
    if not target.exists():
        return {
            'history_path': str(target),
            'exists': False,
            'capture_count': 0,
            'latest_capture': None,
        }
    payload = _read_json(target)
    if not isinstance(payload, dict):
        return {
            'history_path': str(target),
            'exists': True,
            'capture_count': 0,
            'latest_capture': None,
            'error': 'history file is not a JSON object',
        }
    payload.setdefault('history_path', str(target))
    payload.setdefault('exists', True)
    payload.setdefault('capture_count', len(payload.get('entries') or []))
    payload.setdefault('latest_capture', (payload.get('entries') or [None])[-1])
    return payload


def capture_readiness_report(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    report = build_readiness_report(doctor_report=doctor_report, root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    readiness_path = output_dir / 'readiness-report.json'
    doctor_path = output_dir / 'doctor.json'
    summary_path = output_dir / 'SUMMARY.md'
    readiness = report.get('readiness') if isinstance(report.get('readiness'), dict) else {}

    _write_json(readiness_path, report)
    _write_json(doctor_path, report.get('doctor'))
    summary_path.write_text(_summary_markdown(report), encoding='utf-8')

    history = summarize_capture_history(history_path)
    entries = list(history.get('entries') or []) if isinstance(history.get('entries'), list) else []
    current_entry = _history_entry(report, output_dir)
    previous_entry = entries[-1] if entries else None
    diff = _capture_diff(previous_entry if isinstance(previous_entry, dict) else None, current_entry)
    entries.append(current_entry)
    history_payload = {
        'history_path': str(history_path),
        'exists': True,
        'capture_count': len(entries),
        'latest_capture': current_entry,
        'entries': entries,
    }
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', history_payload)
    _write_json(output_dir / 'capture-diff.json', diff)

    bundle = {
        'output_dir': str(output_dir),
        'report_path': str(readiness_path),
        'doctor_path': str(doctor_path),
        'summary_path': str(summary_path),
        'readiness': readiness,
        'history_update': {
            'capture_count_after_write': len(entries),
            'history_path': str(history_path),
        },
        'diff': diff,
    }
    _write_json(output_dir / 'bundle-summary.json', bundle)
    return bundle


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build or capture a condensed GlassTTY readiness board')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Capture the current readiness board into a durable bundle')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')

    history_parser = subparsers.add_parser('history', help='Show readiness capture history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    pretty = bool(getattr(args, 'pretty', False))
    if args.command == 'capture':
        payload = capture_readiness_report(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
    else:
        payload = build_readiness_report()
    print(json.dumps(payload, indent=2 if pretty else None))


if __name__ == '__main__':
    main()

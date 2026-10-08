#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / 'OPENING-CONTRACT.json'
STARTUP_DOC_PATH = ROOT / 'docs' / 'operator-startup.md'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'opening-surface-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'opening-surface-captures.json'
REPORT_COMMAND = 'python scripts/check-opening-contract.py --pretty'
CAPTURE_COMMAND = 'python scripts/check-opening-contract.py capture --output-dir validation/latest/opening-surface-capture'
HISTORY_COMMAND = 'python scripts/check-opening-contract.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/check-opening-contract.py write-root'
ROOT_OUTPUT_PATH = ROOT / 'OPENING-SURFACE-CONFORMANCE.json'


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return sorted(key for key in set(previous) | set(current) if previous.get(key) != current.get(key))


def _contract() -> dict[str, Any]:
    payload = _read_json(CONTRACT_PATH)
    if not isinstance(payload, dict):
        raise RuntimeError('OPENING-CONTRACT.json must contain a JSON object')
    return payload


def _startup_text() -> str:
    return STARTUP_DOC_PATH.read_text(encoding='utf-8') if STARTUP_DOC_PATH.exists() else ''


def _path_mentions(text: str, path: str) -> bool:
    return path in text


def _command_mentions(text: str, command: str) -> bool:
    return command in text


def build_opening_surface_conformance(*, root: Path = ROOT) -> dict[str, Any]:
    contract = _contract()
    startup_text = _startup_text()
    ordered_reads = contract.get('ordered_reads') if isinstance(contract.get('ordered_reads'), list) else []
    commands = contract.get('commands') if isinstance(contract.get('commands'), list) else []
    checked_reads: list[dict[str, Any]] = []
    checked_commands: list[dict[str, Any]] = []
    missing_paths: list[str] = []
    missing_read_mentions: list[str] = []
    missing_command_mentions: list[str] = []
    for item in ordered_reads:
        if not isinstance(item, dict):
            continue
        rel = str(item.get('path') or '').strip()
        if not rel:
            continue
        abs_path = root / rel
        exists = abs_path.exists()
        mentioned = _path_mentions(startup_text, rel)
        checked_reads.append({
            'path': rel,
            'role': item.get('role'),
            'required': bool(item.get('required', True)),
            'exists': exists,
            'mentioned_in_startup_doc': mentioned,
        })
        if item.get('required', True) and not exists:
            missing_paths.append(rel)
        if item.get('required', True) and not mentioned:
            missing_read_mentions.append(rel)
    for item in commands:
        if not isinstance(item, dict):
            continue
        command = str(item.get('command') or '').strip()
        if not command:
            continue
        mentioned = _command_mentions(startup_text, command)
        checked_commands.append({
            'name': item.get('name'),
            'command': command,
            'required': bool(item.get('required', True)),
            'mentioned_in_startup_doc': mentioned,
        })
        if item.get('required', True) and not mentioned:
            missing_command_mentions.append(command)
    warnings: list[str] = []
    if missing_read_mentions:
        warnings.append('operator-startup.md does not mention every required opening read in OPENING-CONTRACT.json')
    if missing_command_mentions:
        warnings.append('operator-startup.md does not mention every required opening command in OPENING-CONTRACT.json')
    if not STARTUP_DOC_PATH.exists():
        warnings.append('docs/operator-startup.md is missing')
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'contract_path': str(CONTRACT_PATH),
        'startup_doc_path': str(STARTUP_DOC_PATH),
        'ordered_reads': checked_reads,
        'commands': checked_commands,
        'required_read_count': sum(1 for item in checked_reads if item.get('required')),
        'required_command_count': sum(1 for item in checked_commands if item.get('required')),
        'missing_paths': missing_paths,
        'missing_read_mentions': missing_read_mentions,
        'missing_command_mentions': missing_command_mentions,
        'warning_count': len(warnings),
        'warnings': warnings,
        'all_valid': not missing_paths and not missing_read_mentions and not missing_command_mentions,
        'write_root_command': WRITE_ROOT_COMMAND,
        'commands_surface': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
        },
    }


def write_root_conformance(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_opening_surface_conformance(root=root)
    _write_json(root / 'OPENING-SURFACE-CONFORMANCE.json', payload)
    return payload


def summarize_capture_history(history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    if not history_path.exists():
        return {'path': str(history_path), 'exists': False, 'capture_count': 0, 'latest_capture': None}
    payload = _read_json(history_path)
    captures = payload.get('captures') if isinstance(payload, dict) else None
    entries = [entry for entry in captures if isinstance(entry, dict)] if isinstance(captures, list) else []
    return {
        'path': str(history_path),
        'exists': True,
        'capture_count': len(entries),
        'latest_capture': entries[-1] if entries else None,
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# Opening surface conformance',
        '',
        f"- generated_at: {payload.get('generated_at')}",
        f"- all_valid: {payload.get('all_valid')}",
        f"- required_read_count: {payload.get('required_read_count')}",
        f"- required_command_count: {payload.get('required_command_count')}",
        f"- warning_count: {payload.get('warning_count')}",
        '',
        '## Required reads',
        '',
    ]
    for item in payload.get('ordered_reads') or []:
        if not item.get('required'):
            continue
        lines.append(f"- `{item.get('path')}` — exists={item.get('exists')}, mentioned_in_startup_doc={item.get('mentioned_in_startup_doc')}")
    lines.extend(['', '## Required commands', ''])
    for item in payload.get('commands') or []:
        if not item.get('required'):
            continue
        lines.append(f"- `{item.get('command')}` — mentioned_in_startup_doc={item.get('mentioned_in_startup_doc')}")
    if payload.get('warnings'):
        lines.extend(['', '## Warnings', ''])
        for warning in payload.get('warnings') or []:
            lines.append(f'- {warning}')
    return '\n'.join(lines) + '\n'


def capture_opening_surface(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, root: Path = ROOT) -> dict[str, Any]:
    payload = write_root_conformance(root=root)
    previous_history = _read_json(history_path) if history_path.exists() else {'captures': []}
    captures = previous_history.get('captures') if isinstance(previous_history, dict) else None
    entries = [entry for entry in captures if isinstance(entry, dict)] if isinstance(captures, list) else []
    previous_latest = entries[-1].get('conformance') if entries else None
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'opening-surface-conformance.json', payload)
    _write_json(output_dir / 'opening-contract.json', _contract())
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    history_payload = previous_history if isinstance(previous_history, dict) else {'captures': []}
    history_entries = history_payload.setdefault('captures', [])
    history_entries.append({
        'captured_at': payload.get('generated_at'),
        'output_dir': str(output_dir),
        'all_valid': payload.get('all_valid'),
        'warning_count': payload.get('warning_count'),
        'conformance': payload,
    })
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path))
    _write_json(output_dir / 'capture-diff.json', {'changed_fields': _changed_fields(previous_latest, payload)})
    return {
        'conformance': payload,
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(history_entries),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Check that GlassTTY opening docs and commands match the declared opening contract.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Freeze the current opening-surface conformance into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true')

    history_parser = subparsers.add_parser('history', help='Show opening-surface capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')

    write_root_parser = subparsers.add_parser('write-root', help='Refresh OPENING-SURFACE-CONFORMANCE.json in the repo root.')
    write_root_parser.add_argument('--pretty', action='store_true')

    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_opening_surface(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_conformance(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_opening_surface_conformance(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

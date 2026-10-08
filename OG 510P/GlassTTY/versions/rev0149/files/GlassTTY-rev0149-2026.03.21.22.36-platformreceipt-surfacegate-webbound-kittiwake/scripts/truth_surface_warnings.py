#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from truth_surface_register import build_truth_surface_register
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _REGISTER_PATH = Path(__file__).resolve().parent / 'truth_surface_register.py'
    _REGISTER_SPEC = importlib.util.spec_from_file_location('truth_surface_register', _REGISTER_PATH)
    _REGISTER_MODULE = importlib.util.module_from_spec(_REGISTER_SPEC)
    assert _REGISTER_SPEC.loader is not None
    _REGISTER_SPEC.loader.exec_module(_REGISTER_MODULE)
    build_truth_surface_register = _REGISTER_MODULE.build_truth_surface_register

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'truth-surface-warnings'
REPORT_COMMAND = 'python scripts/truth-surface-warnings.py --pretty'
CAPTURE_COMMAND = 'python scripts/truth-surface-warnings.py capture --output-dir validation/latest/truth-surface-warnings'

FAMILY_COMMANDS = {
    'opening_surface': 'python scripts/check-opening-contract.py capture --output-dir validation/latest/opening-surface-capture',
    'readiness_report': 'python scripts/readiness-report.py capture --output-dir validation/latest/readiness-report-capture',
    'control_plane_report': 'python scripts/control-plane-report.py capture --output-dir validation/latest/control-plane-report-capture',
    'install_receipt': 'python scripts/install-receipt.py capture --output-dir validation/latest/install-receipt-capture',
    'support_surface': 'python scripts/support-surface-snapshot.py capture --output-dir validation/latest/support-surface-capture',
    'operator_handoff': 'python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff',
}
SEVERITY_ORDER = {'error': 0, 'warning': 1, 'notice': 2}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _warning_severity(message: str) -> str:
    if 'different archive root' in message or 'no current-root capture exists yet' in message or 'no capture history yet' in message:
        return 'error'
    if 'citation' in message or 'contract' in message or 'required artifact' in message:
        return 'warning'
    return 'notice'


def _warning_rationale(message: str) -> str:
    if 'different archive root' in message:
        return 'latest bundled head is stale relative to the current archive root'
    if 'no current-root capture exists yet' in message:
        return 'the family has history, but nothing frozen for this archive root yet'
    if 'no capture history yet' in message:
        return 'the family has never been frozen, so future sessions must rediscover it from live state'
    if 'citation' in message or 'contract' in message:
        return 'the family has a current-root head, but it is not safe as a citation head yet'
    return 'operator attention is still required before treating this family as settled truth'


def build_truth_surface_warnings(*, root: Path = ROOT) -> dict[str, Any]:
    register = build_truth_surface_register(root=root)
    warnings: list[dict[str, Any]] = []
    for family in register.get('families') or []:
        family_key = family.get('family_key') or 'unknown'
        family_label = family.get('label') or family_key
        latest = family.get('latest_operational_head') or {}
        current = family.get('latest_current_root_head') or {}
        for message in family.get('warnings') or []:
            severity = _warning_severity(message)
            warnings.append({
                'family_key': family_key,
                'family_label': family_label,
                'severity': severity,
                'message': message,
                'rationale': _warning_rationale(message),
                'suggested_command': FAMILY_COMMANDS.get(family_key),
                'latest_operational_head_at': latest.get('captured_at'),
                'latest_current_root_head_at': current.get('captured_at'),
            })
    warnings.sort(key=lambda item: (SEVERITY_ORDER.get(item['severity'], 99), item['family_key'], item['message']))
    for index, item in enumerate(warnings, start=1):
        item['priority'] = index
    counts = {
        'warning_count': len(warnings),
        'blocking_warning_count': sum(1 for item in warnings if item['severity'] == 'error'),
        'families_with_warnings': len({item['family_key'] for item in warnings}),
        'severity_counts': {
            'error': sum(1 for item in warnings if item['severity'] == 'error'),
            'warning': sum(1 for item in warnings if item['severity'] == 'warning'),
            'notice': sum(1 for item in warnings if item['severity'] == 'notice'),
        },
    }
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'counts': counts,
        'warnings': warnings,
        'top_warning': warnings[0] if warnings else None,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'truth_surface_register': 'python scripts/truth-surface-register.py --pretty',
            'refresh_all': 'python scripts/refresh-truth-surfaces.py --pretty',
        },
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    counts = payload.get('counts') or {}
    lines = [
        '# Truth-surface warnings',
        '',
        f"- generated_at: {payload.get('generated_at')}",
        f"- warning_count: {counts.get('warning_count')}",
        f"- blocking_warning_count: {counts.get('blocking_warning_count')}",
        '',
        '| priority | severity | family | message | suggested command |',
        '|---:|---|---|---|---|',
    ]
    for item in payload.get('warnings') or []:
        lines.append(
            f"| {item.get('priority')} | {item.get('severity')} | `{item.get('family_key')}` | {item.get('message')} | `{item.get('suggested_command') or '—'}` |"
        )
    if not payload.get('warnings'):
        lines.append('| — | — | — | no truth-surface warnings | — |')
    return '\n'.join(lines) + '\n'


def capture_truth_surface_warnings(*, output_dir: Path = DEFAULT_OUTPUT_DIR, root: Path = ROOT) -> dict[str, Any]:
    payload = build_truth_surface_warnings(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'truth-surface-warnings.json', payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize the current warning queue across GlassTTY truth surfaces.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Write the current truth-surface warnings bundle into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_truth_surface_warnings(output_dir=Path(args.output_dir), root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_truth_surface_warnings(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

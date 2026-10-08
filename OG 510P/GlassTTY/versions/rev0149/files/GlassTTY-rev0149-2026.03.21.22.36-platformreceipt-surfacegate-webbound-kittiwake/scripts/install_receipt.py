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

from doctor import build_report as build_doctor_report
from native_host_report import build_report as build_native_host_report
from readiness_report import build_readiness_report

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / 'extension' / 'manifest.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'install-receipt-capture'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'install-receipts.json'
REPORT_COMMAND = 'python scripts/install-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/install-receipt.py capture --output-dir validation/latest/install-receipt-capture'
HISTORY_COMMAND = 'python scripts/install-receipt.py history --pretty'


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    changed: list[str] = []
    for key in sorted(set(previous) | set(current)):
        if previous.get(key) != current.get(key):
            changed.append(key)
    return changed


def _bootstrap_stage(materialization: dict[str, Any], registration: dict[str, Any], runtime: dict[str, Any], reachability: dict[str, Any]) -> tuple[str, str | None]:
    if not materialization.get('manifest_exists') or not materialization.get('host_wrapper_exists'):
        return 'bootstrap-assets-missing', 'extension manifest or native-host wrapper is missing'
    if not materialization.get('native_messaging_permission_declared'):
        return 'extension-permission-missing', 'extension manifest does not declare nativeMessaging permission'
    if registration.get('parse_failure_targets'):
        return 'native-host-registration-broken', f"native-host manifest parse failures: {', '.join(registration.get('parse_failure_targets') or [])}"
    if registration.get('extension_id_mismatch_targets'):
        return 'native-host-registration-mismatched', f"extension ID not allowed by native-host manifest: {', '.join(registration.get('extension_id_mismatch_targets') or [])}"
    if registration.get('host_path_mismatch_targets'):
        return 'native-host-registration-mismatched', f"native-host manifest points at a different wrapper: {', '.join(registration.get('host_path_mismatch_targets') or [])}"
    if registration.get('missing_targets'):
        return 'native-host-registration-missing', f"install the required native-host targets: {', '.join(registration.get('missing_targets') or [])}"
    if runtime.get('broker_socket_exists'):
        return 'runtime-reachable', None
    if reachability.get('best_profile_attach_ready'):
        return 'registered-awaiting-live-runtime', 'launch the best attach-ready profile and wait for the broker socket'
    return 'registered-runtime-idle', 'native-host registration is present, but no live broker/runtime has been observed yet'


def build_install_receipt(*, doctor_report: dict[str, Any] | None = None, native_host_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    doctor_payload = doctor_report or build_doctor_report()
    native_payload = native_host_report or build_native_host_report()
    readiness = build_readiness_report(doctor_report=doctor_payload)['readiness']
    manifest_exists = MANIFEST_PATH.exists()
    manifest = _read_json(MANIFEST_PATH) if manifest_exists else {}
    permissions = list(manifest.get('permissions') or []) if isinstance(manifest, dict) else []
    background = manifest.get('background') if isinstance(manifest.get('background'), dict) else {}
    side_panel = manifest.get('side_panel') if isinstance(manifest.get('side_panel'), dict) else {}
    recommended_status = native_payload.get('combined_recommended_target_status') if isinstance(native_payload.get('combined_recommended_target_status'), dict) else {}
    runtime_info = native_payload.get('runtime') if isinstance(native_payload.get('runtime'), dict) else {}
    best_profile = (((doctor_payload.get('profiles') or {}).get('triage') or {}).get('best_profile') or {})
    materialization = {
        'manifest_path': str(MANIFEST_PATH),
        'manifest_exists': manifest_exists,
        'extension_version': manifest.get('version') if isinstance(manifest, dict) else None,
        'minimum_chrome_version': manifest.get('minimum_chrome_version') if isinstance(manifest, dict) else None,
        'native_messaging_permission_declared': 'nativeMessaging' in permissions,
        'service_worker_path': background.get('service_worker'),
        'side_panel_path': side_panel.get('default_path'),
        'host_wrapper_path': (((doctor_payload.get('native_host') or {}).get('wrapper') or {}).get('path')),
        'host_wrapper_exists': bool((((doctor_payload.get('native_host') or {}).get('wrapper') or {}).get('exists'))),
        'host_wrapper_executable': bool((((doctor_payload.get('native_host') or {}).get('wrapper') or {}).get('executable'))),
    }
    registration = {
        'extension_id': native_payload.get('extension_id'),
        'default_browser_targets': native_payload.get('all_recommended_targets') or native_payload.get('recommended_targets') or [],
        'playwright_targets': native_payload.get('playwright_recommended_targets') or [],
        'combined_targets': native_payload.get('combined_recommended_targets') or [],
        'ready_targets': recommended_status.get('ready_targets') or [],
        'missing_targets': recommended_status.get('missing_targets') or [],
        'parse_failure_targets': recommended_status.get('parse_failure_targets') or [],
        'extension_id_mismatch_targets': recommended_status.get('extension_id_mismatch_targets') or [],
        'host_path_mismatch_targets': recommended_status.get('host_path_mismatch_targets') or [],
        'suggested_install_command': native_payload.get('suggested_install_command'),
        'suggested_install_commands': native_payload.get('suggested_install_commands') or [],
        'selection_mode': 'combined-browser-matrix',
    }
    runtime = {
        'broker_socket_path': runtime_info.get('socket_path'),
        'broker_socket_exists': bool(runtime_info.get('socket_exists')),
        'lock_path': runtime_info.get('lock_path'),
        'lock_exists': bool(runtime_info.get('lock_exists')),
        'owner_metadata_path': runtime_info.get('metadata_path'),
        'owner_metadata_exists': bool(runtime_info.get('metadata_exists')),
        'owner_metadata': runtime_info.get('owner_metadata'),
        'readiness_grade': readiness.get('readiness_grade'),
        'primary_next_kind': readiness.get('primary_next_kind'),
        'primary_next_command': readiness.get('primary_next_command'),
    }
    reachability = {
        'best_profile_name': best_profile.get('name'),
        'best_profile_tier': best_profile.get('tier'),
        'best_profile_attach_ready': bool(best_profile.get('attach_ready')),
        'doctor_socket_exists': bool(((doctor_payload.get('socket') or {}).get('exists'))),
    }
    bootstrap_stage, primary_blocker = _bootstrap_stage(materialization, registration, runtime, reachability)
    return {
        'project': doctor_payload.get('project', 'GlassTTY'),
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'bootstrap': {
            'stage': bootstrap_stage,
            'primary_blocker': primary_blocker,
            'is_runtime_reachable': bootstrap_stage == 'runtime-reachable',
        },
        'materialization': materialization,
        'registration': registration,
        'runtime': runtime,
        'reachability': reachability,
        'commands': {
            'doctor': 'python scripts/doctor.py --pretty',
            'native_host_report': 'python scripts/native-host-report.py --pretty',
            'readiness_report': 'python scripts/readiness-report.py --pretty',
            'install_receipt': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'suggested_install_command': registration.get('suggested_install_command'),
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


def _summary_markdown(receipt: dict[str, Any]) -> str:
    bootstrap = receipt.get('bootstrap') if isinstance(receipt.get('bootstrap'), dict) else {}
    materialization = receipt.get('materialization') if isinstance(receipt.get('materialization'), dict) else {}
    registration = receipt.get('registration') if isinstance(receipt.get('registration'), dict) else {}
    runtime = receipt.get('runtime') if isinstance(receipt.get('runtime'), dict) else {}
    lines = [
        '# Install receipt',
        '',
        f"- generated_at: {receipt.get('generated_at')}",
        f"- bootstrap_stage: {bootstrap.get('stage')}",
        f"- primary_blocker: {bootstrap.get('primary_blocker')}",
        f"- manifest_exists: {materialization.get('manifest_exists')}",
        f"- host_wrapper_exists: {materialization.get('host_wrapper_exists')}",
        f"- ready_targets: {', '.join(registration.get('ready_targets') or []) or '(none)'}",
        f"- missing_targets: {', '.join(registration.get('missing_targets') or []) or '(none)'}",
        f"- broker_socket_exists: {runtime.get('broker_socket_exists')}",
        f"- readiness_grade: {runtime.get('readiness_grade')}",
        '',
    ]
    if registration.get('suggested_install_command'):
        lines.append(f"- suggested_install_command: `{registration.get('suggested_install_command')}`")
    if runtime.get('primary_next_command'):
        lines.append(f"- primary_next_command: `{runtime.get('primary_next_command')}`")
    return '\n'.join(lines) + '\n'


def capture_install_receipt(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, doctor_report: dict[str, Any] | None = None, native_host_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    doctor_payload = doctor_report or build_doctor_report()
    native_payload = native_host_report or build_native_host_report()
    receipt = build_install_receipt(doctor_report=doctor_payload, native_host_report=native_payload, root=root)
    previous_history = None
    if history_path.exists():
        previous_history = json.loads(history_path.read_text(encoding='utf-8'))
    previous_latest = None
    if isinstance(previous_history, dict):
        captures = previous_history.get('captures')
        if isinstance(captures, list) and captures:
            previous_latest = captures[-1].get('receipt')
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'install-receipt.json', receipt)
    _write_json(output_dir / 'doctor.json', doctor_payload)
    _write_json(output_dir / 'native-host-report.json', native_payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(receipt), encoding='utf-8')
    history_payload = previous_history if isinstance(previous_history, dict) else {'captures': []}
    captures = history_payload.setdefault('captures', [])
    entry = {
        'captured_at': receipt.get('generated_at'),
        'output_dir': str(output_dir),
        'bootstrap_stage': receipt.get('bootstrap', {}).get('stage'),
        'primary_blocker': receipt.get('bootstrap', {}).get('primary_blocker'),
        'receipt': receipt,
    }
    captures.append(entry)
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path))
    _write_json(output_dir / 'capture-diff.json', {'changed_fields': _changed_fields(previous_latest, receipt)})
    return {
        'receipt': receipt,
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(captures),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a GlassTTY install/bootstrap receipt.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Freeze the current install receipt into a bundle.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true')

    history_parser = subparsers.add_parser('history', help='Show install-receipt capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')

    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_install_receipt(output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_install_receipt()
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import readiness_report as readiness_module
from profile_metadata import capture_history_path as profile_capture_history_path

ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'operator-handoff'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'operator-handoff-captures.json'
DEFAULT_READINESS_HISTORY_PATH = ROOT / 'validation' / 'readiness-report-captures.json'

OPERATOR_HANDOFF_REPORT_COMMAND = 'python scripts/operator-handoff.py --pretty'
OPERATOR_HANDOFF_CAPTURE_COMMAND = 'python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff'
OPERATOR_HANDOFF_HISTORY_COMMAND = 'python scripts/operator-handoff.py history --pretty'

STATIC_HANDOFF_FILES = (
    'README.md',
    'ROADMAP.md',
    'PROJECT_MAP.md',
    'STATUS.md',
    'TASKS.md',
    'DECISIONS.md',
    'MEMORY.md',
    'OPENING-CONTRACT.json',
    'OPENING-SURFACE-CONFORMANCE.json',
    'REVISION-RECEIPT.json',
    'REVISION-RECEIPT-CONFORMANCE.json',
    'SUPPORT-PUBLISH-GATE.json',
    'SUPPORT-SOURCE-LOCK.json',
    'SUPPORT-SOURCE-BASELINE.json',
    '.llm/README.md',
    '.llm/SESSION_START.md',
    '.llm/SESSION_END.md',
    '.llm/WORKLOG.jsonl',
)
TRACKED_FIELDS = (
    'readiness_grade',
    'primary_next_kind',
    'primary_next_command',
    'primary_next_section',
    'best_profile_name',
    'validation_complete',
    'validation_running_step_name',
    'fixture_report_timestamp',
    'artifact_count',
    'missing_required_artifact_count',
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def _capture_history_summary(path: Path, *, kind: str = 'entries') -> dict[str, Any]:
    if not path.exists():
        return {'path': str(path), 'exists': False, 'capture_count': 0, 'latest_capture': None}
    payload = _read_json(path)
    captures = payload.get(kind) if isinstance(payload, dict) else None
    entries = [entry for entry in captures if isinstance(entry, dict)] if isinstance(captures, list) else []
    latest = entries[-1] if entries else None
    return {
        'path': str(path),
        'exists': True,
        'capture_count': len(entries),
        'latest_capture': latest,
    }


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


def operator_handoff_commands() -> dict[str, str]:
    return {
        'report': OPERATOR_HANDOFF_REPORT_COMMAND,
        'capture_latest': OPERATOR_HANDOFF_CAPTURE_COMMAND,
        'capture_history': OPERATOR_HANDOFF_HISTORY_COMMAND,
    }


def _add_path_artifact(artifacts: list[dict[str, Any]], *, label: str, path: Path | None, kind: str, required: bool = False, notes: str | None = None, root: Path = ROOT) -> None:
    if path is None:
        return
    absolute = path if path.is_absolute() else root / path
    exists = absolute.exists()
    relative = absolute.relative_to(root) if absolute.is_relative_to(root) else None
    destination = Path('artifacts') / (relative if relative is not None else Path('external') / absolute.name)
    artifacts.append({
        'label': label,
        'kind': kind,
        'path': str(absolute),
        'exists': exists,
        'required': required,
        'notes': notes,
        'copy_destination': str(destination),
    })


def _latest_handoff_doc(root: Path = ROOT) -> Path | None:
    docs_dir = root / 'docs'
    matches = sorted(docs_dir.glob('handoff-rev*.md'))
    return matches[-1] if matches else None


def _maybe_path(value: Any) -> Path | None:
    if isinstance(value, str) and value.strip():
        return Path(value)
    return None


def collect_artifacts(doctor_report: dict[str, Any], *, root: Path = ROOT) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for rel in STATIC_HANDOFF_FILES:
        _add_path_artifact(artifacts, label=f'static:{rel}', path=root / rel, kind='static-file', notes='repo handoff context', root=root)
    latest_handoff = _latest_handoff_doc(root)
    if latest_handoff is not None:
        _add_path_artifact(artifacts, label='docs:latest-handoff', path=latest_handoff, kind='static-file', notes='latest revision handoff note', root=root)

    validation = doctor_report.get('validation') if isinstance(doctor_report.get('validation'), dict) else {}
    latest_validation = validation.get('latest_report') if isinstance(validation.get('latest_report'), dict) else {}
    validation_history = validation.get('capture_history') if isinstance(validation.get('capture_history'), dict) else {}
    validation_report_path = _maybe_path(latest_validation.get('path'))
    if validation_report_path is not None:
        _add_path_artifact(artifacts, label='validation:latest-report', path=validation_report_path, kind='validation-report', required=bool(latest_validation.get('exists')), root=root)
        _add_path_artifact(artifacts, label='validation:latest-summary', path=validation_report_path.with_name('SUMMARY.md'), kind='validation-summary', root=root)
        _add_path_artifact(artifacts, label='validation:current-step', path=validation_report_path.with_name('current_step.json'), kind='validation-running-step', root=root)
        _add_path_artifact(artifacts, label='validation:steps-dir', path=validation_report_path.parent / 'steps', kind='validation-steps-dir', notes='per-step stdout/stderr logs', root=root)
    _add_path_artifact(artifacts, label='validation:capture-history', path=_maybe_path(validation_history.get('path')), kind='history-json', root=root)
    latest_validation_capture = validation_history.get('latest_capture') if isinstance(validation_history.get('latest_capture'), dict) else None
    if isinstance(latest_validation_capture, dict):
        _add_path_artifact(artifacts, label='validation:latest-capture-bundle', path=_maybe_path(latest_validation_capture.get('output_dir')), kind='capture-bundle', root=root)

    fixture_lab = doctor_report.get('fixture_lab') if isinstance(doctor_report.get('fixture_lab'), dict) else {}
    latest_smoke = fixture_lab.get('latest_smoke_report') if isinstance(fixture_lab.get('latest_smoke_report'), dict) else {}
    smoke_history = fixture_lab.get('smoke_capture_history') if isinstance(fixture_lab.get('smoke_capture_history'), dict) else {}
    _add_path_artifact(artifacts, label='smoke:latest-report', path=_maybe_path(latest_smoke.get('path')), kind='smoke-report', required=bool(latest_smoke.get('exists')), root=root)
    _add_path_artifact(artifacts, label='smoke:capture-history', path=_maybe_path(smoke_history.get('path')), kind='history-json', root=root)
    latest_smoke_capture = smoke_history.get('latest_capture') if isinstance(smoke_history.get('latest_capture'), dict) else None
    if isinstance(latest_smoke_capture, dict):
        _add_path_artifact(artifacts, label='smoke:latest-capture-bundle', path=_maybe_path(latest_smoke_capture.get('output_dir')), kind='capture-bundle', root=root)

    profiles = doctor_report.get('profiles') if isinstance(doctor_report.get('profiles'), dict) else {}
    triage = profiles.get('triage') if isinstance(profiles.get('triage'), dict) else {}
    best_profile = triage.get('best_profile') if isinstance(triage.get('best_profile'), dict) else None
    fleet_history = profiles.get('fleet_capture_history') if isinstance(profiles.get('fleet_capture_history'), dict) else {}
    _add_path_artifact(artifacts, label='profiles:fleet-capture-history', path=_maybe_path(fleet_history.get('path')), kind='history-json', root=root)
    latest_fleet_capture = fleet_history.get('latest_capture') if isinstance(fleet_history.get('latest_capture'), dict) else None
    if isinstance(latest_fleet_capture, dict):
        _add_path_artifact(artifacts, label='profiles:latest-fleet-capture-bundle', path=_maybe_path(latest_fleet_capture.get('output_dir')), kind='capture-bundle', root=root)
    if isinstance(best_profile, dict):
        profile_path = _maybe_path(best_profile.get('path'))
        if profile_path is not None:
            _add_path_artifact(artifacts, label='profiles:best-profile-dir', path=profile_path, kind='profile-dir', notes='top-ranked managed profile directory', root=root)
            _add_path_artifact(artifacts, label='profiles:best-profile-metadata', path=profile_path / 'glasstty-profile.json', kind='profile-metadata', root=root)
            _add_path_artifact(artifacts, label='profiles:best-profile-native-host', path=profile_path / 'glasstty-native-host.json', kind='profile-native-host-audit', root=root)
            _add_path_artifact(artifacts, label='profiles:best-profile-devtools-port', path=profile_path / 'DevToolsActivePort', kind='profile-devtools-port', root=root)
            _add_path_artifact(artifacts, label='profiles:best-profile-capture-history', path=profile_capture_history_path(profile_path), kind='history-json', root=root)

    operator_attempt_history_path = root / 'validation' / 'operator-attempts.json'
    _add_path_artifact(artifacts, label='attempts:history', path=operator_attempt_history_path, kind='history-json', notes='finished before/after operator attempt ledger', root=root)
    operator_attempt_dir = root / 'validation' / 'latest' / 'operator-attempt'
    _add_path_artifact(artifacts, label='attempts:current-bundle', path=operator_attempt_dir, kind='attempt-bundle', notes='latest in-progress or finished operator attempt bundle', root=root)
    _add_path_artifact(artifacts, label='attempts:current-attempt-json', path=operator_attempt_dir / 'attempt.json', kind='attempt-json', root=root)

    readiness_history = readiness_module.summarize_capture_history(root / 'validation' / 'readiness-report-captures.json')
    readiness_history_path = readiness_history.get('path') or readiness_history.get('history_path')
    _add_path_artifact(artifacts, label='readiness:capture-history', path=_maybe_path(readiness_history_path), kind='history-json', root=root)
    latest_readiness_capture = readiness_history.get('latest_capture') if isinstance(readiness_history.get('latest_capture'), dict) else None
    if isinstance(latest_readiness_capture, dict):
        _add_path_artifact(artifacts, label='readiness:latest-capture-bundle', path=_maybe_path(latest_readiness_capture.get('output_dir')), kind='capture-bundle', root=root)

    install_receipt_history = _capture_history_summary(root / 'validation' / 'install-receipts.json', kind='captures')
    _add_path_artifact(artifacts, label='install-receipt:history', path=_maybe_path(install_receipt_history.get('path')), kind='history-json', root=root)
    latest_install_receipt_capture = install_receipt_history.get('latest_capture') if isinstance(install_receipt_history.get('latest_capture'), dict) else None
    if isinstance(latest_install_receipt_capture, dict):
        output_dir_value = _maybe_path(latest_install_receipt_capture.get('output_dir'))
        _add_path_artifact(artifacts, label='install-receipt:latest-capture-bundle', path=output_dir_value, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='install-receipt:latest-summary', path=output_dir_value / 'SUMMARY.md' if output_dir_value is not None else None, kind='install-receipt-summary', root=root)

    support_surface_history = _capture_history_summary(root / 'validation' / 'support-surface-captures.json', kind='captures')
    _add_path_artifact(artifacts, label='support-surface:history', path=_maybe_path(support_surface_history.get('path')), kind='history-json', root=root)
    latest_support_surface_capture = support_surface_history.get('latest_capture') if isinstance(support_surface_history.get('latest_capture'), dict) else None
    if isinstance(latest_support_surface_capture, dict):
        output_dir_value = _maybe_path(latest_support_surface_capture.get('output_dir'))
        _add_path_artifact(artifacts, label='support-surface:latest-capture-bundle', path=output_dir_value, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='support-surface:latest-summary', path=output_dir_value / 'SUMMARY.md' if output_dir_value is not None else None, kind='support-surface-summary', root=root)
        _add_path_artifact(artifacts, label='support-surface:latest-contract', path=output_dir_value / 'record-contract.json' if output_dir_value is not None else None, kind='support-surface-contract', root=root)

    opening_surface_history = _capture_history_summary(root / 'validation' / 'opening-surface-captures.json', kind='captures')
    _add_path_artifact(artifacts, label='opening-surface:history', path=_maybe_path(opening_surface_history.get('path')), kind='history-json', root=root)
    latest_opening_surface_capture = opening_surface_history.get('latest_capture') if isinstance(opening_surface_history.get('latest_capture'), dict) else None
    if isinstance(latest_opening_surface_capture, dict):
        output_dir_value = _maybe_path(latest_opening_surface_capture.get('output_dir'))
        _add_path_artifact(artifacts, label='opening-surface:latest-capture-bundle', path=output_dir_value, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='opening-surface:latest-summary', path=output_dir_value / 'SUMMARY.md' if output_dir_value is not None else None, kind='opening-surface-summary', root=root)

    truth_surface_dir = root / 'validation' / 'latest' / 'truth-surface-register'
    _add_path_artifact(artifacts, label='truth-surface:latest-register-dir', path=truth_surface_dir, kind='capture-bundle', root=root)
    _add_path_artifact(artifacts, label='truth-surface:latest-register-json', path=truth_surface_dir / 'truth-surface-register.json', kind='truth-surface-register', root=root)
    _add_path_artifact(artifacts, label='truth-surface:latest-summary', path=truth_surface_dir / 'SUMMARY.md', kind='truth-surface-summary', root=root)

    truth_warning_dir = root / 'validation' / 'latest' / 'truth-surface-warnings'
    _add_path_artifact(artifacts, label='truth-surface:latest-warning-dir', path=truth_warning_dir, kind='capture-bundle', root=root)
    _add_path_artifact(artifacts, label='truth-surface:latest-warning-json', path=truth_warning_dir / 'truth-surface-warnings.json', kind='truth-surface-warnings', root=root)
    _add_path_artifact(artifacts, label='truth-surface:latest-warning-summary', path=truth_warning_dir / 'SUMMARY.md', kind='truth-surface-warning-summary', root=root)

    validation_inventory_dir = root / 'validation' / 'latest' / 'validation-artifact-inventory'
    _add_path_artifact(artifacts, label='validation:artifact-inventory-dir', path=validation_inventory_dir, kind='capture-bundle', root=root)
    _add_path_artifact(artifacts, label='validation:artifact-buckets-json', path=validation_inventory_dir / 'artifact-buckets.json', kind='validation-artifact-inventory', root=root)
    _add_path_artifact(artifacts, label='validation:artifact-buckets-summary', path=validation_inventory_dir / 'SUMMARY.md', kind='validation-artifact-summary', root=root)

    support_bundle_history = _capture_history_summary(root / 'validation' / 'support-bundle-queue-captures.json', kind='captures')
    published_support_history = _capture_history_summary(root / 'validation' / 'published-support-surface-captures.json', kind='captures')
    support_publish_gate_history = _capture_history_summary(root / 'validation' / 'support-publish-gate-captures.json', kind='captures')
    support_source_baseline_history = _capture_history_summary(root / 'validation' / 'support-source-baseline-captures.json', kind='captures')
    _add_path_artifact(artifacts, label='support-bundles:history', path=_maybe_path(support_bundle_history.get('path')), kind='history-json', root=root)
    _add_path_artifact(artifacts, label='published-support:history', path=_maybe_path(published_support_history.get('path')), kind='history-json', root=root)
    _add_path_artifact(artifacts, label='support-publish-gate:history', path=_maybe_path(support_publish_gate_history.get('path')), kind='history-json', root=root)
    _add_path_artifact(artifacts, label='support-source-baseline:history', path=_maybe_path(support_source_baseline_history.get('path')), kind='history-json', root=root)
    _add_path_artifact(artifacts, label='support-publish-gate:root-json', path=root / 'SUPPORT-PUBLISH-GATE.json', kind='support-publish-gate', root=root)
    _add_path_artifact(artifacts, label='support-source-lock:root-json', path=root / 'SUPPORT-SOURCE-LOCK.json', kind='support-source-lock', root=root)
    _add_path_artifact(artifacts, label='support-source-baseline:root-json', path=root / 'SUPPORT-SOURCE-BASELINE.json', kind='support-source-baseline', root=root)
    latest_support_bundle_capture = support_bundle_history.get('latest_capture') if isinstance(support_bundle_history.get('latest_capture'), dict) else None
    latest_support_publish_gate_capture = support_publish_gate_history.get('latest_capture') if isinstance(support_publish_gate_history.get('latest_capture'), dict) else None
    latest_support_source_baseline_capture = support_source_baseline_history.get('latest_capture') if isinstance(support_source_baseline_history.get('latest_capture'), dict) else None
    if isinstance(latest_support_publish_gate_capture, dict):
        output_dir_value = _maybe_path(latest_support_publish_gate_capture.get('output_dir'))
        _add_path_artifact(artifacts, label='support-publish-gate:latest-capture-bundle', path=output_dir_value, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='support-publish-gate:latest-json', path=output_dir_value / 'support-publish-gate.json' if output_dir_value is not None else None, kind='support-publish-gate', root=root)
        _add_path_artifact(artifacts, label='support-publish-gate:latest-summary', path=output_dir_value / 'SUMMARY.md' if output_dir_value is not None else None, kind='support-publish-gate-summary', root=root)
    if isinstance(latest_support_source_baseline_capture, dict):
        output_dir_value = _maybe_path(latest_support_source_baseline_capture.get('output_dir'))
        _add_path_artifact(artifacts, label='support-source-baseline:latest-capture-bundle', path=output_dir_value, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='support-source-baseline:latest-json', path=output_dir_value / 'support-source-baseline.json' if output_dir_value is not None else None, kind='support-source-baseline', root=root)
        _add_path_artifact(artifacts, label='support-source-baseline:latest-summary', path=output_dir_value / 'SUMMARY.md' if output_dir_value is not None else None, kind='support-source-baseline-summary', root=root)
    if isinstance(latest_support_bundle_capture, dict):
        output_dir_value = _maybe_path(latest_support_bundle_capture.get('output_dir'))
        _add_path_artifact(artifacts, label='support-bundles:latest-capture-bundle', path=output_dir_value, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='support-bundles:latest-queue-json', path=output_dir_value / 'support-bundle-queue.json' if output_dir_value is not None else None, kind='support-bundle-queue', root=root)
        _add_path_artifact(artifacts, label='support-bundles:latest-summary', path=output_dir_value / 'SUMMARY.md' if output_dir_value is not None else None, kind='support-bundle-summary', root=root)

    latest_published_support_capture = published_support_history.get('latest_capture') if isinstance(published_support_history.get('latest_capture'), dict) else None
    published_output = _maybe_path(latest_published_support_capture.get('output_dir')) if isinstance(latest_published_support_capture, dict) else None
    if published_output is not None:
        _add_path_artifact(artifacts, label='published-support:latest-capture-bundle', path=published_output, kind='capture-bundle', root=root)
        _add_path_artifact(artifacts, label='published-support:latest-snapshot', path=published_output / 'support-public-surface.json', kind='support-public-surface', root=root)
        _add_path_artifact(artifacts, label='published-support:latest-summary', path=published_output / 'SUMMARY.md', kind='support-public-surface-summary', root=root)
    _add_path_artifact(artifacts, label='support-bundles:contract-root', path=root / 'SUPPORT-BUNDLE-CONTRACT.json', kind='support-bundle-contract', root=root)
    _add_path_artifact(artifacts, label='published-support:root-snapshot', path=root / 'SUPPORT-PUBLIC-SURFACE.json', kind='support-public-surface', root=root)
    _add_path_artifact(artifacts, label='support-bundles:manifests-dir', path=root / 'docs' / 'support-bundles', kind='support-bundle-manifests', root=root)

    return artifacts


def _copy_artifact(artifact: dict[str, Any], *, output_dir: Path) -> dict[str, Any]:
    source = Path(artifact['path'])
    destination = output_dir / artifact['copy_destination']
    copied = False
    file_count = 0
    if artifact.get('exists'):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
            copied = True
            file_count = sum(1 for item in destination.rglob('*') if item.is_file())
        elif source.is_file():
            shutil.copy2(source, destination)
            copied = True
            file_count = 1
    result = dict(artifact)
    result['copied'] = copied
    result['copied_file_count'] = file_count
    result['copied_destination'] = str(destination)
    return result


def _summary_for_history(bundle: dict[str, Any], *, output_dir: Path) -> dict[str, Any]:
    readiness = bundle.get('readiness') if isinstance(bundle.get('readiness'), dict) else {}
    validation = bundle.get('doctor', {}).get('validation', {}) if isinstance(bundle.get('doctor'), dict) else {}
    latest_validation = validation.get('latest_report') if isinstance(validation.get('latest_report'), dict) else {}
    validation_summary = latest_validation.get('summary') if isinstance(latest_validation.get('summary'), dict) else {}
    fixture_lab = bundle.get('doctor', {}).get('fixture_lab', {}) if isinstance(bundle.get('doctor'), dict) else {}
    latest_smoke = fixture_lab.get('latest_smoke_report') if isinstance(fixture_lab.get('latest_smoke_report'), dict) else {}
    smoke_summary = latest_smoke.get('summary') if isinstance(latest_smoke.get('summary'), dict) else {}
    best_profile = bundle.get('doctor', {}).get('profiles', {}).get('triage', {}).get('best_profile') if isinstance(bundle.get('doctor'), dict) else None
    artifacts = bundle.get('artifact_inventory') if isinstance(bundle.get('artifact_inventory'), list) else []
    missing_required = [item for item in artifacts if item.get('required') and not item.get('exists')]
    return {
        'captured_at': bundle.get('captured_at'),
        'output_dir': str(output_dir),
        'summary_markdown_path': str(output_dir / 'SUMMARY.md'),
        'bundle_summary_path': str(output_dir / 'bundle-summary.json'),
        'readiness_grade': readiness.get('readiness_grade'),
        'primary_next_kind': readiness.get('primary_next_kind'),
        'primary_next_command': readiness.get('primary_next_command'),
        'primary_next_section': (readiness.get('actions') or [{}])[0].get('section') if isinstance((readiness.get('actions') or [{}])[0], dict) else None,
        'best_profile_name': best_profile.get('name') if isinstance(best_profile, dict) else None,
        'validation_complete': validation_summary.get('complete'),
        'validation_running_step_name': validation_summary.get('running_step_name'),
        'fixture_report_timestamp': smoke_summary.get('report_timestamp'),
        'artifact_count': len(artifacts),
        'missing_required_artifact_count': len(missing_required),
        'missing_required_artifacts': [item.get('label') for item in missing_required],
    }


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': utc_now_iso(),
        'capture_count': len(entries),
        'entries': entries,
    }


def _comparison_to_previous(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        'has_previous_capture': isinstance(previous, dict),
        'previous_captured_at': previous.get('captured_at') if isinstance(previous, dict) else None,
        'current_captured_at': current.get('captured_at'),
        'changed_fields': [],
    }
    if not isinstance(previous, dict):
        comparison['summary'] = 'no previous operator handoff capture exists yet'
        return comparison
    for key in TRACKED_FIELDS:
        before = previous.get(key)
        after = current.get(key)
        changed = before != after
        comparison[f'{key}_before'] = before
        comparison[f'{key}_after'] = after
        comparison[f'{key}_changed'] = changed
        if changed:
            comparison['changed_fields'].append(key)
    comparison['summary'] = 'operator handoff drift detected' if comparison['changed_fields'] else 'operator handoff matches the previous one on tracked fields'
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


def _write_summary_markdown(bundle: dict[str, Any], *, output_dir: Path) -> Path:
    readiness = bundle.get('readiness') if isinstance(bundle.get('readiness'), dict) else {}
    doctor_report = bundle.get('doctor') if isinstance(bundle.get('doctor'), dict) else {}
    validation_summary = doctor_report.get('validation', {}).get('latest_report', {}).get('summary') if isinstance(doctor_report.get('validation'), dict) else {}
    smoke_summary = doctor_report.get('fixture_lab', {}).get('latest_smoke_report', {}).get('summary') if isinstance(doctor_report.get('fixture_lab'), dict) else {}
    best_profile = doctor_report.get('profiles', {}).get('triage', {}).get('best_profile') if isinstance(doctor_report.get('profiles'), dict) else None
    history_update = bundle.get('history_update') if isinstance(bundle.get('history_update'), dict) else {}
    comparison = bundle.get('comparison_to_previous') if isinstance(bundle.get('comparison_to_previous'), dict) else {}
    artifacts = bundle.get('artifact_inventory') if isinstance(bundle.get('artifact_inventory'), list) else []
    copied = [item for item in artifacts if item.get('copied')]
    missing_required = [item for item in artifacts if item.get('required') and not item.get('exists')]
    lines = [
        '# operator handoff summary',
        '',
        f"- captured_at: {bundle.get('captured_at')}",
        f"- readiness_grade: {readiness.get('readiness_grade')}",
        f"- primary_next_kind: {readiness.get('primary_next_kind')}",
        f"- primary_next_command: `{readiness.get('primary_next_command')}`",
        f"- validation_complete: {validation_summary.get('complete')}",
        f"- validation_running_step_name: {validation_summary.get('running_step_name')}",
        f"- smoke_report_timestamp: {smoke_summary.get('report_timestamp')}",
        f"- best_profile: {best_profile.get('name') if isinstance(best_profile, dict) else None}",
        f"- artifact_count: {len(artifacts)}",
        f"- copied_artifact_count: {len(copied)}",
        f"- missing_required_artifact_count: {len(missing_required)}",
        f"- history_count: {history_update.get('capture_count_after_write')}",
        f"- comparison_summary: {comparison.get('summary')}",
        '',
        '## commands',
        '',
        f"- operator_handoff_report: `{OPERATOR_HANDOFF_REPORT_COMMAND}`",
        f"- operator_handoff_capture: `{OPERATOR_HANDOFF_CAPTURE_COMMAND}`",
        f"- operator_handoff_history: `{OPERATOR_HANDOFF_HISTORY_COMMAND}`",
    ]
    if readiness.get('primary_next_command'):
        lines.append(f"- primary_next_command: `{readiness.get('primary_next_command')}`")
    lines.extend(['', '## copied artifacts', ''])
    if copied:
        for item in copied:
            lines.append(f"- {item.get('label')}: `{item.get('copy_destination')}`")
    else:
        lines.append('- none')
    if missing_required:
        lines.extend(['', '## missing required artifacts', ''])
        for item in missing_required:
            lines.append(f"- {item.get('label')}: `{item.get('path')}`")
    summary_path = output_dir / 'SUMMARY.md'
    summary_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return summary_path


def load_doctor_report(*, root: Path = ROOT) -> dict[str, Any]:
    script = root / 'scripts' / 'doctor.py'
    result = subprocess.run([sys.executable, str(script)], check=True, capture_output=True, text=True, env=dict(os.environ))
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError('doctor.py did not return a JSON object')
    return payload


def build_operator_handoff(*, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    report = doctor_report or load_doctor_report(root=root)
    readiness_report = readiness_module.build_readiness_report(doctor_report=report, root=root)
    readiness = readiness_report.get('readiness') if isinstance(readiness_report, dict) else {}
    artifacts = collect_artifacts(report, root=root)
    return {
        'generated_at': utc_now_iso(),
        'commands': operator_handoff_commands(),
        'doctor': report,
        'readiness': readiness,
        'artifact_inventory': artifacts,
    }


def capture_operator_handoff(*, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, doctor_report: dict[str, Any] | None = None, root: Path = ROOT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_operator_handoff(doctor_report=doctor_report, root=root)
    captured_at = utc_now_iso()
    bundle['captured_at'] = captured_at
    copied_inventory = [_copy_artifact(item, output_dir=output_dir) for item in bundle.get('artifact_inventory', [])]
    bundle['artifact_inventory'] = copied_inventory
    _write_json(output_dir / 'doctor.json', bundle['doctor'])
    _write_json(output_dir / 'readiness-report.json', {'generated_at': captured_at, 'readiness': bundle.get('readiness'), 'commands': operator_handoff_commands()})
    _write_json(output_dir / 'artifact-index.json', copied_inventory)
    summary_entry = _summary_for_history(bundle, output_dir=output_dir)
    history_update = _update_history(summary_entry, path=history_path)
    bundle['history_update'] = history_update
    comparison = _comparison_to_previous(history_update.get('previous_capture'), summary_entry)
    bundle['comparison_to_previous'] = comparison
    _write_json(output_dir / 'bundle-summary.json', summary_entry)
    _write_json(output_dir / 'capture-history.json', history_update.get('history'))
    _write_json(output_dir / 'capture-diff.json', comparison)
    summary_path = _write_summary_markdown(bundle, output_dir=output_dir)
    summary_entry['summary_markdown_path'] = str(summary_path)
    _write_json(output_dir / 'bundle-summary.json', summary_entry)
    bundle['bundle_summary'] = summary_entry
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or capture a durable GlassTTY operator handoff bundle')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='capture the current operator handoff bundle and update its history ledger')
    capture_parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    capture_parser.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    capture_parser.add_argument('--pretty', action='store_true')

    history_parser = subparsers.add_parser('history', help='show the operator handoff capture history')
    history_parser.add_argument('--history-path', type=Path, default=DEFAULT_HISTORY_PATH)
    history_parser.add_argument('--pretty', action='store_true')

    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        bundle = capture_operator_handoff(output_dir=args.output_dir, history_path=args.history_path)
        print(json.dumps(bundle, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(args.history_path)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    bundle = build_operator_handoff()
    print(json.dumps(bundle, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

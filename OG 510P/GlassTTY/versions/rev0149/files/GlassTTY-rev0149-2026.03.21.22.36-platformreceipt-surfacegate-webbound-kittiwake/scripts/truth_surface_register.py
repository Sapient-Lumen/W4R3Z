#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'truth-surface-register'

FAMILIES: dict[str, dict[str, Any]] = {
    'opening_surface': {
        'label': 'Opening surface conformance',
        'history_path': ROOT / 'validation' / 'opening-surface-captures.json',
        'kind': 'captures',
        'bundle_file': 'opening-surface-conformance.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: bool(payload.get('all_valid')),
        'citation_reason': 'opening contract and startup doc agree on required files and commands',
    },
    'readiness_report': {
        'label': 'Readiness report',
        'history_path': ROOT / 'validation' / 'readiness-report-captures.json',
        'kind': 'entries',
        'bundle_file': 'readiness-report.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: True,
        'citation_reason': 'current-root readiness snapshots are honest even when they are blocked',
    },
    'control_plane_report': {
        'label': 'Control-plane report',
        'history_path': ROOT / 'validation' / 'control-plane-report-captures.json',
        'kind': 'captures',
        'bundle_file': 'control-plane-report.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: True,
        'citation_reason': 'current-root control-plane captures remain citable even when they surface blockers',
    },
    'install_receipt': {
        'label': 'Install receipt',
        'history_path': ROOT / 'validation' / 'install-receipts.json',
        'kind': 'captures',
        'bundle_file': 'install-receipt.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: True,
        'citation_reason': 'current-root install receipts are citable bootstrap truth even when registration is missing',
    },
    'support_surface': {
        'label': 'Support-surface snapshot',
        'history_path': ROOT / 'validation' / 'support-surface-captures.json',
        'kind': 'captures',
        'bundle_file': 'support-surface.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: int(summary.get('contract_error_count') or 0) == 0,
        'citation_reason': 'current-root support snapshots need a clean record contract',
    },
    'operator_handoff': {
        'label': 'Operator handoff bundle',
        'history_path': ROOT / 'validation' / 'operator-handoff-captures.json',
        'kind': 'entries',
        'bundle_file': 'doctor.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: int(summary.get('missing_required_artifact_count') or 0) == 0,
        'citation_reason': 'current-root handoff bundles become citation heads only when no required artifact is missing',
    },
    'support_source_baseline': {
        'label': 'Support-source baseline',
        'history_path': ROOT / 'validation' / 'support-source-baseline-captures.json',
        'kind': 'captures',
        'bundle_file': 'support-source-baseline.json',
        'root_field': 'root',
        'citation_test': lambda payload, summary: bool(payload.get('lock_valid')) and int((payload.get('counts') or {}).get('blocking_warning_count') or 0) == 0,
        'citation_reason': 'support-source baseline needs a valid lock and no blocking source-hierarchy warnings',
    },
}
REPORT_COMMAND = 'python scripts/truth-surface-register.py --pretty'
CAPTURE_COMMAND = 'python scripts/truth-surface-register.py capture --output-dir validation/latest/truth-surface-register'


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _entries(path: Path, *, kind: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = _read_json(path)
    values = payload.get(kind) if isinstance(payload, dict) else None
    return [entry for entry in values if isinstance(entry, dict)] if isinstance(values, list) else []


def _bundle_payload(output_dir: Path | None, bundle_file: str) -> dict[str, Any] | None:
    if output_dir is None:
        return None
    path = output_dir / bundle_file
    if not path.exists():
        return None
    payload = _read_json(path)
    return payload if isinstance(payload, dict) else None


def _capture_summary(family_key: str, entry: dict[str, Any], config: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    output_dir_value = entry.get('output_dir')
    output_dir = root / output_dir_value if isinstance(output_dir_value, str) and output_dir_value else None
    payload = _bundle_payload(output_dir, config['bundle_file'])
    payload_root = payload.get(config['root_field']) if isinstance(payload, dict) else None
    payload_root_current = isinstance(payload_root, str) and payload_root == str(root)
    citation_ready = False
    if isinstance(payload, dict) and payload_root_current:
        citation_ready = bool(config['citation_test'](payload, entry))
    summary = {
        'captured_at': entry.get('captured_at'),
        'output_dir': output_dir_value,
        'bundle_file': config['bundle_file'],
        'bundle_exists': bool(output_dir and (output_dir / config['bundle_file']).exists()),
        'payload_root': payload_root,
        'payload_root_is_current': payload_root_current,
        'citation_ready': citation_ready,
    }
    if family_key == 'install_receipt' and isinstance(payload, dict):
        summary['bootstrap_stage'] = ((payload.get('bootstrap') or {}).get('stage'))
    elif family_key == 'support_surface' and isinstance(entry, dict):
        summary['contract_error_count'] = entry.get('contract_error_count')
        summary['surface_count'] = entry.get('surface_count')
    elif family_key == 'control_plane_report' and isinstance(entry, dict):
        summary['readiness_grade'] = entry.get('readiness_grade')
        summary['primary_next_kind'] = entry.get('primary_next_kind')
    elif family_key == 'readiness_report' and isinstance(payload, dict):
        readiness = payload.get('readiness') if isinstance(payload.get('readiness'), dict) else {}
        summary['readiness_grade'] = readiness.get('readiness_grade')
        summary['primary_next_kind'] = readiness.get('primary_next_kind')
    elif family_key == 'opening_surface' and isinstance(payload, dict):
        summary['all_valid'] = payload.get('all_valid')
        summary['warning_count'] = payload.get('warning_count')
    elif family_key == 'operator_handoff':
        summary['missing_required_artifact_count'] = entry.get('missing_required_artifact_count')
        summary['artifact_count'] = entry.get('artifact_count')
        if isinstance(payload, dict):
            validation = payload.get('validation') if isinstance(payload.get('validation'), dict) else {}
            summary['validation_complete'] = (validation.get('latest_report') or {}).get('summary', {}).get('complete') if isinstance(validation.get('latest_report'), dict) else None
    elif family_key == 'support_source_baseline' and isinstance(payload, dict):
        counts = payload.get('counts') if isinstance(payload.get('counts'), dict) else {}
        summary['source_count'] = counts.get('source_count')
        summary['blocking_warning_count'] = counts.get('blocking_warning_count')
        summary['lock_valid'] = payload.get('lock_valid')
    return summary


def build_truth_surface_register(*, root: Path = ROOT) -> dict[str, Any]:
    families: list[dict[str, Any]] = []
    foreign_root_count = 0
    no_capture_count = 0
    no_current_root_capture_count = 0
    no_citation_head_count = 0
    for family_key, config in FAMILIES.items():
        history_path: Path = config['history_path']
        if history_path.is_absolute() and history_path.is_relative_to(ROOT):
            history_path = root / history_path.relative_to(ROOT)
        elif not history_path.is_absolute():
            history_path = root / history_path
        entries = _entries(history_path, kind=config['kind'])
        summaries = [_capture_summary(family_key, entry, config, root=root) for entry in entries]
        latest = summaries[-1] if summaries else None
        current_candidates = [item for item in summaries if item.get('payload_root_is_current')]
        citation_candidates = [item for item in current_candidates if item.get('citation_ready')]
        latest_current = current_candidates[-1] if current_candidates else None
        citation_head = citation_candidates[-1] if citation_candidates else None
        warnings: list[str] = []
        if not summaries:
            warnings.append('no capture history yet')
            no_capture_count += 1
        else:
            if latest and latest.get('payload_root') and not latest.get('payload_root_is_current'):
                warnings.append('latest operational head points at a different archive root')
                foreign_root_count += 1
            if not current_candidates:
                warnings.append('no current-root capture exists yet')
                no_current_root_capture_count += 1
            if latest_current and not citation_head:
                warnings.append(config['citation_reason'])
                no_citation_head_count += 1
        families.append({
            'family_key': family_key,
            'label': config['label'],
            'history_path': str(history_path),
            'history_exists': history_path.exists(),
            'capture_count': len(summaries),
            'latest_operational_head': latest,
            'latest_current_root_head': latest_current,
            'citation_head': citation_head,
            'warnings': warnings,
        })
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'family_count': len(families),
        'families': families,
        'counts': {
            'families_without_capture_history': no_capture_count,
            'families_whose_latest_head_points_at_foreign_root': foreign_root_count,
            'families_without_current_root_capture': no_current_root_capture_count,
            'families_without_citation_head': no_citation_head_count,
        },
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
        },
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# Truth-surface register',
        '',
        f"- generated_at: {payload.get('generated_at')}",
        f"- family_count: {payload.get('family_count')}",
        f"- foreign_root_latest_heads: {(payload.get('counts') or {}).get('families_whose_latest_head_points_at_foreign_root')}",
        f"- families_without_citation_head: {(payload.get('counts') or {}).get('families_without_citation_head')}",
        '',
        '| family | captures | latest operational head | citation head | warnings |',
        '|---|---:|---|---|---|',
    ]
    for family in payload.get('families') or []:
        latest = family.get('latest_operational_head') or {}
        citation = family.get('citation_head') or {}
        latest_label = latest.get('captured_at') or '—'
        if latest and latest.get('payload_root_is_current') is False:
            latest_label += ' (foreign-root)'
        citation_label = citation.get('captured_at') or '—'
        warnings = '; '.join(family.get('warnings') or []) or '—'
        lines.append(f"| `{family.get('family_key')}` | {family.get('capture_count')} | {latest_label} | {citation_label} | {warnings} |")
    return '\n'.join(lines) + '\n'


def capture_truth_surface_register(*, output_dir: Path = DEFAULT_OUTPUT_DIR, root: Path = ROOT) -> dict[str, Any]:
    payload = build_truth_surface_register(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'truth-surface-register.json', payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize the latest operational and citation-ready heads for GlassTTY truth surfaces.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Write the current truth-surface register into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_truth_surface_register(output_dir=Path(args.output_dir), root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_truth_surface_register(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

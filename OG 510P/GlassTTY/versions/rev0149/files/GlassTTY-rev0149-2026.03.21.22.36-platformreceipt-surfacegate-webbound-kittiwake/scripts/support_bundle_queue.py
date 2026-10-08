#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUNDLES_DIR = ROOT / 'docs' / 'support-bundles'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'support-bundle-queue'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'support-bundle-queue-captures.json'


def _default_bundles_dir(root: Path) -> Path:
    return root / 'docs' / 'support-bundles'


def _default_output_dir(root: Path) -> Path:
    return root / 'validation' / 'latest' / 'support-bundle-queue'


def _default_history_path(root: Path) -> Path:
    return root / 'validation' / 'support-bundle-queue-captures.json'
REPORT_COMMAND = 'python scripts/support-bundle-queue.py --pretty'
CAPTURE_COMMAND = 'python scripts/support-bundle-queue.py capture --output-dir validation/latest/support-bundle-queue'
HISTORY_COMMAND = 'python scripts/support-bundle-queue.py history --pretty'

STATUS_ORDER = {
    'published-ready': 0,
    'candidate': 1,
    'hold': 2,
    'published': 3,
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
ALLOWED_STATUSES = set(STATUS_ORDER)
REQUIRED_FIELDS = (
    'bundle_key',
    'bundle_status',
    'surface_key',
    'browser_lane',
    'captured_at',
    'workflows_touched',
    'artifact_refs',
    'support_record',
    'result_summary',
    'publication_decision',
)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError(f'{path} is not a JSON object')
    return payload


def _display_path(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _list_bundle_paths(*, bundles_dir: Path) -> list[Path]:
    if not bundles_dir.exists():
        return []
    paths: list[Path] = []
    for status in ('candidate', 'hold', 'published-ready', 'published'):
        paths.extend(sorted((bundles_dir / status).glob('*.json')))
    return paths


def validate_bundle_manifest(path: Path, *, root: Path = ROOT, bundles_dir: Path | None = None) -> dict[str, Any]:
    bundles_dir = bundles_dir or _default_bundles_dir(root)
    payload = _read_json(path)
    issues: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in payload:
            issues.append(f'missing required field {field!r}')
    status = payload.get('bundle_status')
    expected_status = path.parent.name
    if status not in ALLOWED_STATUSES:
        issues.append(f'unsupported bundle_status {status!r}')
    if status != expected_status:
        issues.append(f'bundle_status {status!r} does not match directory {expected_status!r}')
    workflows = payload.get('workflows_touched')
    if not isinstance(workflows, list) or not workflows:
        issues.append('workflows_touched must be a non-empty list')
    else:
        bad = [item for item in workflows if item not in WORKFLOW_ORDER]
        if bad:
            issues.append(f'unknown workflows_touched entries: {bad}')
    support_record = payload.get('support_record')
    if isinstance(support_record, str):
        support_path = root / support_record
        if not support_path.exists():
            issues.append(f'support_record path {support_record!r} does not exist')
    else:
        issues.append('support_record must be a string path')
    artifact_refs = payload.get('artifact_refs')
    source_refs = payload.get('source_refs')
    normalized_source_refs: list[str] = []
    if source_refs is None:
        source_refs = []
    elif not isinstance(source_refs, list):
        issues.append('source_refs must be a list when present')
        source_refs = []
    for index, source_ref in enumerate(source_refs):
        if not isinstance(source_ref, str) or not source_ref.strip():
            issues.append(f'source_refs[{index}] must be a non-empty string')
            continue
        normalized_source_refs.append(source_ref.strip())
    existing_artifact_count = 0
    missing_artifacts: list[str] = []
    normalized_artifacts: list[dict[str, Any]] = []
    if not isinstance(artifact_refs, list) or not artifact_refs:
        issues.append('artifact_refs must be a non-empty list')
        artifact_refs = []
    for index, artifact in enumerate(artifact_refs):
        if not isinstance(artifact, dict):
            issues.append(f'artifact_refs[{index}] is not an object')
            continue
        rel_path = artifact.get('path')
        if not isinstance(rel_path, str) or not rel_path:
            issues.append(f'artifact_refs[{index}] missing path')
            continue
        abs_path = root / rel_path
        exists = abs_path.exists()
        if exists:
            existing_artifact_count += 1
        else:
            missing_artifacts.append(rel_path)
        normalized_artifacts.append({
            'path': rel_path,
            'kind': artifact.get('kind'),
            'role': artifact.get('role'),
            'exists': exists,
        })
    if missing_artifacts:
        issues.append(f'missing artifact refs: {missing_artifacts}')
    decision = payload.get('publication_decision')
    if not isinstance(decision, dict):
        issues.append('publication_decision must be an object')
        decision = {}
    decision_value = decision.get('decision')
    if isinstance(decision_value, str) and decision_value != status:
        issues.append(f'publication_decision.decision {decision_value!r} does not match bundle_status {status!r}')
    result_summary = payload.get('result_summary')
    if not isinstance(result_summary, dict):
        issues.append('result_summary must be an object')
        result_summary = {}
    return {
        'path': _display_path(path, root=root),
        'bundle_key': payload.get('bundle_key', path.stem),
        'bundle_status': status,
        'surface_key': payload.get('surface_key'),
        'browser_lane': payload.get('browser_lane'),
        'captured_at': payload.get('captured_at'),
        'workflows_touched': workflows or [],
        'workflow_count': len(workflows or []),
        'support_record': support_record,
        'artifact_refs': normalized_artifacts,
        'source_refs': normalized_source_refs,
        'source_ref_count': len(normalized_source_refs),
        'existing_artifact_count': existing_artifact_count,
        'missing_artifact_count': len(missing_artifacts),
        'publication_decision': decision,
        'result_summary': result_summary,
        'issues': issues,
        'ok': not issues,
    }


def _review_priority(item: dict[str, Any]) -> tuple[int, int, int, str]:
    status = item.get('bundle_status', '')
    workflow_pressure = min((WORKFLOW_ORDER.get(workflow, 99) for workflow in item.get('workflows_touched') or []), default=99)
    issue_pressure = 0 if item.get('issues') else 1
    return (STATUS_ORDER.get(status, 99), issue_pressure, workflow_pressure, item.get('bundle_key', ''))


def build_support_bundle_queue(*, root: Path = ROOT, bundles_dir: Path | None = None) -> dict[str, Any]:
    bundles_dir = bundles_dir or _default_bundles_dir(root)
    bundles = [validate_bundle_manifest(path, root=root, bundles_dir=bundles_dir) for path in _list_bundle_paths(bundles_dir=bundles_dir)]
    bundles.sort(key=_review_priority)
    by_status = Counter(bundle.get('bundle_status') or 'unknown' for bundle in bundles)
    by_surface = Counter(bundle.get('surface_key') or 'unknown' for bundle in bundles)
    warnings: list[dict[str, Any]] = []
    review_queue: list[dict[str, Any]] = []
    for bundle in bundles:
        decision = bundle.get('publication_decision') if isinstance(bundle.get('publication_decision'), dict) else {}
        next_action = (bundle.get('result_summary') or {}).get('next_action')
        why = decision.get('why') if isinstance(decision, dict) else None
        review_queue.append({
            'bundle_key': bundle.get('bundle_key'),
            'bundle_status': bundle.get('bundle_status'),
            'surface_key': bundle.get('surface_key'),
            'browser_lane': bundle.get('browser_lane'),
            'issue_count': len(bundle.get('issues') or []),
            'next_action': next_action,
            'why': why,
        })
        for issue in bundle.get('issues') or []:
            warnings.append({
                'bundle_key': bundle.get('bundle_key'),
                'surface_key': bundle.get('surface_key'),
                'severity': 'blocking',
                'message': issue,
            })
        if bundle.get('bundle_status') == 'hold' and not bundle.get('issues'):
            blockers = decision.get('why') if isinstance(decision, dict) else None
            warnings.append({
                'bundle_key': bundle.get('bundle_key'),
                'surface_key': bundle.get('surface_key'),
                'severity': 'advisory',
                'message': '; '.join(blockers) if isinstance(blockers, list) and blockers else 'bundle is intentionally held',
            })
    for index, item in enumerate(review_queue, start=1):
        item['priority'] = index
    counts = {
        'bundle_count': len(bundles),
        'by_status': dict(sorted(by_status.items(), key=lambda item: (STATUS_ORDER.get(item[0], 999), item[0]))),
        'by_surface': dict(sorted(by_surface.items())),
        'warning_count': len(warnings),
        'blocking_warning_count': sum(1 for item in warnings if item.get('severity') == 'blocking'),
    }
    return {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'root': str(root),
        'bundles_dir': _display_path(bundles_dir, root=root),
        'counts': counts,
        'bundles': bundles,
        'review_queue': review_queue[:16],
        'warnings': warnings,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
        },
    }


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def summarize_capture_history(history_path: Path | None = None, *, root: Path = ROOT) -> dict[str, Any]:
    history_path = history_path or _default_history_path(root)
    if not history_path.exists():
        return {'path': str(history_path), 'exists': False, 'capture_count': 0, 'latest_capture': None}
    payload = _read_json(history_path)
    captures = payload.get('captures') if isinstance(payload, dict) else None
    latest = captures[-1] if isinstance(captures, list) and captures else None
    return {
        'path': str(history_path),
        'exists': True,
        'capture_count': len(captures or []),
        'latest_capture': latest,
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# Support bundle queue',
        '',
        f"- generated_at: {payload.get('generated_at')}",
        f"- bundle_count: {(payload.get('counts') or {}).get('bundle_count')}",
        f"- warning_count: {(payload.get('counts') or {}).get('warning_count')}",
        '',
        '| priority | bundle | status | surface | lane | next action |',
        '|---:|---|---|---|---|---|',
    ]
    for item in payload.get('review_queue') or []:
        lines.append(
            f"| {item.get('priority')} | `{item.get('bundle_key')}` | `{item.get('bundle_status')}` | `{item.get('surface_key')}` | `{item.get('browser_lane')}` | {item.get('next_action') or '—'} |"
        )
    if not payload.get('review_queue'):
        lines.append('| 1 | — | — | — | — | no support bundles yet |')
    return '\n'.join(lines) + '\n'


def capture_support_bundle_queue(*, root: Path = ROOT, output_dir: Path | None = None, history_path: Path | None = None) -> dict[str, Any]:
    output_dir = output_dir or _default_output_dir(root)
    history_path = history_path or _default_history_path(root)
    payload = build_support_bundle_queue(root=root)
    previous_history = _read_json(history_path) if history_path.exists() else {'captures': []}
    captures = previous_history.setdefault('captures', [])
    previous_latest = captures[-1].get('report') if captures else None
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'support-bundle-queue.json', payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    captures.append({
        'captured_at': payload.get('generated_at'),
        'output_dir': str(output_dir),
        'bundle_count': (payload.get('counts') or {}).get('bundle_count'),
        'warning_count': (payload.get('counts') or {}).get('warning_count'),
        'top_review_item': (payload.get('review_queue') or [None])[0],
        'report': payload,
    })
    _write_json(history_path, previous_history)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path))
    _write_json(output_dir / 'capture-diff.json', {'changed_fields': _changed_fields(previous_latest, payload)})
    return {
        'report': payload,
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(captures),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize GlassTTY support bundle candidate/published queue state.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Write the current support bundle queue into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--pretty', action='store_true')
    history_parser = subparsers.add_parser('history', help='Show support bundle queue capture history.')
    history_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_support_bundle_queue(root=ROOT, output_dir=Path(args.output_dir))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_support_bundle_queue(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

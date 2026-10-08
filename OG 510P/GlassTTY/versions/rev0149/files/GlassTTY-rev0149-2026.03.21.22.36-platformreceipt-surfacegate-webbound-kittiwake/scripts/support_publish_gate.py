#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from support_bundle_queue import validate_bundle_manifest, _default_bundles_dir, _list_bundle_paths, _read_json, STATUS_ORDER
    from support_records import load_support_records, summarize_support
    from support_source_baseline import load_source_lock, bundle_source_report
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _QUEUE_PATH = Path(__file__).resolve().parent / 'support_bundle_queue.py'
    _QUEUE_SPEC = importlib.util.spec_from_file_location('support_bundle_queue', _QUEUE_PATH)
    _QUEUE_MODULE = importlib.util.module_from_spec(_QUEUE_SPEC)
    assert _QUEUE_SPEC.loader is not None
    _QUEUE_SPEC.loader.exec_module(_QUEUE_MODULE)
    validate_bundle_manifest = _QUEUE_MODULE.validate_bundle_manifest
    _default_bundles_dir = _QUEUE_MODULE._default_bundles_dir
    _list_bundle_paths = _QUEUE_MODULE._list_bundle_paths
    _read_json = _QUEUE_MODULE._read_json
    STATUS_ORDER = _QUEUE_MODULE.STATUS_ORDER

    _RECORDS_PATH = Path(__file__).resolve().parent / 'support_records.py'
    _RECORDS_SPEC = importlib.util.spec_from_file_location('support_records', _RECORDS_PATH)
    _RECORDS_MODULE = importlib.util.module_from_spec(_RECORDS_SPEC)
    assert _RECORDS_SPEC.loader is not None
    _RECORDS_SPEC.loader.exec_module(_RECORDS_MODULE)
    load_support_records = _RECORDS_MODULE.load_support_records
    summarize_support = _RECORDS_MODULE.summarize_support

    _SOURCE_BASELINE_PATH = Path(__file__).resolve().parent / 'support_source_baseline.py'
    _SOURCE_BASELINE_SPEC = importlib.util.spec_from_file_location('support_source_baseline', _SOURCE_BASELINE_PATH)
    _SOURCE_BASELINE_MODULE = importlib.util.module_from_spec(_SOURCE_BASELINE_SPEC)
    assert _SOURCE_BASELINE_SPEC.loader is not None
    _SOURCE_BASELINE_SPEC.loader.exec_module(_SOURCE_BASELINE_MODULE)
    load_source_lock = _SOURCE_BASELINE_MODULE.load_source_lock
    bundle_source_report = _SOURCE_BASELINE_MODULE.bundle_source_report

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'support-publish-gate'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'support-publish-gate-captures.json'
ROOT_OUTPUT_PATH = ROOT / 'SUPPORT-PUBLISH-GATE.json'
REPORT_COMMAND = 'python scripts/support-publish-gate.py --pretty'
CAPTURE_COMMAND = 'python scripts/support-publish-gate.py capture --output-dir validation/latest/support-publish-gate'
HISTORY_COMMAND = 'python scripts/support-publish-gate.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/support-publish-gate.py write-root'
TRANSITION_COMMAND = 'python scripts/support-bundle-transition.py --bundle <bundle-key> --to-state <candidate|hold|published-ready|published>'

PUBLISH_EVIDENCE_KINDS = {
    'support-capture',
    'official-surface-capture',
    'workflow-proof',
    'route-capture',
    'history-witness',
    'latest-turn-capture',
    'submit-proof',
    'live-dom-capture',
}
PUBLISH_EVIDENCE_TOKENS = ('live', 'official', 'route', 'history', 'workflow-proof', 'support-capture', 'latest-turn', 'submit')
READY_RECORD_STATUSES = {'backfilled-from-evidence', 'current'}
ALLOWED_TRANSITIONS = {
    'candidate': {'hold', 'published-ready'},
    'hold': {'candidate', 'published-ready'},
    'published-ready': {'hold', 'published'},
    'published': {'hold'},
}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _display_path(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _surface_map(*, root: Path) -> dict[str, dict[str, Any]]:
    support = summarize_support(load_support_records(root=root))
    return {
        str(item.get('surface_key')): item
        for item in (support.get('surfaces') or [])
        if isinstance(item, dict) and item.get('surface_key')
    }


def _artifact_is_publish_evidence(artifact: dict[str, Any]) -> bool:
    kind = str(artifact.get('kind') or '').strip().lower()
    role = str(artifact.get('role') or '').strip().lower()
    path = str(artifact.get('path') or '').strip().lower()
    if kind in PUBLISH_EVIDENCE_KINDS:
        return True
    haystack = ' '.join(bit for bit in (kind, role, path) if bit)
    return any(token in haystack for token in PUBLISH_EVIDENCE_TOKENS)


def current_heads_for_bundle(*, root: Path = ROOT, support_record: str | None = None) -> dict[str, Any]:
    heads: dict[str, Any] = {}
    if support_record:
        support_record_path = root / support_record
        heads['support_record'] = {
            'path': support_record,
            'exists': support_record_path.exists(),
            'sha256': _sha256_path(support_record_path),
        }
    support_surface_root = root / 'validation' / 'latest' / 'support-surface-capture' / 'support-surface.json'
    heads['support_surface_snapshot'] = {
        'path': _display_path(support_surface_root, root=root),
        'exists': support_surface_root.exists(),
        'sha256': _sha256_path(support_surface_root),
    }
    published_surface_root = root / 'SUPPORT-PUBLIC-SURFACE.json'
    heads['published_support_surface'] = {
        'path': _display_path(published_surface_root, root=root),
        'exists': published_surface_root.exists(),
        'sha256': _sha256_path(published_surface_root),
    }
    revision_receipt_root = root / 'REVISION-RECEIPT.json'
    heads['revision_receipt'] = {
        'path': _display_path(revision_receipt_root, root=root),
        'exists': revision_receipt_root.exists(),
        'sha256': _sha256_path(revision_receipt_root),
    }
    source_lock_root = root / 'SUPPORT-SOURCE-LOCK.json'
    heads['support_source_lock'] = {
        'path': _display_path(source_lock_root, root=root),
        'exists': source_lock_root.exists(),
        'sha256': _sha256_path(source_lock_root),
    }
    source_baseline_root = root / 'SUPPORT-SOURCE-BASELINE.json'
    heads['support_source_baseline'] = {
        'path': _display_path(source_baseline_root, root=root),
        'exists': source_baseline_root.exists(),
        'sha256': _sha256_path(source_baseline_root),
    }
    return heads


def stamp_publish_guard(payload: dict[str, Any], *, root: Path = ROOT, target_state: str | None = None, gate_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    support_record = payload.get('support_record') if isinstance(payload.get('support_record'), str) else None
    guard = {
        'stamped_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'target_state': target_state,
        'current_heads': current_heads_for_bundle(root=root, support_record=support_record),
    }
    if isinstance(gate_summary, dict):
        guard['gate_summary'] = {
            'target_state': gate_summary.get('target_state'),
            'ok': gate_summary.get('ok'),
            'blocking_reasons': gate_summary.get('blocking_reasons') or [],
        }
    payload['publish_guard'] = guard
    return guard


def _head_guard_report(raw_payload: dict[str, Any], *, root: Path, support_record: str | None) -> dict[str, Any]:
    current = current_heads_for_bundle(root=root, support_record=support_record)
    guard = raw_payload.get('publish_guard') if isinstance(raw_payload.get('publish_guard'), dict) else None
    if not isinstance(guard, dict):
        return {
            'present': False,
            'matches_current': False,
            'current_heads': current,
            'mismatches': [{'head': 'publish_guard', 'reason': 'missing publish_guard'}],
        }
    guarded_heads = guard.get('current_heads') if isinstance(guard.get('current_heads'), dict) else {}
    mismatches: list[dict[str, Any]] = []
    for name, current_head in current.items():
        guarded = guarded_heads.get(name) if isinstance(guarded_heads, dict) else None
        if not isinstance(guarded, dict):
            mismatches.append({'head': name, 'reason': 'missing guarded head'})
            continue
        if guarded.get('path') != current_head.get('path'):
            mismatches.append({'head': name, 'reason': 'path mismatch', 'guarded': guarded.get('path'), 'current': current_head.get('path')})
            continue
        if guarded.get('sha256') != current_head.get('sha256'):
            mismatches.append({'head': name, 'reason': 'sha256 mismatch', 'guarded': guarded.get('sha256'), 'current': current_head.get('sha256')})
    return {
        'present': True,
        'matches_current': not mismatches,
        'stamped_at': guard.get('stamped_at'),
        'target_state': guard.get('target_state'),
        'guarded_heads': guarded_heads,
        'current_heads': current,
        'mismatches': mismatches,
    }


def evaluate_bundle_gate(*, bundle_path: Path, root: Path = ROOT, target_state: str = 'published-ready') -> dict[str, Any]:
    validated = validate_bundle_manifest(bundle_path, root=root)
    raw = _read_json(bundle_path)
    surface_key = str(validated.get('surface_key') or '')
    surface = _surface_map(root=root).get(surface_key) or {}
    support_record = raw.get('support_record') if isinstance(raw.get('support_record'), str) else None
    source_lock = load_source_lock(root=root)
    source_report = bundle_source_report(raw, surface_key=surface_key, lock=source_lock)
    lock_review_status = source_lock.get('review_status') if isinstance(source_lock.get('review_status'), dict) else {}
    artifact_refs = validated.get('artifact_refs') or []
    publish_artifacts = [artifact for artifact in artifact_refs if isinstance(artifact, dict) and _artifact_is_publish_evidence(artifact)]
    decision = raw.get('publication_decision') if isinstance(raw.get('publication_decision'), dict) else {}
    claim_scope = raw.get('claim_scope') if isinstance(raw.get('claim_scope'), dict) else {}
    decision_why = [item for item in (decision.get('why') or []) if isinstance(item, str) and item.strip()]
    publication_blockers = [item for item in (claim_scope.get('publication_blockers') or []) if isinstance(item, str) and item.strip()]
    current_state = str(validated.get('bundle_status') or '')
    state_transition_ok = current_state == target_state or target_state in ALLOWED_TRANSITIONS.get(current_state, set())
    head_guard = _head_guard_report(raw, root=root, support_record=support_record)
    checks = [
        {
            'name': 'manifest_valid',
            'ok': bool(validated.get('ok')),
            'message': 'bundle manifest passes the queue/contract validator' if validated.get('ok') else 'bundle manifest still has contract issues',
        },
        {
            'name': 'state_transition_allowed',
            'ok': state_transition_ok,
            'message': f'{current_state} may transition to {target_state}' if state_transition_ok else f'{current_state} cannot transition directly to {target_state}',
        },
        {
            'name': 'support_record_ready',
            'ok': surface.get('record_status') in READY_RECORD_STATUSES,
            'message': f"support record status {surface.get('record_status')!r} is publishable" if surface.get('record_status') in READY_RECORD_STATUSES else f"support record status {surface.get('record_status')!r} is not publishable yet",
        },
        {
            'name': 'claim_scope_clear',
            'ok': not publication_blockers,
            'message': 'claim scope publication blockers are empty' if not publication_blockers else 'claim scope still lists publication blockers',
        },
        {
            'name': 'decision_why_clear',
            'ok': not decision_why,
            'message': 'publication decision has no remaining blockers' if not decision_why else 'publication decision still lists hold/review blockers',
        },
        {
            'name': 'publish_evidence_present',
            'ok': bool(publish_artifacts),
            'message': 'bundle carries direct live/route/history/workflow evidence artifacts' if publish_artifacts else 'bundle lacks direct live/route/history/workflow evidence artifacts',
        },
        {
            'name': 'support_source_lock_review_current',
            'ok': not lock_review_status.get('stale') and not source_lock.get('issues'),
            'message': 'support-source lock review is current under policy' if (not lock_review_status.get('stale') and not source_lock.get('issues')) else 'support-source lock review is stale, missing, or invalid under policy',
        },
        {
            'name': 'required_source_refs_present',
            'ok': not source_report.get('missing_required_source_keys'),
            'message': 'bundle cites all required approved source refs for this surface' if not source_report.get('missing_required_source_keys') else f"bundle is missing required approved source refs: {source_report.get('missing_required_source_keys')}",
        },
        {
            'name': 'required_source_reviews_current',
            'ok': not source_report.get('stale_required_source_keys'),
            'message': 'required approved source refs are current under the review policy' if not source_report.get('stale_required_source_keys') else f"required approved source refs are stale or missing review: {source_report.get('stale_required_source_keys')}",
        },
        {
            'name': 'source_refs_known_and_approved',
            'ok': not source_report.get('unknown_source_keys') and not source_report.get('foreign_source_keys'),
            'message': 'bundle source refs are known and approved for this surface' if (not source_report.get('unknown_source_keys') and not source_report.get('foreign_source_keys')) else 'bundle source refs include unknown or non-approved entries for this surface',
        },
    ]
    if target_state == 'published':
        checks.append({
            'name': 'head_guard_matches_current',
            'ok': bool(head_guard.get('matches_current')),
            'message': 'publish_guard still matches current support/support-surface/revision heads' if head_guard.get('matches_current') else 'publish_guard is missing or stale against current heads',
        })
    required_names = {'manifest_valid', 'state_transition_allowed', 'support_record_ready', 'claim_scope_clear', 'decision_why_clear', 'publish_evidence_present', 'support_source_lock_review_current', 'required_source_refs_present', 'required_source_reviews_current', 'source_refs_known_and_approved'}
    if target_state == 'published':
        required_names.add('head_guard_matches_current')
    blocking_reasons = [check['message'] for check in checks if check['name'] in required_names and not check['ok']]
    return {
        'bundle_key': raw.get('bundle_key') or bundle_path.stem,
        'bundle_path': _display_path(bundle_path, root=root),
        'surface_key': validated.get('surface_key'),
        'current_state': current_state,
        'target_state': target_state,
        'ok': not blocking_reasons,
        'blocking_reasons': blocking_reasons,
        'checks': checks,
        'surface_record_status': surface.get('record_status'),
        'surface_rollout_priority': surface.get('rollout_priority'),
        'support_record': support_record,
        'source_lock_review_status': lock_review_status,
        'source_report': source_report,
        'publish_evidence_artifacts': publish_artifacts,
        'publication_blockers': publication_blockers,
        'decision_why': decision_why,
        'head_guard': head_guard,
        'commands': {
            'transition_bundle': TRANSITION_COMMAND,
            'report': REPORT_COMMAND,
        },
    }


def build_support_publish_gate(*, root: Path = ROOT) -> dict[str, Any]:
    bundles_dir = _default_bundles_dir(root)
    bundle_paths = _list_bundle_paths(bundles_dir=bundles_dir)
    bundles: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for path in bundle_paths:
        ready_gate = evaluate_bundle_gate(bundle_path=path, root=root, target_state='published-ready')
        published_gate = evaluate_bundle_gate(bundle_path=path, root=root, target_state='published')
        entry = {
            'bundle_key': ready_gate.get('bundle_key'),
            'surface_key': ready_gate.get('surface_key'),
            'current_state': ready_gate.get('current_state'),
            'bundle_path': ready_gate.get('bundle_path'),
            'published_ready_gate': ready_gate,
            'published_gate': published_gate,
        }
        bundles.append(entry)
        if not ready_gate.get('ok'):
            warnings.append({
                'bundle_key': ready_gate.get('bundle_key'),
                'surface_key': ready_gate.get('surface_key'),
                'severity': 'blocking',
                'message': '; '.join(ready_gate.get('blocking_reasons') or ['bundle does not clear the published-ready gate']),
            })
        elif not published_gate.get('ok'):
            warnings.append({
                'bundle_key': published_gate.get('bundle_key'),
                'surface_key': published_gate.get('surface_key'),
                'severity': 'advisory',
                'message': '; '.join(published_gate.get('blocking_reasons') or ['bundle is not yet publishable']),
            })
    bundles.sort(key=lambda item: (STATUS_ORDER.get(item.get('current_state', ''), 999), item.get('bundle_key', '')))
    counts = {
        'bundle_count': len(bundles),
        'published_ready_pass_count': sum(1 for item in bundles if (item.get('published_ready_gate') or {}).get('ok')),
        'published_pass_count': sum(1 for item in bundles if (item.get('published_gate') or {}).get('ok')),
        'blocking_warning_count': sum(1 for item in warnings if item.get('severity') == 'blocking'),
        'warning_count': len(warnings),
    }
    return {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'root': str(root),
        'bundles_dir': _display_path(bundles_dir, root=root),
        'counts': counts,
        'bundles': bundles,
        'warnings': warnings,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'transition_bundle': TRANSITION_COMMAND,
        },
    }


def summarize_capture_history(history_path: Path | None = None, *, root: Path = ROOT) -> dict[str, Any]:
    history_path = history_path or DEFAULT_HISTORY_PATH
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


def capture_support_publish_gate(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    report = build_support_publish_gate(root=root)
    previous_history = _read_json(history_path) if history_path.exists() else None
    previous_latest = None
    if isinstance(previous_history, dict):
        captures = previous_history.get('captures')
        if isinstance(captures, list) and captures:
            previous_latest = captures[-1].get('report')
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'support-publish-gate.json', report)
    lines = ['# Support publish gate', '']
    for item in report.get('bundles') or []:
        ready_gate = item.get('published_ready_gate') or {}
        published_gate = item.get('published_gate') or {}
        lines.append(
            f"- `{item.get('bundle_key')}` — state={item.get('current_state')}, published-ready={ready_gate.get('ok')}, published={published_gate.get('ok')}"
        )
    if not report.get('bundles'):
        lines.append('- no support bundles yet')
    (output_dir / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    history_payload = previous_history if isinstance(previous_history, dict) else {'captures': []}
    captures = history_payload.setdefault('captures', [])
    captures.append({
        'captured_at': report.get('generated_at'),
        'output_dir': str(output_dir),
        'counts': report.get('counts'),
        'top_warning': (report.get('warnings') or [None])[0],
        'report': report,
    })
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', summarize_capture_history(history_path, root=root))
    _write_json(output_dir / 'capture-diff.json', {'changed_fields': _changed_fields(previous_latest, report)})
    return {
        'report': report,
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(captures),
        },
    }


def write_root_support_publish_gate(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_support_publish_gate(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Evaluate whether current support bundles may honestly clear published-ready or published gates.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Freeze the current support publish gate into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history', help='Summarize support-publish-gate capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    subparsers.add_parser('write-root', help='Write SUPPORT-PUBLISH-GATE.json in the repo root.')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_support_publish_gate(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path), root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_support_publish_gate(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    payload = build_support_publish_gate(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

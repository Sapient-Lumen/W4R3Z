#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from support_records import load_support_records, ROLLOUT_PRIORITY_ORDER
    from support_source_baseline import load_source_lock
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _RECORDS_PATH = Path(__file__).resolve().parent / 'support_records.py'
    _RECORDS_SPEC = importlib.util.spec_from_file_location('support_records', _RECORDS_PATH)
    _RECORDS_MODULE = importlib.util.module_from_spec(_RECORDS_SPEC)
    assert _RECORDS_SPEC.loader is not None
    _RECORDS_SPEC.loader.exec_module(_RECORDS_MODULE)
    load_support_records = _RECORDS_MODULE.load_support_records
    ROLLOUT_PRIORITY_ORDER = _RECORDS_MODULE.ROLLOUT_PRIORITY_ORDER

    _BASELINE_PATH = Path(__file__).resolve().parent / 'support_source_baseline.py'
    _BASELINE_SPEC = importlib.util.spec_from_file_location('support_source_baseline', _BASELINE_PATH)
    _BASELINE_MODULE = importlib.util.module_from_spec(_BASELINE_SPEC)
    assert _BASELINE_SPEC.loader is not None
    _BASELINE_SPEC.loader.exec_module(_BASELINE_MODULE)
    load_source_lock = _BASELINE_MODULE.load_source_lock

ROOT = Path(__file__).resolve().parent.parent
MATRIX_PATH = ROOT / 'SECOND-ADAPTER-MATRIX.json'
ROOT_OUTPUT_PATH = ROOT / 'SECOND-ADAPTER-REPORT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'second-adapter-report'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'second-adapter-report-captures.json'
REPORT_COMMAND = 'python scripts/second-adapter-report.py --pretty'
CAPTURE_COMMAND = 'python scripts/second-adapter-report.py capture --output-dir validation/latest/second-adapter-report'
HISTORY_COMMAND = 'python scripts/second-adapter-report.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/second-adapter-report.py write-root'


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError(f'{path} is not a JSON object')
    return payload


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _record_map(*, root: Path) -> dict[str, dict[str, Any]]:
    return {record.get('surface_key'): record for record in load_support_records(root=root)}


def _load_matrix(*, root: Path = ROOT) -> dict[str, Any]:
    path = root / 'SECOND-ADAPTER-MATRIX.json'
    if not path.exists():
        raise FileNotFoundError(f'missing matrix file: {path}')
    payload = _read_json(path)
    surfaces = payload.get('surfaces')
    if not isinstance(surfaces, list) or not surfaces:
        raise ValueError('SECOND-ADAPTER-MATRIX.json must contain a non-empty surfaces list')
    return payload


def _fresh_first_party_sources(surface_key: str, *, lock: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fresh: list[dict[str, Any]] = []
    stale_or_missing: list[dict[str, Any]] = []
    for source in lock.get('sources') or []:
        if surface_key not in (source.get('surface_keys') or []):
            continue
        if source.get('tier') != 'first-party-product-surface':
            continue
        review_status = source.get('review_status') if isinstance(source.get('review_status'), dict) else {}
        if review_status.get('stale'):
            stale_or_missing.append(source)
        else:
            fresh.append(source)
    return fresh, stale_or_missing


def _priority_boost(priority: str, *, matrix: dict[str, Any]) -> int:
    boosts = matrix.get('priority_boost') if isinstance(matrix.get('priority_boost'), dict) else {}
    value = boosts.get(priority, 0)
    return int(value) if isinstance(value, int) else 0


def _criterion_weight_map(matrix: dict[str, Any]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in matrix.get('criteria') or []:
        if not isinstance(item, dict):
            continue
        key = item.get('key')
        weight = item.get('weight')
        if isinstance(key, str) and isinstance(weight, int):
            result[key] = weight
    return result


def _criteria_score(surface: dict[str, Any], *, matrix: dict[str, Any]) -> tuple[int, dict[str, int]]:
    weights = _criterion_weight_map(matrix)
    total = 0
    components: dict[str, int] = {}
    for key, weight in weights.items():
        raw = surface.get(key)
        if not isinstance(raw, int):
            continue
        contribution = raw * weight
        components[key] = contribution
        total += contribution
    return total, components


def _source_freshness_score(surface_key: str, *, lock: dict[str, Any], matrix: dict[str, Any]) -> tuple[int, list[str], list[str]]:
    policy = matrix.get('source_freshness') if isinstance(matrix.get('source_freshness'), dict) else {}
    fresh_bonus = int(policy.get('fresh_first_party_bonus', 0)) if isinstance(policy.get('fresh_first_party_bonus'), int) else 0
    stale_penalty = int(policy.get('stale_or_missing_first_party_penalty', 0)) if isinstance(policy.get('stale_or_missing_first_party_penalty'), int) else 0
    fresh, stale_or_missing = _fresh_first_party_sources(surface_key, lock=lock)
    fresh_keys = [item.get('source_key') for item in fresh if item.get('source_key')]
    stale_keys = [item.get('source_key') for item in stale_or_missing if item.get('source_key')]
    if fresh:
        return fresh_bonus, fresh_keys, stale_keys
    return stale_penalty, fresh_keys, stale_keys


def _surface_entry(surface: dict[str, Any], *, record: dict[str, Any] | None, matrix: dict[str, Any], lock: dict[str, Any]) -> dict[str, Any]:
    surface_key = str(surface.get('surface_key'))
    criteria_total, criteria_components = _criteria_score(surface, matrix=matrix)
    rollout_priority = str((record or {}).get('rollout_priority') or 'unknown')
    priority_score = _priority_boost(rollout_priority, matrix=matrix)
    source_score, fresh_source_keys, stale_source_keys = _source_freshness_score(surface_key, lock=lock, matrix=matrix)
    total_score = criteria_total + priority_score + source_score
    excluded = rollout_priority == 'reference adapter'
    eligible_for_lock = bool(fresh_source_keys) and not excluded
    recommendation_posture = 'consider'
    if excluded:
        recommendation_posture = 'exclude-reference-adapter'
    elif not fresh_source_keys:
        recommendation_posture = 'blocked-stale-source-authority'
    elif rollout_priority == 'recommended second adapter':
        recommendation_posture = 'preferred'
    elif rollout_priority == 'phase-2':
        recommendation_posture = 'next-wave'
    reasons: list[str] = []
    if isinstance(surface.get('notes'), list):
        reasons.extend(str(item) for item in surface.get('notes') if str(item).strip())
    if fresh_source_keys:
        reasons.append(f'Fresh first-party source refs are present: {", ".join(fresh_source_keys)}.')
    if stale_source_keys:
        reasons.append(f'Stale or missing first-party source review needs attention: {", ".join(stale_source_keys)}.')
    if record and record.get('next_action'):
        reasons.append(f'Current support-record next action: {record.get("next_action")}.')
    return {
        'surface_key': surface_key,
        'title': (record or {}).get('title', surface_key.title()),
        'excluded_from_second_adapter': excluded,
        'eligible_for_lock': eligible_for_lock,
        'recommendation_posture': recommendation_posture,
        'rollout_priority': rollout_priority,
        'record_status': (record or {}).get('record_status'),
        'default_browser_lane': (record or {}).get('default_browser_lane', surface.get('first_lane')),
        'last_reviewed': (record or {}).get('last_reviewed'),
        'criteria_components': criteria_components,
        'criteria_total': criteria_total,
        'priority_score': priority_score,
        'source_freshness_score': source_score,
        'total_score': total_score,
        'fresh_first_party_source_keys': fresh_source_keys,
        'stale_first_party_source_keys': stale_source_keys,
        'first_lane': surface.get('first_lane'),
        'first_workflow_targets': surface.get('first_workflow_targets') or [],
        'reasons': reasons,
        'next_action': (record or {}).get('next_action'),
    }


def _sort_key(item: dict[str, Any]) -> tuple[int, int, int, int, str]:
    excluded = 1 if item.get('excluded_from_second_adapter') else 0
    eligible = 0 if item.get('eligible_for_lock') else 1
    priority = ROLLOUT_PRIORITY_ORDER.get(str(item.get('rollout_priority') or ''), 99)
    return (excluded, eligible, -int(item.get('total_score') or 0), priority, str(item.get('surface_key') or ''))


def build_second_adapter_report(*, root: Path = ROOT) -> dict[str, Any]:
    matrix = _load_matrix(root=root)
    records = _record_map(root=root)
    lock = load_source_lock(root=root)
    entries = [_surface_entry(surface, record=records.get(surface.get('surface_key')), matrix=matrix, lock=lock) for surface in matrix.get('surfaces') or []]
    entries.sort(key=_sort_key)
    ranked_candidates = [item for item in entries if not item.get('excluded_from_second_adapter')]
    eligible_candidates = [item for item in ranked_candidates if item.get('eligible_for_lock')]
    recommendation = eligible_candidates[0] if eligible_candidates else (ranked_candidates[0] if ranked_candidates else None)
    counts = {
        'candidate_surface_count': len(ranked_candidates),
        'eligible_candidate_count': len(eligible_candidates),
        'excluded_reference_adapter_count': sum(1 for item in entries if item.get('excluded_from_second_adapter')),
        'fresh_first_party_covered_candidates': sum(1 for item in ranked_candidates if item.get('fresh_first_party_source_keys')),
        'stale_or_missing_first_party_candidates': sum(1 for item in ranked_candidates if not item.get('fresh_first_party_source_keys')),
    }
    warnings: list[dict[str, Any]] = []
    if recommendation is None:
        warnings.append({'surface_key': None, 'message': 'No non-reference candidate surfaces are available in SECOND-ADAPTER-MATRIX.json.'})
    for item in ranked_candidates:
        if not item.get('fresh_first_party_source_keys'):
            warnings.append({
                'surface_key': item.get('surface_key'),
                'message': 'Surface lacks a fresh first-party product source review and should not be locked as next adapter without refreshing SUPPORT-SOURCE-LOCK.json.',
            })
    summary_lines = [
        '# Second adapter report',
        '',
        f"- reviewed at: `{datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')}`",
    ]
    if recommendation:
        summary_lines.extend([
            f"- recommended second adapter: `{recommendation['surface_key']}`",
            f"- first lane: `{recommendation.get('first_lane')}`",
            f"- first workflows: `{', '.join(recommendation.get('first_workflow_targets') or [])}`",
        ])
    summary_lines.extend(['', '## Ranked candidates', ''])
    for index, item in enumerate(ranked_candidates, start=1):
        summary_lines.append(f"{index}. `{item['surface_key']}` — total score {item['total_score']} ({item['recommendation_posture']})")
    return {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'matrix_path': str((root / 'SECOND-ADAPTER-MATRIX.json').relative_to(root)),
        'source_lock_path': str((root / 'SUPPORT-SOURCE-LOCK.json').relative_to(root)),
        'counts': counts,
        'recommendation': recommendation,
        'candidates': entries,
        'warnings': warnings,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
        },
        'summary_markdown': '\n'.join(summary_lines) + '\n',
    }


def summarize_capture_history(history_path: Path) -> dict[str, Any]:
    if not history_path.exists():
        return {'capture_count': 0, 'latest_capture': None, 'captures': []}
    payload = _read_json(history_path)
    captures = payload.get('captures') if isinstance(payload.get('captures'), list) else []
    latest_capture = captures[-1] if captures else None
    return {
        'capture_count': len(captures),
        'latest_capture': latest_capture,
        'captures': captures,
    }


def capture_second_adapter_report(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_second_adapter_report(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    previous_payload = _read_json(output_dir / 'second-adapter-report.json') if (output_dir / 'second-adapter-report.json').exists() else None
    _write_json(output_dir / 'second-adapter-report.json', payload)
    (output_dir / 'SUMMARY.md').write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    previous_history = summarize_capture_history(history_path)
    previous_capture = previous_history.get('latest_capture')
    captures = list(previous_history.get('captures') or [])
    capture_entry = {
        'captured_at': payload['generated_at'],
        'output_dir': str(output_dir.relative_to(root)),
        'recommended_surface_key': (payload.get('recommendation') or {}).get('surface_key'),
        'candidate_surface_count': payload['counts']['candidate_surface_count'],
    }
    captures.append(capture_entry)
    _write_json(history_path, {'captures': captures})
    history_summary = summarize_capture_history(history_path)
    diff = {
        'previous_capture': previous_capture,
        'changed_fields': _changed_fields(previous_payload if isinstance(previous_payload, dict) else None, payload),
    }
    _write_json(output_dir / 'capture-history.json', history_summary)
    _write_json(output_dir / 'capture-diff.json', diff)
    result = dict(payload)
    result['history_update'] = {'capture_count_after_write': history_summary['capture_count'], 'latest_capture': history_summary['latest_capture']}
    result['capture_diff'] = diff
    _write_json(output_dir / 'second-adapter-report.json', result)
    return result


def write_root_second_adapter_report(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_second_adapter_report(root=root)
    _write_json(root / 'SECOND-ADAPTER-REPORT.json', payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build the GlassTTY second-adapter report')
    parser.add_argument('--root', default=str(ROOT), help='Repo root to inspect')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Write the report bundle and update capture history')
    capture_parser.add_argument('--output-dir', default=None, help='Output directory for the capture bundle')
    capture_parser.add_argument('--history-path', default=None, help='History JSON path')

    history_parser = subparsers.add_parser('history', help='Show capture history')
    history_parser.add_argument('--history-path', default=None, help='History JSON path')

    subparsers.add_parser('write-root', help='Write SECOND-ADAPTER-REPORT.json at the repo root')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.command == 'capture':
        output_dir = Path(args.output_dir).resolve() if args.output_dir else root / 'validation' / 'latest' / 'second-adapter-report'
        history_path = Path(args.history_path).resolve() if args.history_path else root / 'validation' / 'second-adapter-report-captures.json'
        payload = capture_second_adapter_report(root=root, output_dir=output_dir, history_path=history_path)
    elif args.command == 'history':
        history_path = Path(args.history_path).resolve() if args.history_path else root / 'validation' / 'second-adapter-report-captures.json'
        payload = summarize_capture_history(history_path)
    elif args.command == 'write-root':
        payload = write_root_second_adapter_report(root=root)
    else:
        payload = build_second_adapter_report(root=root)

    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))


if __name__ == '__main__':
    main()

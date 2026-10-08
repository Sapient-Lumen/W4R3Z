#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from second_adapter_report import build_second_adapter_report
    from support_records import load_support_records
    from support_source_baseline import load_source_lock
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _REPORT_PATH = Path(__file__).resolve().parent / 'second_adapter_report.py'
    _REPORT_SPEC = importlib.util.spec_from_file_location('second_adapter_report', _REPORT_PATH)
    _REPORT_MODULE = importlib.util.module_from_spec(_REPORT_SPEC)
    assert _REPORT_SPEC.loader is not None
    _REPORT_SPEC.loader.exec_module(_REPORT_MODULE)
    build_second_adapter_report = _REPORT_MODULE.build_second_adapter_report

    _RECORDS_PATH = Path(__file__).resolve().parent / 'support_records.py'
    _RECORDS_SPEC = importlib.util.spec_from_file_location('support_records', _RECORDS_PATH)
    _RECORDS_MODULE = importlib.util.module_from_spec(_RECORDS_SPEC)
    assert _RECORDS_SPEC.loader is not None
    _RECORDS_SPEC.loader.exec_module(_RECORDS_MODULE)
    load_support_records = _RECORDS_MODULE.load_support_records

    _SOURCE_PATH = Path(__file__).resolve().parent / 'support_source_baseline.py'
    _SOURCE_SPEC = importlib.util.spec_from_file_location('support_source_baseline', _SOURCE_PATH)
    _SOURCE_MODULE = importlib.util.module_from_spec(_SOURCE_SPEC)
    assert _SOURCE_SPEC.loader is not None
    _SOURCE_SPEC.loader.exec_module(_SOURCE_MODULE)
    load_source_lock = _SOURCE_MODULE.load_source_lock

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'SECOND-ADAPTER-BRIEF.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'second-adapter-brief'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'second-adapter-brief-captures.json'
REPORT_COMMAND = 'python scripts/second-adapter-brief.py --pretty'
CAPTURE_COMMAND = 'python scripts/second-adapter-brief.py capture --output-dir validation/latest/second-adapter-brief'
HISTORY_COMMAND = 'python scripts/second-adapter-brief.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/second-adapter-brief.py write-root'
CORE_BROWSER_SUBSTRATE_KEYS = {'shared-browser-substrate', 'shared', 'all-surfaces'}


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


def _workflow_map(record: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in (record or {}).get('workflow_rows') or []:
        workflow = row.get('workflow')
        if isinstance(workflow, str) and workflow:
            result[workflow] = row
    return result


def _source_groups(surface_key: str, *, lock: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    product_sources: list[dict[str, Any]] = []
    shared_sources: list[dict[str, Any]] = []
    for source in lock.get('sources') or []:
        if not isinstance(source, dict):
            continue
        surface_keys = {str(item) for item in source.get('surface_keys') or [] if str(item).strip()}
        if surface_key in surface_keys and source.get('tier') == 'first-party-product-surface':
            product_sources.append(source)
        if CORE_BROWSER_SUBSTRATE_KEYS.intersection(surface_keys):
            shared_sources.append(source)
    product_sources.sort(key=lambda item: (not bool(item.get('required_for_publication')), str(item.get('source_key') or '')))
    shared_sources.sort(key=lambda item: str(item.get('source_key') or ''))
    return {
        'first_party_product_sources': product_sources,
        'shared_browser_substrate_sources': shared_sources,
    }


def _primary_route_source(product_sources: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not product_sources:
        return None
    for source in product_sources:
        claim_uses = {str(item).strip().lower() for item in source.get('claim_uses') or [] if str(item).strip()}
        url = str(source.get('url') or '')
        if 'direct browser route' in claim_uses or 'pre-login baseline posture' in claim_uses or 'chatgpt.com' in url:
            return source
    return product_sources[0]


def _phase_rows(workflow_map: dict[str, dict[str, Any]], workflows: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for workflow in workflows:
        row = workflow_map.get(workflow)
        rows.append({
            'workflow': workflow,
            'current_tier': (row or {}).get('current_tier'),
            'lane': (row or {}).get('lane'),
            'evidence_posture': (row or {}).get('evidence_posture'),
            'promotion_requirement': (row or {}).get('promotion_requirement'),
        })
    return rows


def _phase(
    key: str,
    title: str,
    *,
    workflows: list[str],
    workflow_map: dict[str, dict[str, Any]],
    goal: str,
    actions: list[str],
    exit_criteria: list[str],
    source_keys: list[str],
    artifact_targets: list[str],
) -> dict[str, Any]:
    return {
        'phase_key': key,
        'title': title,
        'goal': goal,
        'workflows': workflows,
        'workflow_rows': _phase_rows(workflow_map, workflows),
        'actions': actions,
        'exit_criteria': exit_criteria,
        'source_keys': source_keys,
        'artifact_targets': artifact_targets,
    }


def build_second_adapter_brief(*, root: Path = ROOT, surface_key: str | None = None) -> dict[str, Any]:
    report = build_second_adapter_report(root=root)
    recommendation = report.get('recommendation') if isinstance(report.get('recommendation'), dict) else None
    selected_surface_key = surface_key or ((recommendation or {}).get('surface_key'))
    if not isinstance(selected_surface_key, str) or not selected_surface_key:
        raise ValueError('No second-adapter recommendation is available to brief.')
    candidates = report.get('candidates') if isinstance(report.get('candidates'), list) else []
    candidate = next((item for item in candidates if item.get('surface_key') == selected_surface_key), None)
    if not isinstance(candidate, dict):
        raise ValueError(f'No second-adapter candidate found for {selected_surface_key!r}')
    record = _record_map(root=root).get(selected_surface_key)
    workflow_map = _workflow_map(record)
    lock = load_source_lock(root=root)
    source_groups = _source_groups(selected_surface_key, lock=lock)
    product_sources = source_groups['first_party_product_sources']
    shared_sources = source_groups['shared_browser_substrate_sources']
    primary_route_source = _primary_route_source(product_sources)
    primary_route = primary_route_source.get('url') if isinstance(primary_route_source, dict) else None
    product_source_keys = [str(item.get('source_key')) for item in product_sources if item.get('source_key')]
    shared_source_keys = [str(item.get('source_key')) for item in shared_sources if item.get('source_key')]

    phases = [
        _phase(
            'route-anchor-baseline',
            'Route anchor and baseline witness',
            workflows=['surface-detect', 'receiver-resolve'],
            workflow_map=workflow_map,
            goal='Prove the session is on the intended official browser surface and record the initial route, gate, and receiver posture.',
            actions=[
                'Open the plain browser route for the selected surface before branching into richer modes.',
                'Freeze the URL, title, logged-in or logged-out posture, and any visible surface-identifying text.',
                'Capture one route/history witness and one screenshot before touching the composer.',
            ],
            exit_criteria=[
                'At least one route witness artifact identifies the expected official surface.',
                'Receiver posture is explicit: ready, gated by login, or blocked by an overlay worth preserving.',
            ],
            source_keys=product_source_keys,
            artifact_targets=['route-witness.json', 'surface-screenshot.png', 'receiver-posture.md'],
        ),
        _phase(
            'composer-baseline',
            'Composer discovery and writability proof',
            workflows=['composer-read', 'composer-write'],
            workflow_map=workflow_map,
            goal='Find a writable composer using accessible, user-facing semantics before relying on brittle DOM details.',
            actions=[
                'Probe textbox-like candidates first, then fallback to textarea or contenteditable candidates.',
                'Record both the winning composer path and at least one failed candidate so drift is reviewable.',
                'Verify that the composer can be read and written without yet sending a turn.',
            ],
            exit_criteria=[
                'One stable composer candidate is readable and writable.',
                'The bundle preserves enough detail to explain why alternate candidates failed.',
            ],
            source_keys=product_source_keys,
            artifact_targets=['composer-candidates.json', 'composer-before.txt', 'composer-after.txt'],
        ),
        _phase(
            'submit-and-readback',
            'Submit one harmless probe and read the latest turn',
            workflows=['turn-submit', 'generation-read', 'latest-turn-read'],
            workflow_map=workflow_map,
            goal='Prove the minimal generic chat lane: submit a benign probe turn, observe generation, and read back the latest assistant turn.',
            actions=[
                'Use a harmless, low-ambiguity probe prompt so submit/readback failures are easier to interpret.',
                'Capture submit affordance evidence separately from latest-turn extraction evidence.',
                'Freeze both streaming or intermediate state and the stable latest-turn readback when available.',
            ],
            exit_criteria=[
                'One probe turn is submitted or a concrete blocking failure is captured with enough evidence to debug.',
                'The latest visible assistant turn is extracted from the main conversation region or the failure is localized clearly.',
            ],
            source_keys=product_source_keys + shared_source_keys,
            artifact_targets=['probe-prompt.txt', 'submit-evidence.json', 'latest-turn.txt', 'generation-timeline.json'],
        ),
        _phase(
            'bundle-and-promote',
            'Freeze the first support bundle and promotion evidence',
            workflows=['support-capture'],
            workflow_map=workflow_map,
            goal='Turn the first baseline into a named support bundle that can move the record beyond seeded planning.',
            actions=[
                'Package the baseline, compose, submit, and readback artifacts under one named bundle.',
                'Cite the current approved first-party source refs and the shared browser-substrate refs used for runtime semantics.',
                'Run support-source baseline, support-publish gate, and revision/contract checks after packaging.',
            ],
            exit_criteria=[
                'A named support bundle exists with cited source refs and artifact refs.',
                'The support record can move from seeded toward backfilled-from-evidence with an honest caveat set.',
            ],
            source_keys=product_source_keys + shared_source_keys,
            artifact_targets=['bundle-manifest.json', 'promotion-notes.md', 'gate-results.json'],
        ),
    ]

    selector_strategy = {
        'principles': [
            'Prefer accessible, user-facing locators before DOM-shape or CSS-class selectors.',
            'Keep route detection, composer discovery, submit affordance, and latest-turn extraction as separate probes so drift is easier to localize.',
            'Preserve at least one failed candidate and one successful candidate in the first real bundle.',
        ],
        'composer_candidates': [
            'accessible textbox locator',
            'textarea',
            '[contenteditable="true"]',
        ],
        'submit_candidates': [
            'visible button with accessible name resembling Send or Submit',
            'keyboard submit only after writable composer proof exists',
        ],
        'latest_turn_candidates': [
            'main conversation region',
            'latest visible assistant turn grouping inside that region',
        ],
    }

    summary_lines = [
        '# Second adapter brief',
        '',
        f"- generated_at: `{datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')}`",
        f"- selected surface: `{selected_surface_key}`",
        f"- primary route hint: `{primary_route}`" if primary_route else '- primary route hint: unavailable',
        f"- first workflows: `{', '.join(candidate.get('first_workflow_targets') or [])}`",
        '',
        '## Ordered phases',
        '',
    ]
    for index, phase in enumerate(phases, start=1):
        summary_lines.append(f"{index}. `{phase['phase_key']}` — {phase['goal']}")

    return {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'source': {
            'second_adapter_report_path': str((root / 'SECOND-ADAPTER-REPORT.json').relative_to(root)),
            'source_lock_path': str((root / 'SUPPORT-SOURCE-LOCK.json').relative_to(root)),
        },
        'selected_surface': {
            'surface_key': selected_surface_key,
            'title': candidate.get('title'),
            'rollout_priority': candidate.get('rollout_priority'),
            'record_status': candidate.get('record_status'),
            'default_browser_lane': candidate.get('default_browser_lane'),
            'first_lane': candidate.get('first_lane'),
            'first_workflow_targets': candidate.get('first_workflow_targets') or [],
            'recommendation_posture': candidate.get('recommendation_posture'),
            'total_score': candidate.get('total_score'),
            'primary_route_hint': primary_route,
        },
        'source_groups': {
            'first_party_product_sources': product_sources,
            'shared_browser_substrate_sources': shared_sources,
        },
        'selector_strategy': selector_strategy,
        'risk_controls': {
            'known_blockers': (record or {}).get('known_blockers') or [],
            'notes': [
                'Run the first proof on the plain chat lane before branching into richer feature modes.',
                'Treat the first useful blocked run as evidence rather than wasted work.',
                'Keep support claims tied to named artifacts and current source refs.',
            ],
        },
        'promotion_path': {
            'current_record_status': (record or {}).get('record_status'),
            'target_after_first_bundle': 'backfilled-from-evidence',
            'later_target': 'current',
            'conditions': [
                'named support bundle exists',
                'bundle cites approved current source refs',
                'workflow caveats and blockers remain explicit',
            ],
        },
        'phases': phases,
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


def capture_second_adapter_brief(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH, surface_key: str | None = None) -> dict[str, Any]:
    payload = build_second_adapter_brief(root=root, surface_key=surface_key)
    output_dir.mkdir(parents=True, exist_ok=True)
    previous_payload = _read_json(output_dir / 'second-adapter-brief.json') if (output_dir / 'second-adapter-brief.json').exists() else None
    _write_json(output_dir / 'second-adapter-brief.json', payload)
    (output_dir / 'SUMMARY.md').write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    previous_history = summarize_capture_history(history_path)
    previous_capture = previous_history.get('latest_capture')
    captures = list(previous_history.get('captures') or [])
    capture_entry = {
        'captured_at': payload['generated_at'],
        'output_dir': str(output_dir.relative_to(root)),
        'surface_key': payload['selected_surface']['surface_key'],
        'primary_route_hint': payload['selected_surface']['primary_route_hint'],
        'phase_count': len(payload.get('phases') or []),
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
    _write_json(output_dir / 'second-adapter-brief.json', result)
    return result


def write_root_second_adapter_brief(*, root: Path = ROOT, surface_key: str | None = None) -> dict[str, Any]:
    payload = build_second_adapter_brief(root=root, surface_key=surface_key)
    _write_json(root / 'SECOND-ADAPTER-BRIEF.json', payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build the GlassTTY second-adapter execution brief')
    parser.add_argument('--root', default=str(ROOT), help='Repo root to inspect')
    parser.add_argument('--surface-key', default=None, help='Optional surface key override')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    subparsers = parser.add_subparsers(dest='command')

    capture_parser = subparsers.add_parser('capture', help='Write the brief bundle and update capture history')
    capture_parser.add_argument('--output-dir', default=None, help='Output directory for the capture bundle')
    capture_parser.add_argument('--history-path', default=None, help='History JSON path')
    capture_parser.add_argument('--surface-key', default=None, help='Optional surface key override')

    history_parser = subparsers.add_parser('history', help='Show capture history')
    history_parser.add_argument('--history-path', default=None, help='History JSON path')

    write_root_parser = subparsers.add_parser('write-root', help='Write SECOND-ADAPTER-BRIEF.json at the repo root')
    write_root_parser.add_argument('--surface-key', default=None, help='Optional surface key override')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.command == 'capture':
        output_dir = Path(args.output_dir).resolve() if args.output_dir else root / 'validation' / 'latest' / 'second-adapter-brief'
        history_path = Path(args.history_path).resolve() if args.history_path else root / 'validation' / 'second-adapter-brief-captures.json'
        payload = capture_second_adapter_brief(root=root, output_dir=output_dir, history_path=history_path, surface_key=args.surface_key)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        history_path = Path(args.history_path).resolve() if args.history_path else root / 'validation' / 'second-adapter-brief-captures.json'
        print(json.dumps(summarize_capture_history(history_path), indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_second_adapter_brief(root=root, surface_key=args.surface_key)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return

    payload = build_second_adapter_brief(root=root, surface_key=args.surface_key)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()

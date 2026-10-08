#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_card.json'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_path(path: Path) -> str:
    if not path.exists():
        return 'MISSING'
    return _sha256_bytes(path.read_bytes())


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _classify(report: dict[str, Any], observed_hashes: dict[str, str]) -> dict[str, Any]:
    target_files = report['target_files']
    states = report['state_plans']
    exact = next((state for state in states if state['file_hashes'] == observed_hashes), None)
    scores: list[dict[str, Any]] = []
    for state in states:
        matching_files = [rel for rel in target_files if state['file_hashes'][rel] == observed_hashes[rel]]
        differing_files = [rel for rel in target_files if state['file_hashes'][rel] != observed_hashes[rel]]
        scores.append(
            {
                'state_id': state['state_id'],
                'label': state['label'],
                'matching_files': matching_files,
                'differing_files': differing_files,
                'matched_file_count': len(matching_files),
            }
        )
    scores.sort(key=lambda row: (-row['matched_file_count'], row['state_id']))
    result: dict[str, Any] = {
        'recognized': exact is not None,
        'observed_hashes': observed_hashes,
        'observed_combined_hash': _combined_hash(observed_hashes),
        'best_partial_match': scores[0],
        'candidate_scores': scores,
    }
    if exact is not None:
        result['matched_state_id'] = exact['state_id']
        result['matched_label'] = exact['label']
        result['plan'] = {
            'state_id': exact['state_id'],
            'label': exact['label'],
            'route_kind': exact['route_kind'],
            'action_kind': exact['action_kind'],
            'summary': exact['summary'],
            'apply_commands': list(exact['apply_commands']),
            'verification_commands': list(exact['verification_commands']),
            'expected_final_state_id': exact['expected_final_state_id'],
            'expected_final_combined_hash': exact['expected_final_combined_hash'],
            'post_apply_expectation': exact['post_apply_expectation'],
            'minimality_note': exact['minimality_note'],
        }
    else:
        result['matched_state_id'] = None
        result['matched_label'] = None
        result['plan'] = {
            'state_id': None,
            'label': None,
            'route_kind': 'unknown',
            'action_kind': report['unknown_policy']['action_kind'],
            'summary': report['unknown_policy']['summary'],
            'apply_commands': list(report['unknown_policy'].get('apply_commands') or []),
            'verification_commands': list(report['unknown_policy'].get('verification_commands') or []),
            'expected_final_state_id': report['unknown_policy'].get('expected_final_state_id'),
            'expected_final_combined_hash': report['unknown_policy'].get('expected_final_combined_hash'),
            'post_apply_expectation': 'Investigate drift before applying any bootstrap patch.',
            'minimality_note': 'Unknown or mixed state: fail closed and inspect diffs first.',
        }
    return result


def inspect(target_root: Path, report_path: Path) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding='utf-8'))
    observed_hashes = {rel: _hash_path(target_root / rel) for rel in report['target_files']}
    result = _classify(report, observed_hashes)
    result['target_root'] = str(target_root)
    result['report_path'] = str(report_path)
    return result


def _render_text(result: dict[str, Any]) -> str:
    plan = result['plan']
    lines = [
        f"recognized: {str(result['recognized']).lower()}",
        f"matched_state_id: {result['matched_state_id'] or 'none'}",
        f"action_kind: {plan['action_kind']}",
        f"summary: {plan['summary']}",
        f"route_kind: {plan['route_kind']}",
    ]
    if plan.get('expected_final_combined_hash'):
        lines.append(f"expected_final_combined_hash: {plan['expected_final_combined_hash']}")
    lines.append('apply_commands:')
    if plan['apply_commands']:
        for cmd in plan['apply_commands']:
            lines.append(f'  - {cmd}')
    else:
        lines.append('  - none')
    lines.append('verification_commands:')
    if plan['verification_commands']:
        for cmd in plan['verification_commands']:
            lines.append(f'  - {cmd}')
    else:
        lines.append('  - none')
    if not result['recognized']:
        best = result['best_partial_match']
        lines.append(
            'best_partial_match: '
            f"{best['state_id']} ({best['matched_file_count']}/{len(result['observed_hashes'])} files)"
        )
        if best['differing_files']:
            lines.append('differing_files:')
            for rel in best['differing_files']:
                lines.append(f'  - {rel}')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-root', type=Path, default=ROOT)
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if not args.report.exists():
        print(f'missing execution-card report: {args.report}', file=sys.stderr)
        return 1
    result = inspect(args.target_root, args.report)
    if args.json:
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write('\n')
    else:
        print(_render_text(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

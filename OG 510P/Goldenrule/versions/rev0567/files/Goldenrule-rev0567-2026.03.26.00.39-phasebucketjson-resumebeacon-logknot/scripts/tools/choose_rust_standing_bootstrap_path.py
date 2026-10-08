#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_state_selector.json'


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
    states = report['states']
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
        result['recommendation'] = exact['recommendation']
        result['notes'] = exact['notes']
    else:
        result['matched_state_id'] = None
        result['matched_label'] = None
        result['recommendation'] = report['unknown_policy']['recommendation']
        result['notes'] = report['unknown_policy']['notes']
    return result


def inspect(target_root: Path, report_path: Path) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding='utf-8'))
    observed_hashes = {
        rel: _hash_path(target_root / rel)
        for rel in report['target_files']
    }
    result = _classify(report, observed_hashes)
    result['target_root'] = str(target_root)
    result['report_path'] = str(report_path)
    return result


def _render_text(result: dict[str, Any]) -> str:
    lines = [
        f"recognized: {str(result['recognized']).lower()}",
        f"matched_state_id: {result['matched_state_id'] or 'none'}",
    ]
    rec = result['recommendation']
    lines.append(f"action_kind: {rec['action_kind']}")
    lines.append(f"summary: {rec['summary']}")
    if rec.get('primary_apply_hint'):
        lines.append(f"primary_apply_hint: {rec['primary_apply_hint']}")
    if rec.get('next_commands'):
        lines.append('next_commands:')
        for cmd in rec['next_commands']:
            lines.append(f"  - {cmd}")
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
        print(f'missing selector report: {args.report}', file=sys.stderr)
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

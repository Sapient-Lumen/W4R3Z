#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoints.json'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_path(path: Path) -> str:
    if not path.exists():
        return 'MISSING'
    return _sha256_bytes(path.read_bytes())


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _state_scores(target_files: list[str], states: list[dict[str, Any]], observed_hashes: dict[str, str]) -> list[dict[str, Any]]:
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
    return scores


def _resolve_expected(
    report: dict[str, Any],
    expect_state_id: str | None,
    expect_combined_hash: str | None,
    from_state_id: str | None,
    step_index: int | None,
) -> tuple[str | None, str | None, dict[str, Any] | None]:
    if (from_state_id is None) != (step_index is None):
        raise SystemExit('checkpoint-verifier: --from-state-id and --step-index must be provided together')
    if from_state_id is None:
        return expect_state_id, expect_combined_hash, None
    by_state = {state['state_id']: state for state in report['state_checkpoints']}
    if from_state_id not in by_state:
        raise SystemExit(f'checkpoint-verifier: unknown from_state_id {from_state_id!r}')
    state = by_state[from_state_id]
    checkpoints = state['checkpoints']
    if step_index is None or step_index < 1 or step_index > len(checkpoints):
        raise SystemExit(
            f'checkpoint-verifier: step_index {step_index} out of range for {from_state_id} (1..{len(checkpoints)})'
        )
    checkpoint = checkpoints[step_index - 1]
    resolved_state_id = checkpoint['expected_state_id']
    resolved_hash = checkpoint['expected_combined_hash']
    if expect_state_id is not None and expect_state_id != resolved_state_id:
        raise SystemExit(
            'checkpoint-verifier: expect-state-id conflicts with derived checkpoint expectation '
            f'({expect_state_id!r} != {resolved_state_id!r})'
        )
    if expect_combined_hash is not None and expect_combined_hash != resolved_hash:
        raise SystemExit(
            'checkpoint-verifier: expect-combined-hash conflicts with derived checkpoint expectation '
            f'({expect_combined_hash!r} != {resolved_hash!r})'
        )
    return resolved_state_id, resolved_hash, checkpoint


def inspect(
    target_root: Path,
    report_path: Path,
    expect_state_id: str | None = None,
    expect_combined_hash: str | None = None,
    from_state_id: str | None = None,
    step_index: int | None = None,
) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding='utf-8'))
    observed_hashes = {rel: _hash_path(target_root / rel) for rel in report['target_files']}
    states = report['state_checkpoints']
    matched = next((state for state in states if state['file_hashes'] == observed_hashes), None)
    scores = _state_scores(report['target_files'], states, observed_hashes)
    resolved_state_id, resolved_hash, checkpoint = _resolve_expected(
        report,
        expect_state_id=expect_state_id,
        expect_combined_hash=expect_combined_hash,
        from_state_id=from_state_id,
        step_index=step_index,
    )
    observed_combined_hash = _combined_hash(observed_hashes)
    verified = matched is not None
    if resolved_state_id is not None:
        verified = verified and matched is not None and matched['state_id'] == resolved_state_id
    if resolved_hash is not None:
        verified = verified and observed_combined_hash == resolved_hash
    result: dict[str, Any] = {
        'verified': verified,
        'recognized': matched is not None,
        'matched_state_id': None if matched is None else matched['state_id'],
        'matched_label': None if matched is None else matched['label'],
        'observed_hashes': observed_hashes,
        'observed_combined_hash': observed_combined_hash,
        'expected_state_id': resolved_state_id,
        'expected_combined_hash': resolved_hash,
        'derived_from_checkpoint': None,
        'best_partial_match': scores[0],
        'candidate_scores': scores,
        'target_root': str(target_root),
        'report_path': str(report_path),
        'summary': report['summary'],
    }
    if matched is not None:
        result['current_apply_commands'] = list(matched['apply_commands'])
        result['current_verification_commands'] = list(matched['verification_commands'])
        result['current_expected_final_combined_hash'] = matched['expected_final_combined_hash']
    else:
        result['current_apply_commands'] = []
        result['current_verification_commands'] = []
        result['current_expected_final_combined_hash'] = report['summary']['canonical_final_combined_hash']
    if checkpoint is not None:
        result['derived_from_checkpoint'] = {
            'from_state_id': from_state_id,
            'step_index': step_index,
            'apply_command': checkpoint['apply_command'],
            'expected_state_id': checkpoint['expected_state_id'],
            'expected_combined_hash': checkpoint['expected_combined_hash'],
            'expected_remaining_apply_commands': list(checkpoint['expected_remaining_apply_commands']),
            'final_verification_handoff': checkpoint['final_verification_handoff'],
        }
    return result


def _render_text(result: dict[str, Any]) -> str:
    lines = [
        f"verified: {str(result['verified']).lower()}",
        f"recognized: {str(result['recognized']).lower()}",
        f"matched_state_id: {result['matched_state_id'] or 'none'}",
        f"observed_combined_hash: {result['observed_combined_hash']}",
    ]
    if result.get('expected_state_id'):
        lines.append(f"expected_state_id: {result['expected_state_id']}")
    if result.get('expected_combined_hash'):
        lines.append(f"expected_combined_hash: {result['expected_combined_hash']}")
    if result.get('derived_from_checkpoint'):
        cp = result['derived_from_checkpoint']
        lines.append(f"derived_from_checkpoint: {cp['from_state_id']} step {cp['step_index']}")
        lines.append(f"checkpoint_apply_command: {cp['apply_command']}")
    lines.append('remaining_apply_commands:')
    if result['current_apply_commands']:
        for cmd in result['current_apply_commands']:
            lines.append(f'  - {cmd}')
    else:
        lines.append('  - none')
    if not result['verified']:
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
    parser.add_argument('--expect-state-id')
    parser.add_argument('--expect-combined-hash')
    parser.add_argument('--from-state-id')
    parser.add_argument('--step-index', type=int)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if not args.report.exists():
        print(f'missing checkpoints report: {args.report}', file=sys.stderr)
        return 1
    try:
        result = inspect(
            target_root=args.target_root,
            report_path=args.report,
            expect_state_id=args.expect_state_id,
            expect_combined_hash=args.expect_combined_hash,
            from_state_id=args.from_state_id,
            step_index=args.step_index,
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write('\n')
    else:
        print(_render_text(result))
    return 0 if result['verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rust_comeback_card.json'
QUEUE = ROOT / 'artifacts' / 'reports' / 'rust_external_test_queue.json'
SEED = ROOT / 'artifacts' / 'reports' / 'rust_seed_loader_readiness.json'
BUNDLE = ROOT / 'artifacts' / 'reports' / 'rust_lift_bundle_plan.json'
PATCHSET = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patchset.json'
SHARDS = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_shards.json'
REHEARSAL = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
FRONTIER = ROOT / 'artifacts' / 'reports' / 'rust_patch_prefix_frontier.json'


def main() -> int:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    queue = json.loads(QUEUE.read_text(encoding='utf-8'))
    seed = json.loads(SEED.read_text(encoding='utf-8'))
    bundle = json.loads(BUNDLE.read_text(encoding='utf-8'))
    patchset = json.loads(PATCHSET.read_text(encoding='utf-8'))
    shards = json.loads(SHARDS.read_text(encoding='utf-8'))
    rehearsal = json.loads(REHEARSAL.read_text(encoding='utf-8'))
    frontier = json.loads(FRONTIER.read_text(encoding='utf-8'))

    summary = report.get('summary') or {}
    if int(summary.get('total_queue_rows', -1)) != int(queue.get('summary', {}).get('queue_entries', -2)):
        print('rust-comeback-card: queue row mismatch', file=sys.stderr)
        return 1
    if int(summary.get('direct_probe_ready_rows', -1)) != int(seed.get('summary', {}).get('direct_probe_ready', -2)):
        print('rust-comeback-card: direct probe ready mismatch', file=sys.stderr)
        return 1
    if int(summary.get('bundle_count', -1)) != int(bundle.get('summary', {}).get('bundle_count', -2)):
        print('rust-comeback-card: bundle count mismatch', file=sys.stderr)
        return 1
    if int(summary.get('shard_count', -1)) != len(shards.get('entries') or []):
        print('rust-comeback-card: shard count mismatch', file=sys.stderr)
        return 1
    if int(summary.get('full_closure_prefix', -1)) != int(frontier.get('summary', {}).get('full_closure_prefix', -2)):
        print('rust-comeback-card: full closure prefix mismatch', file=sys.stderr)
        return 1
    if str(summary.get('monolithic_patch_apply_hint')) != str(patchset.get('patch', {}).get('apply_hint')):
        print('rust-comeback-card: monolithic apply hint mismatch', file=sys.stderr)
        return 1
    if bool(summary.get('final_state_equivalent')) != bool(rehearsal.get('summary', {}).get('final_state_equivalent')):
        print('rust-comeback-card: rehearsal equivalence mismatch', file=sys.stderr)
        return 1

    milestone_cards = report.get('milestone_cards') or []
    expected_labels = ['quick_foothold', 'lift_first_closure', 'first_externalize_now', 'full_closure']
    got_labels = [str(card.get('label')) for card in milestone_cards]
    if got_labels != expected_labels:
        print(f'rust-comeback-card: milestone labels mismatch: {got_labels}', file=sys.stderr)
        return 1

    for card in milestone_cards:
        prefix_index = int(card.get('prefix_index', -1))
        if prefix_index < 1 or prefix_index > len(shards.get('entries') or []):
            print(f'rust-comeback-card: invalid prefix index {prefix_index}', file=sys.stderr)
            return 1
        if int(card.get('rows_covered', -1)) + int(card.get('rows_remaining', -1)) != int(summary['total_queue_rows']):
            print(f"rust-comeback-card: row accounting mismatch for {card.get('label')}", file=sys.stderr)
            return 1
        if 'git apply artifacts/patches/rust_external_test_shards/' not in str(card.get('cumulative_apply_hint')):
            print(f"rust-comeback-card: missing cumulative apply hint for {card.get('label')}", file=sys.stderr)
            return 1

    landing_recipe = report.get('landing_recipe') or []
    if len(landing_recipe) < 5:
        print('rust-comeback-card: landing recipe too short', file=sys.stderr)
        return 1

    if int(summary.get('direct_probe_ready_rows', 0)) != int(summary.get('total_queue_rows', -1)):
        print('rust-comeback-card: expected all queue rows to be direct-probe-ready', file=sys.stderr)
        return 1

    print(
        'rust-comeback-card: ok '
        f"(rows={summary.get('total_queue_rows')} lift_first={summary.get('lift_first_closure_prefix')} full={summary.get('full_closure_prefix')})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

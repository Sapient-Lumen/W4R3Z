#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rust_comeback_execution_card.json'
FRONTIER = ROOT / 'artifacts' / 'reports' / 'rust_patch_prefix_frontier.json'
SHARDS = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_shards.json'
PATCHSET = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patchset.json'
REHEARSAL = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def main() -> int:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    frontier = json.loads(FRONTIER.read_text(encoding='utf-8'))
    shards = json.loads(SHARDS.read_text(encoding='utf-8'))
    patchset = json.loads(PATCHSET.read_text(encoding='utf-8'))
    rehearsal = json.loads(REHEARSAL.read_text(encoding='utf-8'))

    summary = report.get('summary') or {}
    if int(summary.get('full_closure_prefix', -1)) != int(frontier.get('summary', {}).get('full_closure_prefix', -2)):
        print('rust-comeback-execution-card: full closure prefix mismatch', file=sys.stderr)
        return 1
    if int(summary.get('all_probe_run_prefix', -1)) != int(frontier.get('summary', {}).get('all_probe_run_prefix', -2)):
        print('rust-comeback-execution-card: probe-run prefix mismatch', file=sys.stderr)
        return 1
    if str(summary.get('monolithic_apply_hint')) != str(patchset.get('patch', {}).get('apply_hint')):
        print('rust-comeback-execution-card: monolithic apply hint mismatch', file=sys.stderr)
        return 1
    if bool(summary.get('final_state_equivalent')) != bool(rehearsal.get('summary', {}).get('final_state_equivalent')):
        print('rust-comeback-execution-card: rehearsal equivalence mismatch', file=sys.stderr)
        return 1

    all_exact = _unique([hint for entry in (shards.get('entries') or []) for hint in entry.get('future_cargo_hints') or []])
    if int(summary.get('exact_witness_total', -1)) != len(all_exact):
        print('rust-comeback-execution-card: exact witness count mismatch', file=sys.stderr)
        return 1

    plateau_cards = report.get('plateau_cards') or []
    expected_labels = ['quick_foothold', 'lift_first_closure', 'first_externalize_now', 'full_closure']
    got_labels = [str(card.get('label')) for card in plateau_cards]
    if got_labels != expected_labels:
        print(f'rust-comeback-execution-card: plateau labels mismatch: {got_labels}', file=sys.stderr)
        return 1

    counts = [int(card.get('cumulative_exact_witness_count', -1)) for card in plateau_cards]
    if counts != sorted(counts):
        print('rust-comeback-execution-card: cumulative witness counts not monotone', file=sys.stderr)
        return 1

    if int(summary.get('plateau_count', -1)) != len(plateau_cards):
        print('rust-comeback-execution-card: plateau count mismatch', file=sys.stderr)
        return 1

    full_card = plateau_cards[-1]
    probe_total = int(full_card.get('cumulative_exact_witnesses_by_target', {}).get('probe_run', -1))
    metamorphic_total = int(full_card.get('cumulative_exact_witnesses_by_target', {}).get('metamorphic_suite', -1))
    if probe_total != int(summary.get('probe_run_exact_witness_total', -2)):
        print('rust-comeback-execution-card: probe_run total mismatch', file=sys.stderr)
        return 1
    if metamorphic_total != int(summary.get('metamorphic_exact_witness_total', -2)):
        print('rust-comeback-execution-card: metamorphic total mismatch', file=sys.stderr)
        return 1
    if probe_total + metamorphic_total != int(summary.get('exact_witness_total', -3)):
        print('rust-comeback-execution-card: target totals do not sum to total exact witnesses', file=sys.stderr)
        return 1

    if not bool(summary.get('probe_run_closure_requires_dual_lane')):
        print('rust-comeback-execution-card: expected dual-lane coupling flag to be true', file=sys.stderr)
        return 1

    if int(summary.get('last_probe_only_prefix', -1)) >= int(summary.get('full_closure_prefix', -2)):
        print('rust-comeback-execution-card: expected probe-only prefix to end before full closure', file=sys.stderr)
        return 1

    for card in plateau_cards[:-1]:
        targets = list(card.get('test_targets') or [])
        if targets != ['probe_run']:
            print(f"rust-comeback-execution-card: unexpected early plateau targets for {card.get('label')}: {targets}", file=sys.stderr)
            return 1
    if list(full_card.get('test_targets') or []) != ['metamorphic_suite', 'probe_run']:
        print('rust-comeback-execution-card: full closure targets mismatch', file=sys.stderr)
        return 1

    print(
        'rust-comeback-execution-card: ok '
        f"(plateaus={summary.get('plateau_count')} exact={summary.get('exact_witness_total')})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

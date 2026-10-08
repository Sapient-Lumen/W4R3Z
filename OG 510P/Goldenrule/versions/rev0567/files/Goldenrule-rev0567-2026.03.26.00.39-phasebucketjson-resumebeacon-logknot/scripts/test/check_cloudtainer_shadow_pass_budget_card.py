#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_budget_card.json'
FRONTIER = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_frontier.json'
HISTORY = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_history.json'
VOLATILITY = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_volatility.json'


def main() -> int:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    frontier = json.loads(FRONTIER.read_text(encoding='utf-8'))
    history = json.loads(HISTORY.read_text(encoding='utf-8'))
    volatility = json.loads(VOLATILITY.read_text(encoding='utf-8'))

    cards = report.get('budget_cards') or []
    if len(cards) != 3:
        print('shadow-pass-budget-card: expected exactly three budget cards', file=sys.stderr)
        return 1

    card_by_label = {str(card.get('label')): card for card in cards}
    for label in ('short_budget', 'medium_budget', 'long_budget'):
        if label not in card_by_label:
            print(f'shadow-pass-budget-card: missing {label}', file=sys.stderr)
            return 1

    frontier_profiles = {str(entry.get('label')): entry for entry in frontier.get('recommended_budget_prefixes') or []}
    frontier_rows = {str(entry.get('label')): entry for entry in frontier.get('frontiers') or []}
    history_rows = {str(entry.get('label')): entry for entry in history.get('current_profile_frontier_ranges') or []}
    volatility_rows = {str(entry.get('label')): entry for entry in volatility.get('frontier_step_stats') or []}

    for label, card in card_by_label.items():
        profile = frontier_profiles.get(label)
        if profile is None:
            print(f'shadow-pass-budget-card: missing frontier profile for {label}', file=sys.stderr)
            return 1
        frontier_label = str(profile.get('frontier_label'))
        if str(card.get('frontier_label')) != frontier_label:
            print(f'shadow-pass-budget-card: frontier label mismatch for {label}', file=sys.stderr)
            return 1
        if str(card.get('command')) != str(profile.get('command')):
            print(f'shadow-pass-budget-card: command mismatch for {label}', file=sys.stderr)
            return 1
        if frontier_label not in frontier_rows or frontier_label not in history_rows or frontier_label not in volatility_rows:
            print(f'shadow-pass-budget-card: missing supporting rows for {label}', file=sys.stderr)
            return 1
        if float(card.get('buffered_budget_seconds', 0)) < float(card.get('cumulative_seconds_latest', 0)):
            print(f'shadow-pass-budget-card: buffered budget shrank for {label}', file=sys.stderr)
            return 1
        if float(card.get('recommended_slack_seconds', -1)) < 0:
            print(f'shadow-pass-budget-card: negative slack for {label}', file=sys.stderr)
            return 1

    recipe = report.get('reentry_recipe') or []
    if len(recipe) < 4:
        print('shadow-pass-budget-card: reentry recipe too short', file=sys.stderr)
        return 1

    summary = report.get('summary') or {}
    if str(summary.get('latest_receipt')) != str(frontier.get('metadata', {}).get('source_receipt')):
        print('shadow-pass-budget-card: latest receipt mismatch', file=sys.stderr)
        return 1

    print(
        'shadow-pass-budget-card: ok '
        f"(latest={summary.get('latest_receipt')} short={card_by_label['short_budget']['buffered_budget_seconds']}s long={card_by_label['long_budget']['buffered_budget_seconds']}s)"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FRONTIER_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_frontier.json'
HISTORY_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_history.json'
VOLATILITY_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_volatility.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_budget_card.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_SHADOW_PASS_BUDGET_CARD.md'


def _round(value: float) -> float:
    return round(float(value), 3)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _slack_for_class(volatility_class: str, spread_seconds: float) -> float:
    spread = float(spread_seconds)
    if volatility_class == 'stable':
        return _round(max(0.5, spread))
    if volatility_class == 'watch':
        return _round(max(1.0, spread * 2.0))
    if volatility_class == 'jittery':
        return _round(max(2.0, spread * 2.5))
    return _round(max(1.0, spread * 2.0))


def _buffer_posture(volatility_class: str) -> str:
    if volatility_class == 'stable':
        return 'tight_ok'
    if volatility_class == 'watch':
        return 'buffer_recommended'
    if volatility_class == 'jittery':
        return 'extra_buffer_required'
    return 'buffer_recommended'


def build_report() -> dict[str, Any]:
    frontier = _load(FRONTIER_REPORT)
    history = _load(HISTORY_REPORT)
    volatility = _load(VOLATILITY_REPORT)

    frontier_by_label = {str(entry['label']): entry for entry in frontier.get('frontiers') or []}
    history_by_label = {str(entry['label']): entry for entry in history.get('current_profile_frontier_ranges') or []}
    volatility_by_label = {str(entry['label']): entry for entry in volatility.get('frontier_step_stats') or []}

    budget_cards: list[dict[str, Any]] = []
    for budget in frontier.get('recommended_budget_prefixes') or []:
        frontier_label = str(budget['frontier_label'])
        frontier_row = frontier_by_label[frontier_label]
        history_row = history_by_label[frontier_label]
        volatility_row = volatility_by_label[frontier_label]
        slack_seconds = _slack_for_class(str(volatility_row['volatility_class']), float(volatility_row['spread_seconds']))
        budget_cards.append(
            {
                'label': str(budget['label']),
                'command': str(budget['command']),
                'resume_command': str(budget['resume_command']),
                'why_choose_it': str(budget['why_choose_it']),
                'frontier_label': frontier_label,
                'frontier_step_id': str(frontier_row['step_id']),
                'frontier_step_index': int(frontier_row['step_index']),
                'lane': str(frontier_row['lane']),
                'cumulative_seconds_latest': _round(frontier_row['cumulative_seconds']),
                'remaining_seconds_latest': _round(frontier_row['remaining_seconds']),
                'current_profile_min_seconds': _round(history_row['min_seconds']),
                'current_profile_median_seconds': _round(history_row['median_seconds']),
                'current_profile_max_seconds': _round(history_row['max_seconds']),
                'current_profile_spread_seconds': _round(history_row['spread_seconds']),
                'sample_count': int(history_row['sample_count']),
                'volatility_class': str(volatility_row['volatility_class']),
                'cv_fraction': _round(volatility_row['cv_fraction']),
                'recommended_slack_seconds': slack_seconds,
                'buffered_budget_seconds': _round(float(frontier_row['cumulative_seconds']) + slack_seconds),
                'buffer_posture': _buffer_posture(str(volatility_row['volatility_class'])),
                'rationale': str(frontier_row['rationale']),
            }
        )

    latest_total = _round(frontier['summary']['total_duration_seconds'])
    current_profile_median = _round(history['summary']['current_profile_duration_median_seconds'])
    current_profile_min = _round(history['summary']['current_profile_duration_min_seconds'])
    current_profile_max = _round(history['summary']['current_profile_duration_max_seconds'])
    full_pass_cv = _round(volatility['summary']['current_profile_total_duration_cv_fraction'])
    full_pass_slack = _slack_for_class(
        str(next(entry['volatility_class'] for entry in volatility['frontier_step_stats'] if entry['label'] == 'full_shadow_pass')),
        float(next(entry['spread_seconds'] for entry in volatility['frontier_step_stats'] if entry['label'] == 'full_shadow_pass')),
    )

    headline_findings = [
        (
            f"The latest full blocked-session pass took {latest_total} seconds; current-profile full-pass receipts span "
            f"{current_profile_min} .. {current_profile_max} seconds (median {current_profile_median}, cv {full_pass_cv})."
        ),
        (
            f"The safest tight budget remains `short_budget`: {budget_cards[0]['command']} reaches "
            f"`{budget_cards[0]['frontier_step_id']}` in {budget_cards[0]['cumulative_seconds_latest']} seconds, and a "
            f"{budget_cards[0]['recommended_slack_seconds']}-second buffer lifts that to {budget_cards[0]['buffered_budget_seconds']} seconds."
        ),
        (
            f"`medium_budget` is still the best reentry point when you want the comeback inputs refreshed without paying for the full patch lane: "
            f"it stops at `{budget_cards[1]['frontier_step_id']}` after {budget_cards[1]['cumulative_seconds_latest']} seconds and leaves "
            f"{budget_cards[1]['remaining_seconds_latest']} seconds for a later resume."
        ),
        (
            f"`long_budget` closes the full static Rust comeback plan before archive/Python lanes, but it is only a watch-grade timing anchor: budget about "
            f"{budget_cards[2]['buffered_budget_seconds']} seconds rather than the raw {budget_cards[2]['cumulative_seconds_latest']} seconds if wrapper ceilings are real."
        ),
    ]

    reentry_recipe = [
        {
            'rank': 1,
            'action': 'If you only have a small uninterrupted window, run the short budget profile first.',
            'command': budget_cards[0]['command'],
            'expected_seconds_with_buffer': budget_cards[0]['buffered_budget_seconds'],
        },
        {
            'rank': 2,
            'action': 'If you can stay longer, prefer the medium budget profile; it refreshes the queue/seed-loader comeback inputs before you stop.',
            'command': budget_cards[1]['command'],
            'expected_seconds_with_buffer': budget_cards[1]['buffered_budget_seconds'],
        },
        {
            'rank': 3,
            'action': 'Only use the long profile when you specifically want the full static comeback lane refreshed before resuming later.',
            'command': budget_cards[2]['command'],
            'expected_seconds_with_buffer': budget_cards[2]['buffered_budget_seconds'],
        },
        {
            'rank': 4,
            'action': 'After any intentional stop or wrapper interruption, resume from the checkpoint instead of restarting.',
            'command': 'make cloudtainer-shadow-pass-resume',
            'expected_seconds_with_buffer': _round(max(budget_cards[0]['remaining_seconds_latest'], budget_cards[1]['remaining_seconds_latest'], budget_cards[2]['remaining_seconds_latest'])),
        },
        {
            'rank': 5,
            'action': 'If you do have enough room for the whole pass, budget the buffered full-pass number rather than the raw latest receipt.',
            'command': 'make cloudtainer-shadow-pass',
            'expected_seconds_with_buffer': _round(latest_total + full_pass_slack),
        },
    ]

    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                FRONTIER_REPORT.relative_to(ROOT).as_posix(),
                HISTORY_REPORT.relative_to(ROOT).as_posix(),
                VOLATILITY_REPORT.relative_to(ROOT).as_posix(),
            ],
        },
        'summary': {
            'latest_receipt': str(frontier['metadata']['source_receipt']),
            'latest_decision': str(frontier['summary']['decision']),
            'current_profile_receipt_count': int(history['summary']['current_profile_receipt_count']),
            'latest_total_duration_seconds': latest_total,
            'current_profile_total_duration_min_seconds': current_profile_min,
            'current_profile_total_duration_median_seconds': current_profile_median,
            'current_profile_total_duration_max_seconds': current_profile_max,
            'current_profile_total_duration_cv_fraction': full_pass_cv,
            'recommended_full_pass_slack_seconds': full_pass_slack,
            'recommended_full_pass_buffered_seconds': _round(latest_total + full_pass_slack),
        },
        'budget_cards': budget_cards,
        'reentry_recipe': reentry_recipe,
        'headline_findings': headline_findings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Cloudtainer Shadow Pass Budget Card',
        '',
        'Generated by `scripts/report/build_cloudtainer_shadow_pass_budget_card.py`. This fuses the latest frontier, receipt history, and volatility map into one compact command card so a blocked-session inheritor can pick a budget profile without reopening three neighboring reports.',
        '',
        '## Summary',
        '',
        f"- latest receipt: `{summary['latest_receipt']}`",
        f"- latest decision: `{summary['latest_decision']}`",
        f"- current-profile receipt count: `{summary['current_profile_receipt_count']}`",
        f"- full-pass timing range: `{summary['current_profile_total_duration_min_seconds']}` .. `{summary['current_profile_total_duration_max_seconds']}` seconds (median `{summary['current_profile_total_duration_median_seconds']}`, cv `{summary['current_profile_total_duration_cv_fraction']}`)",
        f"- buffered full-pass budget: `{summary['recommended_full_pass_buffered_seconds']}` seconds (raw latest `{summary['latest_total_duration_seconds']}` + slack `{summary['recommended_full_pass_slack_seconds']}`)",
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')

    lines.extend([
        '',
        '## Budget cards',
        '',
        '| profile | command | stop step | raw seconds | buffered seconds | volatility | posture | why |',
        '|---|---|---|---:|---:|---|---|---|',
    ])
    for card in report['budget_cards']:
        lines.append(
            f"| `{card['label']}` | `{card['command']}` | `{card['frontier_step_id']}` | {card['cumulative_seconds_latest']} | {card['buffered_budget_seconds']} | `{card['volatility_class']}` | `{card['buffer_posture']}` | {card['why_choose_it']} |"
        )

    lines.extend([
        '',
        '## Per-profile notes',
        '',
    ])
    for card in report['budget_cards']:
        lines.extend([
            f"### {card['label']}",
            '',
            f"- command: `{card['command']}`",
            f"- resume later with: `{card['resume_command']}`",
            f"- frontier: `{card['frontier_label']}` / `{card['frontier_step_id']}` (step `{card['frontier_step_index']}`)",
            f"- latest cumulative duration: `{card['cumulative_seconds_latest']}` seconds; buffered budget: `{card['buffered_budget_seconds']}` seconds",
            f"- current-profile range: `{card['current_profile_min_seconds']}` .. `{card['current_profile_max_seconds']}` seconds (median `{card['current_profile_median_seconds']}`, spread `{card['current_profile_spread_seconds']}`, cv `{card['cv_fraction']}`)",
            f"- remaining duration after stop in the latest receipt: `{card['remaining_seconds_latest']}` seconds",
            f"- rationale: {card['rationale']}",
            '',
        ])

    lines.extend([
        '## Reentry recipe',
        '',
    ])
    for row in report['reentry_recipe']:
        lines.append(
            f"{row['rank']}. {row['action']} Command: `{row['command']}`. Budget around `{row['expected_seconds_with_buffer']}` seconds when wrapper ceilings matter."
        )

    lines.extend([
        '',
        '## Source reports',
        '',
    ])
    for path in report['metadata']['source_reports']:
        lines.append(f'- `{path}`')

    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a fused cloudtainer shadow-pass budget card from the frontier/history/volatility reports.')
    parser.add_argument('--write', action='store_true', help='write the JSON and markdown outputs in place')
    args = parser.parse_args()

    report = build_report()
    rendered = render_markdown(report)

    if not args.write:
        existing = _load(OUT_JSON)
        existing_md = OUT_MD.read_text(encoding='utf-8')
        if existing != report or existing_md != rendered:
            print('cloudtainer-shadow-pass-budget-card is out of date; run make update-cloudtainer-shadow-pass-budget-card')
            return 1
        print(
            'cloudtainer-shadow-pass-budget-card: ok '
            f"(latest={report['summary']['latest_receipt']} short={report['budget_cards'][0]['buffered_budget_seconds']}s medium={report['budget_cards'][1]['buffered_budget_seconds']}s long={report['budget_cards'][2]['buffered_budget_seconds']}s)"
        )
        return 0

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(rendered, encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
    print(f'wrote {OUT_MD.relative_to(ROOT).as_posix()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

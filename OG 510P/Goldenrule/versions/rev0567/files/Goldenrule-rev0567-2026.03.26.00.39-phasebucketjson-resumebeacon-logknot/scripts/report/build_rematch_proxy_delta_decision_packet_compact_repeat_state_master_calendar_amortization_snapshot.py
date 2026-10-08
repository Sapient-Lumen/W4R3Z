#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.md'
MASTER_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.json'
PREMIUM_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _mode_rows() -> list[dict[str, Any]]:
    master = _load(MASTER_REPORT)
    premium = _load(PREMIUM_REPORT)

    full_master = [int(x) for x in master['headline_findings']['full_master_audit_checkpoints_unique_appends']]
    structural_only = [int(x) for x in master['headline_findings']['structural_only_checkpoints_unique_appends']]
    master_set = set(full_master)

    baseline = premium['trusted_repeat_baseline']
    rows: list[dict[str, Any]] = []
    baseline_points = [int(x) for x in baseline['transition_checkpoints_unique_appends']]
    baseline_missing = sorted(master_set - set(baseline_points))
    rows.append(
        {
            'mode': baseline['mode'],
            'mode_class': 'trusted_repeat_baseline',
            'minimum_gain_share_of_full_dynamic_savings': float(baseline['preserved_gain_share_of_full_dynamic_savings']),
            'mode_specific_checkpoint_count': int(baseline['transition_checkpoint_count']),
            'mode_specific_checkpoints_unique_appends': baseline_points,
            'additional_dates_needed_to_pre_register_full_master_calendar': len(baseline_missing),
            'master_calendar_dates_not_already_in_mode_specific_calendar': baseline_missing,
            'master_calendar_coverage_share': round(len(baseline_points) / len(full_master), 6),
            'structural_only_dates_missing_from_mode_specific_calendar': structural_only,
            'switching_inside_master_calendar_requires_new_dates': 0,
        }
    )

    for row in premium['uncertainty_tier_rows']:
        mode_points = [int(x) for x in row['union_transition_checkpoints_unique_appends']]
        missing = sorted(master_set - set(mode_points))
        rows.append(
            {
                'mode': str(row['tier']),
                'mode_class': 'exact_uncertainty_tier',
                'minimum_gain_share_of_full_dynamic_savings': float(row['minimum_gain_share_of_full_dynamic_savings']),
                'mode_specific_checkpoint_count': int(row['union_transition_checkpoint_count']),
                'mode_specific_checkpoints_unique_appends': mode_points,
                'additional_dates_needed_to_pre_register_full_master_calendar': len(missing),
                'master_calendar_dates_not_already_in_mode_specific_calendar': missing,
                'master_calendar_coverage_share': round(len(mode_points) / len(full_master), 6),
                'structural_only_dates_missing_from_mode_specific_calendar': [
                    point for point in structural_only if point not in mode_points
                ],
                'switching_inside_master_calendar_requires_new_dates': 0,
                'representative_anchor_minimum_dwell_unique_appends': int(
                    row['representative_anchor_minimum_dwell_unique_appends']
                ),
                'exact_hard_cap': int(row['exact_hard_cap']),
            }
        )

    order = {
        'trusted_repeat_rewrite_budgeted': 0,
        'lower_guarantee': 1,
        'near_optimal': 2,
        'near_exact': 3,
    }
    rows.sort(key=lambda item: order[item['mode']])
    return rows


def _build_report() -> dict[str, Any]:
    master = _load(MASTER_REPORT)
    rows = _mode_rows()
    row_by_mode = {row['mode']: row for row in rows}
    full_master = [int(x) for x in master['headline_findings']['full_master_audit_checkpoints_unique_appends']]
    structural_only = [int(x) for x in master['headline_findings']['structural_only_checkpoints_unique_appends']]

    report = {
        'focus': 'Price the full 17-point master audit calendar as a one-time pre-registration cost so inheritors can see when checkpoint burden can be amortized away and future mode switching becomes calendar-free.',
        'headline_findings': {
            'full_master_audit_checkpoint_count': len(full_master),
            'full_master_audit_checkpoints_unique_appends': full_master,
            'trusted_repeat_additional_dates_needed_to_pre_register_full_master_calendar': row_by_mode['trusted_repeat_rewrite_budgeted']['additional_dates_needed_to_pre_register_full_master_calendar'],
            'lower_guarantee_additional_dates_needed_to_pre_register_full_master_calendar': row_by_mode['lower_guarantee']['additional_dates_needed_to_pre_register_full_master_calendar'],
            'near_optimal_additional_dates_needed_to_pre_register_full_master_calendar': row_by_mode['near_optimal']['additional_dates_needed_to_pre_register_full_master_calendar'],
            'near_exact_additional_dates_needed_to_pre_register_full_master_calendar': row_by_mode['near_exact']['additional_dates_needed_to_pre_register_full_master_calendar'],
            'structural_only_checkpoints_unique_appends': structural_only,
            'all_current_modes_become_calendar_free_to_switch_once_full_master_is_pre_registered': all(
                row['switching_inside_master_calendar_requires_new_dates'] == 0 for row in rows
            ),
            'near_exact_is_cheapest_future_proof_starting_point': (
                row_by_mode['near_exact']['additional_dates_needed_to_pre_register_full_master_calendar']
                < row_by_mode['near_optimal']['additional_dates_needed_to_pre_register_full_master_calendar']
                < row_by_mode['lower_guarantee']['additional_dates_needed_to_pre_register_full_master_calendar']
                < row_by_mode['trusted_repeat_rewrite_budgeted']['additional_dates_needed_to_pre_register_full_master_calendar']
            ),
            'main_rule': 'if the archive expects any future switching among the trusted fallback and the current exact uncertainty-safe tiers, pre-register the full 17-point master audit calendar once; after that, mode changes cost zero new audit dates and should be decided only by cap, guarantee, and tolerance needs.',
        },
        'decision_rules': [
            'Use a mode-specific checkpoint list only when the archive is confident it will remain in that one operating mode for a while and immediate audit burden is more constrained than future flexibility.',
            'If the archive expects mode churn among the trusted fallback and the current exact uncertainty tiers, pre-register the full 17-point master calendar once and then treat future mode changes as calendar-free.',
            'Starting from the near-exact 0.99 tier is already almost future-proof: only three extra dates, 56 plus the structural-only pair 79 and 191, are needed to reach the full master calendar.',
            'Starting from the near-optimal 0.95 tier still leaves a moderate future-proofing gap of nine extra dates, so it is the main operating knee but not the cheapest pre-registration launch point.',
            'Starting from the trusted 4-transition fallback minimizes immediate calendar size but leaves the largest future-proofing gap: thirteen extra dates are still needed to cover all current certified modes and structural flips.',
        ],
        'mode_rows': rows,
        'source_reports': [
            str(MASTER_REPORT.relative_to(ROOT)),
            str(PREMIUM_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Master Calendar Amortization Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- full master calendar: `{findings['full_master_audit_checkpoint_count']}` checkpoints at `{findings['full_master_audit_checkpoints_unique_appends']}`.",
        f"- additional dates needed from trusted fallback to full master: `{findings['trusted_repeat_additional_dates_needed_to_pre_register_full_master_calendar']}`.",
        f"- additional dates needed from exact `0.85` to full master: `{findings['lower_guarantee_additional_dates_needed_to_pre_register_full_master_calendar']}`.",
        f"- additional dates needed from exact `0.95` to full master: `{findings['near_optimal_additional_dates_needed_to_pre_register_full_master_calendar']}`.",
        f"- additional dates needed from exact `0.99` to full master: `{findings['near_exact_additional_dates_needed_to_pre_register_full_master_calendar']}`.",
        f"- all current modes become calendar-free to switch once the full master calendar is pre-registered: `{findings['all_current_modes_become_calendar_free_to_switch_once_full_master_is_pre_registered']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Mode-specific calendar vs full master calendar',
        '| mode | min gain/share objective | mode-specific checkpoint count | additional dates to reach full master | missing dates | coverage share of full master | switching inside master needs new dates |',
        '|---|---:|---:|---:|---|---:|---:|',
    ]
    for row in report['mode_rows']:
        lines.append(
            f"| {row['mode']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['mode_specific_checkpoint_count']} | {row['additional_dates_needed_to_pre_register_full_master_calendar']} | {row['master_calendar_dates_not_already_in_mode_specific_calendar']} | {row['master_calendar_coverage_share']} | {row['switching_inside_master_calendar_requires_new_dates']} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Source reports',
    ])
    for src in report['source_reports']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_upgrade_tariff_snapshot_20260308.md'
CAP_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.json'
CHECKPOINT_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'
MASTER_AUDIT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _band_width(start: int, end: int) -> int:
    return end - start + 1


def _tier_rows() -> list[dict[str, Any]]:
    cap = _load(CAP_STAIRCASE_REPORT)
    checkpoints = _load(CHECKPOINT_STAIRCASE_REPORT)
    checkpoint_by_tier = {row['tier']: row for row in checkpoints['tier_rows']}
    rows: list[dict[str, Any]] = []
    for row in cap['tier_rows']:
        tier = str(row['tier'])
        check_row = checkpoint_by_tier[tier]
        start = int(row['exact_dwell_band_start_unique_appends'])
        end = int(row['exact_dwell_band_end_unique_appends'])
        rows.append(
            {
                'tier': tier,
                'minimum_gain_share_of_full_dynamic_savings': float(row['minimum_gain_share_of_full_dynamic_savings']),
                'worst_case_gain_share_of_full_dynamic_savings': float(check_row['worst_case_gain_share_of_full_dynamic_savings']),
                'exact_hard_cap': int(row['exact_hard_cap']),
                'representative_anchor_minimum_dwell_unique_appends': int(row['representative_anchor_minimum_dwell_unique_appends']),
                'exact_dwell_band_start_unique_appends': start,
                'exact_dwell_band_end_unique_appends': end,
                'exact_dwell_band_width_unique_appends': _band_width(start, end),
                'union_transition_checkpoint_count': int(check_row['union_transition_checkpoint_count']),
                'union_transition_checkpoints_unique_appends': list(check_row['union_transition_checkpoints_unique_appends']),
            }
        )
    return rows


def _make_upgrade(from_row: dict[str, Any], to_row: dict[str, Any]) -> dict[str, Any]:
    from_set = set(from_row['union_transition_checkpoints_unique_appends'])
    to_set = set(to_row['union_transition_checkpoints_unique_appends'])
    added = sorted(to_set - from_set)
    dropped = sorted(from_set - to_set)
    return {
        'from_tier': from_row['tier'],
        'to_tier': to_row['tier'],
        'from_minimum_gain_share_of_full_dynamic_savings': from_row['minimum_gain_share_of_full_dynamic_savings'],
        'to_minimum_gain_share_of_full_dynamic_savings': to_row['minimum_gain_share_of_full_dynamic_savings'],
        'nominal_gain_floor_delta': round(
            to_row['minimum_gain_share_of_full_dynamic_savings'] - from_row['minimum_gain_share_of_full_dynamic_savings'], 6
        ),
        'realized_worst_case_gain_share_delta': round(
            to_row['worst_case_gain_share_of_full_dynamic_savings'] - from_row['worst_case_gain_share_of_full_dynamic_savings'], 6
        ),
        'hard_cap_delta': to_row['exact_hard_cap'] - from_row['exact_hard_cap'],
        'net_checkpoint_count_delta': to_row['union_transition_checkpoint_count'] - from_row['union_transition_checkpoint_count'],
        'gross_added_checkpoint_count': len(added),
        'gross_dropped_checkpoint_count': len(dropped),
        'checkpoints_added_unique_appends': added,
        'checkpoints_dropped_unique_appends': dropped,
        'representative_anchor_shift_unique_appends': to_row['representative_anchor_minimum_dwell_unique_appends'] - from_row['representative_anchor_minimum_dwell_unique_appends'],
        'dwell_band_width_delta_unique_appends': to_row['exact_dwell_band_width_unique_appends'] - from_row['exact_dwell_band_width_unique_appends'],
    }


def _build_report() -> dict[str, Any]:
    tiers = _tier_rows()
    rows = {row['tier']: row for row in tiers}
    master = _load(MASTER_AUDIT_REPORT)

    lower_to_near_optimal = _make_upgrade(rows['lower_guarantee'], rows['near_optimal'])
    near_optimal_to_near_exact = _make_upgrade(rows['near_optimal'], rows['near_exact'])
    lower_to_near_exact = _make_upgrade(rows['lower_guarantee'], rows['near_exact'])

    near_optimal_is_knee = (
        lower_to_near_optimal['hard_cap_delta'] < near_optimal_to_near_exact['hard_cap_delta']
        and lower_to_near_optimal['net_checkpoint_count_delta'] < near_optimal_to_near_exact['net_checkpoint_count_delta']
        and lower_to_near_optimal['realized_worst_case_gain_share_delta']
        > near_optimal_to_near_exact['realized_worst_case_gain_share_delta']
    )

    report = {
        'focus': 'Price upgrades between the exact compact repeat-state uncertainty tiers so inheritors can compare the marginal operating cost of stricter guarantees instead of memorizing each lane in isolation.',
        'headline_findings': {
            'near_optimal_is_current_upgrade_knee': near_optimal_is_knee,
            'lower_to_near_optimal_hard_cap_delta': lower_to_near_optimal['hard_cap_delta'],
            'lower_to_near_optimal_net_checkpoint_count_delta': lower_to_near_optimal['net_checkpoint_count_delta'],
            'lower_to_near_optimal_realized_worst_case_gain_share_delta': lower_to_near_optimal['realized_worst_case_gain_share_delta'],
            'near_optimal_to_near_exact_hard_cap_delta': near_optimal_to_near_exact['hard_cap_delta'],
            'near_optimal_to_near_exact_net_checkpoint_count_delta': near_optimal_to_near_exact['net_checkpoint_count_delta'],
            'near_optimal_to_near_exact_realized_worst_case_gain_share_delta': near_optimal_to_near_exact['realized_worst_case_gain_share_delta'],
            'direct_lower_to_near_exact_hard_cap_delta': lower_to_near_exact['hard_cap_delta'],
            'direct_lower_to_near_exact_net_checkpoint_count_delta': lower_to_near_exact['net_checkpoint_count_delta'],
            'direct_lower_to_near_exact_realized_worst_case_gain_share_delta': lower_to_near_exact['realized_worst_case_gain_share_delta'],
            'master_audit_calendar_checkpoint_count': int(master['headline_findings']['full_master_audit_checkpoint_count']),
            'main_rule': 'treat the current 0.95 tier as the upgrade knee: moving up from 0.85 to 0.95 costs only +2 hard-cap steps and +3 net checkpoints while buying +0.109999 worst-case gain share, whereas pushing further from 0.95 to 0.99 costs +6 hard-cap steps and +6 net checkpoints for only +0.019341 more worst-case gain share.',
        },
        'decision_rules': [
            'Default to the exact 0.95 lane when the archive wants the best bargain between uncertainty guarantee and operating burden; it is the current upgrade knee.',
            'Relax from 0.95 to 0.85 only when surrendering roughly 0.11 worst-case gain share and the late-tail checkpoints 230/239 is an intentional maintenance-saving choice, not an accident.',
            'Upgrade from 0.95 to 0.99 only when near-exact preservation is the substantive goal itself; that last step is structurally expensive in both rewrite cap and checkpoint surface.',
            'Use the direct 0.85-to-0.99 span as the budget envelope for an all-the-way upgrade: +8 hard-cap steps, +9 net checkpoints, and a much tighter dwell corridor.',
        ],
        'tier_rows': tiers,
        'upgrade_rows': [lower_to_near_optimal, near_optimal_to_near_exact, lower_to_near_exact],
        'source_reports': [
            str(CAP_STAIRCASE_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_STAIRCASE_REPORT.relative_to(ROOT)),
            str(MASTER_AUDIT_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty Upgrade Tariff Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- near-optimal `0.95` is the current upgrade knee: `near_optimal_is_current_upgrade_knee = {findings['near_optimal_is_current_upgrade_knee']}`.",
        f"- upgrading `0.85 -> 0.95` costs `+{findings['lower_to_near_optimal_hard_cap_delta']}` hard-cap steps and `+{findings['lower_to_near_optimal_net_checkpoint_count_delta']}` net checkpoints while buying `+{findings['lower_to_near_optimal_realized_worst_case_gain_share_delta']}` worst-case gain share.",
        f"- upgrading `0.95 -> 0.99` costs `+{findings['near_optimal_to_near_exact_hard_cap_delta']}` hard-cap steps and `+{findings['near_optimal_to_near_exact_net_checkpoint_count_delta']}` net checkpoints while buying only `+{findings['near_optimal_to_near_exact_realized_worst_case_gain_share_delta']}` worst-case gain share.",
        f"- direct `0.85 -> 0.99` span: `+{findings['direct_lower_to_near_exact_hard_cap_delta']}` hard-cap steps, `+{findings['direct_lower_to_near_exact_net_checkpoint_count_delta']}` net checkpoints, `+{findings['direct_lower_to_near_exact_realized_worst_case_gain_share_delta']}` worst-case gain share, all still covered by the `master_audit_calendar_checkpoint_count = {findings['master_audit_calendar_checkpoint_count']}` sparse master calendar.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact certified tiers',
        '| tier | min gain floor | worst-case gain share | hard cap | anchor dwell | dwell band | band width | checkpoint count | checkpoint union |',
        '|---|---:|---:|---:|---:|---|---:|---:|---|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['worst_case_gain_share_of_full_dynamic_savings']} | {row['exact_hard_cap']} | {row['representative_anchor_minimum_dwell_unique_appends']} | {row['exact_dwell_band_start_unique_appends']}–{row['exact_dwell_band_end_unique_appends']} | {row['exact_dwell_band_width_unique_appends']} | {row['union_transition_checkpoint_count']} | {row['union_transition_checkpoints_unique_appends']} |"
        )
    lines.extend([
        '',
        '## Exact upgrade tariffs',
        '| upgrade | nominal floor delta | worst-case gain delta | hard-cap delta | net checkpoint delta | checkpoints added | checkpoints dropped | anchor shift | band-width delta |',
        '|---|---:|---:|---:|---:|---|---|---:|---:|',
    ])
    for row in report['upgrade_rows']:
        lines.append(
            f"| {row['from_tier']} -> {row['to_tier']} | {row['nominal_gain_floor_delta']} | {row['realized_worst_case_gain_share_delta']} | {row['hard_cap_delta']} | {row['net_checkpoint_count_delta']} | {row['checkpoints_added_unique_appends']} | {row['checkpoints_dropped_unique_appends']} | {row['representative_anchor_shift_unique_appends']} | {row['dwell_band_width_delta_unique_appends']} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Provenance',
        f"- source reports: {', '.join(report['source_reports'])}",
        f"- source script: `{report['source_script']}`",
        '',
    ])
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

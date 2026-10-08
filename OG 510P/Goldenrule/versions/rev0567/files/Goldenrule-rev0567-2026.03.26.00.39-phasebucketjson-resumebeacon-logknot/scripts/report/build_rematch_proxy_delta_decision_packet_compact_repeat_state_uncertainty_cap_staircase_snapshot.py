#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GUARDRAIL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
CAP_SAFE_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot_20260308.json'
CAP_SAFE_CHECKPOINT_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'
LOWER_GUARANTEE_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.md'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _guardrail_row(report: dict[str, Any], gain_share: float) -> dict[str, Any]:
    return next(
        row for row in report['guardrail_rows']
        if float(row['minimum_gain_share_of_full_dynamic_savings']) == gain_share
    )


def _build_report() -> dict[str, Any]:
    guardrail = _load(GUARDRAIL_REPORT)
    cap_safe = _load(CAP_SAFE_REPORT)
    cap_safe_checkpoints = _load(CAP_SAFE_CHECKPOINT_REPORT)
    lower_guarantee = _load(LOWER_GUARANTEE_REPORT)

    near_exact = _guardrail_row(guardrail, 0.99)
    near_optimal = _guardrail_row(guardrail, 0.95)
    stale_lower = _guardrail_row(guardrail, 0.85)
    cap_safe_findings = cap_safe['headline_findings']
    cap_safe_checkpoint_findings = cap_safe_checkpoints['headline_findings']
    lower_findings = lower_guarantee['headline_findings']

    tier_rows = [
        {
            'tier': 'near_exact',
            'minimum_gain_share_of_full_dynamic_savings': 0.99,
            'exact_hard_cap': int(near_exact['certified_band_wide_feasible_hard_cap']),
            'exact_dwell_band_start_unique_appends': int(near_exact['band_wide_cap_safe_overlap_start_unique_appends']),
            'exact_dwell_band_end_unique_appends': int(near_exact['band_wide_cap_safe_overlap_end_unique_appends']),
            'representative_anchor_minimum_dwell_unique_appends': int(near_exact['band_wide_cap_safe_anchor_minimum_dwell_unique_appends']),
            'representative_anchor_margin_unique_appends': int(near_exact['band_wide_cap_safe_anchor_margin_unique_appends']),
            'focal_expected_repeat_lookups': 0.18,
            'focal_selected_transition_count': int(near_exact['certified_focal_lower_bound_on_hard_cap']),
            'focal_gain_share_of_full_dynamic_savings': float(near_exact['focal_lower_bound_gain_share_of_full_dynamic_savings_at_0_18_repeats']),
            'focal_regret_vs_unbounded_dynamic': float(near_exact['focal_lower_bound_regret_vs_unbounded_dynamic_at_0_18_repeats']),
            'focal_interval_summary': str(near_exact['focal_lower_bound_interval_summary_at_0_18_repeats']),
            'note': str(near_exact['note']),
        },
        {
            'tier': 'near_optimal',
            'minimum_gain_share_of_full_dynamic_savings': 0.95,
            'exact_hard_cap': int(near_optimal['certified_band_wide_feasible_hard_cap']),
            'exact_dwell_band_start_unique_appends': int(near_optimal['cap_safe_overlap_start_unique_appends']),
            'exact_dwell_band_end_unique_appends': int(near_optimal['cap_safe_overlap_end_unique_appends']),
            'representative_anchor_minimum_dwell_unique_appends': int(near_optimal['cap_safe_anchor_minimum_dwell_unique_appends']),
            'representative_anchor_margin_unique_appends': int(near_optimal['cap_safe_anchor_margin_unique_appends']),
            'focal_expected_repeat_lookups': 0.18,
            'focal_selected_transition_count': int(near_optimal['selected_transition_count_at_0_18_repeats']),
            'focal_gain_share_of_full_dynamic_savings': float(near_optimal['gain_share_of_full_dynamic_savings_at_0_18_repeats']),
            'focal_regret_vs_unbounded_dynamic': float(near_optimal['regret_vs_unbounded_dynamic_at_0_18_repeats']),
            'focal_interval_summary': str(near_optimal['interval_summary_at_0_18_repeats']),
            'union_transition_checkpoints_unique_appends': cap_safe_checkpoint_findings['cap_safe_union_transition_checkpoints_unique_appends'],
            'checkpoint_union_matches_uncertainty_default': bool(cap_safe_checkpoint_findings['checkpoint_union_matches_uncertainty_default']),
            'note': 'This is the checkpoint-neutral cap-safe lane: it preserves the same eight-point union checkpoint calendar as the dwell-9 default while making the five-transition requirement explicit.',
        },
        {
            'tier': 'lower_guarantee',
            'minimum_gain_share_of_full_dynamic_savings': float(lower_findings['target_minimum_gain_share_of_full_dynamic_savings']),
            'exact_hard_cap': int(lower_findings['promoted_exact_band_wide_hard_cap']),
            'exact_dwell_band_start_unique_appends': int(lower_findings['promoted_exact_band_start_unique_appends']),
            'exact_dwell_band_end_unique_appends': int(lower_findings['promoted_exact_band_end_unique_appends']),
            'representative_anchor_minimum_dwell_unique_appends': int(lower_findings['promoted_exact_anchor_minimum_dwell_unique_appends']),
            'representative_anchor_margin_unique_appends': int(lower_findings['promoted_exact_anchor_margin_unique_appends']),
            'focal_expected_repeat_lookups': 0.18,
            'focal_selected_transition_count': 3,
            'focal_gain_share_of_full_dynamic_savings': float(lower_findings['anchor_worst_case_gain_share_of_full_dynamic_savings']),
            'focal_regret_vs_unbounded_dynamic': 1441.826445,
            'focal_interval_summary': 'pages 0–55; route-blocks 56–110; filters 111–158; route-blocks 159–256',
            'union_transition_checkpoints_unique_appends': lower_findings['anchor_union_transition_checkpoints_unique_appends'],
            'anchor_transition_range': lower_findings['anchor_transition_range'],
            'note': 'This exact three-cap lane supersedes the old conservative four-cap planning note for the relaxed 0.85 guarantee.',
        },
    ]

    exact_caps = [row['exact_hard_cap'] for row in tier_rows]
    report = {
        'focus': 'Refresh the repeat-uncertainty rewrite-cap story into one exact inheritor staircase so the archive stops carrying a stale lower-guarantee planning cap alongside newer exact certifications.',
        'source_reports': [
            str(GUARDRAIL_REPORT.relative_to(ROOT)),
            str(CAP_SAFE_REPORT.relative_to(ROOT)),
            str(CAP_SAFE_CHECKPOINT_REPORT.relative_to(ROOT)),
            str(LOWER_GUARANTEE_REPORT.relative_to(ROOT)),
        ],
        'headline_findings': {
            'exact_tier_count': len(tier_rows),
            'exact_hard_caps_descending_by_guarantee': exact_caps,
            'largest_exact_hard_cap': max(exact_caps),
            'smallest_exact_hard_cap': min(exact_caps),
            'near_exact_exact_hard_cap': tier_rows[0]['exact_hard_cap'],
            'near_optimal_exact_hard_cap': tier_rows[1]['exact_hard_cap'],
            'lower_guarantee_exact_hard_cap': tier_rows[2]['exact_hard_cap'],
            'near_optimal_checkpoint_union_matches_uncertainty_default': bool(tier_rows[1]['checkpoint_union_matches_uncertainty_default']),
            'stale_guardrail_lower_guarantee_cap': int(stale_lower['certified_band_wide_feasible_hard_cap']),
            'stale_guardrail_lower_guarantee_status': str(stale_lower['band_wide_hard_cap_status']),
            'stale_guardrail_lower_guarantee_has_been_superseded': True,
            'main_rule': 'keep the uncertainty-cap tradeoff as one exact three-tier staircase: hard cap 11 buys the near-exact 0.99 lane, hard cap 5 buys the checkpoint-neutral near-optimal 0.95 lane, and hard cap 3 buys the exact relaxed 0.85 lane; do not keep citing the stale four-cap lower-guarantee note.',
        },
        'decision_rules': [
            'When the archive needs an exact uncertainty-safe cap card, cite the three certified tiers together instead of mixing one fresh lower-guarantee note with one stale guardrail table.',
            'Use hard cap 11 only for near-exact 0.99 preservation, anchored at dwell 2.',
            'Use hard cap 5 for the current near-optimal 0.95 lane on dwell 8–18 with representative anchor 13; this lane is checkpoint-neutral relative to the dwell-9 default.',
            'Use hard cap 3 for the relaxed 0.85 lane on dwell 19–32 with representative anchor 25.',
            'Do not cite the old lower-guarantee four-cap planning row as current truth; it has been superseded by the exact three-cap certification.',
        ],
        'tier_rows': tier_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty-Cap Staircase Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the archive now has `{findings['exact_tier_count']}` exact uncertainty-cap tiers worth remembering together: hard caps `{findings['exact_hard_caps_descending_by_guarantee']}` map to guaranteed gain-share floors `0.99`, `0.95`, and `0.85` respectively.",
        f"- the near-optimal exact lane remains checkpoint-neutral relative to the dwell-`9` default: `near_optimal_checkpoint_union_matches_uncertainty_default = {findings['near_optimal_checkpoint_union_matches_uncertainty_default']}`.",
        f"- the old lower-guarantee guardrail row is now explicitly stale: it still says cap `{findings['stale_guardrail_lower_guarantee_cap']}` with status `{findings['stale_guardrail_lower_guarantee_status']}`, but that claim has been superseded by the exact three-cap certification.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact staircase rows',
        '| tier | minimum gain share | exact hard cap | dwell band | representative anchor | focal 0.18 transitions | focal 0.18 gain share | note |',
        '|---|---:|---:|---|---:|---:|---:|---|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['exact_hard_cap']} | {row['exact_dwell_band_start_unique_appends']}–{row['exact_dwell_band_end_unique_appends']} | {row['representative_anchor_minimum_dwell_unique_appends']} ± {row['representative_anchor_margin_unique_appends']} | {row['focal_selected_transition_count']} | {row['focal_gain_share_of_full_dynamic_savings']} | {row['note']} |"
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
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

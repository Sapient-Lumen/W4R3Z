#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.md'
MIN_DWELL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
REPEAT_UNCERTAINTY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
OPERATING_MODES_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.json'


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _intersections(
    focal_rows: list[dict[str, object]],
    *,
    overlap_start: int,
    overlap_end: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in focal_rows:
        start = max(overlap_start, int(row['minimum_dwell_start_unique_appends']))
        end = min(overlap_end, int(row['minimum_dwell_end_unique_appends']))
        if start > end:
            continue
        rows.append({
            'intersection_start_unique_appends': start,
            'intersection_end_unique_appends': end,
            'intersection_width_unique_appends': end - start + 1,
            'selected_transition_count_at_0_18_repeats': int(row['selected_transition_count']),
            'gain_share_of_full_dynamic_savings_at_0_18_repeats': float(row['gain_share_of_full_dynamic_savings']),
            'regret_vs_unbounded_dynamic_at_0_18_repeats': float(row['regret_vs_unbounded_dynamic']),
            'interval_summary_at_0_18_repeats': str(row['interval_summary']),
        })
    return rows


def _pick_cap_safe_anchor(
    intersections: list[dict[str, object]],
    *,
    max_transition_count: int,
) -> dict[str, object] | None:
    eligible = [
        row for row in intersections
        if row['selected_transition_count_at_0_18_repeats'] <= max_transition_count
    ]
    if not eligible:
        return None
    selected = max(
        eligible,
        key=lambda row: (
            row['intersection_width_unique_appends'],
            row['intersection_end_unique_appends'],
            -row['selected_transition_count_at_0_18_repeats'],
        ),
    )
    anchor = (
        selected['intersection_start_unique_appends']
        + selected['intersection_end_unique_appends']
    ) // 2
    margin = min(
        anchor - selected['intersection_start_unique_appends'],
        selected['intersection_end_unique_appends'] - anchor,
    )
    return {
        'cap_safe_overlap_start_unique_appends': selected['intersection_start_unique_appends'],
        'cap_safe_overlap_end_unique_appends': selected['intersection_end_unique_appends'],
        'cap_safe_overlap_width_unique_appends': selected['intersection_width_unique_appends'],
        'cap_safe_anchor_minimum_dwell_unique_appends': anchor,
        'cap_safe_anchor_margin_unique_appends': margin,
        'selected_transition_count_at_0_18_repeats': selected['selected_transition_count_at_0_18_repeats'],
        'gain_share_of_full_dynamic_savings_at_0_18_repeats': selected['gain_share_of_full_dynamic_savings_at_0_18_repeats'],
        'regret_vs_unbounded_dynamic_at_0_18_repeats': selected['regret_vs_unbounded_dynamic_at_0_18_repeats'],
        'interval_summary_at_0_18_repeats': selected['interval_summary_at_0_18_repeats'],
    }


def _build_summary() -> dict[str, object]:
    min_dwell = _load(MIN_DWELL_REPORT)
    repeat_uncertainty = _load(REPEAT_UNCERTAINTY_REPORT)
    operating_modes = _load(OPERATING_MODES_REPORT)

    focal_rows = min_dwell['frontier_rows']
    uncertainty_rows = repeat_uncertainty['uncertainty_rows']
    by_share = {
        float(row['minimum_gain_share_of_full_dynamic_savings']): row
        for row in uncertainty_rows
    }

    guardrail_rows = []
    for minimum_gain_share in [0.99, 0.95, 0.85]:
        uncertainty_row = by_share[minimum_gain_share]
        overlap_start = int(uncertainty_row['minimum_dwell_overlap_start_unique_appends'])
        overlap_end = int(uncertainty_row['minimum_dwell_overlap_end_unique_appends'])
        intersections = _intersections(
            focal_rows,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
        )
        certified_focal_lower_bound = min(
            row['selected_transition_count_at_0_18_repeats'] for row in intersections
        )
        focal_lower_bound_rows = [
            row for row in intersections
            if row['selected_transition_count_at_0_18_repeats'] == certified_focal_lower_bound
        ]
        focal_lower_bound_row = max(
            focal_lower_bound_rows,
            key=lambda row: (
                row['intersection_width_unique_appends'],
                row['intersection_end_unique_appends'],
            ),
        )
        guardrail_row = {
            'minimum_gain_share_of_full_dynamic_savings': minimum_gain_share,
            'uncertainty_safe_overlap_start_unique_appends': overlap_start,
            'uncertainty_safe_overlap_end_unique_appends': overlap_end,
            'uncertainty_safe_overlap_width_unique_appends': int(uncertainty_row['overlap_width_unique_appends']),
            'worst_case_gain_share_of_full_dynamic_savings_at_existing_uncertainty_anchor': float(
                uncertainty_row['worst_case_gain_share_of_full_dynamic_savings']
            ),
            'focal_transition_rows_inside_overlap': intersections,
            'certified_focal_lower_bound_on_hard_cap': certified_focal_lower_bound,
            'focal_lower_bound_overlap_start_unique_appends': focal_lower_bound_row['intersection_start_unique_appends'],
            'focal_lower_bound_overlap_end_unique_appends': focal_lower_bound_row['intersection_end_unique_appends'],
            'focal_lower_bound_gain_share_of_full_dynamic_savings_at_0_18_repeats': focal_lower_bound_row['gain_share_of_full_dynamic_savings_at_0_18_repeats'],
            'focal_lower_bound_regret_vs_unbounded_dynamic_at_0_18_repeats': focal_lower_bound_row['regret_vs_unbounded_dynamic_at_0_18_repeats'],
            'focal_lower_bound_interval_summary_at_0_18_repeats': focal_lower_bound_row['interval_summary_at_0_18_repeats'],
        }
        if minimum_gain_share == 0.99:
            guardrail_row.update({
                'certified_band_wide_feasible_hard_cap': 11,
                'band_wide_hard_cap_status': 'exact',
                'band_wide_cap_safe_anchor_minimum_dwell_unique_appends': 2,
                'band_wide_cap_safe_anchor_margin_unique_appends': 0,
                'band_wide_cap_safe_overlap_start_unique_appends': 2,
                'band_wide_cap_safe_overlap_end_unique_appends': 2,
                'note': 'near-exact uncertainty-robust behavior can be cap-minimized to dwell 2, but it still needs up to 11 transitions because the focal 0.18 frontier only drops below 11 after the 0.99-safe overlap has already ended.',
            })
        elif minimum_gain_share == 0.95:
            cap_safe = _pick_cap_safe_anchor(intersections, max_transition_count=5)
            assert cap_safe is not None
            guardrail_row.update({
                'certified_band_wide_feasible_hard_cap': 5,
                'band_wide_hard_cap_status': 'exact',
                **cap_safe,
                'note': 'a hard cap of 4 is impossible for the current 0.95 uncertainty band because every focal 0.18 dwell inside the 1–18 overlap still needs at least 5 transitions once the preset is far enough from the fragile 1–7 edge.',
            })
        else:
            cap_safe = _pick_cap_safe_anchor(intersections, max_transition_count=4)
            assert cap_safe is not None
            guardrail_row.update({
                'certified_band_wide_feasible_hard_cap': 4,
                'band_wide_hard_cap_status': 'planning_inference',
                **cap_safe,
                'note': 'the saved artifacts already show a promising 19–32 dwell band that drops the focal 0.18 planner to 3 transitions; pairing that with the non-increasing dwell rule and the existing 0.25 four-transition anchor makes 4 the current conservative band-wide cap for the lower-guarantee lane, but an exact minimum below 4 is not yet certified in the archive.',
            })
        guardrail_rows.append(guardrail_row)

    guardrails_by_share = {row['minimum_gain_share_of_full_dynamic_savings']: row for row in guardrail_rows}
    return {
        'focus': 'Expose the joint guardrails between repeat uncertainty and hard rewrite caps so future inheritors stop pretending the current compact repeat-sidecar presets can be both near-optimal and four-transition bounded at the same time.',
        'source_reports': [
            str(MIN_DWELL_REPORT.relative_to(ROOT)),
            str(REPEAT_UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(OPERATING_MODES_REPORT.relative_to(ROOT)),
        ],
        'headline_findings': {
            'current_operating_modes_rewrite_budget_ceiling': operating_modes['headline_findings']['rewrite_budget_mode_transition_ceiling'],
            'current_uncertainty_robust_default_minimum_dwell_unique_appends': operating_modes['headline_findings']['default_anchor_minimum_dwell_unique_appends'],
            'current_uncertainty_robust_default_transition_range': operating_modes['headline_findings']['default_transition_range'],
            'near_exact_certified_band_wide_hard_cap': guardrails_by_share[0.99]['certified_band_wide_feasible_hard_cap'],
            'near_optimal_certified_band_wide_hard_cap': guardrails_by_share[0.95]['certified_band_wide_feasible_hard_cap'],
            'near_optimal_cap_safe_overlap_start_unique_appends': guardrails_by_share[0.95]['cap_safe_overlap_start_unique_appends'],
            'near_optimal_cap_safe_overlap_end_unique_appends': guardrails_by_share[0.95]['cap_safe_overlap_end_unique_appends'],
            'near_optimal_cap_safe_anchor_minimum_dwell_unique_appends': guardrails_by_share[0.95]['cap_safe_anchor_minimum_dwell_unique_appends'],
            'near_optimal_four_transition_no_go': True,
            'lower_guarantee_conservative_band_wide_cap': guardrails_by_share[0.85]['certified_band_wide_feasible_hard_cap'],
            'lower_guarantee_cap_status': guardrails_by_share[0.85]['band_wide_hard_cap_status'],
            'lower_guarantee_planning_anchor_minimum_dwell_unique_appends': guardrails_by_share[0.85]['cap_safe_anchor_minimum_dwell_unique_appends'],
            'main_rule': 'do not promise one preset that is both four-transition bounded and 0.95-safe under the current repeat-uncertainty band; keep 5 transitions available for the robust near-optimal lane, or explicitly relax the guarantee before demanding a smaller cap.',
        },
        'decision_rules': [
            'Treat the current 4-transition staged planner and the current 0.95 uncertainty-robust preset as different operating lanes, not one merged promise.',
            'Keep 5 transitions available whenever the archive wants one minimum-dwell preset that remains near-optimal across repeat budgets 0.15–0.25.',
            'If the archive insists on a hard cap of 4 under repeat uncertainty, relax the guarantee first and move into the 19–32 dwell planning zone instead of pretending the dwell-9 lane still fits.',
            'Only target the 0.99-safe lane when the archive is willing to fund roughly 11 transitions; near-exact robustness is structurally expensive on the current frontier.',
        ],
        'guardrail_rows': guardrail_rows,
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty-Cap Guardrails Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the operating ladder still exposes a `{findings['current_operating_modes_rewrite_budget_ceiling']}`-transition rewrite-budget lane and a dwell-`{findings['current_uncertainty_robust_default_minimum_dwell_unique_appends']}` uncertainty-robust lane whose measured transition range is `{findings['current_uncertainty_robust_default_transition_range']['minimum_selected_transition_count']}`–`{findings['current_uncertainty_robust_default_transition_range']['maximum_selected_transition_count']}`.",
        f"- certified guardrail: the current `0.95` uncertainty-safe lane needs a hard cap of at least `{findings['near_optimal_certified_band_wide_hard_cap']}` transitions; a hard cap of `4` is incompatible with that guarantee.",
        f"- the cap-safe interior of that near-optimal lane is dwell `{findings['near_optimal_cap_safe_overlap_start_unique_appends']}`–`{findings['near_optimal_cap_safe_overlap_end_unique_appends']}`, with midpoint anchor `{findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends']}`.",
        f"- near-exact uncertainty-robust behavior remains structurally expensive: even after cap minimization it still needs `{findings['near_exact_certified_band_wide_hard_cap']}` transitions.",
        f"- the lower-guarantee lane has a conservative band-wide cap of `{findings['lower_guarantee_conservative_band_wide_cap']}` transitions and currently points at dwell `{findings['lower_guarantee_planning_anchor_minimum_dwell_unique_appends']}`, but its exact minimum cap is still a planning inference rather than a saved certification.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Joint guardrail rows',
        '| minimum gain share | uncertainty-safe dwell band | focal 0.18 transition rows inside band | certified focal lower bound on hard cap | certified band-wide feasible hard cap | cap status | cap-safe anchor | note |',
        '|---:|---|---|---:|---:|---|---:|---|',
    ]
    for row in report['guardrail_rows']:
        plateau_bits = ', '.join(
            f"{part['intersection_start_unique_appends']}–{part['intersection_end_unique_appends']}=>{part['selected_transition_count_at_0_18_repeats']}"
            for part in row['focal_transition_rows_inside_overlap']
        )
        anchor = row.get('band_wide_cap_safe_anchor_minimum_dwell_unique_appends')
        if anchor is None:
            anchor = row.get('cap_safe_anchor_minimum_dwell_unique_appends')
        lines.append(
            f"| {row['minimum_gain_share_of_full_dynamic_savings']} | {row['uncertainty_safe_overlap_start_unique_appends']}–{row['uncertainty_safe_overlap_end_unique_appends']} | {plateau_bits} | {row['certified_focal_lower_bound_on_hard_cap']} | {row['certified_band_wide_feasible_hard_cap']} | {row['band_wide_hard_cap_status']} | {anchor} | {row['note']} |"
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
    report = _build_summary()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

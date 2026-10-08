#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.md'
GUARANTEE_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
TOPOLOGY_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _witness(module: Any, *, dwell: int, floor: str = '0.80', cap: int = 20, checkpoints: int = 20) -> dict[str, Any]:
    return module.classify_request(
        required_gain_share_floor=floor,
        max_hard_cap_budget_inclusive=cap,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        target_dwell_unique_appends=dwell,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=checkpoints,
    )


def _build_summary() -> dict[str, Any]:
    guarantee = _load_json(GUARANTEE_REPORT)
    topology = _load_json(TOPOLOGY_REPORT)
    oracle = _load_oracle_module()

    tier_rows = {row['tier']: row for row in guarantee['tier_rows']}

    below_menu = _witness(oracle, dwell=1)
    precision = _witness(oracle, dwell=2, cap=11, checkpoints=14)
    internal_gap = _witness(oracle, dwell=5)
    high_floor_band = _witness(oracle, dwell=13, floor='0.96', cap=5, checkpoints=8)
    relaxed_suffix = _witness(oracle, dwell=25, floor='0.84', cap=3, checkpoints=5)
    above_menu = _witness(oracle, dwell=33)

    atlas_rows = [
        {
            'region_label': '<2',
            'target_dwell_interval_notation': '<2',
            'representative_target_dwell_unique_appends': 1,
            'menu_status': below_menu['status'],
            'blocking_summary': below_menu['blocking_summary'],
            'nearest_live_support_repair_unique_appends': below_menu['nearest_live_support_repair_for_target_dwell'],
            'most_important_rule': 'No current exact tier exists below dwell 2; repair by jumping directly to the precision singleton at dwell 2.',
        },
        {
            'region_label': '{2}',
            'target_dwell_interval_notation': '{2}',
            'representative_target_dwell_unique_appends': 2,
            'menu_status': precision['status'],
            'cheapest_exact_tier_available_at_target_dwell': 'near_exact',
            'maximum_actual_certified_gain_share_floor_of_full_dynamic_savings': tier_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'rounded_label_minimum_gain_share_of_full_dynamic_savings': tier_rows['near_exact']['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
            'exact_hard_cap': tier_rows['near_exact']['exact_hard_cap'],
            'mode_specific_checkpoint_count': tier_rows['near_exact']['union_transition_checkpoint_count'],
            'minimum_anchor_slack_unique_appends': tier_rows['near_exact']['minimum_anchor_slack_unique_appends'],
            'exact_dwell_band_width_unique_appends': tier_rows['near_exact']['exact_dwell_band_end_unique_appends'] - tier_rows['near_exact']['exact_dwell_band_start_unique_appends'] + 1,
            'canonical_anchor_minimum_dwell_unique_appends': tier_rows['near_exact']['canonical_anchor_minimum_dwell_unique_appends'],
            'most_important_rule': 'Target dwell 2 is precision-only: even low-floor requests must pay the near-exact cap/checkpoint budget if they insist on this dwell.',
        },
        {
            'region_label': '[3, 7]',
            'target_dwell_interval_notation': '[3, 7]',
            'representative_target_dwell_unique_appends': 5,
            'menu_status': internal_gap['status'],
            'blocking_summary': internal_gap['blocking_summary'],
            'nearest_live_support_repair_unique_appends': internal_gap['nearest_live_support_repair_for_target_dwell'],
            'most_important_rule': 'Dwell 3 through 7 remains an internal exact gap; skip local retuning here and jump to dwell 8 or back to dwell 2.',
        },
        {
            'region_label': '[8, 18]',
            'target_dwell_interval_notation': '[8, 18]',
            'representative_target_dwell_unique_appends': 13,
            'menu_status': high_floor_band['status'],
            'cheapest_exact_tier_available_at_target_dwell': 'near_optimal',
            'maximum_actual_certified_gain_share_floor_of_full_dynamic_savings': tier_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'rounded_label_minimum_gain_share_of_full_dynamic_savings': tier_rows['near_optimal']['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
            'exact_hard_cap': tier_rows['near_optimal']['exact_hard_cap'],
            'mode_specific_checkpoint_count': tier_rows['near_optimal']['union_transition_checkpoint_count'],
            'minimum_anchor_slack_unique_appends': tier_rows['near_optimal']['minimum_anchor_slack_unique_appends'],
            'exact_dwell_band_width_unique_appends': tier_rows['near_optimal']['exact_dwell_band_end_unique_appends'] - tier_rows['near_optimal']['exact_dwell_band_start_unique_appends'] + 1,
            'canonical_anchor_minimum_dwell_unique_appends': tier_rows['near_optimal']['canonical_anchor_minimum_dwell_unique_appends'],
            'most_important_rule': 'Dwell 8 through 18 is the strongest non-fragile exact band: it supports floors up to 0.980481 without collapsing to the precision singleton.',
        },
        {
            'region_label': '[19, 32]',
            'target_dwell_interval_notation': '[19, 32]',
            'representative_target_dwell_unique_appends': 25,
            'menu_status': relaxed_suffix['status'],
            'cheapest_exact_tier_available_at_target_dwell': 'lower_guarantee',
            'maximum_actual_certified_gain_share_floor_of_full_dynamic_savings': tier_rows['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            'rounded_label_minimum_gain_share_of_full_dynamic_savings': tier_rows['lower_guarantee']['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
            'exact_hard_cap': tier_rows['lower_guarantee']['exact_hard_cap'],
            'mode_specific_checkpoint_count': tier_rows['lower_guarantee']['union_transition_checkpoint_count'],
            'minimum_anchor_slack_unique_appends': tier_rows['lower_guarantee']['minimum_anchor_slack_unique_appends'],
            'exact_dwell_band_width_unique_appends': tier_rows['lower_guarantee']['exact_dwell_band_end_unique_appends'] - tier_rows['lower_guarantee']['exact_dwell_band_start_unique_appends'] + 1,
            'canonical_anchor_minimum_dwell_unique_appends': tier_rows['lower_guarantee']['canonical_anchor_minimum_dwell_unique_appends'],
            'most_important_rule': 'Dwell 19 through 32 is relaxed-only support: extra cap or checkpoints cannot lift this suffix above the exact 0.85 floor ceiling of 0.870482.',
        },
        {
            'region_label': '>32',
            'target_dwell_interval_notation': '>32',
            'representative_target_dwell_unique_appends': 33,
            'menu_status': above_menu['status'],
            'blocking_summary': above_menu['blocking_summary'],
            'nearest_live_support_repair_unique_appends': above_menu['nearest_live_support_repair_for_target_dwell'],
            'most_important_rule': 'No current exact tier exists above dwell 32; repair by dropping back to dwell 32 or generating new frontier evidence.',
        },
    ]

    headline_findings = {
        'main_rule': 'When a deployment shape pre-commits target dwell, start from the dwell atlas before broader retuning: dwell 2 forces the precision tier, dwell 8 through 18 is the strongest non-fragile exact band, dwell 19 through 32 is relaxed-only, and dwell 3 through 7 is dead search space.',
        'strongest_actual_certified_gain_share_floor_by_live_dwell_region': {
            '{2}': tier_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            '[8, 18]': tier_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            '[19, 32]': tier_rows['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        },
        'cheapest_exact_tier_by_live_dwell_region': {
            '{2}': 'near_exact',
            '[8, 18]': 'near_optimal',
            '[19, 32]': 'lower_guarantee',
        },
        'exact_hard_cap_by_live_dwell_region': {
            '{2}': tier_rows['near_exact']['exact_hard_cap'],
            '[8, 18]': tier_rows['near_optimal']['exact_hard_cap'],
            '[19, 32]': tier_rows['lower_guarantee']['exact_hard_cap'],
        },
        'mode_specific_checkpoint_count_by_live_dwell_region': {
            '{2}': tier_rows['near_exact']['union_transition_checkpoint_count'],
            '[8, 18]': tier_rows['near_optimal']['union_transition_checkpoint_count'],
            '[19, 32]': tier_rows['lower_guarantee']['union_transition_checkpoint_count'],
        },
        'internal_exact_gap_interval_unique_appends': [3, 7],
        'precision_singleton_forces_high_cap_even_at_low_floor': True,
        'relaxed_suffix_cannot_be_upgraded_by_extra_budget': True,
        'continuous_non_precision_exact_menu': [8, 32],
        'canonical_anchor_labels_by_live_dwell_region': {
            '{2}': tier_rows['near_exact']['canonical_anchor_minimum_dwell_unique_appends'],
            '[8, 18]': tier_rows['near_optimal']['canonical_anchor_minimum_dwell_unique_appends'],
            '[19, 32]': tier_rows['lower_guarantee']['canonical_anchor_minimum_dwell_unique_appends'],
        },
    }

    witness_examples = [
        {
            'example_label': 'precision_singleton_still_requires_precision_budget',
            'input': {
                'required_gain_share_floor': 0.999,
                'max_hard_cap_budget_inclusive': 10,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 2,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 20,
            },
            'oracle_result': oracle.classify_request(
                required_gain_share_floor='0.999',
                max_hard_cap_budget_inclusive=10,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=2,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=20,
            ),
        },
        {
            'example_label': 'high_floor_band_resolves_cleanly_inside_8_through_18',
            'input': {
                'required_gain_share_floor': 0.96,
                'max_hard_cap_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 2,
                'minimum_band_width_unique_appends': 3,
                'target_dwell_unique_appends': 13,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'oracle_result': oracle.classify_request(
                required_gain_share_floor='0.96',
                max_hard_cap_budget_inclusive=5,
                minimum_anchor_slack_unique_appends=2,
                minimum_band_width_unique_appends=3,
                target_dwell_unique_appends=13,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=8,
            ),
        },
        {
            'example_label': 'relaxed_suffix_is_pruned_once_floor_exceeds_0_870482',
            'input': {
                'required_gain_share_floor': 0.96,
                'max_hard_cap_budget_inclusive': 20,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 25,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 20,
            },
            'oracle_result': oracle.classify_request(
                required_gain_share_floor='0.96',
                max_hard_cap_budget_inclusive=20,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=25,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=20,
            ),
        },
    ]

    return {
        'focus': 'Turn the saved exact uncertainty tier cards into a target-dwell atlas so inheritors can start from the deployment shape itself when dwell is pre-committed, instead of re-deriving which exact tier even survives at that dwell.',
        'decision_rules': [
            'If target dwell is pre-committed, use the dwell atlas before broader cap or slack tuning because each live dwell region already has a unique strongest exact floor ceiling and cheapest surviving exact tier.',
            'Treat dwell 2 as a precision-only singleton: it is not a cheap low-floor shortcut because the near-exact tier is the only current exact row that contains it.',
            'Treat dwell 8 through 18 as the strongest non-fragile exact band and dwell 19 through 32 as relaxed-only support that cannot be upgraded by spending more cap or checkpoints.',
            'Treat dwell 3 through 7 as dead search space and dwell values below 2 or above 32 as outside the current exact menu until new frontier evidence appears.',
        ],
        'headline_findings': headline_findings,
        'atlas_rows': atlas_rows,
        'witness_examples': witness_examples,
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(TOPOLOGY_REPORT.relative_to(ROOT)),
            str(ORACLE_PATH.relative_to(ROOT)),
            str(Path(__file__).relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, Any]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Compact Repeat-State Uncertainty Target-Dwell Atlas Snapshot (2026-03-08)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Decision rules',
    ]
    for rule in summary['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Headline findings',
        f"- main rule: {findings['main_rule']}",
        f"- strongest certified floor by live dwell region: `{findings['strongest_actual_certified_gain_share_floor_by_live_dwell_region']}`.",
        f"- cheapest exact tier by live dwell region: `{findings['cheapest_exact_tier_by_live_dwell_region']}`.",
        f"- exact hard cap by live dwell region: `{findings['exact_hard_cap_by_live_dwell_region']}`.",
        f"- mode-specific checkpoint count by live dwell region: `{findings['mode_specific_checkpoint_count_by_live_dwell_region']}`.",
        f"- canonical anchor labels by live dwell region: `{findings['canonical_anchor_labels_by_live_dwell_region']}`.",
        f"- internal exact gap: `{findings['internal_exact_gap_interval_unique_appends']}`.",
        f"- precision singleton forces high cap even at low floor: `{findings['precision_singleton_forces_high_cap_even_at_low_floor']}`.",
        f"- relaxed suffix cannot be upgraded by extra budget: `{findings['relaxed_suffix_cannot_be_upgraded_by_extra_budget']}`.",
        f"- continuous non-precision exact menu: `{findings['continuous_non_precision_exact_menu']}`.",
        '',
        '## Atlas rows',
    ])
    for row in summary['atlas_rows']:
        lines.append(f"- `{row['target_dwell_interval_notation']}` -> status `{row['menu_status']}`.")
        if row['menu_status'] == 'exact_tier_available':
            lines.append(
                f"  - cheapest exact tier `{row['cheapest_exact_tier_available_at_target_dwell']}`, certified floor ceiling `{row['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings']}`, hard cap `{row['exact_hard_cap']}`, checkpoints `{row['mode_specific_checkpoint_count']}`, slack `{row['minimum_anchor_slack_unique_appends']}`, band width `{row['exact_dwell_band_width_unique_appends']}`, canonical anchor `{row['canonical_anchor_minimum_dwell_unique_appends']}`."
            )
        else:
            lines.append(
                f"  - blocking summary `{row['blocking_summary']}`, nearest live repair `{row['nearest_live_support_repair_unique_appends']}`."
            )
        lines.append(f"  - {row['most_important_rule']}")
    lines.extend([
        '',
        '## Checked oracle witnesses',
    ])
    for row in summary['witness_examples']:
        result = row['oracle_result']
        lines.append(
            f"- `{row['example_label']}` with input `{row['input']}` -> status `{result['status']}`, strongest feasible tier `{result['strongest_feasible_tier']}`, blocking summary `{result['blocking_summary']}`."
        )
    lines.extend([
        '',
        '## Why this matters',
        '- some deployments start from a fixed implementation shape, not from a floor target. The dwell atlas answers that dwell-first question directly.',
        '- the atlas makes two non-obvious costs explicit: insisting on dwell 2 forces the full precision tier even for low floors, while insisting on dwell 19+ hard-caps the best available exact floor at 0.870482 no matter how much extra budget you spend.',
        '- that means future inheritors can prune whole retuning branches immediately when dwell is already dictated by surrounding system constraints.',
        '',
        '## Sources',
    ])
    for src in summary['source_reports']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

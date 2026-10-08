#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.md'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'
FLOOR_SUPPORT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'
REPAIR_GUIDE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot_20260308.json'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
POST_AMORTIZATION_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_summary() -> dict[str, Any]:
    oracle = _load_oracle_module()
    floor_support = _load(FLOOR_SUPPORT_REPORT)
    repair_guide = _load(REPAIR_GUIDE_REPORT)
    guarantee = _load(GUARANTEE_REPORT)
    post_amortization = _load(POST_AMORTIZATION_REPORT)

    tier_rows = {row['tier']: row for row in guarantee['tier_rows']}
    selector_rows = {row['tier']: row for row in post_amortization['tier_rows']}

    examples = [
        {
            'example_label': 'strong_non_fragile_default',
            'input': {
                'required_gain_share_floor': '0.96',
                'max_hard_cap_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 2,
                'minimum_band_width_unique_appends': 4,
                'target_dwell_unique_appends': 13,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'expected_status': 'exact_tier_available',
            'expected_strongest_tier': 'near_optimal',
            'expected_blocking_summary': 'none',
        },
        {
            'example_label': 'high_floor_positive_slack_conflict',
            'input': {
                'required_gain_share_floor': '0.99',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 2,
                'master_calendar_pre_registered': True,
            },
            'expected_status': 'no_current_exact_tier',
            'expected_strongest_tier': None,
            'expected_blocking_summary': 'high_floor_positive_slack_conflict',
        },
        {
            'example_label': 'floor_pruned_relaxed_suffix',
            'input': {
                'required_gain_share_floor': '0.96',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 20,
                'master_calendar_pre_registered': True,
            },
            'expected_status': 'no_current_exact_tier',
            'expected_strongest_tier': None,
            'expected_blocking_summary': 'target_dwell_pruned_by_required_floor',
        },
        {
            'example_label': 'cap_underflow_on_relaxed_request',
            'input': {
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 2,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 25,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 5,
            },
            'expected_status': 'no_current_exact_tier',
            'expected_strongest_tier': None,
            'expected_blocking_summary': 'hard_cap_underflow',
        },
    ]

    resolved_examples = []
    for row in examples:
        result = oracle.classify_request(**row['input'])
        if result['status'] != row['expected_status']:
            raise SystemExit(f"unexpected status for {row['example_label']}: {result['status']}")
        if result['strongest_feasible_tier'] != row['expected_strongest_tier']:
            raise SystemExit(f"unexpected tier for {row['example_label']}: {result['strongest_feasible_tier']}")
        if result['blocking_summary'] != row['expected_blocking_summary']:
            raise SystemExit(f"unexpected blocking summary for {row['example_label']}: {result['blocking_summary']}")
        resolved_examples.append({**row, 'oracle_result': result})

    support_rows = floor_support['support_rows']
    if support_rows[0]['live_support_set_notation'] != '{2} ∪ [8, 32]':
        raise SystemExit('unexpected widest floor-conditioned support in source report')

    headline_findings = {
        'oracle_script': str(ORACLE_PATH.relative_to(ROOT)),
        'accepted_input_fields': [
            'required_gain_share_floor',
            'max_hard_cap_budget_inclusive',
            'minimum_anchor_slack_unique_appends',
            'minimum_band_width_unique_appends',
            'target_dwell_unique_appends',
            'master_calendar_pre_registered',
            'max_pre_amortization_checkpoint_budget_inclusive',
        ],
        'evaluation_order': [
            'required_gain_share_floor',
            'target_dwell_against_floor_conditioned_live_support',
            'hard_cap_budget',
            'checkpoint_budget_when_master_calendar_not_pre_registered',
            'minimum_anchor_slack',
            'minimum_band_width',
        ],
        'exact_floor_cliffs': [
            float(tier_rows['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings']),
            float(tier_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings']),
            float(tier_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings']),
        ],
        'widest_live_support_below_first_floor_cliff': support_rows[0]['live_support_set_notation'],
        'continuous_non_precision_support_after_first_floor_cliff': '[8, 18]',
        'singleton_precision_support_after_second_floor_cliff': '{2}',
        'strongest_future_proof_non_fragile_default': 'near_optimal',
        'mode_specific_checkpoint_thresholds_before_amortization': {
            tier: selector_rows[tier]['mode_specific_checkpoint_count'] for tier in ['lower_guarantee', 'near_optimal', 'near_exact']
        },
        'post_amortized_master_calendar_size': selector_rows['near_optimal']['post_amortized_checkpoint_count'],
        'main_rule': 'Route exact uncertainty-safe requests through one deterministic cascade: prune by required floor first, reject target dwell values outside the resulting live support immediately, then inspect the remaining tier deficits in cap, checkpoints, slack, and width instead of re-deriving the menu by hand.',
    }

    return {
        'focus': 'Turn the saved exact uncertainty-tier cards into a small executable request oracle so inheritors can classify a request bundle into strongest feasible tier or exact blocking deficits without reopening the heavy frontier computation.',
        'headline_findings': headline_findings,
        'oracle_examples': resolved_examples,
        'source_reports': [
            str(FLOOR_SUPPORT_REPORT.relative_to(ROOT)),
            str(REPAIR_GUIDE_REPORT.relative_to(ROOT)),
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(POST_AMORTIZATION_REPORT.relative_to(ROOT)),
            str(ORACLE_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, Any]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Compact Repeat-State Uncertainty Request Oracle Snapshot (2026-03-08)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- oracle script: `{findings['oracle_script']}`.",
        f"- accepted input fields: `{findings['accepted_input_fields']}`.",
        f"- evaluation order: `{findings['evaluation_order']}`.",
        f"- exact floor cliffs: `{findings['exact_floor_cliffs']}`.",
        f"- widest support below the first cliff: `{findings['widest_live_support_below_first_floor_cliff']}`.",
        f"- middle support after the first cliff: `{findings['continuous_non_precision_support_after_first_floor_cliff']}`.",
        f"- precision-only support after the second cliff: `{findings['singleton_precision_support_after_second_floor_cliff']}`.",
        f"- strongest future-proof non-fragile default: `{findings['strongest_future_proof_non_fragile_default']}`.",
        f"- mode-specific checkpoint thresholds before amortization: `{findings['mode_specific_checkpoint_thresholds_before_amortization']}`.",
        f"- post-amortized master calendar size: `{findings['post_amortized_master_calendar_size']}`.",
        '',
        '## Checked oracle examples',
    ]
    for row in summary['oracle_examples']:
        result = row['oracle_result']
        lines.append(
            f"- `{row['example_label']}` with input `{row['input']}` -> status `{result['status']}`, strongest feasible tier `{result['strongest_feasible_tier']}`, blocking summary `{result['blocking_summary']}`, live support `{result['floor_conditioned_live_support_components']}`."
        )
    lines.extend([
        '',
        '## Why this matters',
        '- future inheritors no longer need to hand-merge the threshold selector, dwell-topology card, repair guide, and post-amortization selector to understand one request bundle.',
        '- the oracle makes the archive declaration-first and deficit-first: it shows the strongest feasible exact tier when one exists and otherwise exposes the exact shortfalls that block each floor-eligible tier.',
        '- this makes follow-on tuning narrower because floor and dwell infeasibility are detected before expensive cap or tolerance discussions begin.',
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

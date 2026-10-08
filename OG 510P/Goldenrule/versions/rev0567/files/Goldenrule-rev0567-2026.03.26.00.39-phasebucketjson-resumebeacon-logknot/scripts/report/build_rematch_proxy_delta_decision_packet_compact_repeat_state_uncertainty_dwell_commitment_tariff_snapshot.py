#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot_20260308.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot_20260308.md'
GUARANTEE_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
TARGET_DWELL_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'
POST_AMORTIZATION_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_summary() -> dict[str, Any]:
    guarantee = _load_json(GUARANTEE_REPORT)
    target_dwell = _load_json(TARGET_DWELL_REPORT)
    post_amortization = _load_json(POST_AMORTIZATION_REPORT)
    oracle = _load_oracle_module()

    tiers = {row['tier']: row for row in guarantee['tier_rows']}
    near_exact = tiers['near_exact']
    near_optimal = tiers['near_optimal']
    lower_guarantee = tiers['lower_guarantee']
    master_calendar_count = post_amortization['headline_findings']['full_master_audit_checkpoint_count']

    precision_vs_neutral = {
        'target_dwell_region': '{2}',
        'comparison_baseline_region': '[8, 18]',
        'classification': 'avoidable_precision_commitment_when_floor_leq_0_980481',
        'meaningful_required_floor_interval': '[0, 0.980481]',
        'selected_exact_tier_at_committed_region': 'near_exact',
        'selected_exact_tier_at_baseline_region': 'near_optimal',
        'actual_certified_gain_share_floor_delta_vs_baseline': round(
            near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']
            - near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            6,
        ),
        'hard_cap_delta_vs_baseline': near_exact['exact_hard_cap'] - near_optimal['exact_hard_cap'],
        'pre_amortization_checkpoint_delta_vs_baseline': near_exact['union_transition_checkpoint_count'] - near_optimal['union_transition_checkpoint_count'],
        'post_amortization_checkpoint_delta_vs_baseline': 0,
        'minimum_anchor_slack_delta_vs_baseline': near_exact['minimum_anchor_slack_unique_appends'] - near_optimal['minimum_anchor_slack_unique_appends'],
        'exact_dwell_band_width_delta_vs_baseline': (
            (near_exact['exact_dwell_band_end_unique_appends'] - near_exact['exact_dwell_band_start_unique_appends'] + 1)
            - (near_optimal['exact_dwell_band_end_unique_appends'] - near_optimal['exact_dwell_band_start_unique_appends'] + 1)
        ),
        'most_important_rule': 'If the deployment does not physically require dwell 2 and the floor requirement is at most 0.980481, refusing the singleton avoids an exact +6 cap / +6 checkpoint precision premium and restores positive slack and band width.',
    }

    relaxed_vs_neutral = {
        'target_dwell_region': '[19, 32]',
        'comparison_baseline_region': '[8, 18]',
        'classification': 'relaxed_only_commitment_with_budget_tolerance_subsidy',
        'meaningful_required_floor_interval': '[0, 0.870482]',
        'selected_exact_tier_at_committed_region': 'lower_guarantee',
        'selected_exact_tier_at_baseline_region': 'near_optimal',
        'actual_certified_gain_share_floor_delta_vs_baseline': round(
            lower_guarantee['actual_certified_gain_share_floor_of_full_dynamic_savings']
            - near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            6,
        ),
        'hard_cap_delta_vs_baseline': lower_guarantee['exact_hard_cap'] - near_optimal['exact_hard_cap'],
        'pre_amortization_checkpoint_delta_vs_baseline': lower_guarantee['union_transition_checkpoint_count'] - near_optimal['union_transition_checkpoint_count'],
        'post_amortization_checkpoint_delta_vs_baseline': 0,
        'minimum_anchor_slack_delta_vs_baseline': lower_guarantee['minimum_anchor_slack_unique_appends'] - near_optimal['minimum_anchor_slack_unique_appends'],
        'exact_dwell_band_width_delta_vs_baseline': (
            (lower_guarantee['exact_dwell_band_end_unique_appends'] - lower_guarantee['exact_dwell_band_start_unique_appends'] + 1)
            - (near_optimal['exact_dwell_band_end_unique_appends'] - near_optimal['exact_dwell_band_start_unique_appends'] + 1)
        ),
        'most_important_rule': 'If the deployment does not physically require dwell 19 through 32, staying in the 8 through 18 band buys +0.109999 exact floor for only +2 cap and +3 checkpoints before amortization.',
    }

    neutral_row = {
        'target_dwell_region': '[8, 18]',
        'classification': 'neutral_exact_default_zone',
        'supported_required_floor_interval': '[0, 0.980481]',
        'selected_exact_tier': 'near_optimal',
        'actual_certified_gain_share_floor_of_full_dynamic_savings': near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        'exact_hard_cap': near_optimal['exact_hard_cap'],
        'pre_amortization_checkpoint_count': near_optimal['union_transition_checkpoint_count'],
        'post_amortized_checkpoint_count': master_calendar_count,
        'minimum_anchor_slack_unique_appends': near_optimal['minimum_anchor_slack_unique_appends'],
        'exact_dwell_band_width_unique_appends': near_optimal['exact_dwell_band_end_unique_appends'] - near_optimal['exact_dwell_band_start_unique_appends'] + 1,
        'most_important_rule': 'Treat dwell 8 through 18 as the neutral exact uncertainty zone whenever dwell is not externally fixed: it is the strongest non-fragile band and the cheapest region that still certifies floors above 0.870482.',
    }

    headline_findings = {
        'main_rule': 'If dwell is not physically pre-committed, default to the exact 8 through 18 band. Dwell 2 is an expensive precision commitment, while dwell 19 through 32 is a relaxed-only commitment that extra budget cannot upgrade.',
        'neutral_exact_default_region': '[8, 18]',
        'neutral_exact_default_tier': 'near_optimal',
        'singleton_precision_commitment_requires_extra_cap_for_small_extra_floor': True,
        'singleton_precision_commitment_hard_cap_delta_vs_neutral': precision_vs_neutral['hard_cap_delta_vs_baseline'],
        'singleton_precision_commitment_pre_amortization_checkpoint_delta_vs_neutral': precision_vs_neutral['pre_amortization_checkpoint_delta_vs_baseline'],
        'singleton_precision_commitment_floor_gain_vs_neutral': precision_vs_neutral['actual_certified_gain_share_floor_delta_vs_baseline'],
        'singleton_precision_commitment_slack_delta_vs_neutral': precision_vs_neutral['minimum_anchor_slack_delta_vs_baseline'],
        'relaxed_suffix_commitment_floor_loss_vs_neutral': abs(relaxed_vs_neutral['actual_certified_gain_share_floor_delta_vs_baseline']),
        'relaxed_suffix_commitment_hard_cap_savings_vs_neutral': abs(relaxed_vs_neutral['hard_cap_delta_vs_baseline']),
        'relaxed_suffix_commitment_pre_amortization_checkpoint_savings_vs_neutral': abs(relaxed_vs_neutral['pre_amortization_checkpoint_delta_vs_baseline']),
        'relaxed_suffix_commitment_extra_budget_cannot_upgrade_floor': True,
        'master_calendar_amortization_does_not_remove_dwell_commitment_cap_and_fragility_effects': True,
    }

    decision_rules = [
        'If dwell is not externally fixed and the required exact floor is at most 0.980481, start in the 8 through 18 band before considering singleton precision or the relaxed suffix.',
        'Only commit to dwell 2 when the floor requirement truly exceeds 0.980481 or an external deployment constraint literally fixes the singleton precision point.',
        'Only commit to dwell 19 through 32 when cap/tolerance constraints themselves force the relaxed exact 0.85 lane or when the deployment literally requires that dwell region.',
        'Do not expect master-calendar amortization to neutralize the singleton precision commitment: it removes checkpoint discrimination, but the +6 cap jump and fragility collapse remain.',
    ]

    witness_examples = [
        {
            'example_label': 'dwell_2_forces_avoidable_precision_premium_at_floor_0_96',
            'input': {
                'required_gain_share_floor': 0.96,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 2,
                'master_calendar_pre_registered': False,
                'max_hard_cap_budget_inclusive': 11,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
            'oracle_result': oracle.classify_request(
                required_gain_share_floor='0.96',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=2,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            ),
        },
        {
            'example_label': 'same_floor_in_neutral_zone_needs_only_near_optimal_budget',
            'input': {
                'required_gain_share_floor': 0.96,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 13,
                'master_calendar_pre_registered': False,
                'max_hard_cap_budget_inclusive': 5,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'oracle_result': oracle.classify_request(
                required_gain_share_floor='0.96',
                max_hard_cap_budget_inclusive=5,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=13,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=8,
            ),
        },
        {
            'example_label': 'relaxed_suffix_stays_relaxed_even_with_large_budget',
            'input': {
                'required_gain_share_floor': 0.84,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 25,
                'master_calendar_pre_registered': False,
                'max_hard_cap_budget_inclusive': 11,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
            'oracle_result': oracle.classify_request(
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                target_dwell_unique_appends=25,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            ),
        },
    ]

    return {
        'focus': 'Price exact uncertainty-safe target-dwell commitments against the neutral 8 through 18 band so inheritors can see when a pre-committed dwell is imposing an avoidable precision premium or an avoidable floor discount.',
        'headline_findings': headline_findings,
        'decision_rules': decision_rules,
        'commitment_rows': [precision_vs_neutral, neutral_row, relaxed_vs_neutral],
        'witness_examples': witness_examples,
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(TARGET_DWELL_REPORT.relative_to(ROOT)),
            str(POST_AMORTIZATION_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _to_markdown(summary: dict[str, Any]) -> str:
    findings = summary['headline_findings']
    rows = summary['commitment_rows']
    lines = [
        '# Compact Repeat-State Uncertainty Dwell-Commitment Tariff Snapshot',
        '',
        summary['focus'],
        '',
        '## Headline findings',
        '',
        f"- Main rule: {findings['main_rule']}",
        f"- Neutral exact default region: `{findings['neutral_exact_default_region']}` owned by exact `{findings['neutral_exact_default_tier']}`.",
        f"- Singleton precision commitment `{rows[0]['target_dwell_region']}` vs neutral band `{rows[0]['comparison_baseline_region']}`: `+{rows[0]['hard_cap_delta_vs_baseline']}` hard-cap steps, `+{rows[0]['pre_amortization_checkpoint_delta_vs_baseline']}` pre-amortization checkpoints, `{rows[0]['minimum_anchor_slack_delta_vs_baseline']}` slack delta, `{rows[0]['exact_dwell_band_width_delta_vs_baseline']}` band-width delta, for only `+{rows[0]['actual_certified_gain_share_floor_delta_vs_baseline']}` exact floor.",
        f"- Relaxed suffix commitment `{rows[2]['target_dwell_region']}` vs neutral band `{rows[2]['comparison_baseline_region']}`: `{rows[2]['hard_cap_delta_vs_baseline']}` hard-cap delta, `{rows[2]['pre_amortization_checkpoint_delta_vs_baseline']}` pre-amortization checkpoint delta, `+{rows[2]['minimum_anchor_slack_delta_vs_baseline']}` slack, `+{rows[2]['exact_dwell_band_width_delta_vs_baseline']}` width, but `{rows[2]['actual_certified_gain_share_floor_delta_vs_baseline']}` exact floor.",
        '',
        '## Decision rules',
        '',
    ]
    for rule in summary['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Commitment rows',
        '',
    ])
    for row in rows:
        lines.append(f"### {row['target_dwell_region']}")
        lines.append('')
        for key, value in row.items():
            lines.append(f'- {key}: `{value}`')
        lines.append('')
    lines.extend([
        '## Witness examples',
        '',
    ])
    for witness in summary['witness_examples']:
        result = witness['oracle_result']
        lines.append(f"- `{witness['example_label']}` -> status `{result['status']}`, strongest feasible tier `{result['strongest_feasible_tier']}`, blocker `{result['blocking_summary']}`.")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_to_markdown(summary), encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()

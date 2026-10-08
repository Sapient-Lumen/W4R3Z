#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.md'
TARGET_DWELL_ATLAS_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_target_dwell_atlas_snapshot_20260308.json'
PRECISION_GATE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.json'
DWELL_COMMITMENT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot_20260308.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py'

LIVE_REGIONS = ['{2}', '[8, 18]', '[19, 32]']
DEAD_REGIONS = ['<2', '[3, 7]', '>32']
UPGRADE_TARGET = {
    '{2}': None,
    '[8, 18]': '{2}',
    '[19, 32]': '[8, 18]',
}
DEAD_REPAIR = {
    '<2': '{2}',
    '[3, 7]': '[8, 18]',
    '>32': '[19, 32]',
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('compact_repeat_state_uncertainty_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _live_rows() -> list[dict[str, Any]]:
    atlas = _load(TARGET_DWELL_ATLAS_REPORT)
    atlas_rows = {row['region_label']: row for row in atlas['atlas_rows']}
    precision = _load(PRECISION_GATE_REPORT)
    neutral_floor = float(atlas['headline_findings']['strongest_actual_certified_gain_share_floor_by_live_dwell_region']['[8, 18]'])
    precision_floor = float(precision['headline_findings']['near_exact_exact_floor_ceiling'])

    rows: list[dict[str, Any]] = []
    for region in LIVE_REGIONS:
        row = atlas_rows[region]
        region_ceiling = float(row['maximum_actual_certified_gain_share_floor_of_full_dynamic_savings'])
        stronger_region = UPGRADE_TARGET[region]
        if stronger_region is None:
            next_region_floor = None
            extra_floor_available_by_retargeting = 0.0
        elif stronger_region == '{2}':
            next_region_floor = precision_floor
            extra_floor_available_by_retargeting = round(precision_floor - region_ceiling, 6)
        else:
            next_region_floor = neutral_floor
            extra_floor_available_by_retargeting = round(neutral_floor - region_ceiling, 6)

        rows.append(
            {
                'region_label': region,
                'ceiling_status': 'live_exact_region',
                'cheapest_exact_tier_available_at_target_dwell': row['cheapest_exact_tier_available_at_target_dwell'],
                'ceiling_actual_certified_gain_share_floor_of_full_dynamic_savings': region_ceiling,
                'ceiling_exact_hard_cap': int(row['exact_hard_cap']),
                'ceiling_mode_specific_checkpoint_count': int(row['mode_specific_checkpoint_count']),
                'ceiling_minimum_anchor_slack_unique_appends': int(row['minimum_anchor_slack_unique_appends']),
                'ceiling_exact_dwell_band_width_unique_appends': int(row['exact_dwell_band_width_unique_appends']),
                'canonical_anchor_minimum_dwell_unique_appends': int(row['canonical_anchor_minimum_dwell_unique_appends']),
                'extra_budget_can_raise_floor_without_changing_target_dwell': False,
                'next_region_needed_for_stronger_exact_floor': stronger_region,
                'next_region_floor_ceiling_if_retargeted': next_region_floor,
                'stronger_exact_floor_available_by_retargeting': extra_floor_available_by_retargeting,
                'most_important_rule': (
                    'This target-dwell region already sits at its strongest current exact floor ceiling; higher cap/checkpoint budget cannot raise the exact floor unless target dwell moves to a different live region.'
                    if stronger_region is not None
                    else 'This singleton is already the top saved exact floor ceiling; extra budget above the near-exact requirement buys no stronger current exact floor anywhere in the saved menu.'
                ),
            }
        )
    return rows


def _dead_rows() -> list[dict[str, Any]]:
    atlas = _load(TARGET_DWELL_ATLAS_REPORT)
    atlas_rows = {row['region_label']: row for row in atlas['atlas_rows']}
    rows: list[dict[str, Any]] = []
    for region in DEAD_REGIONS:
        row = atlas_rows[region]
        rows.append(
            {
                'region_label': region,
                'ceiling_status': 'dead_exact_region',
                'blocking_summary': row['blocking_summary'],
                'extra_budget_can_buy_entry_without_changing_target_dwell': False,
                'nearest_live_region_repair': DEAD_REPAIR[region],
                'nearest_live_support_repair_unique_appends': int(row['nearest_live_support_repair_unique_appends']),
                'most_important_rule': row['most_important_rule'],
            }
        )
    return rows


def _headline(live_rows: list[dict[str, Any]], dead_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_region = {row['region_label']: row for row in live_rows}
    return {
        'main_rule': 'When target dwell is fixed, treat each live region as having a hard exact floor ceiling: extra cap or checkpoint budget cannot buy a stronger exact floor until you move to a different live region.',
        'ceiling_actual_certified_gain_share_floor_by_live_region': {
            row['region_label']: row['ceiling_actual_certified_gain_share_floor_of_full_dynamic_savings'] for row in live_rows
        },
        'ceiling_exact_hard_cap_by_live_region': {
            row['region_label']: row['ceiling_exact_hard_cap'] for row in live_rows
        },
        'ceiling_mode_specific_checkpoint_count_by_live_region': {
            row['region_label']: row['ceiling_mode_specific_checkpoint_count'] for row in live_rows
        },
        'all_live_regions_are_budget_ceiling_limited_without_retargeting': all(
            not row['extra_budget_can_raise_floor_without_changing_target_dwell'] for row in live_rows
        ),
        'dead_regions_ignore_extra_budget_until_dwell_moves': all(
            not row['extra_budget_can_buy_entry_without_changing_target_dwell'] for row in dead_rows
        ),
        'stronger_floor_requires_region_jump': {
            '[19, 32]': by_region['[19, 32]']['next_region_needed_for_stronger_exact_floor'],
            '[8, 18]': by_region['[8, 18]']['next_region_needed_for_stronger_exact_floor'],
            '{2}': by_region['{2}']['next_region_needed_for_stronger_exact_floor'],
        },
        'extra_floor_available_only_by_retargeting': {
            row['region_label']: row['stronger_exact_floor_available_by_retargeting'] for row in live_rows
        },
        'post_amortization_master_calendar_changes_only_checkpoint_payment_not_region_ceiling': True,
    }


def _decision_rules() -> list[str]:
    return [
        'When target dwell is physically fixed, optimize only up to that region\'s exact floor ceiling; stop spending extra cap/checkpoint budget once the region ceiling is reached.',
        'Treat dwell 8 through 18 as the strongest non-fragile live region: its fixed-dwell exact ceiling is 0.980481 and no amount of extra budget can push that region higher without collapsing to dwell 2.',
        'Treat dwell 19 through 32 as a relaxed-only suffix with a hard ceiling of 0.870482: higher cap or checkpoints are wasted there unless you retarget into the 8 through 18 band.',
        'Treat dwell 2 as the precision singleton ceiling itself: once you have paid cap 11 and the near-exact fragility cost, there is no stronger current exact floor left to buy inside the saved menu.',
        'Treat dead regions (<2, 3 through 7, >32) as budget-impotent gaps: no amount of extra cap or checkpoints buys entry until target dwell moves to live support.',
    ]


def _witness_examples() -> list[dict[str, Any]]:
    oracle = _load_oracle_module()
    examples = [
        (
            'extra_budget_cannot_upgrade_8_through_18_past_its_region_ceiling',
            {
                'required_gain_share_floor': '0.99',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 13,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
        ),
        (
            'extra_budget_cannot_upgrade_19_through_32_past_its_region_ceiling',
            {
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 25,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
        ),
        (
            'dead_gap_ignores_extra_budget_until_dwell_moves',
            {
                'required_gain_share_floor': '0.85',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'target_dwell_unique_appends': 5,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
        ),
    ]
    rows: list[dict[str, Any]] = []
    for label, kwargs in examples:
        result = oracle.classify_request(**kwargs)
        payload = dict(kwargs)
        payload['required_gain_share_floor'] = float(payload['required_gain_share_floor'])
        rows.append({'example_label': label, 'input': payload, 'oracle_result': result})
    return rows


def _build_report() -> dict[str, Any]:
    live_rows = _live_rows()
    dead_rows = _dead_rows()
    return {
        'focus': 'Turn the fixed-dwell atlas into a budget-ceiling card so inheritors stop wasting cap and checkpoint budget on a target-dwell region whose strongest current exact floor is already saturated.',
        'headline_findings': _headline(live_rows, dead_rows),
        'decision_rules': _decision_rules(),
        'live_region_rows': live_rows,
        'dead_region_rows': dead_rows,
        'witness_examples': _witness_examples(),
        'source_reports': [
            str(TARGET_DWELL_ATLAS_REPORT.relative_to(ROOT)),
            str(PRECISION_GATE_REPORT.relative_to(ROOT)),
            str(DWELL_COMMITMENT_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty fixed-dwell budget ceiling snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Live dwell-region ceiling rows')
    for row in report['live_region_rows']:
        lines.append(
            '- '
            f"{row['region_label']}: tier `{row['cheapest_exact_tier_available_at_target_dwell']}`; "
            f"ceiling floor `{row['ceiling_actual_certified_gain_share_floor_of_full_dynamic_savings']}`; "
            f"cap `{row['ceiling_exact_hard_cap']}`; checkpoints `{row['ceiling_mode_specific_checkpoint_count']}`; "
            f"slack `{row['ceiling_minimum_anchor_slack_unique_appends']}`; width `{row['ceiling_exact_dwell_band_width_unique_appends']}`; "
            f"next stronger region `{row['next_region_needed_for_stronger_exact_floor']}`; "
            f"extra floor only by retargeting `{row['stronger_exact_floor_available_by_retargeting']}`"
        )
    lines.append('')
    lines.append('## Dead dwell-region rows')
    for row in report['dead_region_rows']:
        lines.append(
            '- '
            f"{row['region_label']}: blocker `{row['blocking_summary']}`; "
            f"nearest live repair `{row['nearest_live_region_repair']}` at dwell `{row['nearest_live_support_repair_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Witness examples')
    for row in report['witness_examples']:
        lines.append(
            '- '
            f"{row['example_label']}: status `{row['oracle_result']['status']}`; "
            f"blocking summary `{row['oracle_result']['blocking_summary']}`; "
            f"strongest feasible tier `{row['oracle_result']['strongest_feasible_tier']}`"
        )
    lines.append('')
    lines.append('## Sources')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['source_script']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

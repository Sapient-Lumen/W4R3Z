#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot_20260308.md'
MIN_DWELL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
ANCHOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.json'
UNCERTAINTY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
GUARDRAIL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'
CAP_SAFE_CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'

INTERVAL_RE = re.compile(r'(?P<kind>[a-z\-]+) (?P<start>\d+)–(?P<end>\d+)$')
TARGET_GAIN_SHARE = 0.95


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _transition_boundaries(interval_summary: str) -> list[int]:
    points = []
    for chunk in interval_summary.split('; ')[1:]:
        match = INTERVAL_RE.fullmatch(chunk)
        if match is None:
            raise ValueError(f'unexpected interval chunk: {chunk!r}')
        points.append(int(match.group('start')))
    return points


def _build_summary() -> dict[str, object]:
    min_dwell = _load(MIN_DWELL_REPORT)
    anchor = _load(ANCHOR_REPORT)
    uncertainty = _load(UNCERTAINTY_REPORT)
    guardrail = _load(GUARDRAIL_REPORT)
    checkpoints = _load(CHECKPOINT_REPORT)
    cap_safe_checkpoints = _load(CAP_SAFE_CHECKPOINT_REPORT)

    anchor_findings = anchor['headline_findings']
    guardrail_findings = guardrail['headline_findings']
    uncertainty_row = next(
        row for row in uncertainty['uncertainty_rows']
        if float(row['minimum_gain_share_of_full_dynamic_savings']) == TARGET_GAIN_SHARE
    )
    focal_plateau = next(
        row for row in min_dwell['frontier_rows']
        if int(row['minimum_dwell_start_unique_appends']) == 8 and int(row['minimum_dwell_end_unique_appends']) == 18
    )
    left_neighbor = next(
        row for row in min_dwell['frontier_rows']
        if int(row['minimum_dwell_start_unique_appends']) == 7 and int(row['minimum_dwell_end_unique_appends']) == 7
    )
    right_neighbor = next(
        row for row in min_dwell['frontier_rows']
        if int(row['minimum_dwell_start_unique_appends']) == 19 and int(row['minimum_dwell_end_unique_appends']) == 48
    )

    default_focal_row = next(
        row for row in checkpoints['mode_boundary_rows']
        if row['mode'] == 'uncertainty_robust_default' and float(row['expected_repeat_lookups']) == 0.18
    )
    cap_safe_focal_row = next(
        row for row in cap_safe_checkpoints['cap_safe_boundary_rows']
        if float(row['expected_repeat_lookups']) == 0.18
    )
    focal_checkpoints = _transition_boundaries(str(focal_plateau['interval_summary']))

    findings = {
        'target_minimum_gain_share_of_full_dynamic_savings': TARGET_GAIN_SHARE,
        'cap_safe_band_start_unique_appends': int(focal_plateau['minimum_dwell_start_unique_appends']),
        'cap_safe_band_end_unique_appends': int(focal_plateau['minimum_dwell_end_unique_appends']),
        'cap_safe_band_width_unique_appends': int(focal_plateau['minimum_dwell_end_unique_appends']) - int(focal_plateau['minimum_dwell_start_unique_appends']) + 1,
        'representative_anchor_minimum_dwell_unique_appends': int(guardrail_findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends']),
        'representative_anchor_margin_unique_appends': int(anchor_findings['ninety_five_percent_anchor_margin_unique_appends']),
        'uncertainty_default_anchor_minimum_dwell_unique_appends': int(uncertainty_row['anchor_minimum_dwell_unique_appends']),
        'uncertainty_default_anchor_is_inside_cap_safe_band': int(focal_plateau['minimum_dwell_start_unique_appends']) <= int(uncertainty_row['anchor_minimum_dwell_unique_appends']) <= int(focal_plateau['minimum_dwell_end_unique_appends']),
        'focal_expected_repeat_lookups': float(min_dwell['focal_expected_repeat_lookups']),
        'focal_selected_transition_count': int(focal_plateau['selected_transition_count']),
        'focal_gain_share_of_full_dynamic_savings': float(focal_plateau['gain_share_of_full_dynamic_savings']),
        'focal_regret_vs_unbounded_dynamic': float(focal_plateau['regret_vs_unbounded_dynamic']),
        'focal_transition_checkpoints_unique_appends': focal_checkpoints,
        'focal_transition_checkpoint_count': len(focal_checkpoints),
        'uncertainty_default_focal_checkpoints_match_cap_safe_band': default_focal_row['transition_boundaries_unique_appends'] == focal_checkpoints,
        'representative_anchor_focal_checkpoints_match_default_anchor': cap_safe_focal_row['transition_boundaries_unique_appends'] == default_focal_row['transition_boundaries_unique_appends'],
        'left_boundary_transition_count_before_cap_safe_band': int(left_neighbor['selected_transition_count']),
        'left_boundary_gain_share_before_cap_safe_band': float(left_neighbor['gain_share_of_full_dynamic_savings']),
        'right_boundary_transition_count_after_cap_safe_band': int(right_neighbor['selected_transition_count']),
        'right_boundary_gain_share_after_cap_safe_band': float(right_neighbor['gain_share_of_full_dynamic_savings']),
        'main_rule': 'treat dwell 13 as the label for the cap-safe near-optimal lane, not as a sacred constant: the whole dwell band 8–18 is one focal five-transition plateau, while 7 and 19 are the real structural boundaries that change the promised lane.',
    }

    return {
        'focus': 'Clarify whether the cap-safe near-optimal dwell anchor is a brittle magic constant or a representative label for a wider interchangeable band so future inheritors preserve the real boundaries instead of memorizing one integer.',
        'headline_findings': findings,
        'cap_safe_band_row': {
            'minimum_dwell_start_unique_appends': int(focal_plateau['minimum_dwell_start_unique_appends']),
            'minimum_dwell_end_unique_appends': int(focal_plateau['minimum_dwell_end_unique_appends']),
            'selected_transition_count': int(focal_plateau['selected_transition_count']),
            'gain_share_of_full_dynamic_savings': float(focal_plateau['gain_share_of_full_dynamic_savings']),
            'regret_vs_unbounded_dynamic': float(focal_plateau['regret_vs_unbounded_dynamic']),
            'interval_summary': str(focal_plateau['interval_summary']),
            'transition_checkpoints_unique_appends': focal_checkpoints,
        },
        'neighbor_rows': [
            {
                'position': 'left_boundary_before_cap_safe_band',
                'minimum_dwell_start_unique_appends': int(left_neighbor['minimum_dwell_start_unique_appends']),
                'minimum_dwell_end_unique_appends': int(left_neighbor['minimum_dwell_end_unique_appends']),
                'selected_transition_count': int(left_neighbor['selected_transition_count']),
                'gain_share_of_full_dynamic_savings': float(left_neighbor['gain_share_of_full_dynamic_savings']),
                'regret_vs_unbounded_dynamic': float(left_neighbor['regret_vs_unbounded_dynamic']),
                'interval_summary': str(left_neighbor['interval_summary']),
            },
            {
                'position': 'right_boundary_after_cap_safe_band',
                'minimum_dwell_start_unique_appends': int(right_neighbor['minimum_dwell_start_unique_appends']),
                'minimum_dwell_end_unique_appends': int(right_neighbor['minimum_dwell_end_unique_appends']),
                'selected_transition_count': int(right_neighbor['selected_transition_count']),
                'gain_share_of_full_dynamic_savings': float(right_neighbor['gain_share_of_full_dynamic_savings']),
                'regret_vs_unbounded_dynamic': float(right_neighbor['regret_vs_unbounded_dynamic']),
                'interval_summary': str(right_neighbor['interval_summary']),
            },
        ],
        'decision_rules': [
            'Document the near-optimal cap-safe lane as dwell band 8–18 with representative label 13 so future sessions keep the real invariant instead of overfitting to one integer.',
            'Treat dwell 9 and dwell 13 as focal-plan-equivalent on the saved frontier: both sit inside the same 0.18 five-transition plateau and hit the same focal checkpoints [24, 63, 111, 159, 239].',
            'Fail fast when a proposed change crosses below dwell 8 or above dwell 18 without an explicit lane change, because 7 and 19 are the boundaries where the schedule and guarantee move onto different plateaus.',
        ],
        'source_reports': [
            str(MIN_DWELL_REPORT.relative_to(ROOT)),
            str(ANCHOR_REPORT.relative_to(ROOT)),
            str(UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(GUARDRAIL_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_REPORT.relative_to(ROOT)),
            str(CAP_SAFE_CHECKPOINT_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    band = report['cap_safe_band_row']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Cap-Safe Anchor Fungibility Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the near-optimal cap-safe lane is a full dwell band, not one brittle point: focal dwell `{findings['cap_safe_band_start_unique_appends']}`–`{findings['cap_safe_band_end_unique_appends']}` is one `{findings['focal_selected_transition_count']}`-transition plateau at repeat budget `{findings['focal_expected_repeat_lookups']}`.",
        f"- the representative label remains dwell `{findings['representative_anchor_minimum_dwell_unique_appends']}` with ±`{findings['representative_anchor_margin_unique_appends']}` margin, but the current uncertainty-default dwell `{findings['uncertainty_default_anchor_minimum_dwell_unique_appends']}` also sits inside that cap-safe band: `{findings['uncertainty_default_anchor_is_inside_cap_safe_band']}`.",
        f"- every dwell inside that focal cap-safe band shares the same measured summary `{band['interval_summary']}`, the same gain share `{findings['focal_gain_share_of_full_dynamic_savings']}`, and the same focal checkpoints `{findings['focal_transition_checkpoints_unique_appends']}`.",
        f"- the saved frontier's real boundaries are the neighbors: dwell `7` still needs `{findings['left_boundary_transition_count_before_cap_safe_band']}` transitions, while dwell `19` drops to `{findings['right_boundary_transition_count_after_cap_safe_band']}` transitions but also falls to gain share `{findings['right_boundary_gain_share_after_cap_safe_band']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Cap-safe focal plateau',
        '| dwell band | focal transitions | gain share | regret vs full dynamic | checkpoints | summary |',
        '|---|---:|---:|---:|---|---|',
        f"| {band['minimum_dwell_start_unique_appends']}–{band['minimum_dwell_end_unique_appends']} | {band['selected_transition_count']} | {band['gain_share_of_full_dynamic_savings']} | {band['regret_vs_unbounded_dynamic']} | {band['transition_checkpoints_unique_appends']} | {band['interval_summary']} |",
        '',
        '## Structural boundary neighbors',
        '| position | dwell band | transitions | gain share | regret vs full dynamic | summary |',
        '|---|---|---:|---:|---:|---|',
    ]
    for row in report['neighbor_rows']:
        lines.append(
            f"| {row['position']} | {row['minimum_dwell_start_unique_appends']}–{row['minimum_dwell_end_unique_appends']} | {row['selected_transition_count']} | {row['gain_share_of_full_dynamic_savings']} | {row['regret_vs_unbounded_dynamic']} | {row['interval_summary']} |"
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

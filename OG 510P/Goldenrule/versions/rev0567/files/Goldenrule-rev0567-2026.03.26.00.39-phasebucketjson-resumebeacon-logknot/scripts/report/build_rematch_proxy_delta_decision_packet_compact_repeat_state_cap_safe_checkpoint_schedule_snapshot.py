#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.md'
UNCERTAINTY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
MIN_DWELL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
GUARDRAIL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.json'
CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'

INTERVAL_RE = re.compile(r'(?P<kind>[a-z\-]+) (?P<start>\d+)–(?P<end>\d+)$')
TARGET_GAIN_SHARE = 0.95
TARGET_REPEATS = [0.15, 0.18, 0.25]


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _parse_interval_summary(interval_summary: str) -> list[dict[str, object]]:
    rows = []
    for chunk in interval_summary.split('; '):
        match = INTERVAL_RE.fullmatch(chunk)
        if match is None:
            raise ValueError(f'unexpected interval chunk: {chunk!r}')
        rows.append(
            {
                'state_kind_label': match.group('kind'),
                'start_unique_appends': int(match.group('start')),
                'end_unique_appends': int(match.group('end')),
            }
        )
    return rows


def _transition_boundaries(interval_summary: str) -> list[int]:
    return [row['start_unique_appends'] for row in _parse_interval_summary(interval_summary)[1:]]


def _build_summary() -> dict[str, object]:
    uncertainty = _load(UNCERTAINTY_REPORT)
    min_dwell = _load(MIN_DWELL_REPORT)
    guardrail = _load(GUARDRAIL_REPORT)
    checkpoints = _load(CHECKPOINT_REPORT)

    guardrail_findings = guardrail['headline_findings']
    target_anchor = int(guardrail_findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends'])

    uncertainty_row = next(
        row for row in uncertainty['uncertainty_rows']
        if float(row['minimum_gain_share_of_full_dynamic_savings']) == TARGET_GAIN_SHARE
    )
    focal_row = next(
        row for row in min_dwell['frontier_rows']
        if int(row['minimum_dwell_start_unique_appends']) <= target_anchor <= int(row['minimum_dwell_end_unique_appends'])
    )

    boundary_rows = []
    for repeat_value in TARGET_REPEATS:
        if repeat_value == 0.18:
            source_row = focal_row
            admissible_end = int(focal_row['minimum_dwell_end_unique_appends'])
            admissible_start = int(focal_row['minimum_dwell_start_unique_appends'])
        else:
            source_row = next(
                row for row in uncertainty_row['anchor_rows']
                if float(row['expected_repeat_lookups']) == repeat_value
            )
            admissible_start = 1
            admissible_end = int(source_row['admissible_minimum_dwell_end_unique_appends'])
        assert admissible_start <= target_anchor <= admissible_end
        boundaries = _transition_boundaries(source_row['interval_summary'])
        boundary_rows.append(
            {
                'expected_repeat_lookups': repeat_value,
                'minimum_dwell_unique_appends': target_anchor,
                'admissible_minimum_dwell_start_unique_appends': admissible_start,
                'admissible_minimum_dwell_end_unique_appends': admissible_end,
                'selected_transition_count': int(source_row['selected_transition_count']),
                'gain_share_of_full_dynamic_savings': float(source_row['gain_share_of_full_dynamic_savings']),
                'transition_boundaries_unique_appends': boundaries,
                'interval_summary': str(source_row['interval_summary']),
            }
        )

    union_checkpoints = sorted({p for row in boundary_rows for p in row['transition_boundaries_unique_appends']})
    default_union = checkpoints['headline_findings']['default_robust_union_transition_checkpoints_unique_appends']

    findings = {
        'near_optimal_cap_safe_anchor_minimum_dwell_unique_appends': target_anchor,
        'near_optimal_certified_band_wide_hard_cap': int(guardrail_findings['near_optimal_certified_band_wide_hard_cap']),
        'cap_safe_union_transition_checkpoints_unique_appends': union_checkpoints,
        'cap_safe_union_transition_checkpoint_count': len(union_checkpoints),
        'checkpoint_union_matches_uncertainty_default': union_checkpoints == default_union,
        'uncertainty_default_anchor_minimum_dwell_unique_appends': int(checkpoints['headline_findings']['default_robust_minimum_dwell_unique_appends']),
        'uncertainty_default_union_transition_checkpoints_unique_appends': default_union,
        'focal_repeat_budget_for_certified_cap': 0.18,
        'focal_selected_transition_count': int(focal_row['selected_transition_count']),
        'main_rule': 'the cap-safe near-optimal uncertainty lane can move from dwell 9 to dwell 13 without increasing the archive\'s finite checkpoint surface across the current 0.15–0.25 repeat band, so the real tradeoff is guarantee compatibility versus transition count, not maintenance sprawl.',
    }

    return {
        'focus': 'Certify the finite checkpoint schedule for the cap-safe near-optimal uncertainty lane so future inheritors know whether moving from the default dwell-9 preset to the five-transition-safe dwell-13 preset changes maintenance burden.',
        'headline_findings': findings,
        'cap_safe_boundary_rows': boundary_rows,
        'decision_rules': [
            'Use the cap-safe dwell-13 lane when repeat uncertainty is real, near-optimal 0.95-safe behavior is still required, and the archive can fund 5 transitions.',
            'Do not reject dwell 13 on maintenance-cost grounds alone: its measured union checkpoint set is no larger than the current uncertainty-default dwell-9 union.',
            'If a hard cap of 4 is non-negotiable, fail fast instead of trying to compress the dwell-13 lane further; that incompatibility is structural on the saved frontier.',
        ],
        'source_reports': [
            str(UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(MIN_DWELL_REPORT.relative_to(ROOT)),
            str(GUARDRAIL_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, object]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Cap-Safe Checkpoint Schedule Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the cap-safe near-optimal uncertainty lane is dwell `{findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends']}` with certified band-wide hard cap `{findings['near_optimal_certified_band_wide_hard_cap']}` transitions.",
        f"- its finite union checkpoint set across repeat budgets `0.15`, `0.18`, and `0.25` is `{findings['cap_safe_union_transition_checkpoints_unique_appends']}`.",
        f"- that union has `{findings['cap_safe_union_transition_checkpoint_count']}` checkpoints and matches the current uncertainty-default dwell-`{findings['uncertainty_default_anchor_minimum_dwell_unique_appends']}` union exactly: `{findings['checkpoint_union_matches_uncertainty_default']}`.",
        f"- at the focal repeat budget `{findings['focal_repeat_budget_for_certified_cap']}`, the cap-safe anchor still uses `{findings['focal_selected_transition_count']}` transitions, which is why the archive needs cap `5` rather than `4`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Checkpoints by repeat budget for the cap-safe anchor',
        '| repeat budget | admissible dwell band covering anchor 13 | selected transitions | checkpoints | summary |',
        '|---:|---|---:|---|---|',
    ]
    for row in report['cap_safe_boundary_rows']:
        lines.append(
            f"| {row['expected_repeat_lookups']} | {row['admissible_minimum_dwell_start_unique_appends']}–{row['admissible_minimum_dwell_end_unique_appends']} | {row['selected_transition_count']} | {row['transition_boundaries_unique_appends']} | {row['interval_summary']} |"
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

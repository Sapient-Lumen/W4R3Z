#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.md'
UNCERTAINTY_CHECKPOINT_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'
CHECKPOINT_SCHEDULE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _sorted_union(*collections: list[int]) -> list[int]:
    return sorted({value for collection in collections for value in collection})


def _build_report() -> dict[str, Any]:
    staircase = _load(UNCERTAINTY_CHECKPOINT_STAIRCASE_REPORT)
    schedule = _load(CHECKPOINT_SCHEDULE_REPORT)

    tiers = {row['tier']: row for row in staircase['tier_rows']}
    near_exact = list(tiers['near_exact']['union_transition_checkpoints_unique_appends'])
    near_optimal = list(tiers['near_optimal']['union_transition_checkpoints_unique_appends'])
    lower = list(tiers['lower_guarantee']['union_transition_checkpoints_unique_appends'])
    structural = list(schedule['headline_findings']['mandatory_structural_checkpoints_unique_appends'])
    rewrite_budget = list(schedule['headline_findings']['rewrite_budget_transition_checkpoints_unique_appends'])

    near_exact_set = set(near_exact)
    near_optimal_set = set(near_optimal)
    lower_set = set(lower)
    structural_set = set(structural)
    rewrite_budget_set = set(rewrite_budget)

    all_exact_intersection = sorted(near_exact_set & near_optimal_set & lower_set)
    near_optimal_and_above_not_lower = sorted(near_optimal_set - lower_set)
    near_exact_only = sorted(near_exact_set - near_optimal_set)
    lower_unique = sorted(lower_set - near_exact_set)
    structural_only = sorted(structural_set - (near_exact_set | lower_set))
    structural_overlap_with_exact = sorted(structural_set & (near_exact_set | lower_set))

    exact_master = _sorted_union(near_exact, lower)
    full_master = _sorted_union(exact_master, structural)

    checkpoint_rows: list[dict[str, Any]] = []
    for checkpoint in full_master:
        tags: list[str] = []
        if checkpoint in all_exact_intersection:
            tags.append('all_exact_tiers')
        if checkpoint in near_optimal_and_above_not_lower:
            tags.append('near_optimal_and_near_exact_only')
        if checkpoint in near_exact_only:
            tags.append('near_exact_only')
        if checkpoint in lower_unique:
            tags.append('lower_guarantee_only')
        if checkpoint in structural_only:
            tags.append('structural_only')
        if checkpoint in structural_overlap_with_exact:
            tags.append('structural_overlap')
        if checkpoint in rewrite_budget_set:
            tags.append('rewrite_budgeted_mode')
        checkpoint_rows.append(
            {
                'unique_appends': checkpoint,
                'coverage_tags': tags,
            }
        )

    report = {
        'focus': 'Collapse the saved exact uncertainty tiers plus the mandatory structural checkpoints into one finite master audit calendar so inheritors can pre-register one sparse review schedule instead of juggling several overlapping lists.',
        'headline_findings': {
            'near_exact_subsumes_near_optimal_checkpoint_union_exactly': near_optimal_set <= near_exact_set,
            'lower_guarantee_adds_only_checkpoint_56_beyond_near_exact': lower_unique == [56],
            'exact_master_transition_checkpoints_unique_appends': exact_master,
            'exact_master_transition_checkpoint_count': len(exact_master),
            'full_master_audit_checkpoints_unique_appends': full_master,
            'full_master_audit_checkpoint_count': len(full_master),
            'structural_only_checkpoints_unique_appends': structural_only,
            'structural_overlap_with_exact_checkpoints_unique_appends': structural_overlap_with_exact,
            'rewrite_budgeted_mode_is_covered_by_full_master_calendar': rewrite_budget_set <= set(full_master),
            'main_rule': 'when the archive wants one pre-registered sparse audit calendar that covers every currently certified uncertainty tier plus the mandatory structural flips and bitmap cliffs, use the 17-point master set rather than polling per append.',
        },
        'decision_rules': [
            'If one calendar must cover all currently certified uncertainty-safe lanes, start from the near-exact 0.99 calendar because it already subsumes the full near-optimal 0.95 checkpoint union.',
            'Add checkpoint 56 if the archive may relax to the exact 0.85 lower-guarantee lane; that is the only extra transition checkpoint not already present in the near-exact union.',
            'Always keep structural checkpoints 79 and 191 even though they are not transition checkpoints for the current exact uncertainty tiers; they capture filter/route order flips that the maintenance loop should never skip.',
            'The same 17-point master calendar also covers the trusted-repeat 4-transition rewrite-budgeted mode, so one sparse schedule is enough for both exact uncertainty tiers and the practical budgeted fallback.',
        ],
        'group_rows': [
            {
                'group': 'all_exact_tiers',
                'checkpoint_count': len(all_exact_intersection),
                'checkpoints_unique_appends': all_exact_intersection,
                'note': 'core checkpoints shared by every currently certified uncertainty tier',
            },
            {
                'group': 'near_optimal_and_near_exact_only',
                'checkpoint_count': len(near_optimal_and_above_not_lower),
                'checkpoints_unique_appends': near_optimal_and_above_not_lower,
                'note': 'mid/tail checkpoints kept by the 0.95 and 0.99 tiers but dropped by the relaxed 0.85 tier',
            },
            {
                'group': 'near_exact_only',
                'checkpoint_count': len(near_exact_only),
                'checkpoints_unique_appends': near_exact_only,
                'note': 'extra micro/tail checkpoints paid only for the 0.99 near-exact tier',
            },
            {
                'group': 'lower_guarantee_only',
                'checkpoint_count': len(lower_unique),
                'checkpoints_unique_appends': lower_unique,
                'note': 'the single extra checkpoint needed to cover the exact 0.85 tier beyond the near-exact union',
            },
            {
                'group': 'structural_only',
                'checkpoint_count': len(structural_only),
                'checkpoints_unique_appends': structural_only,
                'note': 'non-transition structural checkpoints that still matter for maintenance because they mark filter/route order flips',
            },
        ],
        'checkpoint_rows': checkpoint_rows,
        'source_reports': [
            str(UNCERTAINTY_CHECKPOINT_STAIRCASE_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_SCHEDULE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Master Audit Calendar Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the near-exact `0.99` checkpoint union already subsumes the full near-optimal `0.95` union exactly: `near_exact_subsumes_near_optimal_checkpoint_union_exactly = {findings['near_exact_subsumes_near_optimal_checkpoint_union_exactly']}`.",
        f"- covering the exact relaxed `0.85` tier requires only one extra transition checkpoint beyond the near-exact union: `{report['group_rows'][3]['checkpoints_unique_appends']}`.",
        f"- the exact uncertainty tiers therefore collapse to a `15`-point master transition calendar: `{findings['exact_master_transition_checkpoints_unique_appends']}`.",
        f"- adding the non-transition structural checkpoints `{findings['structural_only_checkpoints_unique_appends']}` yields a `17`-point full master audit calendar that also covers the trusted-repeat rewrite-budgeted fallback: `rewrite_budgeted_mode_is_covered_by_full_master_calendar = {findings['rewrite_budgeted_mode_is_covered_by_full_master_calendar']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Grouped decomposition of the master calendar',
        '| group | count | checkpoints | note |',
        '|---|---:|---|---|',
    ]
    for row in report['group_rows']:
        lines.append(
            f"| {row['group']} | {row['checkpoint_count']} | {row['checkpoints_unique_appends']} | {row['note']} |"
        )
    lines.extend([
        '',
        '## Full master audit calendar',
        '| unique appends | coverage tags |',
        '|---:|---|',
    ])
    for row in report['checkpoint_rows']:
        lines.append(f"| {row['unique_appends']} | {', '.join(row['coverage_tags'])} |")
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
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.json'

EXPECTED_PRIORITY_CHECKPOINTS = [79, 111, 191, 239]
EXPECTED_DEFAULT_UNION = [24, 47, 63, 111, 143, 159, 230, 239]
EXPECTED_SIMPLICITY_UNION = [24, 47, 63, 111, 143, 159, 239]
EXPECTED_REWRITE_BUDGET_CHECKPOINTS = [56, 111, 159, 239]
EXPECTED_PAGE_BIRTH_SPACING = 16


def _load() -> dict[str, object]:
    return json.loads(REPORT.read_text())



def main() -> int:
    report = _load()
    findings = report['headline_findings']

    page_birth_checkpoints = report['routine_page_birth_checkpoints_unique_appends']
    page_birth_spacings = [
        page_birth_checkpoints[index + 1] - page_birth_checkpoints[index]
        for index in range(len(page_birth_checkpoints) - 1)
    ]
    if not page_birth_spacings or any(spacing != EXPECTED_PAGE_BIRTH_SPACING for spacing in page_birth_spacings):
        print(
            f'checkpoint-schedule: expected constant page-birth spacing {EXPECTED_PAGE_BIRTH_SPACING}, got {page_birth_spacings}',
            file=sys.stderr,
        )
        return 1

    priority_checkpoints = [row['unique_append_count'] for row in report['priority_checkpoint_rows']]
    if priority_checkpoints != EXPECTED_PRIORITY_CHECKPOINTS:
        print(
            f'checkpoint-schedule: expected priority checkpoints {EXPECTED_PRIORITY_CHECKPOINTS}, got {priority_checkpoints}',
            file=sys.stderr,
        )
        return 1

    default_union = findings['default_robust_union_transition_checkpoints_unique_appends']
    if default_union != EXPECTED_DEFAULT_UNION:
        print(
            f'checkpoint-schedule: expected default robust union {EXPECTED_DEFAULT_UNION}, got {default_union}',
            file=sys.stderr,
        )
        return 1

    simplicity_union = findings['simplicity_robust_union_transition_checkpoints_unique_appends']
    if simplicity_union != EXPECTED_SIMPLICITY_UNION:
        print(
            f'checkpoint-schedule: expected simplicity robust union {EXPECTED_SIMPLICITY_UNION}, got {simplicity_union}',
            file=sys.stderr,
        )
        return 1

    rewrite_budget_checkpoints = findings['rewrite_budget_transition_checkpoints_unique_appends']
    if rewrite_budget_checkpoints != EXPECTED_REWRITE_BUDGET_CHECKPOINTS:
        print(
            f'checkpoint-schedule: expected rewrite-budget checkpoints {EXPECTED_REWRITE_BUDGET_CHECKPOINTS}, got {rewrite_budget_checkpoints}',
            file=sys.stderr,
        )
        return 1

    if findings['first_route_block_bitmap_cliff_unique_appends'] != EXPECTED_PRIORITY_CHECKPOINTS[1]:
        print('checkpoint-schedule: first route-block bitmap cliff mismatch', file=sys.stderr)
        return 1
    if findings['second_route_block_bitmap_cliff_unique_appends'] != EXPECTED_PRIORITY_CHECKPOINTS[3]:
        print('checkpoint-schedule: second route-block bitmap cliff mismatch', file=sys.stderr)
        return 1

    if findings['default_robust_minimum_dwell_unique_appends'] > EXPECTED_PAGE_BIRTH_SPACING:
        print('checkpoint-schedule: default robust dwell should not exceed page-birth spacing', file=sys.stderr)
        return 1
    if findings['simplicity_robust_minimum_dwell_unique_appends'] != EXPECTED_PAGE_BIRTH_SPACING:
        print('checkpoint-schedule: simplicity robust dwell should align with page-birth spacing', file=sys.stderr)
        return 1

    if 111 not in default_union or 239 not in default_union:
        print('checkpoint-schedule: default union must include both bitmap cliffs', file=sys.stderr)
        return 1
    if 111 not in rewrite_budget_checkpoints or 239 not in rewrite_budget_checkpoints:
        print('checkpoint-schedule: rewrite-budget checkpoints must include both bitmap cliffs', file=sys.stderr)
        return 1

    if report['rewrite_budget_row']['selected_transition_count'] != 4:
        print('checkpoint-schedule: rewrite-budget row should use four transitions', file=sys.stderr)
        return 1

    print(
        'checkpoint-schedule: ok '
        f"(default_union={default_union}, priority_checkpoints={priority_checkpoints}, rewrite_budget={rewrite_budget_checkpoints})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

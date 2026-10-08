#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails import (
    build_weakening_overshoot_axis_guardrails_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening overshoot-axis guardrails snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Guardrail profiles')
    lines.append('| profile | precision hitchhike | suffix hitchhike | admitted coords | admitted hitchhikes | budgets | admitted families |')
    lines.append('|---|---|---|---:|---:|---|---|')
    for row in report['guardrail_profiles']:
        lines.append(
            f"| `{row['profile_label']}` | `{row['allow_precision_hitchhike']}` | `{row['allow_suffix_hitchhike']}` | `{row['admitted_coordinate_count']}` | `{row['admitted_hitchhike_coordinate_count']}` | `{row['admitted_budget_set']}` | `{row['admitted_hitchhike_axis_families']}` |"
        )
    lines.append('')
    lines.append('## Minimal profile partition')
    lines.append('| profile | member count | member demands |')
    lines.append('|---|---:|---|')
    for row in report['minimal_guardrail_profile_partition']:
        lines.append(
            f"| `{row['profile_label']}` | `{row['member_count']}` | `{row['member_demands']}` |"
        )
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| demand | precision hitchhike | suffix hitchhike | admissible | selected budget | overshoot |')
    lines.append('|---|---|---|---|---:|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['demand_coordinate']}` | `{row['allow_precision_hitchhike']}` | `{row['allow_suffix_hitchhike']}` | `{row['admissible_under_axis_guardrails']}` | `{row['selected_budget']}` | `{row['overshoot_coordinate']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_weakening_overshoot_axis_guardrails_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

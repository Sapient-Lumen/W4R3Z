#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy import (
    build_weakening_primitive_overshoot_taxonomy_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot_20260308.md'



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening primitive-overshoot taxonomy snapshot — 2026-03-08')
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
    lines.append('## Overshoot axis families')
    lines.append('| axis family | members | signatures | L1 histogram |')
    lines.append('|---|---:|---|---|')
    for row in report['primitive_overshoot_axis_families']:
        lines.append(
            f"| `{row['overshoot_axis_family']}` | `{row['member_count']}` | `{row['overshoot_signature_labels']}` | `{row['overshoot_l1_unit_histogram']}` |"
        )
    lines.append('')
    lines.append('## Overshoot signature classes')
    lines.append('| signature | axis family | L1 units | members | selected budgets | member demands |')
    lines.append('|---|---|---:|---:|---|---|')
    for row in report['primitive_overshoot_signature_classes']:
        lines.append(
            f"| `{row['overshoot_signature_label']}` | `{row['overshoot_axis_family']}` | `{row['overshoot_l1_units']}` | `{row['member_count']}` | `{row['selected_budget_set']}` | `{row['member_demands']}` |"
        )
    lines.append('')
    lines.append('## Unreachable primitive overshoot rows')
    lines.append('| demand | budget | selected coordinate | overshoot | axis family | shared axes |')
    lines.append('|---|---:|---|---|---|---|')
    for row in report['unreachable_primitive_overshoot_rows']:
        lines.append(
            f"| `{row['demand_coordinate']}` | `{row['selected_budget']}` | `{row['selected_coordinate']}` | `{row['overshoot_coordinate']}` | `{row['overshoot_axis_family']}` | `{row['shared_axes']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_primitive_overshoot_taxonomy_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

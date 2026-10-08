#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface import (
    build_weakening_primitive_demand_surface_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening primitive-demand surface snapshot — 2026-03-08')
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
    lines.append('## Budget coordinate path')
    lines.append('| budget | threshold | regime | coordinate |')
    lines.append('|---:|---:|---|---|')
    for row in report['budget_coordinate_path']:
        lines.append(
            f"| `{row['budget']}` | `{row['threshold_unique_appends']}` | `{row['selected_regime_label']}` | `{row['coordinate']}` |"
        )
    lines.append('')
    lines.append('## Primitive demand surface')
    lines.append('| demand | budget | threshold | selected coordinate | exact? | overshoot |')
    lines.append('|---|---:|---:|---|---|---|')
    for row in report['primitive_demand_surface']:
        lines.append(
            f"| `{row['demand_coordinate']}` | `{row['selected_budget']}` | `{row['selected_threshold_unique_appends']}` | `{row['selected_coordinate']}` | `{row['exact_coordinate_reachable']}` | `{row['overshoot_coordinate']}` |"
        )
    lines.append('')
    lines.append('## Unreachable demand classes')
    lines.append('| selected budget | threshold | selected coordinate | overshoot | member demands |')
    lines.append('|---:|---:|---|---|---|')
    for row in report['unreachable_demand_classes']:
        lines.append(
            f"| `{row['selected_budget']}` | `{row['selected_threshold_unique_appends']}` | `{row['selected_coordinate']}` | `{row['overshoot_coordinate']}` | `{row['member_demands']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_weakening_primitive_demand_surface_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

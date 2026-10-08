#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface import (
    build_weakening_budget_live_action_surface_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot_20260308.md'



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-budget live-action surface snapshot — 2026-03-08')
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
    lines.append('## Budget action surface')
    lines.append('| budget | threshold | regime | hold | stabilize | weaken | strengthen |')
    lines.append('|---:|---:|---|---:|---:|---:|---:|')
    for row in report['budget_action_surface']:
        counts = row['action_counts']
        lines.append(
            f"| `{row['budget']}` | `{row['selected_threshold_unique_appends']}` | `{row['selected_threshold_band_label']} / {row['selected_regime_label']}` | `{counts['hold']}` | `{counts['stabilize']}` | `{counts['weaken']}` | `{counts['strengthen']}` |"
        )
    lines.append('')
    lines.append('## Marginal live flips')
    lines.append('| budget step | state | floor | from | to | released route |')
    lines.append('|---:|---|---:|---|---|---|')
    for row in report['marginal_live_flips']:
        lines.append(
            f"| `{row['state_transition_budget_step']}` | `{row['current_state_label']}` | `{row['required_gain_share_floor']}` | `{row['from_action_family']} / {row['from_status']}` | `{row['to_action_family']} / {row['to_status']}` | `{row['to_route_unique_appends']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_budget_live_action_surface_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

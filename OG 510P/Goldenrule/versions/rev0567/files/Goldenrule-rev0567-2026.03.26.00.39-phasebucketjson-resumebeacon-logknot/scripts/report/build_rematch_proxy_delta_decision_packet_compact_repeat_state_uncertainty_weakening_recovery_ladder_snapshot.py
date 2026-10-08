#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder import (
    build_weakening_recovery_ladder_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder_snapshot_20260308.md'



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-recovery ladder snapshot — 2026-03-08')
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
    lines.append('## Serial recovery ladder')
    lines.append('| order | threshold | recovery kind | current state | floor | destination anchor | route |')
    lines.append('|---:|---:|---|---:|---:|---:|---|')
    for index, row in enumerate(report['recovery_ladder'], start=1):
        lines.append(
            f"| `{index}` | `{row['minimal_recovery_threshold_unique_appends']}` | `{row['recovery_kind']}` | `{row['current_state_unique_appends']}` | `{row['required_gain_share_floor']}` | `{row['selected_anchor_unique_appends']}` | `{row['route_unique_appends']}` |"
        )
    lines.append('')
    lines.append('## Threshold-band progression')
    lines.append('| band | threshold | recovered cases | still deferred | newly recovered case(s) |')
    lines.append('|---|---:|---:|---:|---|')
    for row in report['threshold_band_progression']:
        new_cases = [
            f"{case['current_state_unique_appends']}@{case['required_gain_share_floor']}"
            for case in row['newly_recovered_cases']
        ]
        lines.append(
            f"| `{row['threshold_band_label']}` | `{row['representative_threshold_unique_appends']}` | `{row['recovered_case_count']}` | `{row['remaining_deferred_case_count']}` | `{new_cases}` |"
        )
    lines.append('')
    lines.append('## Below-threshold vs at-threshold examples')
    for row in report['reference_examples']:
        lines.append(
            f"- **{row['recovery_kind']}** (`state {row['current_state_unique_appends']}`, `floor {row['required_gain_share_floor']}`): below `{row['decision_just_below_threshold']['threshold']}` -> `{row['decision_just_below_threshold']['action_family']}` / `{row['decision_just_below_threshold']['route_unique_appends']}`; at `{row['decision_at_threshold']['threshold']}` -> `{row['decision_at_threshold']['action_family']}` / `{row['decision_at_threshold']['route_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_recovery_ladder_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

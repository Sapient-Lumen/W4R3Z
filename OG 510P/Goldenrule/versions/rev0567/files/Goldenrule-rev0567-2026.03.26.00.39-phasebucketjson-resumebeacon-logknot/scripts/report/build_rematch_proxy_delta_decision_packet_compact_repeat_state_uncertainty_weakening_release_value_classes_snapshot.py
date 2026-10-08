#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes import (
    build_weakening_release_value_classes_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot_20260308.md'



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-release value classes snapshot — 2026-03-08')
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
    lines.append('## Marginal release steps')
    lines.append('| budget step | threshold | threshold increment | state | floor | route shift | value class | savings vector |')
    lines.append('|---:|---:|---:|---|---:|---:|---|---|')
    for row in report['marginal_release_steps']:
        lines.append(
            f"| `{row['budget_step']}` | `{row['threshold_unique_appends']}` | `{row['threshold_increment_unique_appends']}` | `{row['current_state_label']}` | `{row['required_gain_share_floor']}` | `{row['released_route_shift_unique_appends']}` | `{row['value_class_label']}` | `{row['savings_vector']}` |"
        )
    lines.append('')
    lines.append('## Release value classes')
    lines.append('| value class | budget steps | route shifts | thresholds | savings vector |')
    lines.append('|---|---:|---:|---:|---|')
    for row in report['release_value_classes']:
        lines.append(
            f"| `{row['value_class_label']}` | `{row['member_budget_steps']}` | `{row['member_route_shifts_unique_appends']}` | `{row['member_thresholds_unique_appends']}` | `{row['recovered_steady_state_savings_vector']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_release_value_classes_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

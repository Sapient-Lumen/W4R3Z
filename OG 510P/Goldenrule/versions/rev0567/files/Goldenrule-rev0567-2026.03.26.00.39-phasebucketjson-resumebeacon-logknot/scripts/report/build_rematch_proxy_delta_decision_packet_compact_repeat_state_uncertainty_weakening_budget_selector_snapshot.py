#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector import (
    build_weakening_budget_selector_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot_20260308.md'



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-budget selector snapshot — 2026-03-08')
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
    lines.append('## Budget selector catalog')
    lines.append('| budget | threshold | band / regime | recovered cases | next locked case |')
    lines.append('|---:|---:|---|---:|---|')
    for row in report['budget_catalog']:
        next_locked = 'none' if row['next_locked_case'] is None else row['next_locked_case']['recovered_case_label']
        lines.append(
            f"| `{row['selected_recovered_base_weakening_case_budget']}` | `{row['selected_threshold_unique_appends']}` | `{row['selected_threshold_band_label']} / {row['selected_regime_label']}` | `{row['selected_recovered_case_count']}` | `{next_locked}` |"
        )
    lines.append('')
    lines.append('## Marginal budget steps')
    lines.append('| recovered budget after step | threshold | recovered case |')
    lines.append('|---:|---:|---|')
    for row in report['marginal_budget_steps']:
        lines.append(
            f"| `{row['recovered_case_budget_after_step']}` | `{row['budget_step']}` | `{row['recovered_case_label']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_budget_selector_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

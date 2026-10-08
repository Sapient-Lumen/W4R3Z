#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law import (
    build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law_snapshot_20260309.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law_snapshot_20260309.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service mode-suffix batch shared half-step shared-interval-state equiprobable exact-shortest-script marginal-gain law snapshot — 2026-03-09')
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
    lines.append('## Marginal-gain family summary')
    for row in report['marginal_gain_family_summary']['families']:
        lines.append(f'- `{json.dumps(row, ensure_ascii=False, sort_keys=True)}`')
    lines.append('')
    lines.append('## Universal target schedule')
    for row in report['universal_target_schedule']:
        lines.append(f'- `{json.dumps(row, ensure_ascii=False, sort_keys=True)}`')
    lines.append('')
    lines.append('## State examples')
    for row in report['state_examples']:
        lines.append(f'- `{json.dumps(row, ensure_ascii=False, sort_keys=True)}`')
    lines.append('')
    lines.append('## Validation summary')
    lines.append(f"- `{json.dumps(report['validation_summary'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

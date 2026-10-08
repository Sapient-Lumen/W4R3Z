#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law import (
    build_service_horizon_staircase_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service horizon staircase law snapshot — 2026-03-08')
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
    lines.append('## Positive-service staircase states')
    lines.append('| state | interval `(lower, upper]` | probe target | exact horizon | suffix horizon |')
    lines.append('|---:|---|---:|---:|---:|')
    for state in report['positive_service_staircase_states']:
        lines.append(
            f"| `{state['signature']}` | `({state['lower_bound_exclusive']:.12f}, {state['upper_bound_inclusive']:.12f}]` | `{state['probe_target']:.12f}` | `{state['exact_only_support_horizon']}` | `{state['suffix_hitchhike_only_support_horizon']}` |"
        )
    lines.append('')
    lines.append('## Positive-service staircase transitions')
    lines.append('| crossing threshold | step kind | from | to | Δexact | Δsuffix |')
    lines.append('|---:|---|---|---|---:|---:|')
    for transition in report['positive_service_staircase_transitions']:
        lines.append(
            f"| `{transition['crossed_threshold_numerator']}/{transition['crossed_threshold_denominator']}` | `{transition['step_kind']}` | `{transition['from_signature']}` | `{transition['to_signature']}` | `{transition['exact_increment']}` | `{transition['suffix_increment']}` |"
        )
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| target service | staircase signature |')
    lines.append('|---:|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['minimum_service_share']:.12f}` | `{row['selected_signature']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_service_horizon_staircase_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

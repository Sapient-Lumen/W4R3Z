#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law import (
    build_service_local_triad_grammar_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service local triad grammar law snapshot — 2026-03-08')
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
    lines.append('## Positive-service local triad rows')
    lines.append('| state | probe | signature | triad | family | shared depth | current | next | second next |')
    lines.append('|---:|---:|---|---|---|---|---|---|---|')
    for row in report['positive_service_local_triad_rows']:
        shared_depth = row['shared_visibility_depth'] if row['shared_visibility_depth'] is not None else 'None'
        lines.append(
            f"| `{row['state_index']}` | `{row['probe_target']:.12f}` | `{row['current_signature']}` | `{row['corridor_triad_signature']}` | `{row['triad_family']}` | `{shared_depth}` | `{row['current_corridor_kind']}` | `{row['next_corridor_kind']}` | `{row['second_next_corridor_kind']}` |"
        )
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| target | signature | triad | family | shared depth | current | next | second next |')
    lines.append('|---:|---|---|---|---|---|---|---|')
    for row in report['selector_examples']:
        shared_depth = row['shared_visibility_depth'] if row['shared_visibility_depth'] is not None else 'None'
        lines.append(
            f"| `{row['minimum_service_share']:.12f}` | `{row['current_signature']}` | `{row['corridor_triad_signature']}` | `{row['triad_family']}` | `{shared_depth}` | `{row['current_corridor_kind']}` | `{row['next_corridor_kind']}` | `{row['second_next_corridor_kind']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_service_local_triad_grammar_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

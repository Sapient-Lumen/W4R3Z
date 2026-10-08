#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law import (
    build_service_local_upgrade_witness_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.md'


def _threshold_text(row: dict | None) -> str:
    if row is None:
        return '—'
    return f"{row['threshold_numerator']}/{row['threshold_denominator']} ({row['threshold_value']:.12f})"



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service local upgrade witness law snapshot — 2026-03-08')
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
    lines.append('## Positive-service local witness rows')
    lines.append('| state | probe | signature | next kind | next threshold | next signature |')
    lines.append('|---:|---:|---|---|---|---|')
    for row in report['positive_service_local_witness_rows']:
        lines.append(
            f"| `{row['state_index']}` | `{row['probe_target']:.12f}` | `{row['current_signature']}` | `{row['next_unlock_kind']}` | `{row['next_unlock_threshold_fraction'] or '—'}` | `{row['next_signature_after_relaxation'] or '—'}` |"
        )
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| target | signature | next exact | next suffix | next kind | next signature |')
    lines.append('|---:|---|---|---|---|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['minimum_service_share']:.12f}` | `{row['current_signature']}` | `{_threshold_text(row['next_exact_threshold'])}` | `{_threshold_text(row['next_suffix_threshold'])}` | `{row['next_unlock_kind']}` | `{row['next_signature_after_relaxation'] or '—'}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_service_local_upgrade_witness_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

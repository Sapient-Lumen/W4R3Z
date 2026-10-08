#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law import (
    build_service_threshold_provenance_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service threshold provenance law snapshot — 2026-03-08')
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
    lines.append('## Profile threshold ladders')
    for profile_label, rows in report['profile_threshold_ladders'].items():
        lines.append(f'### `{profile_label}`')
        lines.append('| width | threshold | value |')
        lines.append('|---:|---:|---:|')
        for row in rows:
            lines.append(
                f"| `{row['portfolio_size']}` | `{row['threshold_numerator']}/{row['threshold_denominator']}` | `{row['threshold_value']:.12f}` |"
            )
        lines.append('')
    lines.append('## Descending unique threshold provenance rows')
    lines.append('| idx | threshold | kind | sources |')
    lines.append('|---:|---:|---|---|')
    for row in report['threshold_provenance_rows']:
        source_text = ', '.join(
            f"{source['profile_label']}@{source['portfolio_size']}" for source in row['sources']
        )
        lines.append(
            f"| `{row['threshold_index_descending']}` | `{row['threshold_numerator']}/{row['threshold_denominator']}` | `{row['provenance_kind']}` | `{source_text}` |"
        )
    lines.append('')
    lines.append('## Signature reconstruction')
    lines.append(f"- reconstructed chain: `{report['reconstructed_positive_service_signatures']}`")
    lines.append(f"- staircase chain: `{report['positive_service_staircase_signatures']}`")
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| target service | signature |')
    lines.append('|---:|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['minimum_service_share']:.12f}` | `{row['threshold_basis_signature']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_service_threshold_provenance_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

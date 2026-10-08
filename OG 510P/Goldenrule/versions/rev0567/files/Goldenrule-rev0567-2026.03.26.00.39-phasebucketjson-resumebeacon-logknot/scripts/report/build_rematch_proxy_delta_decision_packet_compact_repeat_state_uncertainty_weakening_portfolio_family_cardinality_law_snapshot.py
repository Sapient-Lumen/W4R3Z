#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law import (
    build_weakening_portfolio_family_cardinality_law_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot_20260308.md'


def _ratio(cell: dict) -> str:
    return f"{cell['numerator']}/{cell['denominator']} ({cell['value']:.3f})"



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio family cardinality law snapshot — 2026-03-08')
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
    lines.append('## Width thresholds implied directly by admissible-family size')
    lines.append('| profile | family size | singleton service share | last width with positive service | first width with zero service |')
    lines.append('|---|---:|---|---:|---:|')
    for row in report['width_threshold_summary']:
        zero = '`None`' if row['first_width_with_zero_service'] is None else f"`{row['first_width_with_zero_service']}`"
        lines.append(
            f"| `{row['profile_label']}` | `{row['admissible_family_size']}` | `{_ratio(row['singleton_service_share'])}` | `{row['last_width_with_positive_service']}` | {zero} |"
        )
    lines.append('')
    lines.append('## Closed-form coverage shares by width')
    lines.append('| width | exact-only | precision-only | suffix-only | dual-axis |')
    lines.append('|---:|---|---|---|---|')
    for row in report['closed_form_service_rows']:
        shares = row['closed_form_coverage_shares']
        lines.append(
            f"| `{row['portfolio_size']}` | `{_ratio(shares['exact_only'])}` | `{_ratio(shares['precision_hitchhike_only'])}` | `{_ratio(shares['suffix_hitchhike_only'])}` | `{_ratio(shares['any_single_axis_hitchhike'])}` |"
        )
    lines.append('')
    lines.append('## Example choose-ratio instantiations')
    lines.append('| profile | width | family size | formula | share |')
    lines.append('|---|---:|---:|---|---|')
    for row in report['cardinality_law_examples']:
        lines.append(
            f"| `{row['profile_label']}` | `{row['width']}` | `{row['family_size']}` | `{row['formula']}` | `{_ratio(row['closed_form_share'])}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_portfolio_family_cardinality_law_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

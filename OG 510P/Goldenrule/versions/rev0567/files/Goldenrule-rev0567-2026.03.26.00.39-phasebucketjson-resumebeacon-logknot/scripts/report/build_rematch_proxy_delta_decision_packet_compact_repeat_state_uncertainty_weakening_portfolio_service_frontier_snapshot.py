#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier import (
    build_weakening_portfolio_service_frontier_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.md'


def _ratio(cell: dict) -> str:
    return f"{cell['numerator']}/{cell['denominator']} ({cell['value']:.3f})"



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service frontier snapshot — 2026-03-08')
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
    lines.append('## Profile maximum service levels')
    lines.append('| profile | maximum width-conditioned service share | attained at width |')
    lines.append('|---|---|---:|')
    for label, row in report['profile_max_service_levels'].items():
        lines.append(
            f"| `{label}` | `{_ratio(row['maximum_coverage_share'])}` | `{row['attained_at_portfolio_size']}` |"
        )
    lines.append('')
    lines.append('## Width-conditioned service frontier by target share')
    lines.append('| minimum service share | exact-only last sufficient width | suffix-only last sufficient width | dual-axis first minimally required width |')
    lines.append('|---:|---:|---:|---:|')
    for row in report['service_level_frontier_rows']:
        exact_last = '`None`' if row['exact_only_last_sufficient_width'] is None else f"`{row['exact_only_last_sufficient_width']}`"
        suffix_last = '`None`' if row['suffix_hitchhike_only_last_sufficient_width'] is None else f"`{row['suffix_hitchhike_only_last_sufficient_width']}`"
        lines.append(
            f"| `{row['minimum_service_share']:.2f}` | {exact_last} | {suffix_last} | `{row['dual_axis_first_minimally_required_width']}` |"
        )
    lines.append('')
    lines.append('## Width-conditioned profile coverage shares')
    lines.append('| width | exact-only coverage | precision-only coverage | suffix-only coverage | dual-axis coverage | precision dominated by suffix? |')
    lines.append('|---:|---|---|---|---|---|')
    for row in report['portfolio_service_rows']:
        shares = row['coverage_shares']
        lines.append(
            f"| `{row['portfolio_size']}` | `{_ratio(shares['exact_only'])}` | `{_ratio(shares['precision_hitchhike_only'])}` | `{_ratio(shares['suffix_hitchhike_only'])}` | `{_ratio(shares['any_single_axis_hitchhike'])}` | `{row['precision_profile_is_dominated_by_suffix_profile']}` |"
        )
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| width | minimum service share | selected profile | selected profile coverage |')
    lines.append('|---:|---:|---|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['portfolio_size']}` | `{row['minimum_service_share']:.2f}` | `{row['selected_profile_label']}` | `{_ratio(row['selected_profile_coverage_share'])}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_portfolio_service_frontier_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

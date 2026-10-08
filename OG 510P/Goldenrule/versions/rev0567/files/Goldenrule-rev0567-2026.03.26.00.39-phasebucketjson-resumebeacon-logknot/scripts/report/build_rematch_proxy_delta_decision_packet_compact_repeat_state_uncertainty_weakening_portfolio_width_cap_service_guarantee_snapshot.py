#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee import (
    build_weakening_portfolio_width_cap_service_guarantee_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.md'


def _ratio(cell: dict) -> str:
    return f"{cell['numerator']}/{cell['denominator']} ({cell['value']:.3f})"



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio width-cap service guarantee snapshot — 2026-03-08')
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
    lines.append('## Efficient-profile monotonicity sequences by width cap')
    lines.append('| profile | guarantee sequence |')
    lines.append('|---|---|')
    for label, values in report['profile_monotonicity_summary'].items():
        rendered = ', '.join(f'{value:.3f}' for value in values)
        lines.append(f'| `{label}` | `{rendered}` |')
    lines.append('')
    lines.append('## Width-cap robust service frontier by target share')
    lines.append('| minimum service share | exact-only last safe width cap | suffix-only last safe width cap | dual-axis first required width cap |')
    lines.append('|---:|---:|---:|---:|')
    for row in report['width_cap_service_frontier_rows']:
        exact_last = '`None`' if row['exact_only_last_safe_width_cap'] is None else f"`{row['exact_only_last_safe_width_cap']}`"
        suffix_last = '`None`' if row['suffix_hitchhike_only_last_safe_width_cap'] is None else f"`{row['suffix_hitchhike_only_last_safe_width_cap']}`"
        lines.append(
            f"| `{row['minimum_service_share']:.2f}` | {exact_last} | {suffix_last} | `{row['dual_axis_first_required_width_cap']}` |"
        )
    lines.append('')
    lines.append('## Width-cap guaranteed profile coverage shares')
    lines.append('| width cap | exact-only guarantee | precision-only guarantee | suffix-only guarantee | dual-axis guarantee |')
    lines.append('|---:|---|---|---|---|')
    for row in report['portfolio_width_cap_service_rows']:
        shares = row['guaranteed_coverage_shares']
        lines.append(
            f"| `{row['maximum_portfolio_size']}` | `{_ratio(shares['exact_only'])}` | `{_ratio(shares['precision_hitchhike_only'])}` | `{_ratio(shares['suffix_hitchhike_only'])}` | `{_ratio(shares['any_single_axis_hitchhike'])}` |"
        )
    lines.append('')
    lines.append('## Exact-width vs width-cap selector equivalence examples')
    lines.append('| endpoint width | minimum service share | exact-width profile | width-cap profile | selectors coincide? |')
    lines.append('|---:|---:|---|---|---|')
    for row in report['selector_equivalence_examples']:
        lines.append(
            f"| `{row['width']}` | `{row['minimum_service_share']:.2f}` | `{row['exact_width_selected_profile_label']}` | `{row['width_cap_selected_profile_label']}` | `{row['selectors_coincide']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_portfolio_width_cap_service_guarantee_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

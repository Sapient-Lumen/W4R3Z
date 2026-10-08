#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law import (
    build_weakening_portfolio_guardrail_law_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio guardrail law snapshot — 2026-03-08')
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
    lines.append('## Portfolio signature partition')
    lines.append('| signature | minimal profile | portfolio count | formula |')
    lines.append('|---|---|---:|---|')
    for row in report['portfolio_signature_partition']:
        lines.append(
            f"| `{row['signature_label']}` | `{row['minimal_profile_label']}` | `{row['portfolio_count']}` | `{row['count_formula']}` |"
        )
    lines.append('')
    lines.append('## Demand family catalog')
    lines.append('| family | count | member labels |')
    lines.append('|---|---:|---|')
    for label, row in report['demand_family_catalog'].items():
        lines.append(f"| `{label}` | `{row['member_count']}` | `{row['member_labels']}` |")
    lines.append('')
    lines.append('## Selector examples')
    lines.append('| portfolio labels | minimal profile | family counts | dual-axis necessary |')
    lines.append('|---|---|---|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['portfolio_coordinate_labels']}` | `{row['minimal_profile_label']}` | `{row['family_counts']}` | `{row['dual_axis_permission_is_minimally_necessary']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_weakening_portfolio_guardrail_law_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

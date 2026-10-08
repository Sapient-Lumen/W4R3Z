#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law import (
    build_weakening_portfolio_width_law_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.md'


def _ratio(cell: dict) -> str:
    return f"{cell['numerator']}/{cell['denominator']} ({cell['value']:.3f})"



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio width law snapshot — 2026-03-08')
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
    lines.append('## Width-conditioned minimal-profile counts')
    lines.append('| size | total | exact-only | precision-only | suffix-only | dual-axis | dual-axis share |')
    lines.append('|---:|---:|---:|---:|---:|---:|---|')
    for row in report['portfolio_width_profile_rows']:
        counts = row['minimal_profile_counts']
        lines.append(
            f"| `{row['portfolio_size']}` | `{row['total_portfolios']}` | `{counts['exact_only']}` | `{counts['precision_hitchhike_only']}` | `{counts['suffix_hitchhike_only']}` | `{counts['any_single_axis_hitchhike']}` | `{_ratio(row['minimal_profile_shares']['any_single_axis_hitchhike'])}` |"
        )
    lines.append('')
    lines.append('## Key width examples')
    lines.append('| size | exact-only possible | precision-only possible | suffix-only possible | dual-axis majority | dual-axis universal |')
    lines.append('|---:|---|---|---|---|---|')
    for row in report['portfolio_width_examples']:
        lines.append(
            f"| `{row['portfolio_size']}` | `{row['exact_only_still_possible']}` | `{row['precision_only_still_possible']}` | `{row['suffix_only_still_possible']}` | `{row['dual_axis_majority']}` | `{row['dual_axis_universal']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_portfolio_width_law_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

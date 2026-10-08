#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder import (
    build_weakening_portfolio_confidence_ladder_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder_snapshot_20260308.md'


def _ratio(cell: dict) -> str:
    return f"{cell['numerator']}/{cell['denominator']} ({cell['value']:.3f})"



def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio confidence ladder snapshot — 2026-03-08')
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
    lines.append('## Dual-axis confidence thresholds')
    lines.append('| dual-axis share at least | minimum width |')
    lines.append('|---:|---:|')
    for row in report['dual_axis_confidence_thresholds']:
        lines.append(f"| `{row['confidence_level']:.3f}` | `{row['minimum_portfolio_size']}` |")
    lines.append('')
    lines.append('## Suffix-tail confidence thresholds within the non-dual tail')
    lines.append('| suffix-only tail share at least | minimum width |')
    lines.append('|---:|---:|')
    for row in report['suffix_tail_confidence_thresholds']:
        lines.append(f"| `{row['suffix_tail_share_level']:.3f}` | `{row['minimum_portfolio_size']}` |")
    lines.append('')
    lines.append('## Width-conditioned confidence rows')
    lines.append('| width | dual-axis share | non-dual share | suffix share inside non-dual tail | precision share inside non-dual tail | exact share inside non-dual tail |')
    lines.append('|---:|---|---|---|---|---|')
    for row in report['portfolio_confidence_rows']:
        tail = row['tail_profile_shares']
        lines.append(
            f"| `{row['portfolio_size']}` | `{_ratio(row['dual_axis_share'])}` | `{_ratio(row['non_dual_share'])}` | `{_ratio(tail['suffix_hitchhike_only'])}` | `{_ratio(tail['precision_hitchhike_only'])}` | `{_ratio(tail['exact_only'])}` |"
        )
    lines.append('')
    lines.append('## Key width examples')
    lines.append('| width | dual-axis share | suffix dominates non-dual tail | suffix is strict majority of non-dual tail |')
    lines.append('|---:|---|---|---|')
    for row in report['portfolio_confidence_examples']:
        lines.append(
            f"| `{row['portfolio_size']}` | `{_ratio(row['dual_axis_share'])}` | `{row['suffix_dominates_non_dual_tail']}` | `{row['suffix_strict_majority_of_non_dual_tail']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_portfolio_confidence_ladder_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

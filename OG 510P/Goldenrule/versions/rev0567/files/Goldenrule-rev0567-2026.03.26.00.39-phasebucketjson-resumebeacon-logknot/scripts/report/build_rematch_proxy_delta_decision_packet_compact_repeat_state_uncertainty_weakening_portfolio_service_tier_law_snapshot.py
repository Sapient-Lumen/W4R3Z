#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law import (
    build_weakening_portfolio_service_tier_law_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot_20260308.md'


def _ratio(cell: dict) -> str:
    return f"{cell['numerator']}/{cell['denominator']} ({cell['value']:.3f})"


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service tier law snapshot — 2026-03-08')
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
    lines.append('## Service tier cutoffs')
    for key, value in report['service_tier_cutoff_summary'].items():
        lines.append(f'- **{key}**: `{value}`')
    lines.append('')
    lines.append('## Two-breakpoint tier table by width')
    lines.append('| width | exact-only ceiling | suffix-only ceiling | positive tier count | exact positive? | suffix positive? |')
    lines.append('|---:|---|---|---:|---|---|')
    for row in report['service_tier_rows']:
        lines.append(
            f"| `{row['portfolio_size']}` | `{_ratio(row['exact_only_ceiling'])}` | `{_ratio(row['suffix_hitchhike_only_ceiling'])}` | `{row['positive_service_tier_count']}` | `{row['exact_only_is_positive_option']}` | `{row['suffix_hitchhike_only_is_positive_option']}` |"
        )
    lines.append('')
    lines.append('## Minimal-profile regions by width')
    for row in report['service_tier_rows']:
        lines.append(f"### Width `{row['portfolio_size']}`")
        for region in row['minimal_profile_regions']:
            lower = region['lower_bound']
            upper = region['upper_bound']
            if isinstance(lower, dict):
                lower_text = _ratio(lower)
            else:
                lower_text = f"{lower:.3f}"
            upper_text = _ratio(upper)
            lines.append(
                f"- `{region['profile_label']}` via `{region['interval_kind']}` from `{lower_text}` to `{upper_text}`"
            )
        lines.append('')
    lines.append('## Selector examples')
    lines.append('| width | target service | selected profile |')
    lines.append('|---:|---:|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['portfolio_size']}` | `{row['minimum_service_share']:.12f}` | `{row['selected_profile_label']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_weakening_portfolio_service_tier_law_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

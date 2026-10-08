#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law import (
    build_service_horizon_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.md'


def _render_band_list(bands: list[dict]) -> str:
    parts = []
    for band in bands:
        parts.append(
            f"{band['profile_label']}[{band['start_width']}-{band['end_width']}]"
        )
    return ', '.join(parts)


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening portfolio service horizon law snapshot — 2026-03-08')
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
    lines.append('## Horizon cutoffs')
    for key, value in report['horizon_cutoff_summary'].items():
        lines.append(f'- **{key}**: `{value}`')
    lines.append('')
    lines.append('## Positive service threshold catalog')
    for entry in report['service_threshold_catalog']:
        lines.append(
            f"- `{entry['profile_label']}` has `{entry['positive_threshold_count']}` positive thresholds: `{entry['positive_service_thresholds_descending']}`"
        )
    lines.append('')
    lines.append('## Positive service horizon bands')
    lines.append('| interval `(lower, upper]` | probe target | exact horizon | suffix horizon |')
    lines.append('|---|---:|---:|---:|')
    for band in report['positive_service_horizon_bands']:
        lines.append(
            f"| `({band['lower_bound_exclusive']:.12f}, {band['upper_bound_inclusive']:.12f}]` | `{band['probe_target']:.12f}` | `{band['exact_only_support_horizon']}` | `{band['suffix_hitchhike_only_support_horizon']}` |"
        )
    lines.append('')
    lines.append('## Upgrade schedule examples')
    lines.append('| target service | exact horizon | suffix horizon | first dual width | width-band schedule |')
    lines.append('|---:|---:|---:|---:|---|')
    for row in report['selector_examples']:
        lines.append(
            f"| `{row['minimum_service_share']:.6f}` | `{row['exact_only_support_horizon']}` | `{row['suffix_hitchhike_only_support_horizon']}` | `{row['first_width_requiring_any_single_axis_hitchhike']}` | `{_render_band_list(row['minimal_profile_width_bands'])}` |"
        )
    lines.append('')
    lines.append('## Width-selector consistency checks')
    for row in report['selector_examples']:
        lines.append(f"### Target `{row['minimum_service_share']:.6f}`")
        lines.append('| width | exact-width selector | max-width guarantee selector |')
        lines.append('|---:|---|---|')
        for check in row['width_checks']:
            lines.append(
                f"| `{check['portfolio_size']}` | `{check['exact_width_profile_label']}` | `{check['max_width_guarantee_profile_label']}` |"
            )
        lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_service_horizon_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

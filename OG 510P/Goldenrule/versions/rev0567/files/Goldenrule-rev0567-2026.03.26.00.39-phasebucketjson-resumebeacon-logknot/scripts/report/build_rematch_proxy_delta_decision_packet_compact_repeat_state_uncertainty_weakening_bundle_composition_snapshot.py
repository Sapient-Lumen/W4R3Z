#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition import (
    build_weakening_bundle_composition_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-bundle composition snapshot — 2026-03-08')
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
    lines.append('## Primitive bundles')
    lines.append('| value class | budget step | state | floor | threshold | route shift | route | savings vector |')
    lines.append('|---|---:|---|---:|---:|---:|---|---|')
    for row in report['bundle_primitives']:
        lines.append(
            f"| `{row['value_class_label']}` | `{row['representative_budget_step']}` | `{row['representative_current_state_label']}` | `{row['representative_required_gain_share_floor']}` | `{row['representative_threshold_unique_appends']}` | `{row['representative_route_shift_unique_appends']}` | `{row['representative_route_unique_appends']}` | `{row['recovered_steady_state_savings_vector']}` |"
        )
    lines.append('')
    lines.append('## Bundle composition relations')
    lines.append('| composite class | components | thresholds | route shifts | canonical chain | vector sum matches |')
    lines.append('|---|---|---:|---:|---|---|')
    for row in report['bundle_composition_relations']:
        lines.append(
            f"| `{row['composite_value_class_label']}` | `{row['component_value_class_labels']}` | `{row['component_thresholds_unique_appends']}` | `{row['component_route_shifts_unique_appends']}` | `{row['component_canonical_anchor_chain']}` | `{row['vector_sum_matches_composite'] and row['threshold_sum_matches_composite'] and row['route_shift_sum_matches_composite']}` |"
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_weakening_bundle_composition_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

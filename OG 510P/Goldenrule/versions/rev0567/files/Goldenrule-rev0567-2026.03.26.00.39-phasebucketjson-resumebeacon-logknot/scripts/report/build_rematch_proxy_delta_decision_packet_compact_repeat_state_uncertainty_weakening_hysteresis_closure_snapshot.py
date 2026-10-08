#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure import (
    build_weakening_hysteresis_closure_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot_20260308.md'


def _render_sequence(closure: dict[str, Any]) -> str:
    parts = []
    for step in closure['sequence']:
        action = step['action_family']
        route = 'hold' if step['route_unique_appends'] is None else '→'.join(str(x) for x in step['route_unique_appends'])
        parts.append(f"{step['from_state_unique_appends']}[{action}:{route}]→{step['to_state_unique_appends']}")
    return '; '.join(parts)



def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-hysteresis closure snapshot — 2026-03-08')
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
    lines.append('## Persistent relaxed-floor release thresholds (`floor = 0.84`)')
    lines.append('| current state | label | tier | eventual threshold to `25` | direct threshold to `25` | cycles at eventual threshold | state suffix |')
    lines.append('|---:|---|---|---:|---:|---:|---|')
    for row in report['persistent_floor_relaxation_release_table']:
        route = 'never' if row['eventual_route_state_suffix_at_threshold'] is None else '→'.join(str(x) for x in row['eventual_route_state_suffix_at_threshold'])
        eventual = 'never' if row['minimum_threshold_for_eventual_relaxed_anchor'] is None else str(row['minimum_threshold_for_eventual_relaxed_anchor'])
        direct = 'never' if row['minimum_threshold_for_direct_relaxed_anchor'] is None else str(row['minimum_threshold_for_direct_relaxed_anchor'])
        cycles = '—' if row['cycles_to_relaxed_anchor_at_eventual_threshold'] is None else str(row['cycles_to_relaxed_anchor_at_eventual_threshold'])
        lines.append(
            f"| `{row['current_state_unique_appends']}` | `{row['current_state_label']}` | `{row['current_tier']}` | `{eventual}` | `{direct}` | `{cycles}` | `{route}` |"
        )
    lines.append('')
    lines.append('## Threshold-band closure summary')
    lines.append('| threshold band | representative threshold | final anchor counts | max cycles to settle |')
    lines.append('|---|---:|---|---:|')
    for row in report['threshold_closure_bands']:
        lines.append(
            f"| `{row['threshold_band_label']}` | `{row['representative_threshold_unique_appends']}` | `{json.dumps(row['final_anchor_counts'], ensure_ascii=False)}` | `{row['max_cycles_to_settle']}` |"
        )
    lines.append('')
    lines.append('## Why threshold `12` and `17` differ')
    for label, closure in [
        ('threshold `12` from entry boundary `8` under relaxed floor', report['reference_entry_boundary_threshold_twelve_closure']),
        ('threshold `17` from entry boundary `8` under relaxed floor', report['reference_entry_boundary_threshold_seventeen_closure']),
    ]:
        lines.append(f"- **{label}**: final anchor `{closure['final_state_unique_appends']}`, cycles `{closure['settled_after_cycles']}`, sequence `{_render_sequence(closure)}`")
    lines.append('')
    lines.append('## Checked examples')
    for example in report['examples']:
        closure = example['closure']
        lines.append(
            f"- `{example['example_label']}`: final `{closure['final_state_unique_appends']}`, cycles `{closure['settled_after_cycles']}`, actions `{[step['action_family'] for step in closure['sequence']]}`, sequence `{_render_sequence(closure)}`."
        )
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_hysteresis_closure_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector import (
    build_weakening_capability_selector_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-capability selector snapshot — 2026-03-08')
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
    lines.append('## Capability ladder')
    lines.append('| band | regime | threshold | relaxed release states from stronger tiers | direct stronger-tier relaxed releases | middle-band precision relief | max settle cycles |')
    lines.append('|---|---|---:|---|---|---|---:|')
    for profile in report['capability_profiles']:
        lines.append(
            f"| `{profile['threshold_band_label']}` | `{profile['regime_label']}` | `{profile['threshold_unique_appends']}` | `{profile['support_sets']['eventual_relaxed_anchor_states_from_stronger_tiers']}` | `{profile['support_sets']['direct_relaxed_anchor_states_from_stronger_tiers']}` | `{profile['capabilities']['admits_middle_band_precision_relief']}` | `{profile['closure_summary']['max_cycles_to_settle']}` |"
        )
    lines.append('')
    lines.append('## Objective catalog')
    lines.append('| objective | requested promises | minimal threshold | selected regime |')
    lines.append('|---|---|---:|---|')
    for row in report['objective_catalog']:
        selector = row['selector']
        lines.append(
            f"| `{row['objective_code']}` | `{json.dumps(selector['requirements'], ensure_ascii=False, sort_keys=True)}` | `{selector['selected_threshold_unique_appends']}` | `{selector['selected_threshold_band_label']} / {selector['selected_regime_label']}` |"
        )
    lines.append('')
    lines.append('## Infeasible promise bundles')
    for row in report['infeasible_objectives']:
        selector = row['selector']
        lines.append(f"- **{row['objective_code']}**: {row['objective_label']}")
        lines.append(f"  - requested promises: `{json.dumps(selector['requirements'], ensure_ascii=False, sort_keys=True)}`")
        lines.append(f"  - incompatibility notes: `{selector['incompatibility_notes']}`")
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_capability_selector_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

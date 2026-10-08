#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form import (
    build_weakening_regime_normal_form_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot_20260308.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-regime normal-form snapshot — 2026-03-08')
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
    lines.append('## Named regimes')
    lines.append('| band | regime | representative threshold | newly admitted one-shot weakenings | stronger-tier eventual relaxed releases | stronger-tier direct relaxed releases | middle-band neutral releases | final anchor counts | max settle cycles |')
    lines.append('|---|---|---:|---|---|---|---|---|---:|')
    for regime in report['regimes']:
        closure = regime['closure_summary']
        lines.append(
            f"| `{regime['threshold_band_label']}` | `{regime['regime_label']}` | `{regime['normalized_threshold_unique_appends']}` | `{regime['newly_admitted_one_shot_weakening_cases']}` | `{regime['eventual_relaxed_anchor_states_from_stronger_tiers']}` | `{regime['direct_relaxed_anchor_states_from_stronger_tiers']}` | `{regime['middle_band_neutral_release_states']}` | `{json.dumps(closure['final_anchor_counts'], ensure_ascii=False)}` | `{closure['max_cycles_to_settle']}` |"
        )
    lines.append('')
    lines.append('## Regime notes')
    for regime in report['regimes']:
        lines.append(f"- **{regime['threshold_band_label']} / {regime['regime_label']}**: {regime['operator_summary']}")
        lines.append(f"  - forced weakenings: `{regime['forced_one_shot_weakening_cases']}`")
        lines.append(f"  - stronger-tier eventual relaxed releases: `{regime['eventual_relaxed_anchor_states_from_stronger_tiers']}`")
        lines.append(f"  - stronger-tier direct relaxed releases: `{regime['direct_relaxed_anchor_states_from_stronger_tiers']}`")
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'



def main() -> None:
    report = build_weakening_regime_normal_form_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

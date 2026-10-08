#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_arrival_floor_law import (
    build_geometric_arrival_live_arrival_floor_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'geometric_arrival_live_arrival_floor_law_snapshot_20260316.json'
OUT_MD = REPORTS / 'geometric_arrival_live_arrival_floor_law_snapshot_20260316.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Geometric-arrival live arrival-floor law snapshot — 2026-03-16')
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
    for label in [
        'state_positive_example',
        'state_impossible_example',
        'universal_positive_example',
        'universal_impossible_example',
    ]:
        lines.append(f"## {label.replace('_', ' ').title()}")
        lines.append(f"- `{json.dumps(report[label], ensure_ascii=False, sort_keys=True)}`")
        lines.append('')
    lines.append('## Validation summary')
    lines.append(f"- `{json.dumps(report['validation_summary'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## Source reports')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_geometric_arrival_live_arrival_floor_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

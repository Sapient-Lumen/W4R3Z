#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_batch_cap_law import (
    build_geometric_arrival_live_batch_cap_snapshot,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'geometric_arrival_live_batch_cap_law_snapshot_20260316.json'
OUT_MD = REPORTS / 'geometric_arrival_live_batch_cap_law_snapshot_20260316.md'


def _render_md(report: dict) -> str:
    lines: list[str] = []
    lines.append('# Geometric-arrival live batch-cap law snapshot — 2026-03-16')
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
    lines.append('## State positive preserved example')
    lines.append(f"- `{json.dumps(report['state_positive_preserved_example'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## State positive rejected example')
    lines.append(f"- `{json.dumps(report['state_positive_rejected_example'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## State zero-margin example')
    lines.append(f"- `{json.dumps(report['state_zero_margin_example'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## Universal positive preserved example')
    lines.append(f"- `{json.dumps(report['universal_positive_preserved_example'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## Universal positive rejected example')
    lines.append(f"- `{json.dumps(report['universal_positive_rejected_example'], ensure_ascii=False, sort_keys=True)}`")
    lines.append('')
    lines.append('## Universal zero-margin example')
    lines.append(f"- `{json.dumps(report['universal_zero_margin_example'], ensure_ascii=False, sort_keys=True)}`")
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
    report = build_geometric_arrival_live_batch_cap_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

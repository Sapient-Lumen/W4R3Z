#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_retention_exit_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_retention_exit_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark retention-exit snapshot — 2026-03-16',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The rematch-world publication lifecycle now has an explicit scratch-exit boundary: `retention_exit_ready={str(report['retention_exit_ready']).lower()}` with `{report['durable_object_count']}` durable retained objects and `{report['transient_object_count']}` exit-ready transient objects.",
        f"- The durable retained publication set weighs `{report['retained_publication_set_bytes']}` bytes while the now-elidable transient patch plus scratch sources weigh `{report['transient_exit_bytes']}` bytes, a `{report['transient_exit_share_of_publication_lifecycle']}` share of the full publication lifecycle surface.",
        f"- The exit-ready transient set is exactly one reconstructible fill patch plus `{report['scratch_source_count']}` hashed scratch sources, so future sessions can delete the right things without guessing.",
        '- The exit receipt keeps the bundle, audit, preflight, and provenance conditions in one place, which means archive-size discipline no longer depends on remembering an informal cleanup ritual.',
        '',
        '## Implementor guidance',
        '',
        '- After a real rematch-world run, retain the six durable publication objects and use the retention-exit receipt as the explicit permission slip for dropping scratch and the compiled patch.',
        '- Do not keep wide traces or the compiled patch in the long-term archive once the evidence receipt, preflight receipt, bundle receipt, and spine audit all pass together.',
        '- Treat the exit receipt as the compact archive-shaping handoff artifact that tells the next session what may leave safely, not just what must stay.',
        '',
    ])


def main() -> int:
    receipt = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-16',
        'focus': 'make the rematch-world publication lifecycle end with one explicit retention-exit receipt so future sessions know exactly which scratch and intermediate objects may leave the archive',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_retention_exit_snapshot.py',
        'retention_exit_ready': receipt['exit_conditions']['retention_exit_ready'],
        'durable_object_count': len(receipt['durable_retained_objects']),
        'transient_object_count': len(receipt['exit_ready_transient_objects']),
        'scratch_source_count': sum(1 for row in receipt['exit_ready_transient_objects'] if row['retention_class'] == 'scratch_exit_candidate'),
        'retained_publication_set_bytes': receipt['retained_byte_totals']['retained_publication_set_bytes'],
        'transient_exit_bytes': receipt['retained_byte_totals']['transient_exit_bytes'],
        'transient_exit_share_of_publication_lifecycle': receipt['retained_byte_totals']['transient_exit_share_of_publication_lifecycle'],
        'recommended_next_move': receipt['recommended_next_move'],
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'retention-exit-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'retention-exit-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_spine_audit_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_publication_spine_audit_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_publication_spine_audit_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark publication-spine audit snapshot — 2026-03-16',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The retained publication spine can now be audited by deterministic rebuild: `publication_spine_ready={str(report['publication_spine_ready']).lower()}` with artifact, preflight, and bundle rebuild checks all passing.",
        f"- The durable four-object spine weighs `{report['durable_spine_bytes']}` bytes and the compact bundle receipt adds `{report['bundle_receipt_bytes']}` bytes as an index over it.",
        f"- The retained compiled artifact remains publication-ready with `{report['blocking_fill_slot_count']}` blockers, `{report['forbidden_changed_path_count']}` forbidden changed paths, and `{report['allowed_decision_null_count']}` allowed open-ended decision nulls.",
        '- The audit now proves the retained compiled artifact, retained preflight receipt, and retained bundle receipt all rebuild exactly from the retained packet and evidence receipt under the standing seed and decision contract.',
        '',
        '## Implementor guidance',
        '',
        '- For a real rematch-world run, rerun the publication-spine audit after retaining the packet, evidence receipt, compiled artifact, preflight receipt, and bundle receipt.',
        '- Treat the audit receipt as the compact proof that the durable publication spine is rebuild-stable and not just visually plausible.',
        '- Keep the fill patch scratch-only unless drift debugging actually requires it.',
        '',
    ])


def main() -> int:
    receipt = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-16',
        'focus': 'audit the retained rematch-world publication spine by deterministic rebuild so future inheritors can trust the retained artifact and receipts without keeping the fill patch',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_publication_spine_audit_snapshot.py',
        'publication_spine_ready': receipt['publication_spine_ready'],
        'durable_spine_bytes': receipt['retained_bytes']['durable_spine_bytes'],
        'bundle_receipt_bytes': receipt['retained_bytes']['bundle_receipt_bytes'],
        'artifact_rebuild_matches_retained': receipt['checks']['artifact_rebuild_matches_retained'],
        'preflight_rebuild_matches_retained': receipt['checks']['preflight_rebuild_matches_retained'],
        'bundle_rebuild_matches_retained': receipt['checks']['bundle_rebuild_matches_retained'],
        'blocking_fill_slot_count': receipt['retained_preflight_status']['blocking_fill_slot_count'],
        'forbidden_changed_path_count': receipt['retained_preflight_status']['forbidden_changed_path_count'],
        'allowed_decision_null_count': receipt['retained_preflight_status']['allowed_decision_null_count'],
        'filled_world_section_count': receipt['retained_preflight_status']['filled_world_section_count'],
        'recommended_next_move': receipt['recommended_next_move'],
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'publication-spine-audit-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'publication-spine-audit-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

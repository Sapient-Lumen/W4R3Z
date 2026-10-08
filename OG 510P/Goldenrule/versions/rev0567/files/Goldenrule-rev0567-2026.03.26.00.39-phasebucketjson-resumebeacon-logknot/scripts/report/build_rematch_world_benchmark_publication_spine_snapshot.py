#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
EVIDENCE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
ARTIFACT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
PREFLIGHT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
BUNDLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_publication_spine_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_publication_spine_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark publication spine snapshot — 2026-03-16',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The archive now retains the previously only-named durable publication spine concretely: packet `{report['packet_bytes']}` bytes, evidence receipt `{report['evidence_receipt_bytes']}` bytes, compiled artifact `{report['compiled_artifact_bytes']}` bytes, and preflight receipt `{report['preflight_receipt_bytes']}` bytes.",
        f"- Those four durable objects total `{report['durable_spine_bytes']}` bytes; the bundle receipt adds `{report['bundle_receipt_bytes']}` bytes as an optional handoff convenience layer rather than as a missing prerequisite.",
        f"- The retained compiled artifact stays preflight-ready with `{report['blocking_fill_slot_count']}` blockers, `{report['forbidden_changed_path_count']}` forbidden changed paths, and `{report['allowed_decision_null_count']}` allowed open-ended decision nulls.",
        f"- The bundle receipt now points at the retained artifact path `{report['artifact_output_path']}` instead of leaving the durable artifact implicit.",
        '',
        '## Implementor guidance',
        '',
        '- After a real rematch-world run, retain the concrete four-object publication spine, not just the bundle receipt that names it.',
        '- Treat the bundle receipt as a compact handoff index over those durable objects.',
        '- Keep the compiled fill patch scratch-only by default; verify the retained artifact against the retained preflight receipt instead of retaining the patch.',
        '',
    ])


def main() -> int:
    packet_bytes = len(PACKET.read_bytes())
    evidence_receipt_bytes = len(EVIDENCE_RECEIPT.read_bytes())
    artifact_bytes = len(ARTIFACT.read_bytes())
    preflight_bytes = len(PREFLIGHT.read_bytes())
    bundle = load_json(BUNDLE)
    preflight = load_json(PREFLIGHT)
    report = {
        'snapshot_date': '2026-03-16',
        'focus': 'retain the durable rematch-world publication spine concretely so future inheritors audit real retained objects instead of a merely named bundle',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_publication_spine_snapshot.py',
        'packet_bytes': packet_bytes,
        'evidence_receipt_bytes': evidence_receipt_bytes,
        'compiled_artifact_bytes': artifact_bytes,
        'preflight_receipt_bytes': preflight_bytes,
        'durable_spine_bytes': packet_bytes + evidence_receipt_bytes + artifact_bytes + preflight_bytes,
        'bundle_receipt_bytes': len(BUNDLE.read_bytes()),
        'artifact_output_path': bundle['compiled_candidate']['artifact_output_path'],
        'artifact_written': bundle['artifact_written'],
        'patch_elision_ready': bundle['patch_elision_ready'],
        'blocking_fill_slot_count': preflight['status_counts']['blocking_fill_slot_count'],
        'forbidden_changed_path_count': preflight['status_counts']['forbidden_changed_path_count'],
        'allowed_decision_null_count': preflight['status_counts']['allowed_decision_null_count'],
        'recommended_next_move': 'For a real run, keep the concrete four-object publication spine together and cite the bundle receipt as the compact handoff index over it.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'publication-spine-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'publication-spine-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

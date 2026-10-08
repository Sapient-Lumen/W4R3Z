#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_publication_bundle_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_publication_bundle_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch-world benchmark publication-bundle snapshot — 2026-03-16',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The publication bundle can now prove that the compiled fill patch is an expendable intermediate: `patch_elision_ready={str(report['patch_elision_ready']).lower()}` and `patch_retention_required={str(report['patch_retention_required']).lower()}`.",
        f"- The example packet remains `{report['packet_bytes']}` bytes, the compiled transient patch is `{report['transient_patch_bytes']}` bytes, and the compiled benchmark artifact would be `{report['compiled_candidate_bytes']}` bytes if written.",
        f"- That means each future real run can drop one `{report['transient_patch_bytes']}`-byte retained sidecar once the packet, evidence receipt, compiled benchmark artifact, and preflight receipt exist.",
        f"- The example bundle stays preflight-ready with `{report['blocking_fill_slot_count']}` blockers, `{report['forbidden_changed_path_count']}` forbidden changed paths, and `{report['allowed_decision_null_count']}` allowed open-ended decision nulls.",
        '',
        '## Implementor guidance',
        '',
        '- After a real rematch-world run, keep the packet and evidence receipt as the retained distillation spine.',
        '- Compile the packet into the benchmark artifact, emit a preflight receipt, and cite this publication-bundle receipt in the handoff log.',
        '- Let the compiled fill patch stay scratch-only unless a debugging or diff-review need makes it worth keeping temporarily.',
        '',
    ])


def main() -> int:
    receipt = load_json(EXAMPLE)
    packet_path = ROOT / receipt['packet_path']
    report = {
        'snapshot_date': '2026-03-16',
        'focus': 'treat the compiled fill patch as a scratch-only intermediate once packet provenance and benchmark preflight are bundled into one receipt',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_publication_bundle_snapshot.py',
        'packet_bytes': len(packet_path.read_bytes()),
        'patch_elision_ready': receipt['patch_elision_ready'],
        'patch_retention_required': receipt['patch_retention_required'],
        'transient_patch_bytes': receipt['transient_patch']['byte_count'],
        'compiled_candidate_bytes': receipt['compiled_candidate']['byte_count'],
        'blocking_fill_slot_count': receipt['preflight']['blocking_fill_slot_count'],
        'forbidden_changed_path_count': receipt['preflight']['forbidden_changed_path_count'],
        'allowed_decision_null_count': receipt['preflight']['allowed_decision_null_count'],
        'evidence_receipt_matches_packet': receipt['evidence_receipt_matches_packet'],
        'evidence_receipt_strict_coverage_passed': receipt['evidence_receipt_strict_coverage_passed'],
        'recommended_retained_objects': receipt['recommended_retained_objects'],
        'recommended_next_move': receipt['recommended_next_move'],
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'publication-bundle-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'publication-bundle-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

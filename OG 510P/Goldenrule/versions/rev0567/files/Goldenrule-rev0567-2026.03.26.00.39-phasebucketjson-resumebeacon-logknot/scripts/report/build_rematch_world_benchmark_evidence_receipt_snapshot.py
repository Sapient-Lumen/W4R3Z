#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_evidence_receipt_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_evidence_receipt_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def build_snapshot() -> dict[str, Any]:
    packet = load_json(PACKET)
    receipt = load_json(RECEIPT)
    packet_bytes = len(PACKET.read_bytes())
    receipt_bytes = len(RECEIPT.read_bytes())
    seed_bytes = len(SEED.read_bytes())
    combined = packet_bytes + receipt_bytes
    saved = seed_bytes - combined
    return {
        'snapshot_date': '2026-03-16',
        'focus': 'retain one compact evidence packet plus one compact receipt so bulky rematch-world traces can leave the archive without leaving the packet unauditable',
        'packet_path': PACKET.relative_to(ROOT).as_posix(),
        'receipt_path': RECEIPT.relative_to(ROOT).as_posix(),
        'seed_path': SEED.relative_to(ROOT).as_posix(),
        'packet_bytes': packet_bytes,
        'receipt_bytes': receipt_bytes,
        'packet_plus_receipt_bytes': combined,
        'seed_bytes': seed_bytes,
        'bytes_saved_vs_seed': saved,
        'saved_share_vs_seed': saved / seed_bytes if seed_bytes else 0.0,
        'scratch_source_count': receipt['scratch_source_count'],
        'scratch_total_bytes': receipt['scratch_total_bytes'],
        'covered_section_count': len(receipt['coverage_sections']),
        'strict_coverage_passed': receipt['strict_coverage_passed'],
        'source_run_label': packet['source_run_label'],
        'recommended_next_move': 'For a real benchmark run, retain the distilled evidence packet and one hashed receipt like this, then allow wider traces to remain scratch-only once the standard patch and preflight receipt have been produced.'
    }


def render_md(snapshot: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch World Benchmark Evidence Receipt Snapshot — 2026-03-16',
        '',
        f"Focus: {snapshot['focus']}",
        '',
        '## Main local result',
        '',
        f"- The retained evidence packet example weighs `{snapshot['packet_bytes']}` bytes and the hashed receipt weighs `{snapshot['receipt_bytes']}` bytes.",
        f"- Together they weigh `{snapshot['packet_plus_receipt_bytes']}` bytes versus `{snapshot['seed_bytes']}` bytes for the full retained seed, saving `{snapshot['bytes_saved_vs_seed']}` bytes (`{snapshot['saved_share_vs_seed']:.6f}` share) while preserving packet-to-scratch provenance.",
        f"- The receipt covers `{snapshot['covered_section_count']}` benchmark sections across `{snapshot['scratch_source_count']}` scratch sources totaling `{snapshot['scratch_total_bytes']}` bytes, with strict coverage passing=`{str(snapshot['strict_coverage_passed']).lower()}`.",
        '',
        '## Recommended next move',
        '',
        f"- {snapshot['recommended_next_move']}",
        ''
    ])


def main() -> int:
    snapshot = build_snapshot()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(snapshot), encoding='utf-8')
    print(f'rematch-world-benchmark-evidence-receipt-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-evidence-receipt-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
SEED_PATH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_evidence_flow_snapshot_20260316.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_evidence_flow_snapshot_20260316.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_snapshot() -> dict[str, Any]:
    packet_builder = _load_module(
        'build_rematch_world_benchmark_evidence_packet_example',
        ROOT / 'scripts' / 'report' / 'build_rematch_world_benchmark_evidence_packet_example.py',
    )
    packet_compiler = _load_module(
        'compile_rematch_world_benchmark_fill_patch_from_evidence_packet',
        ROOT / 'scripts' / 'tools' / 'compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py',
    )
    applier = _load_module(
        'apply_rematch_world_benchmark_fill_patch',
        ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py',
    )
    preflight = _load_module(
        'rematch_world_benchmark_publication_preflight',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py',
    )

    packet = packet_builder.build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    patch = packet_compiler.build_fill_patch(packet)
    seed = load_json(SEED_PATH)
    decision = load_json(DECISION_PATH)
    candidate = applier.build_candidate_from_patch(patch, seed)
    receipt = preflight.build_preflight_summary(
        candidate=candidate,
        seed=seed,
        decision_contract=decision,
        inspection_mode='compiled_from_evidence_packet',
        inspection_target_path=PACKET_PATH.relative_to(ROOT).as_posix(),
        seed_path=SEED_PATH.relative_to(ROOT).as_posix(),
        decision_contract_path=DECISION_PATH.relative_to(ROOT).as_posix(),
    )

    packet_bytes = len(PACKET_PATH.read_bytes())
    patch_bytes = len(json.dumps(patch, indent=2, sort_keys=True).encode('utf-8')) + 1
    seed_bytes = len(SEED_PATH.read_bytes())
    packet_savings = seed_bytes - packet_bytes
    packet_to_patch_delta = patch_bytes - packet_bytes

    return {
        'snapshot_date': '2026-03-16',
        'focus': 'retain one tiny evidence packet from a real rematch-world run, compile it into the standard fill patch, and let raw run output stay scratch-only',
        'evidence_packet_path': PACKET_PATH.relative_to(ROOT).as_posix(),
        'seed_path': SEED_PATH.relative_to(ROOT).as_posix(),
        'decision_contract_path': DECISION_PATH.relative_to(ROOT).as_posix(),
        'evidence_packet_bytes': packet_bytes,
        'compiled_fill_patch_bytes': patch_bytes,
        'seed_bytes': seed_bytes,
        'bytes_saved_vs_seed': packet_savings,
        'saved_share_vs_seed': packet_savings / seed_bytes if seed_bytes else 0.0,
        'packet_to_patch_byte_delta': packet_to_patch_delta,
        'row_counts': {
            'occupancy_policy_rows': len(packet['occupancy_policy_rows']),
            'turnover_policy_rows': len(packet['turnover_policy_rows']),
            'leaderboard_rows': len(packet['leaderboard_rows']),
        },
        'compiled_preflight': {
            'preflight_ready': receipt['preflight_ready'],
            'forbidden_changed_path_count': receipt['status_counts']['forbidden_changed_path_count'],
            'blocking_fill_slot_count': receipt['status_counts']['blocking_fill_slot_count'],
            'allowed_decision_null_count': receipt['status_counts']['allowed_decision_null_count'],
            'decision_bundle_digest_matches_contract': receipt['decision_bundle_digest_matches_contract'],
        },
        'recommended_next_move': 'When a real rematch-world run exists, retain one evidence packet like this, compile it into the standard fill patch, compile back onto the seed, and cite the resulting preflight receipt instead of retaining bulky raw benchmark sidecars.'
    }


def render_md(snapshot: dict[str, Any]) -> str:
    return '\n'.join([
        '# Rematch World Benchmark Evidence Flow Snapshot — 2026-03-16',
        '',
        f"Focus: {snapshot['focus']}",
        '',
        '## Main local result',
        '',
        f"- The retained evidence packet example weighs `{snapshot['evidence_packet_bytes']}` bytes, versus `{snapshot['seed_bytes']}` bytes for the standing seed that embeds the frozen decision bundle.",
        f"- That saves `{snapshot['bytes_saved_vs_seed']}` bytes (`{snapshot['saved_share_vs_seed']:.6f}` share) during evidence distillation while still compiling forward into the standard fill patch and one-artifact benchmark shape.",
        f"- Compiling the packet into the standard fill patch adds only `{snapshot['packet_to_patch_byte_delta']}` bytes because the packet already holds the exact world-dependent facts the patch needs.",
        '',
        '## Compiled packet check',
        '',
        f"- The example packet compiles into a patch with `{snapshot['row_counts']['occupancy_policy_rows']}` occupancy rows, `{snapshot['row_counts']['turnover_policy_rows']}` turnover rows, and `{snapshot['row_counts']['leaderboard_rows']}` leaderboard rows.",
        f"- Compiling that patch back onto the seed is preflight-ready=`{str(snapshot['compiled_preflight']['preflight_ready']).lower()}` with `{snapshot['compiled_preflight']['forbidden_changed_path_count']}` forbidden changed paths, `{snapshot['compiled_preflight']['blocking_fill_slot_count']}` fill blockers, and `{snapshot['compiled_preflight']['allowed_decision_null_count']}` allowed open-ended decision nulls.",
        f"- The copied decision bundle digest still matches the standing contract: `{str(snapshot['compiled_preflight']['decision_bundle_digest_matches_contract']).lower()}`.",
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
    print(f'rematch-world-benchmark-evidence-flow-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-evidence-flow-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DEFAULT_PATCH = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_fill_patch.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
DEFAULT_ARTIFACT = DEFAULT_SEED
WORLD_SECTIONS = [
    'world_semantics_contract',
    'matching_state_contract',
    'occupancy_accounting_contract',
    'turnover_tempo_contract',
    'paired_ranking_views_contract',
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _extract_subtree(node: Any, dotted_path: str) -> Any:
    current = node
    for part in dotted_path.split('.'):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f'missing dotted path {dotted_path}')
        current = current[part]
    return copy.deepcopy(current)


def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def build_preflight_summary(
    candidate: dict[str, Any],
    seed: dict[str, Any],
    decision_contract: dict[str, Any],
    inspection_mode: str,
    inspection_target_path: str,
    seed_path: str,
    decision_contract_path: str,
) -> dict[str, Any]:
    mutation_guard = _load_module(
        'rematch_world_benchmark_mutation_guard',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py',
    )
    completion_gate = _load_module(
        'rematch_world_benchmark_completion_gate',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_completion_gate.py',
    )

    mutation = mutation_guard.inspect_candidate_mutations(candidate, seed, decision_contract)
    completion = completion_gate.summarize_completion_status(candidate, decision_contract)

    frozen_surface = {
        row['prefix']: _extract_subtree(candidate, row['prefix'])
        for row in mutation_guard.FROZEN_PREFIX_ROWS
    }
    section_status = candidate.get('section_status', {})
    filled_world_sections = sorted(section for section in WORLD_SECTIONS if section_status.get(section) == 'filled')
    pending_world_sections = sorted(section for section in WORLD_SECTIONS if section_status.get(section) != 'filled')

    decision_bundle_digest = _sha256_json(candidate.get('compact_decision_bundle'))
    decision_contract_digest = _sha256_json(decision_contract)
    preflight_ready = bool(mutation['mutation_surface_ok'] and completion['completion_ready'])

    if preflight_ready:
        recommended_next_move = (
            'Publish the filled benchmark artifact together with this preflight receipt; no further sidecar benchmark notes are needed.'
        )
    elif mutation['status_counts']['forbidden_changed_path_count'] > 0:
        recommended_next_move = (
            'Rebuild the candidate from the standing seed or compact fill patch and clear frozen-surface mutations before publication.'
        )
    else:
        recommended_next_move = (
            'Keep filling the compact patch or compiled benchmark in place until the 24 world-dependent blockers clear, then rerun this one-command preflight gate.'
        )

    return {
        'snapshot_date': '2026-03-16',
        'focus': 'collapse compile-back, mutation-surface, and completion checks into one preflight receipt before publishing the first endogenous rematch benchmark',
        'inspection_mode': inspection_mode,
        'inspection_target_path': inspection_target_path,
        'seed_path': seed_path,
        'decision_contract_path': decision_contract_path,
        'artifact_state': candidate.get('artifact_state'),
        'preflight_ready': preflight_ready,
        'strict_mode_would_pass': preflight_ready,
        'mutation_surface_ok': bool(mutation['mutation_surface_ok']),
        'completion_ready': bool(completion['completion_ready']),
        'decision_bundle_digest_matches_contract': decision_bundle_digest == decision_contract_digest,
        'status_counts': {
            'allowed_changed_path_count': mutation['status_counts']['allowed_changed_path_count'],
            'forbidden_changed_path_count': mutation['status_counts']['forbidden_changed_path_count'],
            'unchanged_required_mutation_prefix_count': mutation['status_counts']['unchanged_required_mutation_prefix_count'],
            'blocking_fill_slot_count': completion['status_counts']['blocking_slot_count'],
            'template_blocker_count': completion['status_counts']['template_blocker_count'],
            'null_blocker_count': completion['status_counts']['null_blocker_count'],
            'allowed_decision_null_count': completion['status_counts']['allowed_decision_null_count'],
            'pending_world_section_status_count': completion['status_counts']['world_section_status_pending_count'],
            'filled_world_section_count': len(filled_world_sections),
        },
        'filled_world_sections': filled_world_sections,
        'pending_world_sections': pending_world_sections,
        'forbidden_changed_path_rows': mutation['forbidden_changed_path_rows'],
        'blocking_slot_rows': completion['blocking_slot_rows'],
        'artifact_fingerprints': {
            'artifact_sha256': _sha256_json(candidate),
            'compact_decision_bundle_sha256': decision_bundle_digest,
            'standing_decision_contract_sha256': decision_contract_digest,
            'frozen_surface_sha256': _sha256_json(frozen_surface),
        },
        'recommended_next_move': recommended_next_move,
        'analysis_script': 'scripts/tools/rematch_world_benchmark_publication_preflight.py',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Run one consolidated preflight gate for a rematch-world benchmark candidate before publication.')
    parser.add_argument('artifact', nargs='?', default=str(DEFAULT_ARTIFACT), help='Path to a compiled benchmark artifact to inspect.')
    parser.add_argument('--patch', help='Path to a compact fill patch to compile and inspect instead of reading a compiled artifact.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing benchmark seed JSON.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--json', action='store_true', help='Emit the full preflight receipt as JSON.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the inspected artifact is publication-ready.')
    args = parser.parse_args()

    seed_path = Path(args.seed)
    decision_path = Path(args.decision_contract)
    seed = load_json(seed_path)
    decision_contract = load_json(decision_path)

    if args.patch:
        patch_path = Path(args.patch)
        patch = load_json(patch_path)
        applier = _load_module(
            'apply_rematch_world_benchmark_fill_patch',
            ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py',
        )
        candidate = applier.build_candidate_from_patch(patch, seed)
        inspection_mode = 'patch_compile'
        inspection_target_path = _relativize(patch_path)
    else:
        artifact_path = Path(args.artifact)
        candidate = load_json(artifact_path)
        inspection_mode = 'artifact'
        inspection_target_path = _relativize(artifact_path)

    summary = build_preflight_summary(
        candidate=candidate,
        seed=seed,
        decision_contract=decision_contract,
        inspection_mode=inspection_mode,
        inspection_target_path=inspection_target_path,
        seed_path=_relativize(seed_path),
        decision_contract_path=_relativize(decision_path),
    )

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        state = 'ready' if summary['preflight_ready'] else 'not-ready'
        print(
            'rematch-world-benchmark-publication-preflight: '
            f"{state} ({summary['status_counts']['forbidden_changed_path_count']} forbidden paths, "
            f"{summary['status_counts']['blocking_fill_slot_count']} fill blockers, "
            f"{summary['status_counts']['allowed_decision_null_count']} allowed decision nulls, "
            f"artifact_sha256={summary['artifact_fingerprints']['artifact_sha256'][:12]})"
        )

    if args.strict and not summary['preflight_ready']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FROZEN_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_frozen_handoff_audit_receipt.json'
DEFAULT_COPY_FORWARD_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_copy_forward_audit_receipt.json'
DEFAULT_PUBLICATION_SPINE_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_spine_audit_receipt.json'
DEFAULT_POST_PRUNE_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_post_prune_audit_receipt.json'

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))

def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()

def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)

def _section_question_ids(copy_forward_audit: dict[str, Any]) -> list[str]:
    seen: set[str] = set(); ordered: list[str] = []
    for row in copy_forward_audit['audited_sections']:
        for qid in row['linked_question_ids']:
            if qid not in seen:
                seen.add(qid); ordered.append(qid)
    return ordered

def _ready_frozen_audit(receipt: dict[str, Any]) -> bool:
    c = receipt['status_counts']
    return bool(receipt['rebuilt_seed_matches_standing_seed'] and c['mismatch_count'] == 0 and c['audited_section_count'] == c['exact_match_count'])

def _ready_copy_forward(receipt: dict[str, Any], frozen_audit_path: Path, frozen_audit_sha: str) -> bool:
    c = receipt['status_counts']
    return bool(c['mismatch_count'] == 0 and c['audited_section_count'] == c['exact_match_count'] and receipt['seed_frozen_handoff_audit_path'] == _relativize(frozen_audit_path) and receipt['seed_frozen_handoff_audit_sha256'] == frozen_audit_sha)

def _ready_publication_spine(receipt: dict[str, Any], compiled_artifact_sha: str) -> bool:
    return bool(receipt['publication_spine_ready'] and receipt['checks']['retained_preflight_ready'] and receipt['checks']['retained_artifact_matches_bundle'] and receipt['retained_hashes']['compiled_artifact_sha256'] == compiled_artifact_sha)

def _ready_post_prune(receipt: dict[str, Any], publication_spine_sha: str, compiled_artifact_sha: str) -> bool:
    durable_by_label = {row['label']: row for row in receipt['durable_rows']}
    required = {'compiled_benchmark_artifact': compiled_artifact_sha, 'publication_spine_audit_receipt': publication_spine_sha}
    required_ok = all(label in durable_by_label and durable_by_label[label]['hash_matches'] and durable_by_label[label]['sha256'] == sha for label, sha in required.items())
    return bool(receipt['cleaned_tree_ready_for_zip'] and required_ok)

def build_receipt(frozen_audit: dict[str, Any], frozen_audit_path: Path, copy_forward_audit: dict[str, Any], copy_forward_audit_path: Path, publication_spine_audit: dict[str, Any], publication_spine_audit_path: Path, post_prune_audit: dict[str, Any], post_prune_audit_path: Path) -> dict[str, Any]:
    frozen_sha = _sha256_json(frozen_audit)
    copy_sha = _sha256_json(copy_forward_audit)
    spine_sha = _sha256_json(publication_spine_audit)
    prune_sha = _sha256_json(post_prune_audit)
    compiled_artifact_sha = copy_forward_audit['artifact_sha256']
    question_ids = _section_question_ids(copy_forward_audit)
    chain_links = [
        {'stage': 'frozen_seed_rebuild_audit', 'path': _relativize(frozen_audit_path), 'sha256': frozen_sha, 'ready': _ready_frozen_audit(frozen_audit), 'summary': 'Standing seed rebuild-matches and all copied frozen sections hash-match their standalone sources.'},
        {'stage': 'compiled_artifact_copy_forward_audit', 'path': _relativize(copy_forward_audit_path), 'sha256': copy_sha, 'ready': _ready_copy_forward(copy_forward_audit, frozen_audit_path, frozen_sha), 'summary': 'Compiled benchmark artifact preserved all copied frozen sections and the compact decision bundle unchanged.'},
        {'stage': 'durable_publication_spine_audit', 'path': _relativize(publication_spine_audit_path), 'sha256': spine_sha, 'ready': _ready_publication_spine(publication_spine_audit, compiled_artifact_sha), 'summary': 'Retained packet, evidence receipt, compiled artifact, preflight receipt, and bundle receipt rebuild-audit cleanly without keeping the fill patch.'},
        {'stage': 'post_prune_zip_readiness_audit', 'path': _relativize(post_prune_audit_path), 'sha256': prune_sha, 'ready': _ready_post_prune(post_prune_audit, spine_sha, compiled_artifact_sha), 'summary': 'Durable publication spine still hash-matches after cleanup and exit-ready transients are absent or unlinked.'},
    ]
    ready_link_count = sum(1 for row in chain_links if row['ready'])
    overall_chain_ready = ready_link_count == len(chain_links)
    next_move = 'Cite this chain receipt as the one inheritor-facing proof that the rematch-world benchmark publication path held from frozen source handoffs through cleaned-tree zip readiness, then cut the next revision zip.' if overall_chain_ready else 'Do not cut the next revision zip yet; restore the first broken chain link and rebuild this receipt so the inheritor can trust one compact end-to-end audit.'
    return {
        'receipt_kind': 'rematch_world_benchmark_publication_chain_receipt',
        'receipt_version': '2026-03-17.rematch_world_benchmark_publication_chain_receipt.v1',
        'analysis_script': 'scripts/tools/build_rematch_world_benchmark_publication_chain_receipt.py',
        'chain_links': chain_links,
        'compiled_artifact_path': copy_forward_audit['artifact_path'],
        'compiled_artifact_sha256': compiled_artifact_sha,
        'coverage': {'copied_frozen_section_count': int(copy_forward_audit['status_counts']['audited_section_count']), 'durable_publication_object_count': int(post_prune_audit['counts']['durable_count']), 'question_id_count': len(question_ids), 'question_id_range_summary': 'SQ-003 through SQ-026', 'question_ids': question_ids},
        'status_counts': {'ready_link_count': ready_link_count, 'total_link_count': len(chain_links), 'transient_cleared_count': int(post_prune_audit['counts']['transient_absent_or_unlinked_count']), 'overall_chain_ready': overall_chain_ready},
        'archive_posture': {'prefer_citation_over_recopy': True, 'intended_retention_class': 'durable_end_to_end_chain_receipt', 'size_discipline_note': 'Carry one tiny chain receipt that hashes the four checkpoint receipts instead of reopening or recopying the larger benchmark artifact family every session.'},
        'recommended_next_move': next_move,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact rematch-world benchmark publication chain receipt from the standing frozen-seed, copy-forward, publication-spine, and post-prune audits.')
    parser.add_argument('--frozen-audit', default=str(DEFAULT_FROZEN_AUDIT))
    parser.add_argument('--copy-forward-audit', default=str(DEFAULT_COPY_FORWARD_AUDIT))
    parser.add_argument('--publication-spine-audit', default=str(DEFAULT_PUBLICATION_SPINE_AUDIT))
    parser.add_argument('--post-prune-audit', default=str(DEFAULT_POST_PRUNE_AUDIT))
    parser.add_argument('--output')
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    receipt = build_receipt(load_json(Path(args.frozen_audit)), Path(args.frozen_audit), load_json(Path(args.copy_forward_audit)), Path(args.copy_forward_audit), load_json(Path(args.publication_spine_audit)), Path(args.publication_spine_audit), load_json(Path(args.post_prune_audit)), Path(args.post_prune_audit))
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    return 0 if (not args.strict or receipt['status_counts']['overall_chain_ready']) else 1

if __name__ == '__main__':
    raise SystemExit(main())

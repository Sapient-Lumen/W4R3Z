#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHAIN_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_chain_receipt.json'
DEFAULT_POST_PRUNE_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_post_prune_audit_receipt.json'
DEFAULT_SCRATCH_MANIFEST = ROOT / 'artifacts' / 'process' / 'scratch_manifest.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
SKIP_PARTS = {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
SKIP_SUFFIXES = {'.pyc', '.pyo'}
FIXED_POINT_EXCLUDED_PATHS = {
    'examples/snapshots/archive_report_hotspot_receipt.json',
    'examples/snapshots/archive_report_semantic_handle_receipt.json',
    'examples/snapshots/archive_report_compaction_candidate_receipt.json',
    'examples/snapshots/archive_report_compaction_gap_receipt.json',
    'examples/snapshots/archive_report_compaction_manifest_receipt.json',
    'examples/snapshots/archive_report_compaction_rehearsal_receipt.json',
    'examples/snapshots/archive_report_compaction_stage_receipt.json',
    'examples/snapshots/archive_report_compaction_execution_receipt.json',
    'artifacts/reports/artifact_summary.json',
    'artifacts/reports/artifact_bucket_inventory.json',
    'artifacts/reports/archive_size_profile_snapshot_20260316.json',
    'artifacts/reports/archive_size_profile_snapshot_20260316.md',
    'docs/ARTIFACT_BUCKETS.md',
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _iter_files(root: Path, excluded_output: Path) -> list[Path]:
    files: list[Path] = []
    excluded = excluded_output.resolve()
    fixed_point_excluded = {(ROOT / rel).resolve() for rel in FIXED_POINT_EXCLUDED_PATHS}
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if path.suffix in SKIP_SUFFIXES or path.name == '.gitkeep':
            continue
        if path.resolve() == excluded or path.resolve() in fixed_point_excluded:
            continue
        files.append(path)
    return sorted(files)


def _zip_size(files: list[Path]) -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_zip = Path(tmpdir) / 'rematch_world_benchmark_package_receipt_tmp.zip'
        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in files:
                zf.write(path, arcname=path.relative_to(ROOT).as_posix())
        return tmp_zip.stat().st_size


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def _report_bucket(files: list[Path]) -> dict[str, Any]:
    report_root = ROOT / 'artifacts' / 'reports'
    report_files = [path for path in files if path.is_relative_to(report_root)]
    pair_map: defaultdict[str, dict[str, int]] = defaultdict(dict)
    for path in report_files:
        if path.suffix in {'.json', '.md'}:
            pair_map[str(path.with_suffix(''))][path.suffix] = path.stat().st_size
    paired_count = 0
    paired_raw_bytes = 0
    for entry in pair_map.values():
        if '.json' in entry and '.md' in entry:
            paired_count += 1
            paired_raw_bytes += entry['.json'] + entry['.md']
    raw_bytes = sum(path.stat().st_size for path in report_files)
    total_raw_bytes = sum(path.stat().st_size for path in files)
    return {
        'path': 'artifacts/reports',
        'file_count': len(report_files),
        'raw_bytes': raw_bytes,
        'raw_mebibytes': _mib(raw_bytes),
        'share_of_raw_tree': round(raw_bytes / total_raw_bytes, 6) if total_raw_bytes else 0.0,
        'json_md_pair_count': paired_count,
        'paired_raw_bytes': paired_raw_bytes,
        'pair_share_of_report_bucket_raw_bytes': round(paired_raw_bytes / raw_bytes, 6) if raw_bytes else 0.0,
    }


def _retention_hygiene(files: list[Path], scratch_manifest: dict[str, Any], scratch_manifest_path: Path) -> dict[str, Any]:
    scratch_root = ROOT / 'examples' / 'scratch'
    examples_scratch_file_count = sum(1 for path in scratch_root.rglob('*') if path.is_file()) if scratch_root.exists() else 0
    pdf_file_count = sum(1 for path in files if path.suffix.lower() == '.pdf')
    pycache_dir_count = sum(1 for path in ROOT.rglob('__pycache__') if path.is_dir())
    return {
        'scratch_manifest_path': _relativize(scratch_manifest_path),
        'scratch_manifest_active_count': len(scratch_manifest.get('active_scratch', [])),
        'examples_scratch_file_count': examples_scratch_file_count,
        'pdf_file_count': pdf_file_count,
        'pycache_dir_count': pycache_dir_count,
    }


def _post_prune_compiled_artifact_sha(post_prune_audit: dict[str, Any]) -> str | None:
    for row in post_prune_audit.get('durable_rows', []):
        if row.get('label') == 'compiled_benchmark_artifact':
            return row.get('sha256')
    return None


def build_receipt(
    chain_receipt: dict[str, Any],
    chain_receipt_path: Path,
    post_prune_audit: dict[str, Any],
    post_prune_audit_path: Path,
    scratch_manifest: dict[str, Any],
    scratch_manifest_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    files = _iter_files(ROOT, output_path)
    raw_bytes = sum(path.stat().st_size for path in files)
    zip_bytes = _zip_size(files)
    report_growth_surface = _report_bucket(files)
    retention_hygiene = _retention_hygiene(files, scratch_manifest, scratch_manifest_path)

    compiled_artifact_sha = str(chain_receipt['compiled_artifact_sha256'])
    post_prune_compiled_sha = _post_prune_compiled_artifact_sha(post_prune_audit)
    policy_checks = {
        'publication_chain_ready': bool(chain_receipt['status_counts']['overall_chain_ready']),
        'post_prune_zip_ready': bool(post_prune_audit['cleaned_tree_ready_for_zip']),
        'compiled_artifact_digest_consistent': post_prune_compiled_sha == compiled_artifact_sha,
        'pdf_free_tree': retention_hygiene['pdf_file_count'] == 0,
        'scratch_tree_empty': retention_hygiene['examples_scratch_file_count'] == 0,
        'scratch_manifest_clear': retention_hygiene['scratch_manifest_active_count'] == 0,
        'pycache_free_tree': retention_hygiene['pycache_dir_count'] == 0,
    }
    passed_check_count = sum(1 for value in policy_checks.values() if value)
    package_ready = passed_check_count == len(policy_checks)
    if package_ready:
        next_move = (
            'Cite this package receipt as the package-boundary proof that the cleaned rematch-world tree stayed '
            'chain-consistent, PDF-free, scratch-free, and size-profiled, then cut the next revision zip.'
        )
    else:
        next_move = (
            'Do not cut the next revision zip yet; restore the first failed package-boundary check, rebuild this '
            'receipt, and only package the tree once chain, cleanup, and retention hygiene all pass together.'
        )

    return {
        'receipt_kind': 'rematch_world_benchmark_package_receipt',
        'receipt_version': '2026-03-17.rematch_world_benchmark_package_receipt.v1',
        'analysis_script': 'scripts/tools/build_rematch_world_benchmark_package_receipt.py',
        'measurement_scope': {
            'tree_root': '.',
            'output_receipt_self_excluded': True,
            'excluded_output_path': _relativize(output_path),
            'skip_parts': sorted(SKIP_PARTS),
            'skip_suffixes': sorted(SKIP_SUFFIXES),
            'fixed_point_excluded_paths': sorted(FIXED_POINT_EXCLUDED_PATHS),
        },
        'chain_receipt_path': _relativize(chain_receipt_path),
        'chain_receipt_sha256': _sha256_json(chain_receipt),
        'post_prune_audit_path': _relativize(post_prune_audit_path),
        'post_prune_audit_sha256': _sha256_json(post_prune_audit),
        'compiled_artifact_sha256': compiled_artifact_sha,
        'archive_totals': {
            'retained_file_count_excluding_receipt': len(files),
            'raw_bytes_excluding_receipt': raw_bytes,
            'raw_mebibytes_excluding_receipt': _mib(raw_bytes),
            'approx_revision_zip_bytes_excluding_receipt': zip_bytes,
            'approx_revision_zip_mebibytes_excluding_receipt': _mib(zip_bytes),
            'zip_share_of_raw_excluding_receipt': round(zip_bytes / raw_bytes, 6) if raw_bytes else 0.0,
        },
        'report_growth_surface': report_growth_surface,
        'retention_hygiene': retention_hygiene,
        'policy_checks': policy_checks,
        'status_counts': {
            'passed_check_count': passed_check_count,
            'total_check_count': len(policy_checks),
            'package_ready': package_ready,
        },
        'archive_posture': {
            'prefer_citation_over_recopy': True,
            'intended_retention_class': 'durable_package_boundary_receipt',
            'size_discipline_note': 'Carry one tiny package receipt that cites the publication chain, proves the cleaned tree stayed PDF-free and scratch-free, and records the current size profile without retaining another broad report pair.',
        },
        'recommended_next_move': next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact rematch-world package receipt that checks package-boundary hygiene and size posture before the next revision zip is cut.')
    parser.add_argument('--chain-receipt', default=str(DEFAULT_CHAIN_RECEIPT))
    parser.add_argument('--post-prune-audit', default=str(DEFAULT_POST_PRUNE_AUDIT))
    parser.add_argument('--scratch-manifest', default=str(DEFAULT_SCRATCH_MANIFEST))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    output_path = Path(args.output)
    receipt = build_receipt(
        chain_receipt=load_json(Path(args.chain_receipt)),
        chain_receipt_path=Path(args.chain_receipt),
        post_prune_audit=load_json(Path(args.post_prune_audit)),
        post_prune_audit_path=Path(args.post_prune_audit),
        scratch_manifest=load_json(Path(args.scratch_manifest)),
        scratch_manifest_path=Path(args.scratch_manifest),
        output_path=output_path,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    if args.strict and not receipt['status_counts']['package_ready']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

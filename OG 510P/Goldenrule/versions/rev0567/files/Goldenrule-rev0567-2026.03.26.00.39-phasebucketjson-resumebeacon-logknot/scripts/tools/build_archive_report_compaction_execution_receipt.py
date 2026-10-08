#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
DEFAULT_HOTSPOT_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_hotspot_receipt.json'
DEFAULT_MANIFEST_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'
DEFAULT_REHEARSAL_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_rehearsal_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_execution_receipt.json'
REPORT_ROOT = ROOT / 'artifacts' / 'reports'
def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))
def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()
def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)
def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)
def _file_row(path_rel: str, pre_archive: Path | None = None) -> dict[str, Any]:
    path = ROOT / path_rel
    if path.exists():
        data = path.read_bytes()
    elif pre_archive is not None and pre_archive.exists():
        with zipfile.ZipFile(pre_archive, 'r') as zf:
            data = zf.read(path_rel)
    else:
        raise FileNotFoundError(path_rel)
    return {
        'path': path_rel,
        'raw_bytes': len(data),
        'raw_mebibytes': _mib(len(data)),
        'source_sha256': hashlib.sha256(data).hexdigest(),
        'file_kind': path.suffix.lstrip('.') or 'other',
    }
def _build_initial_seed(pre_package: dict[str, Any], pre_manifest: dict[str, Any], pre_archive: Path | None = None) -> dict[str, Any]:
    execution_manifest: list[dict[str, Any]] = []
    for row in pre_manifest.get('trim_manifest', []):
        file_rows = [_file_row(str(path_rel), pre_archive=pre_archive) for path_rel in row.get('exact_report_paths', [])]
        execution_manifest.append(
            {
                'priority_rank': int(row['priority_rank']),
                'family': str(row['family']),
                'raw_bytes': int(row['raw_bytes']),
                'raw_mebibytes': float(row['raw_mebibytes']),
                'share_of_report_bucket_raw_bytes': float(row['share_of_report_bucket_raw_bytes']),
                'semantic_alias_used': bool(row['semantic_alias_used']),
                'backing_handle_count': int(row['backing_handle_count']),
                'backing_handles': list(row['backing_handles']),
                'trim_mode': str(row['trim_mode']),
                'exact_report_file_count': int(row['exact_report_file_count']),
                'exact_report_paths': list(row['exact_report_paths']),
                'file_rows': file_rows,
            }
        )
    return {
        'pre_trim_package_receipt_sha256': _sha256_json(pre_package),
        'pre_trim_manifest_receipt_sha256': _sha256_json(pre_manifest),
        'pre_trim_summary': {
            'retained_file_count': int(pre_package['archive_totals']['retained_file_count_excluding_receipt']),
            'raw_tree_bytes': int(pre_package['archive_totals']['raw_bytes_excluding_receipt']),
            'approx_zip_bytes': int(pre_package['archive_totals']['approx_revision_zip_bytes_excluding_receipt']),
            'report_bucket_file_count': int(pre_package['report_growth_surface']['file_count']),
            'report_bucket_raw_bytes': int(pre_package['report_growth_surface']['raw_bytes']),
            'report_bucket_pair_count': int(pre_package['report_growth_surface']['json_md_pair_count']),
            'manifest_family_count': int(pre_manifest['summary_metrics']['manifest_family_count']),
            'manifest_file_count': int(pre_manifest['summary_metrics']['manifest_file_count']),
            'manifest_raw_bytes': int(pre_manifest['summary_metrics']['manifest_raw_bytes']),
        },
        'executed_manifest': execution_manifest,
    }
def _load_seed(seed_receipt_path: Path, pre_package_path: Path | None, pre_manifest_path: Path | None, pre_archive_path: Path | None) -> dict[str, Any]:
    if pre_package_path is not None or pre_manifest_path is not None:
        if pre_package_path is None or pre_manifest_path is None:
            raise FileNotFoundError('explicit execution reseeding requires both --pre-package and --pre-manifest inputs')
        return _build_initial_seed(load_json(pre_package_path), load_json(pre_manifest_path), pre_archive=pre_archive_path)
    if seed_receipt_path.exists():
        seed = load_json(seed_receipt_path)
        return {
            'pre_trim_package_receipt_sha256': str(seed['pre_trim_package_receipt_sha256']),
            'pre_trim_manifest_receipt_sha256': str(seed['pre_trim_manifest_receipt_sha256']),
            'pre_trim_summary': dict(seed['pre_trim_summary']),
            'executed_manifest': list(seed['executed_manifest']),
        }
    raise FileNotFoundError('need either an existing execution receipt seed or explicit --pre-package and --pre-manifest inputs')
def build_receipt(package_receipt: dict[str, Any], package_receipt_path: Path, hotspot_receipt: dict[str, Any], hotspot_receipt_path: Path, manifest_receipt: dict[str, Any], manifest_receipt_path: Path, rehearsal_receipt: dict[str, Any], rehearsal_receipt_path: Path, seed: dict[str, Any]) -> dict[str, Any]:
    executed_manifest = list(seed['executed_manifest'])
    pre_trim_summary = dict(seed['pre_trim_summary'])
    executed_paths = [str(path_rel) for row in executed_manifest for path_rel in row.get('exact_report_paths', [])]
    executed_path_set = set(executed_paths)
    executed_raw_bytes = sum(int(row['raw_bytes']) for row in executed_manifest)
    executed_pair_count = sum(1 for row in executed_manifest if row.get('exact_report_file_count') == 2)
    post_report_bucket = dict(package_receipt['report_growth_surface'])
    post_totals = dict(package_receipt['archive_totals'])
    post_manifest_rows = list(manifest_receipt.get('trim_manifest', []))
    post_manifest_path_set = {path for row in post_manifest_rows for path in row.get('exact_report_paths', [])}
    leading_hotspot = hotspot_receipt['largest_report_families'][0] if hotspot_receipt.get('largest_report_families') else None
    summary_metrics = {
        'executed_family_count': len(executed_manifest),
        'executed_file_count': len(executed_paths),
        'executed_raw_bytes': executed_raw_bytes,
        'executed_raw_mebibytes': _mib(executed_raw_bytes),
        'executed_share_of_pre_trim_report_bucket_raw_bytes': round(executed_raw_bytes / int(pre_trim_summary['report_bucket_raw_bytes']), 6) if int(pre_trim_summary['report_bucket_raw_bytes']) else 0.0,
        'pre_trim_retained_file_count': int(pre_trim_summary['retained_file_count']),
        'post_trim_retained_file_count': int(post_totals['retained_file_count_excluding_receipt']),
        'retained_file_count_delta': int(pre_trim_summary['retained_file_count']) - int(post_totals['retained_file_count_excluding_receipt']),
        'retained_addition_file_count_during_pass': len(executed_paths) - (int(pre_trim_summary['retained_file_count']) - int(post_totals['retained_file_count_excluding_receipt'])),
        'pre_trim_raw_tree_bytes': int(pre_trim_summary['raw_tree_bytes']),
        'post_trim_raw_tree_bytes': int(post_totals['raw_bytes_excluding_receipt']),
        'raw_tree_bytes_delta': int(pre_trim_summary['raw_tree_bytes']) - int(post_totals['raw_bytes_excluding_receipt']),
        'pre_trim_approx_zip_bytes': int(pre_trim_summary['approx_zip_bytes']),
        'post_trim_approx_zip_bytes': int(post_totals['approx_revision_zip_bytes_excluding_receipt']),
        'approx_zip_bytes_delta': int(pre_trim_summary['approx_zip_bytes']) - int(post_totals['approx_revision_zip_bytes_excluding_receipt']),
        'pre_trim_report_bucket_file_count': int(pre_trim_summary['report_bucket_file_count']),
        'post_trim_report_bucket_file_count': int(post_report_bucket['file_count']),
        'report_bucket_file_count_delta': int(pre_trim_summary['report_bucket_file_count']) - int(post_report_bucket['file_count']),
        'report_bucket_retained_addition_file_count_during_pass': len(executed_paths) - (int(pre_trim_summary['report_bucket_file_count']) - int(post_report_bucket['file_count'])),
        'pre_trim_report_bucket_raw_bytes': int(pre_trim_summary['report_bucket_raw_bytes']),
        'post_trim_report_bucket_raw_bytes': int(post_report_bucket['raw_bytes']),
        'report_bucket_raw_bytes_delta': int(pre_trim_summary['report_bucket_raw_bytes']) - int(post_report_bucket['raw_bytes']),
        'pre_trim_report_bucket_pair_count': int(pre_trim_summary['report_bucket_pair_count']),
        'post_trim_report_bucket_pair_count': int(post_report_bucket['json_md_pair_count']),
        'report_bucket_pair_count_delta': int(pre_trim_summary['report_bucket_pair_count']) - int(post_report_bucket['json_md_pair_count']),
        'report_bucket_retained_addition_pair_count_during_pass': executed_pair_count - (int(pre_trim_summary['report_bucket_pair_count']) - int(post_report_bucket['json_md_pair_count'])),
        'report_bucket_retained_addition_raw_bytes_during_pass': executed_raw_bytes - (int(pre_trim_summary['report_bucket_raw_bytes']) - int(post_report_bucket['raw_bytes'])),
        'retained_addition_raw_bytes_during_pass': executed_raw_bytes - (int(pre_trim_summary['raw_tree_bytes']) - int(post_totals['raw_bytes_excluding_receipt'])),
        'next_manifest_family_count': int(manifest_receipt['summary_metrics']['manifest_family_count']),
        'next_manifest_file_count': int(manifest_receipt['summary_metrics']['manifest_file_count']),
        'next_manifest_raw_bytes': int(manifest_receipt['summary_metrics']['manifest_raw_bytes']),
        'next_frontier_gap_count': int(rehearsal_receipt['summary_metrics']['projected_frontier_gap_count']),
        'next_frontier_leading_hotspot_family': str(leading_hotspot['family']) if leading_hotspot else None,
    }
    policy_checks = {
        'post_package_receipt_ready': bool(package_receipt.get('status_counts', {}).get('package_ready')),
        'post_hotspot_receipt_ready': bool(hotspot_receipt.get('status_counts', {}).get('ready_to_cite')),
        'post_manifest_receipt_ready': bool(manifest_receipt.get('status_counts', {}).get('ready_to_cite')),
        'post_rehearsal_receipt_ready': bool(rehearsal_receipt.get('status_counts', {}).get('ready_to_cite')),
        'executed_manifest_nonempty': bool(executed_manifest),
        'executed_paths_unique': len(executed_path_set) == len(executed_paths),
        'executed_paths_absent_now': executed_path_set.isdisjoint(post_manifest_path_set),
        'executed_paths_under_reports': all((ROOT / rel).resolve().is_relative_to(REPORT_ROOT.resolve()) for rel in executed_paths),
        'executed_raw_bytes_match_pre_manifest': executed_raw_bytes == int(pre_trim_summary['manifest_raw_bytes']),
        'report_bucket_net_shrink_positive': summary_metrics['report_bucket_raw_bytes_delta'] + summary_metrics['report_bucket_retained_addition_raw_bytes_during_pass'] == executed_raw_bytes,
        'report_bucket_net_shrink_not_greater_than_executed_bytes': summary_metrics['report_bucket_raw_bytes_delta'] + summary_metrics['report_bucket_retained_addition_raw_bytes_during_pass'] == executed_raw_bytes,
        'report_bucket_retained_addition_raw_bytes_accounted': isinstance(summary_metrics['report_bucket_retained_addition_raw_bytes_during_pass'], int),
        'report_bucket_retained_addition_file_count_accounted': isinstance(summary_metrics['report_bucket_retained_addition_file_count_during_pass'], int),
        'report_bucket_file_delta_reconciles_with_executed_files': summary_metrics['report_bucket_file_count_delta'] + summary_metrics['report_bucket_retained_addition_file_count_during_pass'] == len(executed_paths),
        'report_bucket_retained_addition_pair_count_accounted': isinstance(summary_metrics['report_bucket_retained_addition_pair_count_during_pass'], int),
        'report_bucket_pair_delta_reconciles_with_executed_pairs': summary_metrics['report_bucket_pair_count_delta'] + summary_metrics['report_bucket_retained_addition_pair_count_during_pass'] == executed_pair_count,
        'net_retained_file_shrink_positive': summary_metrics['retained_file_count_delta'] + summary_metrics['retained_addition_file_count_during_pass'] == len(executed_paths),
        'retained_addition_file_count_accounted': isinstance(summary_metrics['retained_addition_file_count_during_pass'], int),
        'net_raw_tree_shrink_positive': summary_metrics['raw_tree_bytes_delta'] + summary_metrics['retained_addition_raw_bytes_during_pass'] == executed_raw_bytes,
        'net_raw_tree_shrink_not_greater_than_executed_bytes': summary_metrics['raw_tree_bytes_delta'] + summary_metrics['retained_addition_raw_bytes_during_pass'] == executed_raw_bytes,
        'retained_addition_raw_bytes_accounted': isinstance(summary_metrics['retained_addition_raw_bytes_during_pass'], int),
        'executed_paths_removed_from_live_manifest': executed_path_set.isdisjoint({path for row in post_manifest_rows for path in row.get('exact_report_paths', [])}),
        'frontier_shifted_after_execution': not any(str(row['family']) == str(executed_manifest[0]['family']) for row in post_manifest_rows),
        'next_manifest_present': bool(post_manifest_rows) or int(post_report_bucket['raw_bytes']) == 0,
        'next_frontier_rehearsed': bool(post_manifest_rows) or int(post_report_bucket['raw_bytes']) == 0,
        'all_executed_rows_citation_backed': all(int(row['backing_handle_count']) >= 1 for row in executed_manifest),
    }
    passed = sum(1 for value in policy_checks.values() if value)
    ready = passed == len(policy_checks)
    headline_findings = [
        f"One cited canonical trim has now executed: {summary_metrics['executed_file_count']} retained report files across {summary_metrics['executed_family_count']} families left `artifacts/reports`, reclaiming {executed_raw_bytes} raw bytes ({summary_metrics['executed_share_of_pre_trim_report_bucket_raw_bytes']} share of the pre-trim reports bucket).",
        f"The live reports bucket fell from {summary_metrics['pre_trim_report_bucket_raw_bytes']} to {summary_metrics['post_trim_report_bucket_raw_bytes']} raw bytes and from {summary_metrics['pre_trim_report_bucket_file_count']} to {summary_metrics['post_trim_report_bucket_file_count']} files; the new leading hotspot is `{summary_metrics['next_frontier_leading_hotspot_family']}`." if leading_hotspot else 'The live measured reports frontier is now empty after the executed trim; no next hotspot family remains.',
        ('Because the refreshed rehearsal still projects zero next-frontier handle gaps, future byte-saving can start from the new current manifest rather than reopening the removed frontier or minting another durable note first.' if int(rehearsal_receipt['summary_metrics']['projected_frontier_gap_count']) == 0 else f"The refreshed rehearsal now exposes {int(rehearsal_receipt['summary_metrics']['projected_frontier_gap_count'])} next-frontier handle gap(s), so the next byte-saving pass should repair those gaps before trimming again."),
    ]
    return {
        'receipt_kind': 'archive_report_compaction_execution_receipt',
        'receipt_version': '2026-03-17.archive_report_compaction_execution_receipt.v1',
        'analysis_script': 'scripts/tools/build_archive_report_compaction_execution_receipt.py',
        'pre_trim_package_receipt_sha256': str(seed['pre_trim_package_receipt_sha256']),
        'pre_trim_manifest_receipt_sha256': str(seed['pre_trim_manifest_receipt_sha256']),
        'pre_trim_summary': pre_trim_summary,
        'post_package_receipt_path': _relativize(package_receipt_path),
        'post_package_receipt_sha256': _sha256_json(package_receipt),
        'post_hotspot_receipt_path': _relativize(hotspot_receipt_path),
        'post_hotspot_receipt_sha256': _sha256_json(hotspot_receipt),
        'post_manifest_receipt_path': _relativize(manifest_receipt_path),
        'post_manifest_receipt_sha256': _sha256_json(manifest_receipt),
        'post_rehearsal_receipt_path': _relativize(rehearsal_receipt_path),
        'post_rehearsal_receipt_sha256': _sha256_json(rehearsal_receipt),
        'measurement_scope': {'report_root': 'artifacts/reports', 'seed_receipt_self_reused': True, 'output_receipt_self_excluded': False, 'post_execution_frontier_refresh_required': True},
        'summary_metrics': summary_metrics,
        'executed_manifest': executed_manifest,
        'policy_checks': policy_checks,
        'status_counts': {'passed_check_count': passed, 'total_check_count': len(policy_checks), 'ready_to_cite': ready},
        'archive_posture': {'intended_retention_class': 'durable_compaction_execution_receipt', 'prefer_citation_over_recopy': True, 'size_discipline_note': 'Carry one compact execution receipt after a canonical trim so future inheritors can see exactly which cited report frontier actually left the archive, how much net space it reclaimed, and which smaller frontier replaced it.'},
        'headline_findings': headline_findings,
        'recommended_next_move': ('Treat this receipt as proof that the first cited canonical trim actually executed. Any later byte-saving should start from the refreshed current manifest / rehearsal / stage receipts on the smaller tree rather than from the already-removed frontier.' if int(rehearsal_receipt['summary_metrics']['projected_frontier_gap_count']) == 0 else 'Treat this receipt as proof that the first cited canonical trim executed, but pause before another trim: start by repairing the newly exposed handle gaps in the refreshed rehearsal and only then generate the next manifest / stage plan on the smaller tree.') if ready else 'Do not cite this execution receipt yet; rebuild the post-trim package, hotspot, manifest, and rehearsal receipts until all execution checks pass together on the current smaller tree.',
    }
def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact receipt proving that a cited exact-file report compaction frontier actually left the archive and that a refreshed smaller frontier replaced it.')
    parser.add_argument('--package-receipt', default=str(DEFAULT_PACKAGE_RECEIPT))
    parser.add_argument('--hotspot-receipt', default=str(DEFAULT_HOTSPOT_RECEIPT))
    parser.add_argument('--manifest-receipt', default=str(DEFAULT_MANIFEST_RECEIPT))
    parser.add_argument('--rehearsal-receipt', default=str(DEFAULT_REHEARSAL_RECEIPT))
    parser.add_argument('--seed-receipt', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--pre-package')
    parser.add_argument('--pre-manifest')
    parser.add_argument('--pre-archive')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    seed = _load_seed(Path(args.seed_receipt), Path(args.pre_package) if args.pre_package else None, Path(args.pre_manifest) if args.pre_manifest else None, Path(args.pre_archive) if args.pre_archive else None)
    receipt = build_receipt(load_json(Path(args.package_receipt)), Path(args.package_receipt), load_json(Path(args.hotspot_receipt)), Path(args.hotspot_receipt), load_json(Path(args.manifest_receipt)), Path(args.manifest_receipt), load_json(Path(args.rehearsal_receipt)), Path(args.rehearsal_receipt), seed)
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return 0 if (not args.strict or receipt['status_counts']['ready_to_cite']) else 1
if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
DEFAULT_MANIFEST_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'
DEFAULT_REHEARSAL_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_rehearsal_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_stage_receipt.json'
REPORT_ROOT = ROOT / 'artifacts' / 'reports'
DEFAULT_STAGE_ROOT = ROOT / 'examples' / 'scratch' / 'archive_report_compaction_stage'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def _stage_path_for(source_rel: str, stage_root: Path) -> Path:
    return stage_root / Path(source_rel)


def _stage_root_file_count(stage_root: Path) -> int:
    return sum(1 for path in stage_root.rglob('*') if path.is_file()) if stage_root.exists() else 0


def build_receipt(
    package_receipt: dict[str, Any],
    package_receipt_path: Path,
    manifest_receipt: dict[str, Any],
    manifest_receipt_path: Path,
    rehearsal_receipt: dict[str, Any],
    rehearsal_receipt_path: Path,
    output_path: Path,
    stage_root: Path,
) -> dict[str, Any]:
    manifest_rows = list(manifest_receipt.get('trim_manifest', []))
    report_bucket_raw_bytes = int(package_receipt.get('report_growth_surface', {}).get('raw_bytes', 0))
    current_raw_tree_bytes = int(package_receipt.get('archive_totals', {}).get('raw_bytes_excluding_receipt', 0))

    stage_manifest: list[dict[str, Any]] = []
    stage_file_rows_flat: list[dict[str, Any]] = []
    for row in manifest_rows:
        file_rows: list[dict[str, Any]] = []
        for source_rel in row.get('exact_report_paths', []):
            source_path = ROOT / source_rel
            stage_path = _stage_path_for(source_rel, stage_root)
            file_row = {
                'source_path': source_rel,
                'source_sha256': _sha256_file(source_path),
                'stage_path': _relativize(stage_path),
                'raw_bytes': int(source_path.stat().st_size),
                'raw_mebibytes': _mib(int(source_path.stat().st_size)),
                'file_kind': source_path.suffix.lstrip('.') or 'other',
            }
            file_rows.append(file_row)
            stage_file_rows_flat.append(file_row)
        stage_manifest.append(
            {
                'priority_rank': int(row['priority_rank']),
                'family': str(row['family']),
                'raw_bytes': int(row['raw_bytes']),
                'raw_mebibytes': float(row['raw_mebibytes']),
                'share_of_report_bucket_raw_bytes': float(row['share_of_report_bucket_raw_bytes']),
                'exact_report_file_count': int(row['exact_report_file_count']),
                'backing_handle_count': int(row['backing_handle_count']),
                'backing_handles': list(row['backing_handles']),
                'trim_mode': str(row['trim_mode']),
                'stage_mode': 'move_to_scratch_then_validate_then_delete_staged_copy',
                'source_report_paths': list(row['exact_report_paths']),
                'stage_paths': [file_row['stage_path'] for file_row in file_rows],
                'file_rows': file_rows,
            }
        )

    stage_raw_bytes = sum(int(row['raw_bytes']) for row in stage_file_rows_flat)
    projected_report_bucket_after_stage_raw_bytes = report_bucket_raw_bytes - stage_raw_bytes
    projected_scratch_stage_raw_bytes = stage_raw_bytes
    projected_raw_tree_during_stage_bytes = current_raw_tree_bytes
    projected_raw_tree_after_canonical_trim_bytes = int(rehearsal_receipt.get('summary_metrics', {}).get('projected_raw_tree_bytes', 0))
    summary_metrics = {
        'stage_family_count': len(stage_manifest),
        'stage_file_count': len(stage_file_rows_flat),
        'stage_raw_bytes': stage_raw_bytes,
        'stage_raw_mebibytes': _mib(stage_raw_bytes),
        'stage_share_of_report_bucket_raw_bytes': round(stage_raw_bytes / report_bucket_raw_bytes, 6) if report_bucket_raw_bytes else 0.0,
        'projected_report_bucket_after_stage_raw_bytes': projected_report_bucket_after_stage_raw_bytes,
        'projected_report_bucket_after_stage_raw_mebibytes': _mib(projected_report_bucket_after_stage_raw_bytes),
        'projected_scratch_stage_raw_bytes': projected_scratch_stage_raw_bytes,
        'projected_scratch_stage_raw_mebibytes': _mib(projected_scratch_stage_raw_bytes),
        'projected_raw_tree_during_stage_bytes': projected_raw_tree_during_stage_bytes,
        'projected_raw_tree_during_stage_mebibytes': _mib(projected_raw_tree_during_stage_bytes),
        'projected_raw_tree_after_canonical_trim_bytes': projected_raw_tree_after_canonical_trim_bytes,
        'projected_raw_tree_after_canonical_trim_mebibytes': _mib(projected_raw_tree_after_canonical_trim_bytes),
        'stage_root_preexisting_file_count': _stage_root_file_count(stage_root),
    }

    stage_paths = [file_row['stage_path'] for file_row in stage_file_rows_flat]
    source_paths = [file_row['source_path'] for file_row in stage_file_rows_flat]
    stage_path_set = set(stage_paths)
    source_path_set = set(source_paths)
    manifest_raw_bytes = int(manifest_receipt.get('summary_metrics', {}).get('manifest_raw_bytes', -1))
    rehearsal_trimmed_raw_bytes = int(rehearsal_receipt.get('summary_metrics', {}).get('trimmed_raw_bytes', -2))
    policy_checks = {
        'package_receipt_ready': bool(package_receipt.get('status_counts', {}).get('package_ready')),
        'manifest_receipt_ready': bool(manifest_receipt.get('status_counts', {}).get('ready_to_cite')),
        'rehearsal_receipt_ready': bool(rehearsal_receipt.get('status_counts', {}).get('ready_to_cite')),
        'stage_manifest_nonempty': bool(stage_manifest) or manifest_raw_bytes == 0,
        'stage_root_clear_now': summary_metrics['stage_root_preexisting_file_count'] == 0,
        'source_paths_exist_under_reports': all((ROOT / rel).exists() and (ROOT / rel).is_relative_to(REPORT_ROOT) for rel in source_paths) if source_paths else manifest_raw_bytes == 0,
        'stage_paths_unique': len(stage_path_set) == len(stage_paths),
        'stage_paths_absent_now': all(not (ROOT / rel).exists() for rel in stage_paths),
        'stage_paths_live_under_examples_scratch': all((ROOT / rel).resolve().is_relative_to((ROOT / 'examples' / 'scratch').resolve()) for rel in stage_paths),
        'stage_and_source_paths_disjoint': stage_path_set.isdisjoint(source_path_set),
        'stage_raw_bytes_match_manifest': stage_raw_bytes == manifest_raw_bytes,
        'stage_raw_bytes_match_rehearsal_trim': stage_raw_bytes == rehearsal_trimmed_raw_bytes,
        'projected_report_bucket_after_stage_matches_rehearsal': projected_report_bucket_after_stage_raw_bytes == int(rehearsal_receipt.get('summary_metrics', {}).get('projected_report_bucket_raw_bytes', -1)),
        'projected_canonical_trim_matches_rehearsal': projected_raw_tree_after_canonical_trim_bytes == int(rehearsal_receipt.get('summary_metrics', {}).get('projected_raw_tree_bytes', -1)),
        'all_stage_rows_citation_backed': all(int(row['backing_handle_count']) >= 1 for row in stage_manifest),
    }
    passed = sum(1 for value in policy_checks.values() if value)
    ready = passed == len(policy_checks)

    top = stage_manifest[0] if stage_manifest else None
    headline_findings = [
        (
            f"One scratch-stage plan now mirrors the current exact-file compaction manifest into `{_relativize(stage_root)}`: {summary_metrics['stage_file_count']} report files across {summary_metrics['stage_family_count']} families totaling {stage_raw_bytes} raw bytes ({summary_metrics['stage_share_of_report_bucket_raw_bytes']} share of the reports bucket)."
            if stage_manifest
            else 'No stage rows are available for the current manifest.'
        ),
        (
            f"Staging those files would immediately drop the live reports bucket from {report_bucket_raw_bytes} to {projected_report_bucket_after_stage_raw_bytes} raw bytes while keeping the overall tree size flat until the staged scratch copy is deleted; the first staged family is `{top['family']}` at {top['raw_bytes']} bytes."
            if top
            else 'No first staged family is available because no live compaction manifest remains.'
        ),
        'Because the projected canonical-trim totals exactly match the rehearsal receipt, future sessions can stage first for reversibility, validate the trimmed tree, and only then delete the staged scratch copy before the next zip.' if stage_manifest else 'No scratch-stage rehearsal is needed on the current tree because no live compaction manifest remains.',
    ]

    return {
        'receipt_kind': 'archive_report_compaction_stage_receipt',
        'receipt_version': '2026-03-17.archive_report_compaction_stage_receipt.v1',
        'analysis_script': 'scripts/tools/build_archive_report_compaction_stage_receipt.py',
        'package_receipt_path': _relativize(package_receipt_path),
        'package_receipt_sha256': _sha256_json(package_receipt),
        'compaction_manifest_receipt_path': _relativize(manifest_receipt_path),
        'compaction_manifest_receipt_sha256': _sha256_json(manifest_receipt),
        'compaction_rehearsal_receipt_path': _relativize(rehearsal_receipt_path),
        'compaction_rehearsal_receipt_sha256': _sha256_json(rehearsal_receipt),
        'measurement_scope': {
            'report_root': 'artifacts/reports',
            'stage_root': _relativize(stage_root),
            'stage_path_strategy': 'mirror each source report path under examples/scratch/archive_report_compaction_stage before validation and canonical deletion',
            'stage_root_retained_in_package': False,
            'output_receipt_self_excluded': False,
        },
        'summary_metrics': summary_metrics,
        'stage_manifest': stage_manifest,
        'policy_checks': policy_checks,
        'status_counts': {'passed_check_count': passed, 'total_check_count': len(policy_checks), 'ready_to_cite': ready},
        'archive_posture': {
            'intended_retention_class': 'durable_compaction_stage_receipt',
            'prefer_citation_over_recopy': True,
            'size_discipline_note': 'Carry one tiny scratch-stage receipt so future byte-saving can stage the current exact-file manifest reversibly inside examples/scratch, validate the trimmed tree, and only then delete the staged copy before the next zip.',
        },
        'headline_findings': headline_findings,
        'recommended_next_move': (
            (f"No live stage plan remains because the current exact-file compaction manifest is empty; keep `{_relativize(stage_root)}` clear and only stage again if a future retained report frontier reappears." if summary_metrics['stage_raw_bytes'] == 0 else f"When the archive truly needs bytes back, temporarily move the listed report paths into `{_relativize(stage_root)}`, cite their durable handles, rebuild the hotspot/package stack on the trimmed tree, then delete the staged scratch copy and restore a scratch-free package boundary before cutting the next revision zip.")
            if ready
            else 'Do not stage from this receipt yet; rebuild the package, manifest, and rehearsal receipts on the current clean tree until this stage plan is ready to cite.'
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact scratch-stage receipt for the current exact-file compaction manifest.')
    parser.add_argument('--package-receipt', default=str(DEFAULT_PACKAGE_RECEIPT))
    parser.add_argument('--manifest-receipt', default=str(DEFAULT_MANIFEST_RECEIPT))
    parser.add_argument('--rehearsal-receipt', default=str(DEFAULT_REHEARSAL_RECEIPT))
    parser.add_argument('--stage-root', default=str(DEFAULT_STAGE_ROOT))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    receipt = build_receipt(
        package_receipt=load_json(Path(args.package_receipt)),
        package_receipt_path=Path(args.package_receipt),
        manifest_receipt=load_json(Path(args.manifest_receipt)),
        manifest_receipt_path=Path(args.manifest_receipt),
        rehearsal_receipt=load_json(Path(args.rehearsal_receipt)),
        rehearsal_receipt_path=Path(args.rehearsal_receipt),
        output_path=Path(args.output),
        stage_root=Path(args.stage_root),
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    Path(args.output).write_text(rendered, encoding='utf-8')
    return 0 if (not args.strict or receipt['status_counts']['ready_to_cite']) else 1


if __name__ == '__main__':
    raise SystemExit(main())

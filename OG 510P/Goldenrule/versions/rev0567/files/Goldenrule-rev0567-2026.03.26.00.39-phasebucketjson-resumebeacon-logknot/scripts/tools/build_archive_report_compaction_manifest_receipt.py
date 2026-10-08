#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
DEFAULT_CANDIDATE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_candidate_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'
REPORT_ROOT = ROOT / 'artifacts' / 'reports'
FAMILY_SUFFIX_PATTERNS = [
    re.compile(r'_snapshot_\d{8}$'),
    re.compile(r'_\d{8}$'),
    re.compile(r'_[0-9]{4}\.[0-9]{2}\.[0-9]{2}$'),
]


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


def _family_name(path: Path) -> str:
    name = path.stem
    for pattern in FAMILY_SUFFIX_PATTERNS:
        name = pattern.sub('', name)
    return name


def _family_files(family: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(REPORT_ROOT.iterdir(), key=lambda p: p.name):
        if not path.is_file():
            continue
        if _family_name(path) != family:
            continue
        size = path.stat().st_size
        rows.append(
            {
                'path': path.relative_to(ROOT).as_posix(),
                'raw_bytes': size,
                'raw_mebibytes': _mib(size),
            }
        )
    rows.sort(key=lambda row: row['path'])
    return rows


def _trim_mode(row: dict[str, Any]) -> str:
    return 'drop_report_pair_after_citing_handles' if row.get('has_json_md_pair') else 'drop_retained_family_after_citing_handles'


def build_receipt(package_receipt: dict[str, Any], package_receipt_path: Path, candidate_receipt: dict[str, Any], candidate_receipt_path: Path) -> dict[str, Any]:
    candidates = list(candidate_receipt.get('priority_candidates', []))
    report_bucket_raw_bytes = int(package_receipt.get('report_growth_surface', {}).get('raw_bytes', 0))
    manifest_rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates, start=1):
        files = _family_files(str(candidate['family']))
        raw_bytes = sum(int(row['raw_bytes']) for row in files)
        manifest_rows.append(
            {
                'priority_rank': rank,
                'family': candidate['family'],
                'raw_bytes': raw_bytes,
                'raw_mebibytes': _mib(raw_bytes),
                'share_of_report_bucket_raw_bytes': round(raw_bytes / report_bucket_raw_bytes, 6) if report_bucket_raw_bytes else 0.0,
                'exact_report_file_count': len(files),
                'exact_report_paths': [row['path'] for row in files],
                'exact_report_files': files,
                'has_json_md_pair': bool(candidate['has_json_md_pair']),
                'candidate_compaction_readiness': candidate['compaction_readiness'],
                'semantic_alias_used': bool(candidate['semantic_alias_used']),
                'backing_handle_count': int(candidate['backing_handle_count']),
                'backing_handles': list(candidate['backing_handles']),
                'trim_mode': _trim_mode(candidate),
                'trim_rationale': str(candidate['rationale']),
            }
        )

    manifest_raw_bytes = sum(int(row['raw_bytes']) for row in manifest_rows)
    summary_metrics = {
        'manifest_family_count': len(manifest_rows),
        'manifest_file_count': sum(int(row['exact_report_file_count']) for row in manifest_rows),
        'manifest_pair_count': sum(1 for row in manifest_rows if row['has_json_md_pair']),
        'manifest_raw_bytes': manifest_raw_bytes,
        'manifest_raw_mebibytes': _mib(manifest_raw_bytes),
        'manifest_share_of_report_bucket_raw_bytes': round(manifest_raw_bytes / report_bucket_raw_bytes, 6) if report_bucket_raw_bytes else 0.0,
        'manifest_rows_using_semantic_alias_count': sum(1 for row in manifest_rows if row['semantic_alias_used']),
    }

    expected_family_order = [str(row['family']) for row in candidates]
    actual_family_order = [str(row['family']) for row in manifest_rows]
    all_paths = [path for row in manifest_rows for path in row['exact_report_paths']]
    per_family_bytes_match = all(int(row['raw_bytes']) == int(candidate['raw_bytes']) for row, candidate in zip(manifest_rows, candidates))
    per_family_counts_match = all(int(row['exact_report_file_count']) == int(candidate['file_count']) for row, candidate in zip(manifest_rows, candidates))
    policy_checks = {
        'package_receipt_ready': bool(package_receipt.get('status_counts', {}).get('package_ready')),
        'candidate_receipt_ready': bool(candidate_receipt.get('status_counts', {}).get('ready_to_cite')),
        'manifest_rows_nonempty': bool(manifest_rows) or int(candidate_receipt.get('summary_metrics', {}).get('priority_candidate_raw_bytes', 0)) == 0,
        'manifest_families_match_priority_candidates': actual_family_order == expected_family_order,
        'manifest_paths_unique': len(set(all_paths)) == len(all_paths),
        'manifest_paths_exist_under_reports': all((ROOT / path).exists() and (ROOT / path).is_relative_to(REPORT_ROOT) for path in all_paths),
        'manifest_file_counts_match_candidate_receipt': per_family_counts_match,
        'manifest_raw_bytes_match_candidate_receipt': per_family_bytes_match and manifest_raw_bytes == int(candidate_receipt.get('summary_metrics', {}).get('priority_candidate_raw_bytes', -1)),
        'all_manifest_rows_citation_backed': all(int(row['backing_handle_count']) >= 1 for row in manifest_rows),
    }
    passed = sum(1 for value in policy_checks.values() if value)
    ready = passed == len(policy_checks)
    top = manifest_rows[0] if manifest_rows else None
    headline_findings = [
        (
            f"One exact-file compaction manifest now covers {summary_metrics['manifest_file_count']} retained report files across {summary_metrics['manifest_family_count']} citation-backed hotspot families, totaling {manifest_raw_bytes} raw bytes ({summary_metrics['manifest_share_of_report_bucket_raw_bytes']} share of the reports bucket)."
            if manifest_rows
            else 'No citation-backed manifest rows were available for the current report-compaction frontier.'
        ),
        (
            f"The first manifest row is `{top['family']}` at {top['raw_bytes']} bytes across {top['exact_report_file_count']} exact retained files; future byte-saving can act on those paths after citing {top['backing_handle_count']} durable handle(s)."
            if top
            else 'No first manifest row is available.'
        ),
        (
            'Because every manifest row already has durable non-report backing handles, the current archive-size frontier can be compacted by exact file path rather than by manual report-family archaeology.'
            if manifest_rows
            else 'A compaction manifest is not yet available for the current archive tree.'
        ),
    ]
    return {
        'receipt_kind': 'archive_report_compaction_manifest_receipt',
        'receipt_version': '2026-03-17.archive_report_compaction_manifest_receipt.v1',
        'analysis_script': 'scripts/tools/build_archive_report_compaction_manifest_receipt.py',
        'package_receipt_path': _relativize(package_receipt_path),
        'package_receipt_sha256': _sha256_json(package_receipt),
        'compaction_candidate_receipt_path': _relativize(candidate_receipt_path),
        'compaction_candidate_receipt_sha256': _sha256_json(candidate_receipt),
        'measurement_scope': {
            'report_root': 'artifacts/reports',
            'family_suffix_patterns': [pattern.pattern for pattern in FAMILY_SUFFIX_PATTERNS],
            'candidate_count_limit': len(candidates),
            'output_receipt_self_excluded': False,
        },
        'summary_metrics': summary_metrics,
        'trim_manifest': manifest_rows,
        'policy_checks': policy_checks,
        'status_counts': {'passed_check_count': passed, 'total_check_count': len(policy_checks), 'ready_to_cite': ready},
        'archive_posture': {
            'intended_retention_class': 'durable_compaction_manifest_receipt',
            'prefer_citation_over_recopy': True,
            'size_discipline_note': 'Carry one tiny exact-file compaction manifest so future byte-saving can remove the current citation-backed report frontier by path and handle, without rediscovering the same deletable families by hand.',
        },
        'headline_findings': headline_findings,
        'recommended_next_move': (
            ('No live exact-file compaction frontier remains on the current clean tree; keep citing the standing package, hotspot, and manifest receipts and avoid reintroducing retained report families unless a new durable contract is needed.' if summary_metrics['manifest_raw_bytes'] == 0 else 'When the archive needs the next byte-saving pass, cite the listed durable handles and compact the exact retained report paths in this manifest instead of rediscovering the current safe trim frontier by hand.')
            if ready
            else 'Do not trim from this manifest yet; rebuild the package and compaction-candidate receipts first, then regenerate the manifest on the current clean tree.'
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact exact-file compaction manifest for the current citation-backed report frontier.')
    parser.add_argument('--package-receipt', default=str(DEFAULT_PACKAGE_RECEIPT))
    parser.add_argument('--candidate-receipt', default=str(DEFAULT_CANDIDATE_RECEIPT))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    receipt = build_receipt(
        package_receipt=load_json(Path(args.package_receipt)),
        package_receipt_path=Path(args.package_receipt),
        candidate_receipt=load_json(Path(args.candidate_receipt)),
        candidate_receipt_path=Path(args.candidate_receipt),
    )
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return 0 if (not args.strict or receipt['status_counts']['ready_to_cite']) else 1


if __name__ == '__main__':
    raise SystemExit(main())

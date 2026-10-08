#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_hotspot_receipt.json'
REPORT_ROOT = ROOT / 'artifacts' / 'reports'
SKIP_PARTS = {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
SKIP_SUFFIXES = {'.pyc', '.pyo'}
FIXED_POINT_EXCLUDED_PATHS = {
    'examples/snapshots/rematch_world_benchmark_package_receipt.json',
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
ARTIFACT_BUCKETS = ['timing', 'security', 'process', 'release', 'formal', 'reports']
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


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def _report_bucket(files: list[Path]) -> tuple[dict[str, Any], list[Path]]:
    report_files = [path for path in files if path.is_relative_to(REPORT_ROOT)]
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
    }, report_files


def _family_name(path: Path) -> str:
    name = path.stem
    for pattern in FAMILY_SUFFIX_PATTERNS:
        name = pattern.sub('', name)
    return name


def _largest_report_families(report_files: list[Path], report_raw_bytes: int, limit: int = 10) -> list[dict[str, Any]]:
    families: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0, 'json_bytes': 0, 'md_bytes': 0})
    for path in report_files:
        family = _family_name(path)
        entry = families[family]
        size = path.stat().st_size
        entry['file_count'] += 1
        entry['raw_bytes'] += size
        if path.suffix == '.json':
            entry['json_bytes'] += size
        elif path.suffix == '.md':
            entry['md_bytes'] += size
    rows: list[dict[str, Any]] = []
    for family, data in families.items():
        rows.append(
            {
                'family': family,
                'file_count': int(data['file_count']),
                'raw_bytes': int(data['raw_bytes']),
                'raw_mebibytes': _mib(int(data['raw_bytes'])),
                'share_of_report_bucket_raw_bytes': round(int(data['raw_bytes']) / report_raw_bytes, 6) if report_raw_bytes else 0.0,
                'has_json_md_pair': data['json_bytes'] > 0 and data['md_bytes'] > 0,
                'json_bytes': int(data['json_bytes']),
                'md_bytes': int(data['md_bytes']),
            }
        )
    rows.sort(key=lambda row: (-row['raw_bytes'], row['family']))
    return rows[:limit]


def _largest_report_files(report_files: list[Path], report_raw_bytes: int, limit: int = 10) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(report_files, key=lambda p: (-p.stat().st_size, p.relative_to(REPORT_ROOT).as_posix()))[:limit]:
        size = path.stat().st_size
        rows.append(
            {
                'path': path.relative_to(ROOT).as_posix(),
                'raw_bytes': size,
                'raw_mebibytes': _mib(size),
                'share_of_report_bucket_raw_bytes': round(size / report_raw_bytes, 6) if report_raw_bytes else 0.0,
            }
        )
    return rows


def _artifact_bucket_ranking(files: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for bucket in ARTIFACT_BUCKETS:
        root = ROOT / 'artifacts' / bucket
        bucket_files = [path for path in files if path.is_relative_to(root)]
        raw_bytes = sum(path.stat().st_size for path in bucket_files)
        rows.append({'bucket': bucket, 'file_count': len(bucket_files), 'raw_bytes': raw_bytes})
    rows.sort(key=lambda row: (-row['raw_bytes'], row['bucket']))
    return rows


def _priority_targets(families: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    targets = []
    for row in families:
        if not row['has_json_md_pair']:
            continue
        targets.append(
            {
                'family': row['family'],
                'raw_bytes': row['raw_bytes'],
                'share_of_report_bucket_raw_bytes': row['share_of_report_bucket_raw_bytes'],
                'reason': 'Large retained JSON+MD report family; future work should cite or collapse this pair before adding another report surface here.',
            }
        )
        if len(targets) >= limit:
            break
    if targets:
        return targets
    fallback = families[:limit]
    return [
        {
            'family': row['family'],
            'raw_bytes': row['raw_bytes'],
            'share_of_report_bucket_raw_bytes': row['share_of_report_bucket_raw_bytes'],
            'reason': 'Large retained report family; review this hotspot first before retaining more archive fanout nearby.',
        }
        for row in fallback
    ]


def _concentration(families: list[dict[str, Any]]) -> dict[str, float]:
    def top_share(n: int) -> float:
        return round(sum(row['share_of_report_bucket_raw_bytes'] for row in families[:n]), 6)

    return {
        'top_1_family_share_of_report_bucket_raw_bytes': top_share(1),
        'top_3_family_share_of_report_bucket_raw_bytes': top_share(3),
        'top_5_family_share_of_report_bucket_raw_bytes': top_share(5),
        'top_10_family_share_of_report_bucket_raw_bytes': top_share(10),
        'top_10_pair_family_share_of_report_bucket_raw_bytes': round(
            sum(row['share_of_report_bucket_raw_bytes'] for row in families[:10] if row['has_json_md_pair']),
            6,
        ),
    }


def build_receipt(package_receipt: dict[str, Any], package_receipt_path: Path, output_path: Path) -> dict[str, Any]:
    files = _iter_files(ROOT, output_path)
    report_bucket_totals, report_files = _report_bucket(files)
    families = _largest_report_families(report_files, report_bucket_totals['raw_bytes'])
    report_files_top = _largest_report_files(report_files, report_bucket_totals['raw_bytes'])
    artifact_bucket_ranking = _artifact_bucket_ranking(files)
    priority_targets = _priority_targets(families)
    concentration = _concentration(families)

    package_growth_surface = package_receipt.get('report_growth_surface', {})
    bucket_keys = ['path', 'file_count', 'raw_bytes', 'json_md_pair_count', 'paired_raw_bytes']
    policy_checks = {
        'package_receipt_ready': bool(package_receipt.get('status_counts', {}).get('package_ready')),
        'report_bucket_totals_match_package_receipt': all(report_bucket_totals.get(key) == package_growth_surface.get(key) for key in bucket_keys),
        'reports_remain_top_three_artifact_buckets': report_bucket_totals['raw_bytes'] == 0 or any(row['bucket'] == 'reports' for row in artifact_bucket_ranking[:3]),
        'hotspot_table_nonempty': (bool(families) and bool(report_files_top)) or report_bucket_totals['raw_bytes'] == 0,
    }
    passed_check_count = sum(1 for value in policy_checks.values() if value)
    ready_to_cite = passed_check_count == len(policy_checks)

    top_family = families[0] if families else None
    headline_findings = [
        (
            f"The measured `artifacts/reports` growth surface now occupies {report_bucket_totals['raw_bytes']} raw bytes "
            f"({report_bucket_totals['share_of_raw_tree']} share of the raw tree), aligned with the standing package receipt."
        ),
        (
            f"The top 10 report families account for {concentration['top_10_family_share_of_report_bucket_raw_bytes']} of report-bucket bytes, "
            f"with paired JSON+MD families alone contributing {concentration['top_10_pair_family_share_of_report_bucket_raw_bytes']} of the bucket among those top hotspots."
            if families
            else 'No citation-counted report families remain on the current tree once fixed-point size-control outputs are excluded from hotspot measurement.'
        ),
        (
            f"The single largest current report family is `{top_family['family']}` at {top_family['raw_bytes']} bytes "
            f"across {top_family['file_count']} retained files."
            if top_family
            else 'No retained report hotspots were found.'
        ),
    ]

    if ready_to_cite:
        next_move = (
            'No citation-counted report hotspot frontier remains on the current tree; keep citing the standing package and hotspot receipts and avoid reintroducing retained report fanout unless a genuinely new machine-readable contract is needed.'
            if report_bucket_totals['raw_bytes'] == 0
            else 'Cite this hotspot receipt when deciding where to compact the report bucket next; prioritize the listed paired families before retaining any new report family nearby.'
        )
    else:
        next_move = (
            'Do not rely on this hotspot receipt yet; rebuild the package receipt and restore report-bucket alignment before using hotspot rankings to guide compaction.'
        )

    return {
        'receipt_kind': 'archive_report_hotspot_receipt',
        'receipt_version': '2026-03-17.archive_report_hotspot_receipt.v1',
        'analysis_script': 'scripts/tools/build_archive_report_hotspot_receipt.py',
        'measurement_scope': {
            'tree_root': '.',
            'report_root': 'artifacts/reports',
            'output_receipt_self_excluded': True,
            'excluded_output_path': _relativize(output_path),
            'skip_parts': sorted(SKIP_PARTS),
            'skip_suffixes': sorted(SKIP_SUFFIXES),
            'fixed_point_excluded_paths': sorted(FIXED_POINT_EXCLUDED_PATHS),
        },
        'package_receipt_path': _relativize(package_receipt_path),
        'package_receipt_sha256': _sha256_json(package_receipt),
        'report_bucket_totals': report_bucket_totals,
        'hotspot_concentration': concentration,
        'largest_report_families': families,
        'largest_report_files': report_files_top,
        'priority_compaction_targets': priority_targets,
        'policy_checks': policy_checks,
        'status_counts': {
            'passed_check_count': passed_check_count,
            'total_check_count': len(policy_checks),
            'ready_to_cite': ready_to_cite,
        },
        'archive_posture': {
            'prefer_citation_over_recopy': True,
            'intended_retention_class': 'durable_report_hotspot_receipt',
            'size_discipline_note': 'Carry one tiny hotspot receipt that distills the bulky archive-size profile into the specific retained report families most worth compacting next, without adding another report pair.',
        },
        'headline_findings': headline_findings,
        'recommended_next_move': next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact receipt ranking the report-bucket hotspots that matter most for future archive compaction.')
    parser.add_argument('--package-receipt', default=str(DEFAULT_PACKAGE_RECEIPT))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    output_path = Path(args.output)
    receipt = build_receipt(
        package_receipt=load_json(Path(args.package_receipt)),
        package_receipt_path=Path(args.package_receipt),
        output_path=output_path,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    if args.strict and not receipt['status_counts']['ready_to_cite']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

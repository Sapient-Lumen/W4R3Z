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
DEFAULT_MANIFEST_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_manifest_receipt.json'
DEFAULT_SEMANTIC_HANDLE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_semantic_handle_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_compaction_rehearsal_receipt.json'
REPORT_ROOT = ROOT / 'artifacts' / 'reports'
SEARCH_ROOTS = [ROOT / 'docs' / 'LIBRARY' / 'topics', ROOT / 'examples' / 'snapshots']
EXCLUDED_HANDLE_PATHS = {
    'docs/AGENT_LOG.md',
    'docs/SCHEMA_INVENTORY.md',
    'docs/VALIDATOR_INVENTORY.md',
    'examples/snapshots/archive_report_hotspot_receipt.json',
    'examples/snapshots/archive_report_semantic_handle_receipt.json',
    'examples/snapshots/archive_report_compaction_candidate_receipt.json',
    'examples/snapshots/archive_report_compaction_gap_receipt.json',
    'examples/snapshots/archive_report_compaction_manifest_receipt.json',
    'examples/snapshots/archive_report_compaction_rehearsal_receipt.json',
    'examples/snapshots/archive_report_compaction_stage_receipt.json',
    'examples/snapshots/archive_report_compaction_execution_receipt.json',
}
PRIMARY_DOC_PATHS = {
    'docs/BENCHMARK_PROGRAM.md',
    'docs/BUCKET.md',
    'docs/DATA_MANAGEMENT.md',
    'docs/LIBRARY/README.md',
    'docs/RESEARCH_AGENDA.md',
    'docs/TRANCHES.md',
    'docs/TRANCHES_SUMMARY.md',
}
PROJECTED_FRONTIER_LIMIT = 6
REPORT_FIXED_POINT_EXCLUDED_PATHS = {
    'artifacts/reports/artifact_summary.json',
    'artifacts/reports/artifact_bucket_inventory.json',
    'artifacts/reports/archive_size_profile_snapshot_20260316.json',
    'artifacts/reports/archive_size_profile_snapshot_20260316.md',
}
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


def _report_files() -> list[Path]:
    excluded = {(ROOT / rel).resolve() for rel in REPORT_FIXED_POINT_EXCLUDED_PATHS}
    return sorted(path for path in REPORT_ROOT.iterdir() if path.is_file() and path.resolve() not in excluded)


def _family_rows(report_files: list[Path], bucket_raw_bytes: int, limit: int | None = None) -> list[dict[str, Any]]:
    families: defaultdict[str, dict[str, int]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0, 'json_bytes': 0, 'md_bytes': 0})
    for path in report_files:
        family = _family_name(path)
        size = path.stat().st_size
        entry = families[family]
        entry['file_count'] += 1
        entry['raw_bytes'] += size
        if path.suffix == '.json':
            entry['json_bytes'] += size
        elif path.suffix == '.md':
            entry['md_bytes'] += size
    rows: list[dict[str, Any]] = []
    for family, entry in families.items():
        rows.append(
            {
                'family': family,
                'file_count': int(entry['file_count']),
                'raw_bytes': int(entry['raw_bytes']),
                'raw_mebibytes': _mib(int(entry['raw_bytes'])),
                'share_of_report_bucket_raw_bytes': round(int(entry['raw_bytes']) / bucket_raw_bytes, 6) if bucket_raw_bytes else 0.0,
                'has_json_md_pair': entry['json_bytes'] > 0 and entry['md_bytes'] > 0,
            }
        )
    rows.sort(key=lambda row: (-row['raw_bytes'], row['family']))
    return rows if limit is None else rows[:limit]


def _pair_count(report_files: list[Path]) -> int:
    pair_map: defaultdict[str, set[str]] = defaultdict(set)
    for path in report_files:
        if path.suffix in {'.json', '.md'}:
            pair_map[str(path.with_suffix(''))].add(path.suffix)
    return sum(1 for suffixes in pair_map.values() if '.json' in suffixes and '.md' in suffixes)


def _handle_kind(rel: str) -> str:
    if rel.startswith('docs/LIBRARY/topics/'):
        return 'library_topic'
    if rel.startswith('examples/snapshots/'):
        return 'snapshot'
    return 'doc'


def _load_search_index() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path.suffix not in {'.md', '.json'}:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in EXCLUDED_HANDLE_PATHS:
                continue
            rows.append((rel, path.read_text(encoding='utf-8', errors='ignore').lower()))
    for rel in sorted(PRIMARY_DOC_PATHS):
        path = ROOT / rel
        if path.exists():
            rows.append((rel, path.read_text(encoding='utf-8', errors='ignore').lower()))
    return rows


def _find_literal_handles(family: str, search_index: list[tuple[str, str]], limit: int = 3) -> list[dict[str, str]]:
    needle = family.lower()
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    for rel, text in search_index:
        if needle not in text or rel in seen:
            continue
        seen.add(rel)
        found.append({'path': rel, 'kind': _handle_kind(rel)})
    found.sort(key=lambda row: ({'library_topic': 0, 'snapshot': 1, 'doc': 2}[row['kind']], row['path']))
    return found[:limit]


def _family_alias_keys(family: str) -> list[str]:
    keys = [family]
    if family.endswith('_snapshot'):
        keys.append(family[:-9])
    return keys

def _load_semantic_alias_map(semantic_handle_receipt: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in semantic_handle_receipt.get('semantic_aliases', []):
        handle = row.get('matched_handle', {})
        path = str(handle.get('path', ''))
        if not path:
            continue
        for key in _family_alias_keys(str(row['family'])):
            out.setdefault(key, []).append({'path': path, 'kind': str(handle.get('kind', _handle_kind(path)))})
    return out


def _combine_handles(family: str, search_index: list[tuple[str, str]], alias_map: dict[str, list[dict[str, str]]], limit: int = 3) -> tuple[list[dict[str, str]], int]:
    found: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    semantic_alias_count = 0
    for handle in alias_map.get(family, []):
        key = (handle['path'], handle['kind'])
        if key in seen:
            continue
        seen.add(key)
        semantic_alias_count += 1
        found.append(handle)
    for handle in _find_literal_handles(family, search_index, limit=limit * 2):
        key = (handle['path'], handle['kind'])
        if key in seen:
            continue
        seen.add(key)
        found.append(handle)
    found.sort(key=lambda row: ({'library_topic': 0, 'snapshot': 1, 'doc': 2}[row['kind']], row['path']))
    return found[:limit], semantic_alias_count


def _readiness(handles: list[dict[str, str]], has_pair: bool) -> str:
    if not handles:
        return 'handle_gap'
    kinds = {row['kind'] for row in handles}
    if 'library_topic' in kinds and has_pair:
        return 'citation_ready_pair'
    if 'library_topic' in kinds:
        return 'citation_ready'
    if 'snapshot' in kinds and has_pair:
        return 'artifact_backed_pair'
    if 'snapshot' in kinds:
        return 'artifact_backed'
    return 'doc_backed'


def build_receipt(package_receipt: dict[str, Any], package_receipt_path: Path, manifest_receipt: dict[str, Any], manifest_receipt_path: Path, semantic_handle_receipt: dict[str, Any], semantic_handle_receipt_path: Path) -> dict[str, Any]:
    current_report_files = _report_files()
    current_report_bucket_raw_bytes = int(package_receipt.get('report_growth_surface', {}).get('raw_bytes', 0))
    current_raw_tree_bytes = int(package_receipt.get('archive_totals', {}).get('raw_bytes_excluding_receipt', 0))
    current_retained_file_count = int(package_receipt.get('archive_totals', {}).get('retained_file_count_excluding_receipt', 0))
    current_family_rows = _family_rows(current_report_files, current_report_bucket_raw_bytes)
    current_rank_map = {str(row['family']): rank for rank, row in enumerate(current_family_rows, start=1)}

    manifest_rows = list(manifest_receipt.get('trim_manifest', []))
    trimmed_paths = [ROOT / path for row in manifest_rows for path in row.get('exact_report_paths', [])]
    trimmed_resolved = {path.resolve() for path in trimmed_paths}
    remaining_report_files = [path for path in current_report_files if path.resolve() not in trimmed_resolved]
    projected_report_bucket_raw_bytes = sum(path.stat().st_size for path in remaining_report_files)
    projected_report_bucket_file_count = len(remaining_report_files)
    projected_report_bucket_pair_count = _pair_count(remaining_report_files)
    projected_raw_tree_bytes = current_raw_tree_bytes - int(manifest_receipt.get('summary_metrics', {}).get('manifest_raw_bytes', 0))
    projected_retained_file_count = current_retained_file_count - int(manifest_receipt.get('summary_metrics', {}).get('manifest_file_count', 0))

    search_index = _load_search_index()
    alias_map = _load_semantic_alias_map(semantic_handle_receipt)
    projected_family_rows = _family_rows(remaining_report_files, projected_report_bucket_raw_bytes, limit=PROJECTED_FRONTIER_LIMIT)
    projected_next_frontier: list[dict[str, Any]] = []
    for rank, row in enumerate(projected_family_rows, start=1):
        handles, alias_count = _combine_handles(str(row['family']), search_index, alias_map)
        readiness = _readiness(handles, bool(row['has_json_md_pair']))
        projected_next_frontier.append(
            {
                'projected_rank': rank,
                'current_rank': current_rank_map.get(str(row['family'])),
                'family': row['family'],
                'raw_bytes': row['raw_bytes'],
                'raw_mebibytes': row['raw_mebibytes'],
                'share_of_projected_report_bucket_raw_bytes': row['share_of_report_bucket_raw_bytes'],
                'file_count': row['file_count'],
                'has_json_md_pair': row['has_json_md_pair'],
                'backing_handle_count': len(handles),
                'backing_handle_kinds': sorted({handle['kind'] for handle in handles}),
                'backing_handles': handles,
                'semantic_alias_used': alias_count >= 1,
                'projected_compaction_readiness': readiness,
            }
        )

    trimmed_families = [
        {
            'priority_rank': int(row['priority_rank']),
            'family': str(row['family']),
            'raw_bytes': int(row['raw_bytes']),
            'raw_mebibytes': float(row['raw_mebibytes']),
            'exact_report_file_count': int(row['exact_report_file_count']),
        }
        for row in manifest_rows
    ]

    projected_frontier_gap_count = sum(1 for row in projected_next_frontier if row['backing_handle_count'] == 0)
    projected_frontier_handle_covered_count = sum(1 for row in projected_next_frontier if row['backing_handle_count'] >= 1)
    summary_metrics = {
        'trimmed_family_count': len(trimmed_families),
        'trimmed_file_count': sum(int(row['exact_report_file_count']) for row in trimmed_families),
        'trimmed_raw_bytes': int(manifest_receipt.get('summary_metrics', {}).get('manifest_raw_bytes', 0)),
        'trimmed_raw_mebibytes': _mib(int(manifest_receipt.get('summary_metrics', {}).get('manifest_raw_bytes', 0))),
        'trimmed_share_of_report_bucket_raw_bytes': float(manifest_receipt.get('summary_metrics', {}).get('manifest_share_of_report_bucket_raw_bytes', 0.0)),
        'projected_report_bucket_raw_bytes': projected_report_bucket_raw_bytes,
        'projected_report_bucket_raw_mebibytes': _mib(projected_report_bucket_raw_bytes),
        'projected_report_bucket_file_count': projected_report_bucket_file_count,
        'projected_report_bucket_pair_count': projected_report_bucket_pair_count,
        'projected_report_bucket_share_of_raw_tree': round(projected_report_bucket_raw_bytes / projected_raw_tree_bytes, 6) if projected_raw_tree_bytes else 0.0,
        'projected_raw_tree_bytes': projected_raw_tree_bytes,
        'projected_raw_tree_mebibytes': _mib(projected_raw_tree_bytes),
        'projected_retained_file_count': projected_retained_file_count,
        'projected_frontier_family_count': len(projected_next_frontier),
        'projected_frontier_handle_covered_count': projected_frontier_handle_covered_count,
        'projected_frontier_gap_count': projected_frontier_gap_count,
    }

    trimmed_family_names = {str(row['family']) for row in manifest_rows}
    projected_family_names = [str(row['family']) for row in projected_next_frontier]
    policy_checks = {
        'package_receipt_ready': bool(package_receipt.get('status_counts', {}).get('package_ready')),
        'manifest_receipt_ready': bool(manifest_receipt.get('status_counts', {}).get('ready_to_cite')),
        'semantic_handle_receipt_ready': bool(semantic_handle_receipt.get('status_counts', {}).get('ready_to_cite')),
        'trimmed_paths_nonempty': bool(trimmed_paths) or int(manifest_receipt.get('summary_metrics', {}).get('manifest_raw_bytes', 0)) == 0,
        'trimmed_paths_unique': len(trimmed_resolved) == len(trimmed_paths),
        'trimmed_paths_exist_under_reports': all(path.exists() and path.is_relative_to(REPORT_ROOT) for path in trimmed_paths),
        'trimmed_families_fully_removed': all(_family_name(path) not in trimmed_family_names for path in remaining_report_files),
        'projected_report_bucket_strictly_smaller': projected_report_bucket_raw_bytes < current_report_bucket_raw_bytes or (current_report_bucket_raw_bytes == 0 and projected_report_bucket_raw_bytes == 0),
        'projected_raw_tree_strictly_smaller': projected_raw_tree_bytes < current_raw_tree_bytes or (current_report_bucket_raw_bytes == 0 and projected_raw_tree_bytes == current_raw_tree_bytes),
        'projected_frontier_accounted_for': bool(projected_next_frontier) or projected_report_bucket_raw_bytes == 0,
        'projected_frontier_sorted_by_size': projected_family_names == [str(row['family']) for row in sorted(projected_next_frontier, key=lambda row: (-int(row['raw_bytes']), str(row['family'])))],
    }
    passed_check_count = sum(1 for value in policy_checks.values() if value)
    ready_to_cite = passed_check_count == len(policy_checks)

    top_projected = projected_next_frontier[0] if projected_next_frontier else None
    if projected_frontier_gap_count == 0:
        frontier_note = 'The projected second-wave frontier is already fully handle-covered, so future compaction can stay citation-first even after the first trim executes.'
        next_move = (
            ('No live exact-file compaction frontier remains on the current tree; keep the archive in its terminal citation-first posture unless a genuinely new retained report family is added.' if summary_metrics['trimmed_raw_bytes'] == 0 else 'Cite the manifest handles, remove the exact report paths in that manifest, then rebuild the hotspot/candidate/manifest stack on the trimmed tree; this rehearsal shows the projected second-wave frontier is already handle-covered.')
            if ready_to_cite
            else 'Do not execute the manifest yet; rebuild the package, semantic-handle, and manifest receipts until this rehearsal becomes ready to cite.'
        )
    else:
        frontier_note = f'The projected second-wave frontier would expose {projected_frontier_gap_count} family(s) with zero durable handles, so handle recovery should precede any real trim.'
        next_move = (
            'Before executing the current manifest, recover or mint durable handles for the projected zero-handle families surfaced here, then rerun the rehearsal so the second-wave frontier is citation-backed too.'
            if ready_to_cite
            else 'Do not execute the manifest yet; rebuild the package, semantic-handle, and manifest receipts until this rehearsal becomes ready to cite.'
        )

    headline_findings = [
        (f"A rehearsal of the current exact-file compaction manifest removes {summary_metrics['trimmed_file_count']} retained report files across {summary_metrics['trimmed_family_count']} families, reclaiming {summary_metrics['trimmed_raw_bytes']} raw bytes ({summary_metrics['trimmed_share_of_report_bucket_raw_bytes']} share of the reports bucket)." if trimmed_families else 'No live exact-file compaction manifest remains on the current tree; the measured report frontier is already empty.'),
        (
            f"If that first trim executed, the report bucket would fall from {current_report_bucket_raw_bytes} to {projected_report_bucket_raw_bytes} raw bytes and the leading remaining hotspot would become `{top_projected['family']}` at {top_projected['raw_bytes']} bytes."
            if top_projected
            else 'If that first trim executed, no projected next-frontier family was available.'
        ),
        frontier_note,
    ]

    return {
        'receipt_kind': 'archive_report_compaction_rehearsal_receipt',
        'receipt_version': '2026-03-17.archive_report_compaction_rehearsal_receipt.v1',
        'analysis_script': 'scripts/tools/build_archive_report_compaction_rehearsal_receipt.py',
        'package_receipt_path': _relativize(package_receipt_path),
        'package_receipt_sha256': _sha256_json(package_receipt),
        'compaction_manifest_receipt_path': _relativize(manifest_receipt_path),
        'compaction_manifest_receipt_sha256': _sha256_json(manifest_receipt),
        'semantic_handle_receipt_path': _relativize(semantic_handle_receipt_path),
        'semantic_handle_receipt_sha256': _sha256_json(semantic_handle_receipt),
        'measurement_scope': {
            'report_root': 'artifacts/reports',
            'projected_frontier_limit': PROJECTED_FRONTIER_LIMIT,
            'candidate_search_roots': [path.relative_to(ROOT).as_posix() for path in SEARCH_ROOTS],
            'excluded_handle_paths': sorted(EXCLUDED_HANDLE_PATHS),
            'primary_doc_paths': sorted(PRIMARY_DOC_PATHS),
        },
        'summary_metrics': summary_metrics,
        'trimmed_families': trimmed_families,
        'projected_next_frontier': projected_next_frontier,
        'policy_checks': policy_checks,
        'status_counts': {'passed_check_count': passed_check_count, 'total_check_count': len(policy_checks), 'ready_to_cite': ready_to_cite},
        'archive_posture': {
            'intended_retention_class': 'durable_compaction_rehearsal_receipt',
            'prefer_citation_over_recopy': True,
            'size_discipline_note': 'Carry one tiny compaction-rehearsal receipt so future byte-saving can preview the first exact-file trim and the next exposed hotspot frontier before any retained report paths are actually removed.',
        },
        'headline_findings': headline_findings,
        'recommended_next_move': next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact rehearsal receipt that previews the outcome of applying the current exact-file compaction manifest before any retained report paths are removed.')
    parser.add_argument('--package-receipt', default=str(DEFAULT_PACKAGE_RECEIPT))
    parser.add_argument('--manifest-receipt', default=str(DEFAULT_MANIFEST_RECEIPT))
    parser.add_argument('--semantic-handle-receipt', default=str(DEFAULT_SEMANTIC_HANDLE_RECEIPT))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    receipt = build_receipt(
        package_receipt=load_json(Path(args.package_receipt)),
        package_receipt_path=Path(args.package_receipt),
        manifest_receipt=load_json(Path(args.manifest_receipt)),
        manifest_receipt_path=Path(args.manifest_receipt),
        semantic_handle_receipt=load_json(Path(args.semantic_handle_receipt)),
        semantic_handle_receipt_path=Path(args.semantic_handle_receipt),
    )
    output_path = Path(args.output)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return 0 if (not args.strict or receipt['status_counts']['ready_to_cite']) else 1


if __name__ == '__main__':
    raise SystemExit(main())

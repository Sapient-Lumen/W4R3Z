#!/usr/bin/env python3
"""Fail-closed archive budget and hygiene check."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT_RESEARCH_OBJECT_METADATA = {
    'CITATION.cff',
    'codemeta.json',
    'ro-crate-metadata.json',
    'LICENSE',
    'NOTICE',
    'release_provenance.intoto.jsonl',
}


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))


def extract_int_after_label(text: str, label: str) -> int | None:
    match = re.search(rf"^-\s*{re.escape(label)}:\s*([0-9]+)\s*$", text, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


TEXT_SCAN_SUFFIXES = {'.md', '.tex', '.json', '.py', '.cff', '.txt', '.bib'}
EVIDENCE_DEPENDENCY_PHRASES = [
    'available on request',
    'on request',
    'Figure omitted',
    'source-only',
]


def relpath(root: pathlib.Path, path: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def directory_hotspots(root: pathlib.Path, files: list[pathlib.Path], depth: int = 3, limit: int = 12) -> list[dict]:
    totals: dict[str, int] = {}
    for path in files:
        rel = relpath(root, path)
        parts = rel.split('/')
        for width in range(1, min(depth, len(parts)) + 1):
            key = '/'.join(parts[:width])
            if width < len(parts):
                key += '/'
            totals[key] = totals.get(key, 0) + path.stat().st_size
    return [
        {'path_prefix': key, 'bytes': value}
        for key, value in sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def file_hotspots(root: pathlib.Path, files: list[pathlib.Path], limit: int = 15) -> list[dict]:
    return [
        {'path': relpath(root, path), 'bytes': path.stat().st_size}
        for path in sorted(files, key=lambda p: (-p.stat().st_size, relpath(root, p)))[:limit]
    ]


def evidence_dependency_phrase_scan(root: pathlib.Path, files: list[pathlib.Path]) -> dict:
    totals = {phrase: {'occurrences': 0, 'files': 0} for phrase in EVIDENCE_DEPENDENCY_PHRASES}
    examples = {phrase: [] for phrase in EVIDENCE_DEPENDENCY_PHRASES}
    for path in files:
        if path.suffix not in TEXT_SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        for phrase in EVIDENCE_DEPENDENCY_PHRASES:
            count = text.count(phrase)
            if count:
                totals[phrase]['occurrences'] += count
                totals[phrase]['files'] += 1
                if len(examples[phrase]) < 8:
                    examples[phrase].append({'path': relpath(root, path), 'occurrences': count})
    return {'phrases': totals, 'examples': examples}


def worked_example_payload_pointer_summary(root: pathlib.Path) -> dict:
    manifest_path = root / 'series' / 'synthesis' / 'paper17_worked_example_receipt_interlock' / 'artifacts' / 'support_manifest.json'
    if not manifest_path.exists():
        return {'pointer_count': 0, 'logical_bytes': 0, 'payload_bytes': 0, 'pointer_hot_path_bytes_saved': 0}
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return {'pointer_count': 0, 'logical_bytes': 0, 'payload_bytes': 0, 'pointer_hot_path_bytes_saved': 0}
    rows = manifest.get('offloaded_payload_summary', []) if isinstance(manifest, dict) else []
    pointer_count = 0
    logical_bytes = 0
    payload_bytes = 0
    hot_path_saved = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        pointer_count += 1
        logical_bytes += int(row.get('logical_bytes') or 0)
        payload_bytes += int(row.get('payload_bytes') or 0)
        logical_path = row.get('logical_path')
        pointer_file = manifest_path.parent / str(logical_path)
        pointer_bytes = pointer_file.stat().st_size if pointer_file.exists() else 0
        hot_path_saved += max(0, int(row.get('logical_bytes') or 0) - pointer_bytes)
    return {
        'pointer_count': pointer_count,
        'logical_bytes': logical_bytes,
        'payload_bytes': payload_bytes,
        'pointer_hot_path_bytes_saved': hot_path_saved,
        'payload_storage_ratio': round(payload_bytes / logical_bytes, 6) if logical_bytes else 0.0,
    }


def check(root: pathlib.Path) -> dict:
    release = load_json(root / 'RELEASE_MANIFEST.json')
    policy = load_json(root / 'publishing' / 'archive_budget_policy.json')
    budget_md_path = root / 'publishing' / 'ARCHIVE_BUDGET.md'
    budget_md_text = budget_md_path.read_text(encoding='utf-8', errors='replace') if budget_md_path.exists() else ''
    files = [p for p in root.rglob('*') if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in files)
    file_count = len(files)
    root_file_count = len([p for p in root.iterdir() if p.is_file()])
    report_file_count = len([p for p in (root / 'reports').glob('*.json')])
    schema_file_count = len([p for p in (root / 'schemas').glob('*.schema.json')])
    root_research_metadata_count = len([p for p in root.iterdir() if p.is_file() and p.name in ROOT_RESEARCH_OBJECT_METADATA])
    forbidden_pattern = re.compile(policy['forbidden_series_render_dir_regex'])
    series_render_dirs = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob('*')
        if p.is_dir() and forbidden_pattern.match(p.relative_to(root).as_posix())
    )
    top_files = file_hotspots(root, files)
    top_dirs = directory_hotspots(root, files)
    evidence_phrase_scan = evidence_dependency_phrase_scan(root, files)
    paper17_dir = root / 'series' / 'synthesis' / 'paper17_worked_example_receipt_interlock'
    paper17_files = [p for p in paper17_dir.rglob('*') if p.is_file()] if paper17_dir.exists() else []
    paper17_total = sum(p.stat().st_size for p in paper17_files)
    paper17_pointer_summary = worked_example_payload_pointer_summary(root)
    decision_index_path = root / 'release_queue' / 'DECISION_INDEX.json'
    decision_index_bytes = decision_index_path.stat().st_size if decision_index_path.exists() else 0
    decision_index_obj = load_json(decision_index_path) if decision_index_path.exists() else {}
    decision_index_version = int(decision_index_obj.get('version', 0)) if isinstance(decision_index_obj, dict) else 0
    decision_index_baseline = int(policy.get('decision_index_rev0892_baseline_bytes', 0))
    decision_index_bytes_reclaimed = max(0, decision_index_baseline - decision_index_bytes) if decision_index_baseline else 0
    budget_headroom = {
        'file_count_headroom': policy['max_file_count'] - file_count,
        'root_file_count_headroom': policy['max_root_file_count'] - root_file_count,
        'report_file_count_headroom': policy['max_report_file_count'] - report_file_count,
        'schema_file_count_headroom': policy['max_schema_file_count'] - schema_file_count,
        'sprawl_risk': 'critical' if report_file_count >= policy['max_report_file_count'] or schema_file_count >= policy['max_schema_file_count'] or file_count >= policy['max_file_count'] - 2 else 'watch',
        'recommended_action': 'prefer modifying existing executable checks and generated surfaces; add files only for substantive decision/evidence changes while report/schema caps remain saturated',
    }
    hot_path_refactor_targets = [
        {
            'target': 'paper17_worked_example_payload',
            'path': 'series/synthesis/paper17_worked_example_receipt_interlock/',
            'bytes': paper17_total,
            'share_of_archive_bytes': round(paper17_total / total_bytes, 6) if total_bytes else 0.0,
            'offloaded_payload_pointer_summary': paper17_pointer_summary,
            'recommended_action': 'second cut is complete for seven large/risk-relevant Paper17 generated JSON artifacts via digest-bound gzip payload pointers; next consider only semantic duplication or optional-pack splitting, not blind report sprawl',
        },
        {
            'target': 'decision_index_hot_ledger',
            'path': 'release_queue/DECISION_INDEX.json',
            'bytes': decision_index_bytes,
            'share_of_archive_bytes': round(decision_index_bytes / total_bytes, 6) if total_bytes else 0.0,
            'sparse_index_version': decision_index_version,
            'rev0892_baseline_bytes': decision_index_baseline,
            'bytes_reclaimed_vs_rev0892': decision_index_bytes_reclaimed,
            'recommended_action': 'keep sparse v3 routing/classification rows; retain full prose in decision notes and full fidelity only for LATEST_DECISION.json',
        },
    ]
    checks = []

    def record(name: str, ok: bool, details: str):
        checks.append({'name': name, 'status': 'pass' if ok else 'fail', 'details': details})

    caps = policy.get('category_caps', {})
    record('total_bytes_within_budget', total_bytes <= policy['max_total_bytes'], f"bytes={total_bytes} max={policy['max_total_bytes']}")
    record('file_count_within_budget', file_count <= policy['max_file_count'], f"files={file_count} max={policy['max_file_count']}")
    record('root_file_count_within_budget', root_file_count <= policy['max_root_file_count'], f"root_files={root_file_count} max={policy['max_root_file_count']}")
    record('report_file_count_within_budget', report_file_count <= policy['max_report_file_count'], f"report_files={report_file_count} max={policy['max_report_file_count']}")
    record('schema_file_count_within_budget', schema_file_count <= policy['max_schema_file_count'], f"schema_files={schema_file_count} max={policy['max_schema_file_count']}")
    if 'machine_reports' in caps:
        record('machine_report_category_cap', report_file_count <= caps['machine_reports'], f"report_files={report_file_count} category_cap={caps['machine_reports']}")
    if 'json_schemas' in caps:
        record('json_schema_category_cap', schema_file_count <= caps['json_schemas'], f"schema_files={schema_file_count} category_cap={caps['json_schemas']}")
    if 'root_research_object_metadata' in caps:
        record('root_research_object_metadata_category_cap', root_research_metadata_count <= caps['root_research_object_metadata'], f"root_research_object_metadata_files={root_research_metadata_count} category_cap={caps['root_research_object_metadata']}")
    if 'transient_files' in caps:
        # Detailed transient file detection lives in check_transient_surface.py; this cap records the intended zero budget.
        record('transient_category_cap_declared_zero', caps['transient_files'] == 0, f"transient_category_cap={caps['transient_files']} expected=0")
    advertised_caps = {
        'Max total bytes': policy['max_total_bytes'],
        'Max total files': policy['max_file_count'],
        'Max root files': policy['max_root_file_count'],
        'Max report files': policy['max_report_file_count'],
        'Max schema files': policy['max_schema_file_count'],
        'Disallowed transient files': caps.get('transient_files'),
    }
    advertised_failures = []
    for label, expected in advertised_caps.items():
        actual = extract_int_after_label(budget_md_text, label)
        if actual != expected:
            advertised_failures.append({'label': label, 'actual': actual, 'expected': expected})
    record('human_archive_budget_surface_matches_policy', not advertised_failures, f"failures={advertised_failures}")
    record('no_series_render_dirs_shipped', not series_render_dirs, 'series_render_dirs=' + (', '.join(series_render_dirs) if series_render_dirs else 'none'))
    record('hotspot_waste_map_present', bool(top_files and top_dirs), f"top_files={len(top_files)} top_dirs={len(top_dirs)} paper17_bytes={paper17_total} decision_index_bytes={decision_index_bytes}")
    record('budget_headroom_reported', all(key in budget_headroom for key in ['file_count_headroom', 'report_file_count_headroom', 'schema_file_count_headroom', 'sprawl_risk']), f"headroom={budget_headroom}")

    failed = [c for c in checks if c['status'] == 'fail']
    return {
        'status': 'pass' if not failed else 'fail',
        'generated_for_revision': release['revision'],
        'checked_bundle': release['bundle'],
        'publication_authorized': False,
        'checked_root': '.',
        'policy_path': 'publishing/archive_budget_policy.json',
        'checks': checks,
        'summary': {
            'checks_passed': len(checks) - len(failed),
            'checks_failed': len(failed),
            'bytes': total_bytes,
            'file_count': file_count,
            'root_file_count': root_file_count,
            'report_file_count': report_file_count,
            'schema_file_count': schema_file_count,
            'root_research_object_metadata_file_count': root_research_metadata_count,
            'series_render_dir_count': len(series_render_dirs),
            'category_caps': caps,
            'paper17_worked_example_bytes': paper17_total,
            'paper17_payload_pointer_count': paper17_pointer_summary.get('pointer_count', 0),
            'paper17_payload_pointer_logical_bytes': paper17_pointer_summary.get('logical_bytes', 0),
            'paper17_payload_pointer_storage_bytes': paper17_pointer_summary.get('payload_bytes', 0),
            'paper17_payload_pointer_hot_path_bytes_saved': paper17_pointer_summary.get('pointer_hot_path_bytes_saved', 0),
            'decision_index_bytes': decision_index_bytes,
            'decision_index_version': decision_index_version,
            'decision_index_bytes_reclaimed_vs_rev0892': decision_index_bytes_reclaimed,
            'file_count_headroom': budget_headroom['file_count_headroom'],
            'root_file_count_headroom': budget_headroom['root_file_count_headroom'],
            'report_file_count_headroom': budget_headroom['report_file_count_headroom'],
            'schema_file_count_headroom': budget_headroom['schema_file_count_headroom'],
            'sprawl_risk': budget_headroom['sprawl_risk'],
        },
        'hotspots': {
            'top_files_by_bytes': top_files,
            'top_directory_prefixes_by_bytes': top_dirs,
            'hot_path_refactor_targets': hot_path_refactor_targets,
            'evidence_dependency_phrase_scan': evidence_phrase_scan,
            'budget_headroom': budget_headroom,
        },
        'fail_closed_rule': 'If this report fails, default to no publication and reduce archive sprawl, split artifact packs, or prune shipped review-render clutter before trusting the bundle.'
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--write-report', default='')
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_size_profile_snapshot_20260316.json'
OUT_MD = REPORTS / 'archive_size_profile_snapshot_20260316.md'
ARTIFACT_BUCKETS = ['timing', 'security', 'process', 'release', 'formal', 'reports']
SKIP_PARTS = {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
SKIP_SUFFIXES = {'.pyc', '.pyo'}
SELF_EXCLUDED_OUTPUTS = {OUT_JSON.resolve(), OUT_MD.resolve()}


def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        if path.name == '.gitkeep':
            continue
        if path.resolve() in SELF_EXCLUDED_OUTPUTS:
            continue
        files.append(path)
    return sorted(files)


def _zip_size(files: list[Path]) -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_zip = Path(tmpdir) / 'archive_size_profile_tmp.zip'
        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in files:
                zf.write(path, arcname=path.relative_to(ROOT).as_posix())
        return tmp_zip.stat().st_size


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def build_snapshot() -> dict[str, object]:
    files = _iter_files(ROOT)
    total_raw_bytes = sum(path.stat().st_size for path in files)
    zip_bytes = _zip_size(files)

    top_level_sizes: defaultdict[str, int] = defaultdict(int)
    for path in files:
        rel = path.relative_to(ROOT)
        top_level_sizes[rel.parts[0]] += path.stat().st_size

    bucket_rows: list[dict[str, object]] = []
    artifact_bytes_total = 0
    for bucket in ARTIFACT_BUCKETS:
        bucket_root = ROOT / 'artifacts' / bucket
        bucket_files = [path for path in files if path.is_relative_to(bucket_root)]
        bucket_bytes = sum(path.stat().st_size for path in bucket_files)
        artifact_bytes_total += bucket_bytes
        bucket_rows.append(
            {
                'bucket': bucket,
                'file_count': len(bucket_files),
                'raw_bytes': bucket_bytes,
                'raw_mebibytes': _mib(bucket_bytes),
            }
        )

    for row in bucket_rows:
        raw_bytes = int(row['raw_bytes'])
        row['share_of_total_raw_bytes'] = round(raw_bytes / total_raw_bytes, 6) if total_raw_bytes else 0.0
        row['share_of_artifact_raw_bytes'] = round(raw_bytes / artifact_bytes_total, 6) if artifact_bytes_total else 0.0

    report_root = ROOT / 'artifacts' / 'reports'
    report_files = [path for path in files if path.is_relative_to(report_root)]
    report_ext: defaultdict[str, dict[str, int]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0})
    pair_map: defaultdict[str, dict[str, int]] = defaultdict(dict)
    report_family_rows: defaultdict[str, dict[str, int]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0})

    for path in report_files:
        ext = path.suffix or '<none>'
        size = path.stat().st_size
        report_ext[ext]['file_count'] += 1
        report_ext[ext]['raw_bytes'] += size
        if path.suffix in {'.json', '.md'}:
            pair_map[str(path.with_suffix(''))][path.suffix] = size
        family = re.sub(r'_\d{8}$', '', path.stem)
        report_family_rows[family]['file_count'] += 1
        report_family_rows[family]['raw_bytes'] += size

    paired_count = 0
    json_only_count = 0
    md_only_count = 0
    pair_raw_bytes = 0
    for entry in pair_map.values():
        if '.json' in entry and '.md' in entry:
            paired_count += 1
            pair_raw_bytes += entry['.json'] + entry['.md']
        elif '.json' in entry:
            json_only_count += 1
        elif '.md' in entry:
            md_only_count += 1

    largest_files = [
        {
            'path': path.relative_to(ROOT).as_posix(),
            'raw_bytes': path.stat().st_size,
            'raw_mebibytes': _mib(path.stat().st_size),
        }
        for path in sorted(files, key=lambda p: (p.stat().st_size, p.relative_to(ROOT).as_posix()), reverse=True)[:15]
    ]

    largest_report_families = [
        {
            'family': family,
            'file_count': data['file_count'],
            'raw_bytes': data['raw_bytes'],
            'raw_mebibytes': _mib(data['raw_bytes']),
        }
        for family, data in sorted(
            report_family_rows.items(),
            key=lambda item: (item[1]['raw_bytes'], item[0]),
            reverse=True,
        )[:15]
    ]

    compaction_reference_path = ROOT / 'artifacts' / 'process' / 'archive_compaction_20260306.json'
    compaction_reference: dict[str, object] | None = None
    if compaction_reference_path.exists():
        compaction_reference = json.loads(compaction_reference_path.read_text(encoding='utf-8'))

    report_bucket_bytes = next(row['raw_bytes'] for row in bucket_rows if row['bucket'] == 'reports')
    pair_share_of_report_bytes = round(pair_raw_bytes / report_bucket_bytes, 6) if report_bucket_bytes else 0.0
    top_file = largest_files[0]

    findings = [
        (
            f"The archive currently holds {len(files)} retained files at {total_raw_bytes} raw bytes "
            f"({_mib(total_raw_bytes)} MiB) and compresses to about {zip_bytes} bytes ({_mib(zip_bytes)} MiB) in a revision zip."
        ),
        (
            f"The `artifacts/reports` bucket is the main retained growth surface at {report_bucket_bytes} raw bytes "
            f"({_mib(report_bucket_bytes)} MiB), or {round(report_bucket_bytes / total_raw_bytes, 6)} share of the raw tree."
        ),
        (
            f"Report fanout is mostly duplicated presentation surfaces: {paired_count} JSON+MD report pairs consume {pair_raw_bytes} raw bytes "
            f"({_mib(pair_raw_bytes)} MiB), which is {pair_share_of_report_bytes} share of the reports bucket."
        ),
        (
            f"The largest retained file is `{top_file['path']}` at {top_file['raw_bytes']} bytes; the next two are `CHANGELOG.md` and `docs/AGENT_LOG.md`, "
            "so internal operational surfaces now matter more than literature blobs."
        ),
    ]
    if compaction_reference is not None:
        findings.append(
            (
                f"The prior PDF compaction removed {compaction_reference['removed_pdf_bytes']} bytes "
                f"({_mib(int(compaction_reference['removed_pdf_bytes']))} MiB), so the archive's next size risk is internal report/log fanout rather than external reading packs."
            )
        )

    recommendations = [
        'Keep external literature in citation-first mode and reacquire PDFs only as temporary scratch.',
        'Treat `artifacts/process/scratch_manifest.json` as the retained handoff index for any temporary scratch that survives a session boundary.',
        'When a pass does not create a standing contract or validator, prefer one canonical machine-readable artifact plus a short inheritor note over another large JSON+MD report pair.',
        'Refresh `artifact_summary.json` and `ARTIFACT_BUCKETS.md` after archive-shaping edits so future sessions can see footprint drift immediately.',
    ]

    snapshot: dict[str, object] = {
        'focus': 'measure the retained archive footprint so future inheritors can keep the archive citation-first and compact without losing reproducibility',
        'snapshot_date': '2026-03-16',
        'archive_totals': {
            'retained_file_count': len(files),
            'raw_bytes': total_raw_bytes,
            'raw_mebibytes': _mib(total_raw_bytes),
            'approx_revision_zip_bytes': zip_bytes,
            'approx_revision_zip_mebibytes': _mib(zip_bytes),
            'zip_share_of_raw': round(zip_bytes / total_raw_bytes, 6) if total_raw_bytes else 0.0,
        },
        'top_level_raw_bytes': [
            {
                'path': key,
                'raw_bytes': value,
                'raw_mebibytes': _mib(value),
                'share_of_total_raw_bytes': round(value / total_raw_bytes, 6) if total_raw_bytes else 0.0,
            }
            for key, value in sorted(top_level_sizes.items(), key=lambda item: (item[1], item[0]), reverse=True)
        ],
        'artifact_buckets': bucket_rows,
        'report_extension_breakdown': [
            {
                'extension': ext,
                'file_count': data['file_count'],
                'raw_bytes': data['raw_bytes'],
                'raw_mebibytes': _mib(data['raw_bytes']),
            }
            for ext, data in sorted(report_ext.items(), key=lambda item: (item[1]['raw_bytes'], item[0]), reverse=True)
        ],
        'report_pair_breakdown': {
            'json_md_pair_count': paired_count,
            'json_only_count': json_only_count,
            'md_only_count': md_only_count,
            'pair_raw_bytes': pair_raw_bytes,
            'pair_raw_mebibytes': _mib(pair_raw_bytes),
            'pair_share_of_report_bucket_raw_bytes': pair_share_of_report_bytes,
        },
        'largest_files': largest_files,
        'largest_report_families': largest_report_families,
        'historical_compaction_reference': compaction_reference,
        'headline_findings': findings,
        'recommendations': recommendations,
        'analysis_script': 'scripts/report/build_archive_size_profile_snapshot.py',
    }
    return snapshot


def _render_md(report: dict[str, object]) -> str:
    totals = report['archive_totals']
    pair_breakdown = report['report_pair_breakdown']
    lines: list[str] = []
    lines.append('# Archive size profile snapshot — 2026-03-16')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Archive totals')
    lines.append(
        f"- retained files: `{totals['retained_file_count']}`; raw footprint: `{totals['raw_bytes']}` bytes (`{totals['raw_mebibytes']}` MiB); "
        f"approx revision zip: `{totals['approx_revision_zip_bytes']}` bytes (`{totals['approx_revision_zip_mebibytes']}` MiB)."
    )
    lines.append('')
    lines.append('## Artifact buckets')
    lines.append('| bucket | files | raw bytes | raw MiB | share of raw tree |')
    lines.append('|---|---:|---:|---:|---:|')
    for row in report['artifact_buckets']:
        lines.append(
            f"| {row['bucket']} | {row['file_count']} | {row['raw_bytes']} | {row['raw_mebibytes']} | {row['share_of_total_raw_bytes']} |"
        )
    lines.append('')
    lines.append('## Report fanout')
    lines.append(
        f"- JSON+MD pairs: `{pair_breakdown['json_md_pair_count']}`; pair bytes: `{pair_breakdown['pair_raw_bytes']}`; "
        f"pair share of report bucket: `{pair_breakdown['pair_share_of_report_bucket_raw_bytes']}`."
    )
    lines.append('')
    lines.append('## Largest retained files')
    for row in report['largest_files'][:10]:
        lines.append(f"- `{row['path']}` — `{row['raw_bytes']}` bytes (`{row['raw_mebibytes']}` MiB)")
    lines.append('')
    lines.append('## Largest report families')
    for row in report['largest_report_families'][:10]:
        lines.append(f"- `{row['family']}` — `{row['file_count']}` files, `{row['raw_bytes']}` bytes (`{row['raw_mebibytes']}` MiB)")
    lines.append('')
    lines.append('## Recommendations')
    for item in report['recommendations']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Source reports')
    if report['historical_compaction_reference'] is not None:
        lines.append("- `artifacts/process/archive_compaction_20260306.json`")
    lines.append(f"- `{report['analysis_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = build_snapshot()
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()

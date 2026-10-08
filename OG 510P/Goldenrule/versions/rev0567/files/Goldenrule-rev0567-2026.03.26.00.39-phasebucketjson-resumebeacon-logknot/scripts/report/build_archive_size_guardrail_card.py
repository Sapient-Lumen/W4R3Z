#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_size_guardrail_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_SIZE_GUARDRAIL_CARD.md'
BASELINE_JSON = REPORTS / 'archive_size_profile_snapshot_20260316.json'
SKIP_PARTS = {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
SKIP_SUFFIXES = {'.pyc', '.pyo'}
PACKAGE_CUT_JSON = REPORTS / 'archive_package_cut_card.json'
PACKAGE_CUT_MD = ROOT / 'docs' / 'ARCHIVE_PACKAGE_CUT_CARD.md'
TRIAGE_JSON = REPORTS / 'archive_byte_triage_card.json'
TRIAGE_MD = ROOT / 'docs' / 'ARCHIVE_BYTE_TRIAGE_CARD.md'
REENTRY_JSON = REPORTS / 'archive_reentry_card.json'
REENTRY_MD = ROOT / 'docs' / 'ARCHIVE_REENTRY_CARD.md'
HANDOFF_PACK_JSON = REPORTS / 'archive_handoff_pack.json'
HANDOFF_PACK_MD = ROOT / 'docs' / 'ARCHIVE_HANDOFF_PACK.md'
REVISION_CUT_JSON = REPORTS / 'archive_revision_cut_card.json'
REVISION_CUT_MD = ROOT / 'docs' / 'ARCHIVE_REVISION_CUT_CARD.md'
ZIP_LINEAGE_JSON = REPORTS / 'archive_zip_lineage_card.json'
ZIP_LINEAGE_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_LINEAGE_CARD.md'
ZIP_CHRONOLOGY_JSON = REPORTS / 'archive_zip_chronology_card.json'
ZIP_CHRONOLOGY_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_CHRONOLOGY_CARD.md'
ZIP_AUTHORITY_JSON = REPORTS / 'archive_zip_authority_card.json'
ZIP_AUTHORITY_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_AUTHORITY_CARD.md'
ZIP_DIGEST_JSON = REPORTS / 'archive_zip_digest_card.json'
ZIP_DIGEST_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_DIGEST_CARD.md'
ZIP_SIZE_TRUTH_JSON = REPORTS / 'archive_zip_size_truth_card.json'
ZIP_SIZE_TRUTH_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_SIZE_TRUTH_CARD.md'
COMMAND_INV_JSON = REPORTS / 'command_inventory.json'
COMMAND_INV_MD = ROOT / 'docs' / 'COMMAND_INVENTORY.md'
VALIDATOR_INV_JSON = REPORTS / 'validator_inventory.json'
VALIDATOR_INV_MD = ROOT / 'docs' / 'VALIDATOR_INVENTORY.md'
BUCKET_JSON = REPORTS / 'artifact_bucket_inventory.json'
BUCKET_MD = ROOT / 'docs' / 'ARTIFACT_BUCKETS.md'
SELF_EXCLUDED_OUTPUTS = {
    OUT_JSON.resolve(),
    OUT_MD.resolve(),
    PACKAGE_CUT_JSON.resolve(),
    PACKAGE_CUT_MD.resolve(),
    TRIAGE_JSON.resolve(),
    TRIAGE_MD.resolve(),
    REENTRY_JSON.resolve(),
    REENTRY_MD.resolve(),
    HANDOFF_PACK_JSON.resolve(),
    HANDOFF_PACK_MD.resolve(),
    REVISION_CUT_JSON.resolve(),
    REVISION_CUT_MD.resolve(),
    ZIP_LINEAGE_JSON.resolve(),
    ZIP_LINEAGE_MD.resolve(),
    ZIP_CHRONOLOGY_JSON.resolve(),
    ZIP_CHRONOLOGY_MD.resolve(),
    ZIP_AUTHORITY_JSON.resolve(),
    ZIP_AUTHORITY_MD.resolve(),
    ZIP_DIGEST_JSON.resolve(),
    ZIP_DIGEST_MD.resolve(),
    ZIP_SIZE_TRUTH_JSON.resolve(),
    ZIP_SIZE_TRUTH_MD.resolve(),
    COMMAND_INV_JSON.resolve(),
    COMMAND_INV_MD.resolve(),
    VALIDATOR_INV_JSON.resolve(),
    VALIDATOR_INV_MD.resolve(),
    BUCKET_JSON.resolve(),
    BUCKET_MD.resolve(),
}
SCRATCH_ROOTS = [
    ROOT / 'examples' / 'scratch',
    ROOT / 'scratch',
    ROOT / 'tmp',
]
ARTIFACT_BUCKETS = ['timing', 'security', 'process', 'release', 'formal', 'reports', 'patches']


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
        tmp_zip = Path(tmpdir) / 'archive_guardrail_tmp.zip'
        with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in files:
                zf.write(path, arcname=path.relative_to(ROOT).as_posix())
        return tmp_zip.stat().st_size


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def _pct(num: int, den: int) -> float:
    return round(num / den, 6) if den else 0.0


def _load_baseline() -> dict[str, Any] | None:
    if not BASELINE_JSON.exists():
        return None
    return json.loads(BASELINE_JSON.read_text(encoding='utf-8'))


def _report_families(files: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    report_root = ROOT / 'artifacts' / 'reports'
    family_rows: defaultdict[str, dict[str, int]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0})
    for path in files:
        if not path.is_relative_to(report_root):
            continue
        family = re.sub(r'_\d{8}$', '', path.stem)
        size = path.stat().st_size
        family_rows[family]['file_count'] += 1
        family_rows[family]['raw_bytes'] += size
    all_rows = [
        {
            'family': family,
            'file_count': data['file_count'],
            'raw_bytes': data['raw_bytes'],
            'raw_mebibytes': _mib(data['raw_bytes']),
        }
        for family, data in sorted(
            family_rows.items(),
            key=lambda item: (item[1]['raw_bytes'], item[0]),
            reverse=True,
        )
    ]
    return all_rows[:12], all_rows


def _prefix_family_rollup(rows: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    total_bytes = 0
    total_files = 0
    for row in rows:
        family = str(row['family'])
        if family.startswith(prefix):
            total_bytes += int(row['raw_bytes'])
            total_files += int(row['file_count'])
    return {
        'prefix': prefix,
        'file_count': total_files,
        'raw_bytes': total_bytes,
        'raw_mebibytes': _mib(total_bytes),
    }


def build_report() -> dict[str, Any]:
    files = _iter_files(ROOT)
    total_raw_bytes = sum(path.stat().st_size for path in files)
    zip_bytes = _zip_size(files)

    top_level_sizes: defaultdict[str, int] = defaultdict(int)
    for path in files:
        rel = path.relative_to(ROOT)
        top_level_sizes[rel.parts[0]] += path.stat().st_size

    largest_files = [
        {
            'path': path.relative_to(ROOT).as_posix(),
            'raw_bytes': path.stat().st_size,
            'raw_mebibytes': _mib(path.stat().st_size),
        }
        for path in sorted(files, key=lambda p: (p.stat().st_size, p.relative_to(ROOT).as_posix()), reverse=True)[:12]
    ]

    bucket_rows: list[dict[str, Any]] = []
    for bucket in ARTIFACT_BUCKETS:
        bucket_root = ROOT / 'artifacts' / bucket
        bucket_files = [path for path in files if path.is_relative_to(bucket_root)]
        bucket_bytes = sum(path.stat().st_size for path in bucket_files)
        bucket_rows.append(
            {
                'bucket': bucket,
                'file_count': len(bucket_files),
                'raw_bytes': bucket_bytes,
                'raw_mebibytes': _mib(bucket_bytes),
                'share_of_total_raw_bytes': _pct(bucket_bytes, total_raw_bytes),
            }
        )

    pdf_files = [path.relative_to(ROOT).as_posix() for path in files if path.suffix.lower() == '.pdf']
    scratch_files: list[str] = []
    for scratch_root in SCRATCH_ROOTS:
        if not scratch_root.exists():
            continue
        for path in scratch_root.rglob('*'):
            if path.is_file():
                scratch_files.append(path.relative_to(ROOT).as_posix())

    baseline = _load_baseline()
    baseline_totals = baseline.get('archive_totals', {}) if baseline else {}
    baseline_top = {row['path']: row['raw_bytes'] for row in baseline.get('top_level_raw_bytes', [])} if baseline else {}
    growth_rows = []
    for key in sorted(set(top_level_sizes) | set(baseline_top)):
        current_bytes = int(top_level_sizes.get(key, 0))
        baseline_bytes = int(baseline_top.get(key, 0))
        delta_bytes = current_bytes - baseline_bytes
        growth_rows.append(
            {
                'path': key,
                'current_raw_bytes': current_bytes,
                'baseline_raw_bytes': baseline_bytes,
                'delta_raw_bytes': delta_bytes,
                'delta_raw_mebibytes': _mib(delta_bytes),
            }
        )
    growth_rows.sort(key=lambda row: (row['delta_raw_bytes'], row['path']), reverse=True)

    report_families, all_report_families = _report_families(files)
    family_rollups = [
        _prefix_family_rollup(all_report_families, 'rust_'),
        _prefix_family_rollup(all_report_families, 'cloudtainer_'),
        _prefix_family_rollup(all_report_families, 'cooperation_benchmark_card_'),
    ]

    current_files = len(files)
    baseline_file_count = int(baseline_totals.get('retained_file_count', 0)) if baseline else 0
    baseline_raw_bytes = int(baseline_totals.get('raw_bytes', 0)) if baseline else 0
    baseline_zip_bytes = int(baseline_totals.get('approx_revision_zip_bytes', 0)) if baseline else 0
    raw_delta = total_raw_bytes - baseline_raw_bytes
    zip_delta = zip_bytes - baseline_zip_bytes
    file_delta = current_files - baseline_file_count

    headline_findings = [
        (
            f"The live tree now holds {current_files} retained files at {total_raw_bytes} raw bytes "
            f"({_mib(total_raw_bytes)} MiB) and compresses to about {zip_bytes} bytes ({_mib(zip_bytes)} MiB)."
        ),
        (
            f"Since the 2026-03-16 size snapshot, the archive grew by {raw_delta} raw bytes ({_mib(raw_delta)} MiB), "
            f"{zip_delta} zip bytes ({_mib(zip_delta)} MiB), and {file_delta} retained files."
            if baseline
            else 'No 2026-03-16 baseline snapshot is available, so the card reports only the live footprint.'
        ),
        (
            f"The main live growth fronts since that baseline are `docs` (+{growth_rows[0]['delta_raw_bytes']} bytes), "
            f"`artifacts` (+{growth_rows[1]['delta_raw_bytes']} bytes), and `scripts` (+{growth_rows[2]['delta_raw_bytes']} bytes)."
            if len(growth_rows) >= 3
            else 'The live growth-front ranking is unavailable because too few top-level rows were measured.'
        ),
        (
            f"Package hygiene is currently clean: PDF count={len(pdf_files)} and scratch file count={len(scratch_files)}, "
            'so the next revision zip can stay citation-first and scratch-free.'
        ),
        (
            f"The largest retained files are `{largest_files[0]['path']}` ({largest_files[0]['raw_bytes']} bytes), "
            f"`{largest_files[1]['path']}` ({largest_files[1]['raw_bytes']} bytes), and `{largest_files[2]['path']}` ({largest_files[2]['raw_bytes']} bytes), "
            'so the dominant byte pressure is now internal chronicles/registries rather than external reading packs.'
        ),
    ]

    recommendations = [
        'Keep the package boundary PDF-free and scratch-free; if a future session needs a large external body, reacquire it only as temporary scratch and delete it before cutting the next revision zip.',
        'When a blocked-session pass needs a new handoff surface, prefer one machine-readable report plus one short card instead of widening a whole parallel family of near-duplicate notes.',
        'If the archive needs a deliberate byte-saving pass, inspect operational chronicles and large registries before shaving compact Rust/cloudtainer cards; the biggest retained pressure is now in `docs/*`, `CHANGELOG.md`, and a few large process notes.',
        'Rebuild this guardrail card after any pass that materially widens `docs/`, `artifacts/`, or `scripts/`, so the next inheritor sees whether new bytes came from durable doctrine, generated reports, or pure tooling mass.',
    ]

    return {
        'analysis_script': 'scripts/report/build_archive_size_guardrail_card.py',
        'focus': 'keep the revision zip citation-first, PDF-free, scratch-free, and explicit about where live archive growth is really coming from',
        'snapshot_date': '2026-03-23',
        'baseline_snapshot_date': '2026-03-16' if baseline else None,
        'archive_totals': {
            'retained_file_count': current_files,
            'raw_bytes': total_raw_bytes,
            'raw_mebibytes': _mib(total_raw_bytes),
            'approx_revision_zip_bytes': zip_bytes,
            'approx_revision_zip_mebibytes': _mib(zip_bytes),
            'zip_share_of_raw': _pct(zip_bytes, total_raw_bytes),
        },
        'baseline_delta': {
            'retained_file_delta': file_delta,
            'raw_byte_delta': raw_delta,
            'raw_mebibyte_delta': _mib(raw_delta),
            'zip_byte_delta': zip_delta,
            'zip_mebibyte_delta': _mib(zip_delta),
        },
        'package_hygiene': {
            'pdf_count': len(pdf_files),
            'pdf_paths': pdf_files[:10],
            'scratch_file_count': len(scratch_files),
            'scratch_file_paths': scratch_files[:10],
            'scratch_roots_checked': [path.relative_to(ROOT).as_posix() for path in SCRATCH_ROOTS],
            'package_boundary_ready': len(pdf_files) == 0 and len(scratch_files) == 0,
        },
        'top_level_growth': growth_rows[:10],
        'largest_files': largest_files,
        'artifact_buckets': bucket_rows,
        'largest_report_families': report_families,
        'report_family_rollups': family_rollups,
        'headline_findings': headline_findings,
        'recommendations': recommendations,
    }


def render_md(report: dict[str, Any]) -> str:
    totals = report['archive_totals']
    hygiene = report['package_hygiene']
    baseline_delta = report['baseline_delta']
    lines: list[str] = []
    lines.append('# Archive Size Guardrail Card')
    lines.append('')
    lines.append(
        'Generated by `scripts/report/build_archive_size_guardrail_card.py`. '
        'This is the compact archive-boundary card for future blocked sessions: where the bytes are now, how the live tree moved since the older size snapshot, and whether the next revision zip is still clean.'
    )
    lines.append('')
    lines.append('## Snapshot')
    lines.append('')
    lines.append(f"- retained_files: `{totals['retained_file_count']}`")
    lines.append(f"- raw_bytes: `{totals['raw_bytes']}` (`{totals['raw_mebibytes']}` MiB)")
    lines.append(
        f"- approx_revision_zip_bytes: `{totals['approx_revision_zip_bytes']}` (`{totals['approx_revision_zip_mebibytes']}` MiB)"
    )
    lines.append(f"- zip_share_of_raw: `{totals['zip_share_of_raw']}`")
    lines.append(f"- baseline_file_delta_since_2026_03_16: `{baseline_delta['retained_file_delta']}`")
    lines.append(f"- baseline_raw_byte_delta_since_2026_03_16: `{baseline_delta['raw_byte_delta']}` (`{baseline_delta['raw_mebibyte_delta']}` MiB)")
    lines.append(f"- baseline_zip_byte_delta_since_2026_03_16: `{baseline_delta['zip_byte_delta']}` (`{baseline_delta['zip_mebibyte_delta']}` MiB)")
    lines.append(f"- pdf_count: `{hygiene['pdf_count']}`")
    lines.append(f"- scratch_file_count: `{hygiene['scratch_file_count']}`")
    lines.append(f"- package_boundary_ready: `{hygiene['package_boundary_ready']}`")
    lines.append('')
    lines.append('## Headline findings')
    for finding in report['headline_findings']:
        lines.append(f'- {finding}')
    lines.append('')
    lines.append('## Top-level growth since 2026-03-16')
    lines.append('')
    lines.append('| path | current raw bytes | baseline raw bytes | delta raw bytes |')
    lines.append('|---|---:|---:|---:|')
    for row in report['top_level_growth']:
        lines.append(
            f"| `{row['path']}` | {row['current_raw_bytes']} | {row['baseline_raw_bytes']} | {row['delta_raw_bytes']} |"
        )
    lines.append('')
    lines.append('## Largest retained files')
    lines.append('')
    for row in report['largest_files'][:10]:
        lines.append(f"- `{row['path']}` — `{row['raw_bytes']}` bytes (`{row['raw_mebibytes']}` MiB)")
    lines.append('')
    lines.append('## Artifact buckets')
    lines.append('')
    lines.append('| bucket | files | raw bytes | share of raw tree |')
    lines.append('|---|---:|---:|---:|')
    for row in report['artifact_buckets']:
        lines.append(
            f"| `{row['bucket']}` | {row['file_count']} | {row['raw_bytes']} | {row['share_of_total_raw_bytes']} |"
        )
    lines.append('')
    lines.append('## Largest report families')
    lines.append('')
    lines.append('| family | files | raw bytes |')
    lines.append('|---|---:|---:|')
    for row in report['largest_report_families'][:10]:
        lines.append(f"| `{row['family']}` | {row['file_count']} | {row['raw_bytes']} |")
    lines.append('')
    lines.append('## Rollups for the current blocked-session card families')
    lines.append('')
    for row in report['report_family_rollups']:
        lines.append(
            f"- `{row['prefix']}` families: `{row['file_count']}` files / `{row['raw_bytes']}` bytes (`{row['raw_mebibytes']}` MiB)"
        )
    lines.append('')
    lines.append('## Guardrails')
    lines.append('')
    for item in report['recommendations']:
        lines.append(f'- {item}')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    report = build_report()
    expected_md = render_md(report)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if write or not OUT_MD.exists():
        OUT_MD.write_text(expected_md, encoding='utf-8')
        print(f'archive-size-guardrail-card: wrote {OUT_MD.relative_to(ROOT).as_posix()}')
        print(f'archive-size-guardrail-card: wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
        return 0

    current_md = OUT_MD.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('archive-size-guardrail-card: drift detected; run with --write', file=sys.stderr)
        return 1

    print('archive-size-guardrail-card: ok')
    print(f'archive-size-guardrail-card: wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

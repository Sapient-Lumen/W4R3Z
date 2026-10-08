#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_byte_triage_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_BYTE_TRIAGE_CARD.md'
GUARDRAIL_JSON = REPORTS / 'archive_size_guardrail_card.json'
COMPACTION_CAP_BYTES = 128 * 1024
SOFT_REVIEW_THRESHOLD_BYTES = 64 * 1024
PACKAGE_CUT_JSON = REPORTS / 'archive_package_cut_card.json'
PACKAGE_CUT_MD = ROOT / 'docs' / 'ARCHIVE_PACKAGE_CUT_CARD.md'
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
ARCHIVE_SIZE_STACK = {
    'docs/ARCHIVE_SIZE_GUARDRAIL_CARD.md',
    'artifacts/reports/archive_size_guardrail_card.json',
    'scripts/report/build_archive_size_guardrail_card.py',
    'scripts/test/check_archive_size_guardrail_card.py',
}
ARCHIVE_PACKAGE_CUT_STACK = {
    'scripts/report/build_archive_package_cut_card.py',
    'scripts/test/check_archive_package_cut_card.py',
}
ARCHIVE_HANDOFF_PACK_STACK = {
    'scripts/report/build_archive_handoff_pack.py',
    'scripts/test/check_archive_handoff_pack.py',
    'scripts/tools/verify_archive_handoff_pack.py',
    'scripts/test/check_archive_handoff_pack_verify_tool.py',
}
ARCHIVE_REVISION_CUT_STACK = {
    'scripts/tools/plan_archive_revision_cut.py',
    'scripts/report/build_archive_revision_cut_card.py',
    'scripts/test/check_archive_revision_cut_card.py',
}
ARCHIVE_ZIP_LINEAGE_STACK = {
    'scripts/tools/audit_archive_zip_lineage.py',
    'scripts/report/build_archive_zip_lineage_card.py',
    'scripts/test/check_archive_zip_lineage_card.py',
}
ARCHIVE_ZIP_CHRONOLOGY_STACK = {
    'scripts/tools/audit_archive_zip_chronology.py',
    'scripts/report/build_archive_zip_chronology_card.py',
    'scripts/test/check_archive_zip_chronology_card.py',
    'scripts/tools/resolve_authoritative_archive_zip.py',
    'scripts/report/build_archive_zip_authority_card.py',
    'scripts/test/check_archive_zip_authority_card.py',
}
ARCHIVE_ZIP_DIGEST_STACK = {
    'scripts/tools/inspect_authoritative_archive_zip.py',
    'scripts/report/build_archive_zip_digest_card.py',
    'scripts/test/check_archive_zip_digest_card.py',
}
ARCHIVE_ZIP_SIZE_TRUTH_STACK = {
    'scripts/report/build_archive_zip_size_truth_card.py',
    'scripts/test/check_archive_zip_size_truth_card.py',
}


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        if path.name == '.gitkeep':
            continue
        rel = path.relative_to(ROOT)
        if any(part in {'.git', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'} for part in rel.parts):
            continue
        if path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.resolve() in SELF_EXCLUDED_OUTPUTS:
            continue
        files.append(path)
    return sorted(files)


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def _pct(num: int, den: int) -> float:
    return round(num / den, 6) if den else 0.0


def _load_guardrail() -> dict[str, Any]:
    if not GUARDRAIL_JSON.exists():
        raise FileNotFoundError(
            'missing artifacts/reports/archive_size_guardrail_card.json; run scripts/report/build_archive_size_guardrail_card.py first'
        )
    return json.loads(GUARDRAIL_JSON.read_text(encoding='utf-8'))


def _protected_group(rel: str) -> str | None:
    if (
        rel.startswith('docs/RUST_')
        or rel.startswith('artifacts/reports/rust_')
        or rel.startswith('scripts/report/build_rust_')
        or rel.startswith('scripts/test/check_rust_')
    ):
        return 'rust_blocked_session_stack'
    if (
        rel.startswith('docs/CLOUDTAINER_')
        or rel.startswith('artifacts/reports/cloudtainer_')
        or rel.startswith('scripts/report/build_cloudtainer_')
        or rel.startswith('scripts/test/check_cloudtainer_')
    ):
        return 'cloudtainer_blocked_session_stack'
    if rel in ARCHIVE_SIZE_STACK:
        return 'archive_size_guardrail_stack'
    if rel in ARCHIVE_PACKAGE_CUT_STACK:
        return 'archive_package_cut_stack'
    if rel in ARCHIVE_HANDOFF_PACK_STACK:
        return 'archive_handoff_pack_stack'
    if rel in ARCHIVE_REVISION_CUT_STACK:
        return 'archive_revision_cut_stack'
    if rel in ARCHIVE_ZIP_LINEAGE_STACK:
        return 'archive_zip_lineage_stack'
    if rel in ARCHIVE_ZIP_CHRONOLOGY_STACK:
        return 'archive_zip_chronology_stack'
    if rel in ARCHIVE_ZIP_DIGEST_STACK:
        return 'archive_zip_digest_stack'
    if rel in ARCHIVE_ZIP_SIZE_TRUTH_STACK:
        return 'archive_zip_size_truth_stack'
    return None


def _candidate_class(rel: str) -> str:
    if rel in {'docs/AGENT_LOG.md', 'CHANGELOG.md'}:
        return 'chronicle'
    if rel == 'docs/RESEARCH_SOURCES.md':
        return 'registry'
    if rel.startswith('artifacts/process/'):
        return 'process_receipt'
    if rel.startswith('docs/LIBRARY/topics/'):
        return 'library_topic'
    if rel.startswith('docs/'):
        return 'doctrine'
    return 'other'


def build_report() -> dict[str, Any]:
    guardrail = _load_guardrail()
    raw_tree_bytes = int(guardrail['archive_totals']['raw_bytes'])
    package_ready = bool(guardrail['package_hygiene']['package_boundary_ready'])
    snapshot_date = str(guardrail.get('snapshot_date', '2026-03-23'))

    files = _iter_files()
    group_rows: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0, 'sample_paths': []})
    protected_paths: set[str] = set()
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        group = _protected_group(rel)
        if group is None:
            continue
        protected_paths.add(rel)
        group_rows[group]['file_count'] += 1
        group_rows[group]['raw_bytes'] += path.stat().st_size
        if len(group_rows[group]['sample_paths']) < 4:
            group_rows[group]['sample_paths'].append(rel)

    protected_groups = [
        {
            'group': group,
            'file_count': data['file_count'],
            'raw_bytes': data['raw_bytes'],
            'raw_mebibytes': _mib(data['raw_bytes']),
            'sample_paths': data['sample_paths'],
        }
        for group, data in sorted(group_rows.items(), key=lambda item: (item[1]['raw_bytes'], item[0]), reverse=True)
    ]
    protected_total_bytes = sum(row['raw_bytes'] for row in protected_groups)
    protected_total_files = sum(row['file_count'] for row in protected_groups)

    markdown_candidates: list[dict[str, Any]] = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel in protected_paths:
            continue
        if path.suffix.lower() != '.md':
            continue
        if not (rel == 'CHANGELOG.md' or rel.startswith('docs/') or rel.startswith('artifacts/process/')):
            continue
        size = path.stat().st_size
        markdown_candidates.append(
            {
                'path': rel,
                'kind': _candidate_class(rel),
                'raw_bytes': size,
                'raw_mebibytes': _mib(size),
                'overflow_above_128k_bytes': max(0, size - COMPACTION_CAP_BYTES),
            }
        )

    markdown_candidates.sort(key=lambda row: (row['raw_bytes'], row['path']), reverse=True)
    cap_first_pack = [row for row in markdown_candidates if row['raw_bytes'] > COMPACTION_CAP_BYTES]
    next_review_tier = [
        row for row in markdown_candidates if SOFT_REVIEW_THRESHOLD_BYTES < row['raw_bytes'] <= COMPACTION_CAP_BYTES
    ]

    cap_first_raw_bytes = sum(row['raw_bytes'] for row in cap_first_pack)
    cap_first_recoverable = sum(row['overflow_above_128k_bytes'] for row in cap_first_pack)

    headline_findings = [
        (
            f"The protected blocked-session handoff stack currently spans {protected_total_files} files and {protected_total_bytes} raw bytes "
            f"({_mib(protected_total_bytes)} MiB), only {_pct(protected_total_bytes, raw_tree_bytes)} of the live raw tree."
        ),
        (
            f"A four-file markdown compaction pack sits above the 128 KiB cap and would recover {cap_first_recoverable} bytes "
            f"({_mib(cap_first_recoverable)} MiB) if condensed to that cap without touching the protected Rust/cloudtainer/archive-size stack."
            if len(cap_first_pack) == 4
            else (
                f"The current cap-first markdown pack contains {len(cap_first_pack)} files above 128 KiB and would recover "
                f"{cap_first_recoverable} bytes ({_mib(cap_first_recoverable)} MiB) if condensed to that cap."
            )
        ),
        (
            f"That recoverable markdown overflow already exceeds the full protected handoff stack by a factor of "
            f"{round(cap_first_recoverable / protected_total_bytes, 3)}x."
            if protected_total_bytes
            else 'The protected handoff stack currently measures zero bytes, which indicates a reporting bug rather than a real archive state.'
        ),
        (
            f"The first trim-first pack is `{cap_first_pack[0]['path']}`, `{cap_first_pack[1]['path']}`, `{cap_first_pack[2]['path']}`, and `{cap_first_pack[3]['path']}`."
            if len(cap_first_pack) >= 4
            else 'Fewer than four markdown files currently exceed the 128 KiB cap, so the safe-first compaction pack is smaller than expected.'
        ),
        (
            f"After that cap-first pack, only {len(next_review_tier)} markdown docs remain between 64 KiB and 128 KiB, so a diet pass can stay narrow instead of broad-brushing the repo."
        ),
        (
            f"The package boundary remains ready according to the guardrail card (package_boundary_ready={package_ready}), so byte triage can focus on retained doctrine/chronicle mass instead of leaked PDFs or scratch."
        ),
    ]

    recommendations = [
        'Protect the blocked-session handoff stack first: all `docs/RUST_*`, `docs/CLOUDTAINER_*`, and `docs/ARCHIVE_SIZE_GUARDRAIL_CARD.md` surfaces plus their paired report/build/check files remain small enough that shaving them saves little and costs navigational clarity.',
        'If the archive needs a deliberate diet, start by condensing the cap-first markdown pack to a summary-plus-citation form before touching code, generated Rust maps, or small cloudtainer cards.',
        'Treat the 64 KiB to 128 KiB markdown tier as review-only, not automatic trim targets; those files are big enough to watch but not yet the dominant byte pressure.',
        'Refresh the guardrail card first and this byte-triage card second whenever inventories or large chronicles change, so the cap-first pack reflects the final post-edit tree rather than an intermediate state.',
    ]

    return {
        'analysis_script': 'scripts/report/build_archive_byte_triage_card.py',
        'focus': 'identify the safest byte-saving moves that preserve the compact blocked-session Rust/cloudtainer handoff stack',
        'snapshot_date': snapshot_date,
        'guardrail_reference': {
            'source_report': 'artifacts/reports/archive_size_guardrail_card.json',
            'archive_raw_bytes': raw_tree_bytes,
            'archive_raw_mebibytes': _mib(raw_tree_bytes),
            'package_boundary_ready': package_ready,
            'pdf_count': int(guardrail['package_hygiene']['pdf_count']),
            'scratch_file_count': int(guardrail['package_hygiene']['scratch_file_count']),
        },
        'protected_stack_groups': protected_groups,
        'protected_stack_totals': {
            'file_count': protected_total_files,
            'raw_bytes': protected_total_bytes,
            'raw_mebibytes': _mib(protected_total_bytes),
            'share_of_archive_raw_bytes': _pct(protected_total_bytes, raw_tree_bytes),
        },
        'cap_first_markdown_pack': cap_first_pack,
        'cap_first_markdown_pack_totals': {
            'file_count': len(cap_first_pack),
            'raw_bytes': cap_first_raw_bytes,
            'raw_mebibytes': _mib(cap_first_raw_bytes),
            'share_of_archive_raw_bytes': _pct(cap_first_raw_bytes, raw_tree_bytes),
            'recoverable_if_capped_at_128k_bytes': cap_first_recoverable,
            'recoverable_if_capped_at_128k_mebibytes': _mib(cap_first_recoverable),
            'recoverable_vs_protected_stack_ratio': round(cap_first_recoverable / protected_total_bytes, 3)
            if protected_total_bytes
            else 0.0,
        },
        'next_review_markdown_tier': next_review_tier,
        'next_review_markdown_tier_totals': {
            'file_count': len(next_review_tier),
            'raw_bytes': sum(row['raw_bytes'] for row in next_review_tier),
            'raw_mebibytes': _mib(sum(row['raw_bytes'] for row in next_review_tier)),
        },
        'headline_findings': headline_findings,
        'recommendations': recommendations,
    }


def render_md(report: dict[str, Any]) -> str:
    guardrail = report['guardrail_reference']
    protected = report['protected_stack_totals']
    cap_pack = report['cap_first_markdown_pack_totals']
    next_tier = report['next_review_markdown_tier_totals']

    lines: list[str] = []
    lines.append('# Archive Byte Triage Card')
    lines.append('')
    lines.append(
        'Generated by `scripts/report/build_archive_byte_triage_card.py`. This is the compact diet-pass card: what to protect, what to trim first, and how much markdown overflow can be reclaimed before touching the small blocked-session handoff stack.'
    )
    lines.append('')
    lines.append('## Snapshot')
    lines.append('')
    lines.append(f"- snapshot_date: `{report['snapshot_date']}`")
    lines.append(f"- guardrail_source: `{guardrail['source_report']}`")
    lines.append(f"- archive_raw_bytes: `{guardrail['archive_raw_bytes']}` (`{guardrail['archive_raw_mebibytes']}` MiB)")
    lines.append(f"- package_boundary_ready: `{guardrail['package_boundary_ready']}`")
    lines.append(f"- protected_stack_files: `{protected['file_count']}`")
    lines.append(f"- protected_stack_raw_bytes: `{protected['raw_bytes']}` (`{protected['raw_mebibytes']}` MiB)")
    lines.append(f"- cap_first_markdown_files: `{cap_pack['file_count']}`")
    lines.append(f"- cap_first_markdown_raw_bytes: `{cap_pack['raw_bytes']}` (`{cap_pack['raw_mebibytes']}` MiB)")
    lines.append(
        f"- recoverable_if_capped_at_128k_bytes: `{cap_pack['recoverable_if_capped_at_128k_bytes']}` (`{cap_pack['recoverable_if_capped_at_128k_mebibytes']}` MiB)"
    )
    lines.append(f"- next_review_markdown_files_64k_to_128k: `{next_tier['file_count']}`")
    lines.append('')
    lines.append('## Headline findings')
    for finding in report['headline_findings']:
        lines.append(f'- {finding}')
    lines.append('')
    lines.append('## Protected blocked-session handoff stack')
    lines.append('')
    lines.append('| group | files | raw bytes | sample paths |')
    lines.append('|---|---:|---:|---|')
    for row in report['protected_stack_groups']:
        sample = ', '.join(f"`{path}`" for path in row['sample_paths'])
        lines.append(f"| `{row['group']}` | {row['file_count']} | {row['raw_bytes']} | {sample} |")
    lines.append('')
    lines.append('## Cap-first markdown pack (>128 KiB)')
    lines.append('')
    lines.append('| path | class | raw bytes | overflow above 128 KiB |')
    lines.append('|---|---|---:|---:|')
    for row in report['cap_first_markdown_pack']:
        lines.append(
            f"| `{row['path']}` | `{row['kind']}` | {row['raw_bytes']} | {row['overflow_above_128k_bytes']} |"
        )
    lines.append('')
    lines.append('## Next markdown review tier (64 KiB to 128 KiB)')
    lines.append('')
    if report['next_review_markdown_tier']:
        lines.append('| path | class | raw bytes |')
        lines.append('|---|---|---:|')
        for row in report['next_review_markdown_tier']:
            lines.append(f"| `{row['path']}` | `{row['kind']}` | {row['raw_bytes']} |")
    else:
        lines.append('- No markdown files currently sit in the 64 KiB to 128 KiB review tier.')
    lines.append('')
    lines.append('## Guardrails')
    lines.append('')
    for item in report['recommendations']:
        lines.append(f'- {item}')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    try:
        report = build_report()
    except FileNotFoundError as exc:
        print(f'archive-byte-triage-card: {exc}', file=sys.stderr)
        return 1

    expected_md = render_md(report)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if write or not OUT_MD.exists():
        OUT_MD.write_text(expected_md, encoding='utf-8')
        print(f'archive-byte-triage-card: wrote {OUT_MD.relative_to(ROOT).as_posix()}')
        print(f'archive-byte-triage-card: wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
        return 0

    current_md = OUT_MD.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('archive-byte-triage-card: drift detected; run with --write', file=sys.stderr)
        return 1

    print('archive-byte-triage-card: ok')
    print(f'archive-byte-triage-card: wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

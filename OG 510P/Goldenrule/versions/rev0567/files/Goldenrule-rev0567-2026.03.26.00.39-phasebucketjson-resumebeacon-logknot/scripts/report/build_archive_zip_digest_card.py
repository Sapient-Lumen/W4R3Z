#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_zip_digest_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_DIGEST_CARD.md'

sys.path.insert(0, str(ROOT / 'scripts' / 'tools'))
from audit_archive_zip_lineage import _default_scan_dir
from inspect_authoritative_archive_zip import inspect_authoritative_archive_zip

DEFAULT_SCAN_DIR = _default_scan_dir()


def _bytes_to_mib(size_bytes: int) -> float:
    return size_bytes / (1024 * 1024)


def build_report(scan_dir: Path = DEFAULT_SCAN_DIR) -> dict[str, Any]:
    inspected = inspect_authoritative_archive_zip(scan_dir)
    selected_live = inspected['selected_zip']
    resolved = inspected['resolved']
    current_zip_name = f"{resolved['current_archive']['root_name']}.zip"

    if selected_live is None:
        selected = None
        headline = [
            f"No sibling Golden Rule revision zips were found in `{inspected['scan_dir']}`, so there is no authoritative zip verification target yet.",
            'Use the authority resolver first; this digest surface only applies once an authoritative external head exists.',
        ]
    else:
        matches_current_root_zip = selected_live['zip_name'] == current_zip_name
        selected = {
            'zip_name': selected_live['zip_name'],
            'zip_path': selected_live['zip_path'],
            'matches_current_root_zip': matches_current_root_zip,
            'embedded_digest_stable': not matches_current_root_zip,
            'embedded_size_bytes': None if matches_current_root_zip else selected_live['size_bytes'],
            'embedded_size_mib': None if matches_current_root_zip else round(_bytes_to_mib(selected_live['size_bytes']), 6),
            'embedded_sha256': None if matches_current_root_zip else selected_live['sha256'],
            'live_emit_sha256_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256',
            'live_emit_size_bytes_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes',
            'live_emit_zip_path_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit zip-path',
        }
        if matches_current_root_zip:
            headline = [
                f"The authoritative sibling zip remains the live current-root package `{selected['zip_name']}` at `{selected['zip_path']}`.",
                'Because this card is embedded inside that same current-head zip, a stable embedded size or SHA-256 would be self-referential and cannot be trusted as a fixed point.',
                f"Use `{selected['live_emit_size_bytes_command']}` and `{selected['live_emit_sha256_command']}` against the sibling zip on disk when you need the live bytes verified.",
                'For one-command winner verification, run `python3 scripts/tools/verify_authoritative_archive_zip.py`.',
            ]
        else:
            headline = [
                f"The authoritative sibling zip remains `{selected['zip_name']}` at `{selected['zip_path']}`.",
                f"Its embedded stable size is {selected['embedded_size_bytes']} bytes ({selected['embedded_size_mib']:.3f} MiB) and its embedded stable SHA-256 digest is `{selected['embedded_sha256']}`.",
                'This older sibling zip is no longer self-referential relative to the current root, so its digest can be embedded directly and rechecked later.',
            ]

    stewardship = {
        'primary_open_doc': 'docs/ARCHIVE_ZIP_DIGEST_CARD.md',
        'inspect_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py',
        'emit_sha256_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256',
        'emit_size_bytes_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes',
        'emit_zip_path_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit zip-path',
        'verify_zip_command': 'python3 scripts/tools/verify_authoritative_archive_zip.py',
        'selected_zip_name': None if selected is None else selected['zip_name'],
        'selected_zip_path': None if selected is None else selected['zip_path'],
    }
    return {
        'card': 'archive_zip_digest_card',
        'scan_dir': inspected['scan_dir'],
        'current_archive': resolved['current_archive'],
        'authoritative_external_head': resolved['authoritative_external_head'],
        'exact_current_zip_present': resolved['exact_current_zip_present'],
        'current_root_vs_authoritative_head_aligned': resolved['current_root_vs_authoritative_head_aligned'],
        'timestamp_head_matches_authoritative_head': resolved['timestamp_head_matches_authoritative_head'],
        'duplicate_revision_count': resolved['duplicate_revision_count'],
        'adjacent_revision_timestamp_inversion_count': resolved['adjacent_revision_timestamp_inversion_count'],
        'selected_zip': selected,
        'headline_findings': headline,
        'stewardship': stewardship,
        'metadata': {
            'source_tool': 'scripts/tools/inspect_authoritative_archive_zip.py',
            'source_scan_dir': inspected['scan_dir'],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        '# Archive Zip Digest Card',
        '',
        'Compact external-zip verification surface: once the authoritative sibling Golden Rule revision zip is known, publish either a stable embedded digest (for older sibling zips) or the exact live verification commands (for the current self-referential head zip).',
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend(['', '## Selected authoritative zip verification surface', ''])
    selected = report['selected_zip']
    if selected is None:
        lines.append(f"- No authoritative sibling zip is currently available in `{report['scan_dir']}`.")
    else:
        lines.extend([
            f"- selected_zip_name: `{selected['zip_name']}`",
            f"- selected_zip_path: `{selected['zip_path']}`",
            f"- matches_current_root_zip: `{selected['matches_current_root_zip']}`",
            f"- embedded_digest_stable: `{selected['embedded_digest_stable']}`",
        ])
        if selected['embedded_digest_stable']:
            lines.extend([
                f"- embedded_size_bytes: `{selected['embedded_size_bytes']}`",
                f"- embedded_size_mib: `{selected['embedded_size_mib']}`",
                f"- embedded_sha256: `{selected['embedded_sha256']}`",
            ])
        else:
            lines.extend([
                '- embedded_size_bytes: `None`',
                '- embedded_sha256: `None`',
                f"- live_emit_size_bytes_command: `{selected['live_emit_size_bytes_command']}`",
                f"- live_emit_sha256_command: `{selected['live_emit_sha256_command']}`",
                f"- verify_zip_command: `{report['stewardship']['verify_zip_command']}`",
            ])
        lines.extend([
            f"- exact_current_zip_present: `{report['exact_current_zip_present']}`",
            f"- current_root_vs_authoritative_head_aligned: `{report['current_root_vs_authoritative_head_aligned']}`",
            f"- timestamp_head_matches_authoritative_head: `{report['timestamp_head_matches_authoritative_head']}`",
            f"- duplicate_revision_count: `{report['duplicate_revision_count']}`",
            f"- adjacent_revision_timestamp_inversion_count: `{report['adjacent_revision_timestamp_inversion_count']}`",
        ])
    lines.extend([
        '',
        '## Stewardship',
        '',
        f"- open_doc: `{report['stewardship']['primary_open_doc']}`",
        f"- inspect_command: `{report['stewardship']['inspect_command']}`",
        f"- emit_sha256_command: `{report['stewardship']['emit_sha256_command']}`",
        f"- emit_size_bytes_command: `{report['stewardship']['emit_size_bytes_command']}`",
        f"- emit_zip_path_command: `{report['stewardship']['emit_zip_path_command']}`",
        f"- verify_zip_command: `{report['stewardship']['verify_zip_command']}`",
        '',
        '## Why this card exists',
        '',
        '- The archive already resolves which sibling zip should win authority, but an inheritor may still need an exact verification surface for the selected zip bytes.',
        '- Current-head zips are self-referential if they try to embed their own final digest inside themselves, so this card deliberately degrades to live verification commands in that case instead of pretending a false fixed point exists.',
        '- Older sibling zips do not have that self-reference problem, so their size and SHA-256 can still be embedded directly when they remain the authoritative external head.',
        '',
    ])
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the archive zip digest card.')
    parser.add_argument('--scan-dir', default=DEFAULT_SCAN_DIR.as_posix(), help='directory containing sibling Golden Rule revision zip files')
    args = parser.parse_args()
    scan_dir = Path(args.scan_dir).expanduser().resolve()
    report = build_report(scan_dir)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_markdown(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

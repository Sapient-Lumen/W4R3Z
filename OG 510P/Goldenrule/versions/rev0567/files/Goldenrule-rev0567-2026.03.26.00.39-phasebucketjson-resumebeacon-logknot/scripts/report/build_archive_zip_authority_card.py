#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_zip_authority_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_AUTHORITY_CARD.md'

sys.path.insert(0, str(ROOT / 'scripts' / 'tools'))
from audit_archive_zip_lineage import _default_scan_dir
from resolve_authoritative_archive_zip import resolve_authoritative_archive_zip

DEFAULT_SCAN_DIR = _default_scan_dir()


def build_report(scan_dir: Path = DEFAULT_SCAN_DIR) -> dict[str, Any]:
    resolved = resolve_authoritative_archive_zip(scan_dir)
    head = resolved['authoritative_external_head']
    predecessor = resolved['immediate_predecessor_zip']
    recommended = resolved['recommended_resume']
    if head is None:
        headline = [
            f"No sibling Golden Rule revision zips were found in `{resolved['scan_dir']}`, so there is no authoritative external zip to reopen yet.",
            f"The live root is still `{resolved['current_archive']['root_name']}`, but external zip authority cannot be re-derived from the package lane.",
        ]
    else:
        headline = [
            (
                f"The authoritative sibling zip to reopen is `{head['zip_name']}`, and its exact path is `{recommended['selected_zip_path']}`."
            ),
            (
                f"Archive head authority stays revision-first: `{resolved['authority_rule']}`; timestamp_head_matches_authoritative_head={resolved['timestamp_head_matches_authoritative_head']}."
            ),
            (
                f"Visible external hazards remain duplicate_revision_count={resolved['duplicate_revision_count']} and adjacent_revision_timestamp_inversion_count={resolved['adjacent_revision_timestamp_inversion_count']}, so stewards should not pick the reopen target by timestamp alone."
            ),
        ]
    stewardship = {
        'primary_open_doc': 'docs/ARCHIVE_ZIP_AUTHORITY_CARD.md',
        'resolve_command': 'python3 scripts/tools/resolve_authoritative_archive_zip.py',
        'emit_zip_path_command': 'python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path',
        'emit_unzip_command': 'python3 scripts/tools/resolve_authoritative_archive_zip.py --emit unzip-command',
        'selected_zip_name': recommended['selected_zip_name'],
        'selected_zip_path': recommended['selected_zip_path'],
        'resume_unzip_command': recommended['resume_unzip_command'],
    }
    return {
        'card': 'archive_zip_authority_card',
        'scan_dir': resolved['scan_dir'],
        'current_archive': resolved['current_archive'],
        'authoritative_external_head': head,
        'latest_by_timestamp': resolved['latest_by_timestamp'],
        'immediate_predecessor_zip': predecessor,
        'authority_rule': resolved['authority_rule'],
        'selection_trace': resolved['selection_trace'],
        'duplicate_revision_rows': resolved['duplicate_revision_rows'],
        'duplicate_revision_count': resolved['duplicate_revision_count'],
        'adjacent_revision_timestamp_inversions': resolved['adjacent_revision_timestamp_inversions'],
        'adjacent_revision_timestamp_inversion_count': resolved['adjacent_revision_timestamp_inversion_count'],
        'exact_current_zip_present': resolved['exact_current_zip_present'],
        'current_root_vs_authoritative_head_aligned': resolved['current_root_vs_authoritative_head_aligned'],
        'timestamp_head_matches_authoritative_head': resolved['timestamp_head_matches_authoritative_head'],
        'recommended_resume': recommended,
        'headline_findings': headline,
        'stewardship': stewardship,
        'metadata': {
            'source_tool': 'scripts/tools/resolve_authoritative_archive_zip.py',
            'source_scan_dir': resolved['scan_dir'],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    head = report['authoritative_external_head']
    predecessor = report['immediate_predecessor_zip']
    stewardship = report['stewardship']
    recommended = report['recommended_resume']
    lines: list[str] = [
        '# Archive Zip Authority Card',
        '',
        'Compact sibling-zip reopen surface: choose one authoritative external revision zip to reopen, even when revision labels are duplicated or timestamps do not stay monotone across revisions.',
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Selected authoritative zip',
        '',
    ])
    if head is None:
        lines.append(f"- No matching Golden Rule revision zips were found in `{report['scan_dir']}`.")
    else:
        lines.extend([
            f"- selected_zip_name: `{recommended['selected_zip_name']}`",
            f"- selected_zip_path: `{recommended['selected_zip_path']}`",
            f"- selected_root_stem: `{recommended['selected_root_stem']}`",
            f"- immediate_predecessor_zip: `{predecessor['zip_name'] if predecessor else 'none'}`",
            f"- current_root_vs_authoritative_head_aligned: `{report['current_root_vs_authoritative_head_aligned']}`",
            f"- exact_current_zip_present: `{report['exact_current_zip_present']}`",
        ])
    lines.extend([
        '',
        '## Resolution rule',
        '',
        f"- authority_rule: `{report['authority_rule']}`",
    ])
    for row in report['selection_trace']:
        lines.append(f'- {row}')
    lines.extend([
        '',
        '## Recommended reopen commands',
        '',
        f"- resolve_command: `{stewardship['resolve_command']}`",
        f"- emit_zip_path_command: `{stewardship['emit_zip_path_command']}`",
        f"- emit_unzip_command: `{stewardship['emit_unzip_command']}`",
        f"- resume_unzip_command: `{stewardship['resume_unzip_command']}`",
        '',
        '## Visible external hazards',
        '',
        f"- duplicate_revision_count: `{report['duplicate_revision_count']}`",
        f"- adjacent_revision_timestamp_inversion_count: `{report['adjacent_revision_timestamp_inversion_count']}`",
        f"- timestamp_head_matches_authoritative_head: `{report['timestamp_head_matches_authoritative_head']}`",
        '',
    ])
    if report['duplicate_revision_rows']:
        lines.append('### Duplicate revision rows')
        lines.append('')
        for row in report['duplicate_revision_rows']:
            joined = ', '.join(f"`{name}`" for name in row['zip_names'])
            lines.append(f"- `{row['revision_label']}` appears {row['count']} times: {joined}")
        lines.append('')
    if report['adjacent_revision_timestamp_inversions']:
        lines.append('### Adjacent revision/timestamp inversions')
        lines.append('')
        for row in report['adjacent_revision_timestamp_inversions']:
            lines.append(
                f"- `{row['previous_revision_label']}` @ `{row['previous_timestamp']}` precedes `{row['current_revision_label']}` @ `{row['current_timestamp']}` in revision order"
            )
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact archive zip authority card that resolves which sibling revision zip should be reopened.')
    parser.add_argument('--write', action='store_true', help='write the JSON report and rendered Markdown doc')
    parser.add_argument('--scan-dir', default=DEFAULT_SCAN_DIR.as_posix(), help='directory containing sibling Golden Rule revision zips')
    args = parser.parse_args()

    report = build_report(Path(args.scan_dir).expanduser().resolve())
    payload = json.dumps(report, indent=2)
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(payload + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown, encoding='utf-8')
    else:
        print(payload)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

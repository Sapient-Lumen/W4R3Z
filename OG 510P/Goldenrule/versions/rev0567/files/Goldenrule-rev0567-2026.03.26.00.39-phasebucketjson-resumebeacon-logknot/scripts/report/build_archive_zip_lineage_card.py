#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_zip_lineage_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_LINEAGE_CARD.md'

sys.path.insert(0, str(ROOT / 'scripts' / 'tools'))
from audit_archive_zip_lineage import _default_scan_dir, scan_zip_lineage

DEFAULT_SCAN_DIR = _default_scan_dir()


def build_report(scan_dir: Path = DEFAULT_SCAN_DIR) -> dict[str, Any]:
    lineage = scan_zip_lineage(scan_dir)
    current = lineage['current_archive']
    head = lineage['authoritative_external_head']
    predecessor = lineage['immediate_predecessor_zip']
    duplicates = lineage['duplicate_revision_rows']
    duplicate_labels = [row['revision_label'] for row in duplicates]

    if head is None:
        headline = [
            f"No sibling Golden Rule revision zips were found in `{lineage['scan_dir']}`, so external package lineage cannot be audited from this cloudtainer right now.",
            f"The live root is still `{current['root_name']}`, but there is no external zip evidence to confirm or contradict it.",
        ]
    else:
        headline = [
            (
                f"The authoritative sibling zip head in `{lineage['scan_dir']}` is `{head['zip_name']}`, and it "
                f"aligns_with_live_root={lineage['current_root_vs_external_head_aligned']}."
            ),
            (
                f"The exact current-root zip `{current['expected_zip_name']}` is present={lineage['exact_current_zip_present']}; "
                f"the immediate predecessor zip is `{predecessor['zip_name'] if predecessor else 'none'}`."
            ),
            (
                f"Sibling zip lineage contains {lineage['duplicate_revision_count']} duplicated revision labels "
                f"({', '.join(duplicate_labels) if duplicate_labels else 'none'}), so revision reuse must be treated as an external package risk."
            ),
        ]

    stewardship = {
        'primary_open_doc': 'docs/ARCHIVE_ZIP_LINEAGE_CARD.md',
        'audit_command': 'python3 scripts/tools/audit_archive_zip_lineage.py',
        'canonical_cut_command': 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"',
        'exact_current_zip_present': lineage['exact_current_zip_present'],
        'current_root_vs_external_head_aligned': lineage['current_root_vs_external_head_aligned'],
        'duplicate_revision_count': lineage['duplicate_revision_count'],
        'duplicate_revision_labels': duplicate_labels,
    }

    return {
        'card': 'archive_zip_lineage_card',
        'scan_dir': lineage['scan_dir'],
        'current_archive': current,
        'authoritative_external_head': head,
        'immediate_predecessor_zip': predecessor,
        'duplicate_revision_rows': duplicates,
        'duplicate_revision_count': lineage['duplicate_revision_count'],
        'tail': lineage['tail'],
        'headline_findings': headline,
        'stewardship': stewardship,
        'metadata': {
            'source_tool': 'scripts/tools/audit_archive_zip_lineage.py',
            'source_scan_dir': lineage['scan_dir'],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    current = report['current_archive']
    head = report['authoritative_external_head']
    predecessor = report['immediate_predecessor_zip']
    duplicates = report['duplicate_revision_rows']
    stewardship = report['stewardship']

    lines: list[str] = [
        '# Archive Zip Lineage Card',
        '',
        'Compact external package-lane audit: confirm whether the sibling revision zips agree with the live root, identify the immediate predecessor zip, and flag any reused revision labels that can make archive-head recovery ambiguous from filenames alone.',
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Current live root',
        '',
        f"- root_name: `{current['root_name']}`",
        f"- revision_label: `{current['revision_label']}`",
        f"- expected_zip_name: `{current['expected_zip_name']}`",
        '',
        '## External zip authority',
        '',
    ])
    if head is None:
        lines.append(f"- No matching Golden Rule revision zips were found in `{report['scan_dir']}`.")
    else:
        lines.extend([
            f"- scan_dir: `{report['scan_dir']}`",
            f"- authoritative_external_head: `{head['zip_name']}`",
            f"- authoritative_revision_label: `{head['revision_label']}`",
            f"- authoritative_timestamp: `{head['timestamp']}`",
            f"- aligns_with_live_root: `{stewardship['current_root_vs_external_head_aligned']}`",
            f"- exact_current_zip_present: `{stewardship['exact_current_zip_present']}`",
            f"- immediate_predecessor_zip: `{predecessor['zip_name'] if predecessor else 'none'}`",
        ])
    lines.extend([
        '',
        '## Duplicate revision labels among sibling zips',
        '',
    ])
    if not duplicates:
        lines.append('- No duplicated revision labels were found among sibling revision zips.')
    else:
        for row in duplicates:
            joined = ', '.join(f"`{name}`" for name in row['zip_names'])
            lines.append(f"- `{row['revision_label']}` appears {row['count']} times: {joined}")
    lines.extend([
        '',
        '## Steward commands',
        '',
        f"- audit_command: `{stewardship['audit_command']}`",
        f"- canonical_cut_command: `{stewardship['canonical_cut_command']}`",
        '',
        '## Tail of sibling zip lineage',
        '',
    ])
    for row in report['tail']:
        lines.append(f"- `{row['revision_label']}` @ `{row['timestamp']}` — `{row['zip_name']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact archive zip lineage card from sibling revision zips.')
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

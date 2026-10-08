#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_zip_chronology_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_CHRONOLOGY_CARD.md'

sys.path.insert(0, str(ROOT / 'scripts' / 'tools'))
from audit_archive_zip_chronology import audit_zip_chronology
from audit_archive_zip_lineage import _default_scan_dir

DEFAULT_SCAN_DIR = _default_scan_dir()


def build_report(scan_dir: Path = DEFAULT_SCAN_DIR) -> dict[str, Any]:
    audit = audit_zip_chronology(scan_dir)
    current = audit['current_archive']
    by_revision = audit['latest_by_revision']
    by_timestamp = audit['latest_by_timestamp']
    inversions = audit['adjacent_revision_timestamp_inversions']
    duplicates = audit['duplicate_revision_rows']

    if by_revision is None or by_timestamp is None:
        headline = [
            f"No sibling Golden Rule revision zips were found in `{audit['scan_dir']}`, so chronology safety cannot be audited from this cloudtainer right now.",
            f"The live root remains `{current['root_name']}`, but there is no external zip history to confirm whether revision labels and timestamps agree.",
        ]
    else:
        first_inversion = inversions[0] if inversions else None
        headline = [
            (
                f"The authoritative head by revision is `{by_revision['zip_name']}`, while the latest zip by timestamp is `{by_timestamp['zip_name']}`; "
                f"same_head={audit['revision_and_timestamp_heads_match']}."
            ),
            (
                f"Sibling zip chronology has {audit['adjacent_revision_timestamp_inversion_count']} adjacent revision/timestamp inversions"
                + (
                    f", led by `{first_inversion['previous_revision_label']}` @ `{first_inversion['previous_timestamp']}` preceding "
                    f"`{first_inversion['current_revision_label']}` @ `{first_inversion['current_timestamp']}` in revision order."
                    if first_inversion
                    else ', so revision order is timestamp-monotone across unique revisions.'
                )
            ),
            (
                f"Duplicate revision labels still number {audit['duplicate_revision_count']}; authority therefore stays rule-based: {audit['authority_rule']}."
            ),
        ]

    stewardship = {
        'primary_open_doc': 'docs/ARCHIVE_ZIP_CHRONOLOGY_CARD.md',
        'audit_command': 'python3 scripts/tools/audit_archive_zip_chronology.py',
        'authority_rule': audit['authority_rule'],
        'adjacent_revision_timestamp_inversion_count': audit['adjacent_revision_timestamp_inversion_count'],
        'duplicate_revision_count': audit['duplicate_revision_count'],
        'revision_and_timestamp_heads_match': audit['revision_and_timestamp_heads_match'],
    }

    return {
        'card': 'archive_zip_chronology_card',
        'scan_dir': audit['scan_dir'],
        'current_archive': current,
        'latest_by_revision': by_revision,
        'latest_by_timestamp': by_timestamp,
        'revision_and_timestamp_heads_match': audit['revision_and_timestamp_heads_match'],
        'adjacent_revision_timestamp_inversions': inversions,
        'adjacent_revision_timestamp_inversion_count': audit['adjacent_revision_timestamp_inversion_count'],
        'duplicate_revision_rows': duplicates,
        'duplicate_revision_count': audit['duplicate_revision_count'],
        'tail_by_revision': audit['tail_by_revision'],
        'tail_by_timestamp': audit['tail_by_timestamp'],
        'headline_findings': headline,
        'stewardship': stewardship,
        'metadata': {
            'source_tool': 'scripts/tools/audit_archive_zip_chronology.py',
            'source_scan_dir': audit['scan_dir'],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    current = report['current_archive']
    by_revision = report['latest_by_revision']
    by_timestamp = report['latest_by_timestamp']
    inversions = report['adjacent_revision_timestamp_inversions']
    stewardship = report['stewardship']
    duplicates = report['duplicate_revision_rows']

    lines: list[str] = [
        '# Archive Zip Chronology Card',
        '',
        'Compact chronology audit for sibling revision zips: record whether the external package lane stays timestamp-monotone across revisions, whether “latest by revision” matches “latest by timestamp,” and why archive head authority must still prefer revision labels when the two orderings differ historically.',
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
        f"- timestamp: `{current['timestamp']}`",
        '',
        '## Head comparison',
        '',
    ])
    if by_revision is None or by_timestamp is None:
        lines.append(f"- No matching Golden Rule revision zips were found in `{report['scan_dir']}`.")
    else:
        lines.extend([
            f"- latest_by_revision: `{by_revision['zip_name']}`",
            f"- latest_by_timestamp: `{by_timestamp['zip_name']}`",
            f"- revision_and_timestamp_heads_match: `{report['revision_and_timestamp_heads_match']}`",
            f"- authority_rule: `{stewardship['authority_rule']}`",
        ])
    lines.extend([
        '',
        '## Adjacent revision/timestamp inversions',
        '',
    ])
    if not inversions:
        lines.append('- No adjacent revision/timestamp inversions were found across the unique revision heads.')
    else:
        for row in inversions:
            lines.append(
                f"- `{row['previous_revision_label']}` @ `{row['previous_timestamp']}` (`{row['previous_zip_name']}`) precedes "
                f"`{row['current_revision_label']}` @ `{row['current_timestamp']}` (`{row['current_zip_name']}`) in revision order, so timestamp order regresses across that step."
            )
    lines.extend([
        '',
        '## Duplicate revision labels',
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
        '## Steward command',
        '',
        f"- audit_command: `{stewardship['audit_command']}`",
        '',
        '## Tail by revision',
        '',
    ])
    for row in report['tail_by_revision']:
        lines.append(f"- `{row['revision_label']}` @ `{row['timestamp']}` — `{row['zip_name']}`")
    lines.extend([
        '',
        '## Tail by timestamp',
        '',
    ])
    for row in report['tail_by_timestamp']:
        lines.append(f"- `{row['revision_label']}` @ `{row['timestamp']}` — `{row['zip_name']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact archive zip chronology card from sibling revision zips.')
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

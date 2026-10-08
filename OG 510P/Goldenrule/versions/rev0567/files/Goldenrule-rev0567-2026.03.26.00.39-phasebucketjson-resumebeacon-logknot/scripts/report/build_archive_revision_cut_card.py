#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_revision_cut_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_REVISION_CUT_CARD.md'
PACKAGE_CUT_JSON = REPORTS / 'archive_package_cut_card.json'
SIZE_JSON = REPORTS / 'archive_size_guardrail_card.json'
CHANGELOG = ROOT / 'CHANGELOG.md'
ROOT_RE = re.compile(r'^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$')
CHANGELOG_RE = re.compile(r'^## rev(?P<revision>\d+) - (?P<date>\d{4}-\d{2}-\d{2})$')
DESCRIPTOR_PATTERN = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
TIMESTAMP_PATTERN = r'^\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}$'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _parse_root_identity() -> dict[str, Any]:
    match = ROOT_RE.match(ROOT.name)
    if not match:
        raise RuntimeError(f'root name does not match archive naming pattern: {ROOT.name}')
    revision = int(match.group('revision'))
    return {
        'root_name': ROOT.name,
        'revision': revision,
        'revision_label': f'rev{revision:04d}',
        'timestamp': match.group('stamp'),
        'descriptor_slug': match.group('descriptor'),
    }


def _load_changelog_chain() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in CHANGELOG.read_text(encoding='utf-8').splitlines():
        match = CHANGELOG_RE.match(line.strip())
        if not match:
            continue
        revision = int(match.group('revision'))
        rows.append({'revision': revision, 'revision_label': f'rev{revision:04d}', 'date': match.group('date')})
    if not rows:
        raise RuntimeError('no changelog revision headings found')
    return rows


def build_report() -> dict[str, Any]:
    identity = _parse_root_identity()
    chain = _load_changelog_chain()
    latest = chain[-1]
    previous = chain[-2] if len(chain) >= 2 else None
    if identity['revision'] != latest['revision']:
        raise RuntimeError(f"current root and changelog head are misaligned (root={identity['revision_label']} changelog={latest['revision_label']})")
    next_revision = latest['revision'] + 1
    next_label = f'rev{next_revision:04d}'
    package_cut = _load_json(PACKAGE_CUT_JSON)
    size = _load_json(SIZE_JSON)
    planner_command = 'python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug'
    cutter_command = 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"'
    template_root_name = f'Goldenrule-{next_label}-YYYY.MM.DD.HH.MM-descriptor-slug'
    example_descriptor = 'normalized-nextname'
    example_timestamp = identity['timestamp']
    example_root_name = f'Goldenrule-{next_label}-{example_timestamp}-{example_descriptor}'
    align = {
        'aligned_to_root': True,
        'latest_recorded_revision': latest,
        'immediate_predecessor_revision': previous,
        'root_vs_latest_delta': 0,
        'chain_tail': [{'revision_label': row['revision_label'], 'date': row['date']} for row in chain[-7:]],
    }
    headline_findings = [
        f"Current archive head `{identity['revision_label']}` is changelog-aligned, so the next safe label is `{next_label}` rather than reusing any existing revision number.",
        f"Normalized cut names must continue to match `{ROOT_RE.pattern}` with descriptor slugs constrained by `{DESCRIPTOR_PATTERN}`.",
        f"Use `{package_cut['canonical_wrapper_command']}` before the final rename/zip step so the package-boundary truth surfaces settle on the live tree first.",
        f"Use `{planner_command}` to stamp the exact next root/zip name; the card template is `{template_root_name}`.",
        f"Use `{cutter_command}` when you want the final settle + changelog append + rename + zip step executed from one command rather than by hand.",
        f"Package boundary is still ready={size['package_hygiene']['package_boundary_ready']} with pdf_count={size['package_hygiene']['pdf_count']} and scratch_file_count={size['package_hygiene']['scratch_file_count']}.",
    ]
    return {
        'card': 'archive_revision_cut_card',
        'snapshot_date': str(size.get('snapshot_date', '2026-03-23')),
        'current_archive_identity': identity,
        'changelog_alignment': align,
        'next_revision_plan': {
            'next_revision': next_revision,
            'next_revision_label': next_label,
            'template_root_name': template_root_name,
            'template_zip_name': f'{template_root_name}.zip',
            'example_descriptor': example_descriptor,
            'example_timestamp': example_timestamp,
            'example_root_name': example_root_name,
            'example_zip_name': f'{example_root_name}.zip',
            'planner_command_template': planner_command,
            'cutter_command_template': cutter_command,
            'descriptor_pattern': DESCRIPTOR_PATTERN,
            'timestamp_pattern': TIMESTAMP_PATTERN,
            'root_pattern': ROOT_RE.pattern,
        },
        'cut_prerequisites': {
            'settle_command': package_cut['canonical_wrapper_command'],
            'package_boundary_ready': size['package_hygiene']['package_boundary_ready'],
            'pdf_count': size['package_hygiene']['pdf_count'],
            'scratch_file_count': size['package_hygiene']['scratch_file_count'],
            'require_changelog_alignment': True,
            'require_descriptor_slug': True,
            'require_utc_minute_stamp': True,
            'rename_before_final_reentry_validation': True,
        },
        'headline_findings': headline_findings,
        'metadata': {
            'source_reports': [PACKAGE_CUT_JSON.relative_to(ROOT).as_posix(), SIZE_JSON.relative_to(ROOT).as_posix()],
            'source_docs': ['docs/ARCHIVE_PACKAGE_CUT_CARD.md', 'docs/ARCHIVE_REENTRY_CARD.md', 'CHANGELOG.md'],
            'source_scripts': ['scripts/tools/plan_archive_revision_cut.py', 'scripts/tools/cut_archive_revision.py'],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    identity = report['current_archive_identity']
    align = report['changelog_alignment']
    next_plan = report['next_revision_plan']
    prereq = report['cut_prerequisites']
    lines = [
        '# Archive Revision Cut Card',
        '',
        'Compact naming-and-cutover card for future package stewards: confirm the current head is safe to increment, derive the next normalized revision label, and stamp the exact next root/zip name without reusing an old revision number or ad-libbing the filename shape.',
        '',
        '## Headline findings',
        '',
    ]
    lines.extend(f'- {item}' for item in report['headline_findings'])
    lines.extend([
        '', '## Current head and alignment', '',
        f"- root_name: `{identity['root_name']}`",
        f"- revision_label: `{identity['revision_label']}`",
        f"- timestamp: `{identity['timestamp']}`",
        f"- descriptor_slug: `{identity['descriptor_slug']}`",
        f"- changelog_aligned_to_root: `{align['aligned_to_root']}`",
        f"- latest_recorded_revision: `{align['latest_recorded_revision']['revision_label']}` ({align['latest_recorded_revision']['date']})",
    ])
    prev = align['immediate_predecessor_revision']
    if prev is not None:
        lines.append(f"- immediate_predecessor_revision: `{prev['revision_label']}` ({prev['date']})")
    lines.extend(['', 'Recent changelog chain tail:', ''])
    lines.extend(f"- `{row['revision_label']}` ({row['date']})" for row in align['chain_tail'])
    lines.extend([
        '', '## Next revision naming contract', '',
        f"- next_revision_label: `{next_plan['next_revision_label']}`",
        f"- root_pattern: `{next_plan['root_pattern']}`",
        f"- descriptor_pattern: `{next_plan['descriptor_pattern']}`",
        f"- timestamp_pattern: `{next_plan['timestamp_pattern']}`",
        f"- template_root_name: `{next_plan['template_root_name']}`",
        f"- template_zip_name: `{next_plan['template_zip_name']}`",
        '', 'Planner invocation:', '',
        f"- `{next_plan['planner_command_template']}`",
        f"- `{next_plan['cutter_command_template']}`",
        f"- Example exact root name if you reuse the current minute with the safe descriptor `{next_plan['example_descriptor']}`: `{next_plan['example_root_name']}`",
        f"- Example exact zip name: `{next_plan['example_zip_name']}`",
        '', '## Cut prerequisites', '',
        f"- settle_command: `{prereq['settle_command']}`",
        f"- package_boundary_ready: `{prereq['package_boundary_ready']}`",
        f"- pdf_count: `{prereq['pdf_count']}`",
        f"- scratch_file_count: `{prereq['scratch_file_count']}`",
        f"- require_changelog_alignment: `{prereq['require_changelog_alignment']}`",
        f"- require_descriptor_slug: `{prereq['require_descriptor_slug']}`",
        f"- require_utc_minute_stamp: `{prereq['require_utc_minute_stamp']}`",
        f"- rename_before_final_reentry_validation: `{prereq['rename_before_final_reentry_validation']}`",
        '', '## Source surfaces', '',
    ])
    lines.extend(f"- `{p}`" for p in report['metadata']['source_reports'])
    lines.extend(f"- `{p}`" for p in report['metadata']['source_docs'])
    lines.extend(f"- `{p}`" for p in report['metadata']['source_scripts'])
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact archive revision cut card.')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        OUT_MD.write_text(render_markdown(report), encoding='utf-8')
    else:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / 'CHANGELOG.md'
ROOT_RE = re.compile(r'^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$')
CHANGELOG_RE = re.compile(r'^## rev(?P<revision>\d+) - (?P<date>\d{4}-\d{2}-\d{2})$')
TIMESTAMP_RE = re.compile(r'^\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}$')
DESCRIPTOR_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def parse_root_identity(root_name: str) -> dict[str, Any]:
    match = ROOT_RE.match(root_name)
    if not match:
        raise ValueError(f'root name does not match archive naming pattern: {root_name}')
    revision = int(match.group('revision'))
    return {
        'root_name': root_name,
        'revision': revision,
        'revision_label': f'rev{revision:04d}',
        'timestamp': match.group('stamp'),
        'descriptor_slug': match.group('descriptor'),
    }


def load_changelog_chain(path: Path = CHANGELOG) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        match = CHANGELOG_RE.match(line.strip())
        if not match:
            continue
        revision = int(match.group('revision'))
        rows.append({'revision': revision, 'revision_label': f'rev{revision:04d}', 'date': match.group('date')})
    if not rows:
        raise RuntimeError('no changelog revision headings found')
    return rows


def validate_descriptor(descriptor: str) -> str:
    if not DESCRIPTOR_RE.fullmatch(descriptor):
        raise ValueError(f'descriptor slug must match {DESCRIPTOR_RE.pattern} (got {descriptor!r})')
    return descriptor


def validate_timestamp(timestamp: str) -> str:
    if not TIMESTAMP_RE.fullmatch(timestamp):
        raise ValueError(f'timestamp must match YYYY.MM.DD.HH.MM (got {timestamp!r})')
    return timestamp


def current_utc_minute_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y.%m.%d.%H.%M')


def build_plan(descriptor: str, timestamp: str, root_name: str = ROOT.name, changelog_path: Path = CHANGELOG) -> dict[str, Any]:
    identity = parse_root_identity(root_name)
    chain = load_changelog_chain(changelog_path)
    latest = chain[-1]
    previous = chain[-2] if len(chain) >= 2 else None
    descriptor = validate_descriptor(descriptor)
    timestamp = validate_timestamp(timestamp)
    if identity['revision'] != latest['revision']:
        raise RuntimeError(
            'archive head is not safe to increment because changelog head does not match the current root '
            f"(root={identity['revision_label']} changelog={latest['revision_label']})"
        )
    next_revision = latest['revision'] + 1
    next_root_name = f"Goldenrule-rev{next_revision:04d}-{timestamp}-{descriptor}"
    return {
        'tool': 'plan_archive_revision_cut',
        'current_archive': identity,
        'changelog_head': latest,
        'immediate_predecessor_revision': previous,
        'aligned_to_current_head': True,
        'next_revision': next_revision,
        'next_revision_label': f'rev{next_revision:04d}',
        'descriptor_slug': descriptor,
        'timestamp': timestamp,
        'next_root_name': next_root_name,
        'next_zip_name': f'{next_root_name}.zip',
        'naming_contract': {
            'root_pattern': ROOT_RE.pattern,
            'descriptor_pattern': DESCRIPTOR_RE.pattern,
            'timestamp_pattern': TIMESTAMP_RE.pattern,
        },
        'recommended_commands': {
            'settle_command': 'make settle-archive-truth',
            'planner_template': 'python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug',
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Plan the normalized next Golden Rule archive revision name and zip stem.')
    parser.add_argument('--descriptor', default='your-summary-slug')
    parser.add_argument('--timestamp', default=None)
    args = parser.parse_args()
    try:
        plan = build_plan(args.descriptor, args.timestamp or current_utc_minute_stamp())
    except Exception as exc:  # noqa: BLE001
        print(f'plan-archive-revision-cut: {exc}', file=sys.stderr)
        return 1
    json.dump(plan, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

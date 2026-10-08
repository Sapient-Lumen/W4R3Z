#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'archive_handoff_pack.json'
DOC_PATH = ROOT / 'docs' / 'ARCHIVE_HANDOFF_PACK.md'
LINEAGE_REPORT = ROOT / 'artifacts' / 'reports' / 'archive_zip_lineage_card.json'
CHRONOLOGY_REPORT = ROOT / 'artifacts' / 'reports' / 'archive_zip_chronology_card.json'


def fail(message: str) -> int:
    print(f'archive-handoff-pack: {message}', file=sys.stderr)
    return 1


def main() -> int:
    proc = subprocess.run(
        ['python3', 'scripts/report/build_archive_handoff_pack.py', '--write'],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end='', file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end='', file=sys.stderr)
        return fail('builder drifted or failed')

    if not REPORT_PATH.exists():
        return fail('missing report json')
    if not DOC_PATH.exists():
        return fail('missing rendered doc')

    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    if report.get('card') != 'archive_handoff_pack':
        return fail('card id mismatch')
    if report.get('primary_open_group_id') != 'archive_head_reentry':
        return fail('primary open group drifted')
    if report.get('primary_open_path') != 'docs/ARCHIVE_REENTRY_CARD.md':
        return fail('primary open path drifted')
    if report.get('primary_verify_command') != 'make test-archive-reentry-card':
        return fail('primary verify command drifted')
    if report.get('primary_refresh_command') != 'make update-archive-reentry-card':
        return fail('primary refresh command drifted')
    groups = report.get('groups', [])
    if len(groups) != 11:
        return fail(f'unexpected group count: {len(groups)}')
    group_ids = [group.get('id') for group in groups]
    required_ids = [
        'archive_head_reentry',
        'blocked_cloudtainer',
        'first_rust_machine',
        'package_cut',
        'external_zip_lineage',
        'external_zip_chronology',
        'external_zip_authority',
        'external_zip_digest',
        'external_zip_size_truth',
        'revision_cut',
        'byte_diet',
    ]
    if group_ids != required_ids:
        return fail(f'group order drifted: {group_ids}')
    if report.get('pack_totals', {}).get('file_count', 0) < 20:
        return fail('pack file count unexpectedly low')
    if len(str(report.get('pack_totals', {}).get('manifest_sha256', ''))) != 64:
        return fail('manifest sha256 missing or malformed')
    if report.get('direct_witnesses', {}).get('blocked_cloudtainer_primary_command') != 'make cloudtainer-shadow-pass-medium':
        return fail('blocked cloudtainer command drifted')
    if report.get('direct_witnesses', {}).get('package_settle_command') != 'make settle-archive-truth':
        return fail('package settle command drifted')
    if report.get('direct_witnesses', {}).get('handoff_pack_verify_command') != 'python3 scripts/tools/verify_archive_handoff_pack.py':
        return fail('handoff pack verify command drifted')
    if report.get('direct_witnesses', {}).get('authoritative_zip_resolver_command') != 'python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path':
        return fail('resolver command drifted')
    if report.get('direct_witnesses', {}).get('authoritative_zip_digest_command') != 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256':
        return fail('zip digest command drifted')
    if report.get('direct_witnesses', {}).get('authoritative_zip_verify_command') != 'python3 scripts/tools/verify_authoritative_archive_zip.py':
        return fail('zip verify command drifted')
    lineage = json.loads(LINEAGE_REPORT.read_text(encoding='utf-8'))
    chronology = json.loads(CHRONOLOGY_REPORT.read_text(encoding='utf-8'))
    duplicate_count = report.get('direct_witnesses', {}).get('duplicate_revision_count', -1)
    chronology_count = report.get('direct_witnesses', {}).get('chronology_inversion_count', -1)
    if duplicate_count != lineage.get('duplicate_revision_count'):
        return fail('duplicate revision count drifted from lineage report')
    if chronology_count != chronology.get('adjacent_revision_timestamp_inversion_count'):
        return fail('chronology inversion count drifted from chronology report')
    if duplicate_count < 0 or chronology_count < 0:
        return fail('lineage hazard counts must stay non-negative')
    for group in groups:
        if len(str(group.get('doc_sha256', ''))) != 64 or len(str(group.get('report_sha256', ''))) != 64:
            return fail(f'malformed sha256 for group {group.get("id")}')
        if group.get('doc_bytes', 0) <= 0 or group.get('report_bytes', 0) <= 0:
            return fail(f'non-positive byte count for group {group.get("id")}')

    text = DOC_PATH.read_text(encoding='utf-8')
    required_fragments = [
        '# Archive Handoff Pack',
        '## Primary entry target',
        '## Ordered group manifest',
        '### archive_head_reentry',
        '### blocked_cloudtainer',
        '### first_rust_machine',
        '### external_zip_digest',
        '### external_zip_size_truth',
        '### package_cut',
        '### external_zip_authority',
        '### revision_cut',
        '### byte_diet',
        '`make test-archive-reentry-card`',
        '`make settle-archive-truth`',
        '`python3 scripts/tools/verify_archive_handoff_pack.py`',
        '`python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path`',
        '`python3 scripts/tools/verify_authoritative_archive_zip.py`',
    ]
    missing = [frag for frag in required_fragments if frag not in text]
    if missing:
        return fail(f'missing required doc fragments: {missing}')

    print(
        'archive-handoff-pack: ok '
        f"(groups={len(groups)} files={report['pack_totals']['file_count']} primary={report['primary_open_path']})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

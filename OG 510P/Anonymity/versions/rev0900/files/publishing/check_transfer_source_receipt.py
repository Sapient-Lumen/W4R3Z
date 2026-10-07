#!/usr/bin/env python3
"""Validate internal agreement among compared-bundle provenance surfaces."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

SOURCE_TOKEN_RE = re.compile(r'[A-Za-z][A-Za-z0-9-]+-rev\d{4}')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))


def parse_sha(path: pathlib.Path) -> list[tuple[str, str]]:
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        parts = line.split('  ', 1)
        if len(parts) != 2:
            raise ValueError(f'malformed TRANSFER_INPUTS.sha256 line: {line!r}')
        rows.append((parts[0], parts[1]))
    return rows


def record(checks: list[dict], name: str, ok: bool, details: str):
    checks.append({'name': name, 'status': 'pass' if ok else 'fail', 'details': details})


def check(root: pathlib.Path) -> dict:
    release = load_json(root / 'RELEASE_MANIFEST.json')
    data = load_json(root / 'TRANSFER_SOURCES.json')
    ledger = load_json(root / 'DATACUBE_TRANSFER_LEDGER.json')
    sha_rows = parse_sha(root / 'TRANSFER_INPUTS.sha256')
    md_text = (root / 'TRANSFER_SOURCES.md').read_text(encoding='utf-8')

    entries = data.get('source_bundles', [])
    checks: list[dict] = []

    record(checks, 'source_bundle_count_matches_entries', data.get('source_bundle_count') == len(entries), f"declared={data.get('source_bundle_count')} actual={len(entries)}")

    statuses = [e.get('transfer_status') for e in entries]
    status_counts = {
        'adopted_pattern': sum(1 for s in statuses if s == 'adopted_pattern'),
        'reviewed_no_strong_transfer': sum(1 for s in statuses if s == 'reviewed_no_strong_transfer'),
    }
    record(checks, 'status_counts_match_entries', data.get('status_counts') == status_counts, f"declared={data.get('status_counts')} actual={status_counts}")

    bundles = [e.get('bundle') for e in entries]
    record(checks, 'bundles_are_unique', len(bundles) == len(set(bundles)), f"bundle_count={len(bundles)} unique={len(set(bundles))}")

    bad_hashes = [e.get('bundle','?') for e in entries if not SHA_RE.match(e.get('sha256',''))]
    record(checks, 'sha256_strings_are_well_formed', not bad_hashes, 'bad=' + (', '.join(bad_hashes) if bad_hashes else 'none'))

    sha_from_json = sorted((e['sha256'], e['bundle']) for e in entries)
    sha_from_file = sorted(sha_rows)
    record(checks, 'sha_receipt_matches_json', sha_from_json == sha_from_file, f"json_rows={len(sha_from_json)} sha_rows={len(sha_from_file)}")

    md_ok = f"- Source bundle count: {len(entries)}" in md_text and '| Project | Revision | Status | Bundle | SHA-256 |' in md_text
    record(checks, 'markdown_summary_mentions_count_and_table', md_ok, f"source_bundle_count={len(entries)}")

    json_tokens = {f"{e['project']}-{e['source_revision']}" for e in entries}
    ledger_tokens = set()
    for section in ('adopted', 'not_adopted'):
        for item in ledger.get(section, []):
            ledger_tokens.update(SOURCE_TOKEN_RE.findall(item.get('source_datacube', '')))
    missing_from_json = sorted(ledger_tokens - json_tokens)
    record(checks, 'ledger_sources_are_present_in_transfer_sources', not missing_from_json, 'missing=' + (', '.join(missing_from_json) if missing_from_json else 'none'))

    adopted_tokens = {f"{e['project']}-{e['source_revision']}" for e in entries if e.get('transfer_status') == 'adopted_pattern'}
    new_anchor_ok = all((root / p).exists() for p in ['TRANSFER_SOURCES.json','TRANSFER_SOURCES.md','TRANSFER_INPUTS.sha256'])
    record(checks, 'adopted_sources_and_anchor_files_exist', bool(adopted_tokens) and new_anchor_ok, f"adopted_source_count={len(adopted_tokens)} anchor_files_exist={new_anchor_ok}")

    failures = [c for c in checks if c['status'] == 'fail']
    return {
        'status': 'pass' if not failures else 'fail',
        'generated_for_revision': release.get('revision'),
        'checked_revision': data.get('generated_for_revision'),
        'checked_bundle': release.get('bundle'),
        'publication_authorized': False,
        'source_bundle_count': len(entries),
        'checks': checks,
        'summary': {'checks_passed': len(checks) - len(failures), 'checks_failed': len(failures)},
        'fail_closed_rule': 'If this report fails, default to no publication and repair the compared-bundle provenance surfaces before relying on transfer-history claims.'
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--write-report', default='')
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + '\n'
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())

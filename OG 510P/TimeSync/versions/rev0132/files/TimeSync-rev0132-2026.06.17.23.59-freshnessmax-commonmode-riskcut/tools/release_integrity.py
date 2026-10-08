#!/usr/bin/env python3
"""Release-identity and source-tree integrity checks for TimeSync.

The revision receipt is the single source of current release identity. Validators,
documentation lint, the manifest, and the release builder derive their revision from
it rather than carrying independent hard-coded literals.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from temporal_coherence import parse_dt

REVISION_RE = re.compile(r'^rev(?P<number>\d{4})$')
ARCHIVE_RE = re.compile(
    r'^TimeSync-(?P<revision>rev\d{4})-'
    r'(?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2})\.'
    r'(?P<hour>\d{2})\.(?P<minute>\d{2})-'
    r'(?P<name>[a-z0-9][a-z0-9-]*)\.zip$'
)
GENERATED_DIR_NAMES = {'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
GENERATED_SUFFIXES = {'.pyc', '.pyo'}


def load_receipt(root: Path) -> dict[str, Any]:
    path = root / 'REVISION-RECEIPT.json'
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f'cannot load REVISION-RECEIPT.json: {exc}') from exc
    if not isinstance(value, dict):
        raise ValueError('REVISION-RECEIPT.json must contain an object')
    return value


def current_revision(root: Path) -> str:
    revision = load_receipt(root).get('revision')
    if not isinstance(revision, str) or REVISION_RE.fullmatch(revision) is None:
        raise ValueError(f'invalid release revision {revision!r}')
    return revision


def is_generated_path(path: Path) -> bool:
    return any(part in GENERATED_DIR_NAMES for part in path.parts) or path.suffix in GENERATED_SUFFIXES


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    revision = receipt.get('revision')
    match = REVISION_RE.fullmatch(revision) if isinstance(revision, str) else None
    if match is None:
        errors.append('receipt revision must match rev####')
        revision_number = None
    else:
        revision_number = int(match.group('number'))

    baseline = receipt.get('baseline')
    if revision_number is not None:
        expected_baseline = f'rev{revision_number - 1:04d}'
        if baseline != expected_baseline:
            errors.append(f'receipt baseline must be immediate predecessor {expected_baseline}')

    issued_at = receipt.get('issued_at')
    if not isinstance(issued_at, str):
        errors.append('receipt issued_at must be an RFC 3339 string')
    else:
        try:
            parse_dt(issued_at)
        except Exception as exc:  # noqa: BLE001
            errors.append(f'receipt issued_at is invalid: {exc}')

    name = receipt.get('name')
    if not isinstance(name, str) or re.fullmatch(r'[a-z0-9][a-z0-9-]*', name) is None:
        errors.append('receipt name must be a lowercase hyphenated release slug')

    archive_filename = receipt.get('archive_filename')
    archive_match = ARCHIVE_RE.fullmatch(archive_filename) if isinstance(archive_filename, str) else None
    if archive_match is None:
        errors.append('receipt archive_filename must match TimeSync-rev####-YYYY.MM.DD.HH.MM-name.zip')
    else:
        if revision is not None and archive_match.group('revision') != revision:
            errors.append('receipt archive_filename revision does not match receipt revision')
        if isinstance(name, str) and archive_match.group('name') != name:
            errors.append('receipt archive_filename suffix does not match receipt name')
        if isinstance(issued_at, str):
            issued_match = re.match(
                r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T'
                r'(?P<hour>\d{2}):(?P<minute>\d{2})',
                issued_at,
            )
            if issued_match and any(
                archive_match.group(field) != issued_match.group(field)
                for field in ('year', 'month', 'day', 'hour', 'minute')
            ):
                errors.append('receipt archive_filename timestamp does not match issued_at local fields')

    summary = receipt.get('summary')
    if not isinstance(summary, str) or len(summary.strip()) < 40:
        errors.append('receipt summary must be a substantive non-empty string')

    validation_expected = receipt.get('validation_expected')
    if not isinstance(validation_expected, str) or not isinstance(revision, str) or revision not in validation_expected:
        errors.append('receipt validation_expected must contain the current revision')

    ticket_fields = ('closed_frontier_ticket', 'opened_frontier_ticket', 'continued_frontier_ticket')
    for field in ticket_fields:
        value = receipt.get(field)
        if value is not None and (not isinstance(value, str) or re.fullmatch(r'FT-\d{4}', value) is None):
            errors.append(f'receipt {field} must be null or match FT-####')
    if receipt.get('continued_frontier_ticket') is not None and (
        receipt.get('closed_frontier_ticket') is not None or receipt.get('opened_frontier_ticket') is not None
    ):
        errors.append('receipt cannot continue a frontier ticket while also closing or opening one')
    if receipt.get('opened_frontier_ticket') == receipt.get('closed_frontier_ticket') and receipt.get('opened_frontier_ticket') is not None:
        errors.append('receipt cannot open and close the same frontier ticket')
    return errors


def check_release_integrity(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        receipt = load_receipt(root)
    except ValueError as exc:
        return [str(exc)]
    errors.extend(validate_receipt(receipt))

    generated = sorted(
        str(path.relative_to(root))
        for path in root.rglob('*')
        if (path.is_file() or path.is_dir()) and is_generated_path(path.relative_to(root))
    )
    if generated:
        preview = ', '.join(generated[:8])
        suffix = '' if len(generated) <= 8 else f' (+{len(generated) - 8} more)'
        errors.append(f'generated cache/build artifacts are forbidden in a release tree: {preview}{suffix}')

    manifest_path = root / 'MANIFEST.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'cannot load MANIFEST.json for release identity: {exc}')
        return errors
    if not isinstance(manifest, dict):
        errors.append('MANIFEST.json must contain an object')
        return errors
    if manifest.get('manifest_version') != 'timesync-manifest-v2':
        errors.append('MANIFEST.json manifest_version must be timesync-manifest-v2')
    if manifest.get('revision') != receipt.get('revision'):
        errors.append('MANIFEST.json revision must match REVISION-RECEIPT.json')
    archive_filename = receipt.get('archive_filename')
    expected_root = archive_filename[:-4] if isinstance(archive_filename, str) and archive_filename.endswith('.zip') else None
    if expected_root is not None and manifest.get('archive_root') != expected_root:
        errors.append('MANIFEST.json archive_root must match receipt archive_filename stem')
    files = manifest.get('files')
    if isinstance(files, list):
        for entry in files:
            rel = entry.get('path') if isinstance(entry, dict) else None
            if isinstance(rel, str) and is_generated_path(Path(rel)):
                errors.append(f'MANIFEST.json must not track generated artifact {rel}')

    archive_root = manifest.get('archive_root')
    if isinstance(archive_root, str) and ARCHIVE_RE.fullmatch(root.name + '.zip') is not None and root.name != archive_root:
        errors.append('extracted archive root directory does not match MANIFEST.json archive_root')

    frontier_path = root / 'frontier-ticket.json'
    try:
        frontier = json.loads(frontier_path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'cannot load frontier-ticket.json: {exc}')
        frontier = None
    if isinstance(frontier, dict):
        active_ticket = receipt.get('opened_frontier_ticket') or receipt.get('continued_frontier_ticket')
        if frontier.get('id') != active_ticket:
            errors.append('frontier-ticket.json id must match the receipt opened/continued frontier ticket')
        if frontier.get('status') != 'open':
            errors.append('frontier-ticket.json current ticket must have status open')
    elif frontier is not None:
        errors.append('frontier-ticket.json must contain an object')

    closed_ticket = receipt.get('closed_frontier_ticket')
    if isinstance(closed_ticket, str):
        closure_matches = sorted((root / 'archive').glob(f'frontier-ticket-{closed_ticket}-closed-*.json'))
        if not closure_matches:
            errors.append(f'receipt closes {closed_ticket} but no archived closure record exists')
        else:
            try:
                closure = json.loads(closure_matches[-1].read_text(encoding='utf-8'))
            except Exception as exc:  # noqa: BLE001
                errors.append(f'cannot load closure record for {closed_ticket}: {exc}')
            else:
                if not isinstance(closure, dict) or closure.get('id') != closed_ticket or closure.get('status') != 'closed':
                    errors.append(f'archived closure record for {closed_ticket} is inconsistent')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid = {
        'revision': 'rev0121',
        'issued_at': '2026-06-17T18:25:00-04:00',
        'name': 'missioncompass-exacttime-releaseintegrity',
        'archive_filename': 'TimeSync-rev0121-2026.06.17.18.25-missioncompass-exacttime-releaseintegrity.zip',
        'baseline': 'rev0120',
        'closed_frontier_ticket': 'FT-0090',
        'opened_frontier_ticket': 'FT-0121',
        'continued_frontier_ticket': None,
        'summary': 'A substantive release summary long enough to exercise receipt validation.',
        'validation_expected': 'TimeSync rev0121 validation passed.',
    }
    valid_errors = validate_receipt(valid)
    if valid_errors:
        errors.append(f'release receipt self-test rejected valid receipt: {valid_errors}')
    bad = dict(valid, baseline='rev0119')
    if not any('immediate predecessor' in error for error in validate_receipt(bad)):
        errors.append('release receipt self-test accepted a stale baseline')
    if not is_generated_path(Path('tools/__pycache__/module.cpython-313.pyc')):
        errors.append('release integrity self-test failed to identify generated bytecode')
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    failures = self_test() + check_release_integrity(root)
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print(f'TimeSync {current_revision(root)} release integrity passed.')

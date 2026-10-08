import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH_DIR = ROOT / 'examples' / 'evidence-watchlists'
SCHEMA_PATH = ROOT / 'schemas' / 'external-evidence-watchlist.schema.json'

SOURCE_CLASSES = {'standard', 'regulation', 'security', 'official_guidance', 'peer_or_independent_study', 'market_signal'}
WATCH_STATES = {'EW0', 'EW1', 'EW2', 'EW3', 'EW4', 'EW5', 'EWX'}
CADENCES = {'monthly', 'quarterly', 'annual', 'triggered'}

bibliography_text = (ROOT / 'docs' / '00-meta' / 'bibliography.md').read_text(encoding='utf-8')
bib_ids = set(re.findall(r'^##\s+(B\d+)\b', bibliography_text, flags=re.MULTILINE))


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    return value is not None


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    for field in ['watchlist_id', 'title', 'owner', 'sources', 'last_reviewed']:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['watchlist_id'].startswith('EWATCH-'):
        fail(errors, rel, 'watchlist_id must start EWATCH-')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    seen = set()
    for idx, source in enumerate(data.get('sources', [])):
        prefix = f'sources[{idx}]'
        required = [
            'source_id', 'title', 'url', 'source_class', 'watch_state', 'review_cadence',
            'next_review_date', 'related_bibliography_ids', 'related_archive_surfaces',
            'invalidation_triggers', 'action_if_changed'
        ]
        for field in required:
            if field not in source or not nonempty(source[field]):
                fail(errors, rel, f'{prefix}.{field} missing or empty')
        sid = source.get('source_id')
        if sid in seen:
            fail(errors, rel, f'duplicate source_id {sid}')
        seen.add(sid)
        if not str(source.get('url', '')).startswith('https://'):
            fail(errors, rel, f'{prefix}.url must be https')
        if source.get('source_class') not in SOURCE_CLASSES:
            fail(errors, rel, f'{prefix}.source_class invalid')
        if source.get('watch_state') not in WATCH_STATES:
            fail(errors, rel, f'{prefix}.watch_state invalid')
        if source.get('review_cadence') not in CADENCES:
            fail(errors, rel, f'{prefix}.review_cadence invalid')
        parse_date(source.get('next_review_date', ''), errors, rel, f'{prefix}.next_review_date')
        bad_bib = sorted(set(source.get('related_bibliography_ids', [])) - bib_ids)
        if bad_bib:
            fail(errors, rel, f'{prefix}.unknown bibliography ids: ' + ', '.join(bad_bib))
        for surface in source.get('related_archive_surfaces', []):
            if not (ROOT / surface).exists():
                fail(errors, rel, f'{prefix}.missing archive surface: {surface}')
        if source.get('watch_state') != 'EWX' and 'review' not in source.get('action_if_changed', '').lower() and 'update' not in source.get('action_if_changed', '').lower() and 'revise' not in source.get('action_if_changed', '').lower():
            fail(errors, rel, f'{prefix}.action_if_changed should name review/update/revise action')

    return errors

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU external evidence watchlist':
    raise SystemExit('external evidence watchlist schema title mismatch')

paths = sorted(WATCH_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no evidence watchlists found')

all_errors = []
source_count = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    source_count += len(data.get('sources', []))
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('evidence watchlist validation errors:\n' + '\n'.join(all_errors))
print(f'check_evidence_watchlists: OK ({len(paths)} watchlists, {source_count} sources)')

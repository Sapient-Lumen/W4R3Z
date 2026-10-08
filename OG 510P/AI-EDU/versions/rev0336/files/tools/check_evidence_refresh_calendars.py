import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL_DIR = ROOT / 'examples' / 'evidence-refresh-calendars'
SCHEMA_PATH = ROOT / 'schemas' / 'evidence-refresh-calendar.schema.json'
STATES = {'ER0', 'ER1', 'ER2', 'ER3', 'ER4', 'ERX'}

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
watchlists = {}
watch_sources = {}
for path in (ROOT / 'examples' / 'evidence-watchlists').glob('*.json'):
    data = json.loads(path.read_text(encoding='utf-8'))
    watchlists[data['watchlist_id']] = data
    for source in data.get('sources', []):
        watch_sources[source['source_id']] = source

bibliography_text = (ROOT / 'docs' / '00-meta' / 'bibliography.md').read_text(encoding='utf-8')
bib_ids = set(re.findall(r'^##\s+(B\d+)\b', bibliography_text, flags=re.MULTILINE))


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        return date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')
        return None


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
    required = ['calendar_id', 'revision', 'refresh_state', 'watchlist_ids', 'rows', 'staleness_rule', 'last_reviewed']
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors
    if not data['calendar_id'].startswith('ER-'):
        fail(errors, rel, 'calendar_id must start ER-')
    if data['revision'] != receipt['revision']:
        fail(errors, rel, 'revision does not match receipt')
    if data['refresh_state'] not in STATES:
        fail(errors, rel, 'refresh_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')
    for wid in data.get('watchlist_ids', []):
        if wid not in watchlists:
            fail(errors, rel, f'unknown watchlist_id {wid}')

    seen_sources = set()
    for idx, row in enumerate(data.get('rows', [])):
        prefix = f'rows[{idx}]'
        required_row = ['source_id', 'related_bibliography_ids', 'claim_families', 'related_archive_surfaces', 'last_checked', 'next_review_due', 'stale_action', 'change_action', 'known_current_public_claim']
        for field in required_row:
            if field not in row or not nonempty(row[field]):
                fail(errors, rel, f'{prefix}.{field} missing or empty')
        sid = row.get('source_id')
        seen_sources.add(sid)
        if sid not in watch_sources:
            fail(errors, rel, f'{prefix}.unknown source_id {sid}')
        last_checked = parse_date(row.get('last_checked', ''), errors, rel, f'{prefix}.last_checked')
        next_due = parse_date(row.get('next_review_due', ''), errors, rel, f'{prefix}.next_review_due')
        if last_checked and next_due and next_due <= last_checked:
            fail(errors, rel, f'{prefix}.next_review_due must be after last_checked')
        bad_bib = sorted(set(row.get('related_bibliography_ids', [])) - bib_ids)
        if bad_bib:
            fail(errors, rel, f'{prefix}.unknown bibliography ids: ' + ', '.join(bad_bib))
        for surface in row.get('related_archive_surfaces', []):
            if not (ROOT / surface).exists():
                fail(errors, rel, f'{prefix}.missing archive surface: {surface}')
        if 'downgrade' not in row.get('stale_action', '').lower() and 'pending-review' not in row.get('stale_action', '').lower():
            fail(errors, rel, f'{prefix}.stale_action must name downgrade or pending-review')
        if 'does not close ft-0181' not in row.get('known_current_public_claim', '').lower():
            fail(errors, rel, f'{prefix}.known_current_public_claim must preserve FT-0181 boundary')

    expected_sources = set(watch_sources)
    if seen_sources != expected_sources:
        missing = sorted(expected_sources - seen_sources)
        extra = sorted(seen_sources - expected_sources)
        if missing:
            fail(errors, rel, 'calendar missing watchlist sources: ' + ', '.join(missing))
        if extra:
            fail(errors, rel, 'calendar has unknown sources: ' + ', '.join(extra))
    if 'public claims must narrow' not in data.get('staleness_rule', '').lower():
        fail(errors, rel, 'staleness_rule must say public claims must narrow')
    return errors

schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU evidence refresh calendar':
    raise SystemExit('evidence refresh calendar schema title mismatch')

paths = sorted(CAL_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no evidence refresh calendars found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('evidence refresh calendar validation errors:\n' + '\n'.join(all_errors))
print(f'check_evidence_refresh_calendars: OK ({len(paths)} calendars, {len(watch_sources)} sources)')

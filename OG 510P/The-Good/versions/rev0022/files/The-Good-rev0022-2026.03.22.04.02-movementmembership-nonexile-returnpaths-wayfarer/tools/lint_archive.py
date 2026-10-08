#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys

from archive_meta import ARCHIVE, CODENAME, CONTROL_SURFACES, LIFECYCLE_GATES, NOTE_SOURCE_MAP, RELEASE_HIGHLIGHTS, REQUIRED_ROOT_FILES, REVISION, ROOT, TIMESTAMP, SOURCE_CATALOG, THREADS, current_revision

VALID_SOURCE_KINDS = {'philosophy-reference', 'policy-framework', 'scientific-assessment', 'scientific-statement'}
VALID_SOURCE_STABILITY = {'stable', 'snapshot', 'rolling'}


def fail(msg: str) -> None:
    print(f'lint: FAIL: {msg}')
    sys.exit(1)


def main() -> None:
    for name in REQUIRED_ROOT_FILES:
        if not (ROOT / name).exists():
            fail(f'missing required root file: {name}')


    if REQUIRED_ROOT_FILES != sorted(dict.fromkeys(REQUIRED_ROOT_FILES)):
        fail('REQUIRED_ROOT_FILES must be unique and sorted')

    if list(SOURCE_CATALOG) != sorted(SOURCE_CATALOG):
        fail('SOURCE_CATALOG keys must remain sorted for stable diffs')

    if list(NOTE_SOURCE_MAP) != sorted(NOTE_SOURCE_MAP):
        fail('NOTE_SOURCE_MAP keys must remain sorted for stable diffs')

    pycache_dirs = list(ROOT.rglob('__pycache__'))
    if pycache_dirs:
        fail(f'python cache directories present: {[str(p.relative_to(ROOT)) for p in pycache_dirs]}')

    pyc_files = list(ROOT.rglob('*.pyc'))
    if pyc_files:
        fail(f'python cache files present: {[str(p.relative_to(ROOT)) for p in pyc_files]}')

    changelog = (ROOT / 'CHANGELOG.md').read_text(errors='ignore')
    if changelog.count('# Changelog') != 1 or not changelog.startswith('# Changelog\n'):
        fail('CHANGELOG.md must contain exactly one top-level # Changelog header at the top of the file')

    readme = (ROOT / 'README.md').read_text(errors='ignore')
    expected_heading = f"# The Good — rev{REVISION:04d}"
    if expected_heading not in readme:
        fail(f'README.md missing current revision heading: {expected_heading}')
    if f"Timestamp: {TIMESTAMP}" not in readme:
        fail('README.md timestamp is out of sync with archive metadata')
    if f"Codename: `{CODENAME}`" not in readme:
        fail('README.md codename is out of sync with archive metadata')

    for key, entry in SOURCE_CATALOG.items():
        for field in ['publisher', 'title', 'url', 'kind', 'stability']:
            if field not in entry:
                fail(f'source {key} missing field: {field}')
        if entry['kind'] not in VALID_SOURCE_KINDS:
            fail(f"source {key} has invalid kind: {entry['kind']}")
        if entry['stability'] not in VALID_SOURCE_STABILITY:
            fail(f"source {key} has invalid stability: {entry['stability']}")
        if not entry['url'].startswith('https://'):
            fail(f"source {key} url must use https: {entry['url']}")
        if entry['url'].lower().endswith('.pdf'):
            fail(f"source {key} url must not point directly to a pdf: {entry['url']}")

    note_paths = sorted(ARCHIVE.glob('[0-9][0-9][0-9]-*.md'))
    if not note_paths:
        fail('no numbered notes found')

    numbers = []
    for path in note_paths:
        m = re.match(r'^(\d{3})-', path.name)
        if not m:
            fail(f'bad note name: {path.name}')
        numbers.append(int(m.group(1)))
        rel = str(path.relative_to(ROOT))
        if rel not in NOTE_SOURCE_MAP:
            fail(f'note missing source mapping: {rel}')
        keys = NOTE_SOURCE_MAP[rel]
        if keys != sorted(dict.fromkeys(keys)):
            fail(f'note source list must be unique and sorted: {rel}')
        for key in keys:
            if key not in SOURCE_CATALOG:
                fail(f'undefined source key {key} referenced by {rel}')
        text = path.read_text(errors='ignore')
        first_heading = next((line[2:].strip() for line in text.splitlines() if line.startswith('# ')), '')
        if not first_heading.startswith(f"{m.group(1)} — "):
            fail(f'first heading number/title must align with filename: {rel}')
        if '## One-line thesis' not in text:
            fail(f'missing one-line thesis block: {rel}')
        if '## Compression rule for the archive' not in text:
            fail(f'missing compression rule block: {rel}')

    expected = list(range(numbers[0], numbers[0] + len(numbers)))
    if numbers != expected:
        fail(f'note numbers not contiguous: {numbers}')

    note_set = {str(p.relative_to(ROOT)) for p in note_paths}

    orphaned_mappings = sorted(set(NOTE_SOURCE_MAP) - note_set)
    if orphaned_mappings:
        fail(f'orphaned note-source mappings present: {orphaned_mappings}')


    duplicate_thread_ids = sorted({thread['id'] for thread in THREADS if sum(1 for t in THREADS if t['id'] == thread['id']) > 1})
    if duplicate_thread_ids:
        fail(f'duplicate thread ids present: {duplicate_thread_ids}')

    duplicate_surfaces = sorted({surface['surface'] for surface in CONTROL_SURFACES if sum(1 for s in CONTROL_SURFACES if s['surface'] == surface['surface']) > 1})
    if duplicate_surfaces:
        fail(f'duplicate control surfaces present: {duplicate_surfaces}')

    thread_seen = set()
    for thread in THREADS:
        if len(thread['notes']) != len(set(thread['notes'])):
            fail(f"duplicate note references inside thread: {thread['id']}")
        for note in thread['notes']:
            if note not in note_set:
                fail(f'thread references missing note: {note}')
            thread_seen.add(note)
    if thread_seen != note_set:
        fail(f'thread coverage mismatch: missing={sorted(note_set - thread_seen)} extra={sorted(thread_seen - note_set)}')

    gate_seen = set()
    for gate_name, gate_notes in LIFECYCLE_GATES.items():
        if len(gate_notes) != len(set(gate_notes)):
            fail(f"duplicate note references inside lifecycle gate: {gate_name}")
        for note in gate_notes:
            if note not in note_set:
                fail(f'lifecycle gate references missing note: {note}')
            gate_seen.add(note)
    if gate_seen != note_set:
        fail(f'lifecycle coverage mismatch: missing={sorted(note_set - gate_seen)} extra={sorted(gate_seen - note_set)}')

    used_source_keys = {key for keys in NOTE_SOURCE_MAP.values() for key in keys}
    unused_source_keys = sorted(set(SOURCE_CATALOG) - used_source_keys)
    if unused_source_keys:
        fail(f'unused source keys present: {unused_source_keys}')

    latest_note = sorted(note_paths)[-1].name
    latest_note_rel = f'archive/{latest_note}'
    dedicated_latest_threads = [thread for thread in THREADS if thread['notes'] == [latest_note_rel]]
    if not dedicated_latest_threads:
        fail('newest numbered note must have a dedicated single-note thematic thread')

    newest_source_keys = NOTE_SOURCE_MAP[latest_note_rel]
    newest_source_kinds = {SOURCE_CATALOG[key]['kind'] for key in newest_source_keys}
    if 'philosophy-reference' not in newest_source_kinds or newest_source_kinds <= {'philosophy-reference'}:
        fail('newest numbered note must draw on both philosophy-reference and non-philosophy sources')

    start_here = (ROOT / 'START_HERE.md').read_text(errors='ignore')
    if latest_note not in start_here:
        fail(f'START_HERE.md must mention newest numbered note: {latest_note}')

    if RELEASE_HIGHLIGHTS != list(dict.fromkeys(RELEASE_HIGHLIGHTS)) or not RELEASE_HIGHLIGHTS:
        fail('RELEASE_HIGHLIGHTS must be non-empty and duplicate-free')

    releases = json.loads((ROOT / 'RELEASES.json').read_text())
    latest_release = releases.get('releases', [{}])[0]
    if latest_release.get('revision') != current_revision():
        fail('RELEASES.json latest revision is out of sync with archive metadata')
    if latest_release.get('timestamp') != TIMESTAMP:
        fail('RELEASES.json latest timestamp is out of sync with archive metadata')
    if latest_release.get('codename') != CODENAME:
        fail('RELEASES.json latest codename is out of sync with archive metadata')
    if latest_release.get('highlights') != RELEASE_HIGHLIGHTS:
        fail('RELEASES.json latest highlights are out of sync with archive metadata')

    expected_change_header = f"## {TIMESTAMP} — {current_revision()} — {CODENAME}"
    if expected_change_header not in changelog:
        fail('CHANGELOG.md latest entry header is out of sync with archive metadata')

    newest_note = latest_note
    if newest_note not in readme:
        fail('README.md must name the newest numbered note for reliable re-entry')

    for doc_name in ['README.md', 'START_HERE.md', 'CHANGELOG.md']:
        doc_text = (ROOT / doc_name).read_text(errors='ignore')
        for rel in sorted(set(re.findall(r'archive/\d{3}[-a-z0-9]+\.md', doc_text))):
            if rel not in note_set:
                fail(f'{doc_name} contains broken archive reference: {rel}')

    parsed_json = {}
    for json_name in ['ARCHIVE_INDEX.json', 'THREADS.json', 'THREAD_SUMMARY.json', 'RELEASES.json', 'CONTROL_SURFACES.json', 'ASSURANCE_ARTIFACTS.json', 'LIFECYCLE_GATES.json', 'MANIFEST.json', 'SOURCES.json']:
        try:
            parsed_json[json_name] = json.loads((ROOT / json_name).read_text())
        except Exception as exc:
            fail(f'invalid json in {json_name}: {exc}')

    archive_index = parsed_json['ARCHIVE_INDEX.json']
    if archive_index.get('revision') != current_revision():
        fail('ARCHIVE_INDEX.json revision is out of sync with archive metadata')
    if archive_index.get('count') != len(note_paths):
        fail('ARCHIVE_INDEX.json count is out of sync with numbered notes')

    thread_summary = parsed_json['THREAD_SUMMARY.json']
    if thread_summary.get('revision') != current_revision():
        fail('THREAD_SUMMARY.json revision is out of sync with archive metadata')
    if thread_summary.get('thread_count') != len(THREADS):
        fail('THREAD_SUMMARY.json thread_count is out of sync with thread definitions')

    print('lint: OK')


if __name__ == '__main__':
    main()

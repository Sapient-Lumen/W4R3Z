#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[1]
errors = []

required = [
    'README.md', 'START_HERE.md', 'CHANGELOG.md', 'ARCHIVE_INDEX.md',
    'MANIFEST.json', 'SPECULATION_REGISTRY.json', 'ASSUMPTION-LEDGER.json',
    'FOLLOWTHROUGH-QUEUE.json', 'context-pack.json', 'REVISION-RECEIPT.json',
    'docs/00-meta/charter.md', 'docs/00-meta/archive-policy.md', 'docs/00-meta/bibliography.md',
    'docs/10-method/salience-rubric.md', 'docs/10-method/canon-vs-quarantine.md', 'docs/10-method/watchpoints.md',
    'docs/30-synthesis/pattern-language.md', 'docs/30-synthesis/portfolio-map.md', 'docs/30-synthesis/research-agenda.md'
]
for rel in required:
    if not (root / rel).exists():
        errors.append(f'missing required file: {rel}')

bib_path = root / 'docs/00-meta/bibliography.md'
bib_ids = set()
bib_id_list = []
if bib_path.exists():
    bib = bib_path.read_text(encoding='utf-8')
    bib_id_list = [b.upper() for b in re.findall(r'<a id="(src-\d+)"></a>', bib, flags=re.IGNORECASE)]
    bib_ids = set(bib_id_list)
    if len(bib_ids) != len(bib_id_list):
        errors.append('bibliography has duplicate source-anchor ids')
    bib_nums = [int(b.split('-', 1)[1]) for b in bib_id_list]
    if bib_nums != sorted(bib_nums):
        errors.append('bibliography source-anchor ids are not in numeric order')

def section_text(txt: str, heading: str) -> str:
    pattern = rf'{re.escape(heading)}\n(.*?)(?=\n## |\Z)'
    m = re.search(pattern, txt, flags=re.DOTALL)
    return m.group(1) if m else ''

pattern_path = root / 'docs/30-synthesis/pattern-language.md'
pattern_families = []
if pattern_path.exists():
    pattern_text = pattern_path.read_text(encoding='utf-8')
    pattern_families = [
        re.sub(r'^\d+\.\s*', '', h).strip().lower()
        for h in re.findall(r'^##\s+(.+)$', pattern_text, flags=re.MULTILINE)
        if re.match(r'^\d+\.', h.strip())
    ]

archive_index_links = set()
archive_index_canon_links = []
archive_index_quarantine_links = []
archive_index_path = root / 'ARCHIVE_INDEX.md'
if archive_index_path.exists():
    archive_index = archive_index_path.read_text(encoding='utf-8')
    archive_index_links = set(re.findall(r'\]\(([^)]+)\)', archive_index))
    archive_index_canon_links = re.findall(r'\]\(([^)]+)\)', section_text(archive_index, '## Canon'))
    archive_index_quarantine_links = re.findall(r'\]\(([^)]+)\)', section_text(archive_index, '## Quarantine'))

reg_path = root / 'SPECULATION_REGISTRY.json'
reg = None
if reg_path.exists():
    reg = json.loads(reg_path.read_text(encoding='utf-8'))
    ids = set()
    spec_list = reg.get('speculations', [])
    spec_numbers = [int(item['id'].split('-', 1)[1]) for item in spec_list]
    if spec_numbers != sorted(spec_numbers):
        errors.append('SPECULATION_REGISTRY.json is not ordered by numeric speculation id')
    for item in spec_list:
        sid = item['id']
        if sid in ids:
            errors.append(f'duplicate speculation id: {sid}')
        ids.add(sid)
        f = root / item['path']
        if not f.exists():
            errors.append(f'registry path missing: {item["path"]}')
        else:
            txt = f.read_text(encoding='utf-8')
            for heading in ['## Thesis', '## Watchpoints', '## Source anchors']:
                if heading not in txt:
                    errors.append(f'{item["path"]} missing heading {heading}')
            status_line = f'**Status:** {item["status"]}'
            if status_line not in txt:
                errors.append(f'{item["path"]} missing or mismatched status line: {status_line}')
            file_num = Path(item['path']).name.split('-', 1)[0]
            heading_expected = f'# {file_num} — {item["title"]}'
            heading_actual = next((line.strip() for line in txt.splitlines() if line.strip()), '')
            if heading_actual != heading_expected:
                errors.append(f'{item["path"]} heading/title drift: expected `{heading_expected}`')
            id_suffix = item['id'].split('-', 1)[1]
            if id_suffix != file_num:
                errors.append(f'{item["id"]} id/file number drift: file prefix {file_num}')
            note_source_list = [s.upper() for s in re.findall(r'\[(SRC-\d+)\]', txt, flags=re.IGNORECASE)]
            registry_source_list = [s.upper() for s in item.get('sources', [])]
            if set(note_source_list) != set(registry_source_list):
                errors.append(f'{item["id"]} note/body source anchors do not match registry sources')
            if note_source_list != registry_source_list:
                errors.append(f'{item["id"]} note/body source anchor order does not match registry source order')
            wp_count = len(re.findall(r'^- ', section_text(txt, '## Watchpoints'), flags=re.MULTILINE))
            if wp_count < 3:
                errors.append(f'{item["id"]} has fewer than 3 watchpoint bullets')
            if item['status'] == 'canon':
                for heading in ['## Mechanism sketch', '## What this speculation predicts', '## What would weaken this']:
                    if heading not in txt:
                        errors.append(f'{item["path"]} missing heading {heading}')
                pred_count = len(re.findall(r'^\d+\. ', section_text(txt, '## What this speculation predicts'), flags=re.MULTILINE))
                if pred_count < 3:
                    errors.append(f'{item["id"]} canon note has fewer than 3 numbered prediction bullets')
                if len(item.get('sources', [])) < 2:
                    errors.append(f'{item["id"]} canon note has fewer than 2 source anchors')
        for src in item.get('sources', []):
            if src.upper() not in bib_ids:
                errors.append(f'{item["id"]} references missing bibliography anchor: {src}')
        if item['path'] not in archive_index_links:
            errors.append(f'{item["id"]} registry path missing from ARCHIVE_INDEX.md: {item["path"]}')
        if not str(item.get('domain', '')).strip():
            errors.append(f'{item["id"]} registry item missing non-empty domain field')
        mech = str(item.get('mechanism_family', '')).strip().lower()
        if not mech:
            errors.append(f'{item["id"]} registry item missing non-empty mechanism_family field')
        elif pattern_families and mech not in pattern_families:
            errors.append(f'{item["id"]} mechanism_family is not recognised by pattern-language headings: {item.get("mechanism_family")}')

    canon_registry_paths = [item['path'] for item in reg.get('speculations', []) if item.get('status') == 'canon']
    quarantine_registry_paths = [item['path'] for item in reg.get('speculations', []) if item.get('status') == 'quarantine']
    if archive_index_canon_links != canon_registry_paths:
        errors.append('ARCHIVE_INDEX canon section is not synchronized with canonical registry order')
    if archive_index_quarantine_links != quarantine_registry_paths:
        errors.append('ARCHIVE_INDEX quarantine section is not synchronized with quarantine registry order')

context_pack_path = root / 'context-pack.json'
context_pack = None
if context_pack_path.exists() and pattern_families:
    context_pack = json.loads(context_pack_path.read_text(encoding='utf-8'))
    cp_families = [f.lower() for f in context_pack.get('mechanism_families', [])]
    if cp_families != pattern_families:
        errors.append('context-pack mechanism_families do not match pattern-language headings')

portfolio_map_path = root / 'docs/30-synthesis/portfolio-map.md'
portfolio_meta_claim = None
if portfolio_map_path.exists():
    portfolio_map_text = portfolio_map_path.read_text(encoding='utf-8')
    m = re.search(r'\*\*(.+?)\*\*', portfolio_map_text, flags=re.DOTALL)
    if m:
        portfolio_meta_claim = m.group(1).strip()
    if reg is not None:
        canon_items = [item for item in reg.get('speculations', []) if item.get('status') == 'canon']
        canon_file_numbers = [Path(item['path']).name.split('-', 1)[0] for item in canon_items]
        canon_rows = re.findall(r'^\|\s*([^|]+?)\s*\|\s*`?(\d{3})`?\s*\|', portfolio_map_text, flags=re.MULTILINE)
        canon_row_domains = [row[0].strip() for row in canon_rows]
        canon_row_numbers = [row[1] for row in canon_rows]
        canon_registry_domains = [item.get('domain', '').strip() for item in canon_items]
        if canon_row_numbers != canon_file_numbers:
            errors.append('portfolio-map canon table is not synchronized with canonical note numbers in SPECULATION_REGISTRY.json')
        if canon_row_domains != canon_registry_domains:
            errors.append('portfolio-map canon table domain labels are not synchronized with SPECULATION_REGISTRY.json')

receipt_path = root / 'REVISION-RECEIPT.json'
receipt = None
if receipt_path.exists():
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if not str(receipt.get('summary', '')).strip():
        errors.append('REVISION-RECEIPT summary is missing or empty')
    move_class = receipt.get('move_class', [])
    if not isinstance(move_class, list) or not move_class:
        errors.append('REVISION-RECEIPT move_class is missing or empty')
    shadow = receipt.get('counterfactual_shadow', {})
    if not str(shadow.get('rejected_move', '')).strip() or not str(shadow.get('why_rejected', '')).strip():
        errors.append('REVISION-RECEIPT counterfactual_shadow is missing required fields')

if portfolio_meta_claim and context_pack is not None:
    if context_pack.get('meta_claim') != portfolio_meta_claim:
        errors.append('context-pack meta_claim does not match portfolio-map meta-claim')
if portfolio_meta_claim and receipt is not None:
    if receipt.get('meta_claim') != portfolio_meta_claim:
        errors.append('REVISION-RECEIPT meta_claim does not match portfolio-map meta-claim')

manifest_path = root / 'MANIFEST.json'
manifest = None
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not str(manifest.get('summary', '')).strip():
        errors.append('MANIFEST summary is missing or empty')
    if reg is not None:
        if manifest.get('revision') != reg.get('version'):
            errors.append('MANIFEST revision does not match SPECULATION_REGISTRY version')
        if manifest.get('timestamp') != reg.get('updated_at'):
            errors.append('MANIFEST timestamp does not match SPECULATION_REGISTRY updated_at')
    if receipt is not None:
        if manifest.get('revision') != receipt.get('revision'):
            errors.append('MANIFEST revision does not match REVISION-RECEIPT revision')
        if manifest.get('timestamp') != receipt.get('timestamp'):
            errors.append('MANIFEST timestamp does not match REVISION-RECEIPT timestamp')
        if manifest.get('slug') != receipt.get('slug'):
            errors.append('MANIFEST slug does not match REVISION-RECEIPT slug')
    files = manifest.get('files', [])
    seen = set()
    for rel in files:
        if rel in seen:
            errors.append(f'duplicate manifest entry: {rel}')
        seen.add(rel)
        if not (root / rel).exists():
            errors.append(f'manifest entry missing on disk: {rel}')

release_manifest_path = root / 'RELEASE-MANIFEST.json'
if release_manifest_path.exists() and manifest is not None:
    release_manifest = json.loads(release_manifest_path.read_text(encoding='utf-8'))
    expected_bundle = f"Salient-Speculations-{manifest.get('revision')}-{manifest.get('timestamp')}-{manifest.get('slug')}.zip"
    if release_manifest.get('revision') != manifest.get('revision'):
        errors.append('RELEASE-MANIFEST revision does not match MANIFEST revision')
    if release_manifest.get('timestamp') != manifest.get('timestamp'):
        errors.append('RELEASE-MANIFEST timestamp does not match MANIFEST timestamp')
    if release_manifest.get('slug') != manifest.get('slug'):
        errors.append('RELEASE-MANIFEST slug does not match MANIFEST slug')
    if release_manifest.get('bundle') != expected_bundle:
        errors.append('RELEASE-MANIFEST bundle does not match MANIFEST-derived bundle filename')

changelog_path = root / 'CHANGELOG.md'
if changelog_path.exists() and manifest is not None:
    changelog_text = changelog_path.read_text(encoding='utf-8')
    m = re.search(r'^##\s+(rev\d+)\s+—\s+([0-9.]+)', changelog_text, flags=re.MULTILINE)
    if m:
        if manifest.get('revision') != m.group(1):
            errors.append('CHANGELOG top revision does not match MANIFEST revision')
        if manifest.get('timestamp') != m.group(2):
            errors.append('CHANGELOG top timestamp does not match MANIFEST timestamp')

if errors:
    print('LINT FAILED')
    for err in errors:
        print('-', err)
    sys.exit(1)

print('LINT OK')

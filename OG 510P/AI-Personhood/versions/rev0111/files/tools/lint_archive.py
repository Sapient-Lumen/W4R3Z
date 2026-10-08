from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

required = [
    'README.md',
    'START_HERE.md',
    'ARCHIVE_INDEX.md',
    'CHANGELOG.md',
    'VERSION',
    'SURFACE-STATUS.json',
    'REVISION-RECEIPT.json',
    'ASSUMPTION-LEDGER.json',
    'FOLLOWTHROUGH-QUEUE.json',
    'DATACUBE-TRANSFER-LEDGER.json',
    'docs/README.md',
    'docs/00-meta/archive-policy.md',
    'docs/00-meta/charter.md',
    'docs/00-meta/bibliography.md',
    'docs/00-meta/trajectory-map.md',
    'docs/10-foundations/assumption-and-scope.md',
    'docs/10-foundations/world-change-overview.md',
    'docs/20-world-design/legal-status-and-rights-stack.md',
    'docs/20-world-design/institutions-and-governance.md',
    'docs/20-world-design/economic-and-labor-reordering.md',
    'docs/20-world-design/research-welfare-and-evaluation.md',
    'docs/30-transition/transition-roadmap.md',
    'docs/90-quarantine/speculative-edges.md',
    'tools/gen_context_pack.py',
    'tools/build_manifest.py',
    'tools/package_release.py',
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f'missing required file: {rel}')

# No PDFs or zip files inside the release tree.
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.pdf', '.zip'}:
        raise SystemExit(f'forbidden retained artifact: {p.relative_to(ROOT)}')
    if '__pycache__' in p.parts:
        raise SystemExit(f'forbidden cache directory content: {p.relative_to(ROOT)}')

# Bibliography ids unique.
bib = (ROOT / 'docs/00-meta/bibliography.md').read_text(encoding='utf-8')
ids = re.findall(r'`(REF-\d{4})`', bib)
if len(ids) != len(set(ids)):
    raise SystemExit('duplicate bibliography ids')

# Citations resolve.
all_md = list(ROOT.rglob('*.md'))
used = set()
for md in all_md:
    txt = md.read_text(encoding='utf-8')
    for ref in re.findall(r'\[(REF-\d{4})\]', txt):
        used.add(ref)
        if ref not in ids:
            raise SystemExit(f'unknown citation {ref} in {md.relative_to(ROOT)}')
if not used:
    raise SystemExit('no citations used in markdown docs')

# Start-here paths exist.
start = (ROOT / 'START_HERE.md').read_text(encoding='utf-8')
for rel in re.findall(r'\d+\. `([^`]+)`', start):
    if not (ROOT / rel).exists():
        raise SystemExit(f'START_HERE missing target: {rel}')

# Generate derived surfaces.
for script in ['tools/gen_context_pack.py', 'tools/build_manifest.py']:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)

# Context pack should stay small.
cp = ROOT / 'context-pack.json'
if cp.stat().st_size > 12000:
    raise SystemExit('context-pack.json too large')

# Revision sync.
rev = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
receipt = json.loads((ROOT / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
if receipt['revision'] != rev:
    raise SystemExit('revision receipt out of sync with VERSION')
status = json.loads((ROOT / 'SURFACE-STATUS.json').read_text(encoding='utf-8'))
if status['revision'] != rev:
    raise SystemExit('surface status out of sync with VERSION')

# ARCHIVE_INDEX should mention every markdown file except itself? include itself too.
index = (ROOT / 'ARCHIVE_INDEX.md').read_text(encoding='utf-8')
for md in sorted(p.relative_to(ROOT).as_posix() for p in all_md):
    if md not in index:
        raise SystemExit(f'ARCHIVE_INDEX missing path: {md}')

print('lint_archive: OK')

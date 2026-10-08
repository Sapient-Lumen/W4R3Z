import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
registry_path = ROOT / 'docs/20-governance/open-question-registry.md'
archive_path = ROOT / 'docs/20-governance/open-question-archive-detail.md'

registry = registry_path.read_text(encoding='utf-8')
if not archive_path.exists():
    raise SystemExit('open-question archive detail is missing')
archive = archive_path.read_text(encoding='utf-8')

heading_re = re.compile(r'^##\s+(OQ-\d{4})\b.*$', re.MULTILINE)
registry_ids = heading_re.findall(registry)
archive_ids = heading_re.findall(archive)

if not registry_ids:
    raise SystemExit('open-question registry has no OQ headings')
if len(registry_ids) != len(set(registry_ids)):
    raise SystemExit('open-question registry contains duplicate OQ headings')

ordered = sorted(registry_ids, key=lambda item: int(item.split('-')[1]))
if registry_ids != ordered:
    raise SystemExit('open-question registry headings must be in ascending numeric order')

missing_in_archive = sorted(set(registry_ids) - set(archive_ids))
if missing_in_archive:
    raise SystemExit('open-question archive detail missing registry IDs: ' + ', '.join(missing_in_archive))

if 'open-question-archive-detail.md' not in registry:
    raise SystemExit('open-question registry must link to open-question-archive-detail.md')

blocks = re.split(r'(?=^##\s+OQ-\d{4}\b)', registry, flags=re.MULTILINE)
long_blocks = []
for block in blocks:
    if not block.startswith('## OQ-'):
        continue
    lines = [line for line in block.rstrip().splitlines() if line.strip()]
    if len(lines) > 12:
        oq = lines[0].split()[1]
        long_blocks.append(f'{oq} has {len(lines)} nonblank lines')
if long_blocks:
    raise SystemExit('open-question registry is no longer compact:\n' + '\n'.join(long_blocks))

print(f'check_open_question_registry: OK ({len(registry_ids)} questions)')

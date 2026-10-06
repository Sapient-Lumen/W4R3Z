import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = [line for line in (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8").splitlines() if line.startswith('| DelayBasin-rev')]
if not rows:
    raise SystemExit('ARCHIVE_INDEX has no bundle rows')
revs = []
for row in rows:
    m = re.search(r'DelayBasin-(rev\d{4})-', row)
    if not m:
        raise SystemExit(f'ARCHIVE_INDEX row missing revision bundle pattern: {row}')
    revs.append(int(m.group(1)[3:]))
if len(revs) != len(set(revs)):
    raise SystemExit('ARCHIVE_INDEX contains duplicate revision rows')
if any(a <= b for a, b in zip(revs, revs[1:])):
    raise SystemExit('ARCHIVE_INDEX rows must stay in strictly descending revision order')
print('check_archive_index_order: OK')

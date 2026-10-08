#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
paths = sorted(
    p for p in root.rglob('*')
    if p.is_file() and p.suffix in {'.md', '.json', '.py'} and '.zip' not in p.name
)

lines = ["# Filesystem index", "", f"Total tracked text surfaces: {len(paths)}", ""]
for p in paths:
    rel = p.relative_to(root).as_posix()
    lines.append(f'- `{rel}`')

(root / 'ARCHIVE_INDEX.generated.md').write_text("\n".join(lines) + "\n")
print('wrote ARCHIVE_INDEX.generated.md')

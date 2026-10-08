#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import ROOT, THREADS, current_revision


def main() -> None:
    out = {'revision': current_revision(), 'threads': THREADS}
    (ROOT / 'THREADS.json').write_text(json.dumps(out, indent=2) + '\n')

    lines = [f'# Threads — {current_revision()}', '']
    for thread in THREADS:
        lines.extend([f"## {thread['title']}", '', thread['description'], ''])
        for note in thread['notes']:
            lines.append(f'- `{note}`')
        lines.append('')
    (ROOT / 'THREADS.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
